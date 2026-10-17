#!/usr/bin/env node
// tool-census — count hand-copied shared factory tools that have drifted apart, and hooks that run twice.
//
// THE RULE (owner defect D1, 2026-10-11; this header is the whole doc)
//   1. A shared tool runs from ONE place: this bus clone (like tools/doctrine-sync.mjs) or ~/.claude/hooks.
//   2. Project copies are deleted, and so is their .claude/settings.json registration when the user
//      settings already wire the shared one (otherwise the hook runs twice per event).
//   3. A copy that MUST exist (a project-specific CONFIG block) is checked by the hash of its shared
//      section only — the text below its 'sharedSectionMarker' line (e.g. END CONFIG).
//   4. The census count may only FALL. --check fails when it rose; --update-baseline refuses to raise.
//   5. A ratchet forbids worse but never requires better, so the baseline may carry a DEADLINE schedule,
//      "schedule": [{"by":"YYYY-MM-DD","max":N}, ...]. From each 'by' date on (calendar date, inclusive)
//      --check also fails when the count exceeds the max of the latest date already reached, naming the
//      families still over (owner D1-D3 adjudication 2026-10-16). It caps DUPLICATE COPIES, a defect
//      count, never a lane or product target (metrics law 1). No schedule = rule 4 alone.
//   6. A count that could not see the fleet is UNMEASURED: never ok, never failed. --check exits 3 when a
//      root the baseline measured (its 'roots' list) is absent here or, for a baseline without that list,
//      when no project or user root is present at all (a CI runner that cannot see the sibling clones).
//   7. VIEWS. A count is only comparable over a fixed (roots x families) set, and the fleet spans boxes
//      that see different clones. The top-level baseline is the PRIMARY view; 'views' adds more:
//      [{name, roots, families, total}]. --check and --update-baseline judge every view whose roots are
//      all visible here and name the rest UNMEASURED; exit 3 only when NO view is measurable. The view
//      'bus' (roots ["bus"]) is always measurable, so CI refuses any duplicate added on the bus itself.
//      --add-view <name> [--roots a,b] seeds a NEW view at today's count (it loosens nothing).
//   8. NEVER RAISED SILENTLY. --check-ratchet <base-ref> compares the baseline file with its copy at
//      the base revision. Any loosening of a view that existed there (removed; total raised; a root or
//      family dropped; a schedule max raised or a date moved later) exits 1 unless the same change adds
//      an entry to metrics/tool-census-rulings.json: {view, change, from?, to?, ruling, date}, change one
//      of view-removed | total-raised (with from/to) | roots-removed | families-removed |
//      schedule-loosened, ruling citing the owner ruling. CI runs it against the push/PR base.
//   9. FORWARDERS. A consumer may keep a thin file at a legacy path that hooks or settings name, which only
//      runs the PINNED canonical: `factory-pins/pin-runner.py run <tool>`. Such a file is a FORWARDER, reported
//      apart and never counted as a version, only when the config has a 'forwarders' block and ALL hold:
//        a. it sits in a non-bus root, is a .py file and is at most forwarders.maxBytes bytes (CRLF read as LF);
//        b. its Python AST has the forwarder SHAPE, tools/tool-census-forwarder.py (stdlib, parses, never
//           executes; its header is the rule): no file I/O, no imports beyond os/sys/subprocess/pathlib, calls
//           only from fixed allowlists, and every subprocess.run is either the vendored runner with
//           `run <tool> --` for THIS family's tool (family 'pinTool', default the family name) or a constant
//           `git rev-parse` query; any list naming another tool fails it;
//        c. the root's factory-pins/factory-pins.json pins that tool: a 40-hex blob, a path whose basename is a
//           family name (and equals the family's 'canonical' when it has one), and that blob is a release on the
//           bus history of that path; the bus root must be visible, else nothing is verified;
//        d. the root's vendored factory-pins/pin-runner.py is itself a release of the bus runner.
//      A file failing any check is a version as before, labelled with the reason. No python = no forwarders.
//   Measured 2026-10-11: session-checkpoint.py in 4 versions, wired by 3 projects AND the user settings.
//
// What it counts
//   count = sum over families of (distinct versions - 1) + double registrations.
//   A version is the sha256 of the file (CRLF read as LF), or of its shared section when the family
//   names a marker; a copy lacking the marker hashes whole and is flagged. The marker is a DELIMITER
//   LINE: after an optional comment token (#, //, --, ;) and fill (= - # * ~ _), the line holds the
//   marker and nothing else, e.g. '# ===== END CONFIG ====='; a prose mention ("below this line to
//   END CONFIG is repo-specific") is not one. A family may name its 'canonical' bus path (e.g.
//   tools/factory/check-doc-size.py): that config-by-data implementation has no CONFIG block, so it
//   hashes whole, is labelled CANONICAL and is never flagged; the copies converge on it, so it is
//   still one version among the family's distinct versions. A double registration is a
//   (project, family) pair where the project's .claude/settings.json and the user settings both wire
//   the family on at least one common hook event.
//   Copies are found with `git ls-files --cached --others --exclude-standard` in a git root (tracked
//   and untracked-not-ignored), or a directory walk minus the config's excludeDirs otherwise.
//
// Usage
//   node tools/tool-census.mjs                       human report
//   node tools/tool-census.mjs --json                machine report
//   node tools/tool-census.mjs --check               exit 1 if the count rose above the baseline or is
//                                                    over the schedule's current max; 3 if UNMEASURED
//   node tools/tool-census.mjs --update-baseline     lower every measured view that fell; refuses a rise
//   node tools/tool-census.mjs --add-view <name> [--roots a,b]   seed a new view (rule 7)
//   node tools/tool-census.mjs --check-ratchet <ref> [--repo <dir>] [--rulings <json>]   rule 8
//   overrides: --config <json> --baseline <json> --root <dir for relative paths> --home <dir for '~'>
//              --today YYYY-MM-DD (the date the schedule is read at; default the local calendar date)
//   '@bus' in the config is this script's own repository.
// Exit: 0 ok; 1 the count rose or is over its deadline (or a refused raise); 2 tool or environment
//       failure (including a malformed schedule); 3 UNMEASURED (the fleet roots are not visible here).
// It reads the fleet and writes only the baseline file, only on --update-baseline/--add-view (law 1, law 2).

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const EXIT_OK = 0, EXIT_ACTION = 1, EXIT_FAIL = 2, EXIT_UNMEASURED = 3;
const BUS = resolve(dirname(fileURLToPath(import.meta.url)), '..');

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) out[a.slice(2)] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
    else out._.push(a);
  }
  return out;
}

