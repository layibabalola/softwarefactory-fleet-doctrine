#!/usr/bin/env node
// Offline D02 slice-A fixtures. Uses only temporary local git repositories and remotes.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = mkdtempSync(join(tmpdir(), 'doctrine-sync-'));
const tool = fileURLToPath(new URL('./doctrine-sync.mjs', import.meta.url));
const run = (cwd, args, allow = false) => {
  try { return execFileSync('git', ['-C', cwd, ...args], { encoding: 'utf8', env: { ...process.env, GIT_TERMINAL_PROMPT: '0' } }).trim(); }
  catch (e) { if (allow) return null; throw e; }
};
const sync = (args, allow = false, selectedTool = tool) => {
  try { return execFileSync(process.execPath, [selectedTool, ...args], { encoding: 'utf8', timeout: 35000, env: { ...process.env, GIT_TERMINAL_PROMPT: '0' } }); }
  catch (e) { if (allow) return { status: e.status ?? 124, timedOut: e.code === 'ETIMEDOUT', output: `${e.stdout || ''}${e.stderr || ''}` }; throw e; }
};
const commit = (repo, name, body) => { writeFileSync(join(repo, name), body); run(repo, ['add', name]); run(repo, ['commit', '-m', body]); return run(repo, ['rev-parse', 'HEAD']); };

