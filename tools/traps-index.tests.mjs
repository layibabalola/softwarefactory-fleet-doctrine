#!/usr/bin/env node
// R14 packet 3 fixtures for tools/traps-index.mjs. Runs the shipped module and CLI against temporary
// git repositories, then checks the live TRAPS.md partition and the committed TRAPS-INDEX.md.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { attributeProject, buildIndex, gitBlobSha, parseTrapsEntries, splitLines } from './traps-index.mjs';

const repo = fileURLToPath(new URL('..', import.meta.url));
const tool = fileURLToPath(new URL('./traps-index.mjs', import.meta.url));
const root = mkdtempSync(join(tmpdir(), 'traps-index-'));
const members = ['adobe-ingester', 'cloudvore', 'mlv-app'];
const cli = (args) => {
  try { return { status: 0, out: execFileSync(process.execPath, [tool, ...args], { encoding: 'utf8', timeout: 60000, stdio: ['ignore', 'pipe', 'pipe'] }) }; }
  catch (e) { return { status: e.status, out: `${e.stdout || ''}${e.stderr || ''}` }; }
};
const gitIn = (cwd, ...args) => execFileSync('git', ['-C', cwd, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
const assertPartition = (entries, total, label) => {
  assert.equal(entries[0].start, 1, `${label}: first row starts at line 1`);
  for (let i = 1; i < entries.length; i++) assert.equal(entries[i].start, entries[i - 1].end + 1, `${label}: no gap or overlap at ${entries[i].id}`);
  assert.equal(entries[entries.length - 1].end, total, `${label}: last row ends at the last line`);
  assert.equal(new Set(entries.map((e) => e.id)).size, entries.length, `${label}: ids unique`);
};
// The --check arguments for a bus checkout. Once TRAPS.freeze.json exists the index covers a frozen
// prefix and the plain check is exact. Before that, an uncommitted index (a local --write) is checked
// against the working tree; otherwise against TRAPS.md at the commit that last wrote TRAPS-INDEX.md, so
// a later TRAPS.md append (which still lands as today until packet 4) does not turn CI red. CI checks
// out full history (fetch-depth: 0) so that commit is reachable.
function liveCheckArgs(dir) {
  if (existsSync(join(dir, 'TRAPS.freeze.json'))) return ['--check'];
  if (gitIn(dir, 'status', '--porcelain', '--', 'TRAPS-INDEX.md')) return ['--check'];
  const rev = gitIn(dir, 'log', '-1', '--format=%H', '--', 'TRAPS-INDEX.md');
  return rev ? ['--check', '--rev', rev] : ['--check'];
}
let cases = 0;

const TRAPS = [
  '# Traps (append-only; date + machine + the test)', //  1
  '',                                                  //  2
  '- 2026-08-08 (fleet): a preamble bullet.',          //  3
  '',                                                  //  4
  '## Appended by MLV-App, 2026-08-09',                //  5
  '- a trap',                                          //  6
  '## A wrapped heading that names nobody until',      //  7
  '## its second line (cloudvore, 2026-09-01, XPS)',   //  8
  'body',                                              //  9
  '```',                                               // 10
  '## not a heading inside a fence (mlv-app, 2026-01-01)', // 11
  '```',                                               // 12
  '### a level-3 line never starts an entry',          // 13
  '',                                                  // 14
  '# Draft for the fleet doctrine bus -- Cloudvore, 2026-09-28: two traps', // 15
  '',                                                  // 16
  '## T1. A trap with no attribution of its own',      // 17
  'body',                                              // 18
  '## Adobe sign-in hangs (mlv-app, 2026-09-29, box)', // 19
  '## Nobody and no date here',                        // 20  (merges with 19: consecutive heading lines)
  '',                                                  // 21
  '# Another filing, unattributed',                    // 22
  '## A child of an unattributed filing',              // 23
  'no date anywhere',                                  // 24
  '### an undated subsection stays body',              // 25
  'text',                                              // 26
  '### mlv-app, 2026-10-05 — an outbox filing',        // 27
  'text',                                              // 28
  '# Draft -- Cloudvore, 2026-09-30',                  // 29
  '',                                                  // 30
  '## Dated foreign filing (Fleet Doctrine, 2026-09-30)', // 31
  'x',                                                 // 32
  '## Undated, after a dated filing closed the context', // 33
  'x',                                                 // 34
].join('\n') + '\n';

try {
  // The parse: partition, merged runs, fences, filing context, parenthetical attribution, unknowns.
  const entries = parseTrapsEntries(TRAPS, members);
  assertPartition(entries, 34, 'fixture'); cases++;
  assert.deepEqual(entries.map((e) => [e.id, e.start, e.end, e.project, e.date]), [
    ['T1', 1, 4, 'unknown', '2026-08-08'],
    ['T5', 5, 6, 'mlv-app', '2026-08-09'],
    ['T7', 7, 14, 'cloudvore', '2026-09-01'],
    ['T15', 15, 16, 'cloudvore', '2026-09-28'],
    ['T17', 17, 18, 'cloudvore', '2026-09-28'],
    ['T19', 19, 21, 'mlv-app', '2026-09-29'],
    ['T22', 22, 26, 'unknown', 'unknown'],
    ['T27', 27, 28, 'mlv-app', '2026-10-05'],
    ['T29', 29, 30, 'cloudvore', '2026-09-30'],
    ['T31', 31, 32, 'unknown', '2026-09-30'],
    ['T33', 33, 34, 'unknown', 'unknown'],
  ]); cases++;
  // Attribution reads a dated PARENTHETICAL, not any paren-free run of text that carries a date.
  assert.equal(attributeProject('2026-10-06 mlv-app relay of a trap (cloudvore, 2026-10-06, box)', members), 'cloudvore'); cases++;
  assert.equal(attributeProject('Adobe failure 2026-10-05 (mlv-app, 2026-10-06, box)', ['adobe-ingester', 'mlv-app']), 'mlv-app'); cases++;
  // A fence closes only on the opener's character at the opener's length or longer (CommonMark): a
  // 3-backtick line inside a 4-backtick fence is body, so the "## Fake" line after it is not an entry.
  const fenced = ['# Title', '', '## Real (cloudvore, 2026-10-01, box)', '````', '```', '## Fake (adobe-ingester, 2026-10-06, box)', '```', '````', 'after',
    '~~~~', '~~~ not a closer', '## Fake two (adobe-ingester, 2026-10-06, box)', '~~~~~', '## After the fence (mlv-app, 2026-10-02, box)', 'x'].join('\n') + '\n';
  const fe = parseTrapsEntries(fenced, members);
  assertPartition(fe, 15, 'fences');
  assert.deepEqual(fe.map((e) => [e.id, e.project]), [['T1', 'unknown'], ['T3', 'cloudvore'], ['T14', 'mlv-app']]); cases++;
  // The live log is partitioned too: every line in exactly one row.
  const live = buildIndex(repo);
  const liveLines = splitLines(readFileSync(join(repo, 'TRAPS.md'), 'utf8').replace(/\r\n/g, '\n')).length;
  assertPartition(live.entries, liveLines, 'live TRAPS.md'); cases++;
  assert.ok(live.entries.every((e) => e.project && e.date), 'every live row has a project and a date (or unknown)'); cases++;

  // The CLI against a temporary bus repository.
  const bus = join(root, 'bus');
  mkdirSync(join(bus, 'specs'), { recursive: true });
  writeFileSync(join(bus, 'RULINGS.md'), 'rulings\n');
  for (const m of members) writeFileSync(join(bus, 'specs', `${m}.md`), `# ${m}\n`);
  writeFileSync(join(bus, 'TRAPS.md'), TRAPS);
  gitIn(bus, 'init', '-q'); gitIn(bus, 'config', 'core.autocrlf', 'false');
  gitIn(bus, 'add', '.'); gitIn(bus, '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-qm', 'seed');
  let a = cli(['--bus', bus]); let b = cli(['--bus', bus]);
  assert.equal(a.status, 0); assert.equal(a.out, b.out, 'two runs give identical bytes'); cases++;
  assert.match(a.out, /Rows: 11\. Project unknown: 4\. Date unknown: 2\./);
  assert.match(a.out, /^\| T22 \| 22-26 \| unknown \| unknown \| Another filing, unattributed A child of an unattributed filing \|$/m, 'unknown is listed, never dropped');
  assert.match(a.out, new RegExp(`blob \`${gitBlobSha(Buffer.from(TRAPS))}\``), 'names the blob it indexed'); cases++;
  let c = cli(['--bus', bus, '--check']); assert.equal(c.status, 1); assert.match(c.out, /is missing/); cases++;
  c = cli(['--bus', bus, '--write']); assert.equal(c.status, 0); assert.equal(readFileSync(join(bus, 'TRAPS-INDEX.md'), 'utf8'), a.out); cases++;
  c = cli(['--bus', bus, '--check']); assert.equal(c.status, 0, c.out); cases++;
  // Deleting one index row turns the check red.
  writeFileSync(join(bus, 'TRAPS-INDEX.md'), a.out.replace(/^\| T17 .*\n/m, ''));
  c = cli(['--bus', bus, '--check']); assert.equal(c.status, 1); assert.match(c.out, /differs from a fresh generation/); cases++;
  // A CRLF working tree reads as the LF bytes git stores.
  writeFileSync(join(bus, 'TRAPS-INDEX.md'), a.out.replace(/\n/g, '\r\n'));
  writeFileSync(join(bus, 'TRAPS.md'), TRAPS.replace(/\n/g, '\r\n'));
  c = cli(['--bus', bus, '--check']); assert.equal(c.status, 0, c.out); cases++;
  // An append changes the unfrozen index; --rev reads the committed bytes, not the working tree.
  writeFileSync(join(bus, 'TRAPS.md'), TRAPS + '## New (adobe, 2026-10-06)\nx\n');
  c = cli(['--bus', bus, '--check']); assert.equal(c.status, 1); cases++;
  writeFileSync(join(bus, 'TRAPS-INDEX.md'), a.out); // committed as git stores it: LF
  gitIn(bus, 'add', 'TRAPS-INDEX.md');
  gitIn(bus, '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-qm', 'index');
  c = cli(['--bus', bus, '--check', '--rev', 'HEAD']); assert.equal(c.status, 0, c.out); cases++;
  assert.match(cli(['--bus', bus]).out, /^\| T35 \| 35-36 \| adobe-ingester \| 2026-10-06 \| New \(adobe, 2026-10-06\) \|$/m, 'an alias attributes'); cases++;

  // With a freeze file, the index covers exactly the frozen prefix and ignores appends.
  const frozen = Buffer.from(TRAPS);
  writeFileSync(join(bus, 'TRAPS.freeze.json'), JSON.stringify({ schema: 'traps-freeze.v1', path: 'TRAPS.md', blob: gitBlobSha(frozen), bytes: frozen.length, lines: 34 }) + '\n');
  a = cli(['--bus', bus]); assert.equal(a.status, 0, a.out);
  assert.match(a.out, /the frozen prefix named by `TRAPS\.freeze\.json`/); assert.doesNotMatch(a.out, /\| T35 \|/); assert.match(a.out, /Rows: 11\./); cases++;
  // A rewritten frozen prefix is refused, never indexed.
  writeFileSync(join(bus, 'TRAPS.md'), TRAPS.replace('a preamble bullet', 'a rewritten bullet'));
  c = cli(['--bus', bus]); assert.equal(c.status, 2); assert.match(c.out, /frozen prefix is not intact/); cases++;
  writeFileSync(join(bus, 'TRAPS.freeze.json'), '{"schema":"wrong"}');
  c = cli(['--bus', bus]); assert.equal(c.status, 2); assert.match(c.out, /must be \{"schema":"traps-freeze.v1"/); cases++;
  c = cli(['--bus', bus, '--write', '--rev', 'HEAD']); assert.equal(c.status, 2); cases++;

  // Before the freeze, CI checks the index against TRAPS.md at the commit that last wrote the index, so
  // an unrelated append after it does not turn every run red; a hand-edit of the index still does.
  const rb = join(root, 'revbus');
  mkdirSync(join(rb, 'specs'), { recursive: true });
  writeFileSync(join(rb, 'RULINGS.md'), 'rulings\n');
  for (const m of members) writeFileSync(join(rb, 'specs', `${m}.md`), `# ${m}\n`);
  writeFileSync(join(rb, 'TRAPS.md'), TRAPS);
  gitIn(rb, 'init', '-q'); gitIn(rb, 'config', 'core.autocrlf', 'false');
  assert.equal(cli(['--bus', rb, '--write']).status, 0);
  const commitAll = (msg) => { gitIn(rb, 'add', '.'); gitIn(rb, '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-qm', msg); };
  commitAll('index');
  writeFileSync(join(rb, 'TRAPS.md'), TRAPS + '## Unrelated append (mlv-app, 2026-10-07, box)\nx\n');
  commitAll('append after the index');
  assert.deepEqual(liveCheckArgs(rb).slice(0, 2), ['--check', '--rev']);
  assert.equal(liveCheckArgs(rb)[2], gitIn(rb, 'rev-parse', 'HEAD~1'), 'the rev is the commit that last wrote the index');
  c = cli(['--bus', rb, ...liveCheckArgs(rb)]); assert.equal(c.status, 0, c.out); cases++;
  c = cli(['--bus', rb, '--check']); assert.equal(c.status, 1, 'the plain check sees the append'); cases++;
  const good = readFileSync(join(rb, 'TRAPS-INDEX.md'), 'utf8');
  writeFileSync(join(rb, 'TRAPS-INDEX.md'), good.replace('| mlv-app | 2026-08-09 |', '| cloudvore | 2026-08-09 |'));
  c = cli(['--bus', rb, '--check', '--rev', gitIn(rb, 'rev-parse', 'HEAD~1')]); assert.equal(c.status, 1, 'a working-tree hand-edit is caught'); cases++;
  commitAll('hand-edit the index');
  c = cli(['--bus', rb, ...liveCheckArgs(rb)]); assert.equal(c.status, 1, 'a committed hand-edit is caught'); assert.match(c.out, /differs from a fresh generation/); cases++;

  // This repository's committed index is current (against the TRAPS.md it was generated from).
  c = cli(liveCheckArgs(repo)); assert.equal(c.status, 0, `${liveCheckArgs(repo).join(' ')}: ${c.out}`); cases++;
  console.log(`traps-index fixtures: ${cases} cases passed (live TRAPS.md: ${live.entries.length} rows over ${liveLines} lines, ${live.entries.filter((e) => e.project === 'unknown').length} unknown project)`);
} finally {
  rmSync(root, { recursive: true, force: true });
}
