#!/usr/bin/env python3
"""Readonly current-profile probes; output belongs only to this review."""
from pathlib import Path
from copy import deepcopy
import importlib.util,json,hashlib,sys,argparse
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'craft/formalization').is_dir())
BASE=ROOT/'craft/formalization/candidates/relational-theorem-checker/v1'
def imported(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
f=imported('review_profile',BASE/'inference/profile/frontend.py')
ref=lambda n:{'kind':'reference','id':n,'version':'v1'}
a,b,c=ref('A'),ref('ContractA'),ref('ContractB');scope={'kind':'scope','value':'Scope1'};kind={'kind':'text','value':'contract'}
pattern=lambda name,terms:{'predicate':name,'terms':terms}
request={'schema':'relational.inference-input/v1','snapshot_epoch':0,'domain':[a,b,c,scope,kind],'predicates':deepcopy(f.CORE)+[{'id':'ConformsTo','version':'v2-probe','sorts':['reference','reference','scope'],'role':'ordinary'},{'id':'TargetKind','version':'v2-probe','sorts':['reference','text'],'role':'ordinary'}],'rules':[{'id':'ordinary-semantic-producer','version':'v1','head':pattern('ConformsTo',[{'variable':'x'},{'constant':c},{'constant':scope}]),'body':[pattern('Conforms',[{'variable':'x'}])]}],'facts':[pattern('Conforms',[a])],'roots':[],'root_assessments':[]}
normal=f.normalize(request)
seed=deepcopy(request);seed['rules']=[];seed['facts']+=[pattern('ConformsTo',[a,c,scope]),pattern('TargetKind',[c,kind])]
seed_normal=f.normalize(seed)
# Execute current captured profile's actual guard; never compile/replay/apply.
bc=imported('review_bundle',BASE/'workflow/evidence/bundle_contract.py')
proposal=json.loads((BASE/'evolution/proposals/rule-change-proposal.json').read_text())
assert proposal['after']['rules']
proposal['after']['rules'][0]['head']['predicate']='ConformsTo'
try:
 bc.execution_profile(proposal)
except bc.UnsupportedScope as error: rejection=str(error)
else:raise AssertionError('captured workflow unexpectedly supported new head')
report={'schema':'relational.implementation-review-probes/v1','result':'pass','generic_normalizer_accepts_ordinary_semantic_head':len(normal['rules'])==1,'generic_normalizer_accepts_ordinary_semantic_seeds':len(seed_normal['facts'])==3,'captured_workflow_rejects_new_head':True,'rejection':rejection,'method':'Executed current Python normalizer and captured-profile guard only; no Lean derivation, closure, application or new theorem. Ordinary supplied truth is intentional in generic v1; producer sealing is a prospective v2 requirement.','request':request,'seed_request':seed,'guard_proposal_identity':bc.g.c.identity(proposal),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(__file__),BASE/'inference/profile/frontend.py',BASE/'workflow/evidence/bundle_contract.py',BASE/'evolution/proposals/rule-change-proposal.json']],'authority_effect':'none'}
if '--write' in sys.argv:(HERE/'probe-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['request','seed_request','sources']},indent=2))
