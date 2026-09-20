#!/usr/bin/env node
// jev-adoption-status.mjs: reads each fleet project's `JEV:` acknowledgement line and reports the
// fleet's Jev shadow-mode adoption state. Read-only: it writes nothing, calls no gateway, and
// exits non-zero only to say what is missing or malformed. Roster = the first column of the
// standard's §5 table (`specs/fleet-jev-shadow-mode.md`), never `tools/fleet-membership.mjs` (which
// over-counts topic docs) and never the kernel roster.
//
// Line grammar (one line, printable ASCII, no trailing whitespace, key=value pairs separated by
// single spaces; the last `JEV:` line on a project's surface is its current state; earlier ones are
// history; any line starting `JEV:` that does not match is malformed):
//   JEV: <STATE> standard=r<N>@<7-40 lowercase hex> qsv=<16 lowercase hex|NONE> log=<path|NONE> lines=<1-9 decimal digits> asOf=<YYYY-MM-DD> record=<lowercase project>:<path-or-sha>
// STATE: NONE | DISPOSITION-ADOPT | DISPOSITION-DISTINGUISH | DISPOSITION-HOLD | SHADOW-LIVE | ADVISORY
// Surface: `specs/<project>.md` when that file exists at the ref, else `RECEIPTS.md` (append-only;
// the record= project token is the lowercase spec stem and must equal the project). ADVISORY is reserved (no project may record
// it until the standard's §2.4 promotion has run); every state but NONE needs a record; SHADOW-LIVE
// also needs qsv, a log path and lines>=100 (the checker reads the declared fields; the tree-side
// conditions of R10.2 are the project's to keep true). Exit: 0 every rostered project has a well-formed line; 2 a project has no line;
// 3 a line is malformed or its state constraints fail; 4 the roster is unreadable or an argument is
// unknown or incomplete.
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const STATES = ['NONE', 'DISPOSITION-ADOPT', 'DISPOSITION-DISTINGUISH', 'DISPOSITION-HOLD', 'SHADOW-LIVE', 'ADVISORY'];
export const STANDARD_PATH = 'specs/fleet-jev-shadow-mode.md';
export const SHADOW_LIVE_MIN_LINES = 100;
const LINE = /^JEV: (\S+) standard=(r\d+@[0-9a-f]{7,40}) qsv=([0-9a-f]{16}|NONE) log=(\S+) lines=(\d{1,9}) asOf=(\d{4}-\d{2}-\d{2}) record=([a-z0-9_.-]+):(\S+)$/;
const ASCII = /^[\x20-\x7e]+$/; // printable ASCII only, no tabs, no trailing whitespace
const RECORD_PROJECT = /(?:^|\s)record=([a-z0-9_.-]+):\S*\s*$/; // attributes a malformed RECEIPTS line by its LAST field only (trailing whitespace tolerated: it is what made the line malformed)

export function readAt(bus, ref, path) {
  if (!ref) {
    const full = join(bus, path);
    return existsSync(full) ? readFileSync(full, 'utf8') : null;
  }
  try {
    // GIT_NO_LAZY_FETCH: a partial clone must not fetch (and write) objects on the checker's behalf
    return execFileSync('git', ['-C', bus, 'show', `${ref}:${path}`], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], env: { ...process.env, GIT_NO_LAZY_FETCH: '1' } });
  } catch { return null; }
}

