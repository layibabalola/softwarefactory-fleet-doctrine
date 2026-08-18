from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys
import tempfile
import unittest


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
            with self.assertRaisesRegex(capsule.CapsuleError,"escapes workspace"): capsule.build(self.manifest(items=[item]))
        finally: outside.unlink()
        with self.assertRaisesRegex(capsule.CapsuleError,"exceeds"): capsule.build(self.manifest(max_payload_bytes=2))

    def test_invalid_range_and_duplicate_refuse(self):
        item=self.manifest()["items"][0]
        with self.assertRaisesRegex(capsule.CapsuleError,"duplicate"): capsule.build(self.manifest(items=[item,item.copy()]))
        bad=item.copy(); bad["end_line"]=99
        with self.assertRaisesRegex(capsule.CapsuleError,"exceeds file"): capsule.build(self.manifest(items=[bad]))


if __name__=="__main__": unittest.main()
