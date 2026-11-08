"""Pure, narrow proof for an engineering design output used by its next phase.

The caller must obtain the transaction through a fully replayed owned Journal
and the material row through the selected sealed original-output reader. This
predicate never labels the private output admitted to signed Source.
"""
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, reason):
    if not value:
        raise ValueError(reason)


def verify_prior_design(*, message, run, head, current_raw, transaction,
                        result, producer_principal, row, receipts, header):
    """Return the exact private design body after all same-run joins pass."""
    require(message['transition_ref'] == 'transition:engineering:implemented' and
            run['state'] == 'designed' and
            header['carrier_ref'] == 'cal.artifact-type.generated-output/v2',
            'only the engineering design successor may consume a produced input')
    require(head['sequence'] >= 1 and sha(current_raw) == message['run_binding']['sha256']
            and json.loads(current_raw) == run,
            'later input lacks the current exact WorkflowRun')
    event = transaction['event']
    require(transaction['sequence'] == head['sequence'] and
            transaction['next_run_sha256'] == head['run_sha256'] and
            event['run_ref'] == run['run_ref'] and
            event['source_cut'] == run['source_cut'] == message['source_cut'] and
            event['actor'] == run['actor'] and
            event['transition_ref'] == 'transition:engineering:designed' and
            event['from_state'] == 'prepared' and event['to_state'] == 'designed' and
            event['output_artifact_refs'] == [header] == transaction['output_artifact_refs'] and
            run['event_bindings'] and run['event_bindings'][-1] ==
            {'ref': 'workflow-event:' + sha(canonical(event)),
             'sha256': sha(canonical(event))},
            'produced input is not the exact committed prior design event')
    require(result.state == 'completed-sealed' and
            result.route_refs == ('transition:engineering:designed',) and
            result.run_binding['sha256'] == transaction['before_run_sha256'] and
            result.work_ref == run['work']['version_ref'] and
            result.source_cut == run['source_cut'] and
            producer_principal == run['actor']['principal_ref'] and
            row['artifact'] == header and row['original_binding']['sha256'] == header['byte_sha256'] and
            type(row['raw']) is bytes and sha(row['raw']) == header['byte_sha256'],
            'prior output lacks exact sealed producer/cut/Work/byte correspondence')
    require(type(receipts) is list and len(receipts) > 0 and
            all(type(item) is dict and type(item.get('original_binding')) is dict
                for item in receipts) and
            [item['original_binding'] for item in receipts] ==
            transaction['producer_receipt_bindings'],
            'prior output capsule receipts differ from committed transaction')
    body = json.loads(row['raw'])
    require(body['kind'] == 'generated-output' and
            body['node_id'] == header['identity_ref'] and
            body['scope_ref'] == header['scope_ref'] and
            body['authority_effect'] == 'none',
            'prior generated-output original body differs')
    return body
