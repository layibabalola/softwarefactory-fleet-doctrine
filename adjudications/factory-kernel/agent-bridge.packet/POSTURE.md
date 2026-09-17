# Posture line, computed (R9.2), not typed

Tool: <bus>/tools/review-posture/review_posture.py, subcommand posture, bus HEAD dc20a28b77d070096f9f192ba3adbbd50c8b6560.
review_posture.py sha256 6418F59DD64D4D133133587C53BEC9959494053119106A97689769787044D523; roles.json sha256 D9AD9776F31C71DFE5F3DD86C29CE157BAB678D3701FE112075131E3B3F2E603.
Command (read-only; dispatches nothing; RP_OUT = an empty directory created for this run):

```
python review_posture.py posture <evidence>/KR4-FILE-2-20260917/posture-out
```

stdout (verbatim); the tool exits 1 when the posture is PARTIAL, as its README states:

```
posture: conjugal-standard-PARTIAL (0/17 lanes; missing: Designer-Scope 0/1; Designer-Verify 0/1; Lint-Consistency 0/2; Arbiter 0/1; Consolidator 0/1; Panel 0/8; Classifier 0/3)
cross_family: NO-CROSS-FAMILY-VALIDATION
roles: Designer-Scope 0/1, Designer-Verify 0/1, Lint-Consistency 0/2, Arbiter 0/1, Consolidator 0/1, Panel 0/8, Classifier 0/3
```

Why 0/17: the review that shaped this filing was the project's class-C round (Codex SOL and Astra lanes through
Invoke-CodexLane.ps1, three Claude adversary subagents writing verdict files). None of those ran under the tool's
roles.json or wrote its LANE-COMPLETE sentinel, so the tool counts none of them (R9.2 forbids counting a narrower check).
run.sh was not invoked: it dispatches 17 lanes and spends; this card writes candidates and spends nothing.
