"""tools/review-posture: the posture is a measurement, the runner cannot silently drop a role, and parsing never guesses.

Each test names the failure it pins (magic-lantern_dannephoto, 2026-09-14): a review filed as `conjugal-standard`
that ran 5 of 17 lanes; a prompt bound to the literal text `$SUBJECT`; a permissive parser that read
"78.73 + 1.5 = 80.23" as a ceiling of 78.73.
"""
import importlib.util, json, os, pathlib, re, shutil, subprocess, tempfile, unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "review-posture"
spec = importlib.util.spec_from_file_location("review_posture", TOOL / "review_posture.py")
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)

SUBJECT = str(ROOT / "specs" / "conjugal-approach-a-v7.4.md")


def _bash():
    # On Windows `which bash` can resolve to System32\bash.exe (WSL), which sees neither these paths nor the CLIs --
    # measured while writing this test. Prefer Git Bash; refuse WSL.
    for c in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe", shutil.which("bash")):
        if c and os.path.exists(c) and "system32" not in c.lower():
            return c
    return None


BASH = _bash()
INVENTORY = """providers:
  claude:
    models:
      fable: claude-fable-5
      haiku: claude-haiku-4-5-20251001
      opus: claude-opus-5
      sonnet: claude-sonnet-5
  codex:
    models:
      astra: gpt-6-astra
      luna: gpt-5.6-luna
      sol: gpt-5.6-sol
"""
PANEL_OK = """{seat} SCORES:
Timeline Realism: 70
Contract Completeness: 80
Cross-Family Safety: 90
Autonomy Achievement: 80
Throughput Goal: 60
Risk Mitigation: 80
COMPOSITE: 99.9
TOP 3 REMAINING BLOCKERS: one "quote"
LANE-COMPLETE
"""


