"""Receipt from actual frozen preparation, exhaustive guards and cold process."""
import re,unittest
from package import *

def run(manifest_pin):
 require(binding(HERE/'manifest.json')['sha256']==manifest_pin,'independent final audit manifest pin differs')
 files={};checks=[]
 def capture(b):
  raw=bound(b,allow_external=True);require(b['path'] not in files or files[b['path']]==b['sha256'],'source epoch collision');files[b['path']]=b['sha256'];return raw
 def check(name,v):require(v,name);checks.append({'test':name,'result':'PASS'})
 frozen=source_guard();capture(binding(HERE/'manifest.json'))
 for b in frozen['files']:capture(b)
 output=HERE/'packages/0001';v=original(binding(output/'preparation.json'));check('exact closed candidate preparation reconstructs',validate(v,output)['result']=='PASS')
 import test_package
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_package.ReviewGuards)
 declared={t.id().split('.')[-1] for t in suite};log=(HERE/'proof/guards.stderr').read_text();observed=re.findall(r'^(test_\S+) \([^\n]+\) \.\.\. ok$',log,re.M)
 check('every declared guard actually passed',len(observed)==len(declared) and set(observed)==declared and re.search(r'Ran '+str(len(declared))+r' tests in [0-9.]+s\n\nOK\s*$',log) is not None)
 terminals=original(binding(HERE/'proof/terminal-observations.json'));check('all actual process completions recorded',terminals['exit_codes']=={'build':0,'guards':0,'cold':0})
 build=parse((HERE/'proof/build.stdout').read_bytes());cold=parse((HERE/'proof/cold.stdout').read_bytes())
 check('actual original-byte build matches exact independent output',build['result']=='PASS' and build['members']==323 and build['preparation_binding']==binding(output/'preparation.json'))
 check('new-process independent source and package validation',cold['result']=='PASS' and cold['fresh_process'] and cold['source_manifest_binding']==binding(HERE/'manifest.json') and cold['preparation_binding']==binding(output/'preparation.json') and cold['members']==323)
 check('cold process and build stderr empty',not (HERE/'proof/cold.stderr').read_bytes() and not (HERE/'proof/build.stderr').read_bytes())
 check('owned mutable guard fixtures removed',set(p.name for p in (HERE/'packages').iterdir())=={'0001'})
 check('no actual owner decision or effects',v['actual_owner_outcome'] is None and not any(v['actual_effects'].values()) and v['canonical_effects_applied']==0 and not v['complete_final_package'])
 check('18 independent axes explicit',all(set(m['requested_axes'])==set(AXES) for m in v['members']))
 check('all member dependencies resolved independently',all(set(m['dependencies'])<={r['member_ref'] for r in v['members']} for m in v['members']))
 for m in v['members']:
  for b in m['targets']+m['evidence']:capture(b)
 for folder in ['packages','proof']:
  for p in (HERE/folder).rglob('*'):
   if p.is_file():capture(binding(p))
 receipt={'schema_version':'lab-O06-review-preparation-evidence/v1-candidate','task':'O06','result':'PASS','task_complete':True,
  'completion_mode':'candidate-implementation-verified','authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,
  'local_transactions_applied':0,'ontology_events_appended':0,'runtime_activation':False,'source_retirements':0,'human_pilot':False,
  'tests':len(declared),'checks':[{'test':name,'result':'PASS'} for name in observed],'validation_checks':checks,
  'source_manifest_binding':binding(HERE/'manifest.json'),'preparation_binding':binding(output/'preparation.json'),'review_binding':binding(HERE/'REVIEW.md'),
  'counts':v['counts'],'source_bindings':original(CONTEXT)['source_bindings'],'source_drift':[],
  'files':[{'path':p,'sha256':h} for p,h in sorted(files.items())],'complete_final_package':False,'remaining_obligations':[],
  'original_operational_owner_obligation_route':'R08/A01','admitted_operation_route':'R08/A01/A03',
  'final_assembly_obligations':v['final_assembly_obligations'],
  'claim_ceiling':'Complete phase-overlay candidate O06 review preparation only; original actual owner and admitted operation criteria remain routed to R08/A01/A03. No original source semantics, domain conformance, new global relation, current action authority, private body export, source retirement, service activation or human pilot inferred.'}
 (ONTOLOGY/'receipts/O06').mkdir(exist_ok=False);target=ONTOLOGY/'receipts/O06/0001.json';put(target,receipt)
 print(encoded({'result':'PASS','tests':len(declared),'validation_checks':len(checks),'files':len(files),'counts':v['counts'],'receipt_binding':binding(target)}).decode(),end='')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest-sha256',required=True);a=p.parse_args();run(a.manifest_sha256)
