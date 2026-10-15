"""Exact fixture Context construction under the real historical source lock."""
import ast,fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];M=HERE.parent/'source8-lesson-fixture-mapped-v1-action-0148';RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 try:
  fcntl.flock(fd,fcntl.LOCK_SH);assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists();rows={}
  def add(row):
   p=Path(row['path']) if Path(row['path']).is_absolute() else ROOT/row['path'];assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];assert rows.get(row['path'],row)==row;rows[row['path']]=row
  for parent in [M/'source-manifest.json',M/'packages/0001/manifest.json',HERE.parent/'api-integration-v12/source-manifest.json']:
   add(binding(parent))
   for row in json.loads(parent.read_bytes())['files']:add(row)
  for p in HERE.rglob('*'):
   if p.is_file() and p.suffix in ('.py','.json'):
    if p.suffix=='.py':ast.parse(p.read_text())
    add(binding(p))
  source={'schema_version':'lab-controlled-fixture-context-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'external_dependency_bindings':[rows[k] for k in sorted(rows) if Path(k).is_absolute()],'qualified_mapper_source_binding':binding(M/'source-manifest.json'),'qualified_mapper_package_binding':binding(M/'packages/0001/manifest.json'),'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'common_host_qualification':False,'actual_human_outcome':False}
  with (HERE/'source-manifest.json').open('x') as f:json.dump(source,f,indent=2,sort_keys=True);f.write('\n')
  name='_cal_source8_lesson_fixture_context_0208';s=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);b=__import__(name+'.build',fromlist=['*']);b.build(binding(HERE/'source-manifest.json')['sha256'],binding(M/'packages/0001/manifest.json')['sha256'])
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
if __name__=='__main__':main()