class Env(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        (self.tmp / "inv.yaml").write_text(INVENTORY, encoding="utf-8")
        self.env = mock.patch.dict(os.environ, {"RP_OUT": str(self.tmp / "out"), "RP_SUBJECT": SUBJECT,
                                                "RP_BENCH": str(self.tmp), "RP_INVENTORY": str(self.tmp / "inv.yaml")})
        self.env.start()
        self.out = self.tmp / "out"; self.out.mkdir()

    def tearDown(self):
        self.env.stop(); shutil.rmtree(self.tmp, ignore_errors=True)

    def lane(self, name, text="finding\nLANE-COMPLETE\n"):
        (self.out / f"{name}.txt").write_text(text, encoding="utf-8")

    def all_lanes(self, skip=()):
        for l in rp.lanes():
            if l["name"] not in skip:
                self.lane(l["name"])


class RolesMatchSpec(unittest.TestCase):
    def test_roles_json_names_exactly_the_spec_table_roles(self):
        text = (ROOT / "specs" / "posture-templates-conjugal-standard.md").read_text(encoding="utf-8")
        table = set(re.findall(r"^\|\s*\*\*([A-Za-z-]+)\*\*\s*\|", text, re.M))
        self.assertEqual(table, {r["role"] for r in rp.roles()["roles"]},
                         "roles.json and the posture template's roles table drifted; change both or neither")

class Posture(Env):
    def test_complete_only_when_every_lane_cleared(self):
        self.all_lanes()
        r = rp.posture()
        self.assertTrue(r["complete"]); self.assertIn("COMPLETE (17/17", r["line"]); self.assertEqual(r["cross_family"], "validated")

    def test_designers_and_lint_alone_are_partial(self):
        for n in ("design-scope", "design-verify", "lint-claude", "lint-codex", "arbiter"):
            self.lane(n)
        r = rp.posture()
        self.assertFalse(r["complete"])
        self.assertIn("PARTIAL (5/17", r["line"])
        for role in ("Consolidator 0/1", "Panel 0/8", "Classifier 0/3"):
            self.assertIn(role, r["line"])

    def test_one_missing_panel_seat_is_partial(self):
        self.all_lanes(skip=("panel-luna",))
        self.assertIn("Panel 7/8", rp.posture()["line"])

    def test_inline_sentinel_does_not_count(self):
        self.all_lanes(skip=("classifier-2",))
        self.lane("classifier-2", "I will end with LANE-COMPLETE once done\n")
        self.assertFalse(rp.posture()["complete"])

    def test_single_family_is_not_cross_family(self):
        for l in rp.lanes():
            if l["family"] == "claude":
                self.lane(l["name"])
        self.assertEqual(rp.posture()["cross_family"], "NO-CROSS-FAMILY-VALIDATION")


class Score(Env):
    def test_composite_recomputed_not_trusted_and_bad_seats_recorded(self):
        for l in rp.lanes("B", "Panel"):
            self.lane(l["name"], PANEL_OK.format(seat=l["name"]))
        self.lane("panel-luna", "LUNA SCORES:\nTimeline Realism: 70\nLANE-COMPLETE\n")
        self.lane("panel-sol", PANEL_OK.format(seat="sol").replace("LANE-COMPLETE", ""))
        with mock.patch("builtins.print"):
            r = rp.score()
        self.assertEqual(r["seats_scored"], 6)
        self.assertEqual(r["rows"][0]["composite"], 76.67)
        self.assertIn("panel-luna:unparseable", r["missing"]); self.assertIn("panel-sol:no-sentinel", r["missing"])


class Tally(Env):
    def test_strict_parse_and_two_of_three(self):
        self.lane("classifier-1", "CLASSIFY\nF1: DESIGN GROUNDED - x\nF2: TEXT GROUNDED - y\nMUST-FIX: F1, F2\n"
                                  "STOPPING: FLAT\nCEILING: 80.5\nLANE-COMPLETE\n")
        self.lane("classifier-2", "**F1: DESIGN GROUNDED** x\nF2: DESIGN UNGROUNDED y\n## MUST-FIX\n\nF1\n\nF2 is only architectural\n"
                                  "## STOPPING\n\nFLAT\n## CEILING\n\n78.73 (current) + 1.5 = 80.23\nLANE-COMPLETE\n")
        self.lane("classifier-3", "F1: §4 K5 evidence | DESIGN GROUNDED | label before the verdict\nF2: TEXT UNGROUNDED\nMUST-FIX: F1\nSTOPPING\nFLAT because reasons\n"
                                  "CEILING: 79\nLANE-COMPLETE\n")
        with mock.patch("builtins.print"):
            r = rp.tally()
        self.assertEqual(r["findings"]["F1"]["must_fix_votes"], 3)
        self.assertEqual(r["findings"]["F2"]["must_fix_votes"], 1, "must-fix list must not run past its line into prose")
        self.assertEqual(r["findings"]["F2"]["kind"], "TEXT"); self.assertEqual(r["findings"]["F2"]["grounded"], "UNGROUNDED")
        self.assertEqual(r["stopping"], "FLAT")
        self.assertEqual(sorted(r["ceilings"]), [79.0, 80.5], "a ceiling inside arithmetic prose is unparsed, never guessed")
        self.assertIn("classifier-2:CEILING", r["unparsed"]); self.assertIn("classifier-3:STOPPING", r["unparsed"])


class Prompts(Env):
    def test_every_prompt_is_bound_and_asks_for_the_sentinel(self):
        rp.prompts_a(); rp.prompts_b()
        for l in rp.lanes("A") + rp.lanes("B"):
            p = (self.out / f"{l['name']}.prompt").read_text(encoding="utf-8")
            self.assertIn(SUBJECT, p); self.assertTrue(p.rstrip().endswith("LANE-COMPLETE"))
            self.assertNotIn("$SUBJECT", p)
        rid = (self.out / "rubric_id").read_text().strip()
        rp.prompts_b()
        self.assertEqual(rid, (self.out / "rubric_id").read_text().strip(), "rubric_id must be deterministic")

    def test_arbiter_reads_designers_and_lint(self):
        for n in ("design-scope", "design-verify", "lint-claude", "lint-codex"):
            self.lane(n, f"output of {n}\nLANE-COMPLETE\n")
        rp.prompts_b()
        arb = (self.out / "arbiter.prompt").read_text(encoding="utf-8")
        for n in ("design-scope", "design-verify", "lint-claude", "lint-codex"):
            self.assertIn(f"output of {n}", arb, "the arbiter must read lint as well as designers")
        self.assertIn("## Losers", arb)

    def test_unbound_prompt_fails_closed(self):
        with self.assertRaises(SystemExit) as e:
            rp.write_prompt("x", "Read: C:\\code\\doctrine$SUBJECT")
        self.assertIn("BINDING FAIL", str(e.exception))

    def test_later_stages_refuse_without_their_inputs(self):
        with self.assertRaises(SystemExit):
            rp.prompts_c()
        with self.assertRaises(SystemExit):
            rp.prompts_d()

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_dry_run_dispatches_nothing(self):
        env, log = self._fakes()
        p = subprocess.run([BASH, (TOOL / "run.sh").as_posix(), "--dry-run"], env=env, capture_output=True, text=True, timeout=120)
        self._assert_nothing_dispatched(log, p)
        self.assertIn("dry-run: stage A prompts OK", p.stdout, p.stdout + p.stderr)
        self.assertIn("posture: conjugal-standard-PARTIAL (0/17", p.stdout)
        self.assertEqual(p.returncode, 1)
        self.assertFalse(list(self.out.glob("*.rc")), "a dry run must not dispatch any lane")

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_survives_a_checkout_path_with_space_and_bang(self):
        # airmypc 2026-09-14: the string-form PY split on `C:\!Layi Wkspc`, `eval ""` passed, 17/17 DID-NOT-RUN.
        tool = self.tmp / "sp ace!dir" / "tools" / "review-posture"
        shutil.copytree(TOOL, tool)
        env, log = self._fakes()
        p = subprocess.run([BASH, (tool / "run.sh").as_posix(), "--dry-run"], env=env, capture_output=True, text=True, timeout=120)
        self.assertIn("dry-run: stage A prompts OK", p.stdout, p.stdout + p.stderr)
        self.assertNotIn("prompt generation failed", p.stdout)
        self._assert_nothing_dispatched(log, p)

    def _fakes(self, codex_body="echo 'fake codex'", claude_body="echo 'fake claude'"):
        # Executable shims that log every call. `timeout` passes probes (--version/--help) through to the real
        # coreutils timeout and refuses anything else, so a runner missing its guards still dispatches nothing real.
        fake = self.tmp / "fakebin"; fake.mkdir(exist_ok=True)
        log = self.tmp / "calls.log"
        shims = {
            "claude": f'#!/bin/sh\necho "claude $*" >> "{log.as_posix()}"\n{claude_body}\n',
            "codex": f'#!/bin/sh\necho "codex $*" >> "{log.as_posix()}"\n{codex_body}\n',
            # Probes run the fake CLI directly (no platform timeout needed); anything else is recorded, never run.
            "timeout": ('#!/bin/sh\ncase " $* " in *" --version "*|*" --help "*)\n'
                        '  while [ $# -gt 0 ]; do case "$1" in -k) shift 2;; -*) shift;; *) break;; esac; done\n'
                        '  shift; exec "$@";;\nesac\n'
                        f'echo "DISPATCH $*" >> "{log.as_posix()}"\nexit 99\n'),
        }
        for name, body in shims.items():
            p = fake / name
            p.write_text(body, encoding="utf-8", newline="\n")
            p.chmod(0o755)
        env = dict(os.environ, RP_REPO=str(ROOT), PATH=str(fake) + os.pathsep + os.environ.get("PATH", ""))
        return env, log

    def _run(self, env, *args):
        return subprocess.run([BASH, (TOOL / "run.sh").as_posix(), *args], env=env, capture_output=True, text=True, timeout=180)

    def _assert_nothing_dispatched(self, log, p):
        calls = log.read_text(encoding="utf-8") if log.exists() else ""
        self.assertNotIn("DISPATCH", calls, p.stdout + p.stderr)
        self.assertNotIn("exec -m", calls)
        self.assertNotIn(" -p ", calls)
        self.assertFalse(list(self.out.glob("*.rc")), "no lane may start")

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_refuses_to_dispatch_when_a_launcher_is_broken(self):
        # airmypc 2026-09-14: a stray npm `node` shim made `codex` exit 127; every Codex lane died as if the family were absent.
        env, log = self._fakes(codex_body="echo 'node: line 1: This: command not found'; exit 127")
        p = self._run(env)
        self.assertIn("LAUNCHER-BROKEN family=codex [codex --version] rc=127", p.stdout, p.stdout + p.stderr)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self._assert_nothing_dispatched(log, p)
        self.assertIn("codex --version", log.read_text(encoding="utf-8"), "the fake, not a real CLI, must have answered")

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_probes_the_exec_entrypoint_not_only_version(self):
        # Codex sol review 2026-09-14: `--version` can pass while `codex exec` is broken.
        env, log = self._fakes(codex_body='case "$1" in exec) exit 127;; esac; echo ok')
        p = self._run(env)
        self.assertIn("LAUNCHER-BROKEN family=codex [codex exec --help] rc=127", p.stdout, p.stdout + p.stderr)
        self.assertEqual(p.returncode, 2)
        self._assert_nothing_dispatched(log, p)

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_never_evaluates_inventory_values_as_shell(self):
        # Codex sol review 2026-09-14: `luna: gpt-5.6-luna; false` made `ids` succeed and the eval fail open.
        (self.tmp / "inv.yaml").write_text(INVENTORY.replace("gpt-5.6-luna", "gpt-5.6-luna;touch PWNED"), encoding="utf-8")
        env, log = self._fakes()
        p = self._run(env)
        self.assertIn("MODEL ID LINE REJECTED", p.stdout, p.stdout + p.stderr)
        self.assertEqual(p.returncode, 2)
        self.assertFalse((ROOT / "PWNED").exists() or (self.tmp / "PWNED").exists())
        self._assert_nothing_dispatched(log, p)

    @unittest.skipUnless(BASH, "no non-WSL bash available")
    def test_run_sh_resolves_every_nickname_before_any_lane_starts(self):
        # Codex sol review 2026-09-14: a roles.json nickname the inventory never defines used to exit only after
        # earlier paid lanes in the same stage had started.
        tool = self.tmp / "tool" / "tools" / "review-posture"
        shutil.copytree(TOOL, tool)
        roles = tool / "roles.json"
        text = roles.read_text(encoding="utf-8")
        self.assertIn('"luna"', text)
        roles.write_text(text.replace('"luna"', '"terra"', 1), encoding="utf-8")
        env, log = self._fakes()
        p = subprocess.run([BASH, (tool / "run.sh").as_posix()], env=env, capture_output=True, text=True, timeout=180)
        self.assertIn("UNRESOLVED nickname terra", p.stdout, p.stdout + p.stderr)
        self.assertEqual(p.returncode, 2)
        self._assert_nothing_dispatched(log, p)


if __name__ == "__main__":
    unittest.main()
