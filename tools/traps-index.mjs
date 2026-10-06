#!/usr/bin/env node
// traps-index — R14 packet 3: the generated index of TRAPS.md (RULINGS.md R14.2).
//
// R14.2: "A tool generates an index of TRAPS.md: one row per entry with id, line range, project and
// date. The index is generated, never hand-edited; an entry the tool cannot attribute is listed as
// unknown, never dropped." This is that tool. It reads TRAPS.md and writes only TRAPS-INDEX.md, and
// only with --write. It never edits TRAPS.md.
//
// WHAT AN ENTRY IS (the parse is mechanical, so the rows are a pointer, never a judgement)
//   - Lines inside ``` or ~~~ fences are body text, never headings. A fence closes only on a line of
//     the opener's character, at least as long as the opener, with nothing after it (CommonMark).
//   - Consecutive "# ", "## " and "### " lines outside a fence form one heading run: a hard-wrapped
//     heading re-prefixed on each line is ONE run, not several entries. An entry starts at line 1 and
//     at every run that holds a "# " or "## " line, or that is a "###" run carrying a YYYY-MM-DD date
//     (the form the mlv-app, agent-bridge, conjugal and airmypc outboxes file in). An undated "###"
//     run is a subsection of the entry above it; "####" and deeper never start an entry.
//   - It runs to the line before the next entry starts, so rows partition the file: every line falls
//     in exactly one row, with no gap and no overlap.
//   - id is "T<first line>". The file is append-only and, after R14 packet 4, frozen, so an id never
//     moves; a board names one in "legacy-read-through: <id>" (R14.3) or "no-card: <id>" (R14.4).
//   - project is the first fleet member id (tools/fleet-membership.mjs) or alias named in the heading
//     run; failing that, the one named in the enclosing "# " filing heading (Cloudvore's filings hold
//     many "##" traps under one "# Draft ... Cloudvore" heading); failing that, "unknown".
//   - date is the first YYYY-MM-DD in the heading run, then in the enclosing "# " heading, then in the
//     first five lines of the entry; failing that, "unknown".
//
// THE FREEZE (R14 packet 4). When TRAPS.freeze.json exists, the index covers exactly the frozen
// prefix it names, and refuses (exit 2) if that prefix is no longer byte-identical. Appends after the
// prefix are not index rows: tools/traps-freeze-check.mjs lists them as UNCARDED-APPEND, owed by their
// writer. So once frozen, the index never changes and --check stays meaningful in CI.
//
// Usage
//   node tools/traps-index.mjs              print the index to stdout
//   node tools/traps-index.mjs --write      write TRAPS-INDEX.md
//   node tools/traps-index.mjs --check      exit 1 if the committed TRAPS-INDEX.md differs from a fresh run
//   --bus <path>   another bus checkout     --rev <ref>   read TRAPS.md, the freeze file and the roster
//                                                         from a git ref instead of the working tree
// With --check --rev <ref>, the index is generated from TRAPS.md at <ref> and compared with the
// WORKING-TREE TRAPS-INDEX.md. Until the freeze (packet 4), CI passes the commit that last wrote the
// index (git log -1 --format=%H -- TRAPS-INDEX.md), so an unrelated TRAPS.md append after it does not
// turn every run red, while a hand-edit or corruption of the index still does.
// The working tree is read with CRLF as LF (a Windows checkout with core.autocrlf), which is what git
// stores; --rev reads the stored bytes exactly.
// Exit: 0 ok; 1 --check found a difference; 2 tool or environment failure.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fleetMembers } from './fleet-membership.mjs';

export const INDEX_PATH = 'TRAPS-INDEX.md';
export const TRAPS_PATH = 'TRAPS.md';
export const FREEZE_PATH = 'TRAPS.freeze.json';
const EXIT_OK = 0, EXIT_DIFF = 1, EXIT_FAIL = 2;

// Names a heading uses for a member that are not its spec id. Each maps to a member id and applies
// only while that member exists. Keep this list short and literal: it is attribution, not inference.
export const PROJECT_ALIASES = {
  'adobe document cloud ingester': 'adobe-ingester',
  'adobe ingester': 'adobe-ingester',
  'adobe-document-cloud-ingester': 'adobe-ingester',
  adobe: 'adobe-ingester',
  'mlv app': 'mlv-app',
  'agent bridge': 'agent-bridge',
  'dng auto processor': 'dng-auto-processor',
};

