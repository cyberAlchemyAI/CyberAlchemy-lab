"""Freeze this controlled fixture producer before signing any owned branch."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'current-participation-v8';READER=HERE.parent/'source8-lesson-fixture-reader-v2-action-0148'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists();rows={}
 def add(row):assert bind(ROOT/row['path'])==row;assert rows.get(row['path'],row)==row;rows[row['path']]=row
 for name in ('source-manifest.json','packages/0001/manifest.json'):
  p=OLD/name;add(bind(p));value=json.loads(p.read_bytes())
  for row in value['files']:add(row)
 for folder in (HERE,READER):
  for p in sorted(folder.iterdir()):
   if p.is_file():
    if p.suffix=='.py':ast.parse(p.read_text())
    add(bind(p))
 for kind in ('operational-lesson','evidence-set'):add(bind(ROOT/'authority/artifact-types'/kind/'v1/fixtures/valid/record.json'))
 value={'schema_version':'lab-controlled-source8-lesson-fixture-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'original_Source8_source_binding':bind(OLD/'source-manifest.json'),'original_Source8_package_binding':bind(OLD/'packages/0001/manifest.json'),'original_Source8_period_binding':bind(OLD/'packages/0001/period.json'),'fixed_fixture_episode_binding':bind(HERE/'episode-contract.json'),'implementation_code_binding':bind(READER/'reader.py'),'implementation_entrypoint_ref':READER.relative_to(ROOT).as_posix()+'/reader.py#FixtureReader.open_signed','fixture_only':True,'original_Source8_keys_or_bytes_or_periods_changed':False,'actual_AC09_or_human_learning_claimed':False,'new_private_key_exported':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'goal_complete':False}
 with (HERE/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'FROZEN-fixture-only','files':len(rows),'source_binding':bind(HERE/'source-manifest.json')}),flush=True)
if __name__=='__main__':main()
