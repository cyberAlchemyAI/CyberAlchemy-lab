"""Record an actual operator-captured response; labels do not authenticate a human.

Use only after a direct human response in this chat. The original message is a
trusted conversation input, not a theorem or an inference from machine passes.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'));import support as s
sys.path.insert(0,str(s.BASE/'s13'));import audit_successor as audit
HERE=Path(__file__).resolve().parent

def record(path):
 feedback=s.read(path)
 fields={'schema','response','source','received_at','reviewed_packet','scope','meaning','diagnostics','bounded_use'}
 s.require(set(feedback)==fields and feedback['schema']=='relational.actual-human-feedback/v1','invalid feedback envelope')
 s.require(feedback['source']=='direct-user-message-in-this-chat' and feedback['scope']=='successor-v2-worked-packet','unsupported response provenance/scope')
 s.require(isinstance(feedback['response'],str) and bool(feedback['response'].strip()) and isinstance(feedback['received_at'],str),'missing actual response')
 s.require(feedback['reviewed_packet']==s.binding(s.BASE/'s13/review-packet.md'),'feedback assessed another packet')
 s.require(feedback['meaning'] in ['fits','needs-revision'] and feedback['diagnostics'] in ['clear','needs-revision'] and feedback['bounded_use'] in ['appropriate','defer','needs-revision'],'invalid assessment')
 s.require(s.task('S14')['status']=='in-progress' and s.task('S13')['status']=='accepted','review prerequisites missing')
 for t in s.read(s.PLAN)['tasks']:
  if t['status']=='accepted':s.audit_receipt(s.check(t['receipt']))
 reviewed=s.read(HERE/'requirement-audit.json');closure_path=s.check(reviewed['current_source_closure'])
 s.require(closure_path==HERE/'final-source-closure.json','unexpected final audit path')
 closure=s.read(closure_path)
 # The full graph audit has just completed. Recheck every distinct audited
 # byte binding, rather than repeating its many documentary references.
 for binding in closure['bindings']:s.check(binding)
 s.require(closure['successor_reader']==s.binding(s.BASE/'s13/audit_successor.py'),'audit reader changed')
 dest=HERE/'human-feedback.json';dest.write_bytes(Path(path).read_bytes())
 final=s.read(HERE/'final-review.json');final['human_feedback']=s.binding(dest)
 required=s.read(HERE/'requirement-audit.json');required['human_feedback']=s.binding(dest)
 revising=feedback['meaning']=='needs-revision' or feedback['diagnostics']=='needs-revision' or feedback['bounded_use']=='needs-revision'
 if revising:
  final['use_qualification']='pending requested revisions';s.write(HERE/'final-review.json',final);s.write(HERE/'requirement-audit.json',required)
  print('Actual feedback recorded; requested revisions remain open. S14 and whole plan are not complete.');return
 final['use_qualification']='qualified bounded local candidate shadow use' if feedback['bounded_use']=='appropriate' else 'deferred bounded use on actual human assessment'
 final['whole_plan_complete']=True;final['remaining_task']=None
 for t in required['task_inventory']:
  if t['id']=='S14':t['status']='accepted'
 required['human_assessment_scope']='Actual successor worked-packet assessment only; no inference that every retained/deferred definition or original R06/G4 was reviewed.'
 s.write(HERE/'requirement-audit.json',required);final['requirements']=s.binding(HERE/'requirement-audit.json');s.write(HERE/'final-review.json',final)
 (HERE/'bounded-use-recommendation.md').write_text('# Bounded-use recommendation\n\n'+final['use_qualification']+'. This recommendation records the [actual response](human-feedback.json) about the exact [successor worked packet](../s13/review-packet.md).\n\n'+feedback['response']+'\n\nMeaning and diagnostic assessment, pure proof validity, and use suitability remain separate. All stated finite-profile, supplied-truth, tested-boundary, same-kernel, budget and cooperative-writer limits remain. [The requirement audit](requirement-audit.json) retains deferred semantics and original R06/G4 status. This successor response does not assess the original v1 review artifacts or authorize deployment, publication, admission, or live authority changes.\n')
 controls=s.read(HERE/'machine-review-controls.json');controls['controls']=[c for c in controls['controls'] if c!='actual human response absent and explicitly pending']+['actual successor human feedback recorded against current packet'];controls['reviewed_outputs']=[s.binding(HERE/f) for f in ['final-review.json','bounded-use-recommendation.md','requirement-audit.json']];s.write(HERE/'machine-review-controls.json',controls)
 receipt={'schema':'relational.v2-task-acceptance/v1','task':'S14','result':'accepted','review':'actual scoped human semantic/diagnostic/use assessment plus current machine evidence','criteria':[{'criterion':c,'finding':f,'result':'pass'} for c,f in zip(s.task('S14')['acceptance_criteria'],['Actual direct human response assesses the exact successor worked packet; use recommendation records its appropriate/deferred outcome.','No feedback inferred; requested revisions would leave acceptance and use qualification pending.','No deployment/publication/live authority effect; original R06/G4 remain pending.'])],'controls':[{'name':'exact-reviewed-packet-current','result':'pass'},{'name':'actual-response-verbatim-recorded','result':'pass'},{'name':'all-predecessor-proof-bindings-current','result':'pass'}],'artifacts':[s.binding(HERE/f) for f in ['final-review.json','bounded-use-recommendation.md','requirement-audit.json','context-pack.json','human-feedback.json']],'dependency_bindings':[s.task('S13')['receipt'],s.binding(HERE/'record_feedback.py'),s.binding(HERE/'final-source-closure.json')],'human_review':s.binding(dest),'authority_effect':'none'}
 receipt['artifacts']+=[s.binding(HERE/'machine-review-controls.json'),s.binding(HERE/'actual-response-capture.json')]
 s.write(HERE/'task-acceptance.json',receipt);plan=s.read(s.PLAN);task=next(t for t in plan['tasks'] if t['id']=='S14');task['status']='accepted';task['receipt']=s.binding(HERE/'task-acceptance.json')
 for unit in task['working_units']:unit['status']='accepted'
 s.write(s.PLAN,plan);s.sync()
 print('S14 accepted from actual human assessment; revised plan complete, original human gates unchanged.')

if __name__=='__main__':record(Path(sys.argv[1]))
