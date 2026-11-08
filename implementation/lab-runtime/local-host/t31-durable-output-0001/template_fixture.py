"""All-template output-custody exercise using explicitly synthetic producers/grants."""
import json
from pathlib import Path
import tempfile

from output_store import J, O, ROOT, OutputJournal, original_carriers, sha
from test_output_store import F


def plan_for(path, transition, *, build_witness=None, selected_outputs=None):
    message, facts = (F.F.build if build_witness is None else build_witness)()
    definition_raw = path.read_bytes()
    definition = json.loads(definition_raw)
    run = json.loads(facts['run_raw'])
    run.update(definition_binding=F.binding(definition['workflow_type_ref'], definition_raw),
               state=transition['from_state'])
    before = J.K.encoded(run)
    scope = facts['host_grant']['scope_ref']
    inputs = [{'scope_ref': scope, 'identity_ref': 'fixture:input:' + str(i),
               'version_ref': 'fixture:input:' + str(i) + '@candidate.1',
               'carrier_ref': carrier, 'byte_sha256': 'c' * 64}
              for i, carrier in enumerate(transition['input_carriers'])]
    message.update(definition_binding=run['definition_binding'], run_binding=F.binding('fixture:before', before),
                   transition_ref=transition['transition_ref'], expected_state=run['state'], input_artifacts=inputs)
    obligations = {ref: [{'ref': 'fixture:evidence:' + ref, 'sha256': 'd' * 64}]
                   for name in ('authority_requirement_refs', 'precondition_refs', 'satisfaction_check_refs', 'relation_requirement_refs')
                   for ref in transition[name]}
    def check(ref):
        return {'check_ref': 'fixture:check:' + ref, 'obligation_ref': ref, 'result': 'pass',
                'evidence_bindings': obligations[ref], 'claim_ceiling': 'Synthetic local fixture only.'}
    authority = json.loads(facts['authority_raw'])
    authority['checks'] = [check(ref) for ref in transition['authority_requirement_refs']]
    authority['evidence_bindings'] = next(iter(obligations.values()))
    satisfaction = json.loads(facts['satisfaction_raw'])
    satisfaction['subject_binding'] = message['run_binding']
    satisfaction['checks'] = [check(ref) for name in ('precondition_refs', 'satisfaction_check_refs', 'relation_requirement_refs')
                               for ref in transition[name]]
    message['authority_evaluation_binding'] = F.binding('fixture:authority', J.K.encoded(authority))
    message['satisfaction_report_binding'] = F.binding('fixture:satisfaction', J.K.encoded(satisfaction))
    facts['host_grant'].update(actor_role_refs=transition['actor_role_refs'],
        permitted_transitions=[transition['transition_ref']], obligation_bindings=obligations,
        **{name: message[name] for name in ('run_binding', 'definition_binding', 'authority_evaluation_binding',
                                           'satisfaction_report_binding', 'action_receipt_bindings')})
    selected_headers = {row['version_ref']: {'artifact': row, 'posture': 'local-admitted-current', 'semantic_kind': 'fixture'}
                        for row in [run[name] for name in ('intent', 'intent_resolution', 'work', 'coordination_context')] + inputs}
    facts.update(definition_raw=definition_raw, run_raw=before, authority_raw=J.K.encoded(authority),
                 satisfaction_raw=J.K.encoded(satisfaction), selected_headers=selected_headers,
                 selected_obligations=obligations)
    plan = J.K.plan(message, **facts)
    carriers = original_carriers()
    outputs, originals = [], {}
    if selected_outputs is not None:
        if (len(selected_outputs) != len(transition['output_carriers'])
                or {h['carrier_ref'] for h, _ in selected_outputs} != set(transition['output_carriers'])):
            raise ValueError('Exact retained output closure required')
    for ref in transition['output_carriers']:
        if selected_outputs is not None:
            matches = [(h, raw) for h, raw in selected_outputs if h['carrier_ref'] == ref]
            if len(matches) != 1:
                raise ValueError('Exact retained output carrier required')
            header, raw = matches[0]
            carriers.output(header, raw, scope_ref=scope, transition_ref=transition['transition_ref'])
            outputs.append(header)
            originals[header['version_ref']] = raw
            continue
        row = carriers.rows[ref]
        folder = (ROOT / row['schema_path']).parent / 'fixtures/valid'
        selected = None
        for fixture in sorted(folder.glob('*.json')):
            body = json.loads(fixture.read_bytes())
            if 'scope_ref' in body:
                body['scope_ref'] = scope
            elif 'project_ref' in body:
                body['project_ref'] = scope
            elif 'project_ref' in body.get('payload', {}):
                body['payload']['project_ref'] = scope
            if ref == 'cal.artifact-type.work-outcome-assessment/v1':
                body['payload']['subject_ref'] = run['work']['version_ref']
            identity = next((body[key] for key in ('node_id', 'goal_id', 'coordination_context_id', 'project_id', 'migration_manifest_id') if key in body), None)
            raw = J.K.encoded(body)
            header = {'scope_ref': scope, 'identity_ref': identity,
                      'version_ref': str(identity) + '@' + body.get('version', 'candidate.1'),
                      'carrier_ref': ref, 'byte_sha256': sha(raw)}
            try:
                carriers.output(header, raw, scope_ref=scope, transition_ref=transition['transition_ref'])
            except (ValueError, KeyError, TypeError):
                continue
            selected = header, raw
            break
        if selected is None:
            raise ValueError('No schema-valid public fixture for ' + ref)
        header, raw = selected
        outputs.append(header)
        originals[header['version_ref']] = raw
    plan = O.attach_outputs(J.K, plan, outputs=outputs, raw_by_ref=originals, carriers=carriers,
                            scope_ref=scope, work_ref=run['work']['version_ref'], transition_ref=transition['transition_ref'])
    J.K.validate_shapes(message, definition, plan['next_run'], authority, satisfaction)
    plan['producer_receipt_bindings'] = [F.binding('fixture:producer:' + h['version_ref'], originals[h['version_ref']]) for h in outputs]
    return plan, before, originals