// The roster: first column of the §5 table, in table order; the standard's own revision marker.
export function roster(standardText) {
  const lines = standardText.split(/\r?\n/);
  const start = lines.findIndex((l) => /^## 5\. Per-project instances/.test(l));
  if (start < 0) throw new Error('standard has no "## 5. Per-project instances" section');
  const names = [];
  for (let i = start + 1; i < lines.length && !/^## /.test(lines[i]); i++) {
    const m = /^\| ([^|]+?) \|/.exec(lines[i]);
    if (!m || m[1] === 'Project' || /^-+$/.test(m[1])) continue;
    names.push(m[1].trim());
  }
  const rev = /\*\*Status: `CANDIDATE (r\d+)`/.exec(standardText);
  if (names.length === 0 || !rev) throw new Error('standard §5 table or status marker not found');
  return { projects: names, revision: rev[1] };
}

export function parseLine(text) {
  const m = ASCII.test(text) ? LINE.exec(text) : null;
  if (!m) return { error: 'malformed' };
  const [, state, standard, qsv, log, lines, asOf, recordProject, record] = m;
  if (!STATES.includes(state)) return { error: `unknown state ${state}` };
  return { state, standard, qsv, log, lines: Number(lines), asOf, recordProject, record };
}

export function constraintErrors(parsed, project, revision) {
  const errs = [];
  if (parsed.recordProject !== project.toLowerCase()) errs.push(`record names ${parsed.recordProject}, surface is ${project.toLowerCase()}`);
  if (!parsed.standard.startsWith(`${revision}@`)) errs.push(`standard ${parsed.standard} is not the bus's ${revision}`);
  if (parsed.state === 'ADVISORY') errs.push('ADVISORY is reserved until the standard\'s §2.4 promotion has run');
  if (parsed.state === 'SHADOW-LIVE') {
    if (parsed.qsv === 'NONE') errs.push('SHADOW-LIVE needs a pinned qsv');
    if (parsed.log === 'NONE') errs.push('SHADOW-LIVE needs a log path');
    if (parsed.lines < SHADOW_LIVE_MIN_LINES) errs.push(`SHADOW-LIVE needs lines>=${SHADOW_LIVE_MIN_LINES}, has ${parsed.lines}`);
  }
  if (parsed.state !== 'NONE' && parsed.record === 'NONE') errs.push(`${parsed.state} needs a record`);
  return errs;
}

export function projectStatus(bus, ref, project, revision) {
  const spec = `specs/${project.toLowerCase()}.md`;
  let surface = spec;
  let text = readAt(bus, ref, spec);
  if (text === null) { surface = 'RECEIPTS.md'; text = readAt(bus, ref, surface); }
  if (text === null) return { project, surface: null, state: 'NONE', found: 0, errors: [] };
  const hits = [];
  text.split(/\r?\n/).forEach((l, i) => {
    if (!l.startsWith('JEV:')) return;
    const p = parseLine(l);
    if (surface === 'RECEIPTS.md') {
      // a shared surface: a line belongs to the project its record= names; a malformed line that names
      // no project belongs to nobody and cannot displace another project's current line
      const who = p.error ? RECORD_PROJECT.exec(l)?.[1] : p.recordProject;
      if (who !== project.toLowerCase()) return;
    }
    hits.push({ lineNo: i + 1, raw: l, parsed: p });
  });
  if (hits.length === 0) return { project, surface, state: 'NONE', found: 0, errors: [] };
  const last = hits[hits.length - 1];
  if (last.parsed.error) return { project, surface, lineNo: last.lineNo, state: 'NONE', found: hits.length, errors: [last.parsed.error] };
  return { project, surface, lineNo: last.lineNo, found: hits.length, ...last.parsed, errors: constraintErrors(last.parsed, project, revision) };
}

export function fleetStatus(bus, ref) {
  const standard = readAt(bus, ref, STANDARD_PATH);
  if (standard === null) throw new Error(`${STANDARD_PATH} not found${ref ? ` at ${ref}` : ''}`);
  const { projects, revision } = roster(standard);
  const rows = projects.map((p) => projectStatus(bus, ref, p, revision));
  const missing = rows.filter((r) => r.found === 0).length;
  const bad = rows.filter((r) => r.errors.length > 0).length;
  const exit = bad ? 3 : missing ? 2 : 0;
  return { revision, ref: ref || null, rows, missing, bad, exit };
}

export function table(status) {
  const out = ['| Project | State | standard | qsv | lines | asOf | record | surface | errors |', '|---|---|---|---|---|---|---|---|---|'];
  for (const r of status.rows) {
    out.push(`| ${r.project} | ${r.state} | ${r.standard ?? ''} | ${r.qsv ?? ''} | ${r.lines ?? ''} | ${r.asOf ?? ''} | ${r.record ?? ''} | ${r.surface ?? ''}${r.lineNo ? `:${r.lineNo}` : ''} | ${r.errors.join('; ')} |`);
  }
  return out.join('\n');
}

function main(argv) {
  let bus = process.cwd(); let ref = null; let json = false;
  for (let i = 0; i < argv.length; i++) {
    const value = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : null; // absent, empty or a flag: no value
    if (argv[i] === '--bus' && value !== null) bus = argv[++i];
    else if (argv[i] === '--ref' && value !== null) ref = argv[++i];
    else if (argv[i] === '--json') json = true;
    else { process.stderr.write(`unknown argument ${argv[i]}\n`); return 4; }
  }
  let status;
  try { status = fleetStatus(bus, ref); }
  catch (err) { process.stderr.write(`${err.message}\n`); return 4; }
  process.stdout.write((json ? JSON.stringify(status, null, 2) : table(status)) + '\n');
  return status.exit;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) process.exit(main(process.argv.slice(2)));
