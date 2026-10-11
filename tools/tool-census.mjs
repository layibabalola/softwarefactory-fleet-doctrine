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
//   Measured 2026-10-11: session-checkpoint.py in 4 versions, wired by 3 projects AND the user settings.
//
// What it counts
//   count = sum over families of (distinct versions - 1) + double registrations.
//   A version is the sha256 of the file (CRLF read as LF), or of its shared section when the family
//   names a marker; a copy lacking the marker hashes whole and is flagged. A double registration is a
//   (project, family) pair where the project's .claude/settings.json and the user settings both wire
//   the family on at least one common hook event.
//   Copies are found with `git ls-files --cached --others --exclude-standard` in a git root (tracked
//   and untracked-not-ignored), or a directory walk minus the config's excludeDirs otherwise.
//
// Usage
//   node tools/tool-census.mjs                       human report
//   node tools/tool-census.mjs --json                machine report
//   node tools/tool-census.mjs --check               exit 1 if the count rose above the baseline
//   node tools/tool-census.mjs --update-baseline     write the baseline; refuses a rise
//   overrides: --config <json> --baseline <json> --root <dir for relative paths> --home <dir for '~'>
//   '@bus' in the config is this script's own repository.
// Exit: 0 ok; 1 the count rose (or a refused raise); 2 tool or environment failure.
// It reads the fleet and writes only the baseline file, and only on --update-baseline (law 1, law 2).

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const EXIT_OK = 0, EXIT_ACTION = 1, EXIT_FAIL = 2;
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

