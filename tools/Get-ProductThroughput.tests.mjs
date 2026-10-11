#!/usr/bin/env node
// Offline regressions for tools/Get-ProductThroughput.ps1 -Lines (fixture git repos in a temp dir).
// Proves: bucket attribution by most-specific pattern, rename attribution, binary ignored,
// merge exclusion (including an evil merge), the -Since window edge, the cross-project ranking,
// fail-closed inputs, and that the classic commit-count mode is unchanged.
import assert from 'node:assert/strict';
import { spawnSync, execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync, appendFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const tool = join(dirname(fileURLToPath(import.meta.url)), 'Get-ProductThroughput.ps1');
const root = mkdtempSync(join(tmpdir(), 'product-throughput-'));
// Hooks export GIT_DIR/GIT_WORK_TREE; inheriting them would point every fixture at a real repo.
const env = Object.fromEntries(Object.entries(process.env).filter(([k]) => !/^GIT_/.test(k)));
Object.assign(env, { GIT_TERMINAL_PROMPT: '0', GIT_CONFIG_NOSYSTEM: '1', GIT_AUTHOR_NAME: 'fixture',
  GIT_AUTHOR_EMAIL: 'fixture@example.invalid', GIT_COMMITTER_NAME: 'fixture', GIT_COMMITTER_EMAIL: 'fixture@example.invalid' });

const git = (cwd, args, extra = {}) => execFileSync('git', ['-C', cwd, '-c', 'core.autocrlf=false', '-c', 'commit.gpgsign=false', ...args],
  { encoding: 'utf8', env: { ...env, ...extra } }).trim();
const lines = (n, tag) => Array.from({ length: n }, (_, i) => `${tag} ${i}`).join('\n') + '\n';
const put = (repo, rel, text) => { const p = join(repo, rel); mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, text); };
const commit = (repo, msg, date) => { git(repo, ['add', '-A']); git(repo, ['commit', '-q', '-m', msg], date ? { GIT_AUTHOR_DATE: date, GIT_COMMITTER_DATE: date } : {}); };
const newRepo = (name) => { const r = join(root, name); mkdirSync(r); git(r, ['init', '-q', '-b', 'master']); return r; };
const run = (args) => {
  const r = spawnSync('pwsh', ['-NoProfile', '-NonInteractive', '-File', tool, ...args], { encoding: 'utf8', env, timeout: 120000 });
  return { code: r.status, out: r.stdout + r.stderr };
};
const classes = { product: ['src/'], tests: ['tests/'], 'factory-tooling': ['tools/'],
  'coordination-paperwork': ['docs/', './*.md'], 'vendored-copies': ['templates/', 'src/vendor/'] };

