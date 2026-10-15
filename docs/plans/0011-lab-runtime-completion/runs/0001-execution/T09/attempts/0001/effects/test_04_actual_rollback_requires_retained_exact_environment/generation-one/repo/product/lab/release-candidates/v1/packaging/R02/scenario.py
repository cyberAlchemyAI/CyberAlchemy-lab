"""Actual installed-code signed branch upgrade, export, cold recovery and rollback."""
from common import *
from installer import OwnedScope,export_legacy,export_successor,restore,verify_install,archive_legacy,archive_successor,restore_legacy,restore_successor
from dataclasses import asdict
import importlib.util, subprocess
from tempfile import TemporaryDirectory
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];PACKAGE=ROOT/'implementation/lab-runtime/candidates/repeatable-operation';INSTALL=ROOT.parent
sys.path.insert(0,str(PACKAGE))
from lab_runtime.common import digest
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.transition import LocalPolicy,BranchPins,committed_files,prepare_transition,authorize_transition,apply_transition,replay_successor

def launcher(args):return [sys.executable,'-I','-S',str(HERE/'installed.py'),'scenario.py',*args]
def cold(x):
 parent=VerifiedLegacyReadStore(x['parent'],Path(x['source_repository']),Path(x['old_install'])/'repo',ReplayPins(**x['replay_pins']));data=parent.verify_full()
 succ=replay_successor(x['successor'],BranchPins(**x['branch_pins']),LocalPolicy(**x['policy']))
 return {'parent_files':committed_files(parent,data),'parent_sequence':data['head']['sequence'],'successor_records_digest':digest(succ['records']),'successor_subjects':len(succ['subjects']),'restored_session':False}

