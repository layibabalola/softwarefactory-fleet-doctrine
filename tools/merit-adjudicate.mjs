#!/usr/bin/env node
// merit-adjudicate — settle a rival-claim question with an instrument instead of a discussion.
//
// Owner ruling, 2026-08-30: "Lets rule based on merit ALWAYS." A rule that says so and stops
// there is a slogan; every board still rules on whoever argued last. This is the instrument that
// makes the rule operable: a declarative rubric, a probe per candidate per criterion, and a
// scorecard any member can re-run and get the same answer.
//
// Three properties are deliberate, and each is a guard against a way merit-talk goes fake:
//
//   1. THE RUBRIC IS WRITTEN FROM INCIDENTS, NOT FROM FEATURE LISTS. Every criterion carries an
//      `incident` string. A criterion nobody was hurt by is a preference wearing a lab coat.
//   2. ANTI-GERRYMANDERING. If the proposing party's own candidate is expected to pass every
//      criterion, the run REFUSES. A rubric written backwards from what you already built is the
//      normal way an author wins on merit without merit.
//   3. NO SILENT UNMEASURED. A candidate with no probe for a criterion scores UNMEASURED and is
//      printed as such. It never scores PASS by absence, and it never disappears from the table.
//
// Authors do not score their own candidate. They may RUN this and publish the receipt: the
// instrument is the thing being trusted, and it is re-runnable by anyone who doubts the result.
//
// Usage
//   node tools/merit-adjudicate.mjs --criteria adjudications/<slug>.json [--out <dir>] [--json]
//
// Exit 0 = scorecard produced. 1 = rubric refused (gerrymandered / malformed). 2 = tool failure.

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const EXIT_OK = 0, EXIT_REFUSED = 1, EXIT_FAIL = 2;
const VERDICTS = { PASS: 'PASS', FAIL: 'FAIL', UNMEASURED: 'UNMEASURED' };

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) out[a.slice(2)] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
    else out._.push(a);
  }
  return out;
}

function fail(msg) { console.error(`[merit] ${msg}`); process.exit(EXIT_FAIL); }
function refuse(msg) { console.error(`[merit] REFUSED — ${msg}`); process.exit(EXIT_REFUSED); }

function validate(rubric) {
  for (const k of ['question', 'proposedBy', 'candidates', 'criteria']) {
    if (!rubric[k]) refuse(`rubric is missing required field '${k}'.`);
  }
  if (!Array.isArray(rubric.candidates) || rubric.candidates.length < 2) {
    refuse('a merit adjudication needs at least two candidates. One candidate is a decision, not an adjudication.');
  }
  for (const c of rubric.criteria) {
    for (const k of ['id', 'statement', 'incident', 'weight']) {
      if (!c[k]) refuse(`criterion ${c.id || '<no id>'} is missing '${k}'. Every criterion names the incident that bought it.`);
    }
    if (!['MUST', 'SHOULD'].includes(c.weight)) refuse(`criterion ${c.id} has weight '${c.weight}'; use MUST or SHOULD.`);
  }
}

// Guard 2: the proposing party must have declared at least one criterion its own candidate is
// expected to fail. Checked against DECLARED expectations, before anything runs, so the refusal
// cannot be dodged by tuning probes after seeing results.
function guardGerrymander(rubric) {
  const own = rubric.candidates.filter((c) => c.owner === rubric.proposedBy).map((c) => c.id);
  if (!own.length) return { checked: false, reason: 'proposer owns no candidate here; guard not applicable.' };
  const selfFails = rubric.criteria.filter((c) => own.some((id) => c.probes?.[id]?.expectFail === true));
  if (!selfFails.length) {
    refuse([
      `every criterion is expected to PASS for the proposer's own candidate(s): ${own.join(', ')}.`,
      'A rubric written backwards from what you already built is how an author wins on merit without merit.',
      'Declare at least one criterion your candidate fails, with `"expectFail": true` on its probe,',
      'or hand the rubric to a party that owns none of the candidates.',
    ].join('\n         '));
  }
  return { checked: true, selfDeclaredFailures: selfFails.map((c) => c.id) };
}

