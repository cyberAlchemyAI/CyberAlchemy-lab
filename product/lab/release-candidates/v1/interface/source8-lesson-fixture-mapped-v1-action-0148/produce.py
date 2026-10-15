"""Freeze explicit fixture mapping inputs and run actual native mapper."""
import ast,hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];SOURCE=HERE.parent/'source8-lesson-fixture-source-v4-action-0148';READER=HERE.parent/'source8-lesson-fixture-reader-v4-action-0148'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists();rows={}
 def add(row):assert binding(ROOT/row['path'])==row;assert rows.get(row['path'],row)==row;rows[row['path']]=row
 for parent in [SOURCE/'source-manifest.json',SOURCE/'packages/0001/manifest.json',READER/'source-manifest.json']:
  add(binding(parent))
  for row in json.loads(parent.read_bytes())['files']:add(row)
 for p in HERE.iterdir():
  if p.is_file() and p.suffix in ('.py','.json'):
   if p.suffix=='.py':ast.parse(p.read_text())
   add(binding(p))
 exe=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader');assert exe.stat().st_mode&0o777==0o755 and hashlib.sha256(exe.read_bytes()).hexdigest()=='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
 value={'schema_version':'lab-controlled-fixture-mapping-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'original_source_binding':binding(SOURCE/'source-manifest.json'),'original_package_binding':binding(SOURCE/'packages/0001/manifest.json'),'adapter_source_binding':binding(READER/'source-manifest.json'),'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'native_executable_binding':{'path':str(exe),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'required_mode':493},'complete_current_Lesson_inventory':2,'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'public_API_qualified':False}
 with (HERE/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 name='_cal_source8_lesson_fixture_native_mapper_0208';s=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);b=__import__(name+'.build',fromlist=['*']);b.build(binding(HERE/'source-manifest.json')['sha256'])
if __name__=='__main__':main()