function listFiles(dir, excludeDirs) {
  if (existsSync(join(dir, '.git'))) {
    try {
      const out = execFileSync('git', ['-C', dir, 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 60000, maxBuffer: 256 * 1024 * 1024,
        env: { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_OPTIONAL_LOCKS: '0' },
      });
      return out.split('\0').filter(Boolean).filter((f) => !f.split('/').some((s) => excludeDirs.has(s)) && existsSync(join(dir, f)));
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
  walk(dir, '');
  return files;
}

function versionOf(file, marker) {
  const text = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  let section = text, markerFound = null;
  if (marker) {
    const lines = text.split('\n');
    const i = lines.findIndex((l) => l.includes(marker));
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

export function census({ config, root, home }) {
  const excludeDirs = new Set(config.excludeDirs || ['.git', 'node_modules', 'archive', '__pycache__', 'worktrees']);
  const roots = (config.roots || []).map((r) => ({ ...r, dir: expand(r.path, { root, home }) }));
  const userSettings = config.userSettings ? expand(config.userSettings, { root, home }) : null;
  const userScripts = userSettings ? hookScripts(userSettings) : null;
  const absent = roots.filter((r) => !existsSync(r.dir) || !statSync(r.dir).isDirectory()).map((r) => r.name);
  const fileCache = new Map();
  const families = [];
  const doubles = [];
  for (const fam of config.families || []) {
    const res = (fam.names || []).map(globRe);
    const copies = [];
    for (const r of roots) {
      if (absent.includes(r.name)) continue;
      if (!fileCache.has(r.name)) fileCache.set(r.name, listFiles(r.dir, excludeDirs));
      for (const f of fileCache.get(r.name)) {
        if (!res.some((re) => re.test(baseName(f)))) continue;
        const v = versionOf(join(r.dir, f), fam.sharedSectionMarker);
        copies.push({ root: r.name, path: f, ...v });
      }
    }
    const distinct = [...new Set(copies.map((c) => c.hash))];
    families.push({ name: fam.name, marker: fam.sharedSectionMarker || null, copies, distinct: distinct.length, excess: Math.max(distinct.length - 1, 0) });
    for (const r of roots) {
      if (r.kind === 'user' || absent.includes(r.name)) continue;
      const proj = familyEvents(hookScripts(join(r.dir, '.claude', 'settings.json')), fam);
      const user = familyEvents(userScripts, fam);
      const both = proj.filter((p) => user.some((u) => u.event === p.event));
      if (both.length) doubles.push({ family: fam.name, project: r.name, events: both.map((p) => p.event), projectFlat: both.some((p) => p.flat) });
    }
  }
  const total = families.reduce((s, f) => s + f.excess, 0) + doubles.length;
  return { total, families, doubleRegistrations: doubles, absentRoots: absent };
}

function human(rep) {
  const L = [];
  for (const f of rep.families) {
    L.push(`[tool-census] ${f.name}: ${f.copies.length} cop${f.copies.length === 1 ? 'y' : 'ies'}, ${f.distinct} distinct version(s)${f.marker ? ` (hashed below '${f.marker}')` : ''}`);
    for (const c of f.copies) L.push(`    ${c.hash.slice(0, 10)}  ${String(c.lines).padStart(5)} lines  ${c.root}: ${c.path}${c.markerFound === false ? '   NO MARKER (hashed whole)' : ''}`);
  }
  for (const d of rep.doubleRegistrations) L.push(`[tool-census] DOUBLE REGISTRATION: ${d.family} wired by ${d.project} .claude/settings.json AND user settings on ${d.events.join(', ')}${d.projectFlat ? ' (project entry is FLAT, not the matcher-group schema: may never fire)' : ''}`);
  if (rep.absentRoots.length) L.push(`[tool-census] roots absent on this box (skipped): ${rep.absentRoots.join(', ')}`);
  L.push(`[tool-census] count = ${rep.families.reduce((s, f) => s + f.excess, 0)} excess version(s) + ${rep.doubleRegistrations.length} double registration(s) = ${rep.total}`);
  return L.join('\n');
}

function baselineOf(rep) {
  return {
    schema: 'tool-census-baseline.v1',
    total: rep.total,
    families: Object.fromEntries(rep.families.map((f) => [f.name, { copies: f.copies.length, distinct: f.distinct }])),
    doubleRegistrations: rep.doubleRegistrations.map((d) => `${d.project}:${d.family}:${d.events.join('+')}`),
    measuredAt: new Date().toISOString(),
    rule: 'The count may only fall. tools/tool-census.mjs --update-baseline refuses a rise. It grades the fleet tool layout, never a lane (metrics law 1).',
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = resolve(args.root ? String(args.root) : process.cwd());
  const home = resolve(args.home ? String(args.home) : homedir());
  const configPath = resolve(args.config ? String(args.config) : join(BUS, 'tools', 'tool-census.config.json'));
  const baselinePath = resolve(args.baseline ? String(args.baseline) : join(BUS, 'metrics', 'tool-census-baseline.json'));
  if (!existsSync(configPath)) { console.error(`[tool-census] config not found: ${configPath}`); return EXIT_FAIL; }
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  const rep = census({ config, root, home });

  if (args['update-baseline']) {
    const old = existsSync(baselinePath) ? JSON.parse(readFileSync(baselinePath, 'utf8')) : null;
    if (old && rep.total > old.total) {
      console.error(`[tool-census] REFUSED: count ${rep.total} is above the baseline ${old.total}. The baseline only falls; retire the copy instead.`);
      return EXIT_ACTION;
    }
    if (old && rep.total === old.total) { console.log(`[tool-census] count ${rep.total} equals the baseline; unchanged.`); return EXIT_OK; }
    writeFileSync(baselinePath, JSON.stringify(baselineOf(rep), null, 2) + '\n');
    console.log(`[tool-census] baseline ${old ? `lowered ${old.total} -> ` : 'seeded at '}${rep.total}: ${baselinePath}`);
    return EXIT_OK;
  }
  if (args.json) console.log(JSON.stringify(rep, null, 2)); else console.log(human(rep));
  if (args.check) {
    if (!existsSync(baselinePath)) { console.error(`[tool-census] no baseline at ${baselinePath}`); return EXIT_FAIL; }
    const base = JSON.parse(readFileSync(baselinePath, 'utf8')).total;
    if (typeof base !== 'number') { console.error('[tool-census] baseline has no numeric total'); return EXIT_FAIL; }
    if (rep.total > base) { console.error(`[tool-census] ROSE: count ${rep.total} > baseline ${base}. A shared tool was copied or re-registered; run it from one place.`); return EXIT_ACTION; }
    console.error(`[tool-census] ok: count ${rep.total} <= baseline ${base}${rep.total < base ? ' (lower: run --update-baseline to ratchet down)' : ''}.`);
  }
  return EXIT_OK;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exit(main()); }
  catch (err) { console.error(`[tool-census] ${err.message}`); process.exit(EXIT_FAIL); }
}
