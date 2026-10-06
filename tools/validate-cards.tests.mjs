#!/usr/bin/env node
// R14 packet 2 fixtures for tools/validate-cards.mjs. Runs the shipped module and the shipped CLI
// against temporary bus checkouts; touches nothing in this repository.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { MAX_CARD_BYTES, parseCardsFile } from './validate-cards.mjs';

const repo = fileURLToPath(new URL('..', import.meta.url));
const tool = fileURLToPath(new URL('./validate-cards.mjs', import.meta.url));
const root = mkdtempSync(join(tmpdir(), 'validate-cards-'));
const members = ['adobe-ingester', 'cloudvore', 'mlv-app'];
const cli = (args) => {
  try { return { status: 0, out: execFileSync(process.execPath, [tool, ...args], { encoding: 'utf8', timeout: 20000, stdio: ['ignore', 'pipe', 'pipe'] }) }; }
  catch (e) { return { status: e.status, out: `${e.stdout || ''}${e.stderr || ''}` }; }
};
const card = (id, extra = [], omit = []) => [
  `## ${id}`,
  ...[['rule', 'the rule'], ['mechanism', 'the mechanism'], ['check', 'node tools/x.mjs'], ['supersedes', 'none'], ['evidence', 'measured']]
    .filter(([k]) => !omit.includes(k)).map(([k, v]) => `${k}: ${v}`),
  ...extra,
].join('\n');
const reasons = (r) => r.errors.map((e) => e.reason).join(' | ');
let cases = 0;

