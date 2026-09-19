import copy, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dataset_context', HERE/'import.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
r = m.tool.read
b = r(HERE/'bundle.json')
assert m.build() == b
cap = next(c for c in r(m.CAPS/'imports.json') if c['id'] == m.ID)
for mode in ['profile', 'duplicate', 'rule', 'product']:
    profile = r(HERE/'source/profile.json')
    ontology = copy.deepcopy(b['source_ontology'])
    candidate = copy.deepcopy(cap)
    if mode == 'profile': profile['ontology_id'] = 'wrong'
    elif mode == 'duplicate': ontology['entities'].append(ontology['events'][0])
    elif mode == 'rule': ontology['rules'][0]['statement'] = ''
    else: candidate['capability']['product_ref'] = 'wrong'
    try: m.validate_source(profile, ontology, b['definitions'], candidate)
    except ValueError: pass
    else: raise AssertionError('Invalid source accepted: ' + mode)
assert r(m.STORE/'bundle.json') == b
for ref in b['snapshots']:
    p = m.ROOT/ref['path']
    assert p.read_bytes() == (m.STORE/'source'/p.name).read_bytes()
for ref in b['ontology']['concept_refs']:
    file, ptr = ref.split('#')
    obj = r(m.STORE/file)
    for key in ptr.strip('/').split('/'):
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    assert m.tool.text(obj)
assert b['counts']['named_concepts'] == 34
assert b['counts']['rules'] == 5 and b['counts']['definitions'] == 8
assert b['ontology']['relation_ids'] == [] and 'relations' not in b['source_ontology']
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes() == (m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json', {
    'result': 'PASS', 'authority_effect': 'none', 'runtime_tests_rerun': False,
    'checks': ['source-bound replay and Lab header schemas', 'wrong context binding rejected',
               'duplicate concept rejected', 'empty rule rejected', 'wrong Product reference rejected',
               'stored snapshots and concept pointers resolve', 'source counts and absent typed relationships preserved',
               'capability store unchanged'],
    'bindings': [m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name != 'verification.json']})
print('PASS: eight checks; 34 named concepts, five rules, eight definitions.')
