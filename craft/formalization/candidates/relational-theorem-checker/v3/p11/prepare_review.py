"""Bind the completed worked packet; keep synthetic contract tests separate from feedback."""
from pathlib import Path
import copy
import json
import re
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE.parent))
from v3.execution import support as s
from jsonschema import Draft202012Validator

if (HERE/'pending-question.json').exists():
    s.require(s.read(HERE/'pending-question.json')['status']=='prepared-not-yet-asked',
              'packet already issued for assessment; do not reset or regenerate its bindings')

def closed(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
def text(maximum=8192):
    return {'type':'string','minLength':1,'maxLength':maximum}
ref = closed({'path':text(4096),'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
assessment = {'enum':['fits','changes-needed']}
schema = {
    '$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'relational.actual-human-feedback/v3',
    **closed({
        'schema':{'const':'relational.actual-human-feedback/v3'},
        'packet':ref,
        'question':text(),
        'actual_answer':text(),
        'assessment_scope':{'const':'v3-worked-packet'},
        'source':{'const':'direct-user-message-in-this-chat'},
        'received_at':text(64),
        'assessment':closed({'meanings':assessment,'diagnostics':assessment,'bounded_local_shadow_use':assessment}),
        'human_assessment':{'const':True},
        'deployment_authorized':{'const':False},
        'authority_effect':{'const':'none'},
    }),
}
Draft202012Validator.check_schema(schema)
s.write(HERE/'feedback-record.schema.json',schema)
validator=Draft202012Validator(schema)
# Synthetic fixtures exercise the shape only and never become human-feedback.json.
example={'schema':'relational.actual-human-feedback/v3','packet':s.binding(HERE/'review-packet.md'),
    'question':'Synthetic schema test, not an assessment request.','actual_answer':'Synthetic contract fixture only.',
    'assessment_scope':'v3-worked-packet','source':'direct-user-message-in-this-chat','received_at':'synthetic-test',
    'assessment':{'meanings':'fits','diagnostics':'fits','bounded_local_shadow_use':'fits'},
    'human_assessment':True,'deployment_authorized':False,'authority_effect':'none'}
controls=[]
def test(name,condition):
    s.require(condition,name)
    controls.append({'name':name,'result':'pass'})
test('closed-feedback-shape-valid-synthetic-fixture',validator.is_valid(example))
for name,mutate in [
    ('empty-answer',lambda x:x.update(actual_answer='')),
    ('wrong-packet-scope',lambda x:x.update(assessment_scope='successor-v2-worked-packet')),
    ('extra-top-field',lambda x:x.update(approved=True)),
    ('bad-packet-digest',lambda x:x['packet'].update(sha256='')),
    ('extra-assessment-field',lambda x:x['assessment'].update(deployment='fits')),
    ('deployment-permission',lambda x:x.update(deployment_authorized=True)),
    ('author-review-as-human',lambda x:x.update(human_assessment=False)),
]:
    value=copy.deepcopy(example);mutate(value)
    test('feedback-schema-refuses-'+name,not validator.is_valid(value))

plan=s.read(s.PLAN)
accepted=[]
for task in plan['tasks']:
    if task['status']!='accepted':continue
    receipt=s.read(s.check(task['receipt']))
    for bound in receipt['artifacts']+receipt['inputs']:s.check(bound)
    accepted.append({'task':task['id'],'receipt':task['receipt'],'artifact_count':len(receipt['artifacts']),
                     'input_count':len(receipt['inputs']),'current':True})
test('eleven-accepted-current-predecessors',len(accepted)==11)
worked=s.read(HERE/'worked-examples.json')
test('sixteen-actual-worked-controls',worked['result']=='pass' and len(worked['controls'])==16 and all(c['result']=='pass' for c in worked['controls']))
bound_refs={}
def walk(value):
    if isinstance(value,dict):
        if set(value)=={'path','sha256'}:
            s.check(value);bound_refs[(value['path'],value['sha256'])]=value
        for item in value.values():walk(item)
    elif isinstance(value,list):
        for item in value:walk(item)
walk(worked)
test('worked-input-output-and-original-feedback-bindings-current',bool(bound_refs))
qualification_case=next(c for c in worked['cases'] if c['name']=='wrong-scope-full-qualification')
public=s.read(s.check(qualification_case['output']))
walk(public)
owned=s.check(public['qualification']['owned_run']).parent
new_run_refs=[s.binding(p) for p in owned.rglob('*') if p.is_file()]
for bound in new_run_refs:s.check(bound)
test('new-complete-kernel-run-artifacts-current',bool(new_run_refs) and public['status']=='qualified-candidate')
test('readers-do-not-reissue-new-mapped-events',worked['new_fresh_horn_qualifications']==1 and worked['new_mapped_qualifications']==0)

summaries=[
 ('P00','Formal evidence and freshness boundary','Compiled required statements distinguish exact current evidence from a live invocation event; model-expansion and activation guarantees retained.'),
 ('P01','Strict versioned contracts','Closed transport shapes, independent obligation inventories, bounded raw decoder and work/operator policies.'),
 ('P02','One exact proof-layout verifier','Combined and staged module roles check full structured statement and axiom inventories; same kernel remains a trust boundary.'),
 ('P03','Qualification and saved inspection','Explicit contexts and shared exact verification; reading a current saved result cannot create a live event.'),
 ('P04','Typed explanations','Complete-profile absence requires typed nonmembership; exact source/rule traces and potential/active/conflict distinctions.'),
 ('P05','Provenance currentness','Strict source/dependency closure and reread checks; documented exact legacy exceptions rather than broad path exemptions.'),
 ('P06','Supervised resource/cancellation path','Fixed worker owns decode through proof replay, bounds tools/run/output and completes cleanup before completion. Default RSS is advisory.'),
 ('P07','Owned runs and cache isolation','Unique immutable runs and independently anchored proof/import closure; public worker cannot accept caller-selected execution code.'),
 ('P08','Local transactions and recovery','Fresh proposal, separate fresh exact successor registration, mapped event ownership, concrete head/transaction binding, process crash and competing writer controls.'),
 ('P09','Unified adversarial API regression','492 coverage/control records include 342 inherited controls; actual two successive applications in each layout plus rich twenty-obligation proof, refusal and numeric trace checks. Records are not all new proof invocations.'),
 ('P10','Measured full proof cost','58 controls, two full cold/warm rich qualifications and two explicit complete-closure deadline refusals. No optimization or wider timing guarantee selected.'),
]
review=['# Successor implementation and review status','',
    'This is an author review with machine currentness checks. It is not the human P11 assessment. All 19 successor units remain selected; eleven are accepted, P11 is awaiting packet-specific assessment, and seven extensions are not started. The actual v2 feedback is retained only as comparison evidence.','',
    '| Unit | Implemented promise | Review finding and evidence |','| --- | --- | --- |']
for tid,title,finding in summaries:
    receipt=s.ROOT/s.task(tid)['receipt']['path']
    review.append(f'| {tid} | {title} | {finding} [Accepted receipt]({receipt}). |')
review += ['',
    'P11 adds 16 actual worked controls and one new complete wrong-scope qualification, followed by public typed absence inspection. It also executes public positive inspection/explanation and incomplete-manifest refusal, and produces new source-bound mapped and operational-failure explanations. Prior mapped results and numeric successor evidence remain recorded evidence. The new run does not create a shadow application.', '',
    'Definitions were reviewed against implementation: unary conformance cannot establish exact target/scope conformance; recursive derivation requires a seed; model expansion preserves arbitrary old models under checked-extension premises; complete-closure absence is absence of selected derivation rather than universal negation. Potential inheritance needs no positive condition, activation does, and active conflict retains both origins without supplying fulfillment or admission. Current evidence, fresh qualification, reviewed head and committed application remain distinct.', '',
    'The operational review retains exact worker/import/source closure, cleanup ordering, conditional cgroup capability, advisory-memory limitation, cooperating lock/storage assumptions, separate fresh successor registration, typed refusal causes and tested JSON/Lean bridge. Lean proves abstract statements; this report does not claim a verified OS, filesystem or JSON parser.', '',
    'The P10 stress failure is a real implementation limit: 4,144 candidate substitutions pass preflight but complete-closure proof compilation exceeds the atomic deadline twice. Do not declare all work ceilings simultaneously tractable, remove a required theorem, infer closure from preliminary modules, or claim a throughput guarantee. Optimization remains unselected because the measured bottleneck is proof/guard work, not the finite evaluator.', '',
    'The selected extension design notes remain proposals. Each unit begins with its formal definitions and obligation contract, then bounded implementation and adversarial validation. None is implemented by this packet. E00 conditions, E01 evidence aggregation, E02 chains, E03 fulfillment, E04 lifecycle, E05 checked IR and E06 independent checker all depend on accepted P11. Their semantic changes require separate profiles; accepted direct and positive-recursive core meanings remain the comparison baseline.', '',
    'Human completion is pending until a real reply is bound to the completed v3 packet bytes. The P11 source criterion requires actual in-scope feedback. No synthetic schema fixture, author judgment, elapsed time, previous-packet answer or selection of all extensions can substitute. Original v1 R06/G4 are separately pending and preserved. Candidate-only authority effect stays none.', '',
    f'[Worked packet]({HERE}/review-packet.md) · [Original gates]({HERE}/original-v1-gate-followup.md)', '']
(HERE/'plan-execution-review.md').write_text('\n'.join(review))

for name in ['review-packet.md','plan-execution-review.md','original-v1-gate-followup.md']:
    body=(HERE/name).read_text()
    for target in re.findall(r'\]\((/[^)]+)\)',body):
        path=re.sub(r':\d+$','',target)
        s.require(Path(path).is_file(),'broken review link '+target)
test('all-review-file-links-exist',True)
test('all-selected-extensions-still-outstanding',all(s.task('E'+str(n).zfill(2))['selected'] and s.task('E'+str(n).zfill(2))['status']=='not-started' for n in range(7)))
packet=s.binding(HERE/'review-packet.md')
question=(f'After reading the [v3 worked review packet]({HERE}/review-packet.md), do its relation meanings fit your intent, '
          'are the worked diagnostics clear, and are its measured limits suitable for bounded candidate-only local shadow use? '
          'P11 requires your actual assessment of this packet before the seven selected extensions can start.')
s.write(HERE/'pending-question.json',{'packet':packet,'assessment_scope':'v3-worked-packet','question':question,
    'status':'prepared-not-yet-asked','actual_answer':None,'source_criterion':'Human gates close only with actual in-scope feedback.',
    'authority_effect':'none'})
s.write(HERE/'review-controls.json',{'result':'pass','controls':controls,'worked_controls':worked['controls'],
    'schema_fixtures':'Synthetic contract tests only; no human feedback created.',
    'checked_worked_bindings':list(bound_refs.values()),'new_kernel_run_artifacts':new_run_refs,
    'authority_effect':'none'})
audit={'schema':'relational.v3-p11-completion-audit/v1','result':'machine-and-author-complete-human-pending',
    'machine_complete':True,'author_complete':True,'human_assessment':'pending','p11_accepted':False,
    'packet':packet,'feedback_schema':s.binding(HERE/'feedback-record.schema.json'),
    'worked_examples':s.binding(HERE/'worked-examples.json'),'review_controls':s.binding(HERE/'review-controls.json'),
    'author_review':s.binding(HERE/'plan-execution-review.md'),
    'accepted_predecessors':accepted,'accepted_count':len(accepted),'selected_count':19,
    'new_complete_horn_qualifications':1,'new_mapped_qualifications':0,
    'remaining_selected':['P11']+['E'+str(n).zfill(2) for n in range(7)],
    'original_gates':{'R06':'pending-separate','G4':'pending-separate'},
    'goal_complete':False,'authority_effect':'none'}
s.write(HERE/'completion-audit.json',audit)
s.write(BASE/'execution/progress-audit.json',{'result':'pass','accepted':accepted,'goal_complete':False,'authority_effect':'none'})
(BASE/'execution/PROGRESS.md').write_text('# Complete-plan execution\n\n11 of 19 selected units accepted: P00–P10. P11 machine and author review are complete; the actual assessment of the v3 packet is pending. All seven selected extensions E00–E06 remain not started behind P11. Original v1 R06/G4 remain separately pending. No deployment or live authority transition.\n\n[Worked packet]('+str(HERE/'review-packet.md')+') · [Completion audit]('+str(HERE/'completion-audit.json')+')\n')
print('P11 packet ready:',len(controls),'review checks;',len(new_run_refs),'current new-run artifacts; human assessment pending',flush=True)