def run(work,package,pin,old_install,source_repository):
 source=Path(source_repository)
 root=Path(work);need(root.is_dir() and root.resolve()==root and not root.is_relative_to(INSTALL),'owned state outside installation required');scope=OwnedScope(str(root));checks={}
 def check(n,v):need(v,n);checks[n]=True
 legacy=ROOT/'implementation/lab-runtime/v1';spec=importlib.util.spec_from_file_location('R02_legacy_fixture',legacy/'lab_runtime/__init__.py',submodule_search_locations=[str(legacy/'lab_runtime')]);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 from R02_legacy_fixture.store import Store,keygen
 from R02_legacy_fixture.cli import example
 private=root/'candidate-only.pem';public=root/'candidate-only.pub';keygen(private,public)
 store=Store(root/'parent',source);store.initialize(load(legacy/'profile.json'),'R02-parent-d74','role:test-only',public.read_text().strip())
 proposal=example(store,'R02-carry');proposal['targets'].append(example(store,'R02-exclude')['targets'][0]);store.apply(proposal,store.authorize(proposal,private))
 manifest=PACKAGE/'design/legacy-runtime-bindings.json';pins=ReplayPins('v1',manifest.relative_to(ROOT).as_posix(),sha(read(manifest)),sha(read(store.path/'config.json')),load(store.path/'baseline.json')['snapshot_digest'],load(store.path/'HEAD.json')['transaction_digest'])
 parent=VerifiedLegacyReadStore(store.path,source,ROOT,pins);data=parent.verify_full();before=committed_files(parent,data)
 row=next(r for r in load(PACKAGE/'profiles/selections.json')['selections'] if r['name']=='d75');args={k:v for k,v in row.items() if k not in ('name','source_bytes','source_materials')};selection=select(source,**args)
 policy=LocalPolicy('role:test-only',public.read_text().strip(),'R02-candidate-successor',str(root/'successor'),'scope:isolated-R02','2099-01-01T00:00:00Z')
 choices=[{'version_ref':r['version_ref'],'new_carrier_ref':r['carrier_ref'],'disposition':'carry' if i==0 else 'exclude','reason':'R02 exact isolated package upgrade selection'} for i,r in enumerate(proposal['targets'])]
 mapping=PACKAGE/'design/contract-impact.json';prepared=prepare_transition(parent,selection,choices,mapping,sha(read(mapping)),policy);approval=authorize_transition(prepared,policy,private)
 outcome=apply_transition(parent,selection,prepared,approval,mapping,policy);bp=BranchPins(**outcome['pins']);replayed=replay_successor(root/'successor',bp,policy)
 check('actual_signed_parent_transaction',data['head']['sequence']==1);check('candidate_carry_exclude',len(replayed['records'])==1 and choices[1]['version_ref'] not in replayed['records'])
 check('no_signature_or_admission_rebase',all(s['decision_ref'] is None and s['effective_state']=='candidate-reconstructed' and not s['provenance']['signatures_copied'] for v,s in replayed['subjects'].items() if v in replayed['records']))
 check('parent_original_bytes_unchanged',committed_files(parent,parent.verify_full())==before)
 # The parent verifier ignores these unrelated private/ephemeral files; export
 # selects exactly committed history rather than copying the branch directory.
 (store.path/'unselected-private.pem').write_bytes(read(private));emit(store.path/'session-notes.json',{'short_memory':'R02-MEMORY-DO-NOT-EXPORT'})
 e1=export_legacy(parent,root/'parent.snapshot',scope);e2=export_successor(root/'successor',bp,policy,root/'successor.snapshot',scope)
 exported=payload(read(root/'parent.snapshot'));check('exact_scoped_history_export',set(exported)==set(before)-{'baseline.json'} and all(sha(exported[n])==h for n,h in before.items() if n!='baseline.json'))
 check('keys_and_short_memory_excluded',b'R02-MEMORY-DO-NOT-EXPORT' not in read(root/'parent.snapshot') and 'unselected-private.pem' not in exported and 'session-notes.json' not in exported)
 # Kill a real recovery process after durable stage creation, preserve residue,
 # then resume the independently pinned archive in another process.
 a1=archive_legacy(parent,root/'parent.protected',scope);a2=archive_successor(root/'successor',bp,policy,root/'successor.protected',scope)
 recovery_request={'archive':str(root/'parent.protected'),'pin':a1['sha256'],'destination':str(root/'recovered-parent'),'scope':str(root),'source':str(source),'pins':asdict(pins)};emit(root/'recovery-request.json',recovery_request)
 child=subprocess.run(launcher(['--recover',str(root/'recovery-request.json')]),capture_output=True,text=True,timeout=120)
 check('interrupted_recovery_terminal',child.returncode==75)
 stage=root/('.recovered-parent.recover-'+a1['sha256']);check('interrupted_recovery_preserved',stage.is_dir() and not (root/'recovered-parent').exists())
 restore_legacy(root/'parent.protected',a1['sha256'],root/'recovered-parent',scope,source,ROOT,pins);restore_successor(root/'successor.protected',a2['sha256'],root/'recovered-successor',scope,bp,policy)
 check('recovery_exact_and_no_session',committed_files(VerifiedLegacyReadStore(root/'recovered-parent',source,ROOT,pins),data)==before and not (root/'recovered-parent/session-notes.json').exists())
 x={'parent':str(root/'recovered-parent'),'successor':str(root/'recovered-successor'),'old_install':old_install,'source_repository':str(source),'replay_pins':asdict(pins),'branch_pins':asdict(bp),'policy':asdict(policy)};emit(root/'cold-request.json',x)
 child=subprocess.run(launcher(['--cold',str(root/'cold-request.json')]),capture_output=True,text=True,timeout=180)
 check('fresh_process_cold_replay_terminal',child.returncode==0);cold_result=parse(child.stdout)
 check('restored_full_signature_and_cut_parity',cold_result['parent_files']==before and cold_result['successor_records_digest']==digest(replayed['records']) and cold_result['parent_sequence']==1)
 # Rollback is an explicit reader/code selection, preserving both histories.
 installed_before=verify_install(old_install,package,pin);rolled=VerifiedLegacyReadStore(root/'recovered-parent',source,Path(old_install)/'repo',pins).verify_full()
 check('rollback_retained_old_code_history',rolled['head']==data['head'] and committed_files(parent,parent.verify_full())==before and replay_successor(root/'successor',bp,policy)==replayed)
 dep=Path(old_install)/'deps/jsonschema/__init__.py';original=read(dep);dep.unlink()
 try:
  try:verify_install(old_install,package,pin)
  except ValueError:check('missing_rollback_dependency_rejected',True)
  else:raise ValueError('missing rollback dependency accepted')
 finally:dep.write_bytes(original);os.chmod(dep,0o600)
 check('rollback_dependencies_restored',verify_install(old_install,package,pin)==installed_before)
 result={'result':'PASS','checks':checks,'parent_replay_pins':asdict(pins),'successor_branch_pins':asdict(bp),'parent_committed_files':before,'exports':{'parent':e1,'successor':e2},'protected_archives':{'parent':a1,'successor':a2},'cold':cold_result,'authority_effect':'none','actual_owner_outcome':None,'actual_admitted_operation':False,'session_restored':False,'private_key_published':False}
 emit(root/'scenario-result.json',result);print(json.dumps(result))

if __name__=='__main__':
 if sys.argv[1]=='--cold':print(json.dumps(cold(load(sys.argv[2]))))
 elif sys.argv[1]=='--recover':
  x=load(sys.argv[2]);restore_legacy(x['archive'],x['pin'],x['destination'],OwnedScope(x['scope']),Path(x['source']),ROOT,ReplayPins(**x['pins']),crash_at='after-stage')
 else:run(*sys.argv[1:])
