#!/usr/bin/env python3
"""Bus K154 pins for the factory kernel as pinned tools.   python tools/factory/kernel-tools.tests.py

  * FACTORY_KERNEL_CONFIG names the config a pinned kernel tool reads (it runs from a private directory);
  * factory-config.schema.json and the loader of record (kernel-subjects.py load_config) name the same keys;
  * kernel-config.py judges a config with that loader;
  * end to end: a throwaway bus holding these files and a fresh `git init` consumer seeded from
    fixtures/kernel/seed-repo/ pin the kernel through pin-runner.py; `run kernel-subjects -- check HEAD --json`
    answers OK (exit 0), the kernel-receipt and kernel-config groups load their siblings, an out-of-order packet
    reads ORDER-VIOLATION (exit 1), and a flipped byte in the vendored runner fails `verify`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE / "fixtures" / "kernel" / "seed-repo"
CLOUDVORE_CONFIG = HERE / "fixtures" / "kernel" / "cloudvore.factory-config.json"
SCHEMA = HERE / "factory-config.schema.json"
BUS_FILES = ("pin-runner.py", "kernel-subjects.py", "kernel-receipt.py", "codex-review.py", "kernel-config.py")


def git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                           "-c", "core.autocrlf=false", *a], check=True, capture_output=True, text=True).stdout.strip()


def env_without(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("FACTORY_KERNEL_CONFIG", "FACTORY_BUS_CLONE")}
    env.update(extra)
    return env


def load_subjects(config: str | None):
    """kernel-subjects.py loaded in this process with FACTORY_KERNEL_CONFIG set to `config` (None: unset)."""
    saved = os.environ.pop("FACTORY_KERNEL_CONFIG", None)
    try:
        if config is not None:
            os.environ["FACTORY_KERNEL_CONFIG"] = config
        spec = importlib.util.spec_from_file_location("ks_under_test", HERE / "kernel-subjects.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        os.environ.pop("FACTORY_KERNEL_CONFIG", None)
        if saved is not None:
            os.environ["FACTORY_KERNEL_CONFIG"] = saved


class ConfigLocation(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_variable_names_the_config(self):
        ks = load_subjects(str(SEED / "factory-config.json"))
        self.assertEqual(("seed/", "seed-runner"), (ks.SUBJECT_PREFIX, ks.BAR_RUNNER))
        ks = load_subjects(str(CLOUDVORE_CONFIG))
        self.assertEqual(("cloudvore/", "ultra-magnus-cloudvore"), (ks.SUBJECT_PREFIX, ks.BAR_RUNNER))

    def test_unset_or_empty_refuses_naming_the_variable_and_a_missing_named_file_is_refused(self):
        """Bus key on K154 packet 2, finding 4: an unset (or empty) FACTORY_KERNEL_CONFIG never falls back to a
        factory-config.json beside the tool, even run by absolute path with one sitting there: exit 2 naming the
        variable, nothing printed on stdout."""
        kit = self.tmp / "kit"
        kit.mkdir()
        shutil.copyfile(HERE / "kernel-subjects.py", kit / "kernel-subjects.py")
        shutil.copyfile(SEED / "factory-config.json", kit / "factory-config.json")
        for env in (env_without(), env_without(FACTORY_KERNEL_CONFIG="")):
            p = subprocess.run([sys.executable, str(kit / "kernel-subjects.py"), "block", "--row", "S2", "--filter",
                                "tests/x.py", "--bus-sha", "abcdef0"], capture_output=True, text=True, env=env)
            self.assertEqual((2, ""), (p.returncode, p.stdout), p.stderr)
            self.assertIn("REFUSE kernel-subjects: ", p.stderr)
            self.assertIn("FACTORY_KERNEL_CONFIG", p.stderr)
            self.assertNotIn("Traceback", p.stderr)
        p = subprocess.run([sys.executable, str(kit / "kernel-subjects.py"), "block", "--row", "S2", "--filter",
                            "tests/x.py", "--bus-sha", "abcdef0"], capture_output=True, text=True,
                           env=env_without(FACTORY_KERNEL_CONFIG=str(kit / "factory-config.json")))
        self.assertEqual((0, True), (p.returncode, "- subject: seed/S2\n" in p.stdout), p.stderr)
        p = subprocess.run([sys.executable, str(kit / "kernel-subjects.py"), "advisory"], capture_output=True,
                           text=True, env=env_without(FACTORY_KERNEL_CONFIG=str(self.tmp / "absent.json")))
        self.assertEqual(2, p.returncode)
        self.assertIn("REFUSE kernel-subjects: the config", p.stderr)
        self.assertIn("absent.json is missing", p.stderr)

    def test_a_relative_name_resolves_against_the_callers_cwd(self):
        p = subprocess.run([sys.executable, str(HERE / "kernel-subjects.py"), "block", "--row", "S3", "--filter",
                            "tests/x.py", "--bus-sha", "abcdef0"], capture_output=True, text=True, cwd=str(SEED),
                           env=env_without(FACTORY_KERNEL_CONFIG="factory-config.json"))
        self.assertEqual((0, True), (p.returncode, "- subject: seed/S3\n" in p.stdout), p.stderr)


class SchemaMatchesTheLoader(unittest.TestCase):
    def test_same_sections_and_keys(self):
        ks = load_subjects(str(SEED / "factory-config.json"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual({"ranker", "evidence"}, set(ks._OPTIONAL_SECTIONS))
        self.assertEqual({"schema", "about", *ks._CONFIG_KEYS} - ks._OPTIONAL_SECTIONS, set(schema["required"]))
        self.assertEqual({"schema", "about", *ks._CONFIG_KEYS}, set(schema["properties"]))
        self.assertEqual(ks.CONFIG_SCHEMA, schema["properties"]["schema"]["const"])
        for section, keys in ks._CONFIG_KEYS.items():
            with self.subTest(section=section):
                node = schema["properties"][section]
                self.assertEqual(set(keys), set(node["required"]))
                self.assertEqual(set(keys), set(node["properties"]))
                self.assertFalse(node["additionalProperties"])

    def test_both_fixture_configs_load(self):
        for cfg in (SEED / "factory-config.json", CLOUDVORE_CONFIG):
            with self.subTest(config=cfg.name):
                self.assertIn("subject", load_subjects(str(cfg)).CONFIG)


class OptionalSections(unittest.TestCase):
    """Bus K154 packet 2 (coordinator ruling 2026-10-18): `ranker` and `evidence` are optional. A project's stub
    config without them runs the kernel at exit 0 with both features off (nothing defaulted in); a section that is
    present is validated strictly and a malformed one is refused, naming the key."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.stub = json.loads((SEED / "factory-config.json").read_text(encoding="utf-8"))
        for section in ("ranker", "evidence"):
            self.stub.pop(section, None)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, data: dict, name: str = "stub.json") -> Path:
        path = self.tmp / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_a_stub_without_ranker_or_evidence_reaches_exit_0_with_both_features_off(self):
        stub = self.write(self.stub)
        p = subprocess.run([sys.executable, str(HERE / "kernel-config.py"), "check", str(stub)], capture_output=True,
                           text=True, env=env_without())
        self.assertEqual((0, True), (p.returncode, p.stdout.startswith("CONFIG OK ")), p.stderr)
        ks = load_subjects(str(stub))
        self.assertEqual(set(), {"ranker", "evidence"} & set(ks.CONFIG))      # off: nothing defaulted in
        p = subprocess.run([sys.executable, str(HERE / "kernel-subjects.py"), "block", "--row", "S2", "--filter",
                            "tests/x.py", "--bus-sha", "abcdef0"], capture_output=True, text=True,
                           env=env_without(FACTORY_KERNEL_CONFIG=str(stub)))
        self.assertEqual((0, True), (p.returncode, "- subject: seed/S2\n" in p.stdout), p.stderr)
        for word in ("evidence-store", "evidence.", "ranker", "starvation"):
            self.assertNotIn(word, p.stdout)

    def test_a_malformed_present_section_is_refused_naming_the_key(self):
        cases = (
            ("ranker", {"starvation_window": 0}, "ranker.starvation_window"),
            ("ranker", {"starvation_window": True}, "ranker.starvation_window"),
            ("ranker", {}, "has no ranker.starvation_window"),
            ("ranker", [4], "has ranker that is not an object"),
            ("evidence", {"branch": "master", "worktree": "w"}, "evidence.branch"),
            ("evidence", {"branch": "evidence-store"}, "has no evidence.worktree"),
            ("evidence", {"branch": "evidence-store", "worktree": "w", "limit": 1}, "unknown key evidence.limit"),
            ("evidence", {"branch": "evidence-store", "worktree": "../w"}, "evidence.worktree"),
        )
        for section, value, says in cases:
            with self.subTest(section=section, value=value):
                bad = self.write({**self.stub, section: value}, "bad.json")
                p = subprocess.run([sys.executable, str(HERE / "kernel-config.py"), "check", str(bad)],
                                   capture_output=True, text=True, env=env_without())
                self.assertEqual(2, p.returncode, p.stdout)
                self.assertIn(says, p.stderr)

    def test_both_sections_present_and_well_formed_load(self):
        good = self.write({**self.stub, "ranker": {"starvation_window": 4},
                           "evidence": {"branch": "evidence-store", "worktree": "seed-evidence-store"}})
        ks = load_subjects(str(good))
        self.assertEqual((4, "evidence-store"), (ks.CONFIG["ranker"]["starvation_window"],
                                                 ks.CONFIG["evidence"]["branch"]))


