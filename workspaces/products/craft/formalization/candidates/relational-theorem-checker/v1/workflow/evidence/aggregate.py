"""Independent evidence replay and complete readiness aggregation for R03."""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import bundle_contract as b
import semantic_replay as sem
s=b.s;g=b.g;v=b.v
sys.path.insert(0,str(s.BASE/'workflow/contracts'))
import outcomes as o
HERE=Path(__file__).resolve().parent


def diagnostic(code,message,obligation=None,location='bundle',next_action='Correct the named input/evidence and replay the full required scope.'):
 return {'code':code,'message':str(message)[:16000],'location':location,'obligation_id':obligation,'next_action':next_action}


def invalid_outcome(command,error):
 doc={'schema_version':'relational.cli-outcome/v1-candidate','command':command,'profile_id':'invalid-input',
  'baseline_identity':None,'proposal_identity':None,'execution':'not-run','currentness':'unresolved',
  'evidence':{'methods':[],'policy_identity':g.c.identity(b.policy()),'trust_boundary':v.policy()['trust']},
  'results':[],'required_hard_obligation_ids':[],'missing_hard_obligation_ids':[],'unresolved_hard_obligation_ids':[],
  'readiness':'unresolved','compatibility_dimensions':{k:'unknown' for k in o.DIMENSIONS},
  'diagnostics':[diagnostic('input-invalid',error)],'authority_effect':'none'}
 o.validate(doc,[])
 return doc


def aggregate_results(proposal,results,execution='completed',currentness='current',diagnostics=None,command='check-extension'):
 # A caller must supply verifier-produced rows. The public API never aggregates
 # client-owned result/status documents and never reads a client required set.
 b.source_boundary(proposal)
 required=g.generate(proposal);ids=[x['id'] for x in required['obligations']]
 actual={r['obligation_id']:r for r in results}
 s.require(len(actual)==len(results) and set(actual)<=set(ids),'duplicate/injected verifier result')
 missing=[i for i in ids if i not in actual]
 unresolved=[i for i in ids if i not in actual or actual[i]['verdict']!='satisfied']
 def dim(name):
  row=actual.get(required['proposal_identity']+':'+name)
  if row is None:return 'unknown'
  return {'satisfied':'verified-for-named-scope','violated':'violated','unsupported':'unsupported'}.get(row['verdict'],'unknown')
 dimensions={label:dim(name) for label,name in [('selected-data-compatibility','selected-data-compatibility'),('invariant-preservation','invariant-preservation'),('model-conservativity','conservative-expansion')]}
 if required['classification']['rule_change']:
  values=[dimensions['model-conservativity'],dim('rule-extension-compatibility')]
  dimensions['model-conservativity']='verified-for-named-scope' if all(x=='verified-for-named-scope' for x in values) else 'violated' if 'violated' in values else 'unsupported' if 'unsupported' in values else 'unknown'
 if not unresolved and execution=='completed' and currentness=='current' and required['supported']:
  readiness='ready-for-review'
 elif any(row['verdict'] in {'violated','unsupported'} for row in results):readiness='blocked'
 else:readiness='unresolved'
 doc={'schema_version':'relational.cli-outcome/v1-candidate','command':command,
  'profile_id':required['classification']['profile'],'baseline_identity':proposal['baseline_identity'],
  'proposal_identity':required['proposal_identity'],'execution':execution,'currentness':currentness,
  'evidence':{'methods':sorted({r['evidence_method'] for r in results}),'policy_identity':g.c.identity(b.policy()),
   'trust_boundary':v.policy()['trust']+['exact supplied model and assessment truth; no authority admission']},
  'results':results,'required_hard_obligation_ids':ids,'missing_hard_obligation_ids':missing,
  'unresolved_hard_obligation_ids':unresolved,'readiness':readiness,'compatibility_dimensions':dimensions,
  'diagnostics':diagnostics or [],'authority_effect':'none'}
 o.validate(doc,ids)
 return doc


