"""Bound structural checks, distinct from actual Session/application qualification."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v82', BASE / 'api-v83'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def functions(path):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, ast.FunctionDef)}


def main():
    checks = []
    count = 0
    for old in OLD.glob('*.py'):
        before, after = functions(old), functions(API / old.name)
        for name in before:
            if name.startswith('test_'):
                assert after[name] == before[name], name
                count += 1
    assert count == 323
    checks.append({'check': 'all323-original-test-method-ASTs-unchanged', 'result': 'PASS'})
    before = functions(OLD / 'custody_context_sessions.py')
    after = functions(API / 'custody_context_sessions.py')
    for name in ('guard','permission','permission_guard','_open_plan','open_plan','dispose','dispose_all','expire','close_session','persist','history'):
        assert before[name] == after[name], name
    checks.append({'check': 'original-live-guards-permission-opening-eligibility-history-and-disposal-unchanged', 'result': 'PASS'})
    schema = json.loads((API / 'authentication.schema.json').read_bytes())
    old_schema = json.loads((OLD / 'authentication.schema.json').read_bytes())
    assert schema['oneOf'][:-1] == old_schema['oneOf']
    branch = schema['oneOf'][-1]
    properties = branch['properties']
    assert properties['schema_version']['const'] == 'lab-local-lesson-application-policy/v2-candidate'
    assert properties['session_control']['type'] == 'object'
    assert properties['session_control']['properties']['max_session_seconds']['maximum'] == 900
    assert properties['source_name']['const'] == 'custody-participation'
    assert 'scope_control' not in properties
    operations = properties['allowed_operations']['const']
    assert len(operations) == 13 and all(op in operations for op in ('context.get','session.open','session.close','lesson.apply'))
    assert properties['application_control']['properties']['runtime_identities']['additionalProperties'] is False
    checks.append({'check': 'independent-v2-policy-requires-current-participation-real-Session-control-and-closed-identities', 'result': 'PASS'})
    auth = (API / 'auth.py').read_text()
    assert 'metadata=(application and not application_session)' in auth
    assert 'APPLICATION_SESSION_SUPPORTED if application_session' in auth
    assert 'if application_session:fields+=' in auth
    assert "value['session_control'] is not None" in auth
    checks.append({'check': 'application-session-branch-does-not-enter-metadata-null-Session-guard', 'result': 'PASS'})
    for name in ('machine_transport.py','guarded_reads.py','guarded_candidate.py','workspace.py'):
        assert (OLD / name).read_bytes() == (API / name).read_bytes(), name
    checks.append({'check': 'Machine-allowlist-original-pure-guards-and-vault-unchanged', 'result': 'PASS'})
    opened = (API / 'custody_context_sessions.py').read_text()
    assert opened.index('self.reserve_runtime_identities(sid,aid,request)') < opened.index('resource=LiveReader(')
    reservation = after['reserve_runtime_identities']
    assert 'require_outside_scope' in reservation and 'atomic' in reservation and 'memory_persistence_allowed' in reservation
    assert "'runtime identity previously reserved; pending operations require inspection'" in reservation
    checks.append({'check': 'one-use-durable-reservation-precedes-actual-RAM-resource-outside-pure-scope', 'result': 'PASS'})
    profile = json.loads((API / 'contract-profile.json').read_bytes())
    assert len(profile['implemented_operations']) == 23
    for row in profile['files']:assert bind(ROOT / row['path']) == row
    checks.append({'check': 'complete-selected-repository-profile-bytes-current', 'result': 'PASS'})
    paths = [OLD / 'source-manifest.json', API / 'source-manifest.json', API / 'contract-profile.json',
             API / 'auth.py', API / 'authentication.schema.json', API / 'custody_context_sessions.py',
             BASE / 'lesson-application-v2/preparation.py', BASE / 'lesson-application-v2/DESIGN.md',
             RUN / 'context-R03-live-application-composition-0083.json', Path(__file__).resolve()]
    value = {'schema_version':'lab-live-application-authoring-checks/v1-candidate','result':'PASS',
             'checks':checks,'files':[bind(path) for path in paths], 'original_inherited_methods':323,
             'unchanged_method_ASTs':323,'authored_handlers':23,'remaining_handlers':11,
             'actual_runtime_qualified':False,'positive_application_qualified':False,
             'actual_owner_outcome':None,'authority_effect':'none',
             'claim_ceiling':'Exact source/structure checks only; actual authentication, live resource and application episodes require separate evidence.'}
    output = RUN / 'API83-live-application-authoring-checks-0001.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'binding':bind(output)}),flush=True)


if __name__=='__main__':main()