STUB_GOLDEN = HERE / "fixtures" / "kernel" / "stub-golden"
# What bus origin/master 69d7d63e's kernel-subjects.py printed for the stub project (the seed config, which carries
# neither optional section), written once by running that file through stub_outputs(); the reference never moves.
STUB_RUNS = {
    "check-json": ["check", "HEAD", "--json"],
    "check": ["check", "HEAD"],
    "advisory-json": ["advisory", "--json"],
    "block": ["block", "--row", "S2", "--filter", "tests/x.py", "--bus-sha", "abcdef0"],
}


def stub_outputs(tool: Path, tmp: Path) -> dict[str, bytes]:
    """`tool` (a kernel-subjects.py) run over a deterministic stub project: the seed config and queue, a brief-first
    packet on work/S1, fixed identities and dates (so every SHA is the same on every machine). Each run's exit code
    and stdout, as bytes with LF line ends."""
    repo = tmp / "stub-repo"
    repo.mkdir()
    genv = env_without(GIT_AUTHOR_DATE="2026-10-18T00:00:00+00:00", GIT_COMMITTER_DATE="2026-10-18T00:00:00+00:00",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
                       GIT_COMMITTER_EMAIL="t@example.invalid")

    def g(*a: str) -> None:
        subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=false", *a], check=True, capture_output=True,
                       env=genv)
    g("init", "-q", "-b", "master")
    for rel, msg in ((None, "seed project"), ("review/briefs/s1.md", "S1 brief"), ("src/hello.py", "S1 product")):
        if rel is None:
            for name in ("factory-config.json", "QUEUE.md"):
                (repo / name).write_bytes((SEED / name).read_bytes().replace(b"\r\n", b"\n"))
            g("add", "factory-config.json", "QUEUE.md")
        else:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_bytes((SEED / rel).read_bytes().replace(b"\r\n", b"\n"))
            g("add", rel)
        g("commit", "-qm", msg)
        if rel is None:
            g("update-ref", "refs/remotes/origin/master", "HEAD")
            g("checkout", "-qb", "work/S1")
    out = {}
    for name, args in STUB_RUNS.items():
        p = subprocess.run([sys.executable, str(tool), *args], capture_output=True, cwd=str(repo),
                           env=env_without(FACTORY_KERNEL_CONFIG="factory-config.json"))
        out[name] = f"exit={p.returncode}\n".encode() + p.stdout.replace(b"\r\n", b"\n")
    return out


