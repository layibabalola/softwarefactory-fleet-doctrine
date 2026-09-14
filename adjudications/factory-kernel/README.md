# Dogfood filings on the fleet factory kernel

Subject: `specs/fleet-factory-kernel.md` (with its profiles under `specs/fleet-factory-kernel/profiles/`). Opened 2026-09-14.
Steward: named in the subject's header (interim: Conjugal).

**This directory is for operational evidence, not design review.** Each filing records what happened when the
project ran real work through the kernel. The paste that produces a filing is `bootstrap/PROMPT-K-dogfood-kernel.md`.

- One file per project: `adjudications/factory-kernel/<project>.md`. Single writer. Rewrite it wholesale each window;
  the harvest tool marks it `STALE` and the steward re-reads it.
- Header and line format: kernel §4. Each line gives a clause and a verdict (`FIT`, `FRICTION`, `BREAK` or `N/A`), a quote, evidence from
  your own repo, and a `REPLACES` and `PROOF` for `FRICTION` or `BREAK`.
- Land it the R7 way: commit on `review/<project>-kernel-<YYYY-MM-DD>` and push at once. Verification is
  `git ls-remote origin refs/heads/<branch>` returning your local tip. Never push to master.
- Answers arrive as `<project>.dispositions.md` beside your filing (`bootstrap/PROMPT-3-harvest.md` §5).
- Status of every filing: `python tools/harvest-status.py factory-kernel`.