try {
  // A 15-line card with all fields passes; absent `applies` reads as every board.
  const fifteen = ['## cloudvore/a', 'rule: the rule', ...Array.from({ length: 9 }, (_, i) => `  continuation ${i}`),
    'mechanism: m', 'check: node tools/x.mjs', 'supersedes: none', 'evidence: measured'].join('\n');
  assert.equal(fifteen.split('\n').length, 15);
  let r = parseCardsFile(fifteen + '\n', 'cloudvore', members);
  assert.deepEqual(r.errors, []); assert.equal(r.cards.length, 1); assert.equal(r.cards[0].applies, null); assert.equal(r.cards[0].lines, 15); cases++;
  // Trailing blank lines are not counted; a 16th real line is.
  r = parseCardsFile(fifteen + '\n\n\n\n', 'cloudvore', members); assert.deepEqual(r.errors, []); cases++;
  r = parseCardsFile(fifteen + '\n  one more\n', 'cloudvore', members); assert.match(reasons(r), /16 lines; the limit is 15/); cases++;
  // Byte cap.
  r = parseCardsFile(card('cloudvore/b', [`  ${'x'.repeat(MAX_CARD_BYTES)}`]), 'cloudvore', members); assert.match(reasons(r), /bytes; the limit is 2000/); cases++;
  // Each required field is required.
  for (const f of ['rule', 'mechanism', 'check', 'supersedes', 'evidence']) {
    r = parseCardsFile(card('cloudvore/c', [], [f]), 'cloudvore', members); assert.match(reasons(r), new RegExp(`missing field '${f}'`)); cases++;
  }
  // evidence is closed; applies must name members; unknown and repeated fields are refused.
  r = parseCardsFile(card('cloudvore/d', [], ['evidence']) + '\nevidence: anecdotal', 'cloudvore', members); assert.match(reasons(r), /evidence must be 'measured' or 'reported'/); cases++;
  r = parseCardsFile(card('cloudvore/e', ['applies: mlv-app, nobody']), 'cloudvore', members); assert.match(reasons(r), /'nobody', which is not a fleet member/); cases++;
  r = parseCardsFile(card('cloudvore/e2', ['applies: mlv-app,adobe-ingester']), 'cloudvore', members); assert.deepEqual(r.errors, []); assert.deepEqual(r.cards[0].applies, ['adobe-ingester', 'mlv-app']); cases++;
  r = parseCardsFile(card('cloudvore/f', ['test: typo for check']), 'cloudvore', members); assert.match(reasons(r), /unknown field 'test'/); cases++;
  r = parseCardsFile(card('cloudvore/g', ['rule: again']), 'cloudvore', members); assert.match(reasons(r), /'rule' appears twice/); cases++;
  r = parseCardsFile(card('cloudvore/h', ['', '  dangling continuation']), 'cloudvore', members); assert.match(reasons(r), /continuation line with no field/); cases++;
  // Duplicate id; a card in another project's file; a malformed heading.
  r = parseCardsFile(`${card('cloudvore/x')}\n\n${card('cloudvore/x')}\n`, 'cloudvore', members); assert.match(reasons(r), /duplicate card id \(first at line 1\)/); cases++;
  r = parseCardsFile(card('mlv-app/x'), 'cloudvore', members); assert.match(reasons(r), /names project 'mlv-app' but sits in specs\/cloudvore\/cards.md/); cases++;
  r = parseCardsFile(card('no slash here'), 'cloudvore', members); assert.match(reasons(r), /card heading must be/); cases++;
  // A file for a project that is not a fleet member.
  r = parseCardsFile(card('ghost/a'), 'ghost', members); assert.match(reasons(r), /'ghost' is not a fleet member/); cases++;
  // no-card lines (R14.4): accepted with an index id and a reason, refused otherwise; they close a card.
  r = parseCardsFile(`# title\nprose\n\n${card('cloudvore/n')}\nno-card: T12 superseded by cloudvore/n\nno-card: T13\nno-card: 13 reason\n`, 'cloudvore', members);
  assert.equal(r.noCards.length, 1); assert.equal(r.noCards[0].indexId, 'T12'); assert.equal(r.cards[0].line, 4); assert.equal(r.cards[0].endLine, 9);
  assert.match(reasons(r), /no-card T13 has no reason/); assert.match(reasons(r), /must read "no-card: T<line> <reason>"/); cases++;
  // CRLF is read as LF.
  r = parseCardsFile(card('cloudvore/crlf').replace(/\n/g, '\r\n') + '\r\n', 'cloudvore', members); assert.deepEqual(r.errors, []); cases++;
  // A "# " line after the first card is refused.
  r = parseCardsFile(`${card('cloudvore/p')}\nno-card: T1 r\n# Another filing\n`, 'cloudvore', members); assert.match(reasons(r), /"# " heading after the first card/); cases++;

  // The bold-bullet spelling of the same six fields (case-insensitive labels) is accepted.
  const bold = (id, extra = [], omit = []) => [
    `## ${id}`,
    ...[['Rule', 'the rule'], ['Mechanism', 'the mechanism'], ['Applies to', 'mlv-app'], ['Check', 'node tools/x.mjs'], ['Supersedes', 'none'], ['Evidence', 'measured']]
      .filter(([k]) => !omit.includes(k)).map(([k, v]) => `- **${k}:** ${v}`),
    ...extra,
  ].join('\n');
  r = parseCardsFile(bold('cloudvore/b1'), 'cloudvore', members);
  assert.deepEqual(r.errors, []); assert.deepEqual(r.cards[0].applies, ['mlv-app']); assert.equal(r.cards[0].fields.evidence, 'measured'); cases++;
  r = parseCardsFile(bold('cloudvore/b2').replace('**Rule:**', '**RULE:**').replace('**Applies to:**', '**applies TO:**'), 'cloudvore', members); assert.deepEqual(r.errors, []); cases++;
  // The same fields stay required, evidence stays closed, a field in both spellings is a repeat.
  for (const f of ['Rule', 'Mechanism', 'Check', 'Supersedes', 'Evidence']) {
    r = parseCardsFile(bold('cloudvore/b3', [], [f]), 'cloudvore', members); assert.match(reasons(r), new RegExp(`missing field '${f.toLowerCase()}'`)); cases++;
  }
  r = parseCardsFile(bold('cloudvore/b4', [], ['Evidence']) + '\n- **Evidence:** dng ledger T1F1/attempt1', 'cloudvore', members); assert.match(reasons(r), /evidence must be 'measured' or 'reported'/); cases++;
  r = parseCardsFile(bold('cloudvore/b5', ['rule: again']), 'cloudvore', members); assert.match(reasons(r), /'rule' appears twice/); cases++;
  // Other bold labels are extra lines: they satisfy nothing and count toward the limits.
  r = parseCardsFile(bold('cloudvore/b6', ['- **Falsifier:** remove the drop; the pin goes red', '  continued', '- **Measured:** 3 of 3']), 'cloudvore', members);
  assert.deepEqual(r.errors, []); assert.equal(r.cards[0].lines, 10); assert.equal(r.cards[0].fields.rule, 'the rule'); cases++;
  r = parseCardsFile(bold('cloudvore/b7', Array.from({ length: 9 }, (_, i) => `- **Where ${i}:** x`)), 'cloudvore', members); assert.match(reasons(r), /16 lines; the limit is 15/); cases++;
  r = parseCardsFile(bold('cloudvore/b8', [], ['Rule']) + '\n- **Rule candidate:** not the rule', 'cloudvore', members); assert.match(reasons(r), /missing field 'rule'/); cases++;
  // A bold label within two edits of a field label is refused, so a typo cannot widen `applies`.
  r = parseCardsFile(bold('cloudvore/b9', [], ['Applies to']) + '\n- **Aplies to:** mlv-app', 'cloudvore', members); assert.match(reasons(r), /'Aplies to' is not a field but is close to 'applies to'/); cases++;
  // A non-field line names both spellings and the example file.
  r = parseCardsFile(card('cloudvore/b10', ['**Rule** no colon']), 'cloudvore', members);
  assert.match(reasons(r), /card fields are "<name>: <value>" or "- \*\*<Name>:\*\* <value>"; see examples\/cards-v1\.md/); cases++;
  // Card-like preamble is diagnosed, never silently accepted as prose.
  r = parseCardsFile('### TRAP 2026-10-06 (adobe-ingester): invalid card\nevidence: maybe\n', 'adobe-ingester', members);
  assert.ok(r.errors.length >= 1); assert.equal(r.cards.length, 0); assert.match(reasons(r), /card-like text outside a card heading; a card starts with `## <project>\/<id>`/);
  assert.deepEqual(r.errors.map((e) => e.line), [1, 2]); cases++;
  r = parseCardsFile(`# title\n- **Rule:** stray\n\n${card('cloudvore/b11')}\n`, 'cloudvore', members); assert.deepEqual(r.errors.map((e) => e.line), [2]); cases++;
  r = parseCardsFile(`# title\nprose that says rule: in the middle\n- **Note:** prose\n\n${card('cloudvore/b12')}\n`, 'cloudvore', members); assert.deepEqual(r.errors, []); cases++;

  // The CLI, against a temporary bus.
  const bus = join(root, 'bus');
  mkdirSync(join(bus, 'specs', 'cloudvore'), { recursive: true });
  writeFileSync(join(bus, 'RULINGS.md'), 'rulings\n');
  for (const m of members) writeFileSync(join(bus, 'specs', `${m}.md`), `# ${m}\n`);
  writeFileSync(join(bus, 'specs', 'fleet-kernel.md'), '# not a member\n');
  let c = cli(['--bus', bus]); assert.equal(c.status, 0); assert.match(c.out, /0 file\(s\), 0 card\(s\)/); cases++;
  writeFileSync(join(bus, 'specs', 'cloudvore', 'cards.md'), `${card('cloudvore/ok')}\n\n${card('cloudvore/bad', [], ['check'])}\n`);
  const before = createHash('sha256').update(readFileSync(join(bus, 'specs', 'cloudvore', 'cards.md'))).digest('hex');
  c = cli(['--bus', bus]); assert.equal(c.status, 1);
  assert.match(c.out, /^INVALID specs\/cloudvore\/cards\.md:8 \[cloudvore\/bad\] missing field 'check'$/m); assert.match(c.out, /2 card\(s\), 0 no-card line\(s\), 1 problem/); cases++;
  assert.equal(createHash('sha256').update(readFileSync(join(bus, 'specs', 'cloudvore', 'cards.md'))).digest('hex'), before, 'validator never touches a file'); cases++;
  mkdirSync(join(bus, 'specs', 'fleet-kernel')); writeFileSync(join(bus, 'specs', 'fleet-kernel', 'cards.md'), card('fleet-kernel/a'));
  c = cli(['--bus', bus]); assert.match(c.out, /specs\/fleet-kernel\/cards\.md:0 'fleet-kernel' is not a fleet member/); cases++;
  c = cli(['--bus', join(root, 'nowhere')]); assert.equal(c.status, 2); cases++;
  c = cli(['--bus', bus, '--file', join(bus, 'specs', 'cloudvore', 'cards.md')]); assert.equal(c.status, 2, '--file without --project'); cases++;

  // The shipped example validates, using this repository's own roster.
  c = cli(['--file', join(repo, 'examples', 'cards-v1.md'), '--project', 'adobe-ingester']);
  assert.equal(c.status, 0, c.out); assert.match(c.out, /2 card\(s\), 1 no-card line\(s\), 0 problem/); cases++;
  // And this repository's own card files (none, or all valid) pass.
  c = cli([]); assert.equal(c.status, 0, c.out); cases++;
  console.log(`validate-cards fixtures: ${cases} cases passed`);
} finally {
  rmSync(root, { recursive: true, force: true });
}
