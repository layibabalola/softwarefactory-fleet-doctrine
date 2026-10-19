#!/usr/bin/env node
// Offline regressions for tools/Get-ProductThroughput.ps1 -Lines (fixture git repos in a temp dir).
// Proves: bucket attribution by most-specific pattern, rename attribution, binary ignored,
// merge exclusion (including an evil merge), the -Since window edge, the cross-project ranking,
// fail-closed inputs, and that the classic commit-count mode is unchanged. Added 2026-10-16: the changed-BYTES
// column (a 50 KB packet line rewrite vs 10 app lines), commit classes, the DNG class entry, and -Repo/-Days.
// Added 2026-10-19 (review E3 r2): DNG profiles/ is runtime-data, not product (N1); both git passes delete their temp files (N2).
import assert from 'node:assert/strict';
import { spawnSync, execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync, appendFileSync, readFileSync, readdirSync } from 'node:fs';
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
    'coordination-paperwork': 37, 'runtime-data': 0, unclassified: 7 }, JSON.stringify(A.lines));
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

  // ---- bytes column, commit classes, DNG class mapping, -Repo / -Days (added 2026-10-16, owner defect D3) ----
  // Alpha's existing rows must carry the additive fields without changing anything above.
  assert.equal(A.product_share_lines, A.product_share);
  assert.ok(A.total_bytes > 0 && A.bytes.product > 0, JSON.stringify(A.bytes));
  assert.equal(A.commit_classes.product, 2);                              // 'mixed' + 'side work'
  const dngEntry = JSON.parse(readFileSync(join(dirname(tool), 'product-throughput-classes.json'), 'utf8')).projects.find((p) => p.name === 'dng');
  assert.ok(dngEntry, 'dng entry exists in the real class config');
  assert.equal(dngEntry.ref, 'master');

  // D3 fixture: one 50,000-byte packet state line rewritten (2 lines, ~100 KB) vs 10 lines of app source (40 B).
  const d = newRepo('dng-shape');
  put(d, 'packets/x.md', 'a'.repeat(50000) + '\n');
  commit(d, 'old packet state line, before the window', '2020-01-01T00:00:00Z');
  put(d, 'packets/x.md', 'b'.repeat(50000) + '\n');
  commit(d, 'cop tick: rewrite the whole state line');
  put(d, 'DngAutoProcessor.Core/A.cs', lines(10, 'p'));                // 10 lines x 4 B = 40 B
  commit(d, 'fix: app change');
  const dcfg = join(root, 'dng-classes.json');
  writeFileSync(dcfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'dng', root: join(root, 'does-not-exist'), ref: 'master', classes: dngEntry.classes } ] }));
  const dr = run(['-Lines', '-ClassConfig', dcfg, '-Repo', d, '-Project', 'dng', '-Days', '14', '-Json']);
  assert.equal(dr.code, 0, dr.out);
  const dj = JSON.parse(dr.out);
  const D = dj.projects[0];
  assert.match(D.root.replace(/\\/g, '/'), /\/dng-shape$/, '-Repo overrides the config root');
  assert.equal(D.lines.product, 10); assert.equal(D.lines['coordination-paperwork'], 2); assert.equal(D.total_lines, 12);
  assert.equal(D.bytes['coordination-paperwork'], 2 * 50001);            // -50,000 and +50,000 bytes, each plus a newline
  assert.equal(D.bytes.product, 40); assert.equal(D.total_bytes, 100042);
  assert.ok(D.product_share_lines > 0.8, `lines share ${D.product_share_lines}`);   // 10/12: looks healthy by lines
  assert.ok(D.product_share_bytes < 0.001, `bytes share ${D.product_share_bytes}`); // 40/100042: the paperwork shows
  assert.ok(D.product_share_lines > 100 * D.product_share_bytes, 'lines and bytes diverge, bytes lower');
  assert.deepEqual({ ...D.commit_classes }, { product: 1, tests: 0, 'paperwork-only': 1, 'tooling-only': 0, 'paperwork-and-tooling': 0, other: 0 });
  assert.equal(D.commits_touching_product, 1); assert.equal(D.commits_paperwork_tooling_only, 1);
  assert.equal(D.paperwork_tooling_commits_per_product_commit, 1);
  assert.equal(dj.ranking[0].product_share_bytes, D.product_share_bytes);
  assert.equal(dj.ranking[0].product_bytes, 40);
  // table output carries the new columns
  const dt = run(['-Lines', '-ClassConfig', dcfg, '-Repo', d, '-Project', 'dng']);
  assert.equal(dt.code, 0, dt.out); assert.match(dt.out, /bshare/); assert.match(dt.out, /pc\/ac/); assert.match(dt.out, /0\.04%/);
  // -NoBytes keeps the default fields and nulls the byte ones
  const nb = JSON.parse(run(['-Lines', '-ClassConfig', dcfg, '-Repo', d, '-Project', 'dng', '-NoBytes', '-Json']).out).projects[0];
  assert.equal(nb.bytes, null); assert.equal(nb.product_share_bytes, null); assert.equal(nb.product_share, D.product_share);

  // DNG class mapping, one file per path class, through the REAL dng class entry.
  const m = newRepo('dng-map');
  const one = (rel) => put(m, rel, 'x\n');
  ['DngAutoProcessor.Core/a.cs', 'DngAutoProcessor.CorpusBridge/b.cs', 'DngAutoProcessor.App/c.cs', 'DngAutoProcessor.Future/d.cs'].forEach(one); // product 4
  one('profiles/house-style-profile.json');                                                                                                     // runtime-data 1 (E3 r2 N1: never product)
  ['DngAutoProcessor.Tests/t.cs', 'corpus/c.txt'].forEach(one);                                                                                 // tests 2 (corpus = validation data)
  ['tools/a.ps1', 'scripts/b.ps1', '.githooks/pre-commit', '.github/w.yml', 'DngAutoProcessor.sln', 'global.json', 'analysis/a.py'].forEach(one); // tooling 7
  ['WORK.md', 'WORK-DONE.md', 'packets/p.md', 'metrics/ratify/c/receipt.json', 'docs/d.md', 'review/r.md', 'receipts/x.txt', 'README.md',
    'analysis/data.json', 'audit-artifacts/x.txt', '.claude-state/m.md', '.codex-state/c.md', '.remember/r.md', 'AGENTS/a.md', 'skill-specs/s.md',
    '_FROZEN-20260905/f.md', 'AUDIT.txt', 'AUDIT.csv', 'cfg.json'].forEach(one);                                                                // paperwork 19
  one('weird/x.txt');                                                                                                                           // unclassified 1
  writeFileSync(join(m, 'DngAutoProcessor.Core', 'blob.bin'), Buffer.alloc(100));                                                               // binary: added, 100 B to product bytes
  commit(m, 'one of each');
  // a learned-store sync alone (the 3b2aff37 shape: one multi-MB store rewritten by script) is not a product commit
  put(m, 'profiles/look-teaching-store.json', lines(50, 'store'));
  commit(m, 'profiles synced back via sanctioned script');
  const mr = run(['-Lines', '-ClassConfig', dcfg, '-Repo', m, '-Project', 'dng', '-Json']);
  assert.equal(mr.code, 0, mr.out);
  const M = JSON.parse(mr.out).projects[0];
  assert.deepEqual({ ...M.lines }, { product: 4, tests: 2, 'vendored-copies': 0, 'factory-tooling': 7, 'coordination-paperwork': 19, 'runtime-data': 51, unclassified: 1 }, JSON.stringify(M.lines));
  assert.equal(M.product_share, Math.round((4 / 84) * 1e4) / 1e4);
  assert.equal(M.bytes.product, 4 * 2 + 100);                             // 4 text lines of 'x\n' (marker-inclusive = 2) + the 100-byte binary
  assert.equal(M.bytes['runtime-data'], 2 + 10 * 8 + 40 * 9);           // 'x\n' + 'store 0'..'store 9' (8 B each) + 'store 10'..'store 49' (9 B each)
  assert.equal(M.bytes['coordination-paperwork'], 38);
  assert.equal(M.binary_files, 1); assert.equal(M.binary_files_ignored, 1);  // deprecated alias keeps its value
  assert.deepEqual(M.top_unclassified.map((u) => u.prefix), ['weird/']);
  assert.deepEqual({ ...M.commit_classes }, { product: 1, tests: 0, 'paperwork-only': 0, 'tooling-only': 0, 'paperwork-and-tooling': 0, other: 1 }, JSON.stringify(M.commit_classes));
  // and the real entry says so directly: no product pattern reaches profiles/, runtime-data names it
  assert.deepEqual(dngEntry.classes['runtime-data'], ['profiles/']);
  assert.ok(!dngEntry.classes.product.some((p) => p.startsWith('profiles')), JSON.stringify(dngEntry.classes.product));

  // RAW bytes: CRLF, a lone CR, Latin-1 0xE9 and a final line with no EOL are counted as git stores them;
  // a same-size binary REPLACEMENT counts old + new (200), not the net size delta (0).
  const rw = newRepo('raw');
  const rawClasses = { product: ['src/'], tests: ['tests/'] };
  writeFileSync(join(rw, 'keep.txt'), 'k\n'); mkdirSync(join(rw, 'src'));
  writeFileSync(join(rw, 'src', 'bin.dat'), Buffer.alloc(100, 0));
  commit(rw, 'binary before the window', '2020-01-01T00:00:00Z');
  writeFileSync(join(rw, 'src', 'crlf.c'), Buffer.from('a\r\n'));                          // "+a\r" = 3
  writeFileSync(join(rw, 'src', 'lonecr.c'), Buffer.from('p\rq\nzzzzzzzzzz\n'));           // "+p\rq" 4 + "+zzzzzzzzzz" 11 = 15 (a lone CR does not split)
  writeFileSync(join(rw, 'src', 'latin1.c'), Buffer.from([0xe9, 0x0a]));                   // "+\xe9" = 2 (not U+FFFD = 4)
  writeFileSync(join(rw, 'src', 'noeol.c'), Buffer.from('abc'));                           // "+abc" minus the LF it does not have = 3
  writeFileSync(join(rw, 'src', 'bin.dat'), Buffer.alloc(100, 1).fill(0, 0, 1));           // same size, different bytes, still binary
  commit(rw, 'raw bytes');
  const rawCfg = join(root, 'raw-classes.json');
  writeFileSync(rawCfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [{ name: 'raw', root: rw, ref: 'master', classes: rawClasses }] }));
  const rr = run(['-Lines', '-ClassConfig', rawCfg, '-Days', '14', '-Json']);
  assert.equal(rr.code, 0, rr.out);
  const R = JSON.parse(rr.out).projects[0];
  assert.equal(R.lines.product, 5);
  assert.equal(R.bytes.product, 3 + 15 + 2 + 3 + 200, JSON.stringify(R.bytes));
  assert.equal(R.binary_files, 1);

  // Temp-file hygiene (E3 r2 N2): both git passes capture stdout in a temp file and must delete it. TMP/TEMP/TMPDIR point
  // at a private empty dir. A copy of the tool whose cleanup is a no-op must leave its two files there, which proves the
  // redirect took effect, so the real tool's empty dir is not a vacuous pass.
  const tmpRun = (script, dir) => {
    mkdirSync(dir);
    const t = spawnSync('pwsh', ['-NoProfile', '-NonInteractive', '-File', script, '-Lines', '-ClassConfig', rawCfg, '-Days', '14', '-Json'],
      { encoding: 'utf8', env: { ...env, TMP: dir, TEMP: dir, TMPDIR: dir }, timeout: 120000 });
    assert.equal(t.status, 0, t.stdout + t.stderr);
    assert.equal(JSON.parse(t.stdout).projects[0].bytes.product, R.bytes.product);   // both passes ran
    return readdirSync(dir);
  };
  const cleanup = 'finally { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }';
  const toolSrc = readFileSync(tool, 'utf8');
  assert.equal(toolSrc.split(cleanup).length, 2, 'exactly one temp-file cleanup site in the tool');
  mkdirSync(join(root, 'mutant'));
  const mutant = join(root, 'mutant', 'Get-ProductThroughput.ps1');
  writeFileSync(mutant, toolSrc.replace(cleanup, 'finally { $null = 1 }'));
  const leaked = tmpRun(mutant, join(root, 'tmp-mutant'));
  assert.equal(leaked.length, 2, `the no-op-cleanup mutant leaves one file per git pass: ${JSON.stringify(leaked)}`);
  assert.deepEqual(tmpRun(tool, join(root, 'tmp-real')), [], 'the tool leaves no temp files behind');

  // Odd paths: ' and ', spaces, a TAB in the name (made through the index, NTFS cannot hold one on disk) and a rename.
  // Paths come from `git log --raw --numstat -z`, never from the 'Binary files a/x and b/y differ' prose.
  const od = newRepo('odd');
  put(od, 'src/old and name.c', lines(4, 'r'));
  writeFileSync(join(od, 'src', 'old bin name.bin'), Buffer.alloc(40, 0));
  commit(od, 'rename sources, before the window', '2020-01-01T00:00:00Z');
  writeFileSync(join(od, 'src', 'a and b.bin'), Buffer.alloc(100, 0));                    // binary, product: 100
  mkdirSync(join(od, 'tests')); writeFileSync(join(od, 'tests', 'with space.bin'), Buffer.alloc(50, 0));  // binary, tests: 50
  put(od, 'src/t and u.c', lines(3, 'q'));                                                // text, product: 3 lines, 12 B
  commit(od, 'odd names');
  git(od, ['mv', 'src/old and name.c', 'tests/new and name.c']);
  appendFileSync(join(od, 'tests', 'new and name.c'), 'added\n');                         // rename + edit: tests 1 line, 6 B
  git(od, ['mv', 'src/old bin name.bin', 'tests/new bin name.bin']);                      // pure binary rename: nothing changed
  commit(od, 'renames');
  const idx = (rel, content) => {
    const tmp = join(root, 'blob.tmp'); writeFileSync(tmp, content);
    const sha = git(od, ['hash-object', '-w', tmp]);
    git(od, ['-c', 'core.protectNTFS=false', 'update-index', '--add', '--cacheinfo', `100644,${sha},${rel}`]);
  };
  idx('src/tab\tbin.bin', Buffer.alloc(30, 0));                                           // binary with a TAB in the name: product 30
  idx('src/tab\ttext.c', Buffer.from('zz\n'));                                            // text with a TAB in the name: 1 line, 3 B
  git(od, ['commit', '-q', '-m', 'tab names']);
  const odCfg = join(root, 'odd.json');
  writeFileSync(odCfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [{ name: 'odd', root: od, ref: 'master', classes: rawClasses }] }));
  const oj = run(['-Lines', '-ClassConfig', odCfg, '-Days', '14', '-Json']);
  assert.equal(oj.code, 0, oj.out);
  const O = JSON.parse(oj.out).projects[0];
  assert.deepEqual({ ...O.lines }, { product: 4, tests: 1, 'vendored-copies': 0, 'factory-tooling': 0, 'coordination-paperwork': 0, 'runtime-data': 0, unclassified: 0 }, JSON.stringify(O.lines));
  assert.deepEqual({ ...O.bytes }, { product: 100 + 12 + 30 + 3, tests: 50 + 6, 'vendored-copies': 0, 'factory-tooling': 0, 'coordination-paperwork': 0, 'runtime-data': 0, unclassified: 0 }, JSON.stringify(O.bytes));
  assert.equal(O.binary_files, 3);
  // -AsRows carries the bytes additively beside upstream's reproducing command
  const orow = JSON.parse(run(['-Lines', '-AsRows', '-ClassConfig', odCfg, '-Days', '14']).out.trim());
  assert.equal(orow.bytes.product, 145); assert.equal(orow.product_share_bytes, O.product_share_bytes);
  assert.equal(orow.commit_classes.product, 2); assert.match(orow.command, /-At [0-9a-f]{40} -Since \S+ -Until \S+$/);

  // ---- final fix pass: pass-2 desync guards, typechange, -Repo in the command, binary_files_ignored keeps its meaning ----
  const plumb = (r, args) => git(r, ['-c', 'core.protectNTFS=false', ...args]);
  const blobOf = (r, text) => { const t = join(root, 'blob2.tmp'); writeFileSync(t, text); return git(r, ['hash-object', '-w', t]); };
  const measure = (r) => { const o = run(['-Lines', '-ClassConfig', dcfg, '-Repo', r, '-Project', 'dng', '-Days', '30', '-Json']); assert.equal(o.code, 0, o.out); return JSON.parse(o.out).projects[0]; };
  // A: a gitlink (product path, sorts before docs/) and a docs edit in ONE commit. With diff.submodule=log git prints no
  // `diff --git` header for the gitlink, which used to shift docs/x.md's 6 bytes onto the product entry silently.
  const fa = newRepo('fx-a');
  put(fa, 'DngAutoProcessor.Core/keep.cs', 'k\n'); put(fa, 'docs/x.md', '');
  commit(fa, 'base');                                                                      // product 2 B
  plumb(fa, ['update-index', '--add', '--cacheinfo', `160000,${'1'.repeat(40)},DngAutoProcessor.Core/sub`]);
  put(fa, 'docs/x.md', 'hello\n'); git(fa, ['add', 'docs/x.md']);
  git(fa, ['commit', '-q', '-m', 'gitlink + docs edit']);                                  // product 59 ("+Subproject commit " + 40 hex), paperwork 6
  const A0 = measure(fa);
  assert.equal(A0.error, null); assert.equal(A0.bytes.product, 2 + 59); assert.equal(A0.bytes['coordination-paperwork'], 6);
  git(fa, ['config', 'diff.submodule', 'log']);                                            // the seat setting that broke the positional mapping
  const A1 = measure(fa);
  assert.equal(A1.error, null); assert.deepEqual({ ...A1.bytes }, { ...A0.bytes }, 'diff.submodule=log must not change a single byte');
  git(fa, ['config', 'diff.submodule', 'diff']);
  assert.deepEqual({ ...measure(fa).bytes }, { ...A0.bytes });
  // B: a typechange (regular file -> symlink) is ONE raw entry but TWO diff sections, both attributed to its bucket
  const fb = newRepo('fx-b');
  put(fb, 'DngAutoProcessor.Core/a.cs', 'x\n'); put(fb, 'docs/link.md', 'one\n');
  commit(fb, 'base');                                                                      // product 2, paperwork 4
  put(fb, 'DngAutoProcessor.Core/a.cs', 'xy\n'); git(fb, ['add', '-A']);                   // product -x +xy = 5
  plumb(fb, ['update-index', '--cacheinfo', `120000,${blobOf(fb, 'target')},docs/link.md`]);
  git(fb, ['commit', '-q', '-m', 'typechange + edit']);                                    // paperwork -one 4 + +target 7 - no-EOL 1 = 10
  assert.match(git(fb, ['log', '-1', '--raw', '--format=']), /\sT\sdocs\/link\.md/);
  const B0 = measure(fb);
  assert.equal(B0.error, null); assert.equal(B0.bytes.product, 2 + 5); assert.equal(B0.bytes['coordination-paperwork'], 4 + 10);
  assert.equal(B0.commit_classes.product, 2);
  // C: binary_files_ignored keeps its ORIGINAL meaning (every numstat '-' entry, pure renames and mode-only changes
  // included); binary_files counts only binaries whose content changed
  const fc = newRepo('fx-c');
  mkdirSync(join(fc, 'DngAutoProcessor.Core'));
  writeFileSync(join(fc, 'DngAutoProcessor.Core', 'old.bin'), Buffer.alloc(40, 0));
  writeFileSync(join(fc, 'DngAutoProcessor.Core', 'mode.bin'), Buffer.alloc(40, 1).fill(0, 0, 1));
  commit(fc, 'base');                                                                      // 2 binary adds
  git(fc, ['mv', 'DngAutoProcessor.Core/old.bin', 'DngAutoProcessor.Core/new.bin']);       // pure binary rename
  git(fc, ['update-index', '--chmod=+x', 'DngAutoProcessor.Core/mode.bin']);               // mode-only binary change
  git(fc, ['commit', '-q', '-m', 'rename + mode']);
  const numstatBinary = git(fc, ['log', '--numstat', '--format=']).split('\n').filter((l) => /^-\t-\t/.test(l)).length;
  assert.equal(numstatBinary, 4);
  const C0 = measure(fc);
  assert.equal(C0.binary_files_ignored, numstatBinary, 'deprecated field = every numstat binary entry, as before');
  assert.equal(C0.binary_files, 2, 'new field = binaries whose content changed');
  assert.equal(C0.bytes.product, 80);
  // -AsRows: the command carries -Repo when the row was measured with it, and re-running it reproduces the row
  const rr2 = run(['-Lines', '-AsRows', '-ClassConfig', dcfg, '-Repo', fa, '-Project', 'dng', '-Days', '30']);
  assert.equal(rr2.code, 0, rr2.out);
  const arow = JSON.parse(rr2.out.trim());
  assert.match(arow.command, / -AsRows -Repo \S+fx-a -Project dng -At [0-9a-f]{40} -Since /, arow.command);
  assert.equal(arow.bytes.product, 61);
  const cargs = arow.command.split(' ').slice(arow.command.split(' ').indexOf('-Lines'));
  const again2 = JSON.parse(run([...cargs, '-ClassConfig', dcfg]).out.trim());
  assert.deepEqual(again2.bytes, arow.bytes); assert.deepEqual(again2.lines, arow.lines); assert.equal(again2.command, arow.command);
  // and a row measured WITHOUT -Repo has no -Repo in its command
  assert.doesNotMatch(JSON.parse(run(['-Lines', '-AsRows', '-ClassConfig', odCfg, '-Days', '14']).out.trim()).command, /-Repo/);

  // every commit-class branch with a nonzero count, plus the paperwork-only variants
  const cc = newRepo('classes');
  const step = (files, msg) => { Object.entries(files).forEach(([k, v]) => put(cc, k, v)); commit(cc, msg); };
  step({ 'src/a.c': 'a\n' }, 'product 1'); step({ 'src/b.c': 'b\n' }, 'product 2');
  step({ 'tests/t.c': 't\n' }, 'tests only');
  step({ 'tools/x.ps1': 'x\n' }, 'tooling only');
  step({ 'docs/a.md': 'a\n', 'tools/y.ps1': 'y\n' }, 'paperwork and tooling');
  step({ 'docs/b.md': 'b\n' }, 'paperwork only 1'); step({ 'docs/c.md': 'c\n' }, 'paperwork only 2');
  step({ 'templates/v.c': 'v\n' }, 'other: vendored'); step({ 'misc/z.txt': 'z\n' }, 'other: unclassified');
  const ccCfg = join(root, 'cc.json');
  writeFileSync(ccCfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [{ name: 'cc', root: cc, ref: 'master', classes }] }));
  const C = JSON.parse(run(['-Lines', '-ClassConfig', ccCfg, '-Days', '14', '-Json']).out).projects[0];
  assert.deepEqual({ ...C.commit_classes }, { product: 2, tests: 1, 'paperwork-only': 2, 'tooling-only': 1, 'paperwork-and-tooling': 1, other: 2 }, JSON.stringify(C.commit_classes));
  assert.equal(C.commits_touching_product, 2);
  assert.equal(C.commits_paperwork_only, 2);
  assert.equal(C.commits_paperwork_tooling_only, 4);                      // paperwork-only 2 + tooling-only 1 + paperwork-and-tooling 1
  assert.equal(C.paperwork_tooling_commits_per_product_commit, 2);
  assert.equal(C.paperwork_only_commits_per_product_commit, 1);

  // -At <raw SHA> (upstream's pinning mechanism) measures a detached commit, labels the row with the SHA, and reproduces the branch run
  const dsha = git(d, ['rev-parse', 'HEAD']);
  const ds = run(['-Lines', '-ClassConfig', dcfg, '-Repo', d, '-Project', 'dng', '-At', dsha, '-Days', '14', '-Json']);
  assert.equal(ds.code, 0, ds.out);
  const DS = JSON.parse(ds.out).projects[0];
  assert.equal(DS.ref_sha, dsha); assert.equal(DS.ref_name, dsha);
  assert.deepEqual({ ...DS.lines }, { ...D.lines }); assert.deepEqual({ ...DS.bytes }, { ...D.bytes });

  // -Repo with no matching class entry and no -Project refuses (the classifier is never guessed); a non-repo refuses too
  const norepo = run(['-Lines', '-ClassConfig', dcfg, '-Repo', d]);
  assert.equal(norepo.code, 4, norepo.out); assert.match(norepo.out, /no class entry/);
  assert.equal(run(['-Lines', '-ClassConfig', dcfg, '-Repo', join(root, 'nope'), '-Project', 'dng']).code, 4);
  // -Repo auto-matches the entry whose root IS that repo
  const selfCfg = join(root, 'self.json');
  writeFileSync(selfCfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'self', root: d, ref: 'master', classes: dngEntry.classes } ] }));
  const self = run(['-Lines', '-ClassConfig', selfCfg, '-Repo', d, '-Json']);
  assert.equal(self.code, 0, self.out); assert.equal(JSON.parse(self.out).projects[0].project, 'self');
  // classic mode takes -Repo as -Root, -Days as the window, and -Since only with an explicit offset
  const cr = run(['-Repo', d, '-ProductPath', 'DngAutoProcessor.Core/', '-Days', '14', '-AsJson']);
  assert.equal(cr.code, 0, cr.out); assert.equal(JSON.parse(cr.out).product_commits_in_window, 1);
  assert.equal(run(['-Repo', d, '-ProductPath', 'DngAutoProcessor.Core/', '-Since', '2026-01-01T00:00:00']).code, 4);
  const cs = run(['-Repo', d, '-ProductPath', 'DngAutoProcessor.Core/', '-Since', since, '-AsJson']);   // a valid explicit -Since must be honoured
  assert.equal(cs.code, 0, cs.out); assert.equal(JSON.parse(cs.out).product_commits_in_window, 1);
  // ---- reproducibility: -At pins the commit, -Until pins the window end, -AsRows records the command ----
  const ud = newRepo('ud');
  put(ud, 'src/one.c', lines(8, 'd1')); commit(ud, 'in window', '2026-03-05T00:00:00Z');
  put(ud, 'docs/p.md', lines(4, 'd2')); commit(ud, 'in window 2', '2026-03-06T00:00:00Z');
  const pinned = git(ud, ['rev-parse', 'HEAD']);
  put(ud, 'src/late.c', lines(50, 'late')); commit(ud, 'after -Until', '2026-03-09T00:00:00Z');
  const ucfg = join(root, 'ud.json');
  writeFileSync(ucfg, JSON.stringify({ schema: 'fleet/product-throughput-classes/v1', projects: [
    { name: 'delta', root: ud, ref: 'master', classes }, { name: 'bravo', root: b, ref: 'HEAD', classes } ] }));
  const win = ['-Since', '2026-03-01T00:00:00Z', '-Until', '2026-03-08T00:00:00Z'];
  // -Until alone excludes the late commit even at the moving tip
  const u = run(['-Lines', '-ClassConfig', ucfg, '-Project', 'delta', ...win, '-AsRows']);
  assert.equal(u.code, 0, u.out);
  const ur = JSON.parse(u.out.trim());
  assert.deepEqual([ur.lines.product, ur.lines['coordination-paperwork'], ur.commits_counted], [8, 4, 2]);
  assert.equal(ur.until_utc, '2026-03-08T00:00:00Z'); assert.equal(ur.window_days, 7);
  assert.match(ur.classifier_sha256, /^[0-9a-f]{64}$/);
  // the recorded command pins -At to the walked sha, so the tip moving after the run changes nothing
  assert.ok(ur.command.includes(`-Project delta -At ${ur.ref_sha} -Since 2026-03-01T00:00:00Z -Until 2026-03-08T00:00:00Z`), ur.command);
  put(ud, 'src/later.c', lines(9, 'x')); commit(ud, 'backdated into the window on the tip', '2026-03-07T00:00:00Z');
  const args = ur.command.split(' ').slice(ur.command.split(' ').indexOf('-Lines'));
  const again = run([...args, '-ClassConfig', ucfg]);
  assert.equal(again.code, 0, again.out);
  const ar = JSON.parse(again.out.trim());
  assert.deepEqual(ar.lines, ur.lines); assert.equal(ar.ref_sha, ur.ref_sha); assert.equal(ar.command, ur.command);
  // the moved tip, unpinned, does differ: the pin is what made the row reproducible
  assert.equal(JSON.parse(run(['-Lines', '-ClassConfig', ucfg, '-Project', 'delta', ...win, '-AsRows']).out.trim()).lines.product, 17);
  // -At by name=sha among several projects; the pinned sha is the earlier commit
  const multi = run(['-Lines', '-ClassConfig', ucfg, '-At', `delta=${pinned}`, ...win, '-AsRows', '-RunId', 'fixture-run']);
  assert.equal(multi.code, 0, multi.out);
  const mrows = multi.out.trim().split('\n').map((x) => JSON.parse(x));
  assert.equal(mrows.find((x) => x.project === 'delta').ref_sha, pinned);
  assert.ok(mrows.every((x) => x.run_id === 'fixture-run'));
  // fail closed: bare -At with two projects, unknown -At name, unresolvable sha, naive -Until, empty window
  assert.equal(run(['-Lines', '-ClassConfig', ucfg, '-At', pinned, ...win]).code, 4);
  assert.equal(run(['-Lines', '-ClassConfig', ucfg, '-At', `nope=${pinned}`, ...win]).code, 4);
  assert.equal(run(['-Lines', '-ClassConfig', ucfg, '-Project', 'delta', '-At', 'f'.repeat(40), ...win]).code, 4);
  assert.equal(run(['-Lines', '-ClassConfig', ucfg, '-Project', 'delta', '-Until', '2026-03-08T00:00:00']).code, 4);
  assert.equal(run(['-Lines', '-ClassConfig', ucfg, '-Project', 'delta', '-Since', '2026-03-08T00:00:00Z', '-Until', '2026-03-01T00:00:00Z']).code, 4);

  console.log('PASS Get-ProductThroughput.tests.mjs');
} finally {
  rmSync(root, { recursive: true, force: true });
}
