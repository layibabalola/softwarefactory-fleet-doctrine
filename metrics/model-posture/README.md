# metrics/model-posture: entry (CANDIDATE)

This file is commands only. The spec explains the design: [`specs/fleet-model-posture/spec.md`](../../specs/fleet-model-posture/spec.md).
The shards are the state: `metrics/<project>/posture-*.jsonl`. They are diagnostic only (metrics law 1).

```bash
# which projects publish, and which periods they have
git ls-files 'metrics/*/posture-*.jsonl'

# declared vs actual vs owner posture (printed, never stored; exit 0 whatever it finds)
python tools/factory/model-posture.py view metrics/<project>/posture-*.jsonl --policy policy/model-posture.json [--declared <file>]

# a project's weekly shard from its LOCAL provider-usage-event-v1 rows (raw rows never leave the project)
python tools/factory/model-posture.py reduce --input <local.jsonl> --project <project> --week <YYYY-Www>

# write it into a bus checkout (one writer per metrics/<project>/), then commit that exact path
python tools/factory/model-posture.py publish --bus <bus checkout> --shard <file> --project <project> --week <YYYY-Www>

# roll aged shards up: the plan first, then one commit per roll-up (adds the rollup, deletes its sources)
python tools/factory/model-posture.py prune --bus <bus checkout> --project <project>
python tools/factory/model-posture.py prune --bus <bus checkout> --project <project> --commit

# the tests
python tools/factory/model-posture.tests.py
```
