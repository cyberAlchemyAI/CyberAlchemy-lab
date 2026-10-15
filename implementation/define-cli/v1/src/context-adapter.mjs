import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {canonicalize, digest} from './canonical.mjs';

export const LAB_ROOT = resolve(import.meta.dirname, '../../../..');
export function callLab(operation, input = {}, repositoryRoot = LAB_ROOT) {
  const run = spawnSync(process.env.DEFINE_PYTHON ?? 'python3', [resolve(import.meta.dirname, '../lab_bridge.py')], {
    input: JSON.stringify({...input, operation, repo: resolve(repositoryRoot)}), encoding: 'utf8',
    env: {...process.env, PYTHONDONTWRITEBYTECODE: '1'}, maxBuffer: 16 * 1024 * 1024, timeout: 60000,
  });
  if (run.error) throw new Error(`define.lab-bridge:${run.error.message}`);
  let value;
  try { value = JSON.parse(run.stdout); } catch { throw new Error(`define.lab-bridge-invalid-output:${run.stderr.slice(0, 300)}`); }
  if (run.status !== 0) throw new Error(`define.lab-bridge-blocked:${value.error ?? 'unknown'}`);
  return value;
}
export function composeDefineContext(input, repositoryRoot = LAB_ROOT) {
  try {
    const result = callLab('context', {store: input.store, subject: input.subject,
      definition_refs: input.definition_refs ?? [], ttl: input.ttl ?? 900}, repositoryRoot);
    const packet = result.packet;
    const included = [
      {context_item_id: 'lab:project-state', content: packet.project_state, authority_posture: 'selected-project-state'},
      {context_item_id: 'lab:context-view', content: packet.context_view, authority_posture: 'candidate-derived-view'},
      {context_item_id: 'lab:ontology-view', content: packet.ontology_view, authority_posture: 'candidate-derived-view'},
      {context_item_id: 'lab:ontology-cut', content: packet.ontology_cut, authority_posture: 'candidate-derived-cut'},
      ...result.definitions.map(row => ({context_item_id: `definition:${row.identity}`, content: row.record,
        authority_posture: row.axes.status, source: row.source, version_ref: row.version_ref, decision_ref: row.decision_ref})),
    ];
    const inlineBytes = Buffer.byteLength(JSON.stringify(included));
    if (inlineBytes > 256 * 1024) throw new Error('define.context-inline-budget-exceeded');
    const sourceEpoch = digest({snapshot: result.source_snapshot_digest, head: result.head});
    const envelope = canonicalize({schema_version: 'cal.define-context-envelope/v1',
      context_epoch_id: packet.context_view.node_id, source_epoch: sourceEpoch,
      included_items: included, inline_bytes: inlineBytes, max_inline_bytes: 256 * 1024,
      freshness_state: result.freshness.status, expires_at: packet.context_view.expires_at,
      source_snapshot_digest: result.source_snapshot_digest, head: result.head,
      ontology_diagnostics: packet.query.diagnostics, authority_effect: 'none',
      session_disposition: 'context-exported-agent-session-closed',
      exclusions: ['admission', 'execution-authority', 'private-long-term-agent-memory']});
    return {ok: true, source_epoch: sourceEpoch,
      request_digest: digest({goal: input.goal, intent: input.intent, context: input.context, consumer: input.consumer}),
      route_decision: {selected: {route_id: 'CAL-DEFINE-EXPLICIT-ENTRY'},
        decision_digest: digest({entry: 'define', effect: 'candidate-meaning-only', source_epoch: sourceEpoch})},
      context_envelope: envelope, context_envelope_digest: digest(envelope),
      refresh_assessment: {status: 'current', source_epoch: sourceEpoch},
      lab_views: packet, authority_effect: 'none'};
  } catch (error) {
    return {ok: false, stage: 'lab-context', reason_codes: [error.message], authority_effect: 'none'};
  }
}
