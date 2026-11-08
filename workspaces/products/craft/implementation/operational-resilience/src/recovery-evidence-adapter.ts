/** Explicit-byte normalization only. No source discovery, process or database API. */
import type { BoundReference } from '../contracts/operational-evidence.js';
import { RECOVERY_IDS, type RecoveryRecord } from '../contracts/recovery-product-test.js';
import { canonicalRecoveryJson, parseRecoveryJson, recoverySha256 } from './evaluate-recovery-product-test.js';

type Json = Record<string, unknown>;
export type RecoveryDocument = { reference: BoundReference; content: string };
export type AdapterInputs = {
  mode: 'historical' | 'fresh';
  manifest: RecoveryDocument; sourceManifest: RecoveryDocument;
  scenarioMap: RecoveryDocument; matrix: RecoveryDocument; results: RecoveryDocument;
  producer: RecoveryDocument; observer: RecoveryDocument;
};
export type AdapterPins = {
  manifest: string; sourceManifest: string; scenarioMap: string; matrix: string; results: string;
  observer: string | null; driver: string | null; python: string | null;
};
function object(value: unknown, label: string): Json {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(label + ': expected object');
  return value as Json;
}
function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw new Error(label + ': expected array');
  return value;
}
const same = (a: unknown, b: unknown) => canonicalRecoveryJson(a) === canonicalRecoveryJson(b);
function exact(value: Json, required: string[], optional: string[], label: string) {
  if (required.some(k => !Object.hasOwn(value, k)) || Object.keys(value).some(k => !required.includes(k) && !optional.includes(k))) throw new Error(label + ': closed shape mismatch');
}
function validRef(ref: BoundReference) {
  if (!ref || !same(Object.keys(ref).sort(), ['ref','sha256','version']) || !ref.ref || !ref.version || !/^[0-9a-f]{64}$/.test(ref.sha256) || /(^|[/:@._-])latest($|[/:@._-])/i.test(ref.ref+'/'+ref.version)) throw new Error('invalid exact reference');
}
export function recoveryDocument(ref: string, value: unknown): RecoveryDocument {
  const content = canonicalRecoveryJson(value);
  return { reference: { ref, version: '1.0.0-candidate.1', sha256: recoverySha256(content) }, content };
}
function read(doc: RecoveryDocument, pin: string, label: string): Json {
  validRef(doc.reference);
  if (doc.reference.sha256 !== pin || recoverySha256(doc.content) !== pin) throw new Error(label + ': digest drift');
  return object(parseRecoveryJson(doc.content), label);
}
function utcInstant(value: unknown): number {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value)) throw new Error('invalid capture timestamp');
  const time=Date.parse(value);
  if (!Number.isFinite(time) || new Date(time).toISOString()!==value) throw new Error('invalid capture timestamp');
  return time;
}
function completeIds(rows: Json[], key: string) {
  if (rows.length !== 30 || !same(rows.map(r => r[key]).sort(), [...RECOVERY_IDS].sort())) throw new Error('exact 30-scenario denominator required');
}

/** Pins must be selected by the caller independently of these input bytes.
 * Historical mode establishes record integrity only. Fresh mode additionally
 * checks the bound driver's observer protocol; authored test assertions remain
 * test-producer evidence, not independently re-proved database invariants.
 */
