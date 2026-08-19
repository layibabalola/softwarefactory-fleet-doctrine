# R26 published project dispositions — phase 3

`r26-published-project-disposition-intake.json` folds three independently accepted and published
project-owned candidates into their central single-writer specs and the closed-set R26 ledger.
Every row remains `DISTINGUISH` with zero authority. It is not project or fleet adoption and grants
no installation, runtime, provider, scheduler, canary, merge, push, publication, or release power.

The production ledger checker freezes a canonical SHA-256 over every complete project-candidate
object. The phase-3 checker independently binds the published doctrine base, the two forward-only
spec commits, the exact three-project set, each central spec blob, and byte-for-byte equality between
the intake and ledger candidate objects. Artifact sizes and SHA-256 values describe published
project Git objects; they do not transfer sibling proof or earn adoption/non-regression credit.

Run the fail-closed controls with:

```console
python tools/check_adoption_ledger.py --treeish HEAD
python tools/check_phase3_disposition_batch.py --treeish HEAD
python -m unittest discover -s tests -p "test_phase3_disposition_batch.py" -v
```

Without `--verify-remotes`, the checker emits `PASS LOCAL-ONLY` and `REMOTES NOT VERIFIED` so local
structure success cannot be mistaken for publication verification. `--verify-remotes` accepts only
the three exact allowlisted GitHub URL/ref pairs, uses a bounded temporary repository with prompts
disabled and command timeouts, fetches each ref, and rederives the commit tree, sole parent, base
ancestry, and every artifact Git blob, byte count, and SHA-256. The publishing CI runs this remote
mode. Git system and user configuration are disabled; the temporary Windows config names only the
installed `schannel` TLS backend and noninteractive credential manager. Terminal and askpass
prompts remain disabled. Temporary Git objects are removed on every exit. None of these checks
invokes a provider or changes runtime state.