export function gitBlobSha(buffer) {
  return createHash('sha1').update(`blob ${buffer.length}\0`).update(buffer).digest('hex');
}

export function git(repo, args, { allowFail = false, encoding = 'utf8' } = {}) {
  try {
    return execFileSync('git', ['-C', repo, ...args], {
      encoding, stdio: ['ignore', 'pipe', 'pipe'], timeout: 60000, maxBuffer: 256 * 1024 * 1024,
      env: { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_OPTIONAL_LOCKS: '0' },
    });
  } catch (err) {
    if (allowFail) return null;
    throw new Error(`git ${args.join(' ')} failed in ${repo}: ${(err.stderr || err.message).toString().trim()}`);
  }
}

// Read a bus file as a Buffer from the working tree (CRLF read as LF) or exactly from a git ref.
// Returns null when the file does not exist there.
export function readBusFile(bus, rel, rev = null) {
  if (rev) {
    const out = git(bus, ['cat-file', 'blob', `${rev}:${rel}`], { allowFail: true, encoding: 'buffer' });
    return out === null ? null : Buffer.from(out);
  }
  const p = join(bus, rel);
  if (!existsSync(p)) return null;
  return Buffer.from(readFileSync(p).toString('latin1').replace(/\r\n/g, '\n'), 'latin1');
}

// Fleet members from the top-level specs/*.md files, at a ref or in the working tree.
export function rosterAt(bus, rev = null) {
  let names;
  if (rev) {
    const out = git(bus, ['ls-tree', `${rev}:specs`]);
    names = out.split('\n').filter(Boolean).map((l) => l.split('\t')).filter(([meta]) => meta.split(' ')[1] === 'blob').map(([, n]) => n);
  } else {
    names = readdirSync(join(bus, 'specs'), { withFileTypes: true }).filter((e) => e.isFile()).map((e) => e.name);
  }
  return fleetMembers(names);
}

// The bus's attribution convention is a dated parenthetical, "(cloudvore, 2026-09-07, machine)". A
// member named in such a parenthetical wins; otherwise the earliest member named anywhere in the text.
export function attributeProject(text, members) {
  for (const m of String(text).matchAll(/\(([^()]*)\)/g)) {
    if (!firstDate(m[1])) continue;
    const hit = earliestMember(m[1], members);
    if (hit) return hit;
  }
  return earliestMember(text, members);
}

function earliestMember(text, members) {
  const lower = String(text).toLowerCase();
  const names = [...members.map((m) => [m, m]), ...Object.entries(PROJECT_ALIASES).filter(([, m]) => members.includes(m))];
  let best = null;
  for (const [name, member] of names) {
    const re = new RegExp(`(^|[^a-z0-9-])${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![a-z0-9-])`);
    const m = re.exec(lower);
    if (!m) continue;
    const at = m.index + m[1].length;
    if (!best || at < best.at || (at === best.at && name.length > best.len)) best = { at, len: name.length, member };
  }
  return best ? best.member : null;
}

function firstDate(text) {
  const m = /\b(20\d\d-[01]\d-[0-3]\d)\b/.exec(String(text));
  return m ? m[1] : null;
}

// Split LF text into lines; a final newline does not make an extra empty line.
export function splitLines(text) {
  const lines = String(text).split('\n');
  if (lines.length && lines[lines.length - 1] === '') lines.pop();
  return lines;
}

