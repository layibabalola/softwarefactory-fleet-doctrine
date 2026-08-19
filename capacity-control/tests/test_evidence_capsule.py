from __future__ import annotations

import hashlib
import importlib.util
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULE=ROOT/"reference"/"build_evidence_capsule.py"
SPEC=importlib.util.spec_from_file_location("build_evidence_capsule",MODULE)
assert SPEC and SPEC.loader
capsule=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=capsule; SPEC.loader.exec_module(capsule)


class CapsuleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=pathlib.Path(self.temp.name)
        self.file=self.root/"ledger.md"; self.file.write_text("one\ntwo\nthree\nfour\n",encoding="utf-8")

    def tearDown(self): self.temp.cleanup()

    def manifest(self,**changes):
        value={"schema":capsule.REQUEST_SCHEMA,"subject_digest":"sha256:"+"a"*64,"workspace_root":str(self.root),"max_payload_bytes":100,"items":[{"relative_path":"ledger.md","sha256":hashlib.sha256(self.file.read_bytes()).hexdigest(),"start_line":2,"end_line":3,"purpose":"addressed records"}]}
        value.update(changes); return value

    def test_exact_slice_is_deterministic_and_hash_bound(self):
        first=capsule.build(self.manifest()); second=capsule.build(self.manifest())
        expected=b''.join(self.file.read_bytes().splitlines(keepends=True)[1:3]).decode('utf-8')
        self.assertEqual(first,second); self.assertEqual(expected,first["items"][0]["content"])
        self.assertEqual(len(expected.encode()),first["payload_bytes"])

    def test_file_change_invalidates_manifest(self):
        manifest=self.manifest(); self.file.write_text("changed\n",encoding="utf-8")
        with self.assertRaisesRegex(capsule.CapsuleError,"hash mismatch"): capsule.build(manifest)

    def test_traversal_and_oversize_refuse(self):
        outside=self.root.parent/(self.root.name+"-outside"); outside.write_text("secret\n",encoding="utf-8")
        try:
            item={"relative_path":"../"+outside.name,"sha256":hashlib.sha256(outside.read_bytes()).hexdigest(),"start_line":1,"end_line":1,"purpose":"bad"}
            with self.assertRaisesRegex(capsule.CapsuleError,"RELATIVE_PATH_SCHEMA"): capsule.build(self.manifest(items=[item]))
        finally: outside.unlink()
        with self.assertRaisesRegex(capsule.CapsuleError,"exceeds"): capsule.build(self.manifest(max_payload_bytes=2))

    def test_invalid_range_and_duplicate_refuse(self):
        item=self.manifest()["items"][0]
        with self.assertRaisesRegex(capsule.CapsuleError,"duplicate"): capsule.build(self.manifest(items=[item,item.copy()]))
        bad=item.copy(); bad["end_line"]=99
        with self.assertRaisesRegex(capsule.CapsuleError,"exceeds file"): capsule.build(self.manifest(items=[bad]))

    def test_pre_read_source_and_item_limits_refuse(self):
        with mock.patch.object(capsule,"MAX_SOURCE_BYTES",3):
            with self.assertRaisesRegex(capsule.CapsuleError,"INPUT_TOO_LARGE"): capsule.build(self.manifest())
        with mock.patch.object(capsule,"MAX_ITEMS",0):
            with self.assertRaisesRegex(capsule.CapsuleError,"ITEM_COUNT_LIMIT"): capsule.build(self.manifest())

    def test_manifest_payload_and_aggregate_preflight_refuse_before_open(self):
        with self.assertRaisesRegex(capsule.CapsuleError,"max_payload_bytes"):
            capsule.build(self.manifest(max_payload_bytes=capsule.MAX_CAPSULE_PAYLOAD_BYTES+1))
        with mock.patch.object(capsule,"MAX_AGGREGATE_SOURCE_BYTES",self.file.stat().st_size-1), mock.patch.object(capsule,"read_bounded",side_effect=AssertionError("source must not open")):
            with self.assertRaisesRegex(capsule.CapsuleError,"SOURCE_AGGREGATE_LIMIT"):
                capsule.build(self.manifest())

    def test_non_object_manifest_is_fixed_schema_error(self):
        with self.assertRaisesRegex(capsule.CapsuleError,"MANIFEST_SCHEMA"):
            capsule.build([])

    def test_manifest_schema_is_exact_and_bounded(self):
        with self.assertRaisesRegex(capsule.CapsuleError,"MANIFEST_SCHEMA"):
            capsule.build(self.manifest(extra="private"))
        with self.assertRaisesRegex(capsule.CapsuleError,"SUBJECT_DIGEST_SCHEMA"):
            capsule.build(self.manifest(subject_digest="C:/private/token"))
        item=self.manifest()["items"][0].copy(); item["start_line"]=True
        with self.assertRaisesRegex(capsule.CapsuleError,"line range"):
            capsule.build(self.manifest(items=[item]))
        item=self.manifest()["items"][0].copy(); item["purpose"]="x"*(capsule.MAX_PURPOSE_CHARS+1)
        with self.assertRaisesRegex(capsule.CapsuleError,"purpose"):
            capsule.build(self.manifest(items=[item]))

    def test_relative_path_is_canonical_and_never_echoes_root(self):
        for alias in (str(self.file),"./ledger.md","nested/../ledger.md"):
            item=self.manifest()["items"][0].copy(); item["relative_path"]=alias
            with self.assertRaisesRegex(capsule.CapsuleError,"RELATIVE_PATH_SCHEMA"):
                capsule.build(self.manifest(items=[item]))
        result=capsule.build(self.manifest())
        self.assertEqual(result["items"][0]["relative_path"],"ledger.md")
        self.assertNotIn(str(self.root),json.dumps(result))

    def test_deep_duplicate_and_nonfinite_manifest_are_fixed_refusals(self):
        deep=b"["*(capsule.MAX_JSON_DEPTH+1)+b"0"+b"]"*(capsule.MAX_JSON_DEPTH+1)
        stderr=io.StringIO()
        with mock.patch.object(capsule,"read_bounded",return_value=deep), mock.patch.object(capsule.json,"loads",side_effect=AssertionError("parser must not run")), contextlib.redirect_stderr(stderr):
            code=capsule.main(["--manifest","C:/private/manifest.json"])
        self.assertEqual(code,22); self.assertEqual(json.loads(stderr.getvalue()),{"error":"INPUT_REFUSED"})
        for raw in (b'{"schema":"x","schema":"y"}',b'{"schema":NaN}'):
            stderr=io.StringIO()
            with mock.patch.object(capsule,"read_bounded",return_value=raw), contextlib.redirect_stderr(stderr):
                code=capsule.main(["--manifest","C:/private/manifest.json"])
            self.assertEqual(code,22); self.assertEqual(json.loads(stderr.getvalue()),{"error":"INPUT_REFUSED"}); self.assertNotIn("private",stderr.getvalue())

    def test_cli_error_is_fixed_and_does_not_echo_private_path(self):
        stderr=io.StringIO()
        with mock.patch.object(capsule,"read_bounded",side_effect=OSError("C:/private/token")), contextlib.redirect_stderr(stderr):
            code=capsule.main(["--manifest","C:/private/manifest.json"])
        self.assertEqual(code,22)
        self.assertEqual(json.loads(stderr.getvalue()),{"error":"INPUT_REFUSED"})
        self.assertNotIn("private",stderr.getvalue())


if __name__=="__main__": unittest.main()
