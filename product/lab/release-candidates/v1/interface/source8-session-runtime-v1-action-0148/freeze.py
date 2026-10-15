"""Freeze additive composition bytes; this is not common API qualification."""
import ast, fcntl, hashlib, importlib.metadata, importlib.util, json, os, platform
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent; ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
OWN=[HERE,BASE/'lesson-host-composition-v45-action-0148',BASE/'lesson-application-v3-action-0148',BASE/'lesson-assessment-v2-action-0148']
PARENTS={
 'api-integration-v12/source-manifest.json':'5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae',
 'source8-mapped-context-v2-action-0148/source-manifest.json':'6bab0989ec925f0e424567e76af85bff9f7b8b5e557c99c5e6e706b31766ae77',
 'source8-mapped-context-v2-action-0148/packages/0001/manifest.json':'eed1eac8ca31d26872b43df0164fed67df3c557cd36392384059f97d16bc401b',
 'source8-context-delivery-v3-action-0148/source-manifest.json':'0017f4455df9d829368cb6448f0063f470283ef175f5f9cdb1836043488760e3',
 'source8-context-delivery-v3-action-0148/packages/0001/manifest.json':'9dac39ab529865f42f50e01cabf92298cac0e323eeee5e612c688abfa2933cfa',
 'source8-lesson-fixture-source-v4-action-0148/source-manifest.json':'93b802f83cc8f45d41d8c7b473e644c91fd0aa04475c6956b014fc0f42723fe5',
 'source8-lesson-fixture-source-v4-action-0148/packages/0001/manifest.json':'389c1757936f350f32c7a2505bb054fba5c7470cddb37bd5ac34fabf447e5b0c',
 'source8-lesson-fixture-reader-v4-action-0148/source-manifest.json':'abf4405cbdeef5aabd4b62562ee7b6d82fc310d9ad46a4fe2b71f6a3ba3109b9',
 'source8-lesson-fixture-mapped-v1-action-0148/source-manifest.json':'d1d78f6d4d618c5387d08230199146c62f4a367d2aa01a5e743597fbc7ad60a3',
 'source8-lesson-fixture-mapped-v1-action-0148/packages/0001/manifest.json':'d71e2064fd4c183416bf6f562bd41555ce9047bbbcc5be4bec06821edacb75e1',
 'source8-lesson-fixture-context-v1-action-0148/source-manifest.json':'0afe7a76c15a26df9f10b0691fb240f6955f772e778e58820cc0d6dc0d0565d3',
 'source8-lesson-fixture-context-v1-action-0148/packages/0001/manifest.json':'60f6ca7202fe4bbb7c17e8981fbd834a83ff8f6aecab617ddc8ad1d6fbef3fc1'}
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 try:
  fcntl.flock(fd,fcntl.LOCK_SH)
  assert all(not (d/'source-manifest.json').exists() for d in OWN),'immutable contribution already frozen'
  rows={};parents=[]
  def add(r):
   assert r['path'] not in rows or rows[r['path']]==r,'conflicting immutable dependency'
   rows[r['path']]=r
  for relative,pin in PARENTS.items():
   p=BASE/relative;b=binding(p);assert b['sha256']==pin,'independent parent pin differs: '+relative
   parents.append(b);value=json.loads(p.read_bytes())
   for r in value['files']:add(r)
   add(b)
  own=[]
  for d in OWN:
   for p in sorted(d.iterdir()):
    assert p.is_file(),'unexpected owned subdirectory'
    if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p))
    elif p.suffix=='.json':json.loads(p.read_bytes())
    else:raise AssertionError('undeclared contribution file '+str(p))
    b=binding(p);own.append(b);add(b)
  spec=importlib.util.spec_from_file_location('_source8_freeze_guard',BASE/'api-integration-v12/guard.py')
  guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
  history=[rows[k] for k in sorted(rows)]
  entry=guard._verify_files(ROOT,history)
  environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
  for d in OWN:
   value={'schema_version':'lab-Source8-composition-source/v1-candidate','files':history,'environment':environment,
    'parent_bindings':parents,'owned_composition_files':own,'construction_guard':'fresh complete deduplicated union entry and exit under original shared lock',
    'qualification':False,'actual_common_API_calls':0,'authority_effect':'none','actual_owner_outcome':None,
    'execution_dependency_closure':'Host-selected actual common API closure must contain these exact code/schema bytes and native Source/Context inputs; historical rows remain validation history, not a permission grant.',
    'public_safe_owned_files':[r for r in own if r['path'].startswith(d.relative_to(ROOT).as_posix()+'/')],
    'private_source_closure':'Full history includes signed archives, private policy schema implementations and absolute environment dependencies; no live/private credential bytes are authored by this candidate. Do not publish this closure as a public resource.'}
   with (d/'source-manifest.json').open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
  exit_check=guard._verify_files(ROOT,history)
  print(json.dumps({'construction_guard':'PASS','common_API_qualification':False,'entry':entry,'exit':exit_check,
   'files':len(history),'unique_files':len({r['path'] for r in history}),
   'bytes':sum((Path(r['path']) if Path(r['path']).is_absolute() else ROOT/r['path']).stat().st_size for r in history),
   'absolute_external_files':sum(Path(r['path']).is_absolute() for r in history),
   'source_bindings':[binding(d/'source-manifest.json') for d in OWN]},indent=2),flush=True)
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
if __name__=='__main__':main()