def verify(proposal,bundle=None,command='check-extension'):
 proposal=deepcopy(proposal);bundle=deepcopy(bundle)
 runs=HERE/'runs';runs.mkdir(exist_ok=True)
 output=Path(tempfile.mkdtemp(prefix='replay-',dir=runs))
 results=[];diagnostics=[];execution='completed';currentness='current'
 required=None;transport=None
 try:
  b.source_boundary(proposal)
  required=g.generate(proposal)
  b.execution_profile(proposal)
  if bundle is None:bundle=b.make_bundle(proposal)
  transport=b.validate_transport(proposal,bundle)
 except (ValueError,KeyError,TypeError,g.c.jsonschema.ValidationError) as error:
  if required is None:
   # Invalid transport has no proven policy scope. This is never vacuous success.
   return invalid_outcome(command,error)
  code='unsupported-profile' if isinstance(error,b.UnsupportedScope) else 'evidence-stale' if 'stale' in str(error) or 'another proposal' in str(error) else 'unsupported-profile' if not required['supported'] else 'input-invalid'
  if code=='evidence-stale':currentness='stale'
  else:currentness='unresolved'
  diagnostics.append(diagnostic(code,error))
  if not required['supported'] or isinstance(error,b.UnsupportedScope):
   for obligation in required['obligations']:
    results.append({'obligation_id':obligation['id'],'hard':True,
     'required_statement':{'id':obligation['name'],'definition_bindings':[s.binding(HERE/'bundle_contract.py')]},
     'execution':'not-run','currentness':currentness,'evidence_method':'none','verdict':'unsupported','evidence_refs':[],
     'diagnostics':[diagnostic(code,error,obligation['id'])]})
  return aggregate_results(proposal,results,'not-run',currentness,diagnostics,command)
 with tempfile.TemporaryDirectory(prefix='bundle-fresh-kernel-') as temp:
  replay=sem.Replay(proposal,Path(temp),output)
  proposal_binding=s.binding(output/'captured-proposal.json')
  for obligation in required['obligations']:
   oid=obligation['id'];name=obligation['name'];entry=transport['entries'][oid]
   row_execution='completed';method='none';verdict='unknown';detail={};row_diags=[]
   try:
    verdict,method,detail=replay.execute(name,entry,transport['loaded_artifacts'][oid])
    if verdict!='satisfied':row_diags=[diagnostic('obligation-'+verdict,detail.get('reason',detail.get('diagnostic',detail.get('unsupported','Required semantic evidence did not pass.'))),oid,name)]
   except v.isolation.IsolationError as error:
    row_execution=error.execution;execution=error.execution if error.execution!='completed' else execution
    verdict='unknown';detail={'diagnostic':str(error)};row_diags=[diagnostic('proof-execution-failed',error,oid,name)]
   except subprocess.TimeoutExpired as error:
    row_execution='timeout';execution='timeout';detail={'diagnostic':str(error)};row_diags=[diagnostic('checker-timeout',error,oid,name)]
   except (ValueError,KeyError,TypeError,g.c.jsonschema.ValidationError) as error:
    verdict='violated';detail={'diagnostic':str(error)};row_diags=[diagnostic('required-scope-invalid',error,oid,name)]
   except OSError as error:
    row_execution='unavailable';execution='unavailable';detail={'diagnostic':str(error)};row_diags=[diagnostic('checker-unavailable',error,oid,name)]
   # Exact R02 failures retain their actual execution/currentness axes.
   proof=detail.get('exact_proof',detail)
   if isinstance(proof,dict) and proof.get('execution') in {'timeout','unavailable','provider-error','not-run'}:
    row_execution=proof['execution'];verdict='unknown'
    if row_execution in {'timeout','unavailable','provider-error'}:execution=row_execution
   evidence=replay.write(name+'.json',{'schema':'relational.verified-obligation-evidence/v1-candidate',
    'proposal_identity':required['proposal_identity'],'obligation_id':oid,'requested_method':entry['method'],
    'execution':row_execution,'verdict':verdict,'evidence_method':method,'detail':detail,'authority_effect':'none'})
   definition= v.CATALOG[name][1] if name in b.PROOF_TARGETS else 'independently-required:'+name
   results.append({'obligation_id':oid,'hard':True,
    'required_statement':{'id':definition,'definition_bindings':[proposal_binding,s.binding(HERE/'semantic_replay.py'),s.binding(HERE/'bundle_contract.py')]},
    'execution':row_execution,'currentness':'current','evidence_method':method,'verdict':verdict,
    'evidence_refs':[evidence],'diagnostics':row_diags})
   print('verified',name,verdict,row_execution,file=sys.stderr,flush=True)
  replay.write('fresh-module-audit.json',{'modules':replay.logs,'authority_effect':'none'})
 try:
  replay.audit_generated()
  after=b.validate_transport(proposal,bundle)
  s.require(after['loaded_artifacts']==transport['loaded_artifacts'],'bound artifact content changed during replay')
  for oid,artifacts in after['loaded_artifacts'].items():
   if 'proof-submission' in artifacts:v.validate_submission(proposal,artifacts['proof-submission'])
 except (ValueError,KeyError,TypeError,g.c.jsonschema.ValidationError) as error:
  currentness='stale';diagnostics.append(diagnostic('evidence-stale',error))
  for row in results:
   row['currentness']='stale'
   if row['verdict']=='satisfied':row['verdict']='unknown'
 outcome=aggregate_results(proposal,results,execution,currentness,diagnostics,command)
 s.write(output/'outcome.json',outcome)
 return outcome


def main(mode='bundle'):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('bundle',type=Path);parser.add_argument('--proposal',required=True,type=Path)
 args=parser.parse_args();command='replay-evidence' if mode=='replay' else 'check-extension'
 try:outcome=verify(v.read_json(args.proposal),v.read_json(args.bundle),command)
 except (ValueError,OSError,KeyError,TypeError,g.c.jsonschema.ValidationError) as error:outcome=invalid_outcome(command,error)
 print(json.dumps(outcome,indent=2,ensure_ascii=False));return o.exit_code(outcome)

if __name__=='__main__':raise SystemExit(main())
