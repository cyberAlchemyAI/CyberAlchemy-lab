"""Keep obligation scope, currency and three compatibility dimensions separate."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'obligations'))
import generator as g
s=g.s
BASE=Path(__file__).resolve().parent
TARGETS={'invariant-preservation':'Registry.Evolution.RequiredPreservation',
         'conservative-expansion':'Registry.Models.RequiredConservativity'}


def policy():
    return {'schema':'relational.readiness-policy/v1','authority_effect':'none',
            'dimensions':['selected-data-compatibility','invariant-preservation','model-conservativity'],
            'supported_non_rule_scope':'exact closed-string ordered-pair declarations and unchanged F0 semantics',
            'rule_readiness_gate':'I06 and G3; never fully ready at L2',
            'full_source_semantic_scope':'unsupported; inherited 263 source-level obligations remain visible',
            'hard_obligation_rule':'Every independently required obligation for the requested scope must have current typed evidence.',
            'truth_verification':'This layer aggregates already checked evidence. Public untrusted submissions require the independent R02/R03 verifiers.',
            'bounded_search_rule':'No witness means unknown, not a proof or non-entailment verdict.'}


def evaluate(proposal,submission,scope='L2'):
    s.require(scope in {'L2','full'},'unsupported readiness scope')
    required=g.validate_submission(proposal,submission)
    if not required['supported']:
        return {'status':'unsupported','proposal_identity':required['proposal_identity'],'required':required,
                'dimensions':{k:'unsupported' for k in policy()['dimensions']},'authority_effect':'none'}
    entries={item['id']:item for item in submission['obligations']};missing=[]
    g.source_projection(proposal)
    for obligation in required['obligations']:
        entry=entries[obligation['id']]
        if obligation['scope']=='L3' and scope=='L2':
            missing.append(obligation);continue
        if entry.get('status')!='discharged' or not entry.get('evidence'):
            missing.append(obligation);continue
        for binding in entry['evidence']:s.check_binding(binding)
        # Compatibility and general proofs demand their stated evidence kinds.
        if obligation['name'] in {'invariant-preservation','conservative-expansion'}:
            s.require(entry.get('evidence_kind')=='general-theorem','bounded model/sample cannot discharge a universal theorem')
            s.require(entry.get('required_statement')==TARGETS[obligation['name']],'weakened or substituted general theorem statement')
        if obligation['name']=='inhabited-model':
            s.require(entry.get('evidence_kind')=='checked-model-witness','inhabitation requires a checked witness')
    dimensions={}
    for label,name in [('selected-data-compatibility','selected-data-compatibility'),('invariant-preservation','invariant-preservation'),('model-conservativity','conservative-expansion')]:
        entry=next(entries[o['id']] for o in required['obligations'] if o['name']==name)
        dimensions[label]='verified-for-named-scope' if entry.get('status')=='discharged' and not any(o['name']==name for o in missing) else 'pending'
    l2_missing=[o for o in missing if o['scope']=='L2'];l3_missing=[o for o in missing if o['scope']=='L3']
    status='pending' if missing else 'supported-ready'
    if required['classification']['rule_change']:
        status='pending-L3' if not l2_missing else 'pending-L2-and-L3'
        if scope=='full' and not missing:
            # L2 cannot authorize its own future rule result. Full use requires
            # the actual current I06/G3 receipts, selected by the trusted plan.
            for task_id in ['I06','G3']:
                task=s.task(task_id);s.require(task['status']=='accepted','rule readiness gate not accepted: '+task_id)
                binding=task['validation']['acceptance_ref'];s.check_binding(binding)
                receipt=s.read(s.ROOT/binding['path'])
                for b in receipt['artifacts']+receipt['dependency_bindings']:s.check_binding(b)
            report=s.read(s.ROOT/s.task('I06')['write_scope']/'rule-extension-report.json')
            s.require(report['result']=='pass' and report['proposal_identity']==required['proposal_identity'],'rule evidence belongs to another proposal or failed')
            status='supported-ready'
    return {'status':status,'proposal_identity':required['proposal_identity'],'dimensions':dimensions,
            'missing_hard_obligations':missing,'non_rule_scope_ready':not l2_missing,
            'rule_scope_ready':status=='supported-ready',
            'required':required,'full_source_semantics':'unsupported','authority_effect':'none'}
