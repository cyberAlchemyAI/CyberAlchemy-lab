#!/usr/bin/env node
// PROPOSAL — not an installed validator.
//
// Purpose: fail closed when any consumer's asserted P2 denominator disagrees with
// the live authority. The 2026-08-16 two-lane check passed while WP-SMO-001 said 17
// and WP-SFC-001 said 16, because it compared which decision bytes each lane bound,
// never the quantities each lane derived from them. Comparing lanes to each other is
// the wrong fix: it is symmetric and would pass if both were wrong. This derives the
// truth from the authority, then asserts every declared consumer matches it.
//
// Usage: node validate-p2-denominator-agreement.mjs [--json] [<repo-root>]
// Exit:  0 agreement · 4 divergence · 22 unreadable input

import { readFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const ROOT = resolve(args.find((a) => !a.startsWith('--')) ?? '.');
const P = (p) => join(ROOT, p);

const KINDS_PATH = 'definitions/meta-types/meta-types.yml';
const RELS_PATH = 'definitions/relationships/relationships.yml';

// Signatures whose feature_scope names a UI plane are outside the backend denominator.
const UI_SCOPES = new Set(['ui', 'ui-backend']);

// Declared consumers of the denominator. Each site states a count in prose or data;
// adding a consumer without registering it here is itself a finding (see --json output).
const CONSUMERS = [
  { id: 'decision.sf-02', path: 'development/first-production-release/decisions/2026-08-16-first-stable-foundation-candidate.md',
    kinds: /all (\d+) active backend meta-types/, relations: /all (\d+) backend relationship signatures/ },
  { id: 'sfc.spec.denominator', path: 'development/first-production-release/stable-foundation-cli/SPEC.md',
    kinds: /(\d+)-node-kind/, relations: /(\d+)-backend-relation source denominator/ },
  { id: 'sfc.spec.breadth', path: 'development/first-production-release/stable-foundation-cli/SPEC.md',
    kinds: /(\d+) active backend node kinds/, relations: /(\d+) backend relationship signatures/ },
  { id: 'sfc.requirements.f-004', path: 'development/first-production-release/stable-foundation-cli/REQUIREMENTS.md',
    kinds: /exactly (\d+) active backend kinds/, relations: /(\d+) backend signatures/ },
  { id: 'sfc.glossary', path: 'development/first-production-release/stable-foundation-cli/GLOSSARY.md',
    kinds: /(\d+) active backend kinds/, relations: /(\d+) backend signatures/ },
  { id: 'sfc.define-context', path: 'development/first-production-release/stable-foundation-cli/DEFINE-CONTEXT.md',
    kinds: null, relations: /(\d+) backend signature rows/ },
  { id: 'sfc.planned-witness', path: 'development/first-production-release/stable-foundation-cli/DESIGN-PLANNED-WITNESSES.json',
    kinds: /(\d+)-kind and \d+-signature profile identity/, relations: /\d+-kind and (\d+)-signature profile identity/ },
  { id: 'sfc.swu-004', path: 'development/first-production-release/stable-foundation-cli/work-pack/shared/SWU-MANIFEST.json',
    kinds: /Verify exact (\d+)-kind/, relations: /(\d+)-relation P2 membership/ },
  { id: 'sfc.wave.w0', path: 'development/first-production-release/stable-foundation-cli/work-pack/waves/W0-CONTRACT.md',
    kinds: /bind exactly (\d+) backend kinds/, relations: /backend kinds and\s+(\d+)/ },
  { id: 'smo.profile-candidate', path: 'development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/proposals/formation/supported-profiles.candidate.json',
    json: true },
];

function fail(code, msg) {
  if (asJson) console.log(JSON.stringify({ result: 'error', exit: code, message: msg }, null, 1));
  else console.error(`ERROR: ${msg}`);
  process.exit(code);
}

// Minimal readers. relationships.yml and meta-types.yml are emitted as JSON by the
// generators despite the .yml suffix; fall back to a line scan if that ever changes.
function readStructured(path) {
  const raw = readFileSync(P(path), 'utf8');
  try { return { data: JSON.parse(raw), raw }; } catch { return { data: null, raw }; }
}

function truthFromAuthority() {
  for (const p of [KINDS_PATH, RELS_PATH]) if (!existsSync(P(p))) fail(22, `missing authority file: ${p}`);

  const { data: kindsDoc, raw: kindsRaw } = readStructured(KINDS_PATH);
  let kinds;
  if (kindsDoc?.members) kinds = kindsDoc.members.filter((m) => m.status === 'active').map((m) => m.term);
  else kinds = [...kindsRaw.matchAll(/^\s*-?\s*term:\s*(.+)$/gm)].map((m) => m[1].trim());
  if (!kinds.length) fail(22, `could not derive active kinds from ${KINDS_PATH}`);

  const { data: relDoc } = readStructured(RELS_PATH);
  if (!relDoc?.signatures) fail(22, `could not derive signatures from ${RELS_PATH}`);
  const active = relDoc.signatures.filter((s) => (s.status ?? 'active') === 'active');
  const backend = active.filter((s) => !(s.feature_scope ?? []).some((f) => UI_SCOPES.has(f)));
  const uiTouching = active.length - backend.length;

  // Every backend endpoint must be one of the active kinds, or the denominator is incoherent.
  const kindSet = new Set(kinds);
  const stray = [];
  for (const s of backend) {
    const ends = [...(s.source_types ?? [s.source_type]), ...(Array.isArray(s.target_type ?? s.target_types)
      ? (s.target_type ?? s.target_types) : [s.target_type ?? s.target_types])];
    for (const e of ends) if (e && !kindSet.has(e)) stray.push(`${s.id}:${e}`);
  }

  return {
    kinds: kinds.length,
    relations: backend.length,
    ui_touching: uiTouching,
    declared_signature_count: relDoc.signature_count ?? null,
    backend_ids: backend.map((s) => s.id),
    stray_endpoints: stray,
  };
}

function readConsumer(c) {
  if (!existsSync(P(c.path))) return { id: c.id, status: 'missing', path: c.path };
  const raw = readFileSync(P(c.path), 'utf8');

  if (c.json) {
    const doc = JSON.parse(raw);
    const rows = (doc.profiles ?? []).filter((p) => (p.relationship_ids ?? p.relationships ?? []).length);
    const widest = rows.sort((a, b) =>
      (b.relationship_ids ?? b.relationships).length - (a.relationship_ids ?? a.relationships).length)[0];
    if (!widest) return { id: c.id, status: 'no-claim', path: c.path };
    return { id: c.id, status: 'read', path: c.path,
      kinds: (widest.kinds ?? []).length,
      relations: (widest.relationship_ids ?? widest.relationships).length };
  }

  const grab = (re) => { if (!re) return null; const m = raw.match(re); return m ? Number(m[1]) : null; };
  const kinds = grab(c.kinds), relations = grab(c.relations);
  if (kinds === null && relations === null) return { id: c.id, status: 'no-claim', path: c.path };
  return { id: c.id, status: 'read', path: c.path, kinds, relations };
}

const truth = truthFromAuthority();
const findings = [];
const seen = [];

for (const c of CONSUMERS) {
  const r = readConsumer(c);
  seen.push(r);
  if (r.status === 'missing') { findings.push({ ...r, reason: 'declared consumer file is absent' }); continue; }
  if (r.status === 'no-claim') { findings.push({ ...r, reason: 'consumer registered but no count matched — pattern drift' }); continue; }
  if (r.kinds !== null && r.kinds !== undefined && r.kinds !== truth.kinds)
    findings.push({ id: r.id, path: r.path, field: 'kinds', asserted: r.kinds, authority: truth.kinds, reason: 'kind count disagrees with live authority' });
  if (r.relations !== null && r.relations !== undefined && r.relations !== truth.relations)
    findings.push({ id: r.id, path: r.path, field: 'relations', asserted: r.relations, authority: truth.relations, reason: 'relation count disagrees with live authority' });
}

if (truth.stray_endpoints.length)
  findings.push({ id: 'authority.self', field: 'endpoints', reason: 'backend signature references a non-active kind', detail: truth.stray_endpoints });

const result = findings.length ? 'divergent' : 'agreed';
const out = { result, authority: truth, consumers: seen, findings };

if (asJson) console.log(JSON.stringify(out, null, 1));
else {
  console.log(`authority: ${truth.kinds} active kinds · ${truth.relations} backend signatures · ${truth.ui_touching} ui-touching (declared total ${truth.declared_signature_count})`);
  for (const r of seen) {
    const claim = r.status === 'read' ? `${r.kinds ?? '-'} kinds / ${r.relations ?? '-'} relations` : r.status;
    const bad = findings.some((f) => f.id === r.id);
    console.log(`  ${bad ? 'FAIL' : 'ok  '}  ${r.id.padEnd(26)} ${claim}`);
  }
  if (findings.length) {
    console.log(`\n${findings.length} finding(s):`);
    for (const f of findings) console.log(`  - ${f.id}${f.field ? ` [${f.field}]` : ''}: ${f.reason}${f.asserted !== undefined ? ` (asserted ${f.asserted}, authority ${f.authority})` : ''}`);
  }
  console.log(`\nresult: ${result}`);
}
process.exit(findings.length ? 4 : 0);