const globRe = (g) => new RegExp('^' + g.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '[^/\\\\]*').replace(/\?/g, '.') + '$', 'i');
const baseName = (p) => p.split(/[\\/]/).pop();

function expand(p, { root, home }) {
  if (p === '@bus') return BUS;
  if (p === '~' || p.startsWith('~/')) return resolve(home, p.slice(2));
  return resolve(root, p);
}

// scan (optional): only these subdirectories of a root are looked in.
function listFiles(dir, excludeDirs, scan = null) {
  const inScan = (f) => !scan || scan.some((s) => f === s || f.startsWith(`${s}/`));
  if (existsSync(join(dir, '.git'))) {
    try {
      const out = execFileSync('git', ['-C', dir, 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 60000, maxBuffer: 256 * 1024 * 1024,
        env: { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_OPTIONAL_LOCKS: '0' },
      });
      return out.split('\0').filter(Boolean).filter((f) => !f.split('/').some((s) => excludeDirs.has(s)) && inScan(f) && existsSync(join(dir, f)));
    } catch { /* fall through to a walk */ }
  }
  const files = [];
  const walk = (d, rel) => {
    let entries; try { entries = readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      const r = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) { if (!excludeDirs.has(e.name)) walk(join(d, e.name), r); }
      else if (e.isFile()) files.push(r);
    }
  };
  if (scan) for (const s of scan) walk(join(dir, s), s); else walk(dir, '');
  return files;
}

// A marker delimiter line: optional comment token, fill, the marker, fill; nothing else.
export function markerLineRe(marker) {
  const m = marker.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+');
  return new RegExp('^\\s*(?:#|//|--|;)?[\\s=#*~_-]*' + m + '[\\s=#*~_-]*$');
}

// The git blob id of a file read as LF (the id the bus stores; a CRLF checkout is the same release).
function blobIdLF(file) {
  const buf = Buffer.from(readFileSync(file).toString('latin1').replace(/\r\n/g, '\n'), 'latin1');
  return createHash('sha1').update(`blob ${buf.length}\0`).update(buf).digest('hex');
}

const gitOut = (dir, ...a) => {
  const env = { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_OPTIONAL_LOCKS: '0' };
  for (const k of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE']) delete env[k];
  return execFileSync('git', ['-C', dir, ...a], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 60000, env }).trim();
};

// The ref the bus's released history is read from: origin/master, else master (never whatever branch is checked
// out); an explicit override is for tests. null = this clone has no such ref (no history, no equivalence).
export function busRef(dir, override = null) {
  for (const c of override ? [override] : ['origin/master', 'master']) {
    try { gitOut(dir, 'rev-parse', '--verify', '--quiet', `${c}^{commit}`); return c; } catch { /* next */ }
  }
  return null;
}

// Every blob the bus ever committed at relPath on that ref (git log of the path, then rev-parse <sha>:<path>),
// derived at run time, never a hand-kept list. For DUPLICATE COUNTING only: any past release is one version with
// the canonical; it is not an approval (verify/status still flag a stale pin).
export function busHistoryBlobs(busDir, relPath, override = null) {
  const blobs = new Set();
  const ref = busRef(busDir, override);
  if (!ref) return { blobs, ref: null };
  let shas = [];
  try { shas = gitOut(busDir, 'log', '--format=%H', ref, '--', relPath).split('\n').filter(Boolean).slice(0, 2000); } catch { return { blobs, ref }; }
  for (const sha of shas) { try { blobs.add(gitOut(busDir, 'rev-parse', '--verify', '--quiet', `${sha}:${relPath}`)); } catch { /* deleted there */ } }
  return { blobs, ref };
}

// --- forwarders (rule 9) ---------------------------------------------------------------------------
const FORWARDER_CHECK = join(dirname(fileURLToPath(import.meta.url)), 'tool-census-forwarder.py');
let pythonExe;
function python() {
  if (pythonExe !== undefined) return pythonExe;
  pythonExe = null;
  for (const c of process.env.TOOL_CENSUS_PYTHON ? [process.env.TOOL_CENSUS_PYTHON] : ['python3', 'python']) {
    try { execFileSync(c, ['-I', '-c', 'import ast, json'], { stdio: 'ignore', timeout: 30000 }); pythonExe = c; break; } catch { /* next */ }
  }
  return pythonExe;
}

