"""Audit proposed definition coverage/bindings; this is not a theorem checker."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
N01=HERE.parent
SUCCESSOR=N01.parents[1]
ROOT=SUCCESSOR.parents[5]

def read(path):
    return json.loads(path.read_text())

def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def audit(root=ROOT, package=None, check=None, enforce_workflow=False):
    index=read(HERE/'index.json')
    checked={}
    def verify_bindings(value):
        if isinstance(value,dict):
            if {'path','sha256'} <= value.keys():
                path=root/value['path']
                assert path.is_file(), value['path']
                checked.setdefault(value['path'],hashlib.sha256(path.read_bytes()).hexdigest())
                assert checked[value['path']]==value['sha256'], value['path']
            for child in value.values(): verify_bindings(child)
        elif isinstance(value,list):
            for child in value: verify_bindings(child)
    verify_bindings(index)
    schema=read(HERE/'definition.schema.json'); Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema)
    spec=importlib.util.spec_from_file_location('batch_spec',HERE/'build_batch.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert len(index['units'])==41
    assert [u['unit'] for u in index['units']]==[f'K{i:02}' for i in range(41)]
    qualifiers=[]; conclusions=[]; effects=[]; pending=[]; all_branches=[]
    original_assessments=[]
    for row in index['units']:
        d=read(root/row['definition']['path']); verify_bindings(d); validator.validate(d)
        original=read(root/d['prior_definition']['path'])
        source=read(root/d['source']['path'])['payload']
        assert d['unit']==row['unit'] and d['kind']==original['kind']==source['relation_kind_id']
        assert d['source']==original['source']
        assert d['pending_ids']==original['pending_ids']==row['pending_ids']
        assert d['actual_owner_review'] is None and not d['inherited_discharges']
        assert [q['field'] for q in d['qualifiers']]==[q['field'] for q in original['qualifiers']]
        assert set(q['field'] for q in d['qualifiers'])==set(source['qualifier_contract']['required_axes'])
        assert all(q['interpretation'] and 'record.' not in q['exact_role'] for q in d['qualifiers'])
        assert [c['id'] for c in d['forbidden_conclusions']]==[c['id'] for c in original['forbidden_conclusions']]
        assert [c['label'] for c in d['forbidden_conclusions']]==source['forbidden_inferences']
        for c,old in zip(d['forbidden_conclusions'],original['forbidden_conclusions']):
            assert all(c[k]==old[k] for k in ['predicate','parameter_types','definition','anchor','context_rule'])
            assert '∃ W,e,f.' in c['theorem_target'] and '¬ ' in c['theorem_target']
            assert c['positive_coexistence_allowed'] and 'unproved' in c['proof_status']
        assert d['ordered_pairs']==original['ordered_pairs']==source['allowed_endpoint_pairs']
        assert len(d['branch_matrix'])==row['signature_branch_count']==len(d['ordered_pairs'])
        assert [(b['source_kind'],b['target_kind']) for b in d['branch_matrix']]==[(p['source_kind'],p['target_kind']) for p in d['ordered_pairs']]
        assert all(not b['refinement_proved'] and not b['source_mapping_implemented'] for b in d['branch_matrix'])
        functions=set(re.findall(r'(?<![\w.])([A-Za-z][A-Za-z0-9_]*)\(',d['formal_expression']))
        assert functions <= set(module.ATOMS)|{f'Meaning_{d["unit"]}',f'Base_{d["unit"]}'}, (d['unit'],functions-set(module.ATOMS))
        assert {q['field'] for q in d['qualifiers']} <= set(re.findall(r'\bq\.([a-z_0-9]+)',d['formal_expression']))
        witness_fields=set(re.findall(r'\bw\.([A-Za-z][A-Za-z0-9]*)',d['formal_expression']))
        assert witness_fields <= set(d['notation']['witness_fields']), (d['unit'],witness_fields-set(d['notation']['witness_fields']))
        assert d['plain_language_intuition']['text']==module.SPECS[d['unit']][0] and not d['plain_language_intuition']['normative']
        assert d['source_refinement_gap']==module.SPECS[d['unit']][4]
        if d['unit'] in {'K10','K14','K25'}:
            assert 'f.profile = typedSuccessor' in d['formal_expression']
            assert d['profile_contract']['equivalence_to_stronger_successor_claimed'] is False
        if row['prior_actual_meaning_assessment']:
            ass=read(root/row['prior_actual_meaning_assessment']['path'])
            assert ass['unit']==d['unit'] and ass['status']=='meaning-accepted'
            assert ass['definition']==d['prior_definition']
            original_assessments.append(d['unit'])
        assert row['batch_actual_assessment'] is None
        doc=(root/row['explanation']['path']).read_text()
        assert d['formal_expression'] in doc and d['plain_language_intuition']['text'] in doc
        assert d['worked_cases']['correction'] in doc
        for target in re.findall(r'\]\((/[^)]+)\)',doc): assert Path(target).is_file(), target
        qualifiers.extend(d['qualifiers']); conclusions.extend(d['forbidden_conclusions'])
        effects.append(d['operational_interpretation']['id']); pending.extend(d['pending_ids']);all_branches.extend(d['branch_matrix'])
    assert len(qualifiers)==82 and len({q['id'] for q in qualifiers})==82
    assert len(conclusions)==148 and len({c['id'] for c in conclusions})==148
    assert len(effects)==len(set(effects))==41
    assert original_assessments==['K00','K01','K02','K03']
    assert len(pending)==len(set(pending))==263
    targets=read(HERE/'obligation-targets.json');verify_bindings(targets)
    inherited=read(root/targets['source_inventory']['path'])
    assert set(pending)=={o['id'] for o in targets['rows']}=={o['id'] for o in inherited['obligations']}
    assert Counter(o['category'] for o in targets['rows'])=={'qualifier':74,'effect':41,'forbidden':148}
    assert all(not o['discharged'] and o['original_status']=='pending' for o in targets['rows'])
    assert inherited['retained_discharged_count']==targets['retained_original_discharged']==90
    matrix=read(HERE/'ordered-pair-matrix.json'); verify_bindings(matrix)
    assert matrix['rows']==all_branches and len(all_branches)==550
    assert len({(b['unit'],b['source_kind'],b['target_kind']) for b in all_branches})==550
    fields=read(HERE/'source-field-inventory.json');verify_bindings(fields)
    assert len(fields['schemas'])==109
    assert set(fields['schemas'])=={b[s] for b in all_branches for s in ['source_kind','target_kind']}
    for kind,inventory_row in fields['schemas'].items():
        if inventory_row['status']=='source-schema-not-found': continue
        source=read(root/inventory_row['source']['path'])
        # Independent JSON-tree census catches properties hidden in conditional
        # branches; field inventory is not allowed to cover only the base object.
        stack=[source];count=0
        while stack:
            node=stack.pop()
            if isinstance(node,dict):
                if isinstance(node.get('properties'),dict): count+=len(node['properties'])
                stack.extend(node.values())
            elif isinstance(node,list): stack.extend(node)
        assert count==len(inventory_row['fields']), (kind,count,len(inventory_row['fields']))
        assert len({f['pointer'] for f in inventory_row['fields']})==count
        for field in inventory_row['fields']:
            shape=source
            for token in field['pointer'].split('/')[1:]:
                token=token.replace('~1','/').replace('~0','~')
                shape=shape[int(token)] if isinstance(shape,list) else shape[token]
            assert shape.get('type')==field['type']
    policies=read(HERE/'shared-policies.json')
    assert [p['id'] for p in policies['policies']]==[f'D{i:02}' for i in range(1,9)]
    assert all(p['actual_assessment'] is None for p in policies['policies'])
    bridges=read(HERE/'extension-bridges.json')
    assert [e['id'] for e in bridges['extensions']]==[f'E{i:02}' for i in range(7)]
    assert all(e['actual_assessment'] is None for e in bridges['extensions'])
    response=read(HERE/'review-response-template.json')
    assert all(v is None for key in ['kind_assessments','policy_assessments','extension_bridge_assessments'] for v in response[key].values())
    assert response['actual_user_response'] is None
    assert index['new_theorem_declarations']==index['inherited_discharges']==0 and not index['N01_accepted']
    if (HERE/'review-manifest.json').exists(): verify_bindings(read(HERE/'review-manifest.json'))
    if package is not None:
        verify_bindings(package)
        assert package['definition_count']==41 and package['new_theorem_declarations']==0
    if check is not None:
        check(index)
    if enforce_workflow:
        seq=read(N01/'sequential-review.json');gate=read(N01/'decision-gate.json')
        plan=read(SUCCESSOR/'execution/plan.json'); progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
        assert seq['review_mode']==gate['review_mode']=='consolidated-at-end'
        assert seq['current_unit']==gate['current_unit']==progress['current_review']=='ALL41'
        assert seq['accepted_meaning_count']==progress['actual_scoped_meaning_assessments']==4
        assert gate['actual_response'] is None
        assert all(u['status']=='ready-for-consolidated-review' for u in seq['units'] if u['actual_assessment'] is None)
        assert seq['procedural_response']['answer']=='do all definitions and we change or approve at the end'
    return {'result':'batch-definition-coverage-and-binding-audit-pass','revision':index['revision'],'definition_count':41,'qualifier_fields':82,'pending_qualifier_ids':74,'retained_legacy_qualifier_ids':8,'effect_ids':41,'conclusion_ids':148,'inherited_pending_ids':263,'ordered_pairs':550,'endpoint_kinds':109,'endpoint_schema_fields_inventoried':sum(len(v.get('fields',[])) for v in fields['schemas'].values()),'missing_endpoint_schemas':[k for k,v in fields['schemas'].items() if v['status']=='source-schema-not-found'],'shared_policies':8,'extension_bridges':7,'prior_scoped_assessments':original_assessments,'new_assessments':0,'new_theorem_declarations':0,'inherited_discharges':0,'N01_accepted':False,'distinct_checked_bindings':len(checked),'workflow_checked':enforce_workflow,'authority_effect':'none','limitations':['Structure, exact coverage, binding and specification-vocabulary audit only.','No new Lean compilation, satisfiability proof, original-source refinement, complete countermodel, independent checker run or owner approval.']}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--workflow',action='store_true'); args=parser.parse_args()
    report=audit(enforce_workflow=args.workflow)
    report['driver']=binding(Path(__file__));report['definition_index']=binding(HERE/'index.json')
    (HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
