"""Pure closed actual packet review; never call preparer main or output writer."""
import ast,hashlib,importlib.util,json,os,stat,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/'
packet_rel=RUN+'T00/final-learning-input-packet-0005.json'
checks=0;bindings=[]
def ck(ok,message):
 global checks
 checks+=1
 if not ok:raise AssertionError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(path,pin):
 p=ROOT/path;ck(not p.is_symlink() and p.is_file(),'regular selected input required')
 raw=p.read_bytes();ck(sha(raw)==pin,'independent input pin '+path);bindings.append({'path':path,'sha256':pin});return raw
def parse(path,pin):return json.loads(exact(path,pin))
fd0=len(os.listdir('/proc/self/fd'))
p=parse(packet_rel,'f96c41139affe4500dcb04e055263c6284b5ce08e388ba12d32477b76858ac84')
prep_rel=RUN+'T35/full-learning-input-preparation-0004/prepare.py'
raw=exact(prep_rel,'721b66ba16123a7ca4eee126fab56c37019ebc099c1b563492320c51e60c8805')
peer=parse(RUN+'T35/full-learning-input-preparation-0004/independent-review-root-0001.json','edaaed73022778ed5d7f193bf1993dc667fa0f76f658139f04240c78b85defdf')
ck(peer['result'].startswith('PASS') and peer['findings']==[],'preparer peer status')
# Import the existing true file unchanged. Its only top-level imports are stdlib;
# build selects jsonschema only after checking exact installed0004 interpreter.
spec=importlib.util.spec_from_file_location('_T35_independent_actual_packet_0005',ROOT/prep_rel)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ck(len(p)==len(m.FIELDS)==36 and set(p)==m.FIELDS,'closed36 actual fields')
ck(p['family_generation']==5 and p['family_instance']=='optimized-0005','exact family5')
schema=json.loads((ROOT/RUN/'T35/full-learning-input-preparation-0004/expected-input-packet.schema.json').read_bytes())
sys.path.append(str(ROOT/p['dependency_installation']/'deps'))
from jsonschema import Draft202012Validator
Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(p);ck(True,'packet schema valid')
# Only build is called; neither main nor write_exclusive nor the driver is invoked.
config_raw,selection_raw=m.build(p)
config=m.parse(config_raw);selection=m.parse(selection_raw)
ck(len(config)==13 and len(selection)==18,'closed output field counts')
ck(config['mode']==selection['margin']['mode']=='diagnostic-measurement' and config['policy_binding'] is None and config['load_binding'] is None,'diagnostic only no policy/load')
ck(selection['margin']['control']['configuration_binding']['sha256']==sha(config_raw),'in-memory output byte binding')
ck(config['api_source_binding']==p['final_source_binding'] and config['profile_binding']==p['final_profile_binding'],'final exact capture correspondence')
source=parse(p['final_source_binding']['path'],'ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1')
profile=parse(p['final_profile_binding']['path'],'9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b')
source_rows={(r['path'],r['sha256']) for r in source['files']};profile_rows={(r['path'],r['sha256']) for r in profile['files']}
ck(len(source['files'])==len(source_rows)==28597 and len(profile['files'])==len(profile_rows)==28596,'actual28597/28596 source profile')
ck(profile_rows==source_rows-{(p['final_profile_binding']['path'],p['final_profile_binding']['sha256'])},'profile/source exact correspondence')
runtime=parse(p['runtime_selection_binding']['path'],'589d36bce32cfef590e0a01c9fd9ea8873cc16eede8f20e9adb1686f1423deff')
ck(p['source_pin']==runtime['source_binding']['sha256']=='5b6bd1fc683fc56b3aaafe5c7a738a45244da290132215288965a2d8a7ec39ad','actual family source pin')
ck(p['source_package_pin']==runtime['source_package_binding']['sha256']=='8a78ca32bb59ac634d5351b1b166bce6022cdc51ae4c548144585af00843d863','actual family package pin')
ck(selection['period_binding']==runtime['period_binding'] and selection['producer_root']==p['producer_root'],'original actual clock/producer metadata selected')
ck('context_lease' not in p and not any('lease' in k for k in selection),'no old Context lease transfer field')
software=parse(p['software_inventory_binding']['path'],'5bdd8adba0ffd73ea2ab5121e6a52ce232c86bf398b1ed25c233b7f3bd3e9081')
inventory_input=parse(p['software_input_selection_binding']['path'],'3d2ba1070c4e2e2093ffa3ca0677c43050ea45d229799392330c4a71cbc78620')
ck(len(software['files'])==16,'current software16')
ck(p['postselector_current_context_binding']==inventory_input['module_bindings']['current_context_sessions'] and p['postselector_current_context_binding']['sha256']=='c1440f882eee2ea619f73f26b47771dcf57fece4937ef136437574bf83cbecbe','exact postselector Context code')
parse(p['selector_merge_review_binding']['path'],'b95f2e2f7660a247f45bef04499f28be35116c0f73837c218e7f1e870e73b146')
parse(p['dependency_selection_binding']['path'],'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835')
instrument=parse(p['instrumentation_binding']['path'],'ce4212ab379637bb8ec1d458e492d72950f23d0fa69c50c5e98f3c577fb09a8b')
ck(p['expected_monitor_tool']==5 and instrument['profile_hook'] is None and instrument['trace_hook'] is None and instrument['monitoring_tools']['5']=='cal-full-learning-measurement-v2','reviewed instrument tool5/profile trace null')
# Account for exact public union independently; never print configuration fields.
public=[p[k] for k in m.ORIGINALS]+[p[k] for k in ['driver_binding','selection_schema_binding','composition_binding','software_inventory_binding','instrumentation_binding','postselector_current_context_binding','runtime_selection_binding','software_input_selection_binding','selector_merge_review_binding','dependency_selection_binding','preparer_binding','family_closure_preview_binding','family_closure_acceptance_binding']]+p['api_bootstrap_bindings']+list(p['helper_bindings'].values())+list(p['lifecycle_bindings'].values())+software['files']
unique={(r['path'],r['sha256']) for r in public}
ck(len(unique)==34 and unique<=source_rows,'all34 exact public selected inputs in final Source')
for path,pin in sorted(unique):exact(path,pin)
# Custody is independently supplied metadata, with directory stat only.
custody=parse(RUN+'T00/learning-output-custody-0005.json','a6494d6eaf4d1f3591e3fd68aa93ede4935f237a44a78caef8d9519e0a7ba018')
ck(custody['protected_control']==p['protected_control'] and custody['selection_output_root_identity']==p['selection_output_root_identity'] and custody['selection_output_leaf']==p['selection_output_leaf'],'Root custody correspondence')
ck(not custody['config_or_selection_created'] and not custody['runtime_started'] and not custody['private_existing_state_read_or_modified'],'custody preparation scope')
for directory,expected in [(p['protected_control']['root'],p['protected_control']['identity']),(custody['selection_output_root'],p['selection_output_root_identity'])]:
 q=Path(directory);st=q.lstat();ck(not stat.S_ISLNK(st.st_mode) and stat.S_ISDIR(st.st_mode) and [st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]==expected,'current directory custody metadata')