// The AST shape verdicts for [{path, tool}]: null = forwarder shape, else why not (fails closed).
export function forwarderShapes(items) {
  if (!items.length) return [];
  const py = python();
  if (!py) return items.map(() => 'python is unavailable here: the forwarder shape cannot be verified');
  try {
    const out = execFileSync(py, ['-I', FORWARDER_CHECK], { input: JSON.stringify(items), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], timeout: 60000 });
    const v = JSON.parse(out);
    if (!Array.isArray(v) || v.length !== items.length) throw new Error('verdict count mismatch');
    return v.map((x) => (x === null ? null : String(x)));
  } catch (e) { return items.map(() => `forwarder check failed: ${String(e.message || e).split('\n')[0]}`); }
}

const HEX40 = /^[0-9a-f]{40}$/;
const BAD_REL = /^[\\/]|^[A-Za-z]:|(^|[\\/])\.\.([\\/]|$)/;
// Rule 9c/9d: the consumer pins the tool to a real bus release, and its vendored runner is a bus release.
export function forwarderPin({ rootDir, tool, fam, bus, fwd, busRefOverride = null }) {
  if (!bus) return { why: 'no bus root is visible: the pin cannot be verified' };
  const pinsRel = fwd.pinsFile || 'factory-pins/factory-pins.json';
  let pins;
  try { pins = JSON.parse(readFileSync(join(rootDir, pinsRel), 'utf8').replace(/^﻿/, '')); } catch { return { why: `no readable ${pinsRel}` }; }
  const t = pins && pins.tools && typeof pins.tools === 'object' ? pins.tools[tool] : null;
  if (!t || typeof t !== 'object') return { why: `${pinsRel} does not pin '${tool}'` };
  if (typeof t.blob !== 'string' || !HEX40.test(t.blob)) return { why: `pin '${tool}' has no 40-hex blob` };
  if (typeof t.path !== 'string' || !t.path || BAD_REL.test(t.path)) return { why: `pin '${tool}' path is not a bus-relative path` };
  if (!(fam.names || []).map(globRe).some((r) => r.test(baseName(t.path)))) return { why: `pin '${tool}' path ${t.path} is not a ${fam.name} file` };
  if (fam.canonical && t.path !== fam.canonical) return { why: `pin '${tool}' path ${t.path} is not the family canonical ${fam.canonical}` };
  const hist = busHistoryBlobs(bus.dir, t.path, busRefOverride);
  if (!hist.blobs.has(t.blob)) return { why: `pinned blob ${t.blob.slice(0, 12)} is not a release of ${t.path} on the bus ${hist.ref || '(no history ref)'}` };
  const runnerRel = fwd.runner || 'factory-pins/pin-runner.py';
  const runner = join(rootDir, runnerRel);
  if (!existsSync(runner)) return { why: `no vendored ${runnerRel}` };
  const runnerCanon = fwd.runnerCanonical || 'tools/factory/pin-runner.py';
  const runnerBlob = blobIdLF(runner);
  if (!busHistoryBlobs(bus.dir, runnerCanon, busRefOverride).blobs.has(runnerBlob)) return { why: `vendored ${runnerRel} (blob ${runnerBlob.slice(0, 12)}) is not a release of ${runnerCanon}` };
  return { why: null, pin: { path: t.path, blob: t.blob } };
}

const isDir = (p) => { try { return statSync(p).isDirectory(); } catch { return false; } };

function versionOf(file, marker, canonical = false) {
  const text = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  let section = text, markerFound = null;
  if (marker && !canonical) {
    const lines = text.split('\n');
    const re = markerLineRe(marker);
    const i = lines.findIndex((l) => re.test(l));
    markerFound = i >= 0;
    if (i >= 0) section = lines.slice(i + 1).join('\n');
  }
  return { hash: createHash('sha256').update(section).digest('hex'), lines: text.split('\n').length - (text.endsWith('\n') ? 1 : 0), markerFound };
}

// Hook event -> set of script basenames its commands name.
function hookScripts(settingsPath) {
  if (!existsSync(settingsPath)) return null;
  const json = JSON.parse(readFileSync(settingsPath, 'utf8').replace(new RegExp('^' + String.fromCharCode(0xfeff)), ''));
  const out = new Map();
  for (const [event, groups] of Object.entries(json.hooks || {})) {
    if (!Array.isArray(groups)) continue;
    for (const g of groups) {
      if (!g || typeof g !== 'object') continue;
      // Schema: event -> [{ matcher?, hooks: [{ type, command }] }]. A bare { type, command } directly
      // under the event is counted too (it is what the file asks for) and flagged FLAT: it is not the
      // matcher-group schema and may never fire.
      const flat = typeof g.command === 'string';
      for (const h of (flat ? [g] : Array.isArray(g.hooks) ? g.hooks : [])) {
        if (!h || typeof h.command !== 'string') continue;
        for (const m of h.command.matchAll(/[\w.-]+\.(?:py|mjs|cjs|js|ps1|sh)\b/g)) {
          if (!out.has(event)) out.set(event, { names: new Set(), flat: false });
          out.get(event).names.add(m[0]);
          if (flat) out.get(event).flat = true;
        }
      }
    }
  }
  return out;
}