try {
  // ---- Project A: one of everything, plus an out-of-window commit and an evil merge ----
  const a = newRepo('a');
  put(a, 'src/old.c', lines(1000, 'old'));
  commit(a, 'old product, before the window', '2020-01-01T00:00:00Z');
  put(a, 'src/main.c', lines(10, 'p'));          // product 10
  put(a, 'src/vendor/lib.c', lines(6, 'v'));     // vendored 6 (more specific than src/)
  put(a, 'tests/t.c', lines(4, 't'));            // tests 4
  put(a, 'tools/x.ps1', lines(20, 'x'));         // tooling 20
  put(a, 'docs/plan.md', lines(30, 'd'));        // paperwork 30
  put(a, 'README.md', lines(5, 'r'));            // paperwork 5 (root-level ./*.md)
  put(a, 'misc/notes.md', lines(7, 'm'));        // unclassified 7 (./*.md is root-only)
  writeFileSync(join(a, 'src', 'blob.bin'), Buffer.from([0, 1, 2, 0, 255, 0, 3]));  // binary: ignored
  commit(a, 'mixed');
  // rename with an edit: lines attributed to the NEW path (tests/), not the old one
  git(a, ['mv', 'src/main.c', 'tests/main_test.c']);
  appendFileSync(join(a, 'tests', 'main_test.c'), 'added after move\n');
  commit(a, 'rename');                           // tests +1 (rename detected, only the edit counts)
  git(a, ['checkout', '-q', '-b', 'side']);
  put(a, 'src/side.c', lines(3, 's'));           // product 3, a real non-merge commit
  commit(a, 'side work');
  git(a, ['checkout', '-q', 'master']);
  put(a, 'docs/master.md', lines(2, 'mm'));      // paperwork 2
  commit(a, 'master work');
  git(a, ['merge', '--no-ff', '--no-commit', '-q', 'side']);
  put(a, 'src/evil.c', lines(500, 'e'));         // lives only in the merge commit: must not count
  git(a, ['add', '-A']); git(a, ['commit', '-q', '-m', 'evil merge']);

  // ---- Project B: more product per week, so it must rank first ----
  const b = newRepo('b');
  put(b, 'src/app.c', lines(40, 'b')); put(b, 'docs/x.md', lines(10, 'bd'));
  commit(b, 'b work');
  // ---- Project C: zero product ----
  const c = newRepo('c');
  put(c, 'docs/only.md', lines(9, 'c'));
  commit(c, 'paper only');

  const cfgPath = join(root, 'classes.json');
  writeFileSync(cfgPath, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'alpha', root: a, ref: 'master', classes },
    { name: 'bravo', root: b, ref: 'HEAD', classes },
    { name: 'charlie', root: c, classes } ] }));

  const since = new Date(Date.now() - 14 * 86400e3).toISOString().replace(/\.\d+Z$/, 'Z');
  const r = run(['-Lines', '-ClassConfig', cfgPath, '-Since', since, '-Json']);
  assert.equal(r.code, 0, r.out);
  const j = JSON.parse(r.out);
  assert.equal(j.schema, 'fleet/product-throughput-lines/v1');
  assert.equal(j.authority, 'DIAGNOSTIC_ONLY_NEVER_A_GATE_OR_TARGET');
  const A = j.projects.find((p) => p.project === 'alpha');
  // bucket attribution
  assert.deepEqual({ ...A.lines }, { product: 13, tests: 5, 'vendored-copies': 6, 'factory-tooling': 20,
    'coordination-paperwork': 37, unclassified: 7 }, JSON.stringify(A.lines));
  // product = main.c 10 + side.c 3 (main.c's later move is tests' +1 edit; the rename itself is free)
  assert.equal(A.total_lines, 88);
  assert.equal(A.product_share, Math.round((13 / 88) * 1e4) / 1e4);
  assert.equal(A.binary_files_ignored, 1);
  assert.deepEqual(A.top_unclassified.map((u) => [u.prefix, u.lines]), [['misc/', 7]]);
  // merge exclusion: the merge is counted as excluded, its evil 500 lines are not in any bucket,
  // and the 1000-line commit before -Since is outside the window
  assert.equal(A.merges_excluded, 1);
  assert.equal(A.commits_counted, 4);
  assert.equal(A.ref_name, 'master');
  // ranking: bravo (40 product) > alpha (13) > charlie (0)
  assert.deepEqual(j.ranking.map((x) => x.project), ['bravo', 'alpha', 'charlie']);
  assert.deepEqual(j.ranking.map((x) => x.rank), [1, 2, 3]);
  const B = j.ranking[0];
  assert.equal(B.product_lines, 40); assert.equal(B.product_share, 0.8);
  assert.ok(Math.abs(B.product_lines_per_week - 20) < 0.2, `per week ${B.product_lines_per_week}`);
  assert.equal(j.ranking[2].product_lines_per_week, 0);

  // -Project filter and the human table
  const t = run(['-Lines', '-ClassConfig', cfgPath, '-Since', since, '-Project', 'charlie,bravo']);
  assert.equal(t.code, 0, t.out);
  assert.match(t.out, /1\s+bravo/); assert.match(t.out, /2\s+charlie/); assert.doesNotMatch(t.out, /alpha/);
  assert.match(t.out, /DIAGNOSTIC ONLY/);

  // fail closed: naive -Since, missing repo, bad ref, unknown bucket
  assert.equal(run(['-Lines', '-ClassConfig', cfgPath, '-Since', '2026-01-01T00:00:00']).code, 4);
  const bad = join(root, 'bad.json');
  writeFileSync(bad, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'gone', root: join(root, 'nope'), classes }, { name: 'badref', root: b, ref: 'no-such-branch', classes } ] }));
  const f = run(['-Lines', '-ClassConfig', bad, '-Json']);
  assert.equal(f.code, 4, f.out);
  const fj = JSON.parse(f.out);
  assert.equal(fj.projects.find((p) => p.project === 'gone').error, 'not a git repository');
  assert.equal(fj.projects.find((p) => p.project === 'badref').error, 'ref not found: no-such-branch');
  writeFileSync(bad, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'typo', root: b, classes: { prodcut: ['src/'] } } ] }));
  const typo = run(['-Lines', '-ClassConfig', bad]);
  assert.equal(typo.code, 4, typo.out); assert.match(typo.out, /unknown bucket 'prodcut'/);

  // line mode is diagnostic: a zero-product project is still exit 0, never STALLED/1
  assert.equal(run(['-Lines', '-ClassConfig', cfgPath, '-Project', 'charlie']).code, 0);

  // classic commit-count mode unchanged
  assert.equal(run(['-Root', a]).code, 4);
  const classic = run(['-Root', b, '-ProductPath', 'src/', '-AsJson']);
  assert.equal(classic.code, 0, classic.out);
  const cj = JSON.parse(classic.out);
  assert.equal(cj.schema, 'fleet/product-throughput/v1');
  assert.equal(cj.product_commits_in_window, 1);
  assert.equal(cj.verdict, 'MOVING');

  console.log('PASS Get-ProductThroughput.tests.mjs');
} finally {
  rmSync(root, { recursive: true, force: true });
}
