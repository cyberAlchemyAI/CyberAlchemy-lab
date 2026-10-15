"""Future pure selector authoring from pinned actual v5 family outputs.

Current optimized002 API preimages and old descriptor are independently pinned
in the preparation baseline. No current API file is edited. Root must review
the generated overlay, merge all margin/observer/API changes and freeze again.
"""
import argparse,ast,hashlib,json,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
RECIPE=HERE
RECIPE4=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0004'
OLD_FAMILY='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0002/instances/optimized-0002'
OLD_PUBLIC='completion-current-participation:optimized-0002'
NEW_PUBLIC='completion-current-participation:optimized-0005'
FAMILY_FIELDS={'source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def inputs():
    path=RECIPE/'recipe_inputs_v5.py';raw=path.read_bytes()
    if sha(raw)!='392789f6da9d870f059d7a7cfec2b4127c88ff3970b283cf27c54e3d1c53ae04':raise ValueError('selected v5 preparation helper differs')
    module=types.ModuleType('_cal_T02_v5_runtime_selected_inputs');module.__file__=str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__);return module
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:f.write(value if isinstance(value,str) else json.dumps(value,sort_keys=True,indent=2)+'\n')
def transform(text,filename,old_descriptor,new_descriptor,new_family):
    if filename=='current_machine_context_scope.py':return text
    mapping={OLD_FAMILY:new_family,OLD_PUBLIC:NEW_PUBLIC,
             'completion-optimized-source8-0002-optimized-0002':'completion-optimized-source8-0005-optimized-0005',
             '_cal_api17_current_source8_optimized_0002':'_cal_api17_current_source8_optimized_0005'}
    if filename=='source_bridge.py':fields=('context_source_binding',)
    elif filename=='current_context_sessions.py':fields=('context_source_binding','mapper_package_binding')
    elif filename=='machine_auth_scope.py':fields=('context_source_binding',)
    elif filename=='authentication.schema.json':fields=()
    else:raise ValueError('unselected runtime selector leaf')
    for field in fields:mapping[old_descriptor[field]['sha256']]=new_descriptor[field]['sha256']
    changed=False
    for old,new in mapping.items():
        if old in text:text=text.replace(old,new);changed=True
    if not changed:raise ValueError('selected optimized002 selector absent')
    if filename.endswith('.py'):ast.parse(text)
    else:
        value=json.loads(text)
        if text.count(NEW_PUBLIC)!=4:raise ValueError('four independently selected current source enum sites required')
    if OLD_FAMILY in text or OLD_PUBLIC in text:raise ValueError('old family executable selector retained')
    return text
