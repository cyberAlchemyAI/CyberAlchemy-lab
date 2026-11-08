import hashlib,json,os,sys,types,unittest
from pathlib import Path
from unittest import mock
HERE=Path(__file__).resolve().parent
CAND=HERE.parent/'mapper-successor-release-0002'
rows=json.loads((HERE/'inputs.json').read_bytes())
def verify():
 for row in rows:
  b=Path(row['path']).read_bytes()
  if len(b)!=row['size'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('SOURCE_DRIFT')
def load(name,path):
 raw=path.read_bytes();module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
 exec(compile(raw,str(path),'exec'),module.__dict__);return module
verify()
R=load('release',CAND/'release.py');T=load('selected_tests',CAND/'test_release.py')
original=Path.read_bytes
opened=[]
def no_private(path):
 if path.name=='branch.snapshot':raise RuntimeError('PRIVATE_BODY_FORBIDDEN')
 opened.append(str(path));return original(path)
with mock.patch.object(Path,'read_bytes',no_private):
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
 if not result.wasSuccessful():raise RuntimeError('BASE_TEST_FAILURE')
 data=T.fixture();positive=R.select_stage(**data);plan=positive['plan']
 outcomes=[]
 for exit_value in (False,0.0,True,1,-1,"0",None):
  data=T.fixture();e=json.loads(data['reader_external_raw']);e['exit_code']=exit_value
  data['reader_external_raw']=R.encoded(e)
  review=json.loads(data['reader_review_raw']);review['external_sha256']=R.sha(data['reader_external_raw'])
  data['reader_review_raw']=R.encoded(review);data['outside_reader_review_sha']=R.sha(data['reader_review_raw'])
  try:
   v=R.select_stage(**data);outcome=v['status']
  except ValueError as error:outcome='REFUSED:'+str(error)
  if outcome!='REFUSED:READER_EXTERNAL_OS_INTEGER_ZERO':raise RuntimeError('R01_NOT_CLOSED')
  outcomes.append({'exit_type':type(exit_value).__name__,'value':exit_value,'outcome':outcome})
 native=R.frozen_selector().NATIVE
 native_sha=R.sha(native.read_bytes())
verify()
print(json.dumps({'normal_or_optimized':sys.flags.optimize,'author_tests':result.testsRun,'passed':result.wasSuccessful(),'rows':len(plan['files']),'distinct_rows':len({r['path'] for r in plan['files']}),'private_mode_rows':sum(r['target_mode']=='0600' for r in plan['files']),'generated_rows':sum(r['source_kind']=='generated-mapper' for r in plan['files']),'plan_sha256':positive['plan_sha256'],'native_sha256':native_sha,'verifier_sha256':plan['verifier_template_sha256'],'counterexamples':outcomes,'private_body_opened':False,'effect':'NOT_RUN','selected_input_bindings':len(rows),'claim':'static/pure metadata selection only'},sort_keys=True))
