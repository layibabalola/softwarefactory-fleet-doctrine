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

  // 2b. The marker is a delimiter line, not the first prose mention (AirMyPC/MLV copies, 2026-10-16):
  //     a docstring or comment naming END CONFIG above the real '# ==== END CONFIG ====' line is ignored.
  const docsizeBefore = fam(json(), 'docsize').distinct;
  put('p1/tools/check-doc-size.py', '"""The machinery below END CONFIG is shared."""\n# Everything below this line to END CONFIG is repo-specific.\nLIMIT = 100\n# ============ END CONFIG ============\nshared()\n');
  rep = json();
  assert.equal(fam(rep, 'docsize').copies.find((c) => c.root === 'p1').markerFound, true);
  assert.equal(fam(rep, 'docsize').distinct, docsizeBefore, 'prose mentions do not move the section start: p1 still hashes as shared()'); cases++;
  put('p1/tools/check-doc-size.py', '# Everything below this line to END CONFIG is repo-specific.\nLIMIT = 100\nshared()\n');
  assert.equal(fam(json(), 'docsize').copies.find((c) => c.root === 'p1').markerFound, false, 'a prose mention alone is not a marker'); cases++;
  put('p1/tools/check-doc-size.py', 'LIMIT = 100\n# END CONFIG\nshared()\n');

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

  // 12. A canonical bus copy (config-by-data, no CONFIG block) is hashed whole, labelled, never flagged,
  //     and still one version: copies converge on it, so each diverged copy is one excess.
  put('canon.json', JSON.stringify({ families: [{ name: 'docsize', names: ['check-doc-size.py'], sharedSectionMarker: 'END CONFIG', canonical: 'tools/factory/check-doc-size.py' }],
    roots: [{ name: 'bus', path: 'busfix', kind: 'bus' }, { name: 'q1', path: 'q1', kind: 'project' }, { name: 'q2', path: 'q2', kind: 'project' }] }));
  put('busfix/tools/factory/check-doc-size.py', 'def main(config): pass\n');
  put('busfix/tools/other/check-doc-size.py', 'stray()\n');
  put('q1/tools/check-doc-size.py', 'L = 1\n# ==== END CONFIG ====\nold_a()\n');
  put('q2/tools/check-doc-size.py', 'L = 2\n# ==== END CONFIG ====\nold_a()\n');
  const canonRep = JSON.parse(census(['--json', '--config', join(root, 'canon.json')]).stdout);
  const cf = fam(canonRep, 'docsize');
  const canonCopy = cf.copies.find((c) => c.path === 'tools/factory/check-doc-size.py');
  assert.equal(canonCopy.canonical, true); assert.equal(canonCopy.markerFound, null, 'canonical is not flagged NO MARKER');
  assert.equal(cf.copies.find((c) => c.path === 'tools/other/check-doc-size.py').markerFound, false, 'only the named bus path is canonical');
  assert.equal(cf.distinct, 3, 'canonical + stray + one shared q1/q2 version'); cases++;
  rmSync(join(root, 'busfix/tools/other/check-doc-size.py')); rmSync(join(root, 'q1/tools/check-doc-size.py')); rmSync(join(root, 'q2/tools/check-doc-size.py'));
  assert.equal(fam(JSON.parse(census(['--json', '--config', join(root, 'canon.json')]).stdout), 'docsize').excess, 0, 'only the canonical left = no excess'); cases++;

  // 13. Views (rule 7): each box's root set is its own count; the 'bus' view is always measurable,
  //     so a CI runner without the sibling clones still refuses a duplicate added on the bus.
  put('v.json', JSON.stringify({ families: [{ name: 'checkpoint', names: ['session-checkpoint.py'] }],
    roots: [{ name: 'bus', path: 'vbus', kind: 'bus' }, { name: 'far', path: 'not-on-this-box', kind: 'project' }, { name: 'v1', path: 'v1', kind: 'project' }] }));
  put('vbus/tools/session-checkpoint.py', 'a()\n');
  put('v1/session-checkpoint.py', 'b()\n');
  const vb = join(root, 'vbase.json');
  writeFileSync(vb, JSON.stringify({ total: 9, roots: ['bus', 'far'], families: { checkpoint: {} } }));
  const vc = (...extra) => census(['--config', join(root, 'v.json'), '--baseline', vb, ...extra]);
  r = vc('--add-view', 'bus', '--roots', 'bus');
  assert.equal(r.status, 0); assert.match(r.out, /view 'bus' seeded at 0/); cases++;
  assert.equal(vc('--add-view', 'bus', '--roots', 'bus').status, 1, 'an existing view is never re-seeded'); cases++;
  assert.equal(vc('--add-view', 'farview', '--roots', 'far').status, 3, 'a view over an invisible root cannot be seeded'); cases++;
  r = vc('--check');
  assert.equal(r.status, 0, 'primary UNMEASURED + bus view ok = 0'); assert.match(r.out, /UNMEASURED: .*far/); assert.match(r.out, /view 'bus': ok: count 0/); cases++;
  put('vbus/other/session-checkpoint.py', 'c()\n');
  r = vc('--check');
  assert.equal(r.status, 1, 'a second bus copy fails CI even with the fleet invisible'); assert.match(r.out, /view 'bus': ROSE: count 1 > baseline 0/); cases++;
  assert.equal(vc('--update-baseline').status, 1, 'a view rise is refused'); cases++;
  rmSync(join(root, 'vbus/other/session-checkpoint.py'));
  r = vc('--add-view', 'box');
  assert.equal(r.status, 0); assert.match(r.out, /view 'box' seeded at 1 over bus, v1/); cases++;
  rmSync(join(root, 'v1/session-checkpoint.py'));
  r = vc('--update-baseline');
  assert.equal(r.status, 0); assert.match(r.out, /view 'box' lowered 1 -> 0/);
  const vjs = JSON.parse(readFileSync(vb, 'utf8'));
  assert.equal(vjs.total, 9, 'the unmeasured primary is untouched'); assert.equal(vjs.views.find((v) => v.name === 'box').total, 0); cases++;

  // 14. Ratchet history (rule 8): a hand-edited raise is refused unless a ruling entry lands with it.
  const g = join(root, 'ratchet');
  mkdirSync(join(g, 'metrics'), { recursive: true });
  const gb = join(g, 'metrics', 'tool-census-baseline.json'), gr = join(g, 'metrics', 'tool-census-rulings.json');
  const sh = (...a) => execFileSync('git', ['-C', g, ...a], { encoding: 'utf8' });
  sh('init', '-q'); sh('config', 'user.email', 't@t'); sh('config', 'user.name', 't');
  const baseDoc = { total: 5, roots: ['bus'], families: { checkpoint: {} }, schedule: [{ by: '2026-11-01', max: 3 }], views: [{ name: 'bus', roots: ['bus'], families: ['checkpoint'], total: 2 }] };
  writeFileSync(gb, JSON.stringify(baseDoc)); sh('add', '--', 'metrics/tool-census-baseline.json'); sh('commit', '-qm', 'base');
  const rc = () => census(['--check-ratchet', 'HEAD', '--repo', g, '--baseline', gb]);
  const edit = (f) => { const d = JSON.parse(JSON.stringify(baseDoc)); f(d); writeFileSync(gb, JSON.stringify(d)); };
  edit((d) => { d.total = 4; d.views[0].total = 1; d.schedule = [{ by: '2026-10-25', max: 3 }]; });
  r = rc(); assert.equal(r.status, 0, 'lowering and tightening need nothing'); assert.match(r.out, /nothing loosened/); cases++;
  for (const [what, f, change] of [
    ['primary raise', (d) => { d.total = 6; }, 'total-raised'],
    ['view raise', (d) => { d.views[0].total = 3; }, 'total-raised'],
    ['view removed', (d) => { d.views = []; }, 'view-removed'],
    ['root dropped', (d) => { d.views[0].roots = ['x']; }, 'roots-removed'],
    ['family dropped', (d) => { d.families = {}; }, 'families-removed'],
    ['date moved later', (d) => { d.schedule = [{ by: '2026-11-08', max: 3 }]; }, 'schedule-loosened'],
    ['max raised', (d) => { d.schedule = [{ by: '2026-11-01', max: 4 }]; }, 'schedule-loosened'],
  ]) {
    edit(f); r = rc();
    assert.equal(r.status, 1, `${what} without a ruling is refused`); assert.match(r.out, /RATCHET REFUSED/);
    assert.match(r.out, new RegExp(`${change === 'total-raised' ? 'total' : change === 'view-removed' ? 'removed' : change === 'roots-removed' ? 'roots dropped' : change === 'families-removed' ? 'families dropped' : 'schedule allows'}.*UNRULED`));
    cases++;
  }
  edit((d) => { d.views[0].total = 3; });
  writeFileSync(gr, JSON.stringify({ rulings: [{ view: 'bus', change: 'total-raised', from: 2, to: 4, ruling: 'x', date: '2026-10-16' }] }));
  assert.equal(rc().status, 1, 'a ruling for a different raise does not cover this one'); cases++;
  writeFileSync(gr, JSON.stringify({ rulings: [{ view: 'bus', change: 'total-raised', from: 2, to: 3, ruling: 'RULINGS.md owner 2026-10-16', date: '2026-10-16' }] }));
  r = rc(); assert.equal(r.status, 0, 'a matching new ruling entry admits the raise'); assert.match(r.out, /\(ruled\)/); cases++;
  sh('add', '--', 'metrics/tool-census-baseline.json', 'metrics/tool-census-rulings.json'); sh('commit', '-qm', 'ruled raise');
  edit((d) => { d.views[0].total = 4; });
  assert.equal(rc().status, 1, 'a ruling already at the base is spent: 3 -> 4 needs a new entry'); cases++;
  assert.equal(census(['--check-ratchet', 'no-such-ref', '--repo', g, '--baseline', gb]).status, 2, 'unknown base revision is a tool failure'); cases++;

  // 15. CI sees every family: the doctrine-sync workflow's push AND pull_request path filters name every
  //     census family basename ('**/<name>'), so adding a copy anywhere on the bus runs the 'bus' view.
  const busRoot = join(dirname(tool), '..');
  const wf = readFileSync(join(busRoot, '.github', 'workflows', 'doctrine-sync.yml'), 'utf8').replace(/\r\n/g, '\n');
  const realCfg = JSON.parse(readFileSync(join(busRoot, 'tools', 'tool-census.config.json'), 'utf8'));
  const pushBlock = wf.slice(wf.indexOf('  push:'), wf.indexOf('  pull_request:'));
  const prBlock = wf.slice(wf.indexOf('  pull_request:'), wf.indexOf('  workflow_dispatch:'));
  for (const f of realCfg.families) for (const n of f.names) {
    assert.ok(pushBlock.includes(`- '**/${n}'`) && prBlock.includes(`- '**/${n}'`), `workflow path filters miss family name ${n}`);
  }
  assert.ok(wf.includes('--check-ratchet'), 'CI runs the ratchet history check'); cases++;
  const realBase = JSON.parse(readFileSync(join(busRoot, 'metrics', 'tool-census-baseline.json'), 'utf8'));
  const busView = (realBase.views || []).find((v) => v.name === 'bus');
  assert.ok(busView && busView.roots.length === 1 && busView.roots[0] === 'bus', "the committed baseline carries the CI-measurable 'bus' view");
  assert.deepEqual([...busView.families].sort(), realCfg.families.map((f) => f.name).sort(), "the 'bus' view counts every configured family"); cases++;

  // ---- E2 (re-expressed on the views design): runner release identity, scan roots, new-member notice ----
  // 18. Identity is the git blob id: identical bytes are one version wherever they sit; a vendored
  //     factory-pins/pin-runner.py equal to ANY blob on the bus's origin/master (else master) history of the canonical
  //     path joins it (CRLF checkout included); an edited or misplaced old copy diverges; no history = no equivalence.
  const gitIn = (dir, ...a) => execFileSync('git', ['-C', dir, '-c', 'user.email=t@example.invalid', '-c', 'user.name=t', '-c', 'core.autocrlf=false', ...a], { encoding: 'utf8' });
  const RUN = (n) => `print("runner release ${n}")\n`;
  execFileSync('git', ['init', '-q', '-b', 'master', join(root, 'busrel')]);
  for (const n of [1, 2, 3]) { put('busrel/tools/factory/pin-runner.py', RUN(n)); gitIn(join(root, 'busrel'), 'add', '-A'); gitIn(join(root, 'busrel'), 'commit', '-qm', `release ${n}`); }
  const prFam = { name: 'pinrunner', names: ['pin-runner.py'], canonical: 'tools/factory/pin-runner.py', releaseHistory: true };
  const prCfg = (name, ...rootNames) => { put(name, JSON.stringify({ families: [prFam], roots: rootNames.map((n) => ({ name: n, path: n, kind: n === 'busrel' ? 'bus' : 'project' })) })); return join(root, name); };
  const prRep = (cfg, ...extra) => fam(JSON.parse(census(['--json', '--config', cfg, ...extra]).stdout), 'pinrunner');
  put('r1/factory-pins/pin-runner.py', RUN(1).replace(/\n/g, '\r\n'));   // an OLD release, CRLF checkout
  put('r2/factory-pins/pin-runner.py', RUN(3));                          // the current release
  let pr = prRep(prCfg('rc.json', 'busrel', 'r1', 'r2', 'r3', 'r4'));
  assert.equal(pr.excess, 0, 'old + current release + the bus canonical are one version');
  assert.equal(pr.copies.find((c) => c.root === 'r1').release, 'history'); assert.equal(pr.copies.find((c) => c.root === 'busrel').release, 'canonical'); assert.equal(pr.historyRef, 'master'); cases++;
  put('r3/factory-pins/pin-runner.py', RUN(2) + '# local edit\n');
  pr = prRep(join(root, 'rc.json'));
  assert.equal(pr.excess, 1, 'a modified vendored runner is divergent'); assert.equal(pr.copies.find((c) => c.root === 'r3').release, undefined); cases++;
  put('r4/tools/pin-runner.py', RUN(1));
  assert.equal(prRep(join(root, 'rc.json')).excess, 2, 'an old release outside factory-pins/ is still divergent'); cases++;
  put('r5/tools/pin-runner.py', RUN(3));
  assert.equal(prRep(prCfg('rc3.json', 'busrel', 'r5')).excess, 0, 'the CURRENT canonical bytes outside factory-pins/ are the same version'); cases++;
  assert.equal(prRep(prCfg('rc2.json', 'r1', 'r2')).excess, 1, 'no bus clone, no history: no equivalence is assumed'); cases++;
  const bus1 = join(root, 'busrel');
  gitIn(bus1, 'checkout', '-q', '-b', 'side'); put('busrel/tools/factory/pin-runner.py', RUN(9)); gitIn(bus1, 'add', '-A'); gitIn(bus1, 'commit', '-qm', 'unmerged release'); gitIn(bus1, 'checkout', '-q', 'master');
  put('r5b/factory-pins/pin-runner.py', RUN(9)); const rc4 = prCfg('rc4.json', 'busrel', 'r5b');
  assert.equal(prRep(rc4).excess, 1, 'a release that exists only on another branch is not canonical history');
  assert.equal(prRep(rc4, '--bus-ref', 'side').excess, 0, 'control: the same blob on the ref the history is read from'); cases++;

  // 19. A root's "scan" limits a non-repository workspace to named subdirectories; a missing scan dir is UNMEASURED.
  put('ws/tools/session-checkpoint.py', 'print("ws live")\n'); put('ws/corpus/deep/session-checkpoint.py', 'print("in the corpus")\n');
  put('scan.json', JSON.stringify({ families: [{ name: 'checkpoint', names: ['session-checkpoint.py'] }], roots: [{ name: 'ws', path: 'ws', kind: 'project', scan: ['tools'] }] }));
  assert.deepEqual(fam(JSON.parse(census(['--json', '--config', join(root, 'scan.json')]).stdout), 'checkpoint').copies.map((c) => c.path), ['tools/session-checkpoint.py'], 'only the scanned subdir is walked');
  put('scan2.json', JSON.stringify({ families: [{ name: 'checkpoint', names: ['session-checkpoint.py'] }], roots: [{ name: 'ws', path: 'ws', kind: 'project', scan: ['tools', 'no-such-dir'] }] }));
  const scan2 = JSON.parse(census(['--json', '--config', join(root, 'scan2.json')]).stdout);
  assert.deepEqual([scan2.measuredRoots, scan2.absentRoots], [[], ['ws']], 'a missing scan dir is not a measured zero'); assert.match(scan2.absentWhy.ws, /scan dir\(s\) missing: no-such-dir/); cases++;

  execFileSync('git', ['init', '-q', join(root, 'ws')]);   // the same root as a git checkout: ls-files lists corpus/ too, scan must still limit it
  assert.deepEqual(fam(JSON.parse(census(['--json', '--config', join(root, 'scan.json')]).stdout), 'checkpoint').copies.map((c) => c.path), ['tools/session-checkpoint.py'], 'scan limits a git root as well'); cases++;

  // 20. Configured members that no baseline view lists are named (informational; the verdict is unchanged).
  put('nm.json', JSON.stringify({ families: [{ name: 'checkpoint', names: ['session-checkpoint.py'] }, { name: 'newfam', names: ['newfam.py'] }],
    roots: [{ name: 'bus', path: 'nmbus', kind: 'bus' }, { name: 'newroot', path: 'nmbus', kind: 'project' }] }));
  put('nmbus/tools/session-checkpoint.py', 'x()\n');
  const nmBase = join(root, 'nm-baseline.json');
  writeFileSync(nmBase, JSON.stringify({ total: 0, roots: ['bus'], families: { checkpoint: {} } }));
  r = census(['--check', '--config', join(root, 'nm.json'), '--baseline', nmBase]);
  assert.equal(r.status, 0, r.out); assert.match(r.out, /NEW-MEMBERS-UNBASELINED: root:newroot, family:newfam/); assert.match(r.out, /Informational/); cases++;

  assert.ok(existsSync(tool));
  console.log(`tool-census fixtures: ${cases} cases passed`);
} finally { rmSync(root, { recursive: true, force: true }); }