class OptionalSectionsOutput(unittest.TestCase):
    """Bus key on K154 packet 2, finding 5: the bus has no consumer of `ranker` or `evidence` (Cloudvore's next.py and
    evidence-store.py check for them themselves), so what is pinned is what the bus tool emits: with both sections
    absent, kernel-subjects' output is byte-identical to bus master's on the same stub and names neither."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_stub_carries_neither_section(self):
        data = json.loads((SEED / "factory-config.json").read_text(encoding="utf-8"))
        self.assertEqual(set(), {"ranker", "evidence"} & set(data))

    def test_kernel_subjects_output_on_the_stub_is_byte_identical_to_bus_masters(self):
        got = stub_outputs(HERE / "kernel-subjects.py", self.tmp)
        self.assertEqual(set(STUB_RUNS), {p.stem for p in STUB_GOLDEN.glob("*.txt")})
        for name, data in got.items():
            with self.subTest(run=name):
                self.assertEqual(STUB_GOLDEN.joinpath(f"{name}.txt").read_bytes().replace(b"\r\n", b"\n"), data)
                for word in (b"ranker", b"starvation", b"evidence-store", b"evidence."):
                    self.assertNotIn(word, data)
        self.assertTrue(got["check-json"].startswith(b"exit=0\n"), got["check-json"])
        self.assertIn(b'"status": "OK"', got["check-json"])


class KernelConfigTool(unittest.TestCase):
    def run_kc(self, *a: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HERE / "kernel-config.py"), *a], capture_output=True, text=True,
                              env=env_without())

    def test_a_good_config_passes_and_a_bad_one_is_refused_naming_the_key(self):
        p = self.run_kc("check", str(SEED / "factory-config.json"))
        self.assertEqual((0, True), (p.returncode, p.stdout.startswith("CONFIG OK ")), p.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads((SEED / "factory-config.json").read_text(encoding="utf-8"))
            data["bar"]["colour"] = "green"
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps(data), encoding="utf-8")
            p = self.run_kc("check", str(bad))
            self.assertEqual(2, p.returncode)
            self.assertIn("has an unknown key bar.colour", p.stderr)
        self.assertEqual(2, self.run_kc("verify", "x").returncode)


class SeedProjectThroughThePinRunner(unittest.TestCase):
    """The packet-1 acceptance shape, against a throwaway bus built from this directory's files."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.bus, self.repo, self.cache = t / "bus", t / "seed", t / "cache"
        (self.bus / "tools" / "factory").mkdir(parents=True)
        git(self.bus, "init", "-q")
        for name in BUS_FILES:            # as the bus stores them: LF blobs
            (self.bus / "tools" / "factory" / name).write_bytes((HERE / name).read_bytes().replace(b"\r\n", b"\n"))
        git(self.bus, "add", "-A")
        git(self.bus, "commit", "-qm", "kernel")
        git(self.bus, "update-ref", "refs/remotes/origin/master", "HEAD")
        self.commit = git(self.bus, "rev-parse", "HEAD")

        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "master")
        for rel in ("factory-config.json", "QUEUE.md"):
            shutil.copyfile(SEED / rel, self.repo / rel)
        pins = self.repo / "factory-pins"
        pins.mkdir()
        (pins / "pin-runner.py").write_bytes((self.bus / "tools" / "factory" / "pin-runner.py").read_bytes())
        (pins / "factory-pins.json").write_text(json.dumps({"schema": "factory-pins.v1", "bus_clone": [str(self.bus)],
                                                            "tools": {}}), encoding="utf-8")
        self.pr("adopt-runner", "--commit", self.commit)
        for tool, extra in (("kernel-subjects", ()), ("codex-review", ()),
                            ("kernel-receipt", ("--with", "kernel-subjects", "--with", "codex-review")),
                            ("kernel-config", ("--with", "kernel-subjects"))):
            self.pr("pin", tool, "--commit", self.commit, "--path", f"tools/factory/{tool}.py",
                    "--reviewer", "seed-test", "--reason", "fixture", *extra)
        git(self.repo, "add", "factory-config.json", "QUEUE.md", "factory-pins")
        git(self.repo, "commit", "-qm", "seed project")

    def tearDown(self):
        self._tmp.cleanup()

    def pr(self, *a: str, isolated: bool = False, check: bool = True) -> subprocess.CompletedProcess:
        env = env_without(FACTORY_PINS_CACHE=str(self.cache), FACTORY_KERNEL_CONFIG="factory-config.json")
        p = subprocess.run([sys.executable, *(["-I"] if isolated else []), str(self.repo / "factory-pins" / "pin-runner.py"),
                            *a], capture_output=True, text=True, cwd=str(self.repo), env=env)
        if check:
            self.assertEqual(0, p.returncode, p.stdout + p.stderr)
        return p

    def packet(self, brief_first: bool = True) -> None:
        git(self.repo, "checkout", "-qb", "work/S1")
        git(self.repo, "update-ref", "refs/remotes/origin/master", "master")
        steps = [("review/briefs/s1.md", "S1 brief"), ("src/hello.py", "S1 product")]
        for rel, msg in (steps if brief_first else steps[::-1]):
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SEED / rel, self.repo / rel)
            git(self.repo, "add", rel)
            git(self.repo, "commit", "-qm", msg)

    def test_check_head_answers_ok_through_the_runner(self):
        self.packet()
        for iso in (False, True):
            p = self.pr("run", "kernel-subjects", "--", "check", "HEAD", "--json", isolated=iso)
            got = json.loads(p.stdout)
            self.assertEqual(("seed/S1", "OK", [], False), (got["subject"], got["status"], got["flags"], got["landing"]))
            # the seed config carries neither optional section: both features off, no field for either
            self.assertEqual(set(), {"evidence", "ranker", "starvation_window"} & set(got))
            p = self.pr("run", "kernel-subjects", "--", "check", "HEAD", isolated=iso)
            self.assertTrue(p.stdout.startswith("seed/S1 OK branch="), p.stdout)

    def test_a_product_before_its_brief_reads_order_violation(self):
        self.packet(brief_first=False)
        p = self.pr("run", "kernel-subjects", "--", "check", "HEAD", "--json", check=False)
        self.assertEqual((1, "ORDER-VIOLATION"), (p.returncode, json.loads(p.stdout)["status"]), p.stderr)

    def test_the_groups_load_their_verified_siblings(self):
        for iso in (False, True):
            p = self.pr("run", "kernel-receipt", "--", "--help", isolated=iso)
            self.assertIn("--merge", p.stdout)
            p = self.pr("run", "kernel-config", "--", "check", "factory-config.json", isolated=iso)
            self.assertTrue(p.stdout.startswith("CONFIG OK factory-config.json"), p.stdout)

    def test_a_group_tool_pinned_without_its_members_refuses_and_never_loads_the_callers_sibling(self):
        # Bus review of K154: in-process (python -I) a pin without `with` runs with __file__ = the relative bus path,
        # so a sibling load resolved against the caller's cwd and ran an unpinned decoy from the caller's tree.
        decoy = self.repo / "tools" / "factory"
        decoy.mkdir(parents=True)
        for sib in ("kernel-subjects.py", "codex-review.py"):
            (decoy / sib).write_text("print('DECOY-RAN')\nraise SystemExit(42)\n", encoding="utf-8")
        for tool in ("kernel-receipt", "kernel-config"):
            pins_file = self.repo / "factory-pins" / "factory-pins.json"
            pins = json.loads(pins_file.read_text(encoding="utf-8"))
            pins["tools"][tool].pop("with")
            pins_file.write_text(json.dumps(pins), encoding="utf-8")
            for iso in (False, True):
                with self.subTest(tool=tool, isolated=iso):
                    a = ("--", "--help") if tool == "kernel-receipt" else ("--", "check", "factory-config.json")
                    p = self.pr("run", tool, *a, isolated=iso, check=False)
                    self.assertEqual(2, p.returncode, p.stdout + p.stderr)
                    self.assertNotIn("DECOY-RAN", p.stdout + p.stderr)
                    self.assertIn(f"REFUSE {tool}", p.stderr)

    def test_unset_config_variable_refuses_and_never_reads_a_config_from_the_callers_tree(self):
        # Bus review of K154: in-process, "beside this file" resolved against the caller's cwd.
        planted = self.repo / "tools" / "factory"
        planted.mkdir(parents=True)
        cfg = json.loads((SEED / "factory-config.json").read_text(encoding="utf-8"))
        cfg["subject"]["prefix"] = "planted/"
        (planted / "factory-config.json").write_text(json.dumps(cfg), encoding="utf-8")
        env = env_without(FACTORY_PINS_CACHE=str(self.cache))
        for iso in (False, True):
            with self.subTest(isolated=iso):
                p = subprocess.run([sys.executable, *(["-I"] if iso else []),
                                    str(self.repo / "factory-pins" / "pin-runner.py"), "run", "kernel-subjects", "--",
                                    "block", "--row", "S2", "--filter", "t.py", "--bus-sha", "abcdef0"],
                                   capture_output=True, text=True, cwd=str(self.repo), env=env)
                self.assertEqual(2, p.returncode, p.stdout + p.stderr)
                self.assertNotIn("planted/", p.stdout)
                self.assertIn("REFUSE kernel-subjects", p.stderr)

    def test_verify_passes_then_fails_on_one_flipped_byte_and_passes_restored(self):
        self.pr("verify")
        runner = self.repo / "factory-pins" / "pin-runner.py"
        good = runner.read_bytes()
        i = good.index(b"pinned GROUP")
        runner.write_bytes(good[:i] + b"P" + good[i + 1:])
        p = self.pr("verify", check=False)
        self.assertEqual(2, p.returncode)
        self.assertIn("DRIFT runner", p.stdout)
        runner.write_bytes(good)
        self.pr("verify")

    def test_a_pin_naming_other_bytes_refuses_and_runs_nothing(self):
        self.packet()
        pins_file = self.repo / "factory-pins" / "factory-pins.json"
        pins = json.loads(pins_file.read_text(encoding="utf-8"))
        pins["tools"]["kernel-subjects"]["sha256"] = "0" * 64
        pins_file.write_text(json.dumps(pins), encoding="utf-8")
        p = self.pr("run", "kernel-receipt", "--", "--help", check=False)    # a group member's pin is checked too
        self.assertEqual((2, ""), (p.returncode, p.stdout))
        p = self.pr("run", "kernel-subjects", "--", "check", "HEAD", "--json", check=False)
        self.assertEqual((2, ""), (p.returncode, p.stdout))


if __name__ == "__main__":
    unittest.main(verbosity=1)
