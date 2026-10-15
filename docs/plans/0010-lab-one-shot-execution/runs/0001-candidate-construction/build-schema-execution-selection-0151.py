"""Separate schema execution inputs from retained full validation history."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v6';NEW=BASE/'api-integration-v7'
PIN='7ab054776a5fa8fd310f60e126a29c98686d159f989fb3a721cb6dcd1f1f119f'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert not NEW.exists()
    spec=importlib.util.spec_from_file_location('_cal_schema_execution_parent_0151',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify(PIN)
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    for name in ('source-manifest.json','contract-profile.json'):(NEW/name).unlink()
    p=NEW/'protocol.py';text=p.read_text()
    old="""for row in [*self.inputs['files'],*self.profile['files'],
                    self.profile['original_operation_catalog_binding'],self.profile['original_schema_inputs_binding']]:"""
    new="""selection_binding=self.profile['schema_execution_dependency_binding']
        selection_raw=source.original(selection_binding)
        selection=source.parse(selection_raw)
        source.require(set(selection)=={'schema_version','files','selection_reasons','parent_source_binding','parent_profile_binding','authority_effect','actual_owner_outcome','claim_ceiling'},'closed schema execution selection required')
        source.require(selection['schema_version']=='lab-schema-execution-dependencies/v1-candidate' and selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'schema execution selection grants no authority')
        declared={row['path']:row for row in self.profile['files']}
        names=[row['path'] for row in selection['files']]
        source.require(names==sorted(set(names)) and set(selection['selection_reasons'])==set(names),'unique explained execution closure required')
        source.require(all(declared.get(row['path'])==row for row in selection['files']),'execution input outside frozen profile')
        mandatory={row['path'] for row in self.inputs['files']}
        mandatory.update(str((HERE/name).relative_to(ROOT)) for name in ('protocol.py','auth.py','service.py','source_bridge.py','guard.py','authentication.schema.json','schema-inputs.json'))
        mandatory.update(str(file.relative_to(ROOT)) for file in (HERE/'schemas').glob('*.schema.json'))
        source.require(mandatory<=set(names),'mandatory schema execution input omitted')
        for row in [*selection['files'],selection_binding,
                    self.profile['original_operation_catalog_binding'],self.profile['original_schema_inputs_binding']]:"""
    assert text.count(old)==1;p.write_text(text.replace(old,new))
    p=NEW/'test_classification_api.py';text=p.read_text()
    old="self.assertEqual(len(reply['message']['targets']), 5)"
    new="""self.assertEqual(len(reply['message']['targets']), 9)
        targets=reply['message']['targets']
        relations=[target for target in targets if target['artifact']['carrier_ref']=='cal.artifact-type.typed-relation/v3']
        self.assertEqual(len(relations),4)
        self.assertEqual(len({target['artifact']['version_ref'] for target in targets}),9)"""
    method=next(n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name=='test_09_independent_axis_is_preserved')
    lines=text.splitlines(keepends=True);section=''.join(lines[method.lineno-1:method.end_lineno])
    assert section.count(old)==1
    lines[method.lineno-1:method.end_lineno]=[section.replace(old,new)]
    p.write_text(''.join(lines))
    for p in NEW.glob('*.py'):ast.parse(p.read_text())
    rows={};reasons={}
    def select(row,reason):
        assert bind(ROOT/row['path'])==row
        assert row['path'] not in rows or rows[row['path']]==row
        rows[row['path']]=row;reasons.setdefault(row['path'],[]).append(reason)
    for row in load(NEW/'schema-inputs.json')['files']:select(row,'Original complete offline schema and operation input selection, unchanged.')
    for p in sorted(NEW.rglob('*')):
        if p.is_file() and p.suffix in ('.py','.json','.whl'):
            select(bind(p),'Operator-local code, schemas, declared controls and dependencies. Conservative complete local executable/data selection.')
    resource_binding=load(OLD/'contract-profile.json')['protocol_resource_selection_binding']
    select(resource_binding,'Exact versioned protocol resource selection consumed by Schemas constructor.')
    resources=load(ROOT/resource_binding['path'])
    for row in resources['resources']:
        for key in ('source_binding','selected_binding'):select(row[key],'Actual source and versioned URI schema consumed by resource configure().')
    for key in ('additional_domain_binding','catalog_declaration_binding','source_binding','package_binding'):
        select(resources[key],'Exact protocol resource configure() witness: '+key)
    for p in sorted((BASE/'source8-protocol-v2').glob('*.py')):select(bind(p),'Original versioned resource implementation used during schema construction.')
    selection_path=NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json'
    emit(selection_path,{'schema_version':'lab-schema-execution-dependencies/v1-candidate','files':[rows[k] for k in sorted(rows)],
        'selection_reasons':reasons,'parent_source_binding':bind(OLD/'source-manifest.json'),'parent_profile_binding':bind(OLD/'contract-profile.json'),
        'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Schema construction/runtime integrity inputs only. Original selected producer/source/permission guards are unchanged; full historical source closure remains a qualification entry/exit obligation. No qualification inferred.'})
    profile=load(OLD/'contract-profile.json');fullrows={r['path']:r for r in profile['files']}
    for row in [*rows.values(),bind(selection_path)]:fullrows[row['path']]=row
    profile.update(files=[fullrows[k] for k in sorted(fullrows)],schema_execution_dependency_binding=bind(selection_path))
    emit(NEW/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for p in sorted(NEW.rglob('*')):
        if p.is_file():full[bind(p)['path']]=bind(p)
    full[bind(Path(__file__).resolve())['path']]=bind(Path(__file__).resolve())
    emit(NEW/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'schema_execution_dependency_binding':bind(selection_path),'full_validation_history_retained':True,
        'explicit_fixture_revision':'One stale classification target count5 corrected to9 with four typed-relation and unique-version closure assertions; actual fixture already contains five artifacts/four relations.',
        'runtime_qualification_transferred':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(NEW/'source-manifest.json'),'profile_binding':bind(NEW/'contract-profile.json'),
        'schema_execution_files':len(rows),'schema_execution_bytes':sum((ROOT/k).stat().st_size for k in rows)}),flush=True)
if __name__=='__main__':main()