def stage(instance,family_selection,activation_selection):
    I=inputs();baseline=I.verify_baseline();I.check_activation(activation_selection,instance)
    value=I.parse(I.exact(family_selection))
    I.need(set(value)=={'schema_version','status','instance','authority_effect','construction_binding','phase_reports','family_bindings'},'closed actual family selector required')
    I.need(value['schema_version']=='lab-T02-v5-actual-family-inputs/v1-candidate' and value['status']=='Root-reviewed-actual-native-family'
           and value['instance']==instance=='optimized-0005' and value['authority_effect']=='none','actual complete new family required')
    family=RECIPE/'instances'/instance;new_family=family.relative_to(ROOT).as_posix()
    I.need(value['construction_binding']['path']==new_family+'/construction-selection.json','true actual v5 construction origin required')
    construction=I.parse(I.exact(value['construction_binding']))
    I.need(construction['instance']==instance and construction['prefix']=='completion-optimized-source8-0005-optimized-0005','actual new family identity required')
    I.need(construction['preserved_recipe4_binding']==baseline['parent_recipe4_binding'] and construction['optimized_recipe_declaration_mapping']==baseline['declaration_mapping'],'complete original recipe4 conservation differs')
    I.need(not {row['path'] for row in construction['optimized_recipe_bindings']+construction['optimized_input_bindings']}&I.FORBIDDEN_LIVE_API_INPUTS,'actual construction includes live mutable API preparation origin')
    I.need(set(value['family_bindings'])==FAMILY_FIELDS,'complete new independently pinned family required')
    targets={'source_binding':'source/source-manifest.json','source_package_binding':'source/packages/0001/manifest.json',
             'reader_binding':'reader/source-manifest.json','mapper_binding':'mapped/source-manifest.json',
             'mapper_package_binding':'mapped/packages/0001/manifest.json','context_source_binding':'context/source-manifest.json',
             'context_package_binding':'context/packages/0001/manifest.json','implementation_binding':'context/implementation-binding.json',
             'period_binding':'source/packages/0001/period.json'}
    for key,row in value['family_bindings'].items():
        I.need(row['path']==new_family+'/'+targets[key],'new family role origin differs');I.exact(row)
    snapshots=[item['snapshot_binding'] for item in baseline['mutable_snapshot_pairs']]
    for key in ['source_binding','reader_binding','mapper_binding','context_source_binding']:
        manifest=I.parse(I.exact(value['family_bindings'][key]));rows=manifest['files']
        names={Path(row['path']).relative_to(ROOT).as_posix() if Path(row['path']).is_absolute() and Path(row['path']).is_relative_to(ROOT) else row['path'] for row in rows}
        I.need(not names&(I.FORBIDDEN_LIVE_API_INPUTS|{'product/lab/release-candidates/v1/interface/api-integration-v17/contract-profile.json','product/lab/release-candidates/v1/interface/api-integration-v17/SCHEMA-EXECUTION-DEPENDENCIES.json','product/lab/release-candidates/v1/interface/api-integration-v17/INPUT-ACCOUNTING.json'}) and all(row in rows for row in snapshots),'actual full role closure needs all snapshots and zero live mutable API preparation origins')
    I.need(type(value['phase_reports']) is list and len(value['phase_reports'])==5,'all five actual phase reports required')
    phases=[]
    for row in value['phase_reports']:
        I.need(row['path'].startswith(RECIPE.relative_to(ROOT).as_posix()+'/reports/'),'new owned phase report origin required')
        report=I.parse(I.exact(row));I.need(report['instance']==instance and report['result']=='PASS' and report['error'] is None,'actual native phase failed')
        phases.append(report['phase'])
    I.need(phases==['source','cold','reader','mapped','context'],'real native phase order differs')
    old=I.parse(I.exact(baseline['fixed_runtime_descriptor_binding']))
    descriptor={'schema_version':'lab-current-session-runtime-selection/v1-candidate','instance':instance,'public_source_name':NEW_PUBLIC,
                **value['family_bindings'],'reader_root':new_family+'/reader','reader_class':'CurrentFixtureReader',
                'context_entrypoint_ref':new_family+'/context/build.py#generate','fixture_only':True,'actual_human_review':False,
                'actual_owner_outcome':None,'authority_effect':'none','shared_API_qualified':False,
                'previous_runtime_selection_binding':baseline['fixed_runtime_descriptor_binding'],
                'actual_family_selection_binding':family_selection,'optimized_capture_selection_binding':construction['optimized_capture_selection_binding']}
    captured=[]
    for pair in baseline['runtime_template_snapshot_pairs']:
        row=pair['original_binding'];snapshot=pair['snapshot_binding'];raw=I.exact(snapshot);name=Path(row['path']).name
        captured.append((name,transform(raw.decode(),name,old,descriptor,new_family),row,snapshot))
    # Only after all independently pinned actual inputs and transformations pass
    # do any output leaves get published. No descriptor/hash self cycle exists.
    out=family/'runtime';postimages=[]
    for name,text,original,snapshot in captured:
        path=out/'postimages'/name;write(path,text);postimages.append({'original':original,'snapshot':snapshot,'postimage':binding(path)})
    descriptor['runtime_postimages']=[r['postimage'] for r in postimages if Path(r['postimage']['path']).name in ('current_context_sessions.py','current_machine_context_scope.py')]
    descriptor['original_templates']=[r['original'] for r in postimages]
    descriptor['original_template_preimages']=[{'original_binding':r['original'],'snapshot_binding':r['snapshot']} for r in postimages]
    write(out/'runtime-selection.json',descriptor)
    ledger={'schema_version':'lab-T02-v5-runtime-selector-overlay/v1-candidate','authority_effect':'none','descriptor_binding':binding(out/'runtime-selection.json'),
            'rows':postimages,'shared_API_modified':False,'full_API_profile_freeze_and_margin_observer_merge_pending':True,'task_complete':False}
    write(out/'selector-postimages.json',ledger);I.verify_baseline()
    print(json.dumps({'result':'STAGED-future-runtime-selectors-UNQUALIFIED','ledger_binding':binding(out/'selector-postimages.json')}))
def main():
    p=argparse.ArgumentParser();p.add_argument('--instance',required=True)
    for name in ('family-selection','activation-selection'):
        p.add_argument('--'+name,required=True);p.add_argument('--'+name+'-sha256',required=True)
    a=p.parse_args();stage(a.instance,{'path':a.family_selection,'sha256':a.family_selection_sha256},
                          {'path':a.activation_selection,'sha256':a.activation_selection_sha256})
if __name__=='__main__':main()
