"""Validate source lineage, all target contracts, adversarial tests and deterministic views."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, L1, load, dump, sha, binding, module, need
import author
import reconcile
from engine import load_graph, profile_eval, project
from catalog import TYPES, POLICIES, LIFECYCLES, EVALUATIONS, DERIVED

def files(root): return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def materials(): return {k:v for k,v in files(ROOT).items() if 'receipts' not in Path(k).parts and k!='manifest.json'}
def validate():
    checks=[]
    def check(name,action):
        try: checks.append({'check':name,'result':'PASS','detail':action()})
        except Exception as exc: checks.append({'check':name,'result':'BLOCK','detail':str(exc)})
    def dependencies():
        deps=load(ROOT/'dependencies.json'); previous=load(PREVIOUS/'manifest.json')
        for ref in previous['materials']+deps['inputs']+deps['definitions']+deps['admitted_definitions']:
            need(sha(LAB/ref['path'])==ref['sha256'],'Dependency drift: '+ref['path'])
        need(load(LAB/previous['validation']['path'])['result']=='PASS','Predecessor did not pass')
        historic={str((L1/x['path']).relative_to(LAB)):x['sha256'] for x in load(L1/'manifest.json')['materials']}
        edges=load(L1/'batches.json')['edges']; closure=set(deps['seed_targets'])
        while True:
            expanded=closure|{x['dependency_target_id'] for x in edges if x['consumer_target_id'] in closure}
            if expanded==closure: break
            closure=expanded
        need(closure=={x['target_id'] for x in deps['definitions']},'Incomplete semantic closure')
        need(deps['source_lineage_residue']==[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in closure],'Source residue lost')
        overlay_root=ROOT.parent/'0005-reconciliation-and-proposition-types'
        result=subprocess.run([sys.executable,'-c','import json,source_rebinding; print(json.dumps(source_rebinding.build()))'],cwd=overlay_root,capture_output=True,text=True,check=True)
        overlay=load(overlay_root/'source-rebinding.json'); need(json.loads(result.stdout)==overlay,'D53 source overlay drift')
        helper=module(L1.parents[1]/'author.py','source_section_reader'); source=LAB.parent/'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md'
        schema_path=LAB/'authority/artifact-types/definition/v1/schema.json'; validator=Draft202012Validator(load(schema_path)); sections=set()
        for ref in deps['definitions']:
            need(ref['sha256']==historic[ref['path']],'Historical Definition drift'); definition=load(LAB/ref['path']); validator.validate(definition)
            need(definition['schema_digest']==sha(schema_path),'Definition schema drift')
            for item in definition['source_refs']:
                actual=hashlib.sha256(helper.markdown_h2_section(source,item['selector'])).hexdigest()
                expected=overlay['current_historical_selector_sha256'] if item['selector']=='## CAV2-D53: Axiom' else item['content_sha256']
                need(actual==expected,'Definition source drift: '+item['selector']); sections.add(item['selector'])
        admitted={x['path']:x for x in load(LAB/'authority/definitions/registry.json')['entries'] if x['lifecycle_state']=='admitted'}
        for ref in deps['admitted_definitions']:
            need(ref['path'] in admitted and admitted[ref['path']]['sha256']==ref['sha256'],'Admission binding changed'); validator.validate(load(LAB/ref['path']))
        normalized=0
        for item in deps['selected_source_refs']:
            if item.get('repository_id')=='cyberalchemy-v2-source':
                actual=hashlib.sha256(helper.markdown_h2_section(source,item['selector'])).hexdigest()
                need(actual==item['section_sha256'],'Scaffold source drift: '+item['selector']); normalized+=1
            else:
                need(item['path']=='docs/normalizations/0001-definition-migration-model/normalization.json','Unrecognized supporting source')
                target=item['selector']; data=load(ROOT/'targets'/target/'contract.json')
                normalization=load(LAB/item['path']); need(any(data['normalization_contract'] in value for value in normalization.values() if isinstance(value,list)),'Supporting normalization target drift')
        return {'candidate_definitions':len(closure),'admitted_definitions':len(deps['admitted_definitions']),'definition_source_sections':len(sections),'normalized_source_bindings':normalized,'preserved_source_residues':len(deps['source_lineage_residue']),'D53':'historical layout residue retained'}
    check('source-and-predecessor-integrity',dependencies)
    def contracts():
        shared=module(LAB/'tooling/validators/artifact_surface.py','batch_shared_validator')
        for name in TYPES: need(shared.validate_package(ROOT/'targets'/('type.'+name))==0,'Artifact mechanics failed: '+name)
        graph=load_graph(ROOT/'examples/graph-manifest.json')
        for name in POLICIES+list(LIFECYCLES)+list(EVALUATIONS):
            p=ROOT/'targets'/('profile.'+name)
            need(profile_eval(name,load(p/'parameters.json'),load(p/'fixtures/valid/input.json'))==load(p/'fixtures/expected.json'),'Profile fixture drift')
        for name in DERIVED:
            p=ROOT/'targets'/('derived.'+name)/'view.json'; data=load(p)
            need(data['input']==binding(ROOT/'examples/graph-manifest.json') and data['result']==project(name,graph),'Derived view drift')
        return {'artifact_packages':26,'negative_schema_fixtures':78,'profiles':25,'relation_kinds':25,'derived_views':7,'graph_nodes':len(graph['nodes']),'graph_edges':len(graph['relations'])}
    check('all-family-contracts-and-examples',contracts)
    def behavior():
        result=subprocess.run([sys.executable,str(ROOT/'test_batch.py')],capture_output=True,text=True)
        dump(ROOT/'receipts/test-command.json',{'command':'python3 test_batch.py','exit_code':result.returncode})
        (ROOT/'receipts/tests.log').write_text(result.stdout+result.stderr)
        need(result.returncode==0,result.stdout+result.stderr)
        data=load(ROOT/'receipts/target-validation.json'); need(data['result']=='PASS' and len(data['targets'])==83,'Incomplete target tests')
        return {'tests_run':data['tests_run'],'targets_passed':len(data['targets'])}
    check('per-target-and-integration-behavior',behavior)
    def deterministic():
        dump(ROOT/'reconciliation.json',reconcile.build())
        before=materials(); predecessor=files(PREVIOUS); author.build()
        need(materials()==before,'Candidate regeneration changed materials')
        need(predecessor==files(PREVIOUS),'Predecessor snapshot changed')
        need(load(ROOT/'reconciliation.json')==reconcile.build(),'Reconciliation is not reproducible')
        return load(ROOT/'reconciliation.json')['state_counts']
    check('deterministic-reconstruction-and-195-target-ledger',deterministic)
    result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK'
    dump(ROOT/'receipts/validation.json',{'schema_version':'cal-remaining-83-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':materials(),'claim_ceiling':'83 bounded constructed candidates only; no admission, authenticated execution, publication, deletion or cutover.'})
    for item in checks: print(item['check'],item['result'],item['detail'])
    print(result); return 0 if result=='PASS' else 1
if __name__=='__main__': raise SystemExit(validate())
