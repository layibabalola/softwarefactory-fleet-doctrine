# Posture line re-run for round 2 (R9.2): computed, not typed

Tool: <bus>/tools/review-posture/review_posture.py, subcommand posture. Run by the round-2 author on 2026-09-17 (CARD:KR4-FILE-2)
at bus HEAD 9ae40302d805a9cb9fac0f04008a45931918202b (two commits after dc20a28: a heartbeat row and a cos-feedback row; the seven
bus files this filing reads are byte-identical to their round-1 hashes, see PROVENANCE.md).
review_posture.py sha256 6418F59DD64D4D133133587C53BEC9959494053119106A97689769787044D523; roles.json sha256 D9AD9776F31C71DFE5F3DD86C29CE157BAB678D3701FE112075131E3B3F2E603.
Command (read-only; RP_OUT = a fresh empty temporary directory; nothing dispatched, nothing spent):

```
python review_posture.py posture <empty RP_OUT>
```

stdout (verbatim); exit code 1 (PARTIAL), as the tool README states:

```
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3)
cross_family: NO-CROSS-FAMILY-VALIDATION
roles: Designer-Scope 0/1, Designer-Verify 0/1, Lint-Consistency 0/2, Arbiter 0/1, Consolidator 0/1, Panel 0/8, Classifier 0/3
```

Byte-identical to the stdout recorded in POSTURE.md (bus dc20a28).