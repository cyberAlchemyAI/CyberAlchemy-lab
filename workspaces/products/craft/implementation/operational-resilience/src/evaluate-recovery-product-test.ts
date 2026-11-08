import { createHash } from 'node:crypto';
import { EVIDENCE_STATES, type BoundReference, type EvidenceState } from '../contracts/operational-evidence.js';
import { RECOVERY_IDS, RECOVERY_ROLES, recoveryBundleSchema, recoveryScenarioSchema, type Schema, type RecoveryBundle, type RecoveryReceipt } from '../contracts/recovery-product-test.js';

export const canonicalRecoveryJson = (value: unknown): string => {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalRecoveryJson).join(',')}]`;
  const o = value as Record<string, unknown>;
  return `{${Object.keys(o).sort().map(k => `${JSON.stringify(k)}:${canonicalRecoveryJson(o[k])}`).join(',')}}`;
};
export const recoverySha256 = (text: string): string => createHash('sha256').update(text, 'utf8').digest('hex');
export const recoveryInvalidationDigest = (references: Record<string, BoundReference>): string => recoverySha256(canonicalRecoveryJson(Object.keys(references).sort().map(role => ({ role, ...references[role] }))));
export const recoveryBindingDigest = (binding: unknown): string => recoverySha256(canonicalRecoveryJson(binding));

// Parse exact JSON text, rejecting escaped duplicate names before interpreting evidence.
export function parseRecoveryJson(text: string): unknown {
  if (text.length > 16_000_000) throw new Error('JSON input exceeds local byte budget');
  const result: unknown = JSON.parse(text);
  const tokens = text.match(/"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null|[{}\[\]:,]/g)!;
  let at = 0;
  function walk(depth: number): void {
    if (depth > 100) throw new Error('JSON nesting exceeds local limit');
    const t = tokens[at++];
    if (t === '{') {
      const keys = new Set<string>();
      while (tokens[at] !== '}') {
        const k = JSON.parse(tokens[at++]) as string;
        if (keys.has(k)) throw new Error(`duplicate JSON key: ${k}`);
        keys.add(k); at++; walk(depth + 1);
        if (tokens[at] !== ',') break;
        at++;
      }
      at++;
    } else if (t === '[') {
      while (tokens[at] !== ']') { walk(depth + 1); if (tokens[at] !== ',') break; at++; }
      at++;
    } else if (t && /^-?\d/.test(t) && !Number.isFinite(Number(t))) throw new Error('non-finite JSON number');
  }
  walk(0);
  return result;
}
export function validateRecoveryShape(value: unknown, schema: Schema, path = '$'): string[] {
  if (schema.anyOf) return schema.anyOf.some(s => validateRecoveryShape(value, s, path).length === 0) ? [] : [path + ': invalid alternative'];
  if (schema.enum && !schema.enum.some(x => x === value)) return [path + ': unsupported value'];
  if (!schema.type) return [];
  const type = value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
  if (type !== schema.type) return [path + ': expected ' + schema.type];
  const findings: string[] = [];
  if (type === 'object') {
    const o = value as Record<string, unknown>;
    for (const k of schema.required ?? []) if (!Object.hasOwn(o, k)) findings.push(`${path}/${k}: required`);
    for (const k of Object.keys(o).sort()) {
      if (!Object.hasOwn(schema.properties ?? {}, k)) findings.push(`${path}/${k}: unexpected field`);
      else findings.push(...validateRecoveryShape(o[k], schema.properties![k], `${path}/${k}`));
    }
  }
  if (type === 'array') {
    const a = value as unknown[];
    if (a.length < (schema.minItems ?? 0) || a.length > (schema.maxItems ?? Infinity)) findings.push(path + ': array size');
    a.forEach((v, i) => findings.push(...validateRecoveryShape(v, schema.items!, `${path}/${i}`)));
  }
  if (type === 'string') {
    const s = value as string;
    if (s.length < (schema.minLength ?? 0) || (schema.pattern && !new RegExp(schema.pattern).test(s))) findings.push(path + ': string constraint');
  }
  return findings;
}
function select(root: unknown, pointer: string): { found: boolean; value: unknown } {
  if (pointer === '') return { found: true, value: root };
  if (!pointer.startsWith('/') || /~(?![01])/u.test(pointer)) return { found: false, value: null };
  let value = root;
  for (const raw of pointer.slice(1).split('/')) {
    const key = raw.replaceAll('~1', '/').replaceAll('~0', '~');
    if (value === null || typeof value !== 'object' || !Object.hasOwn(value, key)) return { found: false, value: null };
    if (Array.isArray(value) && !/^(0|[1-9]\d*)$/.test(key)) return { found: false, value: null };
    value = (value as Record<string, unknown>)[key];
  }
  return { found: true, value };
}
const refKey = (r: BoundReference) => canonicalRecoveryJson(r);
const same = (a: unknown, b: unknown) => canonicalRecoveryJson(a) === canonicalRecoveryJson(b);
function instant(s: string): number {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/.test(s)) return NaN;
  const n = Date.parse(s);
  return Number.isFinite(n) && new Date(n).toISOString() === s.replace(/(?<!\.\d{3})Z$/, '.000Z') ? n : NaN;
}
const precedence: EvidenceState[] = ['invalid', 'stale', 'failed', 'missing', 'inconclusive', 'not-run'];

/** The caller pins the expected binding independently of the untrusted bundle.
 * This evaluates normalized facts, not SQL traces or observer authenticity. B04
 * must establish that bridge; a digest is identity evidence, not truth authority.
 */
export function evaluateRecoveryProductTest(text: string, context: { binding_digest: string; evaluated_at: string }) {
  const findings: { state: EvidenceState; reason: string }[] = [];
  const add = (state: EvidenceState, reason: string) => { findings.push({ state, reason }); };
  let bundle: RecoveryBundle | null = null;
  try {
    const parsed = parseRecoveryJson(text);
    const errors = validateRecoveryShape(parsed, recoveryBundleSchema);
    if (errors.length) errors.forEach(x => add('invalid', x));
    else bundle = parsed as RecoveryBundle;
  } catch (e) { add('invalid', String(e)); }
  const now = instant(context.evaluated_at);
  if (!Number.isFinite(now)) add('invalid', 'invalid evaluation instant');
  if (!/^[0-9a-f]{64}$/.test(context.binding_digest)) add('invalid', 'invalid expected binding digest');
  if (bundle && recoveryBindingDigest(bundle.binding) !== context.binding_digest) add('stale', 'binding differs from caller-pinned candidate');
  const docs = new Map<string, unknown>();
  type Scenario = { id: string; evidence_class: string; checks: { pointer: string; equals: unknown }[] };
  let scenarios: Scenario[] = [];
  if (bundle) {
    const created = instant(bundle.binding.created_at), expires = instant(bundle.binding.expires_at);
    if (!Number.isFinite(created) || !Number.isFinite(expires) || created >= expires || created > now) add('invalid', 'invalid binding interval');
    else if (now >= expires) add('stale', 'binding expired');
    if (recoveryInvalidationDigest(bundle.binding.references) !== bundle.binding.invalidation_key_digest) add('invalid', 'invalidation digest mismatch');
    const identities = new Set<string>();
    for (const d of bundle.documents) {
      const key = refKey(d.reference), identity = `${d.reference.ref}\0${d.reference.version}`;
      if (identities.has(identity)) add('invalid', 'duplicate document identity');
      identities.add(identity);
      if (/(^|[/:@._-])latest($|[/:@._-])/i.test(d.reference.ref + '/' + d.reference.version)) add('invalid', 'ambient latest reference');
      if (recoverySha256(d.content) !== d.reference.sha256) { add('invalid', 'document digest mismatch'); continue; }
      try { docs.set(key, parseRecoveryJson(d.content)); } catch (e) { add('invalid', String(e)); }
    }
    for (const role of RECOVERY_ROLES) if (!docs.has(refKey(bundle.binding.references[role]))) add('missing', 'unresolved binding role: ' + role);
    const contract = docs.get(refKey(bundle.binding.references.scenario_contract));
    const errors = validateRecoveryShape(contract, recoveryScenarioSchema);
    if (errors.length) errors.forEach(x => add('invalid', 'scenario contract: ' + x));
    else {
      scenarios = (contract as { scenarios: Scenario[] }).scenarios;
      if (new Set(scenarios.map(s => s.id)).size !== 30) add('invalid', 'duplicate scenario contract ID');
      for (const s of scenarios) {
        const expectedClass = s.id === 'R01-F26' ? 'formation-only' : ['R01-F27', 'R01-F30'].includes(s.id) ? 'mixed' : 'runtime-product-test';
        if (s.evidence_class !== expectedClass) add('invalid', 'scenario evidence class mismatch: ' + s.id);
      }
    }
    const policy = docs.get(refKey(bundle.binding.references.evaluation_policy));
    if (!same(policy, { policy_id: 'domainspec.orodi.recovery-evaluation-policy-candidate', fresh_max_age_seconds: 86400, receipt_lifetime_seconds: 86400 })) add('invalid', 'unsupported compiled evaluation policy');
    const keys = new Set<string>();
    for (const r of bundle.records) { const k = `${r.scenario_id}/${r.repetition}`; if (keys.has(k)) add('invalid', 'duplicate slot: ' + k); keys.add(k); }
  }
  const receipts: RecoveryReceipt[] = [];
  const globalFailure = precedence.find(s => findings.some(f => f.state === s));
  for (const id of RECOVERY_IDS) for (const repetition of [1, 2]) {
    const rs = bundle?.records.filter(r => r.scenario_id === id && r.repetition === repetition) ?? [];
    const r = rs[0];
    const receipt: RecoveryReceipt = { scenario_id: id, repetition, state: 'passed', reasons: [], source: r?.source ?? null, pointer: r?.pointer ?? null, original_runtime_outcome: null, original_cause: r?.cause ?? null };
    const states: EvidenceState[] = [];
    const fail = (s: EvidenceState, reason: string) => { states.push(s); receipt.reasons.push(reason); };
    if (globalFailure) fail(globalFailure, 'campaign contract or dependency failed; assertion not interpreted');
    else if (!r) fail('missing', 'required slot absent');
    else {
      const source = docs.get(refKey(r.source));
      const selected = select(source, r.pointer);
      if (!docs.has(refKey(r.source)) || !selected.found) fail('missing', 'source document or selector absent');
      if (r.origin === 'workflow') fail('invalid', 'workflow evidence cannot become product evidence');
      if (!same(r.producer, bundle!.binding.references.producer)) fail('invalid', 'producer binding mismatch');
      if (r.execution === 'not-started') fail('not-run', 'test explicitly not started');
      else if (r.execution === 'started') fail('inconclusive', 'completion evidence absent');
      if (bundle!.claim_mode === 'fresh-local-recovery-product-test') {
        if (r.origin === 'historical') fail('inconclusive', 'historical import cannot establish fresh observation');
        else {
          if (!r.observer) fail('missing', 'observer absent');
          else if (!same(r.observer, bundle!.binding.references.observer) || same(r.observer, r.producer)) fail('invalid', 'observer relationship not separately bound');
          if (!r.capture_started_at_utc || !r.capture_finished_at_utc) fail('missing', 'capture interval absent');
          else {
            const start = instant(r.capture_started_at_utc), finish = instant(r.capture_finished_at_utc);
            if (!Number.isFinite(start) || !Number.isFinite(finish) || start > finish || finish > now) fail('invalid', 'invalid capture interval');
            else if (now - finish > 86400000) fail('stale', 'capture interval expired');
          }
        }
      }
      if (selected.found) {
        const outcome = select(selected.value, '/runtime_outcome');
        receipt.original_runtime_outcome = outcome.found ? outcome.value : null;
        if (r.execution === 'completed') for (const check of scenarios.find(s => s.id === id)!.checks) {
          const fact = select(selected.value, check.pointer);
          if (!fact.found) fail('missing', 'expected fact absent: ' + check.pointer);
          else if (!same(fact.value, check.equals)) fail('failed', 'expectation mismatch: ' + check.pointer);
        }
      }
    }
    receipt.state = precedence.find(s => states.includes(s)) ?? 'passed';
    receipts.push(receipt);
  }
  const state = precedence.find(s => findings.some(f => f.state === s) || receipts.some(r => r.state === s)) ?? 'passed';
  if (!EVIDENCE_STATES.includes(state)) throw new Error('internal evidence state mismatch');
  return { schema_version: 'domainspec.orodi.recovery-test-result/v1-candidate', evidence_lane: 'candidate-local-prototype', claim_mode: bundle?.claim_mode ?? null, binding_digest: context.binding_digest, invalidation_key_digest: bundle?.binding.invalidation_key_digest ?? null, evaluated_at: context.evaluated_at, expires_at: Number.isFinite(now) ? new Date(Math.min(now + 86400000, bundle && Number.isFinite(instant(bundle.binding.expires_at)) ? instant(bundle.binding.expires_at) : now + 86400000)).toISOString() : null, state, verdict: state === 'passed' ? 'pass' : 'reject', denominator: 60, assertion_receipts: receipts, findings, qualified_limits: ['Normalized-fact evaluation only; B04 observer/adapter provenance remains required', 'Pre-COMMIT authorization check is not a physical commit-completion deadline', 'Historical integrity does not establish fresh observation', 'No runtime admission or deployment claim'], authority_effect: 'none' };
}
