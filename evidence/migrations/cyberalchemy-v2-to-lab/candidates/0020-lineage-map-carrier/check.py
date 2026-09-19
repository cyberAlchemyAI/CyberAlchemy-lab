"""Inspect selected legacy-to-successor mappings without transferring authority."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, PACKAGE, load, sha, need

def read_input(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'Duplicate JSON key: '+key); result[key]=value
        return result
    def invalid(value): raise ValueError('Invalid JSON constant: '+value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=invalid)

def resolve(ref):
    path=(LAB/ref['path']).resolve()
    need(path.is_relative_to(LAB.resolve()),'Binding escapes Lab')
    need(sha(path)==ref['sha256'],'Bound bytes changed: '+ref['path'])
    return path

def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']+load(ROOT/'dependencies.json')['inputs']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    normalization_path=resolve(record['normalization']); index_path=resolve(record['target_index'])
    need(normalization_path==LAB/'docs/normalizations/0001-definition-migration-model/normalization.json','Unsupported normalization')
    need(index_path==ROOT.parent/'0003-review-led-reconstruction/target-candidate-index.json','Unsupported target index')
    decisions={x['legacy_id']:x for x in read_input(normalization_path)['migration_decisions']}
    index={x['target_id']:x for x in read_input(index_path)['entries']}
    mappings={x['legacy_id']:x for x in record['mappings']}
    need(len(mappings)==len(record['mappings']),'Duplicate legacy mapping')
    need(set(mappings)==set(record['coverage']),'Coverage mismatch')
    results=[]
    for legacy,mapping in mappings.items():
        need(legacy in decisions,'Unknown legacy identity')
        decision=decisions[legacy]
        need(mapping['disposition']==decision['decision'],'Disposition differs from normalization')
        targets=[x['target_id'] for x in mapping['successors']]
        need(len(targets)==len(set(targets)),'Duplicate successor')
        need(set(targets)==set(decision['targets']),'Successor set differs from normalization')
        successors=[]
        for successor in mapping['successors']:
            target_id=successor['target_id']; need(target_id in index,'Unknown successor')
            entry=index[target_id]; path=resolve(successor['binding'])
            need(path==(index_path.parent/entry['machine_path']).resolve() and successor['binding']['sha256']==entry['machine_sha256'],'Successor differs from indexed target')
            target=read_input(path)
            need(target['target_id']==target_id and target['status']==entry['status'],'Successor identity or status mismatch')
            need(target['authority_effect']=='none','Unexpected target authority effect')
            successors.append({'target_id':target_id,'binding':successor['binding'],'recorded_status':target['status']})
        results.append({'legacy_id':legacy,'disposition':mapping['disposition'],'successors':successors,'selection_required':len(successors)>1})
    return {'map_id':record['map_id'],'coverage':record['coverage'],'mappings':results,'mapping_conforms':True,'authority_effect':'none','authority_transferred':False,'identity_equivalence_proven':False,'current_admission_resolved':False,'claim_ceiling':'Selected normalized identities and exact prototype successors only; no automatic selection, identity equivalence or authority transfer.'}

if __name__=='__main__':
    try:
        need(len(sys.argv) in [2,3],'Usage: check.py lineage-map-record.json [legacy-id]')
        result=assess(read_input(Path(sys.argv[1])))
        if len(sys.argv)==3:
            need(sys.argv[2] in result['coverage'],'Legacy identity outside declared coverage')
            result['mappings']=[x for x in result['mappings'] if x['legacy_id']==sys.argv[2]]
        code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