function familyEvents(scripts, fam) {
  const res = (fam.names || []).map(globRe);
  const events = [];
  for (const [event, { names, flat }] of scripts || []) if ([...names].some((n) => res.some((r) => r.test(n)))) events.push({ event, flat });
  return events;
}

export function census({ config, root, home, busRefOverride = null }) {
  const excludeDirs = new Set(config.excludeDirs || ['.git', 'node_modules', 'archive', '__pycache__', 'worktrees']);
  const roots = (config.roots || []).map((r) => ({ ...r, dir: expand(r.path, { root, home }) }));
  const userSettings = config.userSettings ? expand(config.userSettings, { root, home }) : null;
  const userScripts = userSettings ? hookScripts(userSettings) : null;
  // A root is MEASURED only if its directory exists and every "scan" subdirectory exists: a scan dir that is not
  // there (a moved workspace layout) is UNMEASURED, never a measured zero. (An existing but empty root stays
  // measured at 0: that is how a retired copy ratchets down, rule 7.)
  const fileCache = new Map();
  const absentWhy = new Map();
  for (const r of roots) {
    if (!isDir(r.dir)) { absentWhy.set(r.name, 'directory absent'); continue; }
    const gone = (r.scan || []).filter((s) => !isDir(join(r.dir, s)));
    if (gone.length) { absentWhy.set(r.name, `scan dir(s) missing: ${gone.join(', ')}`); continue; }
    const files = listFiles(r.dir, excludeDirs, r.scan || null);
    fileCache.set(r.name, files);
  }
  const absent = [...absentWhy.keys()];
  const families = [];
  const doubles = [];
  for (const fam of config.families || []) {
    const res = (fam.names || []).map(globRe);
    const copies = [];
    // releaseHistory: a family whose canonical bus file is RELEASED over time (the pin runner). Version identity is
    // the git blob id of the LF bytes, so identical bytes are one version wherever they sit. A vendored copy
    // (<vendoredDir>/<name>, default factory-pins) equal to ANY blob in the bus history of the canonical path is
    // aliased to the canonical's version; only an edited copy is divergent.
    const rel = !!(fam.releaseHistory && fam.canonical);
    const busRoot = rel ? roots.find((r) => r.kind === 'bus' && !absent.includes(r.name)) : null;
    const hist = busRoot ? busHistoryBlobs(busRoot.dir, fam.canonical, busRefOverride) : { blobs: new Set(), ref: null };
    const canonBlob = busRoot && existsSync(join(busRoot.dir, fam.canonical)) ? blobIdLF(join(busRoot.dir, fam.canonical)) : null;
    const vendoredDir = fam.vendoredDir || 'factory-pins';
    const fwd = config.forwarders && typeof config.forwarders === 'object' ? config.forwarders : null;
    const fwdBus = fwd ? roots.find((r) => r.kind === 'bus' && !absent.includes(r.name)) : null;
    const fwdMax = fwd && Number.isInteger(fwd.maxBytes) && fwd.maxBytes > 0 ? fwd.maxBytes : 4096;
    const tool = fam.pinTool || fam.name;
    const forwarders = [], candidates = [];
    for (const r of roots) {
      if (absent.includes(r.name)) continue;
      for (const f of fileCache.get(r.name)) {
        if (!res.some((re) => re.test(baseName(f)))) continue;
        const canonical = r.kind === 'bus' && !!fam.canonical && f === fam.canonical;
        const v = versionOf(join(r.dir, f), fam.sharedSectionMarker, canonical);
        let version = v.hash, extra = {};
        if (rel) {
          const blob = blobIdLF(join(r.dir, f));
          const release = canonical ? 'canonical' : (busRoot && r.kind !== 'bus' && f.split('/').slice(-2, -1)[0] === vendoredDir && hist.blobs.has(blob)) ? 'history' : null;
          version = `blob:${release && canonBlob ? canonBlob : blob}`;
          extra = { blob, ...(release ? { release } : {}) };
        }
        const copy = { root: r.name, path: f, ...v, version, ...extra, ...(canonical ? { canonical: true } : {}) };
        copies.push(copy);
        if (fwd && r.kind !== 'bus' && /\.py$/i.test(f)) {
          const text = readFileSync(join(r.dir, f), 'latin1').replace(/\r\n/g, '\n');
          const bytes = Buffer.byteLength(text, 'latin1');
          if (bytes <= fwdMax && text.includes('pin-runner')) candidates.push({ copy, r, abs: join(r.dir, f), bytes });
        }
      }
    }
    // Rule 9: a candidate that passes the shape AND the pin checks leaves the version count.
    const shapes = forwarderShapes(candidates.map((c) => ({ path: c.abs, tool })));
    candidates.forEach((c, i) => {
      let why = shapes[i], pin = null;
      if (!why) ({ why, pin } = forwarderPin({ rootDir: c.r.dir, tool, fam, bus: fwdBus, fwd, busRefOverride }));
      if (why) { c.copy.notForwarder = why; return; }
      copies.splice(copies.indexOf(c.copy), 1);
      forwarders.push({ root: c.copy.root, path: c.copy.path, bytes: c.bytes, tool, pinnedPath: pin.path, pinnedBlob: pin.blob });
    });
    const distinct = [...new Set(copies.map((c) => c.version))];
    families.push({ name: fam.name, marker: fam.sharedSectionMarker || null, copies, distinct: distinct.length, excess: Math.max(distinct.length - 1, 0), ...(rel ? { historyRef: hist.ref } : {}), forwarders });
    for (const r of roots) {
      if (r.kind === 'user' || absent.includes(r.name)) continue;
      const proj = familyEvents(hookScripts(join(r.dir, '.claude', 'settings.json')), fam);
      const user = familyEvents(userScripts, fam);
      const both = proj.filter((p) => user.some((u) => u.event === p.event));
      if (both.length) doubles.push({ family: fam.name, project: r.name, events: both.map((p) => p.event), projectFlat: both.some((p) => p.flat) });
    }
  }
  const total = families.reduce((s, f) => s + f.excess, 0) + doubles.length;
  const measuredRoots = roots.filter((r) => !absent.includes(r.name)).map((r) => r.name);
  const fleetRootsSeen = roots.filter((r) => r.kind !== 'bus' && !absent.includes(r.name)).length;
  return { total, families, doubleRegistrations: doubles, absentRoots: absent, absentWhy: Object.fromEntries(absentWhy), measuredRoots, fleetRootsSeen };
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

// Validates a baseline's optional schedule; returns [] when there is none, throws on a malformed one.
export function parseSchedule(baseline) {
  if (baseline.schedule === undefined) return [];
  if (!Array.isArray(baseline.schedule)) throw new Error('baseline schedule must be an array of {by, max}');
  return baseline.schedule.map((e, i) => {
    if (!e || typeof e.by !== 'string' || !DATE_RE.test(e.by) || Number.isNaN(Date.parse(e.by))) throw new Error(`schedule[${i}].by must be a YYYY-MM-DD date`);
    if (!Number.isInteger(e.max) || e.max < 0) throw new Error(`schedule[${i}].max must be a non-negative integer`);
    return { by: e.by, max: e.max };
  }).sort((a, b) => a.by.localeCompare(b.by));
}

// The entry in force on 'today' (the latest 'by' <= today), and the next one still ahead.
export function scheduleAt(schedule, today) {
  const passed = schedule.filter((e) => e.by <= today);
  return { current: passed.length ? passed[passed.length - 1] : null, next: schedule.find((e) => e.by > today) || null };
}

// Whether a count can be compared with the baseline at all (rule 6).
export function unmeasuredReason(rep, baseline) {
  if (Array.isArray(baseline.roots)) {
    const missing = baseline.roots.filter((r) => !rep.measuredRoots.includes(r));
    if (missing.length) return `root(s) the baseline measured are not visible here: ${missing.join(', ')}`;
    return null;
  }
  if (rep.fleetRootsSeen === 0) return 'no project or user root is visible here (the sibling clones are absent)';
  return null;
}

function localDate() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function over(rep) {
  return [
    ...rep.families.filter((f) => f.excess > 0).map((f) => `${f.name} (+${f.excess})`),
    ...rep.doubleRegistrations.map((d) => `${d.project}:${d.family} double registration`),
  ];
}

function human(rep) {
  const L = [];
  for (const f of rep.families) {
    L.push(`[tool-census] ${f.name}: ${f.copies.length} cop${f.copies.length === 1 ? 'y' : 'ies'}, ${f.distinct} distinct version(s)${f.marker ? ` (hashed below '${f.marker}')` : ''}`);
    for (const c of f.copies) L.push(`    ${c.hash.slice(0, 10)}  ${String(c.lines).padStart(5)} lines  ${c.root}: ${c.path}${c.release === 'history' ? '   RELEASE (equals a bus-history blob: counted as the canonical)' : c.canonical ? '   CANONICAL (hashed whole; copies converge on it)' : c.markerFound === false ? '   NO MARKER (hashed whole)' : ''}${c.notForwarder ? `   (not a forwarder: ${c.notForwarder})` : ''}`);
    for (const w of f.forwarders || []) L.push(`    FORWARDER   ${String(w.bytes).padStart(5)} bytes  ${w.root}: ${w.path}   runs pinned ${w.tool} = ${w.pinnedPath}@${w.pinnedBlob.slice(0, 12)}; not a version`);
  }
  for (const d of rep.doubleRegistrations) L.push(`[tool-census] DOUBLE REGISTRATION: ${d.family} wired by ${d.project} .claude/settings.json AND user settings on ${d.events.join(', ')}${d.projectFlat ? ' (project entry is FLAT, not the matcher-group schema: may never fire)' : ''}`);
  if (rep.absentRoots.length) L.push(`[tool-census] roots absent on this box (skipped): ${rep.absentRoots.map((n) => ((rep.absentWhy || {})[n] && rep.absentWhy[n] !== 'directory absent' ? `${n} [${rep.absentWhy[n]}]` : n)).join(', ')}`);
  const nf = rep.families.reduce((s, f) => s + (f.forwarders || []).length, 0);
  if (nf) L.push(`[tool-census] ${nf} pinned forwarder(s) reported apart, never counted as versions (rule 9)`);
  L.push(`[tool-census] count = ${rep.families.reduce((s, f) => s + f.excess, 0)} excess version(s) + ${rep.doubleRegistrations.length} double registration(s) = ${rep.total}`);
  return L.join('\n');
}

function baselineOf(rep, old) {
  return {
    ...(old || {}),
    schema: 'tool-census-baseline.v1',
    total: rep.total,
    ...(old && old.schedule !== undefined ? { schedule: old.schedule } : {}),
    roots: rep.measuredRoots,
    families: Object.fromEntries(rep.families.map((f) => [f.name, { copies: f.copies.length, distinct: f.distinct, ...((f.forwarders || []).length ? { forwarders: f.forwarders.map((w) => `${w.root}:${w.path}`) } : {}) }])),
    doubleRegistrations: rep.doubleRegistrations.map((d) => `${d.project}:${d.family}:${d.events.join('+')}`),
    measuredAt: new Date().toISOString(),
    rule: 'The count may only fall, and must be at or below the max of the latest schedule date reached. tools/tool-census.mjs --update-baseline refuses a rise and keeps the schedule. It grades the fleet tool layout, never a lane (metrics law 1).',
  };
}

// --- views (rule 7) --------------------------------------------------------------------------------
// One count over one fixed (roots x families) set. The top-level baseline is the PRIMARY view (its
// roots list and families map); 'views' adds more, e.g. the bus alone (always measurable, so CI
// enforces it) and each fleet box's own root set. A view is measured only where all its roots are.
export function viewsOf(baseline) {
  const primary = {
    name: 'primary', primary: true, total: baseline.total,
    roots: Array.isArray(baseline.roots) ? baseline.roots : null,
    families: baseline.families && typeof baseline.families === 'object' ? Object.keys(baseline.families) : null,
    schedule: baseline.schedule,
  };
  const extra = (baseline.views || []).map((v, i) => {
    if (!v || typeof v.name !== 'string' || !v.name || v.name === 'primary') throw new Error(`views[${i}].name must be a non-empty string other than 'primary'`);
    if (!Number.isInteger(v.total) || v.total < 0) throw new Error(`views[${i}].total must be a non-negative integer`);
    if (!Array.isArray(v.roots) || !v.roots.length) throw new Error(`views[${i}].roots must be a non-empty array`);
    if (!Array.isArray(v.families) || !v.families.length) throw new Error(`views[${i}].families must be a non-empty array`);
    return { ...v, primary: false };
  });
  const names = new Set();
  for (const v of extra) { if (names.has(v.name)) throw new Error(`duplicate view '${v.name}'`); names.add(v.name); }
  return [primary, ...extra];
}

export function restrict(config, view) {
  return {
    ...config,
    roots: view.roots ? (config.roots || []).filter((r) => view.roots.includes(r.name)) : config.roots,
    families: view.families ? (config.families || []).filter((f) => view.families.includes(f.name)) : config.families,
  };
}

function viewUnmeasured(rep, view) {
  if (view.roots) {
    const missing = view.roots.filter((r) => !rep.measuredRoots.includes(r));
    return missing.length ? `root(s) the view measured are not visible here: ${missing.join(', ')}` : null;
  }
  return rep.fleetRootsSeen === 0 ? 'no project or user root is visible here (the sibling clones are absent)' : null;
}

function measureViews(config, baseline, { root, home }) {
  return viewsOf(baseline).map((view) => {
    const rep = census({ config: restrict(config, view), root, home });
    return { view, rep, why: viewUnmeasured(rep, view) };
  });
}

// --- ratchet history (rule 8) ---------------------------------------------------------------------
// Compares the baseline at a base revision with the one now. Every LOOSENING of a view that existed at
// the base -- removed, total raised, a root or family dropped, a schedule max raised or a date moved
// later -- needs a NEW entry in the rulings file (metrics/tool-census-rulings.json) naming that view
// and citing the ruling. A lowering, a new view, or a tighter schedule needs nothing.
function maxAt(schedule, d) {
  const passed = schedule.filter((e) => e.by <= d);
  return passed.length ? passed[passed.length - 1].max : Infinity;
}

export function loosenings(base, head) {
  const out = [];
  const headViews = new Map(viewsOf(head).map((v) => [v.name, v]));
  for (const b of viewsOf(base)) {
    const h = headViews.get(b.name);
    if (!h) { out.push({ view: b.name, change: 'view-removed', detail: `view '${b.name}' removed` }); continue; }
    if (typeof h.total !== 'number' || h.total > b.total) out.push({ view: b.name, change: 'total-raised', from: b.total, to: h.total, detail: `total ${b.total} -> ${h.total}` });
    if (b.roots && (!h.roots || b.roots.some((r) => !h.roots.includes(r)))) out.push({ view: b.name, change: 'roots-removed', detail: `roots dropped: ${b.roots.filter((r) => !(h.roots || []).includes(r)).join(', ') || 'list removed'}` });
    if (b.families && (!h.families || b.families.some((f) => !h.families.includes(f)))) out.push({ view: b.name, change: 'families-removed', detail: `families dropped: ${b.families.filter((f) => !(h.families || []).includes(f)).join(', ') || 'list removed'}` });
    const bs = parseSchedule({ schedule: b.schedule }), hs = parseSchedule({ schedule: h.schedule });
    const loose = [...new Set([...bs, ...hs].map((e) => e.by))].sort().find((d) => maxAt(hs, d) > maxAt(bs, d));
    if (loose) out.push({ view: b.name, change: 'schedule-loosened', detail: `schedule allows ${maxAt(hs, loose)} on ${loose} where it allowed ${maxAt(bs, loose)}` });
  }
  return out;
}

export function unruled(found, baseRulings, headRulings) {
  const seen = new Set(((baseRulings && baseRulings.rulings) || []).map((r) => JSON.stringify(r)));
  const fresh = ((headRulings && headRulings.rulings) || []).filter((r) => !seen.has(JSON.stringify(r))
    && r && typeof r.ruling === 'string' && r.ruling.trim() && typeof r.date === 'string' && DATE_RE.test(r.date));
  return found.filter((l) => !fresh.some((r) => r.view === l.view && r.change === l.change
    && (l.change !== 'total-raised' || (r.from === l.from && r.to === l.to))));
}

function gitShowJson(repo, ref, rel) {
  try {
    const out = execFileSync('git', ['--no-optional-locks', '-C', repo, 'show', `${ref}:${rel}`], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 30000,
      env: { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_OPTIONAL_LOCKS: '0' },
    });
    return JSON.parse(out);
  } catch (err) {
    if (/does not exist|exists on disk, but not in|bad revision|invalid object name/i.test(String(err.stderr || err.message))) {
      // the path is absent at the base (a first baseline); an unknown REVISION is a tool failure
      execFileSync('git', ['--no-optional-locks', '-C', repo, 'rev-parse', '--verify', '--quiet', `${ref}^{commit}`], { stdio: 'ignore' });
      return null;
    }
    throw err;
  }
}

