import { readdirSync, readFileSync } from 'node:fs';
import { basename, join } from 'node:path';

const LEGACY_PROTOCOL_SPECS = new Set([
  'provider-model-benchmarking.md',
  'provider-audit-consumer-provenance.md',
]);

// Accept repo-relative paths or bare spec names, and return project ids.
export function fleetMembers(specPaths) {
  return [...new Set(specPaths
    .map((value) => basename(String(value).trim()))
    .filter((name) => name.endsWith('.md'))
    .filter((name) => !name.startsWith('fleet-'))
    .filter((name) => !LEGACY_PROTOCOL_SPECS.has(name))
    .map((name) => name.slice(0, -3))
    .filter((project) => /^[a-z0-9][a-z0-9-]{1,63}$/.test(project)))].sort();
}

function main(argv) {
  // --stdin: the direct entries of specs/ as newline-separated repo paths (`git ls-tree --name-only
  // refs/remotes/origin/master specs/`), so a reader in another language applies this one rule to the
  // committed tree instead of copying it (tools/factory/fleet-scorecard.py --fleet).
  if (argv.includes('--stdin')) {
    const paths = readFileSync(0, 'utf8').split(/\r?\n/).filter(Boolean);
    process.stdout.write(JSON.stringify({ members: fleetMembers(paths) }) + '\n');
    return;
  }
  const index = argv.indexOf('--directory');
  if (index < 0 || !argv[index + 1]) throw new Error('--directory or --stdin is required');
  const directory = argv[index + 1];
  const names = readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => join(directory, entry.name));
  process.stdout.write(JSON.stringify({ members: fleetMembers(names) }) + '\n');
}

if (process.argv[1]?.endsWith('fleet-membership.mjs')) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(`[fleet-membership] ${error.message}`); process.exit(1); }
}
