#!/usr/bin/env node
// product-control-ratio.mjs - read-only, portable. Measures how much of a repository's recent work
// touched product paths versus factory/control paths, so a board can see "control churn, zero product".
// It writes nothing; it only runs `git log`.
//
// usage:
//   node product-control-ratio.mjs --repo <path> --product spikes,src --control .factory,.claude-state
//        [--hours 48] [--all] [--json]
// exit: 0 = product moved in the window (or no control churn); 3 = control churn with zero product
//       commits (a STALL signal, never a gate); 1 = usage or git error.
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

function args(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      out[k] = v;
    } else out._.push(a);
  }
  return out;
}

function git(repo, list) {
  return execFileSync('git', ['-C', repo, ...list], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
}

function count(repo, since, all, paths) {
  if (!paths.length) return 0;
  const base = ['log', '--since', since, '--pretty=format:%H'];
  if (all) base.push('--all');
  const text = git(repo, [...base, '--', ...paths]);
  return text.split('\n').filter(Boolean).length;
}

function last(repo, paths) {
  if (!paths.length) return null;
  const text = git(repo, ['log', '--all', '-1', '--pretty=format:%h %cI %s', '--', ...paths]).trim();
  return text || null;
}

function main() {
  const a = args(process.argv.slice(2));
  const repo = a.repo ? resolve(String(a.repo)) : null;
  const split = (v) => (typeof v === 'string' ? v.split(',').map((s) => s.trim()).filter(Boolean) : []);
  const product = split(a.product);
  const control = split(a.control);
  const hours = Number(a.hours || 48);
  if (!repo || !existsSync(join(repo, '.git')) || !product.length || !control.length || !(hours > 0)) {
    console.error('usage: product-control-ratio.mjs --repo <git repo> --product <p1,p2> --control <c1,c2> [--hours N] [--all] [--json]');
    return 1;
  }
  const since = `${hours} hours ago`;
  const productCommits = count(repo, since, !!a.all, product);
  const controlCommits = count(repo, since, !!a.all, control);
  const result = {
    schema: 'product-control-ratio/v1',
    measured_utc: new Date().toISOString(),
    repo,
    window_hours: hours,
    all_refs: !!a.all,
    product_paths: product,
    control_paths: control,
    product_commits: productCommits,
    control_commits: controlCommits,
    last_product_commit: last(repo, product),
    verdict: productCommits === 0 && controlCommits > 0 ? 'STALL_CONTROL_ONLY' : 'OK',
  };
  if (a.json) console.log(JSON.stringify(result));
  else console.log(`[product-control-ratio] ${hours}h: product ${productCommits}, control ${controlCommits}, verdict ${result.verdict}; last product: ${result.last_product_commit ?? 'none'}`);
  return result.verdict === 'STALL_CONTROL_ONLY' ? 3 : 0;
}

try { process.exit(main()); } catch (e) { console.error(`[product-control-ratio] ${e.message}`); process.exit(1); }
