import base64,hashlib,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
work=root/'e2e-final';work.mkdir()
bin=Path(sys.executable).parent;cli=bin/'define-standalone'
rows=[]
def run(name,args,expected=0,raw=None,api=False):
 command=[str(bin/'define-api')] if api else [str(cli),*map(str,args)]
 p=subprocess.run(command,input=raw,capture_output=True,cwd=work,timeout=90)
 (work/(name+'.stdout.json')).write_bytes(p.stdout);(work/(name+'.stderr')).write_bytes(p.stderr)
 data=json.loads(p.stdout);assert p.returncode==expected,(name,p.returncode,data,p.stderr)
 rows.append({'step':name,'exit_code':p.returncode,'outcome':data.get('outcome','prepared'),'expected_exit':expected})
 return data
run('doctor',['doctor']);run('capabilities',['capabilities'])
run('example',['example','--output',work/'input'])
run('capture',['capture-local','--request',work/'input/request.json','--source-root',work/'input','--permit-retention','--output',work/'capture'])
prepared=run('prepare',['prepare','--request',work/'input/request.json','--capture',work/'capture','--output',work/'package'])
run('inspect',['inspect',work/'package'])
run('reconstruct',['reconstruct',work/'package','--output',work/'restored'])
original={str(p.relative_to(work/'package')):p.read_bytes() for p in (work/'package').rglob('*') if p.is_file()}
restored={str(p.relative_to(work/'restored')):p.read_bytes() for p in (work/'restored').rglob('*') if p.is_file()}
assert original==restored
run('observe-no-current',['observe-use',work/'package','--requested-use','inspect-preparation','--consumer','release-reader','--output',work/'observation-no-current'])
run('observe-matching',['observe-use',work/'package','--requested-use','inspect-preparation','--consumer','release-reader','--current-source',work/'capture/inputs/define-source-catalog.json','--output',work/'observation-matching'])
run('observe-changed-use',['observe-use',work/'package','--requested-use','governing-application','--consumer','release-reader','--output',work/'observation-changed'],expected=3)
from define_core import call
from define_core.exact import encode,decode,write_package
from define_core.capture import bindings_in
request_raw=(work/'input/request.json').read_bytes();capture_raw=(work/'capture/capture.json').read_bytes()
inputs={b['path']:(work/'capture/inputs'/b['path']).read_bytes() for b in bindings_in(decode(capture_raw))}
document={'api_version':'define.api/v1','id':'e2e-parity','operation':'prepare','params':{'request_utf8':request_raw.decode(),'capture_utf8':capture_raw.decode(),
    'inputs':{k:base64.b64encode(v).decode() for k,v in inputs.items()}}}
api=run('api-prepare',[],raw=encode(document),api=True)
assert api==call(document)
assert api['data']['root_sha256']==prepared['data']['root_sha256']
pack=json.loads(original['pack.json']);assert pack['assessments'][0]['reported_result']=='FAIL'
assert pack['readiness']['governing-application']['outcome']=='blocked'
assert len(pack['working_meanings'])==1 and len(pack['applications'])==1
# Materialization inputs are public test fixtures extracted from the final source archive.
sys.path.insert(0,str(root/'final-source/cyberalchemy_define-0.3.0rc2/tests'))
from support import materialization,b64,raw_members
r,i=materialization()
c=call({'api_version':'define.api/v1','id':'e2e-m-capture','operation':'capture','params':{'request_utf8':encode(r).decode(),'inputs':b64(i),'permit_retention':True}})
assert c['data'],c
p=call({'api_version':'define.api/v1','id':'e2e-m-prepare','operation':'prepare','params':{'request_utf8':encode(r).decode(),'capture_utf8':c['data']['capture_utf8'],'inputs':c['data']['inputs']}})
assert p['data'],p
write_package(work/'materialization-package',raw_members(p['data']['package_members']))
m=run('materialize',['materialize',work/'materialization-package','--output',work/'definitions'])
assert m['data']['report']['actual_owner_outcome'] is None
assert (work/'definitions/definitions/000/DEFINITION.md').exists()
summary={'schema_version':'define.installed-e2e/v1','version':'0.3.0rc2','installed_python':sys.executable,'workspace':str(work),'outcome':'passed',
  'steps':rows,'reconstructed_files':len(original),'all_reconstructed_bytes_equal':True,'json_python_cli_package_root_equal':True,
  'package_root_sha256':prepared['data']['root_sha256'],'pack_sha256':prepared['data']['pack_sha256'],
  'working_meanings':1,'applications':1,'reported_assessments':1,'reported_result':'FAIL','domain_assessment_execution_count':0,
  'materialized_definitions':1,'actual_owner_outcome':None,'authority_effect':'none'}
(work/'summary.json').write_bytes(encode(summary));print(json.dumps(summary,indent=2))
