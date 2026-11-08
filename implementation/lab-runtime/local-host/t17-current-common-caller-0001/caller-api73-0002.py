"""Actual paired calls through the selected common dispatcher.

Trusted CLI selects an API/profile and exact historical provider functions. It
changes caller input construction only, never production permission, time,
source, lifecycle or dispatch callbacks. Unadapted units remain explicit failures.
"""
import argparse
import base64
import copy
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-0277/caller.py'
OLD_SHA = '45ce0d17e61a49855f0dd2735f7ad8cbf0da58dbadc959631bb36095b53b384a'
UNITS = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-selection-0278/selection-plan.json'
UNITS_SHA = '1625d9229d855796a7b32661c4a11a084b37a5352138c193de1ec8069aa0891b'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_original():
    need(sha(OLD.read_bytes()) == OLD_SHA and sha(UNITS.read_bytes()) == UNITS_SHA,
         'selected historical caller/unit definition differs')
    spec = importlib.util.spec_from_file_location('_t17_selected_original_caller', OLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(api, source_pin, profile_pin, unit, output):
    need(sys.dont_write_bytecode and sys.flags.isolated, 'isolated no-bytecode caller required')
    api = Path(api).absolute()
    need(api.parent == ROOT/'product/lab/release-candidates/v1/interface', 'selected common API origin differs')
    units = json.loads(UNITS.read_bytes())['units']
    need(unit in units, 'exact original operation unit required')
    C = load_original()
    C.ROOT, C.BASE, C.API = ROOT, api.parent, api
    C.RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
    C.NAME = C.install('_t17_current_selected_API', api)
    for name, suffix in [('P','protocol'),('G','guard'),('A','auth'),('F','fixtures'),
                         ('H','handlers'),('S','service'),('I','integration_dispatch'),
                         ('W','workspace'),('M','artifact_model'),('EF','example_fixture'),
                         ('PR','projection_refresh')]:
        setattr(C, name, C.module(C.NAME, suffix))
    manifest = C.G.verify(source_pin)
    need(manifest['profile_binding']['sha256'] == profile_pin, 'selected common profile differs')
    C.schemas = C.P.Schemas(profile_pin)
    need(len(C.schemas.operations) == 34, 'exact 34-operation surface required')
    C.UNIT, C.ROOTS, C.FAILURES, C.CASES = unit, set(), [], []
    provider_names = {'base': 'base_episode', 'fixture': 'fixtures_episode', 'transfer': 'fixtures_episode',
        'member:action-governance': 'action_governance_episode', 'member:resolution': 'resolution_episode',
        'member:workflow': 'workflow_episode', 'member:ontology': 'ontology_episode'}
    provider_name = provider_names.get(unit, provider_names.get(unit.split(':')[0]))
    need(provider_name is not None, 'current native lifecycle needs the separately qualified current-family adapter')
    output = Path(output).absolute()
    need(not output.exists() and not output.is_symlink(), 'fresh exclusive caller result required')
    cases, pairs = [], []
    source_guard = lambda: C.G.verify(source_pin)
    def call(surface, request, label, expect, expected_code=None, root=None):
        need(type(surface) is C.I.IntegrationService, 'maintained selected common dispatcher required')
        source_guard()
        operation = request['operation']; row = C.schemas.operations[operation]
        raw = C.P.compact(request)
        need(C.schemas.valid('api-call', request)
             and C.schemas.protocol_valid(row['request_schema']['resource_uri'], request['message']),
             'causal case must reach the actual valid request schema')
        before = C.snapshot(root) if root is not None else None
        started = datetime.now(timezone.utc).isoformat()
        reply = surface.call(raw)
        ended = datetime.now(timezone.utc).isoformat()
        C.W.privacy(reply)
        kind = reply.get('kind'); code = reply.get('message',{}).get('code',reply.get('code'))
        wire = C.schemas.valid('api-reply', reply) if kind else C.schemas.valid('transport-error',reply)
        bound = reply.get('request_binding',{}).get('sha256',reply.get('request_byte_sha256')) == sha(raw)
        profile = kind is not None and reply['contract_profile_binding'] == C.schemas.profile_binding
        uri = row['result_schema' if kind == 'result' else 'error_schema']['resource_uri']
        if operation == 'artifact.inspect' and kind == 'result':
            uri = 'urn:cyberalchemy-lab:protocol:artifact-inspect-result:v2-candidate'
        domain = kind is not None and C.schemas.protocol_valid(uri,reply['message'])
        unchanged = before is None or C.snapshot(root) == before
        semantic = C.positive_semantics(surface,request,reply) if expect == 'result' else None
        passed = (wire and bound and profile and domain and kind == expect
            and (expected_code is None or code == expected_code)
            and (kind != 'error' or code in row['allowed_error_codes'])
            and (expect != 'error' or unchanged) and (expect != 'result' or semantic))
        cases.append({'operation':operation,'case':label,'result':'PASS' if passed else 'FAIL',
            'original_request_base64':base64.b64encode(raw).decode(),'request_sha256':sha(raw),
            'actual_reply':reply,'expected_kind':expect,'expected_code':expected_code,
            'actual_code':code,'started_at':started,'ended_at':ended,
            'schema_valid':bool(wire and domain),'request_binding_valid':bound,'profile_matches':profile,
            'negative_owned_state_unchanged':unchanged if expect == 'error' else None,
            'positive_semantics':semantic,'maintained_common_dispatcher':True})
        need(passed, 'actual operation case failed: '+operation+' / '+label)
        source_guard()
        return reply
    def pair(host, request, root=None, surface=None):
        surface = C.common(host) if surface is None else surface
        negative = copy.deepcopy(request)
        negative['call_id'] = 'call:T17-current-negative:'+uuid.uuid4().hex
        actor = negative['message'].get('actor')
        if isinstance(actor, dict):
            actor['principal_ref'] = 'principal:T17-current-foreign'
            expected, cause = 'unauthorized', 'foreign-Actor-with-current-valid-grant'
        else:
            # Keep the actual current policy, data, schemas, inner request and
            # deadline. Only the outer authenticated opaque reference changes.
            negative['caller_context_ref'] = 'context:T17-current-foreign:'+uuid.uuid4().hex
            expected, cause = 'unauthorized', 'foreign-opaque-reference-with-current-valid-grant'
        call(surface, negative, cause, 'error', expected, root)
        reply = call(surface, request, 'actual-positive-domain-result', 'result', root=root)
        pairs.append({'operation':request['operation'],'causal_negative':cause,
                      'actual_negative_and_positive':True})
        return reply
    # These are untrusted caller construction/observation functions. No Service,
    # Source, channel, clock, permissions or lifecycle callable is replaced.
    C.invoke, C.pair = call, pair
    C.event = lambda value: None
    @contextmanager
    def current_base_fixture(view):
        # Fresh actual source/Reader policy; no archived Assignment or lost
        # installation is selected. This changes fixture inputs only.
        with C.tempfile.TemporaryDirectory(prefix='cal-T17-current-base-') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            C.track(root)
            materials, metadata, target = C.EF.materials_for(view)
            delivery = C.P.source.current_legacy_delivery()
            key, path, pin = C.F.provision(root, C.P.source.CURRENT_LEGACY_NAME,
                materials, metadata, principal=delivery.records.PRINCIPAL,
                projection_control=C.PR.control(view))
            channel = C.A.ReaderChannel(path, pin, C.schemas)
            host = None
            try:
                channel.authenticate(C.F.proof(key, channel.challenge))
                key = None
                host = C.S.Service(view, channel, C.schemas)
                yield host, target, root
            finally:
                if host is not None:
                    host.close()
                channel.close()
    def current_base_episode():
        with C.P.source.replay_source(C.P.source.CURRENT_LEGACY_NAME) as view:
            operation = unit.split(':', 1)[1]
            with current_base_fixture(view) as (host, target, root):
                if operation in ('change.prepare', 'change.validate'):
                    request = C.EF.candidate_call(host, target, operation, key='T17:'+operation)
                    if operation == 'change.prepare':
                        C.align_outer_key(request)
                elif operation == 'artifact.inspect':
                    subject = next(s for s in view.subjects.values() if s['identity']=='product:cyberalchemy-lab')
                    request = C.F.call(host.channel.context, operation, C.H.cut(view),
                        artifact=C.M.artifact_ref(view,subject), include=['body','contract','authority','provenance','gaps'])
                elif operation == 'projection.refresh':
                    seed = C.F.call(host.channel.context,'lab.status',C.H.cut(view))
                    budget = seed['message']['budget']; budget['max_actions'] = 1
                    grant = host.channel.policy['projection_control']
                    message = {'schema_version':'lab-projection-refresh-request/v1-candidate',
                        'request_ref':'request:T17-current-refresh','source_cut':C.H.cut(view),
                        'projector_binding':grant['projector_binding'],
                        'contract_catalog_binding':grant['contract_catalog_binding'],
                        'expected_generation_binding':None,'budget':budget,'authority_effect':'none'}
                    request = C.op_call(host,operation,message,'T17:refresh')
                elif operation == 'operation.inspect':
                    dependency = C.align_outer_key(C.EF.candidate_call(host,target,key='T17:inspection-dependency'))
                    call(C.common(host),dependency,'actual-inspection-prerequisite','result',root=root)
                    request = C.F.call(host.channel.context,operation,None,
                        lookup={'operation':'change.prepare','idempotency_key':dependency['idempotency_key']})
                else:
                    request = C.F.call(host.channel.context,operation,C.H.cut(view))
                pair(host,request,root)
    if unit.startswith('base:'):
        C.base_episode = current_base_episode
    entry = source_pin
    failure = None
    try:
        getattr(C, provider_name)()
        need(not C.FAILURES, 'actual provider failed; inspect bounded terminal failures')
    except Exception as error:
        failure = {'exception':type(error).__name__,'message':str(error),
                   'provider_failures':C.FAILURES,'trace':traceback.format_exc()}
    finally:
        try:
            source_guard()
        except Exception as error:
            failure = {'source_exit_failure':str(error),'prior_failure':failure,
                       'trace':traceback.format_exc()}
    coverage = {op:{'positive':sum(c['operation']==op and c['expected_kind']=='result' and c['result']=='PASS' for c in cases),
                    'negative':sum(c['operation']==op and c['expected_kind']=='error' and c['result']=='PASS' for c in cases)}
                for op in units[unit]['operations']}
    cleanup = all(not path.exists() for path in C.ROOTS)
    passed = failure is None and cleanup and all(v['positive'] and v['negative'] for v in coverage.values())
    result = {'schema_version':'lab-current-common-dispatcher-operation-unit/v1',
        'result':'PASS' if passed else 'FAIL','unit':unit,'source_sha256':source_pin,'profile_sha256':profile_pin,
        'historical_caller_sha256':OLD_SHA,'caller_sha256':sha(Path(__file__).read_bytes()),
        'cases':cases,'pairs':pairs,'coverage':coverage,'failure':failure,'owned_cleanup':cleanup,
        'production_callbacks_changed':False,'original_clock_changed':False,
        'current_native_lifecycle_qualified':False,'whole_API_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None}
    raw = (json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    fd = os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    for name in ('api','source-sha256','profile-sha256','unit','output','deps'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    sys.path.insert(0,args.deps)
    value=execute(args.api,args.source_sha256,args.profile_sha256,args.unit,args.output)
    print(json.dumps({'result':value['result'],'unit':value['unit'],'coverage':value['coverage']}))
    raise SystemExit(0 if value['result']=='PASS' else 1)
