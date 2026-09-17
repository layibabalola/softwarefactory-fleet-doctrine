# Receipt extract: ASTRA-20260917-102129-346 (provider capacity refusal, round 2 of the parked KR4-FILE)

Inspected by the KR4-FILE-2 author. Files under coordination/lane-receipts/ (gitignored); sha256 of each original:

| file | sha256 |
|---|---|
| ASTRA-20260917-102129-346.events.jsonl | C765996FA54A34D56EBD338F48F51C0CEF1310199753B98D4BA59AE44BD3CC5B |
| ASTRA-20260917-102129-346.last.txt | 2D712D3CB5AED46A2660D25854FE34734F89A15CBCD00F54A067AF74A4D75821 |
| ASTRA-20260917-102129-346.receipt.json | B1A352438931635CA06354F655EF9B15C8D0E593EFD3A944DFC00C6C7C562732 |

## events.jsonl (verbatim)

```
{"type":"thread.started","thread_id":"01a0aff5-6b4e-7df0-98f4-e9b0a67ee003"}
{"type":"turn.started"}
{"type":"error","message":"Selected model is at capacity. Please try a different model."}
{"type":"turn.failed","error":{"message":"Selected model is at capacity. Please try a different model."}}
```

## receipt.json (selected fields, verbatim values)

lane=ASTRA requestedModel=gpt-6-astra requestedEffort=high invokedAt=09/17/2026 15:21:29 completedAt=09/17/2026 15:21:37 elapsedSeconds=8 processExit=1 processOutcome=EXIT_NONZERO timedOut=False costUsd=null costSource=UNKNOWN tokensObserved=null independenceAttested=False
receiptAsserts: prompt bytes sent, tuple requested, process exit. Nothing else.
promptFile=<agent-bridge>\.claude-state\coordination\lane-prompts\ASTRA-KR4-FILE-round2-A5908251.txt promptSha256=7B56AF6AFF22156A5AAFF8C9649FBADA16532FFD4A518AF5A06BE2CF211A4587 promptBytes=1923

## last.txt (first two lines, verbatim)

```
NO VERDICT. This run produced no final message: process exited 1 without emitting a final message.
processOutcome=EXIT_NONZERO elapsedSeconds=8
```

stderr.txt: 2 bytes.
