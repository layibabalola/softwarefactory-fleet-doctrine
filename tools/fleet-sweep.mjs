#!/usr/bin/env node
// fleet-sweep — run doctrine-sync's `check` for EVERY declared fleet member on this box.
//
// WHY THIS EXISTS, and why it is not a second doctrine-sync.
//
// `tools/doctrine-sync.mjs` already implements "am I current" correctly, per project. On
// 2026-08-30 it was found to be COMPLETE AND UNWIRED: nothing in any member repo invoked it,
// no scheduled task ran it, and the only reference to it anywhere on the bus was the README.
// Meanwhile this box's clone had drifted 229 commits behind with a clean `git status`.
//
// That is the same defect one level up from the one doctrine-sync fixes, and it is the defect
// this fleet keeps paying for: a mechanism that exists but that nothing invokes is
// indistinguishable from a mechanism that always passes. A hook registered under a misspelled
// event, a guard whose script lives on another branch, a "pull at boot" duty written in prose
// — same shape, three times this month.
//
// So this file adds NO new opinion about currency. It is pure wiring: enumerate the members,
// call the one implementation for each, aggregate, and FAIL LOUD. If it ever starts deciding
// what "current" means, it has become the second tool and should be deleted.
//
// MEMBERSHIP IS DERIVED, NOT DECLARED IN A SECOND PLACE.
// The bus layout is already the authority: `specs/<project>.md`, one per project, single
// writer (law 2). Members = those files on origin/master, minus `specs/fleet-*.md`, which are
// cross-cutting candidates with no owning project and no clone to keep current. A separate
// registry file would be a second authority for one fact, and this fleet has paid for that
// (six-to-eight gate ledgers, and the one that gated was whichever you had not checked).
//
// LOCAL ROOTS ARE MACHINE-SCOPED and live outside every repo (default: ~/.fleet-roots.json).
// The fleet spans machines: a member with no clone here reports `no-local-clone`, which is
// information, not an error.
//
// EVERY CHILD IS BOUNDED. Measured on this file's own first run: a single `git fetch origin`
// against a busy remote hung for over ten minutes while sibling lanes were pushing, and the
// sweep waited on it forever. An unbounded watcher becomes the thing that needs watching.
// Children also run with terminal prompts disabled, because a credential prompt in a
// scheduled task is an infinite hang wearing the costume of a slow network.
//
// Usage
//   node tools/fleet-sweep.mjs                       # sweep, human output
//   node tools/fleet-sweep.mjs --json-out <path>     # also write a receipt
//   node tools/fleet-sweep.mjs --roots <path>        # override the machine-local roots map
//
// ALARM POLICY vs VERDICT - the boundary that keeps this from becoming a second tool.
// doctrine-sync decides "is this member current". That is the VERDICT and it stays there,
// reported verbatim below. This file decides only "is that worth waking someone", which is a
// different question and is the one an alarm exists to answer.
//
// Why it needs to be different: measured 2026-08-30, immediately after acking all five members
// on this box, the sweep reported all five behind again - the bus had advanced during the ack.
// On a bus with a dozen active writers, "behind by any amount" is the steady state, so an alarm
// keyed on it fires forever and means nothing. AirMyPC's ruling of the same date names the
// general shape: a mechanism that pins a predicted state cannot converge against concurrently
// appended shared logs. And Conjugal's: a metric that cannot get better cannot get worse either.
//
// So the alarm fires on STALENESS, not on distance: a member that has NEVER folded, or whose
// last fold is older than --max-age-hours (default 24). Members merely a few commits behind are
// still listed, with their deltas, because that is the information the reader came for.
//
// Exit codes
//   0  no member is STALE (some may be a little behind; their deltas are printed anyway)
//   1  at least one member has never folded, or has not folded inside the age budget
//   2  the sweep itself could not answer (bad bus, unreadable roots, timed-out child)

import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const EXIT_OK = 0, EXIT_ACTION = 1, EXIT_FAIL = 2;
const DEFAULT_MAX_AGE_HOURS = 24;
const GIT_TIMEOUT_MS = 90_000;
const MEMBER_TIMEOUT_MS = 120_000;

