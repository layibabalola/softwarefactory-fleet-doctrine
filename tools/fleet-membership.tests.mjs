import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fleetMembers } from './fleet-membership.mjs';

const repo = fileURLToPath(new URL('..', import.meta.url));
for (const name of ['continuity-autonomous-resumption.md', 'resumption-parallel-launch-0906.md']) {
  assert.ok(existsSync(join(repo, 'specs', `fleet-${name}`)), `actual spec must use fleet- prefix: ${name}`);
  assert.ok(!existsSync(join(repo, 'specs', name)), `old name would create phantom board: ${name}`);
}
const ps = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
const root = mkdtempSync(join(tmpdir(), 'fleet-membership-'));
const bus = join(root, 'bus');
const tools = join(bus, 'tools');
mkdirSync(join(bus, 'specs'), { recursive: true });
mkdirSync(join(bus, 'heartbeats'), { recursive: true });
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
  commitSpecs();
  git('push', '-q', 'origin', 'master');
  run(process.execPath, [join(tools, 'fleet-sweep.mjs'), '--roots', roots, '--json-out', receipt]);
  sweep = JSON.parse(readFileSync(receipt, 'utf8'));
  assert.deepEqual(sweep.members.map((m) => m.project).sort(), ['adobe-ingester', 'cloudvore', 'provider-foo']);

  const heartbeat = JSON.parse(runOutput(ps, ['-NoProfile', '-File', join(tools, 'Get-FleetHeartbeatStatus.ps1'), '-BusRoot', bus, '-Json']));
  assert.deepEqual(heartbeat.boards.map((b) => b.board).sort(), ['adobe-ingester', 'cloudvore', 'provider-foo']);
  assert.equal(heartbeat.boards.find((b) => b.board === 'cloudvore').status, 'ABSENT');
  assert.deepEqual(fleetMembers(['specs/cloudvore.md', 'specs/fleet-x.md', 'specs/provider-model-benchmarking.md', 'specs/provider-audit-consumer-provenance.md', 'specs/provider-foo.md']), ['cloudvore', 'provider-foo']);
  writeFileSync(join(tools, 'fleet-membership.mjs'), "process.stdout.write(JSON.stringify({members:[{bad:'object'}]}));\n");
  assert.throws(() => run(ps, ['-NoProfile', '-File', join(tools, 'Get-FleetHeartbeatStatus.ps1'), '-BusRoot', bus, '-Json']), (err) => err.status === 1);
  console.log('fleet membership: shared classifier agrees across sweep and heartbeat reader');
} finally {
  rmSync(root, { recursive: true, force: true });
}