// Parse TRAPS.md text (LF) into entries partitioning lines 1..N.
// `lineOffset` numbers the lines (used to parse an appended region on its own).
export function parseTrapsEntries(text, members, { lineOffset = 0 } = {}) {
  const lines = splitLines(text);
  const isHeading = new Array(lines.length).fill(0);
  // CommonMark fences: the opener's character and length are remembered; a closer is the same
  // character, at least as many of it, and nothing after it but spaces. Any other fence-like line
  // inside a fence is body text.
  let fence = null;
  lines.forEach((l, i) => {
    const f = /^ {0,3}(`{3,}|~{3,})/.exec(l);
    if (fence) {
      if (f && f[1][0] === fence.ch && f[1].length >= fence.len && /^ {0,3}(`{3,}|~{3,})[ \t]*$/.test(l)) fence = null;
      return;
    }
    if (f) { fence = { ch: f[1][0], len: f[1].length }; return; }
    const h = /^(#{1,3}) /.exec(l);
    if (h) isHeading[i] = h[1].length;
  });
  // A run of consecutive heading lines starts an entry if it holds a "#"/"##" line, or if it is a
  // "###" run carrying a date (the form several outboxes file in). An undated "###" run is a
  // subsection of the entry above it, so it is body text.
  for (let i = 0; i < lines.length;) {
    if (!isHeading[i]) { i++; continue; }
    let j = i;
    while (j < lines.length && isHeading[j]) j++;
    const run = lines.slice(i, j);
    const opens = isHeading.slice(i, j).some((v) => v <= 2) || firstDate(run.join(' ')) !== null;
    if (!opens) for (let k = i; k < j; k++) isHeading[k] = 0;
    i = j;
  }
  const starts = [];
  for (let i = 0; i < lines.length; i++) {
    if (i === 0 || (isHeading[i] && !isHeading[i - 1])) starts.push(i);
  }
  const entries = [];
  let filing = null; // the enclosing "# " heading's attribution
  starts.forEach((s, k) => {
    const e = k + 1 < starts.length ? starts[k + 1] - 1 : lines.length - 1;
    let h = s;
    const headingLines = [];
    while (h <= e && isHeading[h]) headingLines.push(lines[h++]);
    const heading = headingLines.map((l) => l.replace(/^#{1,3} /, '').trim()).join(' ');
    const ownProject = attributeProject(heading, members);
    const ownDate = firstDate(heading);
    if (isHeading[s] === 1) {
      // Line 1 is the log's own title, not a filing; any later "# " heading opens a filing context.
      filing = (s + lineOffset === 0) ? null : { project: ownProject, date: ownDate };
    } else if (ownDate) {
      // A dated heading is a filing of its own; it closes the "# " filing above it.
      filing = null;
    }
    const inherit = !ownProject && !ownDate && filing;
    const project = ownProject || (inherit && filing.project) || 'unknown';
    const date = ownDate || (inherit && filing.date) || firstDate(lines.slice(s, Math.min(e + 1, s + 5)).join('\n')) || 'unknown';
    entries.push({ id: `T${s + 1 + lineOffset}`, start: s + 1 + lineOffset, end: e + 1 + lineOffset, project, date, heading });
  });
  return entries;
}

export function parseFreeze(buffer) {
  let f;
  try { f = JSON.parse(buffer.toString('utf8')); } catch { throw new Error(`${FREEZE_PATH} is not JSON`); }
  if (!f || f.schema !== 'traps-freeze.v1' || f.path !== TRAPS_PATH || !/^[0-9a-f]{40}$/.test(f.blob || '')
    || !Number.isInteger(f.bytes) || f.bytes < 1 || !Number.isInteger(f.lines) || f.lines < 1) {
    throw new Error(`${FREEZE_PATH} must be {"schema":"traps-freeze.v1","path":"TRAPS.md","blob":<40-hex>,"bytes":<int>,"lines":<int>}`);
  }
  return f;
}

// The frozen prefix of `traps` (a Buffer), or a reason it is not intact.
export function frozenPrefix(traps, freeze) {
  if (traps.length < freeze.bytes) return { ok: false, reason: `TRAPS.md is ${traps.length} bytes, shorter than the frozen ${freeze.bytes}` };
  const prefix = traps.subarray(0, freeze.bytes);
  const sha = gitBlobSha(prefix);
  if (sha !== freeze.blob) return { ok: false, reason: `the first ${freeze.bytes} bytes hash to ${sha}, not the frozen blob ${freeze.blob}` };
  return { ok: true, prefix };
}

function escapeCell(s) {
  const t = String(s).replace(/\s+/g, ' ').replace(/\|/g, '\\|');
  const chars = Array.from(t);
  return chars.length > 100 ? `${chars.slice(0, 99).join('')}…` : t;
}

// Build { entries, text } for the bus at `rev` (or the working tree).
export function buildIndex(bus, rev = null) {
  const traps = readBusFile(bus, TRAPS_PATH, rev);
  if (traps === null) throw new Error(`${TRAPS_PATH} not found${rev ? ` at ${rev}` : ''}`);
  const members = rosterAt(bus, rev);
  const freezeRaw = readBusFile(bus, FREEZE_PATH, rev);
  let source = traps, scope;
  if (freezeRaw !== null) {
    const freeze = parseFreeze(freezeRaw);
    const fp = frozenPrefix(traps, freeze);
    if (!fp.ok) throw new Error(`frozen prefix is not intact (${fp.reason}); run node tools/traps-freeze-check.mjs`);
    source = fp.prefix;
    scope = `the frozen prefix named by \`${FREEZE_PATH}\`: blob \`${freeze.blob}\`, ${freeze.lines} lines. Lines appended after it are not rows here; \`node tools/traps-freeze-check.mjs\` lists them as UNCARDED-APPEND.`;
  } else {
    scope = `the whole file: blob \`${gitBlobSha(traps)}\`. No freeze file exists yet, so every append changes this index.`;
  }
  const text = source.toString('utf8');
  const entries = parseTrapsEntries(text, members);
  const total = splitLines(text).length;
  const unknownProject = entries.filter((e) => e.project === 'unknown').length;
  const unknownDate = entries.filter((e) => e.date === 'unknown').length;
  const out = [
    '# TRAPS index (generated by tools/traps-index.mjs; never hand-edited)',
    '',
    `Indexes \`${TRAPS_PATH}\` (${total} lines), ${scope}`,
    `Rows: ${entries.length}. Project unknown: ${unknownProject}. Date unknown: ${unknownDate}.`,
    'Rows partition the lines: every line is in exactly one row. An unattributable entry is listed as',
    '`unknown`, never dropped. The `heading` column is the entry\'s own heading text, cut at 100',
    'characters; it is a pointer, not a summary, and this file carries no authority of its own.',
    'Regenerate with `node tools/traps-index.mjs --write`; verify with `node tools/traps-index.mjs --check`.',
    '',
    '| id | lines | project | date | heading |',
    '|---|---|---|---|---|',
    ...entries.map((e) => `| ${e.id} | ${e.start}-${e.end} | ${e.project} | ${e.date} | ${escapeCell(e.heading)} |`),
    '',
  ].join('\n');
  return { entries, text: out, members };
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`unexpected argument '${a}'`);
    out[a.slice(2)] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
  }
  return out;
}