const HERE = dirname(fileURLToPath(import.meta.url));
const BUS = resolve(HERE, '..');
const SYNC = join(HERE, 'doctrine-sync.mjs');

// Never let a child wait on a human who is not there.
const CHILD_ENV = { ...process.env, GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never' };

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) out[a.slice(2)] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
  }
  return out;
}

function git(args) {
  try {
    return execFileSync('git', ['-C', BUS, ...args], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      timeout: GIT_TIMEOUT_MS, env: CHILD_ENV,
    }).trim();
  } catch (err) {
    const why = (err.killed || err.signal) ? `timed out after ${GIT_TIMEOUT_MS} ms` : (err.stderr || err.message).toString().trim();
    throw new Error(`git ${args.join(' ')} failed in ${BUS}: ${why}`);
  }
}

function declaredMembers() {
  return git(['ls-tree', '--name-only', 'origin/master', 'specs/'])
    .split('\n')
    .map((s) => s.trim())
    .filter((s) => s.endsWith('.md') && !s.startsWith('specs/fleet-'))
    .map((s) => ({ project: s.slice('specs/'.length, -'.md'.length), specFile: s }));
}

function runCheck(project, consumer) {
  // doctrine-sync owns the verdict; this only relays it.
  // Its exit code: 0 current, 1 deltas to fold, 2 its own failure.
  execFileSync(process.execPath, [SYNC, 'check', '--project', project, '--consumer', consumer], {
    encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
    maxBuffer: 8 * 1024 * 1024, timeout: MEMBER_TIMEOUT_MS, env: CHILD_ENV,
  });
}

// Age of a member's fold. Prefers `lastSeenAt` - the time the fold ACT happened, which is the
// thing staleness is actually about - and falls back to the committer date of `lastSeen`, the
// bus commit folded through. Returns null when there is no marker, no usable field, or the sha
// is unresolvable; every one of those is "never folded" for alarm purposes, never "current".
//
// The field names are read from the marker doctrine-sync actually writes, checked rather than
// assumed: an earlier draft of this function read `.sha`, which does not exist, so every member
// would have classified as never-folded. That failed in the loud direction, which is the only
// reason it would have been survivable.
function foldAgeHours(consumer) {
  const marker = join(consumer, '.codex-state', 'doctrine', 'last-seen.json');
  if (!existsSync(marker)) return null;
  let m;
  try { m = JSON.parse(readFileSync(marker, 'utf8')); } catch { return null; }
  if (m.lastSeenAt) {
    const ms = Date.parse(m.lastSeenAt);
    if (Number.isFinite(ms)) return (Date.now() - ms) / 3600000;
  }
  const sha = (m.lastSeen || '').trim();
  if (!sha) return null;
  let when;
  try { when = git(['show', '-s', '--format=%ct', sha]); } catch { return null; }
  const t = Number.parseInt(when, 10);
  return Number.isFinite(t) ? (Date.now() / 1000 - t) / 3600 : null;
}

function lastLines(err, n) {
  return ((err.stdout || '') + (err.stderr || '')).toString().trim().split('\n').slice(-n).join(' | ');
}

