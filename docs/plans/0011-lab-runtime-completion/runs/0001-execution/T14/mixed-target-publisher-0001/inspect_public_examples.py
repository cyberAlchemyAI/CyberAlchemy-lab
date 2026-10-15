import importlib.util,json,sys,uuid
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab');H=Path(__file__).resolve().parent;I=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004';sys.path.append(str(I/'deps'))
n='_T14_example_inspection_'+uuid.uuid4().hex;s=importlib.util.spec_from_file_location(n,H/'typed_targets.py');T=importlib.util.module_from_spec(s);s.loader.exec_module(T)
for row in json.loads((H/'public-schema-example-selection.json').read_bytes())['rows']:
 raw=(R/row['public_original_fixture']['path']).read_bytes();doc=(R/row['schema']['path']).read_bytes();schema=T.OriginalSchemas([row['schema']],{row['schema']['path']:doc});sp={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']};sp.update(schema_path=row['schema']['path'],raw_sha256=T.sha(raw))
 try:T.adapt(raw,sp,schema);result='PASS-STRUCTURAL'
 except T.Refusal:result='REFUSED-ORIGINAL-SCHEMA'
 print(json.dumps({'family':row['family'],'result':result,'schema_path':row['schema']['path'],'public_fixture_path':row['public_original_fixture']['path']}))