function main(argv) {
  const args = parseArgs(argv);
  const bus = resolve(args.bus || join(dirname(fileURLToPath(import.meta.url)), '..'));
  if (!existsSync(join(bus, 'RULINGS.md'))) throw new Error(`${bus} does not look like the doctrine bus`);
  const rev = typeof args.rev === 'string' ? args.rev : null;
  const { entries, text } = buildIndex(bus, rev);
  if (args.check) {
    const committed = readBusFile(bus, INDEX_PATH); // always the working tree: the file under check
    if (committed === null) { console.log(`[traps-index] ${INDEX_PATH} is missing; run: node tools/traps-index.mjs --write`); return EXIT_DIFF; }
    if (committed.toString('utf8') !== text) {
      const a = splitLines(committed.toString('utf8')), b = splitLines(text);
      let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
      console.log(`[traps-index] ${INDEX_PATH} differs from a fresh generation at line ${i + 1} (committed ${a.length} lines, generated ${b.length}).`);
      console.log('[traps-index] it is generated, never hand-edited: run node tools/traps-index.mjs --write and commit the result.');
      return EXIT_DIFF;
    }
    console.log(`[traps-index] ${INDEX_PATH} is current: ${entries.length} rows.`);
    return EXIT_OK;
  }
  if (args.write) {
    if (rev) throw new Error('--write and --rev cannot be combined');
    writeFileSync(join(bus, INDEX_PATH), text);
    console.log(`[traps-index] wrote ${INDEX_PATH}: ${entries.length} rows.`);
    return EXIT_OK;
  }
  process.stdout.write(text);
  return EXIT_OK;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exitCode = main(process.argv.slice(2)); }
  catch (error) { console.error(`[traps-index] ${error.message}`); process.exitCode = EXIT_FAIL; }
}
