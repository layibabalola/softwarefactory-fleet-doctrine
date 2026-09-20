import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { constraintErrors, fleetStatus, parseLine, roster, table } from './jev-adoption-status.mjs';

const here = fileURLToPath(new URL('.', import.meta.url));
const root = mkdtempSync(join(tmpdir(), 'jev-adoption-'));
const bus = join(root, 'bus');
mkdirSync(join(bus, 'specs'), { recursive: true });

const STANDARD = [
  '# Jev shadow-mode integration standard', '',
  '**Status: `CANDIDATE r6` — reviewed.**', '',
  '## 5. Per-project instances (top pick, hook point, log, comparison, bounding rule)', '',
  '| Project | Top pick | Hook | Log | Compare | Rule |', '|---|---|---|---|---|---|',
  '| Cloudvore | a | b | c | d | e |',
  '| softwarefactory-fleet-doctrine | a | b | c | d | e |',
  '| Conjugal | a | b | c | d | e |',
  '| magic-lantern_dannephoto | a | b | c | d | e |',
  '| SilentBackgroundProcess | a | b | c | d | e |', '',
  '## 6. Next section', '| Not | a | project |',
].join('\n');
const write = (rel, text) => writeFileSync(join(bus, rel), text, 'utf8');
write('specs/fleet-jev-shadow-mode.md', STANDARD);

// roster: five rows in table order, revision from the status line, next section not swept
const r = roster(STANDARD);
assert.deepEqual(r.projects, ['Cloudvore', 'softwarefactory-fleet-doctrine', 'Conjugal', 'magic-lantern_dannephoto', 'SilentBackgroundProcess']);
assert.equal(r.revision, 'r6');

// grammar
const good = 'JEV: DISPOSITION-ADOPT standard=r6@ad426fb qsv=66e7e43e123e84d5 log=logs/jev/jev-shadow.jsonl lines=575 asOf=2026-09-20 record=cloudvore:BACKLOG.md#JS1';
const p = parseLine(good);
assert.equal(p.error, undefined);
assert.equal(p.state, 'DISPOSITION-ADOPT');
assert.equal(p.lines, 575);
assert.equal(p.recordProject, 'cloudvore');
assert.equal(parseLine('JEV: DISPOSITION-ADOPT standard=r6@ad426fb').error, 'malformed');
assert.equal(parseLine('JEV: LIVE standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=x:y').error, 'unknown state LIVE');
assert.equal(parseLine('JEV: NONE standard=r6@ad426fb qsv=abc log=NONE lines=0 asOf=2026-09-20 record=x:y').error, 'malformed', 'qsv must be 16 hex or NONE');
assert.equal(parseLine(good + ' trailing').error, 'malformed');
assert.equal(parseLine(good + ' ').error, 'malformed', 'no trailing whitespace');
assert.equal(parseLine(good.replace('record=cloudvore:', 'record=cloudvore:\u00e9')).error, 'malformed', 'printable ASCII only');
assert.equal(parseLine(good.replace('JEV: ', 'JEV:\t')).error, 'malformed', 'a tab is not a space');
assert.equal(parseLine(good.replace('record=cloudvore:', 'record=Cloudvore:')).error, 'malformed', 'record project token is lowercase');
assert.equal(parseLine(good.replace('qsv=66e7e43e123e84d5', 'qsv=66E7E43E123E84D5')).error, 'malformed', 'lowercase hex only');
assert.equal(parseLine(good.replace('lines=575', 'lines=9007199254740993')).error, 'malformed', 'at most nine digits');
assert.equal(parseLine(good.replace('lines=575', 'lines=999999999')).lines, 999999999);