def run():
    selected = json.loads((ROOT / 'implementation/lab-runtime/candidates/repeatable-operation/design/workflow-bindings.json').read_bytes())
    rows = []
    with tempfile.TemporaryDirectory(prefix='t31-all-output-fixtures-') as temp:
        for workflow in selected['workflows']:
            path = ROOT / workflow['source_binding']['path']
            raw = path.read_bytes()
            if sha(raw) != workflow['source_binding']['sha256']:
                raise ValueError('selected definition changed')
            for transition in json.loads(raw)['transitions']:
                plan, before, originals = plan_for(path, transition)
                store = OutputJournal.initialize(Path(temp) / str(len(rows)), before,
                    plan['event']['output_artifact_refs'][0]['scope_ref'], plan['next_run']['actor']['principal_ref'])
                tx = store.apply(plan, originals=originals, request_binding=F.binding('fixture:request', J.K.encoded(transition)), host_guard=lambda: None)
                cold = OutputJournal(store.root, store.journal.config_sha256)
                consumed = cold.consume(1)
                if {h['version_ref']: raw for h, raw in consumed} != originals:
                    raise ValueError('later byte consumption differs')
                rows.append({'transition_ref': transition['transition_ref'], 'workflow': workflow['name'],
                             'output_count': len(consumed), 'state': json.loads(cold.replay()[1])['state'],
                             'output_carriers': [h['carrier_ref'] for h, _ in consumed],
                             'sequence': tx['sequence'], 'canonical_admissions': tx['canonical_admissions']})
    return {'result': 'PASS-all-template-fixture-output-custody', 'workflow_count': len(selected['workflows']),
            'transition_count': len(rows), 'transitions': rows, 'synthetic_grant_and_producers': True,
            'actual_original_producer_execution': False, 'T31_complete': False, 'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