ck(str((m.HERE/p['selection_output_leaf']).relative_to(ROOT)) not in {r[0] for r in source_rows},'postcapture output not recaptured/digest cycle')
# Pure AST review of original default: profile-load has store_true and no default=True.
driver_raw=exact(p['driver_binding']['path'],p['driver_binding']['sha256']);tree=ast.parse(driver_raw)
profile_args=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and any(isinstance(a,ast.Constant) and a.value=='--profile-load' for a in n.args)]
ck(len(profile_args)==1 and any(k.arg=='action' and isinstance(k.value,ast.Constant) and k.value.value=='store_true' for k in profile_args[0].keywords) and not any(k.arg=='default' and isinstance(k.value,ast.Constant) and k.value.value is True for k in profile_args[0].keywords),'original driver profiling false by default')
ck(len(os.listdir('/proc/self/fd'))==fd0,'FD balance')
print(json.dumps({'schema_version':'lab-T35-final-packet-independent-controls/v1','result':'PASS','authority_effect':'none','checks':checks,'FD_delta':0,'packet_fields':36,'unique_public_selected_inputs':34,'final_source_rows':28597,'final_profile_rows':28596,'software_rows':16,'in_memory_config_fields':13,'in_memory_selection_fields':18,'in_memory_config_sha256':sha(config_raw),'in_memory_selection_sha256':sha(selection_raw),'instrument_tool':5,'default_profiling':False,'mode':'diagnostic-measurement','policy_binding_null':True,'load_binding_null':True,'only_preparer_build_called':True,'config_or_selection_written':False,'driver_or_Lab_runtime_started':False,'private_body_access':False,'full_capture_peer_result_claimed':False,'bindings':bindings},sort_keys=True,indent=2))