export function normalizeRecoveryEvidence(input: AdapterInputs, pins: AdapterPins) {
  const findings: string[] = [];
  try {
    exact(object(input, 'input'), ['mode','manifest','sourceManifest','scenarioMap','matrix','results','producer','observer'], [], 'input');
    if (!['historical','fresh'].includes(input.mode)) throw new Error('unsupported mode');
    const producerDescriptor=read(input.producer,input.producer.reference.sha256,'producer descriptor');
    const observerDescriptor=read(input.observer,input.observer.reference.sha256,'observer descriptor');
    exact(producerDescriptor,['mode','artifact_sha256'],[],'producer descriptor');
    exact(observerDescriptor,['mode','artifact_sha256'],[],'observer descriptor');
    const manifest = read(input.manifest, pins.manifest, 'manifest');
    const sources = read(input.sourceManifest, pins.sourceManifest, 'source manifest');
    const mapping = read(input.scenarioMap, pins.scenarioMap, 'scenario map');
    const matrix = read(input.matrix, pins.matrix, 'matrix');
    const results = read(input.results, pins.results, 'results');
    if (manifest.source_manifest_sha256 !== pins.sourceManifest) throw new Error('manifest/source-manifest mismatch');
    const harness = object(manifest.harness_files, 'harness');
    if (producerDescriptor.mode!==input.mode || producerDescriptor.artifact_sha256!==(input.mode==='historical'?harness['case.py']:pins.driver)) throw new Error('producer descriptor not bound to selected artifact');
    if (observerDescriptor.mode!==(input.mode==='historical'?'not-established':'fresh') || observerDescriptor.artifact_sha256!==(input.mode==='historical'?null:pins.observer)) throw new Error('observer descriptor not bound to selected artifact');
    if (harness['scenario-map.json'] !== pins.scenarioMap) throw new Error('manifest/scenario-map mismatch');
    const sourceRows = array(sources.files, 'source files').map(r => object(r, 'source row'));
    if (!sourceRows.some(r => r.sha256 === pins.matrix)) throw new Error('matrix not bound in source manifest');
    if (input.mode === 'historical' && manifest.results_sha256 !== pins.results) throw new Error('manifest/results mismatch');
    if (input.mode === 'fresh' && (!pins.observer || !pins.driver || !pins.python)) throw new Error('fresh producer pins missing');
    const maps = array(mapping.scenarios, 'scenario map').map(r => object(r, 'scenario'));
    const obligations = array(matrix.scenarios, 'matrix').map(r => object(r, 'obligation'));
    completeIds(maps, 'scenario_id'); completeIds(obligations, 'scenario_id');
    for (const m of maps) {
      exact(m, ['scenario_id','tests','contract_probe'], [], 'scenario');
      const names = array(m.tests, 'tests');
      if (new Set(names).size !== names.length || names.some(n => typeof n !== 'string')) throw new Error('invalid test list');
      if (typeof m.contract_probe !== 'boolean') throw new Error('invalid formation flag');
    }
    exact(results, ['runs'], ['status','recorded_at_utc','inputs','replay_independence'], 'results');
    const rawRuns = array(results.runs, 'runs');
    if (rawRuns.length > 60) throw new Error('too many runs');
    const seen = new Set<string>();
    const normalized: Json[] = [];
    const records: RecoveryRecord[] = [];
    const scenarioDefinitions = maps.map(m => ({ id: m.scenario_id, evidence_class: m.scenario_id === 'R01-F26' ? 'formation-only' : ['R01-F27','R01-F30'].includes(String(m.scenario_id)) ? 'mixed' : 'runtime-product-test',
      checks: [{ pointer: '/facts/test_names', equals: m.tests }, { pointer: '/facts/test_results', equals: (m.tests as string[]).map(() => ({result:'PASS',tests_run:1})) },
        { pointer: '/facts/record_consistent', equals: true }, { pointer: '/facts/formation_satisfied', equals: true },
        ...(input.mode === 'fresh' ? [{pointer:'/facts/observer_protocol_satisfied',equals:true}] : [])] }));
    for (let i = 0; i < rawRuns.length; i++) {
      const run = object(rawRuns[i], 'run');
      exact(run, ['scenario_id','repetition','result'], ['exit_code','observation','stderr','stdout','duration_seconds','cause','provenance','authority_effect'], 'run');
      if (!RECOVERY_IDS.includes(String(run.scenario_id)) || ![1,2].includes(run.repetition as number)) throw new Error('invalid scenario slot');
      if (!['PASS','FAIL','not_evaluable'].includes(String(run.result))) throw new Error('unsupported original result');
      const key = `${run.scenario_id}/${run.repetition}`;
      if (seen.has(key)) throw new Error('duplicate scenario slot: ' + key);
      seen.add(key);
      const m = maps.find(m => m.scenario_id === run.scenario_id)!;
      const tests: Json[] = [];
      let obs: Json | null = null, formation = !m.contract_probe;
      let captures: Json[] = [];
      if (run.observation !== undefined && run.observation !== null) {
        obs = object(run.observation, 'observation');
        exact(obs, ['scenario_id','pid','result','tests','contract_probe','process_trace'], ['formation_observations'], 'observation');
        if (obs.scenario_id !== run.scenario_id || !Number.isInteger(obs.pid)) throw new Error('observation identity mismatch');
        for (const raw of array(obs.tests, 'observed tests')) {
          const t = object(raw, 'test');
          exact(t, ['test','result','tests_run','raw_output'], ['before','after'], 'test');
          tests.push(t);
          if (input.mode === 'fresh') for (const phase of ['before','after']) {
            if (t[phase]) captures.push(object(t[phase], 'capture'));
          }
        }
        if (m.contract_probe && obs.contract_probe) {
          const probe = object(obs.contract_probe, 'formation probe');
          exact(probe, ['exit_code','stdout','stderr'], [], 'probe');
          const payload = object(parseRecoveryJson(String(probe.stdout)), 'formation output');
          formation = probe.exit_code === 0 && payload.result === 'PASS' && payload.formation_only === true && payload.runtime_guarantees_observed === false;
        }
        if (input.mode === 'fresh' && m.contract_probe) captures = captures.concat(array(obs.formation_observations, 'formation observations').map(c => object(c, 'capture')));
      }
      let observerSatisfied = false;
      if (input.mode === 'fresh' && obs) {
        const provenance = object(run.provenance, 'fresh provenance');
        exact(provenance, ['mode','manifest_sha256','observer_sha256','driver_sha256','source_manifest_sha256','python','executable_sha256'], [], 'provenance');
        if (provenance.mode !== 'fresh-instrumented' || provenance.manifest_sha256 !== pins.manifest || provenance.source_manifest_sha256 !== pins.sourceManifest || provenance.observer_sha256 !== pins.observer || provenance.driver_sha256 !== pins.driver || provenance.executable_sha256 !== pins.python) throw new Error('fresh provenance mismatch');
        const expectedCaptures = tests.length * 2 + (m.contract_probe ? 2 : 0);
        observerSatisfied = captures.length === expectedCaptures && captures.length > 0;
        let previous = -1, previousFinish = -Infinity;
        const capturePlan = tests.flatMap(t => [{test:t.test,barrier:'before-test'}, {test:t.test,barrier:'after-test'}]).concat(m.contract_probe ? [{test:'formation-probe',barrier:'before-formation'}, {test:'formation-probe',barrier:'after-formation'}] : []);
        for (const [captureIndex,c] of captures.entries()) {
          exact(c, ['schema_version','scenario_id','repetition','test_id','subject_digest','observer_digest','producer_pid','observer_pid','parent_pid','barrier_id','sequence','driver_clock','capture_started_at_utc','capture_finished_at_utc','observer_environment','stores','all_connections_closed','cross_store_atomic','authority_effect'], [], 'capture');
          if (c.schema_version !== 'domainspec.orodi.recovery-observer/v1-candidate' || c.scenario_id !== run.scenario_id || c.repetition !== run.repetition || c.subject_digest !== pins.manifest || c.observer_digest !== pins.observer || c.producer_pid !== obs.pid || c.parent_pid !== obs.pid || c.observer_pid === obs.pid || !Number.isInteger(c.observer_pid) || c.authority_effect !== 'none') throw new Error('observer identity mismatch');
          if (c.all_connections_closed !== true || c.cross_store_atomic !== false || !Number.isInteger(c.sequence) || Number(c.sequence) <= previous) throw new Error('observer ordering/interference mismatch');
          if (c.test_id !== capturePlan[captureIndex]?.test || c.barrier_id !== capturePlan[captureIndex]?.barrier) throw new Error('capture test/barrier mismatch');
          const started=utcInstant(c.capture_started_at_utc), finished=utcInstant(c.capture_finished_at_utc);
          if (started>finished || started<previousFinish) throw new Error('capture interval ordering mismatch');
          previousFinish=finished;
          exact(object(c.driver_clock,'clock'),['kind','boot_id','monotonic_value'],[],'clock');
          const clock=c.driver_clock as Json;
          if (clock.kind==='injected') { if (typeof clock.boot_id!=='string'||!Number.isInteger(clock.monotonic_value)) throw new Error('invalid injected clock'); }
          else if (clock.kind!=='not-supplied'||clock.boot_id!==null||clock.monotonic_value!==null) throw new Error('unsupported clock provenance');
          exact(object(c.observer_environment,'observer environment'),['python','sqlite'],[],'observer environment');
          previous = Number(c.sequence);
          const stores = array(c.stores, 'captured stores').map(s => object(s, 'store'));
          if (stores.length > 2 || new Set(stores.map(s => s.role)).size !== stores.length) throw new Error('observer store budget');
          if (c.test_id!=='formation-probe' && stores.length===0) observerSatisfied=false;
          if (c.test_id==='formation-probe' && stores.length!==0) throw new Error('formation capture claims runtime stores');
          for (const store of stores) {
            if (!['coordination','operation'].includes(String(store.role))) throw new Error('unknown store role');
            const common=['role','path','capture_started_at_utc','capture_finished_at_utc','state','connection_closed'];
            exact(store, common.concat(store.state==='observed'?['schema_version','journal_mode','schema_sha256','tables']:['cause']), [], 'store');
            if (!['observed','unavailable'].includes(String(store.state))) throw new Error('unknown store state');
            const a=utcInstant(store.capture_started_at_utc), b=utcInstant(store.capture_finished_at_utc);
            if (a<started || b>finished || a>b) throw new Error('store interval outside capture');
            if (store.state==='observed') {
              if (!Number.isInteger(store.schema_version)||!['delete','truncate','persist','off','memory'].includes(String(store.journal_mode))||!/^[0-9a-f]{64}$/.test(String(store.schema_sha256))) throw new Error('invalid store metadata');
              for (const table of Object.values(object(store.tables,'tables'))) {
                const t=object(table,'table'); exact(t,['columns','rows'],[],'table');
                const columns=array(t.columns,'columns'), rows=array(t.rows,'rows');
                if (columns.some(x=>typeof x!=='string')||new Set(columns).size!==columns.length||rows.some(row=>!Array.isArray(row)||row.length!==columns.length)) throw new Error('invalid table shape');
              }
            }
          }
          // Unavailable snapshots stay explicit and cannot establish fresh eligibility.
          if (stores.some(s => s.state !== 'observed' || s.connection_closed !== true)) observerSatisfied = false;
        }
      }
      const outcomes: unknown[] = [];
      if (obs) for (const t of tests) {
        const after = t.after && typeof t.after === 'object' ? t.after as Json : null;
        if (input.mode === 'historical' && after?.databases) for (const db of Object.values(object(after.databases, 'databases'))) {
          const tables = object(db, 'database').tables as Json | undefined;
          if (tables?.attempts && Array.isArray(tables.attempts)) for (const row of tables.attempts) if (Array.isArray(row) && row[9] != null) outcomes.push(row[9]);
        }
        if (input.mode === 'fresh' && after?.stores) for (const db of array(after.stores, 'stores')) {
          const tables = object(db, 'store').tables as Json | undefined;
          if (tables?.attempts) { const table = object(tables.attempts, 'attempt table'); const at = (table.columns as string[]).indexOf('outcome'); for (const row of table.rows as unknown[][]) if (at >= 0 && row[at] != null) outcomes.push(row[at]); }
        }
      }
      const freshEligible = input.mode === 'fresh' && observerSatisfied;
      normalized.push({ scenario_id: run.scenario_id, repetition: run.repetition, raw_source: input.results.reference, raw_pointer: `/runs/${i}`,
        original_result: run.result, original_cause: run.cause ?? null, runtime_outcome: outcomes.includes('unknown') ? 'unknown' : outcomes.at(-1) ?? null,
        runtime_outcomes: outcomes, expectation_ref: obligations.find(o => o.scenario_id === run.scenario_id)!.constraint_ref,
        facts: { test_names: tests.map(t => t.test), test_results: tests.map(t => ({result:t.result,tests_run:t.tests_run})),
          record_consistent: run.result === 'PASS' && run.exit_code === 0 && obs?.result === 'PASS', formation_satisfied: formation, observer_protocol_satisfied: observerSatisfied },
        freshness: input.mode === 'historical' ? 'unknown' : freshEligible ? 'captured' : 'unsupported',
        capture_limits: 'Before/after test barriers only; authored test assertions are producer evidence. No independent re-proof of every intra-test fault boundary.' });
      const first = captures[0], last = captures.at(-1);
      records.push({scenario_id:String(run.scenario_id),repetition:Number(run.repetition),source:input.results.reference,pointer:`/assertions/${normalized.length-1}`,
        origin:input.mode==='historical'?'historical':'fresh',execution:!obs?'started':input.mode==='fresh'&&!freshEligible?'started':'completed',
        producer:input.producer.reference,observer:input.mode==='fresh'?input.observer.reference:null,
        capture_started_at_utc:first?String(first.capture_started_at_utc):null,capture_finished_at_utc:last?String(last.capture_finished_at_utc):null,
        cause:run.cause?String(run.cause):input.mode==='fresh'&&!freshEligible?'incomplete observer evidence':null});
    }
    const normalizedDocument = recoveryDocument('domainspec.orodi.recovery-normalized/'+pins.results, {assertions:normalized});
    for (const r of records) r.source = normalizedDocument.reference;
    const scenarioDocument = recoveryDocument('domainspec.orodi.recovery-scenario-contract/'+input.mode+'/'+pins.scenarioMap, {schema_version:'domainspec.orodi.recovery-scenarios/v1-candidate',scenarios:scenarioDefinitions});
    return {status:'normalized' as const,findings,documents:[input.producer,input.observer,input.manifest,input.sourceManifest,input.scenarioMap,input.matrix,input.results,normalizedDocument,scenarioDocument],records,normalizedDocument,scenarioDocument,
      claim_mode:input.mode==='historical'?'historical-record-integrity' as const:'fresh-local-recovery-product-test' as const, authority_effect:'none' as const};
  } catch (error) {
    return {status:'invalid' as const,findings:[String(error)],documents:[],records:[],normalizedDocument:null,scenarioDocument:null,claim_mode:null,authority_effect:'none' as const};
  }
}