// constraints
assert.deepEqual(constraintErrors(p, 'Cloudvore', 'r6'), []);
assert.deepEqual(constraintErrors(p, 'conjugal', 'r6'), ['record names cloudvore, surface is conjugal']);
assert.deepEqual(constraintErrors(p, 'cloudvore', 'r7'), ['standard r6@ad426fb is not the bus\'s r7']);
const live = parseLine('JEV: SHADOW-LIVE standard=r6@ad426fb qsv=NONE log=NONE lines=99 asOf=2026-09-20 record=cloudvore:x');
assert.equal(constraintErrors(live, 'cloudvore', 'r6').length, 3);
const liveNoRecord = parseLine('JEV: SHADOW-LIVE standard=r6@ad426fb qsv=66e7e43e123e84d5 log=l lines=500 asOf=2026-09-20 record=cloudvore:NONE');
assert.deepEqual(constraintErrors(liveNoRecord, 'cloudvore', 'r6'), ['SHADOW-LIVE needs a record']);
const adv = parseLine('JEV: ADVISORY standard=r6@ad426fb qsv=66e7e43e123e84d5 log=l lines=500 asOf=2026-09-20 record=cloudvore:x');
assert.match(constraintErrors(adv, 'cloudvore', 'r6')[0], /reserved/);
const noRecord = parseLine('JEV: DISPOSITION-HOLD standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=silentbackgroundprocess:NONE');
assert.deepEqual(constraintErrors(noRecord, 'silentbackgroundprocess', 'r6'), ['DISPOSITION-HOLD needs a record']);

// fleet: nothing recorded -> exit 2, every row NONE / found 0
let s = fleetStatus(bus, null);
assert.equal(s.exit, 2);
assert.equal(s.missing, 5);
assert.ok(s.rows.every((row) => row.state === 'NONE' && row.found === 0));

// spec surface, last line wins; RECEIPTS fallback filtered by record project; malformed -> 3
write('specs/cloudvore.md', ['# Cloudvore', 'JEV: NONE standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-19 record=cloudvore:NONE', 'text', good, ''].join('\n'));
write('specs/conjugal.md', '# Conjugal\nJEV: DISPOSITION-DISTINGUISH standard=r6@ad426fb qsv=NONE log=scratchpad/jev-shadow.jsonl lines=34 asOf=2026-09-20 record=conjugal:coordination/doctrine-folds/20260919-jev-shadow-mode-disposition.md\n');
write('RECEIPTS.md', [
  '# Receipts',
  'JEV: DISPOSITION-DISTINGUISH standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=softwarefactory-fleet-doctrine:receipts/fleet-jev-shadow-mode-ratification-2026-09-19.md',
  'JEV: DISPOSITION-HOLD standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=silentbackgroundprocess:reports/JEV-SHADOW-MODE-DISPOSITION-20260919.md',
  'JEV: DISPOSITION-ADOPT standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=cloudvore:should-not-be-read-here',
  'JEV: DISPOSITION-HOLD standard=r6@ad426fb qsv=abc log=NONE lines=0 asOf=2026-09-20 record=nobody-in-particular',
  'JEV: BROKEN log=record=silentbackgroundprocess:x record=nobody-in-particular', '',
].join('\n'));
s = fleetStatus(bus, null);
const by = Object.fromEntries(s.rows.map((row) => [row.project, row]));
assert.equal(by.Cloudvore.state, 'DISPOSITION-ADOPT');
assert.equal(by.Cloudvore.found, 2, 'both lines counted, last wins');
assert.equal(by.Cloudvore.lineNo, 4);
assert.equal(by.Cloudvore.surface, 'specs/cloudvore.md');
assert.equal(by['softwarefactory-fleet-doctrine'].surface, 'RECEIPTS.md');
assert.equal(by['softwarefactory-fleet-doctrine'].found, 1, 'receipts lines of other projects are not counted');
assert.equal(by.SilentBackgroundProcess.state, 'DISPOSITION-HOLD', 'a malformed receipts line naming no project displaces nobody');
assert.equal(by.SilentBackgroundProcess.errors.length, 0);
assert.equal(by['magic-lantern_dannephoto'].found, 0);
assert.equal(s.exit, 2, 'magic-lantern missing');
write('specs/magic-lantern_dannephoto.md', '# ML\nJEV: SHADOW-LIVE standard=r6@ad426fb qsv=NONE log=.claude-state/jev-shadow.jsonl lines=12 asOf=2026-09-20 record=magic-lantern_dannephoto:abc\n');
s = fleetStatus(bus, null);
assert.equal(s.exit, 3);
// a later malformed SBP line on RECEIPTS is attributed to SBP by its record= token and makes SBP malformed, nobody else
write('RECEIPTS.md', readFileSync(join(bus, 'RECEIPTS.md'), 'utf8') + 'JEV:\tDISPOSITION-HOLD standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=silentbackgroundprocess:x\n');
s = fleetStatus(bus, null);
assert.deepEqual(s.rows.find((row) => row.project === 'SilentBackgroundProcess').errors, ['malformed']);
assert.equal(s.rows.find((row) => row.project === 'softwarefactory-fleet-doctrine').state, 'DISPOSITION-DISTINGUISH');
// a drafted line with one trailing space is malformed AND still attributed to its project (exit 3, not a stale 0)
write('RECEIPTS.md', readFileSync(join(bus, 'RECEIPTS.md'), 'utf8') + 'JEV: DISPOSITION-HOLD standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=silentbackgroundprocess:y \n');
assert.deepEqual(fleetStatus(bus, null).rows.find((row) => row.project === 'SilentBackgroundProcess').errors, ['malformed']);
// SBP appends a fresh valid line: last line wins, the malformed ones become history
write('RECEIPTS.md', readFileSync(join(bus, 'RECEIPTS.md'), 'utf8') + 'JEV: DISPOSITION-HOLD standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=silentbackgroundprocess:reports/JEV-SHADOW-MODE-DISPOSITION-20260919.md\n');
assert.equal(fleetStatus(bus, null).rows.find((row) => row.project === 'SilentBackgroundProcess').found, 4);
assert.equal(s.rows.find((row) => row.project === 'magic-lantern_dannephoto').errors.length, 2);
write('specs/magic-lantern_dannephoto.md', '# ML\nJEV: DISPOSITION-DISTINGUISH standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-19 record=magic-lantern_dannephoto:roadmap/reviews/2026-09-19-jev-shadow-mode-disposition.md\n');
s = fleetStatus(bus, null);
assert.equal(s.exit, 0);
assert.match(table(s), /^\| Project \| State /);
assert.equal(table(s).split('\n').length, 7);

