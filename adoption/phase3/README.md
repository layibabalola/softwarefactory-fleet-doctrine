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

`--verify-remotes` additionally verifies each exact published ref with `git ls-remote`; hosted CI
does not require network access. None of these checks invokes a provider or changes runtime state.
