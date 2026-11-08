#!/usr/bin/env python3
"""Close exact supported non-rule scope and preserve the independent L3 handoff."""
from copy import deepcopy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'evolution/impact'))
import readiness as r
s=r.s
BASE=Path(__file__).resolve().parent


def check_rule_handoff(outcome,required):
    pending=outcome['missing_hard_obligations']
    s.require({o['name'] for o in pending}==set(r.g.RULE) and all(o['scope']=='L3' and o['hard'] for o in pending),'L3 handoff omitted a required proof')
    s.require(outcome['status']=='pending-L3' and not outcome['rule_scope_ready'],'rule extension marked ready at L2')
    s.require(outcome['proposal_identity']==required['proposal_identity'],'rule handoff proposal mismatch')
    return pending


def main():
    reviewed=[]
    for task_id in ['E01','E02','E03','E04','E05']:
        task=s.task(task_id);s.require(task['status']=='accepted','missing L2 task acceptance')
        binding=task['validation']['acceptance_ref'];s.check_binding(binding);receipt=s.read(s.ROOT/binding['path'])
        for item in receipt['artifacts']+receipt['dependency_bindings']:s.check_binding(item)
        reviewed.append(binding)
    impact=s.read(s.BASE/'evolution/impact/extension-impact-report.json')
    proposal=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json');required=r.g.generate(proposal)
    verified=r.evaluate(proposal,impact['fresh_submission'])
    s.require(verified==impact['fresh_extension'] and verified['status']=='supported-ready','L2 scope readiness not reproducible')
    s.require(not verified['missing_hard_obligations'],'missing non-rule hard obligation')
    s.require({o['name'] for o in required['obligations']}==set(r.g.NON_RULE),'non-rule policy set changed')
    rule_proposal=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json');rule_required=r.g.generate(rule_proposal)
    s.require(rule_required==impact['required_rule_obligations'],'rule obligation handoff stale')
    pending=check_rule_handoff(impact['rule_extension'],rule_required)
    controls=[]
    missing=deepcopy(impact['fresh_submission']);missing['obligations'].pop()
    try:r.evaluate(proposal,missing)
    except ValueError:controls.append({'name':'missing hard non-rule obligation','result':'rejected'})
    else:raise ValueError('missing obligation accepted at L2')
    unknown=deepcopy(proposal);unknown['after']['registry']['kinds'][-1]['unknown_constraints']='mandatory existing-language effect'
    unsupported=r.g.generate(unknown)
    s.require(not unsupported['supported'],'unknown preservation scope accepted')
    controls.append({'name':'unsupported preservation/conservativity scope','result':'unsupported; explicit new formal profile required'})
    fake=deepcopy(impact['rule_extension']);fake['status']='supported-ready';fake['rule_scope_ready']=True
    try:check_rule_handoff(fake,rule_required)
    except ValueError:controls.append({'name':'premature rule-changing readiness','result':'rejected','required_I06_G3':True})
    else:raise ValueError('premature rule status accepted')
    s.write(BASE/'l2-review.json',{'result':'accepted','review_mode':'Codex author self-review; candidate gate only',
        'authority_effect':'none','predecessors':reviewed,'proposal_identity':required['proposal_identity'],
        'approved_scope':{'profile':'fresh-kind-extension','registry_profile':'closed-required-string-ordered-pairs/v1',
            'structural_kinds_after':42,'ordered_pairs_after':551,'old_semantic_profile':'unchanged F0 three-kind semantics',
            'all_nine_non_rule_obligations':'discharged with current scoped evidence',
            'full_source_semantics':'unsupported; 263 inherited source-level obligations remain visible'},
        'compatibility_dimensions':verified['dimensions'],'L3_handoff':{'rule_proposal_identity':rule_required['proposal_identity'],
            'required_obligations':rule_required,'pending_rule_obligations':pending,
            'remaining_tasks':['I01','I02','I03','I04','I05','I06','G3'],'rule_readiness':'pending; no L2 authorization',
            'dependency_rule':'G2 closes supported non-rule work and does not depend on future I06 discharge.'},
        'controls':controls,'claim_ceiling':'Scoped candidate annotation extension readiness, not arbitrary new semantic constraints, rule readiness or authority admission.'})
    s.accept('G2',{'l2-review.json':BASE/'l2-review.json'},
        ['All five L2 predecessor receipts and their scoped dependencies are current; the exact nine non-rule obligations are discharged and the three compatibility dimensions remain separate for the fresh annotation proposal.',
         'The L3 handoff exports the exact rule proposal and complete independently generated requirements, including six still-pending rule obligations; no G2-to-I06 cycle or premature rule authorization is introduced.'],
        ['Rule-changing readiness remains pending-L3 and the actual I06/G3 gates are required before full rule use.',
         'Unknown old-language constraints cannot reuse these preservation/conservativity theorems and require a separately formalized profile; the baseline semantic unknowns remain explicit.'],
        [Path(__file__),s.BASE/'evolution/impact/readiness.py',s.BASE/'evolution/impact/extension-impact-report.json',s.BASE/'evolution/obligations/required-rule-obligations.json'])
    print(json.dumps({'task':'G2','result':'accepted','non_rule_obligations':9,'pending_rule_obligations':6}))


if __name__=='__main__':main()
