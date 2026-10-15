"""Independent bounded byte/AST accounting only; no API or controls imports."""
import ast,hashlib,json,os,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T31/output-integration-preparation-0002'
POST=P/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
OWN=Path(__file__).parent
HH='0d203fce0fbc87e8a61c8ff215ac2c377842f2c6c2c924d499752a87a2ecf454'
MF='bd3df70ad187016da65bd6c3a73ac77c4e815a744102153ae72b0f90ae645241'
def need(v,why):
    if not v:raise ValueError(why)
def main():
    before=len(os.listdir('/proc/self/fd'))
    cp=RUN/'T32/native-lifecycle-recovery-adoption-0003/capture.py';raw=cp.read_bytes()
    need(hashlib.sha256(raw).hexdigest()=='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa','independent capture differs')
    m=types.ModuleType('_T31_pure_review_capture');m.__file__=str(cp);exec(compile(raw,str(cp),'exec'),m.__dict__)
    capture=m.capture_path
    cache={}
    def take(row):
        p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
        raw=capture(p,row['sha256'])
        if 'size_bytes'in row:need(len(raw)==row['size_bytes'],'selected size differs')
        if str(p)in cache:need(cache[str(p)]==raw,'contradictory selected bindings')
        cache[str(p)]=raw;return raw
    take({'path':str(P/'HANDOFF.json'),'sha256':HH})
    manifest=json.loads(take({'path':str(P/'source-manifest.json'),'sha256':MF}))
    need(len(manifest['files'])==39,'exact39 package rows required')
    for row in manifest['files']:take(row)
    for leaf in ('external-inputs.json','source-observations.json'):
        for row in json.loads(cache[str(P/leaf)])['files']:take(row)
    conservation=json.loads(cache[str(P/'original-input-conservation.json')])
    parent=json.loads(take(conservation['parent_input_selection']))
    need(conservation['declarations']==parent['files']and len(parent['files'])==293,'original293 declaration bytes not retained')
    proposal=json.loads(cache[str(P/'ROOT-selection-proposal.json')])
    catalog=json.loads(take(proposal['carrier_catalog']))
    need(len(catalog['rows'])==33,'original33 output carriers required')
    for row in catalog['rows']:
        descriptor=json.loads(take({'path':row['artifact_path'],'sha256':row['artifact_sha256']}))
        schema=json.loads(take({'path':row['schema_path'],'sha256':row['schema_sha256']}))
        need(descriptor['artifact_type_ref']==row['artifact_type_ref']and descriptor['schema_digest']==row['schema_sha256'],'original descriptor/schema identity differs')
    inventory_path=RUN/'T31/output-transitions-0001/workflow-output-inventory.json'
    # This inventory is an original293 declaration, independently sealed there.
    inventory_binding=next(row for row in parent['files']if ROOT/row['path']==inventory_path)
    inventory=json.loads(take(inventory_binding))
    original={row['transition_ref']:(w,row)for w in inventory['workflows']for row in w['transitions']}
    need(len(inventory['workflows'])==10 and len(original)==28 and set(proposal['routes'])==set(original),'full10/28 route closure differs')
    for ref,row in proposal['routes'].items():
        w,t=original[ref]
        need(row['original_required_output_carriers']==t['original_required_output_carriers']and row['original_authority_precondition_satisfaction_relation_obligations']==t['original_authority_precondition_satisfaction_relation_obligations'],'original route obligation changed')
        take(row['original_definition_binding'])
    def methods(raw,name):
        return {n.name:ast.dump(n,include_attributes=False)for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)and c.name==name for n in c.body if isinstance(n,ast.FunctionDef)}
    a=methods(cache[str(P/'preimages/product/lab/release-candidates/v1/interface/api-integration-v17/service.py')],'Service')
    b=methods(cache[str(POST/'service.py')],'Service')
    need(set(a)==set(b)and {k for k in a if a[k]!=b[k]}=={'__init__','select_workflow_transition'},'undeclared original Service method change')
    adopted=json.loads(cache[str(P/'ADOPTION.json')])['rows']
    need(len(adopted)==20,'20 source-specific postimages required')
    for row in adopted:
        take(row['postimage'])
        if row['preimage']is not None:
            pre=row['preimage'];take(pre)
            need(capture(ROOT/row['target'],pre['sha256'])==cache[str(ROOT/pre['path'])],'current original target preimage differs')
        else:need(not(ROOT/row['target']).exists(),'new target already exists')
    for file in POST.glob('*.py'):ast.parse(cache[str(file)],filename=str(file))
    for path,raw in cache.items():need(capture(Path(path),hashlib.sha256(raw).hexdigest())==raw,'selected review input changed')
    need(len(os.listdir('/proc/self/fd'))==before,'review FD imbalance')
    out={'result':'PASS-bounded-static-accounting-only','authority_effect':'none','handoff_sha256':HH,'manifest_sha256':MF,'package_rows':39,'original_declarations_retained_as_metadata':293,'original293_body_fullguard_claimed':False,'carrier_schema_and_descriptor_rows':33,'original_definition_count':10,'original_transition_count':28,'postimage_count':20,'unique_public_inputs_captured_entry_exit':len(cache),'Service_other_method_AST_preserved':True,'FD_delta':0,'API_native_Runtime_Source_guard_or_controls_executed':False,'all28_runtime_or_genuineWork_qualified':False}
    with(OWN/'static-result-0001.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