// --ref reads a git ref, not the working tree; the CLI exits with the status code and writes nothing
const git = (...a) => execFileSync('git', ['-C', bus, ...a], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
git('init', '-q');
git('-c', 'user.name=t', '-c', 'user.email=t@t', 'add', '.');
git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'fixture');
git('checkout', '-q', '-b', 'review');
write('specs/magic-lantern_dannephoto.md', '# ML\nJEV: DISPOSITION-ADOPT standard=r6@ad426fb qsv=NONE log=NONE lines=0 asOf=2026-09-20 record=magic-lantern_dannephoto:x\n');
git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-am', 'review');
write('specs/magic-lantern_dannephoto.md', 'JEV: broken\n');
assert.equal(fleetStatus(bus, 'review').rows.find((row) => row.project === 'magic-lantern_dannephoto').state, 'DISPOSITION-ADOPT');
assert.equal(fleetStatus(bus, null).exit, 3, 'working tree is broken');
const run = (args) => { try { return { out: execFileSync('node', [join(here, 'jev-adoption-status.mjs'), ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }), code: 0 }; } catch (e) { return { out: e.stdout, code: e.status }; } };
assert.equal(run(['--bus', bus]).code, 3);
const j = run(['--bus', bus, '--ref', 'review', '--json']);
assert.equal(j.code, 0);
assert.equal(JSON.parse(j.out).ref, 'review');
assert.equal(run(['--bus', bus, '--frobnicate']).code, 4);
assert.equal(run(['--bus', bus, '--ref']).code, 4, 'a --ref with no value is refused, not the working tree');
assert.equal(run(['--bus', bus, '--ref', '--frobnicate', '--ref', 'review']).code, 4, 'a flag is never consumed as a value');
assert.equal(run(['--bus', bus, '--ref', '']).code, 4, 'an empty value is no value');
assert.equal(run(['--bus', root]).code, 4, 'no standard -> 4');
assert.equal(git('status', '--porcelain').trim(), 'M specs/magic-lantern_dannephoto.md', 'the checker wrote nothing');

rmSync(root, { recursive: true, force: true });
const count = (readFileSync(fileURLToPath(import.meta.url), 'utf8').match(/^\s*assert\.\w+\(/gm) || []).length;
console.log(`jev-adoption-status: ${count} assertions passed`);
