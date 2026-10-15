"""Seal additive package without changing the frozen source."""
import hashlib,json,importlib.util,sys,os
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];BASE=HERE.parent/'api-integration-v6'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def write(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def main():
 opened=set();recording=[True]
 def audit(event,args):
  if not recording[0] or event!='open' or not args or not isinstance(args[0],str):return
  p=Path(args[0])
  if p.is_absolute() and p.is_relative_to(ROOT) and p.is_file() and not (len(args)>2 and args[2]&os.O_WRONLY):opened.add(p)
 sys.addaudithook(audit)
 write(HERE/'contract-profile.json',{'schema_version':'lab-action-contract-profile/v1-candidate','implemented_operations':['action.evaluate','action.dispatch','action.reconcile'],'base_source_binding':row(BASE/'source-manifest.json'),'base_contract_profile_binding':{'ref':(BASE/'contract-profile.json').relative_to(ROOT).as_posix(),'sha256':sha((BASE/'contract-profile.json').read_bytes())},'original_operation_catalog_binding':row(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json'),'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Independent additive isolated public Action handler package; base reader profile is unchanged.'})
 files=[p for p in HERE.iterdir() if p.is_file() and p.name not in ('source-manifest.json',)]
 files+=list((ROOT/'implementation/lab-workflows/candidates/v1/authority').glob('*.py'))+[ROOT/'implementation/lab-workflows/candidates/v1/tools/counter.py']
 for kind in ('principal','role','role-assignment','agent-assignment','delegation','tool','agent-instance','agent-session','agent-profile','agent-action'):
  files.append(ROOT/f'authority/artifact-types/{kind}/v1/schema.json')
  if kind!='agent-action':files.append(ROOT/f'authority/artifact-types/{kind}/v1/fixtures/valid/record.json')
 name='_cal_action_0148_selector';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 d=__import__(name+'.dependencies',fromlist=['*']);schemas=d.P.Schemas(d.BASE_PROFILE)
 __import__(d.name+'.service',fromlist=['*']);__import__(d.name+'.jcs',fromlist=['*'])
 with d.P.source.replay_source('engineering') as view:
  assert view.data['projection'] is not None
 recording[0]=False
 mandatory={str(p.resolve()):p for p in files if p.name!='EXECUTION-DEPENDENCIES.json'}
 reasons={str(p.resolve()):'Action implementation, qualification, artifact carrier or qualified W02 Tool/authority' for p in mandatory.values()}
 def add(p,reason):
  p=Path(p);mandatory[str(p.resolve())]=p;reasons[str(p.resolve())]=reason
 for r in json.loads((BASE/'schema-inputs.json').read_bytes())['files']:add(ROOT/r['path'],'Original mandatory schema/contract input')
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in ('.py','.json'):add(p,'Frozen public API code and exact original profile/source selection')
 for p in (BASE/'schemas').glob('*.json'):add(p,'Original public v2 envelope')
 add(BASE/'dependencies/rfc8785-0.1.4-py3-none-any.whl','Original pinned RFC8785 implementation')
 selection=json.loads((ROOT/schemas.protocol_resource_selection_binding['path']).read_bytes())
 add(ROOT/schemas.protocol_resource_selection_binding['path'],'Original Source8 protocol resource selector')
 for r in selection['resources']:
  for k in ('source_binding','selected_binding'):add(ROOT/r[k]['path'],'Original exact selected Source8 protocol resource')
 for k in ('additional_domain_binding','catalog_declaration_binding','source_binding','package_binding'):add(ROOT/selection[k]['path'],'Original Source8 protocol closure')
 imports=[]
 for m in list(sys.modules.values()):
  filename=getattr(m,'__file__',None)
  if not isinstance(filename,str):continue
  p=Path(filename)
  if p.is_absolute() and p.is_relative_to(ROOT) and p.suffix=='.py':
   archive=getattr(getattr(m,'__loader__',None),'archive',None)
   if isinstance(archive,str):p=Path(archive)
   add(p,'Observed actual schema/dependency import');imports.append({'module':m.__name__,'file_binding':row(p)})
 for p in opened:add(p,'Observed actual original file read while constructing selected schemas and reader import closure')
 execution=HERE/'EXECUTION-DEPENDENCIES.json'
 write(execution,{'schema_version':'lab-action-selected-execution-dependencies/v1-candidate','parent_source_binding':row(BASE/'source-manifest.json'),'parent_profile_binding':row(BASE/'contract-profile.json'),'qualification_history_guard':'Complete unchanged frozen history checked at qualification entry and exit; public/effect boundaries freshly verify every selected execution file and exact original manifest/profile bytes. Original Schemas.guard still checks its unchanged schema/profile closure per public call.','files':[dict(row(p),selection_reason=reasons[str(p.resolve())]) for p in sorted(mandatory.values())],'actual_import_witness':imports,'actual_file_read_witness':[row(p) for p in sorted(opened)],'runtime_inputs':['Fresh independently pinned signed source and signature','Current private host grant and channel policy','Actual UTC SessionLease and source-to-runtime binding','Current stop/revocation/gate status','Exact owned input materials','Independently checkpointed current W02 ledger'],'authority_effect':'none','actual_owner_outcome':None})
 files=[p for p in files if p.name!='EXECUTION-DEPENDENCIES.json']+[execution]
 write(HERE/'source-manifest.json',{'schema_version':'lab-action-api-source/v1-candidate','base_source_sha256':sha((BASE/'source-manifest.json').read_bytes()),'base_profile_sha256':sha((BASE/'contract-profile.json').read_bytes()),'profile_sha256':sha((HERE/'contract-profile.json').read_bytes()),'execution_selection_sha256':sha(execution.read_bytes()),'files':[row(p) for p in sorted(files)],'authority_effect':'none','actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0})
 print(json.dumps({'source_sha256':sha((HERE/'source-manifest.json').read_bytes()),'profile_sha256':sha((HERE/'contract-profile.json').read_bytes())}))
if __name__=='__main__':main()
