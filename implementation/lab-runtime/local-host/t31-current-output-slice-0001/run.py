"""One current-signed fixture output event, owned journal, and later consumer."""

import copy
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
CATALOG = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/carrier-catalog.json'
RECEIPT = HERE / 'RUN-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    if RECEIPT.exists():
        raise ValueError('no-replace run receipt already exists')
    paths = [HERE / x for x in ('fixture.py', 'producer.py', 'consumer.py', 'run.py')]
    code_before = {p.name: sha(p.read_bytes()) for p in paths}
    F = load('_cal_t31_output_fixture_0001', HERE / 'fixture.py')
    producer = load('_cal_t31_output_producer_0001', HERE / 'producer.py')
    consumer = load('_cal_t31_output_consumer_0001', HERE / 'consumer.py')
    checks, observed = [], {}
    workspace = None
    failure = None
    try:
        with F.current_fixture() as f:
            workspace = f['workspace']
            P = f['protocol']
            J = f['journal']
            K = importlib.import_module('_cal_t31_workflow_component_0001.kernel')
            O = importlib.import_module('_cal_t31_api49_owned_output_workflow_0001.workflow_output_contracts')
            view, message, grant = f['view'], f['message'], f['grant']
            source_binding = P.source.current_workflow_bindings()['source_binding']
            if (f['source_cut'] != view.legacy_signed_sources.source_cut
                    or f['context']['principal_ref'] != grant['principal_ref']):
                raise ValueError('authenticated signed Source fixture differs')
            checks.append('current-signed-source-and-actor')

            def material(binding):
                return f['service'].vault.material(binding)

            run = json.loads(material(message['run_binding']))
            headers = {}
            for header in [run[k] for k in ('intent', 'intent_resolution', 'work', 'coordination_context')] + message['input_artifacts']:
                row = view.subjects[header['version_ref']]
                headers[header['version_ref']] = {'artifact': header,
                    'posture': row['effective_state'], 'semantic_kind': row['kind']}
            plan = K.plan(message,
                definition_raw=material(message['definition_binding']),
                run_raw=material(message['run_binding']),
                authority_raw=material(message['authority_evaluation_binding']),
                satisfaction_raw=material(message['satisfaction_report_binding']),
                host_grant=grant, authenticated_actor=run['actor'],
                current_cut=f['source_cut'], selected_headers=headers,
                selected_obligations=grant['obligation_bindings'],
                now=datetime.now(timezone.utc))
            if plan['allowed_output_carriers'] != ['cal.artifact-type.generated-output/v2']:
                raise ValueError('selected workflow output carrier differs')
            checks.append('native-kernel-output-contract')
            report_raw, body_raw, output = producer.produce(view, f['source_cut'], f['headers']['work'],
                                                            source_binding, grant['scope_ref'])
            catalog_raw = CATALOG.read_bytes()
            catalog = json.loads(catalog_raw)
            documents = {row[key]: (ROOT / row[key]).read_bytes()
                         for row in catalog['rows'] for key in ('schema_path', 'artifact_path')}
            carriers = O.OriginalCarriers(catalog_raw, sha(catalog_raw), documents)
            before = F.owned_snapshot(workspace)
            changed = copy.deepcopy(output)
            changed['byte_sha256'] = '0' * 64
            try:
                O.attach_outputs(K, plan, outputs=[changed], raw_by_ref={changed['version_ref']: body_raw},
                    carriers=carriers, scope_ref=grant['scope_ref'], work_ref=f['headers']['work']['version_ref'])
            except O.OutputRefusal:
                pass
            else:
                raise ValueError('changed output header unexpectedly accepted')
            if F.owned_snapshot(workspace) != before:
                raise ValueError('refused output changed owned workspace')
            checks.append('changed-output-refused-without-effect')
            attached = O.attach_outputs(K, plan, outputs=[output],
                raw_by_ref={output['version_ref']: body_raw}, carriers=carriers,
                scope_ref=grant['scope_ref'], work_ref=f['headers']['work']['version_ref'])
            producer_receipt = P.compact({'schema_version': 'lab-T31-local-source-output-producer/v1-candidate',
                'source_binding': source_binding, 'source_cut': f['source_cut'],
                'report_sha256': sha(report_raw), 'output_body_sha256': sha(body_raw),
                'output_version_ref': output['version_ref'], 'authority_effect': 'none'})
            attached['producer_receipt_bindings'] = [P.binding('receipt:t31-current-source-output', producer_receipt)]

            def host_guard():
                if (f['channel'].guard()['principal_ref'] != grant['principal_ref']
                        or view.legacy_signed_sources.source_cut != f['source_cut']
                        or P.source.current_workflow_bindings()['source_binding'] != source_binding):
                    raise ValueError('selected workflow host guard differs')

            request = P.binding(message['request_ref'], P.compact(message))
            tx = f['store'].apply(attached, request_binding=request, host_guard=host_guard)
            head, current_raw = J.Journal(workspace / 'workflows/source-inspection',
                                         f['store'].config_sha256).replay()
            if (head['sequence'] != 1 or tx['event']['output_artifact_refs'] != [output]
                    or json.loads(current_raw)['event_bindings'][-1]['sha256'] != K.digest(tx['event'])):
                raise ValueError('native output journal/event replay differs')
            checks.append('native-output-bearing-journal-replay')
            consumed = consumer.consume(view, f['source_cut'], source_binding, f['headers']['work'],
                                        report_raw, body_raw, output)
            if consumed['output_body_sha256'] != output['byte_sha256'] or consumed['discrepancy_count'] != 0:
                raise ValueError('later consumer report differs')
            checks.append('later-consumer-processed-output-body-and-report')
            tampered = bytearray(report_raw)
            tampered[-2] = 49 if tampered[-2] != 49 else 50
            after = F.owned_snapshot(workspace)
            try:
                consumer.consume(view, f['source_cut'], source_binding, f['headers']['work'],
                                 bytes(tampered), body_raw, output)
            except ValueError:
                pass
            else:
                raise ValueError('later consumer accepted changed report bytes')
            if F.owned_snapshot(workspace) != after:
                raise ValueError('changed report caused another workflow effect')
            checks.append('changed-report-refused-without-new-effect')
            observed = {'source_manifest_sha256': source_binding['sha256'],
                'source_cut_sha256': sha(P.compact(f['source_cut'])),
                'output_version_ref': output['version_ref'],
                'output_body_sha256': sha(body_raw), 'report_sha256': sha(report_raw),
                'consumer_sha256': sha(P.compact(consumed)),
                'event_sha256': K.digest(tx['event']),
                'transaction_sha256': sha(P.compact(tx)),
                'next_run_sha256': sha(current_raw),
                'journal_sequence': head['sequence'],
                'current_subject_count': consumed['current_subject_count'],
                'original_w08_transitions_observed': 0}
    except Exception:
        failure = traceback.format_exc()
    code_after = {p.name: sha(p.read_bytes()) for p in paths}
    success = (failure is None and len(checks) == 6 and code_after == code_before
               and workspace is not None and not workspace.exists())
    receipt = {'schema_version': 'lab-T31-current-output-slice/v1-candidate',
        'result': 'PASS' if success else 'FAIL', 'checks': checks, 'failure': failure,
        'code_sha256': code_before, 'code_unchanged': code_after == code_before,
        'owned_fixture_removed': workspace is not None and not workspace.exists(),
        'observed': observed, 'authority_effect': 'none',
        'claim_ceiling': 'One local current-signed-source custom output-bearing native kernel/journal WorkflowRun transition and later behavioral consumer. This is not the selected API49 workflow.transition route or any of 28 original W08 transitions; no Work satisfaction, admission, owner outcome or T31 completion.'}
    with RECEIPT.open('x') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': receipt['result'], 'failure': None if failure is None else failure.splitlines()[-1],
                      'checks': checks, 'receipt_sha256': sha(RECEIPT.read_bytes())}, sort_keys=True), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