function readJsonIf(p) { return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : null; }

function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = resolve(args.root ? String(args.root) : process.cwd());
  const home = resolve(args.home ? String(args.home) : homedir());
  const configPath = resolve(args.config ? String(args.config) : join(BUS, 'tools', 'tool-census.config.json'));
  const baselinePath = resolve(args.baseline ? String(args.baseline) : join(BUS, 'metrics', 'tool-census-baseline.json'));
  const rulingsPath = resolve(args.rulings ? String(args.rulings) : join(dirname(baselinePath), 'tool-census-rulings.json'));
  const today = args.today ? String(args.today) : localDate();
  if (!DATE_RE.test(today)) { console.error(`[tool-census] --today must be YYYY-MM-DD, got '${today}'`); return EXIT_FAIL; }

  if (args['check-ratchet']) {
    const ref = String(args['check-ratchet']);
    const repo = resolve(args.repo ? String(args.repo) : BUS);
    const relOf = (p) => relative(repo, p).split(sep).join('/');
    const head = readJsonIf(baselinePath);
    if (!head) { console.error(`[tool-census] no baseline at ${baselinePath}`); return EXIT_FAIL; }
    const base = gitShowJson(repo, ref, relOf(baselinePath));
    if (!base) { console.error(`[tool-census] ratchet: no baseline at ${ref}; nothing to compare.`); return EXIT_OK; }
    const found = loosenings(base, head);
    const missing = unruled(found, gitShowJson(repo, ref, relOf(rulingsPath)), readJsonIf(rulingsPath));
    for (const l of found) console.error(`[tool-census] ratchet: view '${l.view}' ${l.detail}${missing.includes(l) ? '  UNRULED' : '  (ruled)'}`);
    if (missing.length) {
      console.error(`[tool-census] RATCHET REFUSED: ${missing.length} loosening(s) since ${ref} without a new entry in ${relOf(rulingsPath)} `
        + '({view, change, from?, to?, ruling, date}). The baseline only falls; raising it is an owner ruling, recorded in that file in the same change.');
      return EXIT_ACTION;
    }
    console.error(`[tool-census] ratchet ok since ${ref}: ${found.length ? `${found.length} loosening(s), each ruled` : 'nothing loosened'}.`);
    return EXIT_OK;
  }

  if (!existsSync(configPath)) { console.error(`[tool-census] config not found: ${configPath}`); return EXIT_FAIL; }
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  const rep = census({ config, root, home, busRefOverride: typeof args['bus-ref'] === 'string' ? args['bus-ref'] : null });

  if (args['add-view']) {
    const name = String(args['add-view']);
    const old = readJsonIf(baselinePath);
    if (!old) { console.error(`[tool-census] no baseline at ${baselinePath}; seed it first`); return EXIT_FAIL; }
    if (viewsOf(old).some((v) => v.name === name)) { console.error(`[tool-census] REFUSED: view '${name}' exists; a view is lowered by --update-baseline, never re-seeded`); return EXIT_ACTION; }
    const only = args.roots ? String(args.roots).split(',').map((s) => s.trim()).filter(Boolean) : rep.measuredRoots;
    const absent = only.filter((r) => !rep.measuredRoots.includes(r));
    if (absent.length) { console.error(`[tool-census] UNMEASURED: root(s) not visible here: ${absent.join(', ')}`); return EXIT_UNMEASURED; }
    const view = { name, roots: only, families: (config.families || []).map((f) => f.name) };
    const vrep = census({ config: restrict(config, view), root, home });
    const entry = { ...view, total: vrep.total, measuredAt: new Date().toISOString() };
    writeFileSync(baselinePath, JSON.stringify({ ...old, views: [...(old.views || []), entry] }, null, 2) + '\n');
    console.log(`[tool-census] view '${name}' seeded at ${vrep.total} over ${only.join(', ')}`);
    return EXIT_OK;
  }

  if (args['update-baseline']) {
    const old = readJsonIf(baselinePath);
    if (!old) {
      if (rep.fleetRootsSeen === 0) { console.error('[tool-census] UNMEASURED: no project or user root is visible here. A partial count is not comparable; the baseline is unchanged.'); return EXIT_UNMEASURED; }
      writeFileSync(baselinePath, JSON.stringify(baselineOf(rep, null), null, 2) + '\n');
      console.log(`[tool-census] baseline seeded at ${rep.total}: ${baselinePath}`);
      return EXIT_OK;
    }
    parseSchedule(old);
    const measured = measureViews(config, old, { root, home });
    const seen = measured.filter((m) => !m.why);
    for (const m of measured.filter((x) => x.why)) console.error(`[tool-census] view '${m.view.name}' UNMEASURED: ${m.why}; unchanged.`);
    if (!seen.length) { console.error('[tool-census] UNMEASURED: no view is measurable here. A partial count is not comparable; the baseline is unchanged.'); return EXIT_UNMEASURED; }
    const rose = seen.filter((m) => m.rep.total > m.view.total);
    if (rose.length) {
      for (const m of rose) console.error(`[tool-census] REFUSED: view '${m.view.name}' count ${m.rep.total} is above the baseline ${m.view.total}. The baseline only falls; retire the copy instead.`);
      return EXIT_ACTION;
    }
    const fell = seen.filter((m) => m.rep.total < m.view.total);
    if (!fell.length) { console.log(`[tool-census] every measured view equals its baseline (${seen.map((m) => `${m.view.name}=${m.rep.total}`).join(', ')}); unchanged.`); return EXIT_OK; }
    let next = { ...old };
    for (const m of fell) {
      if (m.view.primary) {
        const { views, ...rest } = next;
        next = { ...baselineOf(m.rep, rest), ...(views ? { views } : {}) };
      } else {
        next.views = next.views.map((v) => (v.name === m.view.name ? { ...v, total: m.rep.total, measuredAt: new Date().toISOString() } : v));
      }
      console.log(`[tool-census] view '${m.view.name}' lowered ${m.view.total} -> ${m.rep.total}`);
    }
    writeFileSync(baselinePath, JSON.stringify(next, null, 2) + '\n');
    console.log(`[tool-census] baseline written: ${baselinePath}`);
    return EXIT_OK;
  }
  if (args.json) console.log(JSON.stringify(rep, null, 2)); else console.log(human(rep));
  if (args.check) {
    if (!existsSync(baselinePath)) { console.error(`[tool-census] no baseline at ${baselinePath}`); return EXIT_FAIL; }
    const baseline = JSON.parse(readFileSync(baselinePath, 'utf8'));
    if (typeof baseline.total !== 'number') { console.error('[tool-census] baseline has no numeric total'); return EXIT_FAIL; }
    parseSchedule(baseline);
    const measured = measureViews(config, baseline, { root, home });
    let failed = false, seen = 0;
    for (const { view, rep: vrep, why } of measured) {
      const tag = view.primary ? '' : `view '${view.name}': `;
      if (why) { console.error(`[tool-census] ${tag}UNMEASURED: ${why}. Neither ok nor failed; run --check on a box that holds the fleet clones.`); continue; }
      seen++;
      const schedule = parseSchedule({ schedule: view.schedule });
      const { current, next } = scheduleAt(schedule, today);
      let bad = false;
      if (vrep.total > view.total) { console.error(`[tool-census] ${tag}ROSE: count ${vrep.total} > baseline ${view.total}. A shared tool was copied or re-registered; run it from one place.${view.primary ? '' : ` Over: ${over(vrep).join('; ') || 'none'}.`}`); bad = true; }
      if (current && vrep.total > current.max) {
        console.error(`[tool-census] ${tag}OVERDUE: count ${vrep.total} > max ${current.max} due by ${current.by} (today ${today}). Still over: ${over(vrep).join('; ')}. Retire the copies; the deadline is not moved to fit.`);
        bad = true;
      }
      if (bad) { failed = true; continue; }
      const ahead = next ? `; next deadline: max ${next.max} by ${next.by}${vrep.total > next.max ? ` (${vrep.total - next.max} to retire)` : ''}` : '';
      console.error(`[tool-census] ${tag}ok: count ${vrep.total} <= baseline ${view.total}${current ? ` and <= max ${current.max} due ${current.by}` : ''}${vrep.total < view.total ? ' (lower: run --update-baseline to ratchet down)' : ''}${ahead}.`);
    }
    // Configured members that no baseline view lists are counted nowhere (rule 7: a view counts only its own roots x
    // families). Named here so they are never silently outside the ratchet; --add-view seeds them at today's count.
    const vs = viewsOf(baseline);
    const freshRoots = vs.some((v) => !v.roots) ? [] : (config.roots || []).filter((r) => !vs.some((v) => v.roots.includes(r.name))).map((r) => `root:${r.name}`);
    const freshFams = vs.some((v) => !v.families) ? [] : (config.families || []).filter((f) => !vs.some((v) => v.families.includes(f.name))).map((f) => `family:${f.name}`);
    if (freshRoots.length || freshFams.length) console.error(`[tool-census] NEW-MEMBERS-UNBASELINED: ${[...freshRoots, ...freshFams].join(', ')} (in no baseline view, so counted nowhere; an owner seeds them with --add-view <name> --roots <a,b>). Informational: the verdict above is unchanged.`);
    if (failed) return EXIT_ACTION;
    if (!seen) return EXIT_UNMEASURED;
  }
  return EXIT_OK;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exit(main()); }
  catch (err) { console.error(`[tool-census] ${err.message}`); process.exit(EXIT_FAIL); }
}
