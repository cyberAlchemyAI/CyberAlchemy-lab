"""Pin the exact fixture reader, original provenance and native package."""
import ast,hashlib,json,importlib.metadata,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];SOURCE=HERE.parent/'source8-lesson-fixture-source-v3-action-0148'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 assert not (HERE/'source-manifest.json').exists();rows={}
 def add(row):assert bind(ROOT/row['path'])==row;assert rows.get(row['path'],row)==row;rows[row['path']]=row
 for name in ('source-manifest.json','packages/0001/manifest.json'):
  p=SOURCE/name;add(bind(p))
  for row in json.loads(p.read_bytes())['files']:add(row)
 for p in sorted(HERE.glob('*.py')):ast.parse(p.read_text());add(bind(p))
 value={'schema_version':'lab-selected-source-adapter-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'producer_source_binding':bind(SOURCE/'source-manifest.json'),'producer_package_binding':bind(SOURCE/'packages/0001/manifest.json'),'implementation_entrypoint_ref':(HERE/'reader.py').relative_to(ROOT).as_posix()+'#FixtureReader.open_signed','environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'original_Source8_permission_transferred':False,'public_API_qualified':False}
 with (HERE/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'FROZEN-fixture-reader','files':len(rows),'source_binding':bind(HERE/'source-manifest.json')}),flush=True)
if __name__=='__main__':main()
