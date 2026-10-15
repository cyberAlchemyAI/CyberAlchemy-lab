"""Freeze operator typed composition; retain all original public schemas/tests."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT, API = BASE / 'api-v47', BASE / 'api-v48'
COMPOSITION = BASE / 'typed-host-composition-v2'
PIN = '666fcd2bc4f0e77b257a26915d26aab8083a8ac6c252dd9bc0f259a7ede80c62'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def files(path):
    return [p for p in path.rglob('*') if p.is_file()
            and not {'receipts', '__pycache__'} & set(p.parts)
            and p.name not in ('source-manifest.json', 'contract-profile.json')]


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new))


def main():
    assert not API.exists() and not (COMPOSITION / 'source-manifest.json').exists()
    spec = importlib.util.spec_from_file_location('_cal_API48_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify(PIN)
    API.mkdir()
    (API / 'receipts').mkdir()
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    (API / 'typed_preparation.py').write_text('''"""Select the frozen typed host composition from the full host closure."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'typed-host-composition-v2'
NAME='_cal_'+HERE.name.replace('-','_')+'_typed_preparation_v2'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
selected=__import__(NAME+'.preparation',fromlist=['TypedPreparation'])
assert Path(selected.__file__).resolve()==PATH/'preparation.py'
TypedPreparation=selected.TypedPreparation
''')
    replace(API / 'protocol.py', "FAILURE_SUPPORTED=METADATA_SUPPORTED+('failure.assess',)",
            "FAILURE_SUPPORTED=METADATA_SUPPORTED+('failure.assess',)\nTYPED_SUPPORTED=METADATA_SUPPORTED+('typed.extension.prepare',)")
    replace(API / 'protocol.py', "SUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review','classification.prepare','failure.assess')",
            "SUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review','classification.prepare','failure.assess','typed.extension.prepare')")
    path = API / 'authentication.schema.json'
    authentication = json.loads(path.read_bytes())
    original_authentication = copy.deepcopy(authentication)
    typed = copy.deepcopy(authentication['oneOf'][-1])
    assert typed['properties']['schema_version']['const'] == 'lab-local-failure-candidate-policy/v1-candidate'
    typed['properties']['schema_version']['const'] = 'lab-local-typed-extension-candidate-policy/v1-candidate'
    typed['properties']['purpose']['const'] = 'durable-metadata-and-exact-typed-extension-preparation'
    typed['properties']['allowed_operations']['const'][-1] = 'typed.extension.prepare'
    typed['properties']['typed_control'] = typed['properties'].pop('failure_control')
    typed['required'][typed['required'].index('failure_control')] = 'typed_control'
    authentication['oneOf'].append(typed)
    assert authentication['oneOf'][:-1] == original_authentication['oneOf']
    path.write_text(json.dumps(authentication, sort_keys=True, indent=2) + '\n')
    replace(API / 'auth.py', "        metadata=export or review or classification or failure or value['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate'",
            "        typed=value['schema_version']=='lab-local-typed-extension-candidate-policy/v1-candidate'\n        metadata=export or review or classification or failure or typed or value['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate'")
    replace(API / 'auth.py', "        if failure:fields+=['failure_control']",
            "        if failure:fields+=['failure_control']\n        if typed:fields+=['typed_control']")
    replace(API / 'auth.py', "'lab-local-classification-candidate-policy/v1-candidate','lab-local-failure-candidate-policy/v1-candidate')",
            "'lab-local-classification-candidate-policy/v1-candidate','lab-local-failure-candidate-policy/v1-candidate','lab-local-typed-extension-candidate-policy/v1-candidate')")
    replace(API / 'auth.py', 'FAILURE_SUPPORTED if failure else METADATA_SUPPORTED if metadata else LEGACY_SUPPORTED',
            'FAILURE_SUPPORTED if failure else TYPED_SUPPORTED if typed else METADATA_SUPPORTED if metadata else LEGACY_SUPPORTED')
    replace(API / 'auth.py', '        borrowed=FACT_SCOPE.policy_scope(self)', '''        if typed:
            from .workspace import read_private
            selected=value['typed_control']['routing_binding']
            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'typed routing object namespace differs')
            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))
            source.require(source.sha(selected_raw)==selected['sha256'],'independent typed routing bytes changed')
        borrowed=FACT_SCOPE.policy_scope(self)''')
    replace(API / 'auth.py', "'durable-metadata-and-exact-failure-preparation' if failure else 'durable-metadata-and-exact-candidate-preparation'",
            "'durable-metadata-and-exact-failure-preparation' if failure else 'durable-metadata-and-exact-typed-extension-preparation' if typed else 'durable-metadata-and-exact-candidate-preparation'")
    replace(API / 'service.py', 'from .failure_preparation import FailurePreparation, FailureRuleFailure',
            'from .failure_preparation import FailurePreparation, FailureRuleFailure\nfrom .typed_preparation import TypedPreparation')
    replace(API / 'service.py', "'classification_preparation.py','failure_preparation.py')", "'classification_preparation.py','failure_preparation.py','typed_preparation.py')")
    replace(API / 'service.py', '    def error(self,call,raw,message_raw,error):', '''    def select_typed(self,message,outer,key):
        from .guarded_candidate import selection
        with selection(self):
            selected=self.channel.policy_guard().get('typed_control')
            if selected is None:
                raise ApplicationError('closure-missing','Independently selected typed routing is unavailable in this owned workspace.')
            try:
                path=HERE/'source-manifest.json'
                builder=TypedPreparation(self,copy.deepcopy(selected['routing_binding']),
                    {'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                builder.preflight(message,outer,key)
                return builder
            except ApplicationError:raise
            except Exception:
                raise ApplicationError('invalid-contract','Exact typed routing, source cut, Actor, scope, key or proposal could not be verified.')
    def error(self,call,raw,message_raw,error):''')
    replace(API / 'service.py', "'handler_binding':binding(str((HERE/'failure_preparation.py').relative_to(ROOT))",
            "'handler_binding':binding(str((HERE/'typed_preparation.py').relative_to(ROOT)),(HERE/'typed_preparation.py').read_bytes()) if call['operation']=='typed.extension.prepare' else binding(str((HERE/'failure_preparation.py').relative_to(ROOT))")
    replace(API / 'service.py', "'proposal.review','classification.prepare','failure.assess')",
            "'proposal.review','classification.prepare','failure.assess','typed.extension.prepare')")
    replace(API / 'service.py', "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])",
            "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='typed.extension.prepare':typed_builder=self.select_typed(message,call['expected_source_cut'],call['idempotency_key'])")
    replace(API / 'service.py', "                elif name=='classification.prepare':\n                    try:domain,evidence=classification_builder.prepare",
            "                elif name=='typed.extension.prepare':domain,evidence=typed_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='classification.prepare':\n                    try:domain,evidence=classification_builder.prepare")
    retained, changed = [], []
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        if target.read_bytes() != path.read_bytes():
            changed.append(path.relative_to(PARENT).as_posix())
        if path.suffix == '.py':
            assert methods(path) == methods(target)
            retained.extend(path.relative_to(PARENT).as_posix() + ':' + name for name in methods(path))
    assert sorted(changed) == ['auth.py', 'authentication.schema.json', 'protocol.py', 'service.py']
    assert len(retained) == 293
    for path in files(API):
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    context = RUN / 'context-R03-typed-host-API-0048.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 authenticated operator typed extension preparation',
        'strict_coverage': 'PASS', 'blockers': [], 'source_bindings': [bind(PARENT / 'source-manifest.json'), bind(RUN / 'authorization.json'),
            bind(BASE / 'typed-host-composition-v1/source-manifest.json'), bind(BASE / 'typed-extension-preparation-v11/source-manifest.json'),
            bind(BASE / 'typed-extension-preparation-v11/receipts/proof-0001.json')],
        'write_scope': [API.relative_to(ROOT).as_posix(), COMPOSITION.relative_to(ROOT).as_posix()],
        'constraints': ['Original34 public contracts and293 original test methods retained.',
            'Authenticated operator only; assigned Agent participation remains unqualified.',
            'Real policy reads/clocks, original journal/retry/recovery and pure source exits retained.',
            'Complete current catalog, exact prospective schemas/cores and independently resolved affected successors.',
            'No source transaction, scope grant, semantic owner verdict, activation or R08 admission.'],
        'validation_surface': 'Closed routing selection and policy schema checks; full actual public typed and all original successor suites remain necessary.',
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    helper = json.loads((BASE / 'typed-extension-preparation-v11/source-manifest.json').read_bytes())
    composition_inputs = list(helper['files']) + [bind(path) for path in [
        BASE / 'typed-host-composition-v1/source-manifest.json', BASE / 'typed-extension-preparation-v11/source-manifest.json',
        BASE / 'typed-extension-preparation-v11/receipts/proof-0001.json', context, Path(__file__).resolve()]]
    put(COMPOSITION / 'source-manifest.json', {'schema_version': 'lab-typed-host-composition-source/v2-candidate',
        'files': [bind(p) for p in sorted(files(COMPOSITION))], 'input_bindings': composition_inputs,
        'operator_composition_authored': True, 'assigned_Agent_qualified': False, 'public_handler_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(PARENT)) if (ROOT / row['path']).is_relative_to(PARENT) else row
                        for row in profile['files']]
    profile['files'].append(bind(API / 'typed_preparation.py'))
    profile['implemented_operations'].append('typed.extension.prepare')
    assert len(profile['implemented_operations']) == 17
    profile['typed_composition_context_binding'] = bind(context)
    profile['typed_composition_source_binding'] = bind(COMPOSITION / 'source-manifest.json')
    profile['claim_ceiling'] = 'Seventeen authored handlers. Operator typed host composition is unqualified; original full suites, assigned Agent and authority resolver obligations remain.'
    put(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}
    for row in composition_inputs:
        rows[row['path']] = row
    for path in files(API) + files(COMPOSITION) + [PARENT / 'source-manifest.json', context, Path(__file__).resolve(),
                                                  API / 'contract-profile.json', COMPOSITION / 'source-manifest.json']:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row
    put(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(PARENT / 'source-manifest.json'), 'context_binding': bind(context),
        'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 293,
        'typed_composition_source_binding': bind(COMPOSITION / 'source-manifest.json'),
        'whole_API_qualified': False, 'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'composition_source_binding': bind(COMPOSITION / 'source-manifest.json'),
        'unchanged_original_methods': 293, 'authored_handlers': 17, 'public_typed_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