try {
  const remote = join(root, 'remote.git');
  execFileSync('git', ['init', '--bare', remote]);
  const seed = join(root, 'seed'); execFileSync('git', ['init', seed]);
  run(seed, ['config', 'user.email', 'test@example.invalid']); run(seed, ['config', 'user.name', 'Test']);
  writeFileSync(join(seed, 'RULINGS.md'), 'rulings\n'); writeFileSync(join(seed, 'specs-a.md'), 'A\n');
  run(seed, ['add', '.']); run(seed, ['commit', '-m', 'A']); const a = run(seed, ['rev-parse', 'HEAD']);
  run(seed, ['branch', '-M', 'master']); run(seed, ['remote', 'add', 'origin', remote]); run(seed, ['push', '-u', 'origin', 'master']);
  const bus = join(root, 'bus'); execFileSync('git', ['clone', remote, bus]);
  run(bus, ['config', 'user.email', 'test@example.invalid']); run(bus, ['config', 'user.name', 'Test']);
  const consumer = join(root, 'consumer'); execFileSync('git', ['init', consumer]);
  const base = ['--bus', bus, '--project', 'a', '--consumer', consumer];
  let cases = 0;
  let r = sync(['check', ...base], true); assert.equal(r.status, 1, 'missing marker is actionable'); cases++;
  commit(seed, 'RULINGS.md', 'B'); const b = run(seed, ['rev-parse', 'HEAD']); run(seed, ['push', 'origin', 'master']);
  sync(['ack', ...base, '--commit', a]);
  assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, a);
  r = sync(['check', ...base], true); assert.equal(r.status, 1, 'newer B remains actionable'); assert.match(r.output, new RegExp(b.slice(0, 7))); cases++;
  // An existing commit that is not on origin/master must be rejected without moving A.
  const orphan = commit(bus, 'orphan.md', 'orphan');
  for (const bad of [undefined, 'not-a-sha', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', orphan]) {
    const before = readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'), 'utf8');
    r = sync(['ack', ...base, ...(bad ? ['--commit', bad] : [])], true); assert.equal(r.status, 2); assert.equal(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'), 'utf8'), before);
    cases++;
  }
  const absent = join(root, 'absent'); r = sync(['ack', ...base.slice(0, 4), '--consumer', absent, '--commit', a], true); assert.equal(r.status, 2); cases++;
  assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, a);
  // A fetch failure preserves the marker.
  run(bus, ['remote', 'set-url', 'origin', join(root, 'missing-remote.git')]);
  r = sync(['ack', ...base, '--commit', a], true); assert.equal(r.status, 2); assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, a); cases++;
  run(bus, ['remote', 'set-url', 'origin', remote]);
  // Simulate a hung git child; the production timeout is finite and marker remains A.
  const sourceText = readFileSync(tool, 'utf8');
  const timeoutTool = join(root, 'timeout-tool.mjs');
  assert.ok(sourceText.includes("execFileSync('git',"));
  const injection = "function timeoutChild(file,args,options) { if(options.timeout !== 30000 || options.env.GCM_INTERACTIVE !== 'never' || options.env.GIT_TERMINAL_PROMPT !== '0') throw new Error('wrong child options'); const e=new Error('simulated git timeout'); e.code='ETIMEDOUT'; throw e; }\n";
  writeFileSync(timeoutTool, sourceText.replace("execFileSync('git',", "timeoutChild('git',") + '\n' + injection);
  r = sync(['ack', ...base, '--commit', a], true, timeoutTool); assert.equal(r.status, 2); assert.match(r.output, /simulated git timeout/); assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, a); cases++;
  // A normal acknowledgement records the exact reviewed SHA, even when origin/master is newer.
  // Run the actual latest-head mutation in a temporary tool copy and prove the A assertion bites.
  const assignment = "const reviewed = git(bus, ['rev-parse', '--verify', `${commit}^{commit}`], { allowFail: true });";
  assert.ok(sourceText.includes(assignment));
  const mutant = join(root, 'latest-head-tool.mjs');
  writeFileSync(mutant, sourceText.replace(assignment, "const reviewed = git(bus, ['rev-parse', 'origin/master']);"));
  sync(['ack', ...base, '--commit', a], false, mutant);
  assert.throws(() => assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, a), assert.AssertionError); cases++;
  sync(['ack', ...base, '--commit', b]); assert.equal(JSON.parse(readFileSync(join(consumer, '.codex-state/doctrine/last-seen.json'))).lastSeen, b);
  cases++;
  // Exact D03 publication fixtures use a separate consumer remote so ancestry is real.
  const sourceRemote = join(root, 'source.git'); execFileSync('git', ['init', '--bare', sourceRemote]);
  const sourceSeed = join(root, 'source-seed'); execFileSync('git', ['init', sourceSeed]);
  run(sourceSeed, ['config', 'user.email', 'test@example.invalid']); run(sourceSeed, ['config', 'user.name', 'Test']);
  commit(sourceSeed, 'result.txt', 'source'); const sourceCommit = run(sourceSeed, ['rev-parse', 'HEAD']); run(sourceSeed, ['branch', '-M', 'master']); run(sourceSeed, ['remote', 'add', 'origin', sourceRemote]); run(sourceSeed, ['push', '-u', 'origin', 'master']);
  const exactConsumer = join(root, 'exact-consumer'); execFileSync('git', ['clone', sourceRemote, exactConsumer]);
  run(exactConsumer, ['config', 'user.email', 'test@example.invalid']); run(exactConsumer, ['config', 'user.name', 'Test']);
  const publishSpec = (body, message) => { mkdirSync(join(seed, 'specs'), { recursive: true }); writeFileSync(join(seed, 'specs', 'a.md'), body); run(seed, ['add', 'specs/a.md']); run(seed, ['commit', '-m', message]); run(seed, ['push', 'origin', 'master']); return run(seed, ['rev-parse', 'HEAD']); };
  const exactBase = ['export-check', '--bus', bus, '--project', 'a', '--consumer', exactConsumer, '--source-commit', sourceCommit];
  const matchingPub = publishSpec(`source_commit: ${sourceCommit}\n`, 'unrelated subject naming a');
  r = sync([...exactBase, '--publication-commit', matchingPub], true); assert.match(r, /publication VERIFIED/); cases++;
  const unrelatedPub = publishSpec('# no provenance\n', 'a unrelated publication');
  r = sync([...exactBase, '--publication-commit', unrelatedPub], true); assert.equal(r.status, 2); cases++;
  const wrongPub = publishSpec('source_commit: 0000000000000000000000000000000000000000\n', 'a wrong source');
  r = sync([...exactBase, '--publication-commit', wrongPub], true); assert.equal(r.status, 2); cases++;
  const duplicatePub = publishSpec(`source_commit: ${sourceCommit}\nsource_commit: ${sourceCommit}\n`, 'a duplicate source');
  r = sync([...exactBase, '--publication-commit', duplicatePub], true); assert.equal(r.status, 2); cases++;
  mkdirSync(join(bus, 'specs'), { recursive: true });
  const localPub = commit(bus, 'specs/a.md', `source_commit: ${sourceCommit}\n`);
  r = sync([...exactBase, '--publication-commit', localPub], true); assert.equal(r.status, 2); cases++;
  const unpublishedSource = commit(exactConsumer, 'result.txt', 'unpublished source'); r = sync([...exactBase.slice(0, -2), '--source-commit', unpublishedSource, '--publication-commit', matchingPub], true); assert.equal(r.status, 2); cases++;
  r = sync(exactBase, true); assert.equal(r.status, 2); cases++;
  r = sync([...exactBase.slice(0, -2), '--publication-commit', matchingPub], true); assert.equal(r.status, 2); cases++;
  r = sync(['export-check', '--bus', bus, '--project', '../a', '--consumer', exactConsumer, '--source-commit', sourceCommit, '--publication-commit', matchingPub], true); assert.equal(r.status, 2); cases++;
  console.log(`doctrine-sync fixtures: ${cases} cases passed (including 9 D03 exact-publication cases)`);
} finally { rmSync(root, { recursive: true, force: true }); }