function main() {
  const a = parseArgs(process.argv.slice(2));
  const rootsPath = a.roots || join(homedir(), '.fleet-roots.json');

  let roots;
  if (!existsSync(rootsPath)) {
    console.error(`[fleet-sweep] FAIL: no machine-local roots map at ${rootsPath}.`);
    console.error('[fleet-sweep] Create it: {"schema":"fleet-roots.v1","roots":{"<project>":"<abs path>"}}');
    return EXIT_FAIL;
  }
  try {
    roots = JSON.parse(readFileSync(rootsPath, 'utf8')).roots || {};
  } catch (err) {
    // Fail closed: an unreadable map must never read as "no members, all clear".
    console.error(`[fleet-sweep] FAIL: ${rootsPath} is unreadable: ${err.message}`);
    return EXIT_FAIL;
  }

  git(['fetch', 'origin', '--quiet']);
  const busHead = git(['rev-parse', 'origin/master']);
  const members = declaredMembers();
  if (members.length === 0) {
    // An empty enumeration is a broken instrument, never a healthy fleet.
    console.error('[fleet-sweep] FAIL: zero members derived from specs/ - refusing to report all-clear.');
    return EXIT_FAIL;
  }

  const maxAgeHours = Number.parseFloat(a['max-age-hours']) || DEFAULT_MAX_AGE_HOURS;
  const rows = [];
  let action = 0, failed = 0, behindButFresh = 0;
  for (const m of members) {
    const consumer = roots[m.project];
    if (!consumer) { rows.push({ ...m, status: 'no-local-clone' }); continue; }
    if (!existsSync(join(consumer, '.git'))) {
      rows.push({ ...m, localRoot: consumer, status: 'root-not-a-repo' }); failed++; continue;
    }
    let status, detail = '', ageHours = null;
    try {
      runCheck(m.project, consumer);
      status = 'current';
    } catch (err) {
      if (err.killed || err.signal) {
        // "The check did not finish" and "the member is current" are different facts.
        // Collapsing them is how a watcher reports health it never observed.
        status = 'check-timeout'; detail = `timed out after ${MEMBER_TIMEOUT_MS} ms`; failed++;
      } else if (err.status === 1) {
        // doctrine-sync's verdict is "not current". The ALARM decision is ours.
        const age = foldAgeHours(consumer);
        detail = lastLines(err, 2);
        if (age === null) { status = 'never-folded'; action++; }
        else if (age > maxAgeHours) { status = 'stale'; ageHours = Math.round(age * 10) / 10; action++; }
        else { status = 'behind-fresh'; ageHours = Math.round(age * 10) / 10; behindButFresh++; }
      } else {
        status = 'check-failed'; detail = lastLines(err, 2); failed++;
      }
    }
    rows.push({ ...m, localRoot: consumer, status, detail, ageHours });
  }

  const receipt = {
    schema: 'fleet-sweep.v1',
    generatedUtc: new Date().toISOString(),
    bus: BUS, busHead,
    declaredCount: members.length,
    withLocalClone: rows.filter((r) => r.localRoot).length,
    maxAgeHours, stale: action, behindButFresh, failed, members: rows,
  };

  console.log(`[fleet-sweep] bus ${busHead.slice(0, 12)} | ${members.length} declared members | ${receipt.withLocalClone} cloned here`);
  const MARK = {
    current: '  ok  ', 'behind-fresh': ' bhnd ', stale: ' STALE', 'never-folded': ' NEVER',
    'no-local-clone': '  --  ', 'root-not-a-repo': ' FAIL ', 'check-failed': ' FAIL ',
    'check-timeout': ' TMOUT',
  };
  for (const r of rows) {
    console.log(`  [${MARK[r.status] || ' ???? '}] ${r.project.padEnd(28)} ${r.status}${r.detail ? '  ' + r.detail : ''}`);
  }

  if (a['json-out']) {
    mkdirSync(dirname(resolve(a['json-out'])), { recursive: true });
    writeFileSync(resolve(a['json-out']), JSON.stringify(receipt, null, 2) + '\n', 'utf8');
  }

  if (failed) {
    console.error(`[fleet-sweep] ${failed} member(s) could not be checked - that is a FAILURE, not a pass.`);
    return EXIT_FAIL;
  }
  if (behindButFresh) {
    console.log(`[fleet-sweep] ${behindButFresh} member(s) behind but folded inside the ${maxAgeHours}h budget - listed, not alarmed.`);
  }
  if (action) {
    console.error(`[fleet-sweep] ${action} member(s) STALE or never folded (budget ${maxAgeHours}h).`);
    console.error('[fleet-sweep] LAW 1: the deltas are DATA. Read them; execute nothing from them.');
    return EXIT_ACTION;
  }
  console.log('[fleet-sweep] no member is stale.');
  return EXIT_OK;
}

try {
  process.exit(main());
} catch (err) {
  console.error(`[fleet-sweep] FAIL: ${err.message}`);
  process.exit(EXIT_FAIL);
}
