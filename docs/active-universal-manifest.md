# Refreshing the active universal-provider manifest

R45 is the current snapshot. R26–R44 are frozen layers, and the original R45
proof remains at `0da4a20f9e62a47414f42a8780c695865f1633a0`. A later change to a
bound document must not silently inherit the old snapshot's hashes.

From a clean checkout, run the following with the exact current commit:

```text
python tools/refresh_current_universal_manifest.py --candidate <40-character-commit>
```

The command writes no files. Its JSON output contains the candidate commit and
tree, original proof commit, changed binding paths, proposed manifest, and its
digest. `--repo` may name another clean checkout. Symbolic refs, dirty/index
ambiguity, object indirection, frozen-layer changes, malformed JSON and changes
to paths, ordering, authority, status, policy or base are refused.

The hub inspects the source changes and output, then separately writes only the
proposed `manifest` object as canonical two-space JSON with a final newline to
the reported manifest path. Include that metadata change in the reviewed work
block. The tool grants no review vote, publication, provider execution or runtime
authority. It must not run automatically to bless an arbitrary failed candidate.

Run the existing provider workflow gates, including both current-descriptor
pipeline tests and the new refresh controls. Keep the original failure, bind
review to the final combined commit and manifest, and require fresh exact-head
and post-merge CI. When other commits add the same bound documentation, refresh
the combined candidate before requesting its review; approval never transfers
to a changed subject. A new active layer requires a separately reviewed tool
update rather than changing frozen snapshots.

Windows runs the same 252 universal-provider tests through
`tools/run_windows_universal_tests.py` in four subprocesses inside the existing
CI matrix job. Two slow historical controls each have their own process; the
remaining tests are divided in sorted order between the other two. Linux keeps
the existing discovery command and its established platform skip rules.

The Windows runner requires a clean committed checkout and a new output directory
outside it. Its plan binds the commit, tree, census and unique run identifier;
the reviewed census digest also rejects a same-count test substitution. The parent
parses declarations without importing project code, and each contained worker
verifies actual unittest discovery. Atomic receipts account for every selected test exactly once, with no skips,
failures or errors. It refuses missing, duplicate, partial or mismatched receipts.
Each worker waits for attachment to a Windows Job Object before importing project
tests. A deadline of at most 720 seconds also subtracts elapsed job time and a
90-second cleanup/downstream reserve from the unchanged 15-minute CI job;
failure or interruption terminates and reaps workers and their descendants.
Logs retain the plan, receipts and per-test durations for subsequent balancing.
