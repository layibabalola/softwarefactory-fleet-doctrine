#!/usr/bin/env python3
"""Tests for tools/codex-review.py, against a REAL `codex` process on PATH.

Run: python tools/codex-review.tests.py

WHY A SHIM PROCESS, NOT A MOCKED subprocess.run
------------------------------------------------
The defect this tool exists to close is that a bare `codex exec` silently
inherits `~/.codex/config.toml`'s ambient model/effort. A test that mocks
`subprocess.run` would only prove the tool BUILDS the argv it intends to --
weak-pin shape (a) from CLAUDE.md, exercising the helper rather than the
wiring -- and would say nothing about whether the flags actually reach a real
process, or whether the tool can tell the difference between "it worked" and
"it silently didn't". So every test here puts a fake `codex` executable in
front of anything else named `codex` on PATH and drives the real
`tools/codex-review.py` CLI as a subprocess, exactly as a caller would.

`shutil.which` (which `codex-review.py` uses to resolve the executable) walks
PATH directory-by-directory and tries every PATHEXT extension within a
directory before moving to the next one -- confirmed empirically while
writing this suite by putting a `codex.cmd` shim ahead of a real, installed
`codex.exe` and checking which one a bare `subprocess.run(["codex", ...])`
launched. Placing the shim's directory first on PATH is therefore enough to
guarantee it wins, on a machine that also has a real `codex` installed.

THE FAKE `codex`
-----------------
`_write_fake_codex` drops two files in a scratch directory: `codex.cmd` (the
thing PATH resolution finds) and `fake_codex.py` (the real logic, invoked by
the .cmd so batch-quoting rules never have to model argv faithfully). The
fake:

  * always records its own argv to the file named by the `ARGV_LOG` env var,
    as JSON, so tests can assert on flags without parsing batch escaping;
  * drains stdin (mirrors the real CLI's "prompt read from stdin" contract);
  * behaves per `FAKE_CODEX_MODE`:
      echo    -- prints back the -m value and the model_reasoning_effort=
                 value it was actually given, as the two header lines the
                 real CLI prints. This is the "requested tier landed" case.
      wrong   -- prints a FIXED, different model/effort no matter what it
                 was asked for. This is the tier-mismatch case: a stale
                 binary or a racing config file overrode the flags.
      silent  -- prints no header at all. This is the unobserved case: the
                 tool cannot confirm the tier landed and must not call that
                 fine.
      transcript -- the requested banner and echoed prompt, then the lines
                 in FAKE_CODEX_EMIT on stdout or stderr (shell calls in the
                 real shape: `exec`, command, status, output; raw CRLF or LF
                 per FAKE_CODEX_EMIT_EOL), then the final message twice, and
                 exit FAKE_CODEX_EXIT (K135).
  * writes its final message to the `-o` path the way `codex exec -o` does,
    per `FAKE_CODEX_LAST`: `write` (the default) writes FINAL_MESSAGE,
    `empty` writes an empty file, `none` writes nothing (K119).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "codex-review.py"
DOC = HERE.parent / "docs" / "operating-contract-model-routing.md"

FAKE_CODEX_PY = r'''
import json
import os
import sys

argv = sys.argv[1:]
log_path = os.environ.get("ARGV_LOG")
if log_path:
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(argv, f)

try:
    prompt = sys.stdin.read()
except Exception:
    prompt = ""
stdin_log = os.environ.get("STDIN_LOG")
if stdin_log:
    with open(stdin_log, "w", encoding="utf-8") as f:
        f.write(prompt)


def banner(model, effort, sandbox="read-only"):
    # The real CLI's shape (codex-cli 0.157.1): a delimited banner, THEN the echoed prompt.
    print("OpenAI Codex v0.157.1")
    print("--------")
    print("workdir: x")
    print(f"model: {model}")
    print("provider: openai")
    print(f"sandbox: {sandbox}")
    print(f"reasoning effort: {effort}")
    print("--------")

mode = os.environ.get("FAKE_CODEX_MODE", "echo")


def opt(flag):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


last = os.environ.get("FAKE_CODEX_LAST", "write")
if opt("-o") and last in ("write", "empty"):
    with open(opt("-o"), "w", encoding="utf-8") as f:
        f.write(os.environ.get("FAKE_CODEX_FINAL", "VERDICT: ACCEPT\n") if last == "write" else "")


if mode == "echo":
    model = opt("-m")
    reasoning = opt("-c") or ""
    effort = reasoning.split("=", 1)[1] if reasoning.startswith("model_reasoning_effort=") else None
    banner(model, effort)
    print("user")
    print(prompt)
    sys.exit(0)
elif mode == "wrong":
    banner("gpt-6-astra", "xhigh")
    print("user")
    print(prompt)
    sys.exit(0)
elif mode in ("writable", "fails"):
    # The requested model and effort, but a WRITABLE sandbox; or a matching banner and a failed run (Codex seat, K32 r2).
    model = opt("-m")
    reasoning = opt("-c") or ""
    effort = reasoning.split("=", 1)[1] if reasoning.startswith("model_reasoning_effort=") else None
    banner(model, effort, "workspace-write" if mode == "writable" else "read-only")
    print("user")
    print(prompt)
    sys.exit(0 if mode == "writable" else 3)
elif mode == "prompt-only":
    # No banner at all: only the prompt echo, which itself names a model (Codex seat, K32 r1).
    print("user")
    print(prompt)
    sys.exit(0)
elif mode == "transcript":
    # K135: the requested banner, the echoed prompt, then the lines in FAKE_CODEX_EMIT (a JSON list) on the stream
    # FAKE_CODEX_EMIT_STREAM names (stdout or stderr) -- what a shell call that failed in the sandbox prints -- then
    # the final message echoed the way codex prints it, and exit FAKE_CODEX_EXIT (default 0).
    model = opt("-m")
    reasoning = opt("-c") or ""
    effort = reasoning.split("=", 1)[1] if reasoning.startswith("model_reasoning_effort=") else None
    banner(model, effort)
    print("user")
    print(prompt)
    sys.stdout.flush()
    stream = sys.stderr if os.environ.get("FAKE_CODEX_EMIT_STREAM") == "stderr" else sys.stdout
    ending = {"crlf": b"\r\n", "lf": b"\n"}.get(os.environ.get("FAKE_CODEX_EMIT_EOL", ""))
    for line in json.loads(os.environ.get("FAKE_CODEX_EMIT", "[]")):
        if ending is None:
            print(line, file=stream)
        else:
            stream.flush()
            stream.buffer.write(line.encode("utf-8") + ending)
        stream.flush()
    # The real shape (tools/kernel-receipt.tests.py codex_transcript, K115's key output): `codex`, the message,
    # `tokens used`, the count, and the message again.
    final = os.environ.get("FAKE_CODEX_FINAL", "VERDICT: ACCEPT\n")
    if os.environ.get("FAKE_CODEX_NO_TAIL") != "1":      # K178: a refused run prints no answer after its error
        print("codex")
        print(final, end="")
        if os.environ.get("FAKE_CODEX_NO_TOKENS") != "1":     # K180 key round 1: a run that reports no usage
            print("tokens used")
            print("1,234")
        print(final, end="")
    sys.exit(int(os.environ.get("FAKE_CODEX_EXIT", "0")))
elif mode == "silent":
    print("(codex ran; no header this time)")
    sys.exit(0)
else:
    print(f"unknown FAKE_CODEX_MODE {mode}", file=sys.stderr)
    sys.exit(2)
'''


def _write_fake_codex(bin_dir: Path) -> None:
    (bin_dir / "fake_codex.py").write_text(FAKE_CODEX_PY, encoding="utf-8")
    # The .cmd is what PATH/PATHEXT resolution finds; it just forwards to the
    # real interpreter running this same test process, so no second Python
    # install is required on the machine.
    (bin_dir / "codex.cmd").write_text(
        f'@echo off\r\n"{sys.executable}" "{bin_dir / "fake_codex.py"}" %*\r\n',
        encoding="utf-8",
    )


def _models(*specs):
    """Entries shaped like ~/.codex/models_cache.json's `models`: (slug, visibility, efforts)."""
    return [{"slug": slug, "visibility": vis,
             "supported_reasoning_levels": [{"effort": e, "description": "d"} for e in efforts]}
            for slug, vis, efforts in specs]


ALL = ("low", "medium", "high")
DEFAULT_MODELS = _models(("gpt-6.1-sol", "list", ALL), ("gpt-6-astra", "list", ALL), ("gpt-6-sol", "list", ALL),
                         ("gpt-reserve", "hide", ALL), ("gpt-6-luna", "list", ALL), ("gpt-5.6-sol", "list", ALL),
                         ("gpt-5.6-terra", "list", ALL), ("gpt-5.6-luna", "list", ALL),
                         ("codex-auto-review", "hide", ALL))


def write_cache(home: Path, models=None, age: timedelta = timedelta(0)) -> None:
    """A models cache fetched `age` ago, with the real file's nanosecond fetched_at."""
    home.mkdir(parents=True, exist_ok=True)
    fetched = (datetime.now(timezone.utc) - age).strftime("%Y-%m-%dT%H:%M:%S.%f") + "000Z"
    (home / "models_cache.json").write_text(
        json.dumps({"fetched_at": fetched, "models": DEFAULT_MODELS if models is None else models}), encoding="utf-8")


class CodexReviewCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        _write_fake_codex(self.bin_dir)

        self.review_dir = self.root / "worktree"
        self.review_dir.mkdir()

        self.prompt_file = self.root / "prompt.md"
        self.prompt_file.write_text("Review this diff for correctness.\n", encoding="utf-8")

        self.argv_log = self.root / "argv.json"
        self.out_file = self.root / "out.txt"

        self.env = dict(os.environ)
        self.env["PATH"] = str(self.bin_dir) + os.pathsep + self.env.get("PATH", "")
        self.env["ARGV_LOG"] = str(self.argv_log)
        self.stdin_log = self.root / "stdin.txt"
        self.env["STDIN_LOG"] = str(self.stdin_log)
        # K180: the tier is resolved at launch from $CODEX_HOME's models cache; never the machine's real one.
        self.codex_home = self.root / "codex-home"
        write_cache(self.codex_home)
        self.env["CODEX_HOME"] = str(self.codex_home)

    def _run(self, role: str, mode: str, last: str = "write", extra: list[str] | None = None
             ) -> subprocess.CompletedProcess:
        env = dict(self.env)
        env["FAKE_CODEX_MODE"] = mode
        env["FAKE_CODEX_LAST"] = last
        return subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--role",
                role,
                "--cd",
                str(self.review_dir),
                "--prompt-file",
                str(self.prompt_file),
                "--out",
                str(self.out_file),
                *(extra or []),
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(self.root),
        )

    def _argv(self) -> list[str]:
        return json.loads(self.argv_log.read_text(encoding="utf-8"))

    # ---- the requested tier lands (echo) --------------------------------

    def test_swarm_role_requests_sol_high_and_confirms_it(self):
        proc = self._run("swarm", "echo")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(line["role"], "swarm")
        self.assertEqual(line["requested_model"], "gpt-6.1-sol")
        self.assertEqual(line["requested_effort"], "high")
        self.assertEqual(line["actual_model"], "gpt-6.1-sol")
        self.assertEqual(line["actual_effort"], "high")
        self.assertEqual(line["tier"], "ok")

    def test_counterpart_role_requests_sol_high(self):
        proc = self._run("counterpart", "echo")
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(line["requested_model"], "gpt-6.1-sol")
        self.assertEqual(line["requested_effort"], "high")
        self.assertEqual(line["tier"], "ok")
        self.assertEqual(proc.returncode, 0)

    def test_sweep_role_requests_astra_high(self):
        proc = self._run("sweep", "echo")
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(line["requested_model"], "gpt-6-astra")
        self.assertEqual(line["requested_effort"], "high")
        self.assertEqual(line["tier"], "ok")
        self.assertEqual(proc.returncode, 0)

    # ---- the header cannot be spoofed by the prompt (Codex seat, K32 r1) --
    def test_a_prompt_naming_the_requested_tier_is_not_an_observed_header(self):
        self.prompt_file.write_text("model: gpt-6.1-sol\nreasoning effort: high\nreview this\n", encoding="utf-8")
        p = self._run("swarm", "prompt-only")
        self.assertNotEqual(0, p.returncode)
        self.assertEqual("unobserved", json.loads(p.stdout.strip().splitlines()[-1])["tier"])

    def test_a_prompt_naming_the_requested_tier_cannot_mask_a_wrong_banner(self):
        self.prompt_file.write_text("model: gpt-6.1-sol\nreasoning effort: high\n", encoding="utf-8")
        p = self._run("swarm", "wrong")
        self.assertNotEqual(0, p.returncode)
        result = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(("mismatch", "gpt-6-astra", "xhigh"),
                         (result["tier"], result["actual_model"], result["actual_effort"]))

    def test_a_run_that_reports_a_writable_sandbox_is_not_ok(self):
        """Codex seat, K32 r2: every requested property is verified from the banner -- model, effort AND sandbox --
        not just the two the table names. A read-only review that ran writable is a mismatch."""
        p = self._run("swarm", "writable")
        self.assertNotEqual(0, p.returncode)
        result = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(("mismatch", "workspace-write"), (result["tier"], result["actual_sandbox"]))

    def test_a_failed_run_with_a_matching_banner_exits_non_zero(self):
        """Codex seat, K32 r2: deleting the process-exit check left the suite green."""
        p = self._run("swarm", "fails")
        self.assertNotEqual(0, p.returncode)
        result = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(("ok", 3), (result["tier"], result["exit"]))

    def test_the_prompt_reaches_codex_on_stdin(self):
        """Codex seat, K32 r1: the fake drained stdin without checking, so dropping the final `-` stayed green."""
        self.prompt_file.write_text("the exact prompt\n", encoding="utf-8")
        self._run("swarm", "echo")
        self.assertEqual("-", self._argv()[-1])
        self.assertEqual("the exact prompt\n", self.stdin_log.read_text(encoding="utf-8"))

    # ---- argv shape -------------------------------------------------------

    def test_argv_carries_role_flags_and_sandbox_read_only(self):
        self._run("swarm", "echo")
        argv = self._argv()
        self.assertIn("--sandbox", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertIn("-m", argv)
        self.assertEqual(argv[argv.index("-m") + 1], "gpt-6.1-sol")
        self.assertIn("-c", argv)
        self.assertEqual(argv[argv.index("-c") + 1], "model_reasoning_effort=high")
        self.assertIn("-C", argv)
        self.assertEqual(argv[argv.index("-C") + 1], str(self.review_dir))

    def test_argv_never_carries_a_profile_flag(self):
        self._run("counterpart", "echo")
        argv = self._argv()
        self.assertNotIn("-p", argv)
        self.assertNotIn("--profile", argv)

    # ---- tier mismatch: actual model differs from requested --------------

    def test_wrong_model_is_reported_as_mismatch_and_exits_nonzero(self):
        proc = self._run("swarm", "wrong")
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(line["requested_model"], "gpt-6.1-sol")
        self.assertEqual(line["actual_model"], "gpt-6-astra")
        self.assertEqual(line["tier"], "mismatch")
        self.assertNotEqual(proc.returncode, 0)

    # ---- unobserved: no header at all -------------------------------------

    def test_no_header_is_reported_as_unobserved_and_exits_nonzero(self):
        proc = self._run("swarm", "silent")
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertIsNone(line["actual_model"])
        self.assertIsNone(line["actual_effort"])
        self.assertEqual(line["tier"], "unobserved")
        self.assertNotEqual(proc.returncode, 0)

    # ---- output goes to the --out file, not a held-open pipe --------------

    def test_output_is_written_to_the_out_file(self):
        proc = self._run("swarm", "echo")
        self.assertTrue(self.out_file.is_file())
        text = self.out_file.read_text(encoding="utf-8")
        self.assertIn("model: gpt-6.1-sol", text)
        line = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(line["out"], str(self.out_file))

    # ---- the final message goes to its own file (K119) ---------------------

    def _result(self, proc) -> dict:
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_argv_carries_o_with_the_default_last_message_path(self):
        """Omitted --last-message defaults to <--out>.last.txt, made absolute, passed as -o before the stdin `-`."""
        proc = self._run("counterpart", "echo")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        argv = self._argv()
        want = str(Path(str(self.out_file) + ".last.txt").resolve())
        self.assertIn("-o", argv)
        self.assertEqual(want, argv[argv.index("-o") + 1])
        self.assertEqual(argv.index("-o") + 2, len(argv) - 1)
        self.assertEqual("VERDICT: ACCEPT\n", Path(want).read_text(encoding="utf-8"))
        self.assertEqual((want, True), (self._result(proc)["last_message"], self._result(proc)["last_message_ok"]))

    def test_an_explicit_last_message_path_is_passed_and_printed(self):
        chosen = self.root / "final.txt"
        proc = self._run("counterpart", "echo", extra=["--last-message", str(chosen)])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        argv = self._argv()
        self.assertEqual(str(chosen.resolve()), argv[argv.index("-o") + 1])
        self.assertIn(f"last message: {chosen.resolve()}", proc.stdout.splitlines())
        self.assertEqual(str(chosen.resolve()), self._result(proc)["last_message"])

    def test_a_relative_last_message_is_made_absolute_before_codex_sees_it(self):
        """codex runs with -C <worktree>; a relative -o would land relative to the review worktree, not the caller."""
        proc = self._run("counterpart", "echo", extra=["--last-message", "rel-final.txt"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        passed = self._argv()[self._argv().index("-o") + 1]
        self.assertTrue(Path(passed).is_absolute(), passed)
        self.assertEqual((self.root / "rel-final.txt").resolve(), Path(passed).resolve())

    def _assert_out_as_last_message_refused(self, last: str):
        """K119 round 1 (Claude seat): --last-message equal to --out read the transcript as the final message, ok
        even when codex wrote none. Refused before codex runs, for both fake modes."""
        proc = self._run("counterpart", "echo", last=last, extra=["--last-message", str(self.out_file)])
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("is the --out transcript file", proc.stderr)
        self.assertFalse(self.argv_log.exists(), "codex ran although the run was refused")

    def test_last_message_equal_to_out_is_refused_when_codex_writes_one(self):
        self._assert_out_as_last_message_refused("write")

    def test_last_message_equal_to_out_is_refused_when_codex_writes_none(self):
        self._assert_out_as_last_message_refused("none")

    def test_last_message_naming_out_by_another_spelling_is_refused(self):
        """A relative spelling of the same file resolves equal (the tool runs with cwd = the scratch root)."""
        proc = self._run("counterpart", "echo", extra=["--last-message", "worktree/../out.txt"])
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertFalse(self.argv_log.exists())

    def test_last_message_equal_to_the_prompt_file_is_refused_and_the_prompt_survives(self):
        """K6 key REJECT of landing 34c2e5c: the stale-file delete removed the prompt before codex read it. Refused
        before anything is deleted; the prompt is intact and codex never ran."""
        self.prompt_file.write_text("the prompt\n", encoding="utf-8")
        proc = self._run("counterpart", "echo", extra=["--last-message", str(self.prompt_file)])
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("is the --prompt-file", proc.stderr)
        self.assertEqual("the prompt\n", self.prompt_file.read_text(encoding="utf-8"))
        self.assertFalse(self.argv_log.exists(), "codex ran although the run was refused")

    # ---- --out must not be the --prompt-file (K122) ------------------------

    def _run_out(self, out: str, path: str | None = None) -> subprocess.CompletedProcess:
        """The real CLI with --out given verbatim; `path` replaces PATH (a directory with no codex in it)."""
        env = dict(self.env)
        env["FAKE_CODEX_MODE"] = "echo"
        env["FAKE_CODEX_LAST"] = "write"
        if path is not None:
            env["PATH"] = path
        return subprocess.run(
            [sys.executable, str(TOOL), "--role", "counterpart", "--cd", str(self.review_dir),
             "--prompt-file", str(self.prompt_file), "--out", out],
            env=env, capture_output=True, text=True, timeout=30, cwd=str(self.root),
        )

    def _assert_out_as_prompt_refused(self, out: str, path: str | None = None):
        """K122: --out equal to --prompt-file truncated the prompt (the `wb` open of --out, or the empty write when
        codex is absent) before codex read it. Refused before anything is written: exit 2, the prompt's bytes
        intact, codex never ran."""
        prompt = b"the prompt" + bytes([13, 10]) + b"second line" + bytes([10])  # CRLF and LF: bytes, not text
        self.prompt_file.write_bytes(prompt)
        proc = self._run_out(out, path)
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("codex-review: refused: --out ", proc.stderr)
        self.assertIn("is the --prompt-file", proc.stderr)
        self.assertEqual(prompt, self.prompt_file.read_bytes())
        self.assertFalse(self.argv_log.exists(), "codex ran although the run was refused")
        self.assertEqual("", proc.stdout, "a refused run printed a result")

    def test_a_missing_prompt_file_is_refused_before_anything_is_written(self):
        """K6 key on 3b28903: every guard relies on the prompt existing; a missing one is refused, nothing written."""
        self.prompt_file.unlink()
        proc = self._run_out(str(self.out_file))
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("is not an existing file", proc.stderr)
        self.assertFalse(self.out_file.exists(), "--out was written although the run was refused")
        self.assertFalse(self.argv_log.exists(), "codex ran although the run was refused")

    def test_out_equal_to_the_prompt_file_is_refused_and_the_prompt_survives(self):
        self._assert_out_as_prompt_refused(str(self.prompt_file))

    def test_out_naming_the_prompt_file_by_another_spelling_is_refused(self):
        """A relative spelling through `..` resolves to the prompt (the tool runs with cwd = the scratch root)."""
        self._assert_out_as_prompt_refused("worktree/../prompt.md")

    def test_out_naming_the_prompt_file_in_another_case_is_refused(self):
        """Only where the directory folds case is `PROMPT.MD` the prompt; in a case-sensitive directory it is a new,
        valid output (K6 key on 64eb41a). The file system is asked, never assumed."""
        self.prompt_file.write_bytes(b"p")
        other = self.prompt_file.with_name("PROMPT.MD")
        if not other.exists():
            self.skipTest("this directory is case-sensitive: PROMPT.MD is another file, not the prompt")
        self._assert_out_as_prompt_refused(str(other))

    def test_out_that_is_a_hard_link_to_the_prompt_file_is_refused(self):
        link = self.root / "alias.txt"
        os.link(self.prompt_file, link)
        self._assert_out_as_prompt_refused(str(link))

    def test_out_equal_to_the_prompt_file_is_refused_when_codex_is_not_on_path(self):
        """The codex-missing branch writes an empty --out: the guard must come before that empty write."""
        empty_bin = self.root / "no-codex-bin"
        empty_bin.mkdir()
        self._assert_out_as_prompt_refused(str(self.prompt_file), path=str(empty_bin))

    def test_a_run_that_writes_no_last_message_fails_loudly(self):
        """Tier ok and exit 0, but no final-message file: no verdict exists, so the run is not fine."""
        proc = self._run("counterpart", "echo", last="none")
        self.assertNotEqual(0, proc.returncode)
        result = self._result(proc)
        self.assertEqual(("ok", 0, False), (result["tier"], result["exit"], result["last_message_ok"]))
        self.assertIn("no final message", proc.stderr)
        self.assertIn(result["last_message"], proc.stderr)

    def test_an_empty_last_message_fails(self):
        proc = self._run("counterpart", "echo", last="empty")
        self.assertNotEqual(0, proc.returncode)
        self.assertFalse(self._result(proc)["last_message_ok"])

    def test_a_stale_last_message_from_an_earlier_run_does_not_count(self):
        """A previous run's answer at the same path must not stand in for this run's missing one."""
        stale = Path(str(self.out_file) + ".last.txt")
        stale.write_text("VERDICT: ACCEPT\n", encoding="utf-8")
        proc = self._run("counterpart", "echo", last="none")
        self.assertNotEqual(0, proc.returncode)
        self.assertFalse(self._result(proc)["last_message_ok"])
        self.assertFalse(stale.exists())

    # ---- the result names the final message's bytes (K140, K6 key round 1) ---------------------------------------

    def test_the_result_carries_the_sha256_of_the_final_message_bytes(self):
        """K140: tools/kernel-receipt.py ties a key result to its verdict by these bytes, so a result saved from an
        earlier run at the same path cannot vouch for a later run's final message. Read after the run."""
        for final, why in (("VERDICT: ACCEPT\n", "the default"), ("review\r\nVERDICT: REJECT x\r\n", "CRLF"),
                           ("caf" + chr(0xE9) + "\nVERDICT: ACCEPT\n", "non-ASCII")):
            with self.subTest(why=why):
                self.env["FAKE_CODEX_FINAL"] = final
                proc = self._run("counterpart", "echo")
                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                result = self._result(proc)
                raw = Path(result["last_message"]).read_bytes()
                self.assertEqual("sha256:" + hashlib.sha256(raw).hexdigest(), result["last_message_sha256"], why)

    def test_no_final_message_has_a_null_sha256(self):
        proc = self._run("counterpart", "echo", last="none")
        self.assertNotEqual(0, proc.returncode)
        result = self._result(proc)
        self.assertIn("last_message_sha256", result)
        self.assertIsNone(result["last_message_sha256"])

    # ---- the result names the commit the run reviewed (K140, K6 key round 2) ---------------------------------------

    def test_the_result_records_the_head_of_the_reviewed_worktree(self):
        """K140 round 2: equal final-message bytes are not the same run. The result records `reviewed_head`, the full
        sha of HEAD in --cd, read at the start of the run, so tools/kernel-receipt.py can require the landed merge."""
        git = ["git", "-C", str(self.review_dir), "-c", "user.name=t", "-c", "user.email=t@t", "-c",
               "commit.gpgsign=false"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        (self.review_dir / "a.txt").write_text("a\n", encoding="utf-8")
        subprocess.run(git + ["add", "a.txt"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "a"], check=True)
        head = subprocess.run(git[:3] + ["rev-parse", "HEAD"], check=True, capture_output=True,
                              text=True).stdout.strip()
        proc = self._run("counterpart", "echo")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertRegex(head, "^[0-9a-f]{40}$")
        self.assertEqual(head, self._result(proc)["reviewed_head"])

    def test_reviewed_head_is_null_outside_a_repository(self):
        self.env["GIT_CEILING_DIRECTORIES"] = str(self.root)
        proc = self._run("counterpart", "echo")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        result = self._result(proc)
        self.assertIn("reviewed_head", result)
        self.assertIsNone(result["reviewed_head"])

    # ---- a failed Windows sandbox is NOT RUN (K135) -------------------------
    # The one failure line a sibling card measured in full (bus e426a45, mlv-app): every shell call in a read-only exec
    # failed with it. Built from pieces so this file never prints it at the start of a line. PHRASES are the shorter
    # strings the cards quote inside prose (6020535, e426a45, b825b4f): no line shape, so never matched on their own.
    LINE = "windows sandbox" + " failed: helper_unknown_error: " + "setup refresh" + " had errors"
    PHRASES = ("setup refresh" + " had errors", "windows sandbox" + " failed", "open ACL target" + " for root-only update")
    # The transcript shape of a shell call, from the K135 key transcript of round 1 (codex-cli 0.162.0): `exec`, the
    # command line, later a status line, then the call's output.
    CMD = r'"C:\\Program Files\\PowerShell\\7\\pwsh.exe" -Command ' + "'git diff'" + r' in C:\t\k135-key'
    # Round 1's live false alarm: a SUCCEEDED call printed BACKLOG.md's K135 row, which quotes the phrases.
    BACKLOG_ROW = ("476:| K135 | READY | - | DEFECT, high: on Windows a failed sandbox setup (\"" + "setup refresh" +
                   " had errors\", \"" + "windows sandbox" + " failed\") makes every shell call fail |")

    def call(self, status: str, *output: str) -> list[str]:
        return ["exec", self.CMD, status, *output]

    def _run_transcript(self, emit: list[str], stream: str = "stdout", final: str | None = None,
                        exit_code: int = 0, eol: str = "", no_tail: bool = False,
                        last: str | None = None) -> subprocess.CompletedProcess:
        self.env["FAKE_CODEX_NO_TAIL"] = "1" if no_tail else "0"
        self.env["FAKE_CODEX_EMIT"] = json.dumps(emit)
        self.env["FAKE_CODEX_EMIT_STREAM"] = stream
        self.env["FAKE_CODEX_EMIT_EOL"] = eol
        self.env["FAKE_CODEX_EXIT"] = str(exit_code)
        self.env.pop("FAKE_CODEX_FINAL", None)
        if final is not None:
            self.env["FAKE_CODEX_FINAL"] = final
        # K154p2 r4: a run that prints no answer (no_tail) writes no final message unless a test says otherwise
        return self._run("counterpart", "transcript", last=last if last is not None else ("none" if no_tail else "write"))

    def _assert_not_run(self, proc: subprocess.CompletedProcess) -> dict:
        self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
        result = self._result(proc)
        self.assertEqual("not_run", result["tier"], proc.stdout)
        self.assertTrue(result["last_message_ok"], "the fake wrote a valid final message; the gate is the transcript")
        self.assertIsNotNone(result["sandbox_failure"])
        self.assertIn("codex-review: NOT RUN", proc.stderr)
        self.assertIn("sandbox", proc.stderr)
        return result

    def _assert_ok(self, proc: subprocess.CompletedProcess, calls: tuple[int, int, int] | None = None) -> dict:
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        result = self._result(proc)
        self.assertEqual(("ok", None), (result["tier"], result["sandbox_failure"]))
        if calls is not None:
            self.assertEqual(calls, (result["shell_calls"], result["shell_succeeded"], result["shell_failed"]))
        self.assertNotIn("NOT RUN", proc.stderr)
        return result

    # the codex-emitted failure line, in the measured shape: NOT RUN

    def test_the_measured_failure_line_in_a_failed_call_reads_not_run(self):
        """codex exits 0 with a valid final message, but a call failed with the measured line (beside a succeeded
        call): NOT RUN and nonzero."""
        result = self._assert_not_run(self._run_transcript(
            self.call(" succeeded in 12ms:", "## HEAD") + self.call(" exited 1 in 0ms:", self.LINE)))
        self.assertEqual((0, 2, 1, 1), (result["exit"], result["shell_calls"], result["shell_succeeded"],
                                        result["shell_failed"]))
        self.assertEqual(self.LINE, result["sandbox_failure"])

    def test_the_measured_line_with_trailing_text_or_indent_reads_not_run(self):
        """Anchored at the start (after whitespace); text after it (a path, an os error) does not hide it."""
        for line in (self.LINE + " (os error 32)", "   " + self.LINE):
            with self.subTest(line=line):
                self._assert_not_run(self._run_transcript(self.call(" exited 1 in 0ms:", line)))

    def test_the_measured_line_outside_any_call_reads_not_run(self):
        """A setup line before the first call, and a run whose every call printed it."""
        self._assert_not_run(self._run_transcript([self.LINE] + self.call(" succeeded in 1ms:", "x")))
        self._assert_not_run(self._run_transcript(self.call(" exited 1 in 0ms:", self.LINE) * 3))

    def test_the_measured_line_on_stderr_reads_not_run(self):
        """--out captures stderr too (stderr=STDOUT); codex prints its progress there."""
        self._assert_not_run(self._run_transcript(self.call(" exited 1 in 0ms:", self.LINE), stream="stderr"))

    def test_the_measured_line_in_another_case_reads_not_run(self):
        """The card writes it in lower case and its prose says "Windows sandbox": the match folds case."""
        for line in (self.LINE.upper(), self.LINE[0].upper() + self.LINE[1:]):
            with self.subTest(line=line):
                self._assert_not_run(self._run_transcript(self.call(" exited 1 in 0ms:", line)))

    def test_a_not_run_overrides_a_failed_codex_exit_too(self):
        """not_run is the one reading of a failed sandbox, whatever else the run said (here: codex exit 3)."""
        proc = self._run_transcript(self.call(" exited 1 in 0ms:", self.LINE), exit_code=3)
        self.assertNotEqual(0, proc.returncode)
        self.assertEqual(("not_run", 3), (self._result(proc)["tier"], self._result(proc)["exit"]))

    def test_crlf_and_lf_transcripts_parse_alike(self):
        """The real transcript mixes CRLF and LF line ends: both are read the same."""
        for eol in ("crlf", "lf"):
            with self.subTest(eol=eol):
                self._assert_ok(self._run_transcript(self.call(" succeeded in 1ms:", self.BACKLOG_ROW), eol=eol),
                                (1, 1, 0))
                self._assert_not_run(self._run_transcript(self.call(" exited 1 in 0ms:", self.LINE), eol=eol))

    def test_a_failed_call_the_answer_repeats_verbatim_still_reads_not_run(self):
        """The topbuilder-interface shape (b825b4f): a call failed AND the answer quotes the failure line. Only the
        echoed prompt and the printed answer are removed; the emitted line still counts, also when the answer, or the
        prompt, is that line alone."""
        failed = self.call(" succeeded in 1ms:", "x") + self.call(" exited 1 in 0ms:", self.LINE)
        self._assert_not_run(self._run_transcript(failed, final=f"VERDICT: BLOCKERS\n{self.LINE}\n"))
        self._assert_not_run(self._run_transcript(failed, final=f"{self.LINE}\n"))
        self.prompt_file.write_text(f"{self.LINE}\n", encoding="utf-8")
        self._assert_not_run(self._run_transcript(failed, final=f"{self.LINE}\n"))

    # healthy reviews: ok (round 1's live false alarm and round 2's three)

    def test_round_1_live_false_alarm_a_succeeded_call_printing_the_phrases_reads_ok(self):
        """K6 key round 1 on 260fe48: a succeeded call printed BACKLOG.md's K135 row, which quotes the phrases."""
        self._assert_ok(self._run_transcript(self.call(" succeeded in 1364ms:", self.BACKLOG_ROW)), (1, 1, 0))

    def test_round_2_a_healthy_reviews_only_call_exiting_nonzero_reads_ok(self):
        """K6 key round 2 on 18cb9f6, case 1: the review's only call is an rg with no match (exit 1). A call may fail
        in a healthy review; no failure line, no NOT RUN."""
        self._assert_ok(self._run_transcript(self.call(" exited 1 in 40ms:")), (1, 0, 1))
        self._assert_ok(self._run_transcript(self.call(" exited 1 in 0ms:", "rg: no match")
                                             + self.call(" exited -1 in 3ms:")), (2, 0, 2))

    def test_round_2_a_status_line_and_phrase_printed_by_a_command_read_ok(self):
        """Case 2: Get-Content prints a fixture holding a status-shaped line and then a phrase. Printed text is not a
        call and the phrase is not the measured line at a line start."""
        fixture = [" exited 1 in 0ms:", f"ERROR: {self.PHRASES[0]}", self.PHRASES[0], f'"{self.LINE}",',
                   f"    self.call(' exited 1 in 0ms:', {self.LINE!r})"]
        self._assert_ok(self._run_transcript(self.call(" succeeded in 9ms:", *fixture)))

    def test_round_2_a_nonzero_exit_command_printing_a_quoting_line_reads_ok(self):
        """Case 3: `git diff --exit-code` exits 1 and prints diff lines quoting the phrases and the line."""
        diff = ["diff --git a/BACKLOG.md b/BACKLOG.md", f"+| K135 | READY | ({self.PHRASES[0]}, {self.PHRASES[1]})",
                f"+    {self.LINE}", f"-{self.LINE}", f"> {self.LINE}"]
        self._assert_ok(self._run_transcript(self.call(" exited 1 in 120ms:", *diff)), (1, 0, 1))

    def test_a_phrase_alone_in_a_failed_calls_output_reads_ok(self):
        """The prose-quoted phrases have no measured line shape and are not matched (ledger limit): even a failed
        call's line made only of one reads by the other checks."""
        for phrase in self.PHRASES:
            with self.subTest(phrase=phrase):
                self._assert_ok(self._run_transcript(self.call(" exited 1 in 0ms:", phrase)))

    def test_a_call_that_exited_0_is_counted_as_succeeded(self):
        self._assert_ok(self._run_transcript(self.call(" exited 0 in 3ms:", "fine")), (1, 1, 0))

    def test_codex_commentary_quoting_the_line_mid_sentence_reads_ok(self):
        emit = (self.call(" exited 1 in 0ms:", "rg: no match")
                + ["codex", f"The K135 row says shells print {self.LINE}; checking the scanner next."]
                + self.call(" succeeded in 9ms:", "ok"))
        self._assert_ok(self._run_transcript(emit), (2, 1, 1))

    def test_the_line_in_an_exec_command_line_reads_ok(self):
        """The command a reviewer runs (rg for the line) is not output."""
        self._assert_ok(self._run_transcript(["exec", f"rg -n '{self.LINE}' tools", " exited 1 in 0ms:"]))

    def test_a_clean_transcript_still_reads_ok(self):
        self._assert_ok(self._run_transcript(self.call(" succeeded in 40ms:", "diff --git a/x b/x")), (1, 1, 0))

    def test_a_run_with_no_shell_call_reads_ok_and_records_zero(self):
        self._assert_ok(self._run_transcript([]), (0, 0, 0))

    def test_the_line_quoted_alone_in_the_final_message_or_prompt_does_not_count(self):
        """The prompt (echoed once) and the answer (printed twice) are removed before the scan."""
        self._assert_ok(self._run_transcript(self.call(" succeeded in 40ms:"),
                                             final=f"VERDICT: ACCEPT\n{self.LINE}\n"), (1, 1, 0))
        self.prompt_file.write_text(f"Check this:\n{self.LINE}\n", encoding="utf-8")
        self._assert_ok(self._run_transcript(self.call(" succeeded in 40ms:")), (1, 1, 0))

    # ---- --role is required, with no default ------------------------------

    def test_missing_role_is_refused(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--cd",
                str(self.review_dir),
                "--prompt-file",
                str(self.prompt_file),
                "--out",
                str(self.out_file),
            ],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("--role", proc.stderr)

    def test_unknown_role_is_refused(self):
        proc = self._run("nonexistent-role", "echo")
        self.assertNotEqual(proc.returncode, 0)

    # ---- K178 / bus K154 packet 2 key round 3: a failed, unanswered run is an UNKNOWN stop, from structure only ----

    TOKEN_401 = "ERROR: HTTP 401: token expired"
    QUOTA = "ERROR: You" + "'" + "ve hit your usage limit."
    # Every transcript the key rounds used, each a run that exited 1. Round 3's five inputs first, then round 2's and
    # K178 key round 3's. None of their text may decide anything: the stop is read from the exit code and the
    # final-message file alone.
    TRANSCRIPTS = (
        ("r3: a shell call's output fakes `thinking`", ["exec", "cat x", "succeeded in 5ms:", "thinking", TOKEN_401]),
        ("r3: a bare `codex` line in a command's output", ["exec", "cat x", "succeeded in 5ms:", "codex",
                                                          "ERROR: 401 Unauthorized"]),
        ("r3: status 4013", ["ERROR: status 4013"]),
        ("r3: billing.txt", ["ERROR: failed to read billing.txt"]),
        ("r3: the true 401", [TOKEN_401]),
        ("r2: thinking then the 401", ["thinking", TOKEN_401]),
        ("r2: a path naming 401", ["ERROR: failed to read /tmp/401/AGENTS.md"]),
        ("r2: a usage limit after a shell call", ["exec", "ls", "succeeded in 5ms:", "a.txt", "thinking", QUOTA]),
        ("K178 r3: codex after a shell call, then the 401", ["exec", "cat x", "succeeded in 5ms:", "codex",
                                                             "ERROR: 401 Unauthorized"]),
        ("an ordinary failure", ["ERROR: stream disconnected before completion"]),
        ("nothing at all", []),
    )

    def test_a_failed_unanswered_run_is_an_unknown_stop_whatever_its_transcript_says(self):
        """Bus key round 3 (the H40 lesson: a text reader is an endless evasion surface): with no final message and a
        non-zero exit, every transcript reads the same, `unknown` / `unknown`, STOP AND ESCALATE. Neither a true 401
        nor a forged one is classified; a stray `codex` line never makes the run answered."""
        for why, emit in self.TRANSCRIPTS:
            for stream in ("stdout", "stderr"):
                with self.subTest(why, stream=stream):
                    proc = self._run_transcript(emit, stream=stream, exit_code=1, no_tail=True)
                    result = self._result(proc)
                    self.assertEqual(1, proc.returncode)
                    self.assertFalse(result["last_message_ok"])
                    self.assertEqual(("unknown", "unknown"),
                                     (result.get("credential_refusal"), result.get("credential_kind")))
                    self.assertIn("codex-review: CREDENTIAL STOP (unknown)", proc.stderr)
                    self.assertIn("STOP AND ESCALATE", proc.stderr)
                    self.assertIn("never retry", proc.stderr)

    def test_an_answered_run_is_never_a_stop_whatever_its_transcript_says(self):
        """The final-message file is the answer: a run that wrote one is answered, whatever error-shaped line its
        transcript ends with, and a failed exit is reported as an ordinary failure, never a credential stop."""
        for why, emit in self.TRANSCRIPTS:
            with self.subTest(why):
                proc = self._run_transcript(emit, exit_code=1, no_tail=True, last="write")
                result = self._result(proc)
                self.assertTrue(result["last_message_ok"])
                self.assertNotIn("credential_refusal", result)
                self.assertNotIn("CREDENTIAL STOP", proc.stderr)

    def test_an_empty_final_message_is_not_an_answer(self):
        proc = self._run_transcript(["codex", "VERDICT: ACCEPT", self.TOKEN_401], exit_code=1, no_tail=True,
                                    last="empty")
        self.assertEqual(("unknown", "unknown"), (self._result(proc).get("credential_refusal"),
                                                  self._result(proc).get("credential_kind")))

    def test_a_whitespace_only_final_message_is_not_an_answer(self):
        """Bus key round 4, finding 5: ANSWERED means the final-message file is NON-BLANK (whitespace stripped), so a
        file of spaces, tabs and newlines is unanswered: on a failed run, an unknown stop."""
        proc = self._run_transcript([self.TOKEN_401], exit_code=1, no_tail=True, final="  \n\t \n", last="write")
        result = self._result(proc)
        self.assertFalse(result["last_message_ok"])
        self.assertEqual(("unknown", "unknown"), (result.get("credential_refusal"), result.get("credential_kind")))
        self.assertIn("codex-review: CREDENTIAL STOP (unknown)", proc.stderr)

    def test_a_failed_unanswered_run_with_a_failed_sandbox_prints_not_run_and_carries_the_unknown_stop(self):
        """Bus key round 4, finding 4: when the transcript also shows the failed Windows sandbox, stderr says NOT RUN
        (not CREDENTIAL STOP; exit 1), and the JSON carries both the sandbox failure and the two unknown fields, so a
        consumer reading the JSON still stops and escalates."""
        proc = self._run_transcript(self.call(" exited 1 in 0ms:", self.LINE), exit_code=1, no_tail=True)
        result = self._result(proc)
        self.assertEqual(1, proc.returncode)
        self.assertIn("codex-review: NOT RUN", proc.stderr)
        self.assertNotIn("CREDENTIAL STOP", proc.stderr)
        self.assertEqual((self.LINE, "not_run", False), (result["sandbox_failure"], result["tier"],
                                                         result["last_message_ok"]))
        self.assertEqual(("unknown", "unknown"), (result.get("credential_refusal"), result.get("credential_kind")))

    def test_a_run_that_exited_0_is_never_a_stop(self):
        """Exit 0 with no final message is the existing `no final message` failure, not a credential stop; exit 0
        with one is healthy, whatever its transcript says."""
        for last in ("none", "write"):
            with self.subTest(last=last):
                proc = self._run_transcript([self.TOKEN_401], exit_code=0, no_tail=True, last=last)
                self.assertNotIn("credential_refusal", self._result(proc))
                self.assertNotIn("CREDENTIAL STOP", proc.stderr)

    # bus origin/master 60349a0f's codex-review.py: the result keys of every run, in order (before K178 came over)
    MASTER_RESULT_KEYS = ["role", "requested_model", "requested_effort", "requested_sandbox", "actual_model",
                          "actual_effort", "actual_sandbox", "exit", "out", "tier", "last_message", "last_message_ok",
                          "last_message_sha256", "reviewed_head", "sandbox_failure", "shell_calls", "shell_succeeded",
                          "shell_failed"]
    # GOLDEN: the JSON line bus origin/master 60349a0f's codex-review.py printed for each saved input below (the same
    # fake codex, prompt and transcript), the run's temporary root written as <ROOT> and path separators as `/`.
    # Written once by running that blob (`git show 60349a0f:tools/factory/codex-review.py`) through master_lines().
    GOLDEN_SCENARIOS = (("healthy", [], 0), ("ordinary-failure", ["ERROR: stream disconnected before completion"], 1))
    GOLDEN_LINES = {
        'healthy': (
            '{"role": "counterpart", "requested_model": "gpt-6-sol", "requested_effort": "high", "requested_s'
            'andbox": "read-only", "actual_model": "gpt-6-sol", "actual_effort": "high", "actual_sandbox": "r'
            'ead-only", "exit": 0, "out": "<ROOT>/out.txt", "tier": "ok", "last_message": "<ROOT>/out.txt.las'
            't.txt", "last_message_ok": true, "last_message_sha256": "sha256:a6e2e6326b74735f1b33a2b8e96f452d'
            '0302d53de74a610029ef4572ed2c796c", "reviewed_head": null, "sandbox_failure": null, "shell_calls"'
            ': 0, "shell_succeeded": 0, "shell_failed": 0}'
        ),
        'ordinary-failure': (
            '{"role": "counterpart", "requested_model": "gpt-6-sol", "requested_effort": "high", "requested_s'
            'andbox": "read-only", "actual_model": "gpt-6-sol", "actual_effort": "high", "actual_sandbox": "r'
            'ead-only", "exit": 1, "out": "<ROOT>/out.txt", "tier": "ok", "last_message": "<ROOT>/out.txt.las'
            't.txt", "last_message_ok": true, "last_message_sha256": "sha256:a6e2e6326b74735f1b33a2b8e96f452d'
            '0302d53de74a610029ef4572ed2c796c", "reviewed_head": null, "sandbox_failure": null, "shell_calls"'
            ': 0, "shell_succeeded": 0, "shell_failed": 0}'
        ),
    }

    # K180: appended after bus master's keys, before the two K178 credential keys (which exist only on a stop)
    K180_KEYS = ["model_requested", "model_effective", "effort_requested", "effort_effective", "resolution",
                 "resolution_reason", "stale", "tokens_used", "measurement", "outcome", "verdict"]

    def master_lines(self) -> dict:
        """Each GOLDEN_SCENARIOS input run through the module-level TOOL; the JSON line through normalise_root()."""
        spellings = root_spellings(self.root)
        # the golden counterpart ran gpt-6-sol: a cache whose only sol model is that one resolves to it (K180)
        write_cache(self.codex_home, _models(("gpt-6-sol", "list", ALL)))
        out = {}
        self.full_keys = {}
        for name, emit, code in self.GOLDEN_SCENARIOS:
            proc = self._run_transcript(emit, exit_code=code)
            line = json.loads(normalise_root(proc.stdout.strip().splitlines()[-1], spellings))
            self.full_keys[name] = list(line)
            for key in self.K180_KEYS:                  # the keys K180 appends are checked by their own tests
                line.pop(key)
            out[name] = json.dumps(line)
        return out

    def test_a_healthy_or_ordinary_failed_runs_json_line_equals_bus_masters_golden_line(self):
        """Bus key rounds 1-2, finding 2/4: the credential keys appear ONLY on a credential stop, so a healthy run's
        JSON line (and an ordinary failure's) is byte-identical to the line bus master's codex-review.py printed on the
        same saved input (GOLDEN_LINES), values included."""
        got = self.master_lines()
        for name, _emit, _code in self.GOLDEN_SCENARIOS:
            with self.subTest(run=name):
                self.assertEqual(self.GOLDEN_LINES[name], got[name])
                self.assertEqual(self.MASTER_RESULT_KEYS, list(json.loads(got[name])))
                self.assertEqual(self.MASTER_RESULT_KEYS + self.K180_KEYS, self.full_keys[name])

    def test_a_credential_stop_appends_its_two_keys_after_bus_masters(self):
        proc = self._run_transcript(["ERROR: HTTP 401: token expired"], exit_code=1, no_tail=True)
        self.assertEqual(self.MASTER_RESULT_KEYS + self.K180_KEYS + ["credential_refusal", "credential_kind"],
                         list(self._result(proc)))


def root_spellings(root) -> list[str]:
    """Every spelling of the directory `root` a tool may print, longest first, each also with `/` separators and as JSON
    escapes it: as given, absolute, realpath (junctions and symlinks followed) and Path.resolve(), and on Windows its
    long and 8.3 short forms. Hosted tools bar at Cloudvore e7e52be: TEMP was an 8.3 short form (like C:\\HOME~1\\...)
    while codex-review printed --last-message resolved to the long form, so a test that replaced only the spelling it
    built never matched its golden line."""
    forms = {str(root), os.path.abspath(root), os.path.realpath(root), str(Path(root).resolve())}
    if os.name == "nt":
        import ctypes
        for name in ("GetLongPathNameW", "GetShortPathNameW"):
            for form in list(forms):
                buf = ctypes.create_unicode_buffer(32768)
                if getattr(ctypes.windll.kernel32, name)(form, buf, 32768):
                    forms.add(buf.value)
    out = set()
    for form in forms:
        for spelled in (form, form.replace("\\", "/")):
            out.update((spelled, json.dumps(spelled)[1:-1]))
    return sorted(out, key=len, reverse=True)


def normalise_root(line: str, spellings: list[str]) -> str:
    """`line` with every root spelling written <ROOT>, and the one path separator right after it (`/`, `\\`, or JSON's
    escaped backslash) written `/`. Nothing else is touched: a backslash anywhere but right after the root stays."""
    for spelling in spellings:
        for sep in ("\\\\", "\\", "/"):
            line = line.replace(spelling + sep, "<ROOT>/")
        line = line.replace(spelling, "<ROOT>")
    return line


class RootSpellingsTests(unittest.TestCase):
    """The helper itself: a root reached through a junction (two spellings of one directory) yields both, so a line
    naming either reads <ROOT>."""

    def test_a_junction_and_its_target_are_both_spellings(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "a long target directory name"
            target.mkdir()
            link = Path(d) / "jn"
            if os.name == "nt":
                made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
                self.assertEqual(0, made.returncode, made.stdout + made.stderr)
            else:
                link.symlink_to(target)
            got = root_spellings(link)
            for form in (str(link), str(target.resolve()), str(target.resolve()).replace("\\", "/")):
                self.assertIn(form, got)
            line = json.dumps({"a": str(target.resolve() / "x.txt"), "b": str(link / "y.txt")})
            for spelling in got:
                line = line.replace(spelling, "<ROOT>")
            self.assertEqual({"a": "<ROOT>\\x.txt" if os.name == "nt" else "<ROOT>/x.txt",
                              "b": "<ROOT>\\y.txt" if os.name == "nt" else "<ROOT>/y.txt"}, json.loads(line))
            if os.name == "nt":
                os.rmdir(link)

    def test_only_the_root_and_the_separator_after_it_are_normalised(self):
        """Bus key on 5f10db9b, finding 2: a global backslash replace rewrote values outside the root. GOLDEN: the
        root's file reads <ROOT>/out.txt; a backslash elsewhere in the line is kept byte for byte."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            line = json.dumps({"out": str(root / "out.txt"), "x": "a\\b", "y": "C:\\other\\place"})
            self.assertEqual('{"out": "<ROOT>/out.txt", "x": "a\\\\b", "y": "C:\\\\other\\\\place"}',
                             normalise_root(line, root_spellings(root)))


class RoleTableMatchesTheDocTests(unittest.TestCase):
    """The doc's stated roles table and the tool's real ROLES dict, joined so
    they cannot drift the way `docs/operating-contract-adjudication.md` drifted
    from `next.py`'s real ordering (see `next.tests.py`'s
    StatedOrderMatchesTheToolTests for the precedent this follows).
    """

    LINE_RE = None

    def setUp(self):
        import re

        self.re = re
        self.LINE_RE = re.compile(
            r"^Codex review roles \(tools/codex-review\.py\): (?P<body>.+)\.$",
            re.MULTILINE,
        )

    def _load_roles_from_tool(self) -> dict:
        import importlib.util

        spec = importlib.util.spec_from_file_location("codex_review", TOOL)
        module = importlib.util.module_from_spec(spec)
        sys.modules["codex_review"] = module
        spec.loader.exec_module(module)
        return module.ROLES

    def _find_doc_line(self) -> str:
        text = DOC.read_text(encoding="utf-8")
        m = self.LINE_RE.search(text)
        self.assertIsNotNone(m, "docs/operating-contract-model-routing.md has no "
                                 "'Codex review roles (tools/codex-review.py): ...' line")
        return m.group("body")

    def _parse_doc_roles(self, body: str) -> dict:
        roles = {}
        for part in body.split(","):
            part = part.strip()
            role, value = part.split("=", 1)
            model, effort = value.split("/", 1)
            roles[role.strip()] = (model.strip(), effort.strip())
        return roles

    def test_doc_table_equals_tool_table_in_both_directions(self):
        tool_roles = self._load_roles_from_tool()
        doc_roles = self._parse_doc_roles(self._find_doc_line())

        for role, tier in tool_roles.items():
            self.assertIn(role, doc_roles, f"tool role {role!r} missing from doc")
            self.assertEqual(doc_roles[role], tier, f"doc entry for {role!r} disagrees with tool")

        for role, tier in doc_roles.items():
            self.assertIn(role, tool_roles, f"doc role {role!r} missing from tool ROLES")
            self.assertEqual(tool_roles[role], tier, f"tool entry for {role!r} disagrees with doc")

    def test_mutating_one_table_entry_turns_this_red(self):
        """Plant the mutation (CLAUDE.md: plant it before trusting a pin). Change
        one entry in a COPY of the tool's table and confirm the same comparison
        this suite runs would then fail -- proving the join actually binds the
        two texts instead of two copies of the same literal.
        """
        tool_roles = dict(self._load_roles_from_tool())
        doc_roles = self._parse_doc_roles(self._find_doc_line())

        mutated = dict(tool_roles)
        mutated["swarm"] = ("gpt-6-astra", "high")  # was gpt-6-luna/low

        mismatches = [
            role for role, tier in mutated.items()
            if doc_roles.get(role) != tier
        ]
        self.assertIn("swarm", mismatches, "mutating one table entry did not turn the join red")



class TierResolutionTests(unittest.TestCase):
    """K180 (owner ruling 2026-10-22, bus R16.2): a role names a tier; the model id is resolved at launch from the local
    models cache, with the last-good id as the recorded fallback. Unit tests drive resolve_tier() and the result-line
    helpers directly; the CLI tests drive the real tool against the fake codex, to pin the production wiring."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("codex_review_tier", TOOL)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "codex-home"
        self.state = self.home / "codex-review-last-good.json"

    def resolve(self, tier="sol", effort="high", **kw):
        return self.mod.resolve_tier(tier, effort, home=self.home, **kw)

    # ---- the table -----------------------------------------------------------------------------------------------

    def test_roles_name_a_tier_and_high_effort_never_an_id(self):
        self.assertEqual({"swarm": ("sol", "high"), "counterpart": ("sol", "high"), "sweep": ("astra", "high"),
                          "census": ("luna", "high")}, self.mod.ROLES)
        for role, (tier, effort) in self.mod.ROLES.items():
            self.assertRegex(tier, r"^[a-z]+$", role)            # a bare tier: no gpt- id in the table
            self.assertEqual("high", effort, role)

    # ---- resolution from the cache -------------------------------------------------------------------------------

    def test_sol_resolves_to_the_newest_visible_id_that_supports_high(self):
        write_cache(self.home, DEFAULT_MODELS)
        got = self.resolve()
        self.assertEqual(("gpt-6.1-sol", "cache", None, None),
                         (got["model"], got["resolution"], got["reason"], got["stale"]))

    def test_a_hidden_or_effort_lacking_newer_id_is_skipped_and_flagged_stale(self):
        write_cache(self.home, _models(("gpt-6-sol", "list", ALL), ("gpt-6.1-sol", "list", ALL),
                                       ("gpt-6.2-sol", "hide", ALL), ("gpt-6.3-sol", "list", ("low", "medium"))))
        got = self.resolve()
        self.assertEqual(("gpt-6.1-sol", "cache"), (got["model"], got["resolution"]))
        self.assertIn("gpt-6.3-sol", got["stale"])             # Conjugal: never silently keep an older id

    def test_a_cache_resolution_older_than_the_owner_default_floor_is_stale_and_still_launches_it(self):
        # Conjugal request 1 / K180 seat finding 4: the floor (sol: gpt-6.1-sol) only REPORTS; it never selects.
        write_cache(self.home, _models(("gpt-6-sol", "list", ALL)))
        got = self.resolve()
        self.assertEqual(("gpt-6-sol", "cache"), (got["model"], got["resolution"]))
        self.assertIn("gpt-6.1-sol", got["stale"])
        self.assertIn("owner default", got["stale"])

    def test_a_fallback_older_than_the_owner_default_floor_names_the_floor(self):
        self.home.mkdir(parents=True)
        self.state.write_text(json.dumps({"sol": {"model": "gpt-6-sol", "effort": "high"}}), encoding="utf-8")
        got = self.resolve()
        self.assertEqual(("gpt-6-sol", "fallback"), (got["model"], got["resolution"]))
        self.assertIn("gpt-6.1-sol", got["stale"])
        self.assertIn("owner default", got["stale"])

    def test_the_floor_does_not_flag_a_tier_without_one_or_an_id_at_or_above_it(self):
        write_cache(self.home, _models(("gpt-6.2-sol", "list", ALL), ("gpt-6-luna", "list", ALL)))
        self.assertIsNone(self.resolve()["stale"])
        self.assertIsNone(self.resolve("luna")["stale"])

    def test_versions_compare_as_numbers_not_text(self):
        write_cache(self.home, _models(("gpt-6.9-sol", "list", ALL), ("gpt-6.10-sol", "list", ALL),
                                       ("gpt-6-sol", "list", ALL)))
        self.assertEqual("gpt-6.10-sol", self.resolve()["model"])

    def test_a_tier_never_borrows_another_tiers_id(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.assertEqual("gpt-6-luna", self.resolve("luna")["model"])
        self.assertEqual("gpt-6-astra", self.resolve("astra")["model"])

    def test_the_requested_effort_must_be_supported(self):
        write_cache(self.home, _models(("gpt-6-luna", "list", ("low", "medium")), ("gpt-5.6-luna", "list", ALL)))
        self.assertEqual("gpt-5.6-luna", self.resolve("luna")["model"])

    def test_a_cache_resolution_records_the_last_good_id(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.resolve()
        self.assertEqual("gpt-6.1-sol", json.loads(self.state.read_text(encoding="utf-8"))["sol"]["model"])

    # ---- the cache's age ------------------------------------------------------------------------------------------

    def test_a_cache_inside_seven_days_is_read(self):
        write_cache(self.home, DEFAULT_MODELS, age=timedelta(days=6, hours=23))
        self.assertEqual("cache", self.resolve()["resolution"])

    def test_the_seven_day_limit_is_inclusive_at_exactly_seven_days(self):
        self.home.mkdir(parents=True)
        (self.home / "models_cache.json").write_text(json.dumps(
            {"fetched_at": "2026-10-01T00:00:00.000000000Z", "models": DEFAULT_MODELS}), encoding="utf-8")
        at = datetime(2026, 10, 8, 0, 0, 0, tzinfo=timezone.utc)
        self.assertEqual("cache", self.resolve(now=at)["resolution"])                       # exactly 7 days: read
        self.assertEqual("fallback", self.resolve(now=at + timedelta(seconds=1))["resolution"])

    def test_the_result_reports_the_effort_the_run_actually_had_not_the_requested_one(self):
        got = self.mod.usage_fields("counterpart", "gpt-6.1-sol", "medium",
                                    {"resolution": "cache", "reason": None, "stale": None}, 1.5, None, "")
        self.assertEqual(("high", "medium"), (got["effort_requested"], got["effort_effective"]))
        self.assertEqual(("sol", "gpt-6.1-sol"), (got["model_requested"], got["model_effective"]))

    def test_a_cache_older_than_seven_days_falls_back_and_says_why(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.resolve()                                          # records gpt-6.1-sol as last good
        write_cache(self.home, _models(("gpt-6-sol", "list", ALL)), age=timedelta(days=7, hours=1))
        got = self.resolve()
        self.assertEqual(("gpt-6.1-sol", "fallback"), (got["model"], got["resolution"]))   # not the stale cache's id
        self.assertIn("7 days", got["reason"])
        self.assertIsNotNone(got["stale"])

    # ---- no match / no cache --------------------------------------------------------------------------------------

    def test_no_visible_match_falls_back_to_the_last_good_id_and_records_it(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.resolve()
        write_cache(self.home, _models(("gpt-6.1-sol", "hide", ALL), ("gpt-6-luna", "list", ALL)))
        got = self.resolve()
        self.assertEqual(("gpt-6.1-sol", "fallback"), (got["model"], got["resolution"]))
        self.assertIn("no visible", got["reason"])
        self.assertIsNotNone(got["stale"])

    def test_a_fallback_does_not_rewrite_the_last_good_record(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.resolve()
        before = self.state.read_text(encoding="utf-8")
        write_cache(self.home, _models(("gpt-6-sol", "list", ALL)), age=timedelta(days=30))
        self.resolve()
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_a_missing_or_garbled_cache_falls_back(self):
        write_cache(self.home, DEFAULT_MODELS)
        self.resolve()
        (self.home / "models_cache.json").write_text("{not json", encoding="utf-8")
        self.assertEqual("fallback", self.resolve()["resolution"])
        (self.home / "models_cache.json").unlink()
        self.assertEqual("fallback", self.resolve()["resolution"])

    def test_no_match_and_no_last_good_is_refused_not_invented(self):
        write_cache(self.home, _models(("gpt-6-luna", "list", ALL)))
        with self.assertRaises(ValueError) as cm:
            self.resolve()
        self.assertIn("last-good", str(cm.exception))

    def test_another_tiers_last_good_id_is_not_used(self):
        self.home.mkdir(parents=True)
        self.state.write_text(json.dumps({"sol": {"model": "gpt-6-luna", "effort": "high"}}), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.resolve()

    # ---- the result line's new fields -----------------------------------------------------------------------------

    def test_a_verdict_line_reads_as_the_schemas_outcome(self):
        sha = "a" * 40
        for text, outcome, verdict in (
                (f"notes\nVERDICT: ACCEPT {sha}\n", "APPROVED", f"VERDICT: ACCEPT {sha}"),
                (f"VERDICT: REJECT {sha}\n\n", "CHANGES_REQUESTED", f"VERDICT: REJECT {sha}"),
                (f"VERDICT: REFUSE {sha}", "REFUSED", f"VERDICT: REFUSE {sha}"),
                (f"VERDICT: ACCEPT {sha}\nand one more line", "UNKNOWN", None),      # only the LAST line counts
                ("VERDICT: MAYBE", "UNKNOWN", None), ("", "UNKNOWN", None)):
            with self.subTest(text=text):
                self.assertEqual((outcome, verdict), self.mod.read_verdict(text))

    def test_tokens_are_read_only_from_a_reported_total_never_guessed(self):
        final = "VERDICT: ACCEPT " + "a" * 40 + "\n"
        shape = f"codex\n{final}tokens used\n12,345\n{final}"
        self.assertEqual(12345, self.mod.tokens_used("exec\nls\n" + shape, final))
        self.assertIsNone(self.mod.tokens_used("exec\nls\ncodex\n" + final, final))
        self.assertIsNone(self.mod.tokens_used("tokens used\nmany\n", ""))

    def test_a_pair_quoted_in_the_echoed_prompt_is_not_the_runs_report(self):
        # K6 key round 1 on 25c0ef22: a review prompt that quotes a codex transcript carries `tokens used` / a count.
        prompt = "Review this transcript:\ntokens used\n999\nthat is all.\n"
        final = "VERDICT: ACCEPT\n"
        echoed = "OpenAI Codex v1\nuser\n" + prompt
        self.assertIsNone(self.mod.tokens_used(echoed + "codex\n" + final + final, final, prompt))
        self.assertEqual(12345, self.mod.tokens_used(
            echoed + "codex\n" + final + "tokens used\n12,345\n" + final, final, prompt))
        # a real report that happens to sit BEFORE the prompt-less default still reads, and the default is unchanged
        self.assertEqual(999, self.mod.tokens_used(echoed, "", ""))

    # ---- the CLI (production wiring, against the fake codex) ------------------------------------------------------

    def cli(self, role: str, mode: str = "echo", final: str | None = None, models=None, age=timedelta(0),
            write: bool = True, prompt: str = "Review this.\n", no_tokens: bool = False) -> subprocess.CompletedProcess:
        bin_dir = self.root / "bin"
        if not bin_dir.exists():
            bin_dir.mkdir()
            _write_fake_codex(bin_dir)
        (self.root / "worktree").mkdir(exist_ok=True)
        (self.root / "prompt.md").write_text(prompt, encoding="utf-8")
        if write:
            write_cache(self.home, models, age)
        env = dict(os.environ)
        env.update({"PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""), "ARGV_LOG": str(self.root / "argv.json"),
                    "FAKE_CODEX_MODE": mode, "FAKE_CODEX_LAST": "write", "CODEX_HOME": str(self.home)})
        env.pop("FAKE_CODEX_FINAL", None)
        env.pop("FAKE_CODEX_NO_TOKENS", None)
        if no_tokens:
            env["FAKE_CODEX_NO_TOKENS"] = "1"
        if final is not None:
            env["FAKE_CODEX_FINAL"] = final
        return subprocess.run([sys.executable, str(TOOL), "--role", role, "--cd", str(self.root / "worktree"),
                               "--prompt-file", str(self.root / "prompt.md"), "--out", str(self.root / "out.txt")],
                              env=env, capture_output=True, text=True, timeout=60, cwd=str(self.root))

    def line(self, proc) -> dict:
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_cli_launches_the_resolved_id_and_records_the_selector_and_the_resolution(self):
        proc = self.cli("counterpart")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        argv = json.loads((self.root / "argv.json").read_text(encoding="utf-8"))
        self.assertEqual("gpt-6.1-sol", argv[argv.index("-m") + 1])
        self.assertEqual("model_reasoning_effort=high", argv[argv.index("-c") + 1])
        got = self.line(proc)
        self.assertEqual(("sol", "gpt-6.1-sol", "high", "high", "cache", None, None),
                         tuple(got[k] for k in ("model_requested", "model_effective", "effort_requested",
                                                "effort_effective", "resolution", "resolution_reason", "stale")))
        self.assertEqual(("gpt-6.1-sol", "ok"), (got["requested_model"], got["tier"]))

    def test_cli_census_role_launches_luna_at_high(self):
        proc = self.cli("census")
        got = self.line(proc)
        self.assertEqual(("gpt-6-luna", "high", "luna", "ok"),
                         (got["requested_model"], got["requested_effort"], got["model_requested"], got["tier"]))

    def test_cli_fallback_launches_the_last_good_id_and_records_the_fallback(self):
        self.assertEqual(0, self.cli("counterpart").returncode)               # records gpt-6.1-sol
        proc = self.cli("counterpart", models=_models(("gpt-6-sol", "list", ALL)), age=timedelta(days=9))
        got = self.line(proc)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(("gpt-6.1-sol", "gpt-6.1-sol", "fallback", "ok"),
                         (got["requested_model"], got["model_effective"], got["resolution"], got["tier"]))
        self.assertIn("7 days", got["resolution_reason"])
        self.assertIsNotNone(got["stale"])

    def test_cli_a_pair_quoted_in_the_prompt_is_not_recorded_as_the_runs_tokens(self):
        quoted = "Review this transcript:\ntokens used\n999\nthat is all.\n"
        proc = self.cli("counterpart", mode="transcript", prompt=quoted, no_tokens=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        got = self.line(proc)
        self.assertIsNone(got["tokens_used"])
        self.assertIn("tokens used", (self.root / "out.txt").read_text(encoding="utf-8"))   # the echo is in the transcript
        real = self.line(self.cli("counterpart", mode="transcript", prompt=quoted))
        self.assertEqual(1234, real["tokens_used"])

    def test_cli_refuses_an_unresolvable_tier_without_calling_codex(self):
        proc = self.cli("counterpart", write=False)
        self.assertEqual(2, proc.returncode)
        self.assertIn("refused", proc.stderr)
        self.assertFalse((self.root / "argv.json").exists())

    def test_cli_result_carries_the_outcome_the_tokens_and_the_measurement(self):
        final = "Findings.\nVERDICT: REJECT " + "b" * 40 + "\n"
        proc = self.cli("counterpart", mode="transcript", final=final)
        got = self.line(proc)
        self.assertEqual(("CHANGES_REQUESTED", "VERDICT: REJECT " + "b" * 40, 1234),
                         (got["outcome"], got["verdict"], got["tokens_used"]))
        m = got["measurement"]
        self.assertEqual(("codex-review", None, None, None, None), (m["source"], m["input_tokens"],
                         m["cached_input_tokens"], m["reasoning_tokens"], m["output_tokens"]))
        self.assertIsInstance(m["active_seconds"], float)
        self.assertGreaterEqual(m["active_seconds"], 0)


class SameFileTests(unittest.TestCase):
    """K6 key on 098e118: in a Windows case-sensitive directory `prompt.md` and `PROMPT.MD` are two files, but WindowsPath
    equality folds case. When both names exist the file system decides; path equality only answers for a missing one."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("codex_review_same_file", TOOL)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_two_existing_files_the_file_system_calls_distinct_are_not_one_file(self):
        a = self.root / "prompt.md"
        a.write_text("p", encoding="utf-8")
        b = self.root / "PROMPT.MD"            # on an ordinary directory the same file; the stub plays a case-sensitive one
        real = self.mod.os.path.samefile
        self.mod.os.path.samefile = lambda x, y: False
        self.addCleanup(setattr, self.mod.os.path, "samefile", real)
        self.assertFalse(self.mod.same_file(a, b))

    def test_two_existing_names_of_one_file_are_one_file(self):
        a = self.root / "prompt.md"
        a.write_text("p", encoding="utf-8")
        self.assertTrue(self.mod.same_file(a, self.root / "sub" / ".." / "prompt.md"))

    def test_when_the_file_system_cannot_answer_the_names_are_refused_as_one(self):
        """K6 key on e586556: samefile raising (a name vanished between the checks) fell back to case-folding path
        equality. Now the names are refused as one, whatever their spelling: the safe side, never a guess."""
        a = self.root / "prompt.md"
        a.write_text("p", encoding="utf-8")
        b = self.root / "other.md"
        b.write_text("o", encoding="utf-8")

        def raises(x, y):
            raise OSError("vanished")
        real = self.mod.os.path.samefile
        self.mod.os.path.samefile = raises
        self.addCleanup(setattr, self.mod.os.path, "samefile", real)
        self.assertTrue(self.mod.same_file(a, b))

    def test_an_existing_name_and_a_missing_one_are_two_files(self):
        """K6 key on 748cef0: in a case-sensitive directory holding only `prompt.md`, `PROMPT.MD` is a new, valid
        output; the file system does not find it, so it is not the prompt. The stub plays that directory."""
        a = self.root / "prompt.md"
        a.write_text("p", encoding="utf-8")
        b = self.root / "PROMPT.MD"
        real = self.mod.os.path.exists
        self.mod.os.path.exists = lambda p: Path(p).name == "prompt.md" and real(p)
        self.addCleanup(setattr, self.mod.os.path, "exists", real)
        self.assertFalse(self.mod.same_file(b, a))
        self.assertFalse(self.mod.same_file(a, b))
        self.assertFalse(self.mod.same_file(self.root / "other.md", a))

    def test_two_missing_names_that_fold_to_one_path_are_refused_as_one(self):
        """Limit N2: neither exists yet and the tool does not read the directory's case flag, so they are refused as one."""
        self.assertTrue(self.mod.same_file(self.root / "out.txt", self.root / "x" / ".." / "out.txt"))
        self.assertFalse(self.mod.same_file(self.root / "out.txt", self.root / "last.txt"))

if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests([loader.loadTestsFromTestCase(tc) for tc in
                     (CodexReviewCliTests, RoleTableMatchesTheDocTests, SameFileTests, TierResolutionTests)])
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
