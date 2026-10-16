#!/usr/bin/env node
// Offline fixtures for tools/tool-census.mjs. Builds a fake fleet (projects, user hooks dir, settings)
// in a temp dir and drives the real CLI through --config/--root/--home/--baseline.
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = mkdtempSync(join(tmpdir(), 'tool-census-'));
const tool = fileURLToPath(new URL('./tool-census.mjs', import.meta.url));
const put = (rel, body) => { const p = join(root, rel); mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, body); return p; };
const hooks = (event, cmd) => JSON.stringify({ hooks: { [event]: [{ hooks: [{ type: 'command', command: cmd }] }] } });
const census = (extra = [], allow = true) => {
  const r = spawnSync(process.execPath, [tool, '--config', join(root, 'census.json'), '--root', root, '--home', join(root, 'home'), '--baseline', join(root, 'baseline.json'), ...extra], { encoding: 'utf8' });
  if (r.status !== 0 && !allow) throw new Error(`census exited ${r.status}: ${r.stderr}`);
  return { status: r.status, out: `${r.stdout || ''}${r.stderr || ''}`, stdout: r.stdout };
};
const json = () => JSON.parse(census(['--json']).stdout);
const fam = (rep, name) => rep.families.find((f) => f.name === name);

try {
  put('census.json', JSON.stringify({
    families: [
      { name: 'checkpoint', names: ['session-checkpoint.py', 'session_checkpoint.py'] },
      { name: 'docsize', names: ['check-doc-size.py'], sharedSectionMarker: 'END CONFIG' },
    ],
    roots: [
      { name: 'p1', path: 'p1', kind: 'project' },
      { name: 'p2', path: 'p2', kind: 'project' },
      { name: 'p3', path: 'p3', kind: 'project' },
      { name: 'gone', path: 'does-not-exist', kind: 'project' },
      { name: 'user-hooks', path: '~/.claude/hooks', kind: 'user' },
    ],
    userSettings: '~/.claude/settings.json',
  }));
  let cases = 0;

  // 1. Distinct versions: p1 and p2 identical (one with CRLF), p3 different, user copy different = 3 distinct.
  put('p1/tools/session-checkpoint.py', 'print(1)\nprint(2)\n');
  put('p2/tools/session-checkpoint.py', 'print(1)\r\nprint(2)\r\n');
  put('p3/session_checkpoint.py', 'print(3)\n');
  put('home/.claude/hooks/session-checkpoint.py', 'print(4)\n');
  put('home/.claude/hooks/session-checkpoint.py.bak-20261004', 'print(5)\n');           // not a copy: name differs
  put('home/.claude/hooks/archive/session-checkpoint.py', 'print(6)\n');                // excluded dir
  let rep = json();
  assert.equal(fam(rep, 'checkpoint').copies.length, 4, 'four copies, .bak and archive ignored');
  assert.equal(fam(rep, 'checkpoint').distinct, 3, 'CRLF is not a version; three distinct');
  assert.deepEqual(rep.absentRoots, ['gone'], 'absent root named, not counted'); cases++;

  // 2. Marker-section hashing: CONFIG differs, shared section equal = one version; a copy without the
  //    marker hashes whole and is flagged.
  put('p1/tools/check-doc-size.py', 'LIMIT = 100\n# END CONFIG\nshared()\n');
  put('p2/tools/check-doc-size.py', 'LIMIT = 900\nOTHER = 1\n# END CONFIG\nshared()\n');
  rep = json();
  assert.equal(fam(rep, 'docsize').distinct, 1, 'only the section below the marker is hashed'); cases++;
  put('p2/tools/check-doc-size.py', 'LIMIT = 900\n# END CONFIG\nshared_but_edited()\n');
  assert.equal(fam(json(), 'docsize').distinct, 2, 'an edit below the marker is a new version'); cases++;
  put('p3/tools/check-doc-size.py', 'LIMIT = 5\nshared()\n');
  rep = json();
  assert.equal(fam(rep, 'docsize').copies.find((c) => c.root === 'p3').markerFound, false, 'missing marker flagged');
  assert.equal(fam(rep, 'docsize').distinct, 3); cases++;

  // 3. Double registration: same family, same event, in a project AND the user settings.
  put('home/.claude/settings.json', hooks('Stop', 'python "C:/x/.claude/hooks/session-checkpoint.py"'));
  put('p1/.claude/settings.json', hooks('Stop', 'python "$CLAUDE_PROJECT_DIR/tools/session-checkpoint.py"'));
  put('p2/.claude/settings.json', hooks('SessionStart', 'python "$CLAUDE_PROJECT_DIR/tools/session-checkpoint.py"'));   // other event: not double
  put('p3/.claude/settings.json', JSON.stringify({ hooks: { Stop: [{ type: 'command', command: 'python tools/session_checkpoint.py' }] } }));  // flat entry
  rep = json();
  assert.deepEqual(rep.doubleRegistrations.map((d) => d.project).sort(), ['p1', 'p3'], 'p1 and flat p3 double; p2 different event');
  assert.equal(rep.doubleRegistrations.find((d) => d.project === 'p3').projectFlat, true, 'flat entry flagged');
  // total = checkpoint (3-1) + docsize (3-1) + 2 doubles = 6
  assert.equal(rep.total, 6); cases++;

  // 4. --check with no baseline is a tool failure; --update-baseline seeds it.
  assert.equal(census(['--check']).status, 2, 'no baseline = exit 2'); cases++;
  assert.equal(census(['--update-baseline']).status, 0);
  assert.equal(JSON.parse(readFileSync(join(root, 'baseline.json'), 'utf8')).total, 6, 'baseline seeded'); cases++;

  // 5. --check: equal passes, a rise fails, a fall passes.
  assert.equal(census(['--check']).status, 0, 'equal = exit 0'); cases++;
  put('p2/tools/session-checkpoint.py', 'print("drifted")\n');
  let r = census(['--check']);
  assert.equal(r.status, 1, 'a rise = exit 1'); assert.match(r.out, /ROSE: count 7 > baseline 6/); cases++;

  // 6. --update-baseline refuses to raise and leaves the file untouched.
  const before = readFileSync(join(root, 'baseline.json'), 'utf8');
  r = census(['--update-baseline']);
  assert.equal(r.status, 1, 'raise refused'); assert.match(r.out, /REFUSED/);
  assert.equal(readFileSync(join(root, 'baseline.json'), 'utf8'), before, 'baseline unchanged'); cases++;

  // 7. Retire copies: the count falls, --check passes, --update-baseline lowers.
  rmSync(join(root, 'p2/tools/session-checkpoint.py')); rmSync(join(root, 'p3/session_checkpoint.py'));
  rmSync(join(root, 'p1/.claude/settings.json'));
  assert.equal(census(['--check']).status, 0, 'a fall = exit 0'); cases++;
  r = census(['--update-baseline']);
  assert.equal(r.status, 0); assert.match(r.out, /lowered 6 -> /);
  assert.ok(JSON.parse(readFileSync(join(root, 'baseline.json'), 'utf8')).total < 6, 'baseline lowered'); cases++;

  // 8. A git root lists tracked + untracked-not-ignored files; ignored copies are not counted.
  execFileSync('git', ['init', '-q', join(root, 'p1')]);
  put('p1/.gitignore', 'ignored/\n');
  put('p1/ignored/session-checkpoint.py', 'print("ignored")\n');
  assert.equal(fam(json(), 'checkpoint').copies.filter((c) => c.root === 'p1').length, 1, 'gitignored copy skipped'); cases++;

  // 9. Deadline schedule (owner D1-D3 adjudication 2026-10-16). Hand-written baselines pin the count.
  const now = json().total;
  assert.ok(now >= 2, `fixture count ${now} must be >= 2 for the schedule cases`);
  const sched = (body) => { put('sched.json', JSON.stringify(body)); return join(root, 'sched.json'); };
  const check = (baselinePath, today) => census(['--check', '--baseline', baselinePath, '--today', today]);
  const schedule = [{ by: '2026-10-23', max: now - 1 }, { by: '2026-11-06', max: 0 }];
  let b = sched({ total: now, schedule });
  r = check(b, '2026-10-22');
  assert.equal(r.status, 0, 'before the first date: old rule only'); assert.match(r.out, new RegExp(`next deadline: max ${now - 1} by 2026-10-23`)); cases++;
  r = check(b, '2026-10-23');
  assert.equal(r.status, 1, 'on the date and over the max = exit 1'); assert.match(r.out, /OVERDUE: count \d+ > max \d+ due by 2026-10-23/);
  assert.match(r.out, /Still over: .*checkpoint/, 'names the families over'); cases++;
  r = check(sched({ total: now, schedule: [{ by: '2026-10-23', max: now }, { by: '2026-11-06', max: 0 }] }), '2026-10-30');
  assert.equal(r.status, 0, 'at the max passes'); cases++;
  r = check(sched({ total: now, schedule: [{ by: '2026-10-23', max: now + 5 }] }), '2026-12-01');
  assert.equal(r.status, 0, 'below the max passes'); cases++;
  r = check(sched({ total: now, schedule }), '2026-11-06');
  assert.equal(r.status, 1, 'the latest date reached governs'); assert.match(r.out, /max 0 due by 2026-11-06/); cases++;
  r = check(sched({ total: now, schedule: [{ by: '2026-11-06', max: 0 }, { by: '2026-10-23', max: now }] }), '2026-10-30');
  assert.equal(r.status, 0, 'schedule order in the file does not matter'); cases++;
  r = check(sched({ total: now }), '2099-01-01');
  assert.equal(r.status, 0, 'no schedule = old behaviour'); assert.doesNotMatch(r.out, /deadline|OVERDUE/); cases++;
  r = check(sched({ total: now - 1 }), '2099-01-01');
  assert.equal(r.status, 1, 'no schedule: the rise rule still fails'); assert.match(r.out, /ROSE/); cases++;
  r = check(sched({ total: now, schedule: [{ by: '23/10/2026', max: 1 }] }), '2026-10-30');
  assert.equal(r.status, 2, 'malformed schedule = tool failure, never a silent pass'); cases++;

  // 10. --update-baseline keeps the schedule and records the roots it measured.
  b = sched({ total: now + 3, schedule });
  r = census(['--update-baseline', '--baseline', b]);
  assert.equal(r.status, 0); const kept = JSON.parse(readFileSync(b, 'utf8'));
  assert.deepEqual(kept.schedule, schedule, 'schedule survives a lowering');
  assert.ok(kept.roots.includes('p1') && !kept.roots.includes('gone'), 'measured roots recorded'); cases++;

  // 11. UNMEASURED: a root the baseline measured is not visible, or no fleet root at all (CI).
  r = check(sched({ total: now, schedule, roots: ['p1', 'p9'] }), '2026-12-01');
  assert.equal(r.status, 3, 'missing measured root = exit 3, not a pass or a fail'); assert.match(r.out, /UNMEASURED: .*p9/); cases++;
  r = census(['--update-baseline', '--baseline', sched({ total: now + 3, roots: ['p9'] })]);
  assert.equal(r.status, 3, 'a partial count never lowers the baseline'); cases++;
  put('ci.json', JSON.stringify({ families: [{ name: 'checkpoint', names: ['session-checkpoint.py'] }],
    roots: [{ name: 'p1', path: 'nowhere-1', kind: 'project' }, { name: 'u', path: '~/nowhere', kind: 'user' }] }));
  r = census(['--check', '--config', join(root, 'ci.json'), '--baseline', sched({ total: 11, schedule }), '--today', '2026-12-01']);
  assert.equal(r.status, 3, 'legacy baseline + no fleet root visible = UNMEASURED'); assert.match(r.out, /sibling clones are absent/); cases++;

  assert.ok(existsSync(tool));
  console.log(`tool-census fixtures: ${cases} cases passed`);
} finally { rmSync(root, { recursive: true, force: true }); }