function runProbe(probe, cwd) {
  const r = spawnSync(probe.cmd, probe.args || [], { cwd, encoding: 'utf8', timeout: probe.timeoutMs || 60000, shell: false });
  if (r.error) return { ok: false, exitCode: null, out: String(r.error.message), note: 'probe could not be executed' };
  const out = `${r.stdout || ''}${r.stderr || ''}`;
  return { ok: true, exitCode: r.status, out };
}

function judge(probe, result) {
  if (!result.ok) return { verdict: VERDICTS.UNMEASURED, why: result.note };
  const checks = [];
  if (probe.expect?.exitCode !== undefined) {
    checks.push({ what: `exit ${probe.expect.exitCode}`, ok: result.exitCode === probe.expect.exitCode, got: `exit ${result.exitCode}` });
  }
  if (probe.expect?.stdoutMatches) {
    const re = new RegExp(probe.expect.stdoutMatches);
    checks.push({ what: `output ~ /${probe.expect.stdoutMatches}/`, ok: re.test(result.out), got: re.test(result.out) ? 'matched' : 'no match' });
  }
  if (probe.expect?.stdoutAbsent) {
    const re = new RegExp(probe.expect.stdoutAbsent);
    checks.push({ what: `output NOT ~ /${probe.expect.stdoutAbsent}/`, ok: !re.test(result.out), got: re.test(result.out) ? 'present' : 'absent' });
  }
  if (!checks.length) return { verdict: VERDICTS.UNMEASURED, why: 'probe declares no expectation; an assertion-free probe cannot fail, so it proves nothing' };
  const passed = checks.every((c) => c.ok);
  return { verdict: passed ? VERDICTS.PASS : VERDICTS.FAIL, why: checks.map((c) => `${c.what} => ${c.got}`).join('; ') };
}

