"""Selected interpreter and frozen SDK main, no actual API constructors."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[8];RUN=Path(__file__).parent;HERE=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003';INSTALL=HERE.parents[1]/'runtime-dependencies-v2-completion-0001/installations/0004'
sys.path[:0]=[str(INSTALL/'deps'),str(HERE)]
import composite as C
from control import sha,parse,compact,public
manifest_raw=public({'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':'15cd8e4e863d110c0da025091220f6efdc7fee8509b001c5bbee816307cfdabd'});manifest=parse(manifest_raw)
for row in manifest['files']:public({'path':row['path'],'sha256':row['sha256']})
selection={'selection':{'path':C.DEPENDENCY_SELECTION,'sha256':C.DEPENDENCY_SHA},'installation':str(INSTALL)};assert C.dependency_guard(selection)==1010
cmd=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S',str(RUN/'observe_main.py')]
cases=[]
for mode in ['pristine-inert','leaf-replace','parent-replace','leaf-symlink-before','parent-symlink-before','leaf-symlink']:
    root=Path(tempfile.mkdtemp(prefix='cal-T06-main-config-controls-'));os.chmod(root,0o700);path=root/'operator-config.json';raw=compact({'owned_inert_fixture':True,'candidate_API_configuration':False});fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'wb') as s:s.write(raw)
    observation=RUN/(mode+'-observation.json');result=subprocess.run(cmd+[str(path),sha(raw),mode,str(observation)],input=b'',capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
    assert result.returncode==2 and result.stderr==b'' and parse(result.stdout)['code']=='startup-or-channel-refused' and b'challenge' not in result.stdout and not list(root.rglob('*.lock'))
    value=json.loads(observation.read_bytes());assert value['selected_config_bytes_restored'] and not value['production_callbacks_replaced'] and value['main_origin']==value['main_code_filename']==str(HERE/'composite.py')
    if mode=='pristine-inert':assert value['parse_calls']==1 and value['preflight_calls']==1 and not value['mutation_performed']
    else:
        assert value['parse_calls']==value['preflight_calls']==0 and value['mutation_performed']
        assert value['read_checkpoint_count']==(0 if mode.endswith('-before') else 1)
    cases.append({'case':mode,'result':'PASS','returncode':2,'config_parsed':bool(value['parse_calls']),'preflight_called':bool(value['preflight_calls']),'owned_root':str(root),'observation_sha256':sha(observation.read_bytes())})
for row in manifest['files']:public({'path':row['path'],'sha256':row['sha256']})
assert public({'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':'15cd8e4e863d110c0da025091220f6efdc7fee8509b001c5bbee816307cfdabd'})==manifest_raw and C.dependency_guard(selection)==1010
value={'schema_version':'lab-T06-existing-main-config-capture-proof/v1-candidate','result':'PASS','cases':cases,'frozen_SDK_manifest_sha256':sha(manifest_raw),'SDK_code_changed':False,'config_capture_already_present_in_revision3':True,'complete_dependencies_entry_exit':1010,'instrumentation':'sys.monitoring observes actual frozen SDK main/helper entry and mutates only own inert configuration; no callback or clock substitution','actual_API_or_branch_constructed':False,'actual_full34_qualification':False,'authority_effect':'none','task_complete':False}
out=RUN/'evidence.json';fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
with os.fdopen(fd,'wb') as s:s.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n')
print(json.dumps({'result':'PASS','cases':len(cases),'report':str(out)}),flush=True)
