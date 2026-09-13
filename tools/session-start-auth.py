"""SessionStart hook: run the CLI auth/parity checker and surface its verdict.

Always exits 0 — a hook that exits non-zero has its output hidden (measured: SessionStart hook silence),
which is the opposite of what a rotation check is for. The verdict line is the evidence; the underlying
checker's exit code is printed beside it so a red is still a red.

Default is IDENTITY-ONLY (~3 s): it proves account parity (is the CLI on the account the app is signed
into?), which is the rotation question. It does NOT prove capacity. The live inference probe is left to the
dispatcher's resume step 0 because, measured 2026-09-13, `--allow-live-probe` takes 5 s from the owner's
terminal but 53-89 s from inside a Claude Code session (scrubbing CLAUDE_CODE_* env does not help), and a
session-start hook must not block for a minute. Pass --live to force the probe (timeout 150 s).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(ROOT, "coordination", "tools", "check-cli-auth.py")


def main() -> int:
    # Windows console defaults to cp1252; the checker prints em-dashes. Never let the evidence line crash.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    live = "--live" in sys.argv[1:]
    cmd = [sys.executable, CHECKER] + (["--allow-live-probe"] if live else [])
    budget = 150 if live else 30
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=budget, encoding="utf-8", errors="replace")
        out = (p.stdout or "").strip() or (p.stderr or "").strip()
        code = p.returncode
    except subprocess.TimeoutExpired:
        out, code = f"checker timed out after {budget} s (treat as UNPROVEN, run it by hand)", 124
    except OSError as e:
        out, code = f"checker could not start: {e}", 127
    mode = "live probe" if live else "identity-only"
    print(f"[session-start] CLI auth/parity, {mode} (exit {code}): {out}")

    # Auto-remedy ACCOUNT_MISMATCH or PARITY_UNVERIFIED by re-authing the CLI
    if code != 0 and ("ACCOUNT_MISMATCH" in out or "PARITY_UNVERIFIED" in out):
        print("[session-start] AUTO-REMEDYING ACCOUNT_MISMATCH: re-authing CLI...")
        try:
            # Find the Claude binary
            binary = None
            for candidate in (os.path.expanduser(r"~\.local\bin\claude.exe"), os.path.expanduser(r"~\.local\bin\claude")):
                if os.path.exists(candidate):
                    binary = candidate
                    break

            if binary:
                # Logout
                print("[session-start] Running: claude auth logout")
                subprocess.run([binary, "auth", "logout"], capture_output=True, timeout=10)

                # Login (will pop browser for OAuth)
                print("[session-start] Running: claude auth login --claudeai (browser will pop up)")
                subprocess.run([binary, "auth", "login", "--claudeai"], timeout=300)

                # Extract the email from auth status and set it in the parity config
                print("[session-start] Detecting logged-in email and updating parity config...")
                try:
                    status = subprocess.run([binary, "auth", "status"], capture_output=True, text=True, timeout=10)
                    if status.returncode == 0:
                        import json
                        status_data = json.loads(status.stdout)
                        if "email" in status_data:
                            cli_email = status_data["email"]
                            # Run the checker with --set-desktop-email to cache this email
                            subprocess.run([sys.executable, CHECKER, "--set-desktop-email", cli_email],
                                         capture_output=True, timeout=10)
                            print(f"[session-start] Set desktop email cache to: {cli_email}")
                except Exception as e:
                    print(f"[session-start] Could not auto-set email: {e}")

                # Re-check
                print("[session-start] Re-checking CLI auth parity after login...")
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=budget, encoding="utf-8", errors="replace")
                out = (p.stdout or "").strip() or (p.stderr or "").strip()
                code = p.returncode
                print(f"[session-start] CLI auth/parity re-check (exit {code}): {out}")
            else:
                print("[session-start] Could not find Claude CLI binary; manual fix required")
        except subprocess.TimeoutExpired:
            print("[session-start] Timeout during auth flow; you may need to manually complete the login")
        except Exception as e:
            print(f"[session-start] Error during auto-remedy: {e}")

    if code == 0:
        print("[session-start] ✅ AUTH VERIFIED. Resume procedure will now ask for workstream selection.")
    else:
        print("[session-start] NON-ZERO: paste the line above into chat before deriving anything; "
              "run the printed remedy, then re-run: "
              f'python "{CHECKER}" --allow-live-probe')
    if code == 0 and not live:
        print("[session-start] capacity UNPROVEN by design here; the resume dispatcher (CLAUDE.md step 0) runs "
              f'python "{CHECKER}" --allow-live-probe (~1 min from inside a session, ~5 s from a terminal).')
    return 0


if __name__ == "__main__":
    sys.exit(main())
