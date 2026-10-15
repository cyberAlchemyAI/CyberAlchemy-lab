"""Independent bounded byte/AST accounting only; no API or controls imports."""
import ast,hashlib,json,os,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T31/output-integration-preparation-0003'
POST=P/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
OWN=Path(__file__).parent
HH='1264995e54c1925228c19b6b76122d5f6fa90718c2150bab1ab207228dcff09a'
MF='c5330d4e2ec0698866eb0ceb3dc0ae40ddcc7f104bd5c85ac2f5f6e79b51dea8'
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
    need(len(manifest['files'])==52,'exact52 package rows required')
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
    # This derived inventory is sealed by its selected predecessor manifest.
    parent_manifest=json.loads(cache[str(RUN/'T31/output-transitions-0001/source-manifest.json')])
    inventory_binding=next(row for row in parent_manifest['files']if ROOT/row['path']==inventory_path)
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
    need(len(adopted)==26,'26 source-specific postimages required')
    for row in adopted:
        take(row['postimage'])
        if row['preimage']is not None:
            pre=row['preimage'];take(pre)
            need(capture(ROOT/row['target'],pre['sha256'])==cache[str(ROOT/pre['path'])],'current original target preimage differs')
        else:need(not(ROOT/row['target']).exists(),'new target already exists')
    for file in POST.glob('*.py'):ast.parse(cache[str(file)],filename=str(file))
    # Parent39 literal declarations and all original293 are separately retained;
    # this is a bounded package/public-source review, not a full historical guard.
    preserved=json.loads(cache[str(P/'parent-preimage-conservation.json')])
    old_manifest=json.loads(take(preserved['parent_manifest']))
    need(preserved['declarations']==old_manifest['files']and len(old_manifest['files'])==39,'v2 parent39 declaration changed')
    for row in preserved['declarations']:take(row)
    inv=json.loads(cache[str(P/'service-code-inventory.json')])
    need(len(inv['original_names'])==71 and len(inv['T31_additional_names'])==24 and len(inv['separate_required_T15_names'])==8,'Service exact71+24+8 components differ')
    need(len(set(inv['final_names']))==len(inv['final_names'])==103 and set(inv['final_names'])==set(inv['original_names'])|set(inv['T31_additional_names'])|set(inv['separate_required_T15_names']),'Service full103 union differs')
    init=next(n for c in ast.parse(cache[str(POST/'service.py')]).body if isinstance(c,ast.ClassDef)and c.name=='Service'for n in c.body if isinstance(n,ast.FunctionDef)and n.name=='__init__')
    assignment=next(n for n in ast.walk(init)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Attribute)and t.attr=='code_files'for t in n.targets))
    actual_names=ast.literal_eval(assignment.value.generators[0].iter)
    need(list(actual_names)==inv['final_names'],'actual Service fingerprints differ from selected103 union')
    boot=ast.parse(cache[str(P/'bootstrap.py')]);groups=next(ast.literal_eval(n.value)for f in boot.body if isinstance(f,ast.FunctionDef)and f.name=='assemble'for n in f.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='groups'for t in n.targets))
    refs=['transition:'+k for _,_,keys in groups for k in keys]
    need(len(refs)==len(set(refs))==28 and set(refs)==set(original),'actual bootstrap all28 closure differs')
    response_group=next(g for g in groups if 'challenge-handling:responded'in g[2]);need(response_group[0]=='response'and response_group[1]is None,'responded still aliases open submit')
    old_schema=json.loads(take(next(row for row in old_manifest['files']if row['path'].endswith('/workflow-stage-controls.schema.json'))))
    new_schema=json.loads(cache[str(POST/'workflow-stage-controls.schema.json')])
    oldalts=old_schema['oneOf'];newalts=new_schema['oneOf']
    old_unique={json.dumps(v,sort_keys=True):v for v in oldalts}
    need(len(oldalts)==11 and len(old_unique)==8 and len(newalts)==9,'actual11-to8-plus1 schema alternative shape differs')
    old_by_version={v['properties']['schema_version']['const']:v for v in old_unique.values()}
    new_by_version={v['properties']['schema_version']['const']:v for v in newalts}
    need(len(new_by_version)==9,'duplicate new schema version alternatives')
    unchanged=set(old_by_version)-{'lab-private-formal-Session-capture/v1-candidate','lab-private-authorized-API-output/v1-candidate'}
    need(all(old_by_version[v]==new_by_version[v]for v in unchanged),'undeclared original stage control schema change')
    for v in set(old_by_version)-unchanged:
        reduced=json.loads(json.dumps(new_by_version[v]))
        for k in ['producer_policy_binding','producer_source_binding']:
            reduced['properties'].pop(k);reduced['required'].remove(k)
        need(reduced==old_by_version[v],'producer control change exceeds exact independent policy/Source bindings')
    need('lab-private-authenticated-challenge-response-stage/v1-candidate'in new_by_version,'new response contract missing')
    # Register and preserve the known authority/lineage gaps without invoking
    # a Service, actual Source guard or any author controls.
    response=ast.parse(cache[str(POST/'workflow_response_outputs.py')])
    need('stable_subject_ref'not in cache[str(POST/'workflow_response_outputs.py')].decode(),'signer finding precondition changed')
    scope=ast.parse(cache[str(POST/'workflow_output_scope.py')])
    sc=next(f for c in scope.body if isinstance(c,ast.ClassDef)for f in c.body if isinstance(f,ast.FunctionDef)and f.name=='validate')
    need([a.arg for a in sc.args.args]==['self','ref','artifact','body_scope','proof'],'scope review signature changed')
    for path,raw in cache.items():need(capture(Path(path),hashlib.sha256(raw).hexdigest())==raw,'selected review input changed')
    need(len(os.listdir('/proc/self/fd'))==before,'review FD imbalance')
    out={'result':'PASS-bounded-static-accounting-only','authority_effect':'none','handoff_sha256':HH,'manifest_sha256':MF,'package_rows':52,'original_declarations_retained_as_metadata':293,'original293_body_fullguard_claimed':False,'carrier_schema_and_descriptor_rows':33,'original_definition_count':10,'original_transition_count':28,'postimage_count':26,'unique_public_inputs_captured_entry_exit':len(cache),'Service_other_method_AST_preserved':True,'FD_delta':0,'parent39_exact_rows_conserved_and_freshly_checked':True,'Service_fingerprint_union_count':103,'bootstrap_groups':len(groups),'old_schema_alternatives_actual':11,'old_schema_unique_actual':8,'new_schema_alternatives_actual':9,'author_delta_old_schema_count_claim':json.loads(cache[str(P/'delta.json')])['old_schema_alternative_count'],'API_native_Runtime_Source_guard_or_controls_executed':False,'all28_runtime_or_genuineWork_qualified':False}
    with(OWN/'static-result-0001.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
