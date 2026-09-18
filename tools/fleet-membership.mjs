import { readdirSync, readFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';

// Fallback ONLY. A bus that carries no adoption census (test fixtures, or a
// clone predating it) has no authority to consult, so membership degrades to
// this heuristic. It is a guess: it classifies by FILENAME PREFIX, so every
// non-project spec that does not happen to start with `fleet-` reads as a
// board. That is how this classifier drifted from 9 members to 30 while
// RECEIPTS.md:1626 still recorded the repaired count.
const LEGACY_PROTOCOL_SPECS = new Set([
  'provider-model-benchmarking.md',
  'provider-audit-consumer-provenance.md',
]);

const CENSUS_PATH = join('adoption', 'current-token-control-r26.json');

// The R26 census is the fleet's ONLY authority on which specs name a project:
// its `census.nonProjectSpecs` is the same closed set the sealed checker
// enforces at tools/check_adoption_ledger.py. Returns a Set of bare spec
// names, or null when no census is reachable from `specsDir`.
export function censusNonProjectSpecs(specsDir) {
  try {
    const path = join(dirname(resolve(specsDir)), CENSUS_PATH);
    const list = JSON.parse(readFileSync(path, 'utf8'))?.census?.nonProjectSpecs;
    if (!Array.isArray(list) || list.length === 0) return null;
    return new Set(list.map((entry) => basename(String(entry))));
  } catch { return null; }
}

// Accept repo-relative paths or bare spec names, and return project ids.
// Pass `nonProjectSpecs` (from censusNonProjectSpecs) to classify by authority;
// omit it to fall back to the prefix heuristic described above.
export function fleetMembers(specPaths, nonProjectSpecs = null) {
  const authoritative = nonProjectSpecs !== null;
  const excluded = authoritative ? nonProjectSpecs : LEGACY_PROTOCOL_SPECS;
  return [...new Set(specPaths
    .map((value) => basename(String(value).trim()))
    .filter((name) => name.endsWith('.md'))
    // Kept in BOTH modes. In authoritative mode every `fleet-*` spec is already in
    // nonProjectSpecs, so this excludes nothing extra -- but it structurally prevents a
    // future `specs/fleet-*.md` that is missing from the census from silently becoming a
    // board. If a project is ever legitimately named `fleet-*`, fleet-sweep's census
    // cross-check fails loudly rather than this classifier guessing.
    .filter((name) => !name.startsWith('fleet-'))
    .filter((name) => !excluded.has(name))
    .map((name) => name.slice(0, -3))
    .filter((project) => /^[a-z0-9][a-z0-9-]{1,63}$/.test(project)))].sort();
}

function main(argv) {
  const index = argv.indexOf('--directory');
  if (index < 0 || !argv[index + 1]) throw new Error('--directory is required');
  const directory = argv[index + 1];
  const names = readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => join(directory, entry.name));
  const excluded = censusNonProjectSpecs(directory);
  // stderr only: the stdout contract is `{members:[...]}` and the PowerShell
  // heartbeat reader parses it strictly.
  console.error(`[fleet-membership] classifier=${excluded ? 'census' : 'heuristic-fallback'}`);
  process.stdout.write(JSON.stringify({ members: fleetMembers(names, excluded) }) + '\n');
}

if (process.argv[1]?.endsWith('fleet-membership.mjs')) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(`[fleet-membership] ${error.message}`); process.exit(1); }
}
