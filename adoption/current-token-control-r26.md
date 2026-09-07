# Current R26 census candidate

Status: proposed current-intake implementation; not active Doctrine, not a ratified descendant-control amendment, and not runtime activation.

`current-token-control-r26.json` is separate from the frozen `universal-token-control-r26.json`. Its current evidence references are recomputed from each project's actual latest spec commit and blob at its census base. It retains the same nine projects, with no new ADOPT or other proof credit. The Conjugal candidate now explicitly distinguishes the current R26 subject; the proposed census is 0 ADOPT / 6 DISTINGUISH / 3 STALE. This is a candidate disposition, pending the current-intake control and publication review.

The current verifier explicitly classifies the four later portable doctrine documents. That fixed classification cannot be expanded by ledger input to hide a project. Historical verification keeps its original project/non-project population and mandatory candidate rules. The current profile accepts an exact canonical negative declaration without repeating the candidate SHA in project prose, while the global verifier still checks the exact merge/candidate/tree/parents. Old project-candidate metadata is optional in the current profile and grants no credit when absent; supplied metadata remains fully checked. Every ADOPT retains the existing subject bindings, profile/review artifacts and non-regression proof gates. Cloudvore carries no old candidate credit because its current project-owned spec removed that table.

After committing a current census, verify it with:

```console
python tools/check_adoption_ledger.py --current --treeish HEAD
python -m unittest discover -s tests -p "test_current_adoption_ledger.py" -v
```

Historical evidence remains independently verifiable on its original publication:

```console
python tools/check_adoption_ledger.py --treeish 53a48a6a0be5eade253ce1a508872d6874fd474a
python -m unittest discover -s tests -p "test_adoption_ledger.py" -v
```

A spec change must produce a new exact current census before receiving current evidence credit. A new project or portable-spec classification requires review; neither is silently omitted. The old census and original hashes are retained as history. Current census validity is not project or fleet adoption.

The proposed successor control and workflow integration is specified in `ruling-candidates/current-intake-epoch-r1.md`. Its manifest seals the new control bytes separately from the original workflow seal. The original Phase 17 publication remains failed; a separately published proof with the required parent and the same six original blobs is checked without retroactive historical credit. This candidate requires exact-subject independent review and the real publication gates. It changes CI control behavior explicitly and does not activate a runtime or adopt Doctrine in a project.
