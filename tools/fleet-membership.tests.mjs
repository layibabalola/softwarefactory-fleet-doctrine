import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { censusNonProjectSpecs, fleetMembers } from './fleet-membership.mjs';

const repo = fileURLToPath(new URL('..', import.meta.url));
for (const name of ['continuity-autonomous-resumption.md', 'resumption-parallel-launch-0906.md']) {
  assert.ok(existsSync(join(repo, 'specs', `fleet-${name}`)), `actual spec must use fleet- prefix: ${name}`);
  assert.ok(!existsSync(join(repo, 'specs', name)), `old name would create phantom board: ${name}`);
}

// Regression control: on the REAL repo the classifier must equal the R26 census
// project set. The census is the only authority on which specs name a project;
// the prefix heuristic is a guess. RECEIPTS.md:1626 recorded this classifier
// repaired to nine members -- it had drifted to thirty against a census of ten,
// because every non-project spec not starting with `fleet-` read as a board.
const realSpecs = readdirSync(join(repo, 'specs'), { withFileTypes: true })
  .filter((entry) => entry.isFile())
  .map((entry) => entry.name);
const nonProject = censusNonProjectSpecs(join(repo, 'specs'));
assert.ok(nonProject && nonProject.size > 0, 'census must be reachable from the real repo');
const censusProjects = JSON.parse(
  readFileSync(join(repo, 'adoption', 'current-token-control-r26.json'), 'utf8'),
).projects.map((project) => project.projectId).sort();
assert.deepEqual(
  fleetMembers(realSpecs, nonProject), censusProjects,
  'classifier must equal the census project set',
);

// NEGATIVE CONTROL -- this gate must be shown able to fail before its pass
// counts. The retired heuristic must still DISAGREE with the census; if this
// assertion ever trips, the two classifiers have converged and the check above
// has silently stopped testing anything.
assert.notDeepEqual(
  fleetMembers(realSpecs), censusProjects,
  'heuristic must still differ from the census, or the regression test is inert',
);
const ps = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
const root = mkdtempSync(join(tmpdir(), 'fleet-membership-'));
const bus = join(root, 'bus');
const tools = join(bus, 'tools');
mkdirSync(join(bus, 'specs'), { recursive: true });
mkdirSync(join(bus, 'heartbeats'), { recursive: true });
mkdirSync(join(bus, 'adoption'), { recursive: true });
mkdirSync(tools);
for (const file of ['fleet-sweep.mjs', 'fleet-membership.mjs', 'doctrine-sync.mjs', 'Get-FleetHeartbeatStatus.ps1']) {
  cpSync(join(repo, 'tools', file), join(tools, file));
}

function run(file, args, options = {}) {
  return execFileSync(file, args, { cwd: bus, encoding: 'utf8', timeout: 20000, ...options });
}
function runOutput(file, args, options = {}) {
  try { return run(file, args, options); }
  catch (err) { if (typeof err.stdout === 'string') return err.stdout; throw err; }
}
function git(...args) { return run('git', args); }
// The sweep classifies membership from the census, so the fixture bus must carry one. Only the
// fields the classifier reads are modelled: census.nonProjectSpecs and projects[].projectId.
function writeCensus(projectIds) {
  writeFileSync(join(bus, 'adoption', 'current-token-control-r26.json'), JSON.stringify({
    census: { nonProjectSpecs: [
      'specs/provider-model-benchmarking.md',
      'specs/provider-audit-consumer-provenance.md',
    ] },
    projects: projectIds.map((projectId) => ({ projectId })),
  }, null, 1));
}

function commitSpecs() {
  git('add', '.');
  git('-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture');
}