function scorecard(rubric, rows, guard, stampUtc) {
  const ids = rubric.candidates.map((c) => c.id);
  const tally = Object.fromEntries(ids.map((id) => [id, { mustPass: 0, mustFail: 0, shouldPass: 0, shouldFail: 0, unmeasured: 0 }]));
  for (const r of rows) {
    for (const id of ids) {
      const v = r.results[id].verdict, t = tally[id];
      if (v === VERDICTS.UNMEASURED) t.unmeasured++;
      else if (r.weight === 'MUST') (v === VERDICTS.PASS ? t.mustPass++ : t.mustFail++);
      else (v === VERDICTS.PASS ? t.shouldPass++ : t.shouldFail++);
    }
  }
  const L = [];
  L.push(`# Merit adjudication — ${rubric.question}`);
  L.push('');
  L.push(`Run ${stampUtc}. Rubric \`${rubric.slug || rubric.question}\`, proposed by \`${rubric.proposedBy}\`.`);
  L.push('Re-run this yourself: `node tools/merit-adjudicate.mjs --criteria <this rubric>`. A ruling with');
  L.push('no re-runnable evidence is an opinion with a timestamp.');
  L.push('');
  if (guard.checked) {
    L.push(`Anti-gerrymandering guard: PASSED — the proposer declared its own candidate failing ${guard.selfDeclaredFailures.join(', ')}.`);
  } else {
    L.push(`Anti-gerrymandering guard: not applicable — ${guard.reason}`);
  }
  L.push('');
  L.push(`| Criterion | Weight | Incident | ${ids.join(' | ')} |`);
  L.push(`|---|---|---|${ids.map(() => '---').join('|')}|`);
  for (const r of rows) {
    L.push(`| **${r.id}** ${r.statement} | ${r.weight} | ${r.incident} | ${ids.map((id) => r.results[id].verdict).join(' | ')} |`);
  }
  L.push('');
  L.push('| Candidate | MUST pass | MUST fail | SHOULD pass | SHOULD fail | UNMEASURED |');
  L.push('|---|---:|---:|---:|---:|---:|');
  for (const id of ids) {
    const t = tally[id];
    L.push(`| \`${id}\` | ${t.mustPass} | ${t.mustFail} | ${t.shouldPass} | ${t.shouldFail} | ${t.unmeasured} |`);
  }
  L.push('');
  const clean = ids.filter((id) => tally[id].mustFail === 0 && tally[id].unmeasured === 0);
  if (clean.length === 1) {
    L.push(`**Zero MUST failures and nothing unmeasured: \`${clean[0]}\`.** That is the measurement, not the ruling —`);
    L.push('a seat that owns none of the candidates still has to rule, and merit is per-property: record what');
    L.push('survives from the losing candidate rather than discarding the artifact whole.');
  } else if (clean.length > 1) {
    L.push(`**${clean.length} candidates carry zero MUST failures: ${clean.map((c) => `\`${c}\``).join(', ')}.**`);
    L.push('A tie on MUST is broken by the property every box actually has — runtime availability,');
    L.push('installability, and blast radius — never by which is more featureful.');
  } else {
    L.push('**No candidate is clean on MUST.** The honest outcome is a remediation order against the');
    L.push('best-placed candidate, not a winner.');
  }
  L.push('');
  L.push('Verdict legend: UNMEASURED means no probe was declared. It never counts as PASS —');
  L.push('a criterion nobody measured is a criterion nobody met.');
  return L.join('\n');
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.criteria) fail('usage: merit-adjudicate.mjs --criteria <rubric.json> [--out <dir>] [--json]');
  const rubricPath = resolve(String(args.criteria));
  if (!existsSync(rubricPath)) fail(`rubric not found: ${rubricPath}`);

  let rubric;
  try { rubric = JSON.parse(readFileSync(rubricPath, 'utf8')); } catch (e) { fail(`rubric is not valid JSON: ${e.message}`); }
  validate(rubric);
  const guard = guardGerrymander(rubric);

  const cwd = rubric.cwd ? resolve(rubric.cwd) : process.cwd();
  const rows = [];
  for (const c of rubric.criteria) {
    const results = {};
    for (const cand of rubric.candidates) {
      const probe = c.probes?.[cand.id];
      if (!probe) { results[cand.id] = { verdict: VERDICTS.UNMEASURED, why: 'no probe declared for this candidate' }; continue; }
      const raw = runProbe(probe, cwd);
      const j = judge(probe, raw);
      // A probe may declare it EXPECTS to fail; that is a declaration of honesty, not a pass.
      results[cand.id] = { ...j, expectedFail: probe.expectFail === true, exitCode: raw.exitCode, evidence: (raw.out || '').split('\n').slice(0, 6).join('\n') };
    }
    rows.push({ id: c.id, statement: c.statement, weight: c.weight, incident: c.incident, results });
  }

  const stampUtc = new Date().toISOString();
  const md = scorecard(rubric, rows, guard, stampUtc);
  const outDir = resolve(String(args.out || join(cwd, 'adjudications')));
  mkdirSync(outDir, { recursive: true });
  const slug = rubric.slug || 'adjudication';
  writeFileSync(join(outDir, `${slug}.scorecard.md`), md + '\n');
  writeFileSync(join(outDir, `${slug}.receipt.json`), JSON.stringify({ rubric: rubric.slug, question: rubric.question, ranUtc: stampUtc, guard, rows }, null, 2) + '\n');
  console.log(md);
  console.log(`\n[merit] scorecard -> ${join(outDir, `${slug}.scorecard.md`)}`);
  console.log(`[merit] receipt   -> ${join(outDir, `${slug}.receipt.json`)}`);
  return EXIT_OK;
}

try { process.exit(main()); }
catch (err) { fail(err.message); }
