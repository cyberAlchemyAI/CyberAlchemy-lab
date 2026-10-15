"""Before-effect closure for exact O03 candidate controls and original obligations."""
from common import *
def freeze():
    p=HERE/'packages/0001';p.mkdir(parents=True,exist_ok=False)
    paths=sorted(HERE.glob('*.py'))+sorted((HERE/'contracts').glob('*.json'))+[HERE/'DESIGN.md']
    context=load(RUN/'context-O03.json')
    for b in context['source_bindings']:original(b)
    result={'schema_version':'lab-O03-query-selection/v1-candidate','task':'O03','authority_effect':'none','actual_owner_outcome':None,
        'context_binding':bind(RUN/'context-O03.json'),'authorization_binding':bind(RUN/'authorization.json'),
        'files':[bind(p) for p in paths],'source_bindings':context['source_bindings'],
        'original_acceptance':'Three source-backed questions reproducible; exact gaps/exclusions returned; mapped/unmapped coverage accounts for declared scope.',
        'native_rebuild_binding':bind(PACKAGE/'queries/attempts/0001/native-build.json'),'native_graph_acceleration_selected':False,
        'predecessor_binding':bind(PACKAGE/'queries/successors/0003/packages/0001/selection.json'),
        'historical_source_relocation_binding':bind(ROOT/'authority/admissions/project-state-bootstrap/v1/registries/definition-registry.json'),
        'semantic_model':'Deterministic Python query graph; native reader verifies O05 original events and exact joins only.',
        'operational_activation':False,'canonical_admission':False,'new_action_permission':False}
    emit(p/'selection.json',result);return bind(p/'selection.json')
def verify(pin):
    require(type(pin) is dict and set(pin)=={'path','sha256'},'independent selection binding required')
    manifest=parse(original(pin));require(manifest['schema_version']=='lab-O03-query-selection/v1-candidate' and manifest['task']=='O03'
        and manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,'query selection cannot invent authority')
    actual={bind(p)['path'] for p in HERE.glob('*.py')}|{bind(p)['path'] for p in (HERE/'contracts').glob('*.json')}|{bind(HERE/'DESIGN.md')['path']}
    require(actual=={b['path'] for b in manifest['files']},'query control file closure differs')
    for b in manifest['files']+manifest['source_bindings']+[manifest['context_binding'],manifest['authorization_binding'],manifest['native_rebuild_binding'],manifest['predecessor_binding'],manifest['historical_source_relocation_binding']]:original(b)
    return manifest
if __name__=='__main__':print(json.dumps(freeze(),sort_keys=True))
