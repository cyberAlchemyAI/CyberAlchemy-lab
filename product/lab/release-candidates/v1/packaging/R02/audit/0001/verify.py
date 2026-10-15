"""Independent cold receipt, public payload/privacy and original criteria audit."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1];ROOT=BASE.parents[5]
sys.path.insert(0,str(BASE/'successors/0001'))
from common import *
PIN='b82d1df6572ce73415ff31b263a7381dbdc5b1765c4eed97e481cd675c24531a'
def verify(receipt_pin):
 source=BASE/'successors/0003/source-manifest.json';need(sha(read(source))==PIN,'independent source manifest pin')
 manifest=load(source)
 for b in manifest['files']:need(sha(read(ROOT/b['path']))==b['sha256'],'frozen selection changed: '+b['path'])
 receipt=BASE/'successors/0003/receipts/0001.json';need(sha(read(receipt))==receipt_pin,'independent terminal receipt pin');v=load(receipt)
 need(v['result']=='PASS' and v['task_complete'] is True and v['actual_owner_outcome'] is None and v['actual_admitted_operation'] is False and v['authority_effect']=='none','candidate task closure required')
 for b in v['files']:need(sha(read(ROOT/b['path']))==b['sha256'],'receipt source changed: '+b['path'])
 need(v['package_binding']==manifest['package_binding'],'source/receipt package selection differs')
 package=ROOT/v['package_binding']['path'];selection=load(package);need(sha(read(package))==v['package_binding']['sha256'],'package pin')
 need(selection['versions']==VERSIONS and selection['environment']==manifest['environment']==v['environment'],'dependency/environment selection differs')
 raw=read(package.parent/'payload.snapshot');need(sha(raw)==selection['snapshot_sha256'],'payload pin');sourcefiles=payload(raw)
 for n,b in sourcefiles.items():
  privacy(b,source=True)
  need(n.startswith(('implementation/lab-runtime/','product/lab/release-candidates/v1/packaging/R02/')),'body data entered executable payload')
 need(len(sourcefiles)==87,'selected code/control closure count')
 for row in selection['wheels']:need(sha(read(package.parent/'wheels'/row['filename']))==row['sha256'],'wheel changed')
 need(len(selection['wheels'])==8,'wheel closure')
 observation=load(BASE/'successors/0003/proof/0001/terminal-observations.json')
 need([x['returncode'] for x in observation['observations']]==[75,76,0,0],'actual terminal process outcomes differ')
 need(observation['packaging_guards']==26 and observation['transition_regression_checks']==20 and all(v['checks'].values()),'negative/integration acceptance failure')
 scenario=observation['scenario'];need(all(scenario['checks'].values()) and scenario['session_restored'] is False and scenario['private_key_published'] is False,'lifecycle/privacy acceptance failure')
 need(scenario['exports']['parent']['files']==len(scenario['parent_committed_files'])-1,'public baseline exclusion lost')
 need(all(x['visibility']=='local-protected-history' for x in scenario['protected_archives'].values()),'protected archive boundary lost')
 need(scenario['cold']['parent_files']==scenario['parent_committed_files'] and scenario['cold']['restored_session'] is False,'original history or ephemeral boundary lost')
 need(observation['owned_fixture_removed'] and scenario['owned_fixture_removed_after_terminal'],'private fixture residue')
 privacy(read(receipt));privacy(read(BASE/'successors/0003/proof/0001/terminal-observations.json'))
 print(json.dumps({'result':'PASS','task':'R02','authority_effect':'none','actual_owner_outcome':None,'source_files':len(sourcefiles),'dependency_wheels':8,'checks':v['counts'],'receipt_sha256':receipt_pin}))
if __name__=='__main__':verify(sys.argv[1])
