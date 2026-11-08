"""Independent read-only audit of frozen inert authority selection0001."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO/'implementation/lab-runtime/local-host'
HERE = LOCAL/'context-successor-authority-selection-0001'
PIN = {
    HERE/'freeze.json':'36f301cb2f2359815eb2474b10a4d33124bfe894e222330d4a2e7f8a54ce3345',
    LOCAL/'context-successor-final-stage-0004/freeze.json':'b96908371b064fa0fd90e398a8dfbe3023cf83cb99175dacb3393d08f02ed984',
    LOCAL/'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0004.md':'44d9681c9b1eefa4f28479e4a27133428c6d735c4f32325203dbd80e2a1d12f6',
    LOCAL/'context-policy-topology-0002/freeze.json':'2c6e5ab3ccb94d5709b585d1307b30f47c101bed5b456db6638c0a333e61839c',
    LOCAL/'CONTEXT-POLICY-TOPOLOGY-INDEPENDENT-STATIC-REVIEW-0002.md':'992803813ea297b43bdd4b66b3abfd2a676d05a20e383104bb46d066d48cc94a',
}


def need(ok,code):
    if not ok: raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_pin():
    for path,digest in PIN.items():
        need(sha(path.read_bytes()) == digest,'PIN_DRIFT')
    freeze = json.loads((HERE/'freeze.json').read_bytes())
    need(freeze['effect_enabled'] is False and
         freeze['actual_bound_rows'] == 1570 and
         freeze['auth_row'] == 'UNMINTED_UNSELECTED' and
         freeze['protected_archive_body'] == 'UNOPENED' and
         freeze['selector_freeze_sha256'] == PIN[LOCAL/'context-successor-final-stage-0004/freeze.json'] and
         freeze['selector_review_sha256'] == PIN[LOCAL/'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0004.md'] and
         freeze['policy_freeze_sha256'] == PIN[LOCAL/'context-policy-topology-0002/freeze.json'] and
         freeze['policy_review_sha256'] == PIN[LOCAL/'CONTEXT-POLICY-TOPOLOGY-INDEPENDENT-STATIC-REVIEW-0002.md'],
         'FREEZE_SCOPE')
    for name,digest in freeze['members'].items():
        need(sha((HERE/name).read_bytes()) == digest,'MEMBER_DRIFT')
    return freeze


def boundary(event,args):
    if event == 'open':
        path = str(args[0])
        need(not path.endswith('/branch.snapshot'), 'PRIVATE_BODY_OPEN')
        mode = args[1]
        flags = args[2]
        need(not (isinstance(mode,str) and any(x in mode for x in 'wax+')) and
             not (isinstance(flags,int) and flags &
                  (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)),
             'WRITE_OPEN')
    if event in {'subprocess.Popen','os.system','os.fork','os.posix_spawn',
                 'socket.__new__'}:
        raise RuntimeError('EFFECT_EVENT_'+event)


def main():
    freeze = check_pin()
    sys.addaudithook(boundary)
    spec = importlib.util.spec_from_file_location('independent_authority_selection',
                                                   HERE/'authority_selection.py')
    need(spec is not None and spec.loader is not None,'IMPORT')
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    now = dt.datetime.now(dt.timezone.utc)
    selected = A.current_selection(now)
    stage = selected['stage']
    source = selected['source']
    rows = stage['bound_rows']
    need(selected['effect'] == 'NOT_RUN' and selected['status'] ==
         'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD' and
         len(rows) == len({row['path'] for row in rows}) == 1570 and
         stage['bound_file_count'] == 1570 and
         stage['final_count_with_auth'] == 1571 and
         stage['auth_placeholder'] == {'path':A.AUTH_PATH,
             'sha256':'UNMINTED_UNSELECTED','mode':'0600'} and
         A.AUTH_PATH not in {row['path'] for row in rows} and
         stage['protected_archive_metadata']['body'] == 'UNOPENED' and
         selected['auth_row'] == 'UNMINTED_UNSELECTED' and
         selected['issuer'] == 'UNSELECTED' and
         selected['private_root'] == 'UNCREATED' and
         selected['proof'] == 'UNSERVED' and
         selected['required_signed_scope']['status'] ==
         'NOT_OPENED_REQUIRES_REVIEWED_READER_SIGNED_VIEW' and
         source['scope_attestation'] == 'NOT_OPENED_SIGNED_SOURCE_VIEW' and
         A.utc(source['period_start']) <= now < A.utc(source['period_end']),
         'ACTUAL_SELECTION')
    topo = selected['policy_topology']
    need(topo['additional_bind'] == {'source':stage['topology']['private_root'],
         'target':'/context-policy','read_only':True} and
         topo['private_key'] == 'PARENT_MEMORY_ONLY_NEVER_MOUNTED' and
         stage['workspace_mount_mode'] == 'ro' and
         stage['context_output']['parent_access'] == 'HELD_WRITER_ONLY',
         'POLICY_TOPOLOGY')
    template = A.auth_template(selected,now)
    candidate = A.parse(template['bytes'])
    need(template['status'] == 'UNTRUSTED_UNISSUED_AUTH_TEMPLATE_ONLY' and
         template['effect'] == 'NOT_RUN' and
         template['issuer'] == 'UNSELECTED' and
         template['signed_scope'] == 'NOT_OPENED' and
         template['actual_bound_count'] == 1570 and
         template['would_be_final_count'] == 1571 and
         template['sha256'] == sha(template['bytes']) and
         candidate['authority_effect'] == 'none' and
         A.utc(candidate['expires_at']) <= A.utc(source['period_end']) and
         A.utc(candidate['expires_at'])-A.utc(candidate['not_before']) <=
         dt.timedelta(minutes=20), 'UNISSUED_TEMPLATE')
    design = A.ordered_design(selected)
    steps = design['steps']
    before = lambda x,y:steps.index(x)<steps.index(y)
    need(before('HOLD_NOFOLLOW_STAGE_PARENT_AND_EXCLUSIVE_ROOT_CLAIM',
                'DURABLE_NO_RETRY_STAGE_MARKER_BEFORE_CONTENT') and
         before('DURABLE_NO_RETRY_STAGE_MARKER_BEFORE_CONTENT',
                'COPY_AND_REHASH_1570_BOUND_ROWS_WITH_PRIVATE_BODY_CUSTODY') and
         before('RECHECK_PERIOD_SIGNED_SCOPE_AND_ISSUER_BEFORE_AUTH_EFFECT',
                'ISSUE_EXACT_AUTH_AND_WRITE_1571ST_ROW_ONCE') and
         before('EXCLUSIVE_PRIVATE_ROOT_CLAIM_AND_DURABLE_NO_RETRY_MARKER',
                'OPEN_ONE_USE_SEQPACKET_WITH_PEER_CREDENTIALS') and
         before('CONSUME_FIRST_PROOF_REQUEST_BEFORE_VALIDATION',
                'FSYNC_DURABLE_PROOF_CONSUMPTION_BEFORE_SINGLE_SIGNATURE') and
         before('VERIFY_OS_OUTPUT_CID_NAME_ABSENCE_BEFORE_ANY_PRIVATE_CLEANUP',
                'ELIGIBLE_HELD_PRIVATE_CLEANUP_ONLY_AFTER_EXTERNAL_GATE') and
         design['real_ipc_server'] == 'UNIMPLEMENTED' and
         design['real_issuer'] == 'UNSELECTED' and
         design['premarker_root_exists'] == 'UNKNOWN_CONSUMED_NO_RETRY',
         'ORDER_ONLY')
    for fn in (A.open_signed_scope,A.issue_auth_row,
               A.create_private_policy_or_key,A.launch_context):
        try: fn()
        except A.Refused as exc: need(str(exc).startswith('EFFECT_DISABLED'),
                                     'EFFECT_REFUSAL')
        else: raise RuntimeError('EFFECT_NOT_REFUSED')
    try: A.current_selection(A.utc(source['period_end']))
    except (A.Refused,ValueError): pass
    else: raise RuntimeError('EXPIRED_ACCEPTED')
    check_pin()
    return {'schema':'context-authority-selection-independent-static-audit/v1',
            'verdict':'PASS_BOUNDED_INERT_SELECTION_ONLY',
            'freeze_sha256':sha((HERE/'freeze.json').read_bytes()),
            'selector_freeze_sha256':PIN[LOCAL/'context-successor-final-stage-0004/freeze.json'],
            'policy_freeze_sha256':PIN[LOCAL/'context-policy-topology-0002/freeze.json'],
            'bound_rows':1570,'auth_row':'UNMINTED_UNSELECTED',
            'signed_scope':'NOT_OPENED','issuer':'UNSELECTED',
            'source_period_end':source['period_end'],
            'private_body_read':False,'effect':False}


if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