try {
  git('init', '-q');
  git('branch', '-M', 'master');
  writeFileSync(join(bus, 'specs', 'cloudvore.md'), '# cloudvore\n');
  writeFileSync(join(bus, 'specs', 'adobe-ingester.md'), '# adobe\n');
  writeFileSync(join(bus, 'specs', 'continuity-autonomous-resumption.md'), 'cross-cutting\n');
  writeFileSync(join(bus, 'specs', 'resumption-parallel-launch-0906.md'), 'cross-cutting\n');
  writeFileSync(join(bus, 'specs', 'provider-model-benchmarking.md'), 'legacy\n');
  writeFileSync(join(bus, 'specs', 'provider-audit-consumer-provenance.md'), 'legacy\n');
  writeFileSync(join(bus, 'specs', 'provider-foo.md'), 'real\n');
  writeCensus(['adobe-ingester', 'cloudvore', 'continuity-autonomous-resumption', 'provider-foo', 'resumption-parallel-launch-0906']);
  commitSpecs();
  const bare = join(root, 'origin.git');
  run('git', ['clone', '--bare', '-q', bus, bare], { cwd: root });
  git('remote', 'add', 'origin', bare);

  const roots = join(root, 'roots.json');
  const receipt = join(root, 'receipt.json');
  writeFileSync(roots, JSON.stringify({ schema: 'fleet-roots.v1', roots: {} }));
  run(process.execPath, [join(tools, 'fleet-sweep.mjs'), '--roots', roots, '--json-out', receipt]);
  let sweep = JSON.parse(readFileSync(receipt, 'utf8'));
  assert.deepEqual(sweep.members.map((m) => m.project).sort(), [
    'adobe-ingester', 'cloudvore', 'continuity-autonomous-resumption', 'provider-foo', 'resumption-parallel-launch-0906',
  ]);

  const oldA = join(bus, 'specs', 'continuity-autonomous-resumption.md');
  const oldB = join(bus, 'specs', 'resumption-parallel-launch-0906.md');
  renameSync(oldA, join(bus, 'specs', 'fleet-continuity-autonomous-resumption.md'));
  renameSync(oldB, join(bus, 'specs', 'fleet-resumption-parallel-launch-0906.md'));
  writeCensus(['adobe-ingester', 'cloudvore', 'provider-foo']);
  commitSpecs();
  git('push', '-q', 'origin', 'master');
  run(process.execPath, [join(tools, 'fleet-sweep.mjs'), '--roots', roots, '--json-out', receipt]);
  sweep = JSON.parse(readFileSync(receipt, 'utf8'));
  assert.deepEqual(sweep.members.map((m) => m.project).sort(), ['adobe-ingester', 'cloudvore', 'provider-foo']);

  const heartbeat = JSON.parse(runOutput(ps, ['-NoProfile', '-File', join(tools, 'Get-FleetHeartbeatStatus.ps1'), '-BusRoot', bus, '-Json']));
  assert.deepEqual(heartbeat.boards.map((b) => b.board).sort(), ['adobe-ingester', 'cloudvore', 'provider-foo']);
  assert.equal(heartbeat.boards.find((b) => b.board === 'cloudvore').status, 'ABSENT');
  assert.deepEqual(fleetMembers(['specs/cloudvore.md', 'specs/fleet-x.md', 'specs/provider-model-benchmarking.md', 'specs/provider-audit-consumer-provenance.md', 'specs/provider-foo.md']), ['cloudvore', 'provider-foo']);
  // NEGATIVE CONTROL for the authoritative-membership guard. Without the census the classifier
  // falls back to a prefix GUESS; measured on the real bus that guess yields 30 boards against a
  // census of 10, and every phantom takes the `no-local-clone` path, which increments nothing --
  // so the sweep would print "no member is stale" and exit 0. A wrong instrument must not be able
  // to report health. If this assertion ever stops throwing, that failure mode is back.
  rmSync(join(bus, 'adoption', 'current-token-control-r26.json'));
  commitSpecs();
  git('push', '-q', 'origin', 'master');
  let refusedStatus = 0;
  let refusedText = '';
  try {
    run(process.execPath, [join(tools, 'fleet-sweep.mjs'), '--roots', roots, '--json-out', receipt]);
  } catch (err) {
    refusedStatus = err.status ?? -1;
    refusedText = `${err.stderr ?? ''}${err.stdout ?? ''}${err.message ?? ''}`;
  }
  assert.notEqual(refusedStatus, 0, 'sweep must REFUSE when membership is not authoritative');
  assert.match(refusedText, /NOT authoritative/, 'the refusal must name the reason');

  writeFileSync(join(tools, 'fleet-membership.mjs'), "process.stdout.write(JSON.stringify({members:[{bad:'object'}]}));\n");
  assert.throws(() => run(ps, ['-NoProfile', '-File', join(tools, 'Get-FleetHeartbeatStatus.ps1'), '-BusRoot', bus, '-Json']), (err) => err.status === 1);
  console.log('fleet membership: shared classifier agrees across sweep and heartbeat reader');
  console.log('fleet membership: sweep refuses to report all-clear on non-authoritative membership');
} finally {
  rmSync(root, { recursive: true, force: true });
}
