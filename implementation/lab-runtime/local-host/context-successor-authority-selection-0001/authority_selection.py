"""Pure actual-Mapper Context authority selection; every effect is refused."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
SELECTOR = LOCAL/'context-successor-final-stage-0004'
POLICY = LOCAL/'context-policy-topology-0002'
SELECTOR_FREEZE = SELECTOR/'freeze.json'
SELECTOR_REVIEW = LOCAL/'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0004.md'
POLICY_FREEZE = POLICY/'freeze.json'
POLICY_REVIEW = LOCAL/'CONTEXT-POLICY-TOPOLOGY-INDEPENDENT-STATIC-REVIEW-0002.md'
SELECTOR_CODE = SELECTOR/'final_stage.py'
POLICY_CODE = POLICY/'adapter.py'
SELECTOR_FREEZE_SHA = 'b96908371b064fa0fd90e398a8dfbe3023cf83cb99175dacb3393d08f02ed984'
SELECTOR_REVIEW_SHA = '44d9681c9b1eefa4f28479e4a27133428c6d735c4f32325203dbd80e2a1d12f6'
POLICY_FREEZE_SHA = '2c6e5ab3ccb94d5709b585d1307b30f47c101bed5b456db6638c0a333e61839c'
POLICY_REVIEW_SHA = '992803813ea297b43bdd4b66b3abfd2a676d05a20e383104bb46d066d48cc94a'
SELECTOR_CODE_SHA = '559d2b2255293deceb4bee862cfcb4f04c23a7159277ad8952994a20bbbd2668'
POLICY_CODE_SHA = '33b0c587689771caa61fbc61c638e23e09d4d023fd0c8a935473ae073f4ed826'
SOURCE_PERIOD_SHA = '3ff862090a38b346a384001c2d87da7cf648f18726fb056653a0fb4df40473ba'
SOURCE_REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
READER_REVIEW_SHA = 'c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295'
MAPPER_REVIEW_SHA = '5676b6b6ea2d45981ea9db637cde240a86a94983afc3411ee2eb3287e9c6b13f'
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
AUTH_PATH = SOURCE_ROLE+'/authorization/context-development.json'
SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'
PERIOD_REF = 'protocol:R03-docker-source-20261020-0002-period/v1'
CLAIM = 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'
EFFECT_ENABLED = False


class Refused(ValueError): pass


def need(ok,code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,
                       allow_nan=False)+'\n').encode()


def read_pin(path,digest,limit=2*1024*1024):
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and not(before.st_mode & 0o022) and
             0 < before.st_size <= limit,'PIN_SHAPE')
        raw = os.read(fd,before.st_size+1)
        after = os.fstat(fd)
        key = lambda st:(st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_size,
                         st.st_mtime_ns,st.st_ctime_ns)
        need(len(raw) == before.st_size and key(before) == key(after) and
             sha(raw) == digest,'PIN_DRIFT')
        return raw
    finally:
        os.close(fd)


def parse(raw):
    def pairs(rows):
        value = {}
        for key,item in rows:
            need(key not in value,'DUPLICATE_KEY')
            value[key] = item
        return value
    try:
        value = json.loads(raw,object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               Refused('NONFINITE_JSON')))
    except (ValueError,UnicodeError,RecursionError) as exc:
        raise Refused('INVALID_JSON') from exc
    need(type(value) is dict,'JSON_OBJECT')
    return value


def checked_modules():
    selector_freeze = parse(read_pin(SELECTOR_FREEZE,SELECTOR_FREEZE_SHA,65536))
    selector_review = read_pin(SELECTOR_REVIEW,SELECTOR_REVIEW_SHA,262144)
    policy_freeze = parse(read_pin(POLICY_FREEZE,POLICY_FREEZE_SHA,65536))
    policy_review = read_pin(POLICY_REVIEW,POLICY_REVIEW_SHA,262144)
    need(selector_freeze['schema'] == 'context-successor-final-stage-freeze/v1' and
         selector_freeze['version'] == '0004' and
         selector_freeze['effect_enabled'] is False and
         selector_freeze['context_effect'] == 'UNRUN' and
         selector_freeze['members']['final_stage.py'] == SELECTOR_CODE_SHA and
         selector_freeze['mapper_effect_review_sha256'] == MAPPER_REVIEW_SHA and
         b'**Verdict: PASS_BOUNDED_ACTUAL_MAPPER_SELECTION_ONLY.**' in selector_review and
         SELECTOR_FREEZE_SHA.encode() in selector_review,
         'SELECTOR_REVIEWED_SCOPE')
    need(policy_freeze['schema'] == 'context-policy-topology-freeze/v2' and
         policy_freeze['effect_enabled'] is False and
         policy_freeze['docker_or_authority_effect'] == 'NOT_RUN' and
         policy_freeze['bindings']['adapter.py'] == POLICY_CODE_SHA and
         b'**Verdict: PASS for the bounded pure correction;' in policy_review and
         POLICY_FREEZE_SHA.encode() in policy_review,
         'POLICY_REVIEWED_SCOPE')
    modules = []
    for name,path,digest in [('actual_mapper_selector',SELECTOR_CODE,SELECTOR_CODE_SHA),
                             ('reviewed_policy_model',POLICY_CODE,POLICY_CODE_SHA)]:
        raw = read_pin(path,digest)
        module = types.ModuleType(name)
        module.__file__ = str(path)
        exec(compile(raw,str(path),'exec'),module.__dict__)
        modules.append(module)
    selector,policy = modules
    need(selector.EFFECT_ENABLED is False and policy.EFFECT_ENABLED is False and
         selector.SOURCE_ROLE == SOURCE_ROLE and
         selector.SOURCE_PERIOD_SHA == SOURCE_PERIOD_SHA and
         selector.SOURCE_REVIEW_SHA == SOURCE_REVIEW_SHA and
         selector.READER_REVIEW_SHA == READER_REVIEW_SHA,
         'SELECTED_MODULE_IDENTITY')
    return selector,policy


def utc(value):
    need(type(value) is str,'UTC_TEXT')
    try: parsed = dt.datetime.fromisoformat(value)
    except ValueError as exc: raise Refused('UTC_TEXT') from exc
    need(parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(),
         'UTC_OFFSET')
    return parsed


def current_selection(now=None,*,modules=checked_modules):
    now = now or dt.datetime.now(dt.timezone.utc)
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(),'CURRENT_UTC')
    selector,policy = modules()
    selected = selector.select_after_mapper(now)
    source = selector.source_reader_preflight(now)['source']
    topo = policy.topology()
    rows = selected['bound_rows']
    need(selected['status'] == 'IN_MEMORY_FINAL_STAGE_AND_AUTHORITY_PLAN_ONLY' and
         selected['effect_enabled'] is False and
         selected['bound_file_count'] == len(rows) == 1570 and
         selected['final_count_with_auth'] == 1571 and
         len({r['path'] for r in rows}) == 1570 and
         selected['auth_placeholder'] ==
         {'path':AUTH_PATH,'sha256':'UNMINTED_UNSELECTED','mode':'0600'} and
         AUTH_PATH not in {r['path'] for r in rows} and
         selected['mapper_effect_review_sha256'] == MAPPER_REVIEW_SHA and
         selected['source_period_sha256'] == SOURCE_PERIOD_SHA and
         selected['protected_archive_metadata']['body'] == 'UNOPENED' and
         selected['signed_scope'] == 'NOT_OPENED' and
         selected['authorization'] == 'UNMINTED' and
         selected['docker_effect'] == 'REFUSED',
         'ACTUAL_1570_AUTH_PLACEHOLDER')
    need(source['status'] == 'SOURCE_PUBLIC_EFFECT_REVIEWED' and
         source['period_ref'] == PERIOD_REF and
         source['period_sha256'] == SOURCE_PERIOD_SHA and
         source['source_effect_review_sha256'] == SOURCE_REVIEW_SHA and
         source['scope_ref'] == SCOPE and
         source['scope_attestation'] == 'NOT_OPENED_SIGNED_SOURCE_VIEW' and
         utc(source['period_start']) <= now < utc(source['period_end']),
         'CURRENT_UNATTESTED_SOURCE_SCOPE')
    stage = selected['topology']
    need(topo['effect_enabled'] is False and
         topo['host_private_root'] == stage['private_root'] and
         topo['source_host'] == stage['stage_root'] and
         topo['source_child'] == '/workspace' and
         topo['child_policy_root'] == '/context-policy' and
         topo['additional_bind'] == {'source':stage['private_root'],
                                    'target':'/context-policy','read_only':True} and
         topo['private_key'] == 'PARENT_MEMORY_ONLY_NEVER_MOUNTED' and
         selected['context_output']['parent_access'] == 'HELD_WRITER_ONLY' and
         selected['workspace_mount_mode'] == 'ro',
         'SIX_BIND_PRIVATE_TOPOLOGY')
    return {'status':'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD',
            'effect':'NOT_RUN','stage':selected,'source':source,
            'policy_topology':topo,
            'required_signed_scope':{
                'status':'NOT_OPENED_REQUIRES_REVIEWED_READER_SIGNED_VIEW',
                'scope_ref':SCOPE,'period_ref':PERIOD_REF,
                'source_manifest_sha256':source['source_manifest_sha256'],
                'source_package_manifest_sha256':source['source_package_manifest_sha256'],
                'source_effect_review_sha256':SOURCE_REVIEW_SHA,
                'reader_effect_review_sha256':READER_REVIEW_SHA},
            'issuer':'UNSELECTED','auth_row':'UNMINTED_UNSELECTED',
            'private_root':'UNCREATED','proof':'UNSERVED',
            'currentness':'CHECKED_NOW_NO_FUTURE_DISPATCH_AUTHORITY'}


def auth_template(selection,now,*,modules=checked_modules):
    """Exact bytes a future issuer must assess; never an issued AUTH row."""
    need(type(selection) is dict and
         selection.get('status') == 'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD' and
         selection.get('auth_row') == 'UNMINTED_UNSELECTED' and
         type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(),'UNISSUED_SELECTION_ONLY')
    selector,_ = modules()
    fresh = selector.source_reader_preflight(now)['source']
    need(selection['source'] == fresh and
         selection['stage']['source_period_sha256'] == SOURCE_PERIOD_SHA and
         selection['stage']['auth_placeholder']['sha256'] == 'UNMINTED_UNSELECTED',
         'CURRENT_SOURCE_RECHECK')
    end = min(now+dt.timedelta(minutes=20),utc(fresh['period_end']))
    need(utc(fresh['period_start']) <= now < end,'SOURCE_PERIOD_EXPIRED')
    value = {'schema_version':'lab-context-development-authorization/v1-candidate',
             'family_ref':selection['stage']['topology']['context_family_ref'],
             'episode_ref':PERIOD_REF,'scope_ref':SCOPE,
             'period_binding':{'path':SOURCE_ROLE+'/packages/0001/period.json',
                               'sha256':SOURCE_PERIOD_SHA},
             'not_before':now.isoformat(),'expires_at':end.isoformat(),
             'authority_effect':'none','actual_owner_outcome':None,
             'claim_ceiling':CLAIM}
    raw = canonical(value)
    return {'status':'UNTRUSTED_UNISSUED_AUTH_TEMPLATE_ONLY',
            'path':AUTH_PATH,'mode':'0600','sha256':sha(raw),
            'bytes':raw,'would_be_final_count':1571,
            'actual_bound_count':1570,'issuer':'UNSELECTED',
            'signed_scope':'NOT_OPENED','effect':'NOT_RUN'}


ORDER = (
    'RECHECK_ACTUAL_1570_AND_SOURCE_PERIOD',
    'REVIEWED_READER_OPEN_SIGNED_SOURCE_SCOPE',
    'SELECT_CURRENT_DISPOSABLE_ISSUER_AND_EXACT_AUTH_SCOPE',
    'HOLD_NOFOLLOW_STAGE_PARENT_AND_EXCLUSIVE_ROOT_CLAIM',
    'DURABLE_NO_RETRY_STAGE_MARKER_BEFORE_CONTENT',
    'COPY_AND_REHASH_1570_BOUND_ROWS_WITH_PRIVATE_BODY_CUSTODY',
    'RECHECK_PERIOD_SIGNED_SCOPE_AND_ISSUER_BEFORE_AUTH_EFFECT',
    'ISSUE_EXACT_AUTH_AND_WRITE_1571ST_ROW_ONCE',
    'EXCLUSIVE_PRIVATE_ROOT_CLAIM_AND_DURABLE_NO_RETRY_MARKER',
    'CREATE_PARENT_ONLY_EPHEMERAL_KEY_AND_DURABLE_POLICY_0600',
    'VERIFY_SIX_RO_BINDS_AND_PARENT_HELD_OUTPUT_WRITER',
    'OPEN_ONE_USE_SEQPACKET_WITH_PEER_CREDENTIALS',
    'CONSUME_FIRST_PROOF_REQUEST_BEFORE_VALIDATION',
    'FSYNC_DURABLE_PROOF_CONSUMPTION_BEFORE_SINGLE_SIGNATURE',
    'RECHECK_PERIOD_AND_AUTH_READBACK_BEFORE_CONTEXT_DISPATCH',
    'RUN_CONTEXT_AND_RETAIN_PRIVATE_POLICY_THROUGH_EXTERNAL_REVIEW',
    'VERIFY_OS_OUTPUT_CID_NAME_ABSENCE_BEFORE_ANY_PRIVATE_CLEANUP',
    'ELIGIBLE_HELD_PRIVATE_CLEANUP_ONLY_AFTER_EXTERNAL_GATE',
)


def ordered_design(selection):
    need(selection['status'] == 'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD' and
         selection['auth_row'] == 'UNMINTED_UNSELECTED' and
         selection['policy_topology']['transport'] ==
         'SEPARATELY_SELECTED_ONE_USE_PROOF_SEQPACKET_ON_CONTROL',
         'ORDER_SELECTION')
    return {'schema':'context-successor-authority-order/v1-inert',
            'steps':list(ORDER),'no_retry_after_root_claim':True,
            'no_retry_after_first_proof_request':True,
            'premarker_root_exists':'UNKNOWN_CONSUMED_NO_RETRY',
            'policy_retained_until_external_gate':True,
            'real_ipc_server':'UNIMPLEMENTED','real_issuer':'UNSELECTED',
            'signed_scope':'NOT_OPENED','effect':'NOT_RUN'}


def open_signed_scope(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_REVIEWED_SIGNED_SOURCE_OPEN')


def issue_auth_row(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CURRENT_ISSUER_OR_GRANT')


def create_private_policy_or_key(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_KEY_POLICY_OR_SERVER')


def launch_context(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_DOCKER')


if __name__ == '__main__':
    if sys.argv[1:] != ['--preview']:
        raise SystemExit('expected --preview')
    selected = current_selection()
    design = ordered_design(selected)
    print(json.dumps({'status':selected['status'],'bound_rows':1570,
                      'auth_row':selected['auth_row'],
                      'source_period_end':selected['source']['period_end'],
                      'signed_scope':selected['required_signed_scope']['status'],
                      'real_issuer':design['real_issuer'],'effect':'NOT_RUN'},
                     sort_keys=True))
