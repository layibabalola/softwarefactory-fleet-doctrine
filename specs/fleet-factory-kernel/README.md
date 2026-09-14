# Factory kernel profiles - index

One file per domain under `profiles/`. Every profile answers the same ten fields, so any two can be compared line by line. Each profile carries its own revision. `BENCHED` means at least one fleet project does work of that kind today. `DRAFT - NO BENCH` means text written from first principles, waiting for its first filing.

| Profile | Status |
|---|---|
| [`code`](profiles/code.md) | BENCHED |
| [`hardware-in-loop`](profiles/hardware-in-loop.md) | BENCHED |
| [`measured-objective`](profiles/measured-objective.md) | BENCHED |
| [`mobile-app`](profiles/mobile-app.md) | DRAFT - NO BENCH |
| [`game-engine`](profiles/game-engine.md) | DRAFT - NO BENCH |
| [`realtime-web-3d`](profiles/realtime-web-3d.md) | DRAFT - NO BENCH |
| [`3d-render`](profiles/3d-render.md) | DRAFT - NO BENCH |
| [`creative-writing`](profiles/creative-writing.md) | DRAFT - NO BENCH |
| [`business-strategy`](profiles/business-strategy.md) | DRAFT - NO BENCH |

To add a domain: copy any profile, fill the ten fields, and file a first dogfood report (`bootstrap/PROMPT-K-dogfood-kernel.md`). The steward merges it at the next harvest.
