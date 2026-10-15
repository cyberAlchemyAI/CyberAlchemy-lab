"""Actual original public carrier fixtures; native/semantic use remains unqualified."""
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
name='_T31_public_output_carrier_controls';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
O=__import__(name+'.output_contracts',fromlist=['*']);catalog_raw=(HERE/'carrier-catalog.json').read_bytes();catalog=json.loads(catalog_raw);docs={row[key]:(ROOT/row[key]).read_bytes() for row in catalog['rows'] for key in ['schema_path','artifact_path']};C=O.OriginalCarriers(catalog_raw,'b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8',docs)
cases=[]
for row in catalog['rows']:
 ref=row['artifact_type_ref'];schema=ROOT/row['schema_path'];folder=schema.parent/'fixtures/valid';paths=sorted(folder.glob('*.json'))
 if ref=='cal.artifact-type.repository-migration-manifest/v1':
  cases.append({'carrier_ref':ref,'result':'BLOCKED-formal-identity-and-external-scope-renderer-required','schema_shape_known':True});continue
 selected=[]
 for p in paths:
  try:
   raw=p.read_bytes();body=O.parse(raw);identity=body.get('node_id');scope=body.get('scope_ref');header={'scope_ref':scope,'identity_ref':identity,'version_ref':identity+'@'+body.get('version','candidate.1'),'carrier_ref':ref,'byte_sha256':O.sha(raw)};C.output(header,raw,scope_ref=scope)
  except Exception:continue
  selected.append({'path':p.relative_to(ROOT).as_posix(),'sha256':O.sha(raw)});break
 cases.append({'carrier_ref':ref,'result':'PASS-original-public-shape-only' if selected else 'NO-original-public-fixture-selected','selected_original_fixture':selected})
report={'schema_version':'lab-T31-public-original-output-carrier-controls/v1-candidate','authority_effect':'none','actual_owner_outcome':None,'cases':cases,'native_semantic_currentness_or_target_transition_or_authority_qualified':False,'Original_Work_Tool_WorkflowRun_journal_or_Session_constructor':False,'all_original_catalog_documents_entry_exit_verified':True}
for row in catalog['rows']:
 for key,h in [('schema_path','schema_sha256'),('artifact_path','artifact_sha256')]:assert O.sha((ROOT/row[key]).read_bytes())==row[h]
p=HERE/'public-carrier-controls-result.json'
with p.open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'positive_public_fixtures':sum(x['result']=='PASS-original-public-shape-only' for x in cases),'missing':sum(x['result']=='NO-original-public-fixture-selected' for x in cases),'explicit_blocked_formal_carriers':1,'report_sha256':O.sha(p.read_bytes())}))
