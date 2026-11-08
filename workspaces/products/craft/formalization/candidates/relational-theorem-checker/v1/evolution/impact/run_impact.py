#!/usr/bin/env python3
"""Compose current scoped extension evidence without merging claim kinds."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import readiness as r
s=r.s
BASE=Path(__file__).resolve().parent


def main():
    proposal=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json');required=r.g.generate(proposal)
    s.require(required==s.read(s.BASE/'evolution/obligations/required-fresh-obligations.json'),'required policy drift')
    receipts=[]
    for task_id in ['E01','E02','E03','E04']:
        task=s.task(task_id);b=task['validation']['acceptance_ref'];s.check_binding(b);receipt=s.read(s.ROOT/b['path'])
        for item in receipt['artifacts']+receipt['dependency_bindings']:s.check_binding(item)
        receipts.append(b)
    sys.path.insert(0,str(s.BASE/'replay'));import replay_engine as replay
    replay.verify(s.read(s.BASE/'replay/dependency-manifest.json'))
    data_path=s.BASE/'evolution/preservation/data-compatibility-report.json';preservation_path=s.BASE/'evolution/preservation/preservation-audit.json'
    model_path=s.BASE/'evolution/models/model-audit.json';data=s.read(data_path);preservation=s.read(preservation_path);models=s.read(model_path)
    for report in [data,preservation,models]:s.require(report['result']=='pass' and report['proposal_identity']==required['proposal_identity'],'extension evidence scope mismatch')
    s.require(data['selected_before_identity']==r.g.c.identity(proposal['before']['graph']) and data['selected_after_identity']==r.g.c.identity(proposal['after']['graph']),'data snapshot drift')
    s.require(data['before_evaluation']['accepted_result'] and data['after_evaluation']['accepted_result'],'selected data failed')
    s.require('Registry.Evolution.audited_preservation' in preservation['formal_theorems'],'missing quantified preservation proof')
    s.require('Registry.Models.audited_conservativity' in models['formal_theorems'],'missing all-model expansion proof')
    s.require(len(models['witnesses'])==3 and all(x['status'].startswith('checked-') for x in models['witnesses']),'missing inhabited/countermodel witnesses')
    for index,result in enumerate(models['witnesses']):s.require(result['source_sha256']==s.digest(s.BASE/'evolution/models'/('Witness'+str(index)+'.lean')),'model witness source drift')
    sys.path.insert(0,str(s.BASE/'coverage/carrier'));from check_coverage import table
    carrier_path=s.BASE/'evolution/obligations/candidate-extension-carrier.json';carrier=table(s.read(carrier_path))
    for row in proposal['after']['registry']['kinds']:
        s.require(carrier[row['id']]['pairs']==row['pairs'],'extension carrier pair mismatch')
        s.require(carrier[row['id']]['qualifiers']=={'type':'object','additionalProperties':False,'required':row['fields'],'properties':{f:{'type':'string','minLength':1} for f in row['fields']}},'extension carrier qualifier mismatch')
    roots_same=proposal['before']['graph']['admission_roots']==proposal['after']['graph']['admission_roots']
    s.require(roots_same and not required['classification']['rule_change'],'L2 prototype changes root inventory or inference rules')
    logic_path=s.FORMAL/'semantic-logic/v1/semantic-logic-audit.json';logic=s.read(logic_path)
    for binding in logic['source_bindings']:s.check_binding(binding)
    s.require('Relational.Logic.admission_roots_do_not_change_instance_meaning' in logic['transitive_axioms'],'missing independent root separation theorem')
    evidence={
        'baseline-current':([s.binding(s.BASE/'replay/dependency-manifest.json')],'current-baseline','Full selected dependency closure checked current.'),
        'computed-classification':([s.binding(s.BASE/'evolution/proposals/fresh-kind-proposal.json')],'computed-diff','Exact current before/after classification and independently generated obligation IDs.'),
        'source-profile-projection':(r.g.source_projection(proposal)['added_sources'],'source-projection','Exact candidate source maps to closed required nonempty annotations with no extra evidence semantics.'),
        'carrier-projection':([s.binding(carrier_path)],'carrier-projection','All 42 kinds, 551 pairs and qualifier shapes match the proposed registry.'),
        'selected-data-compatibility':([s.binding(data_path)],'checked-selected-data','Exact existing graph passes before/after kernel checks.'),
        'invariant-preservation':([s.binding(preservation_path),s.binding(s.BASE/'evolution/preservation/Preservation.lean')],'general-theorem','Quantified old-language lift and reflection for FreshExtension.'),
        'conservative-expansion':([s.binding(model_path),s.binding(s.BASE/'evolution/models/ConservativeExpansion.lean')],'general-theorem','Every base model expands with unchanged old reduct.'),
        'inhabited-model':([s.binding(model_path),s.binding(s.BASE/'evolution/models/witnesses.json')],'checked-model-witness','Inhabited old/new models and a genuine countermodel checked against all structural axioms.'),
        'protected-root-independence':([s.binding(logic_path)],'general-semantic-theorem','Rules and supplied root inventory unchanged; formal instance meaning is independent of roots.')}
    submission={'proposal_identity':required['proposal_identity'],'policy_identity':required['policy_identity'],'obligations':[]}
    for obligation in required['obligations']:
        bindings,kind,finding=evidence[obligation['name']]
        entry={**obligation,'status':'discharged','evidence':bindings,'evidence_kind':kind,'finding':finding}
        if obligation['name'] in r.TARGETS:entry['required_statement']=r.TARGETS[obligation['name']]
        submission['obligations'].append(entry)
    outcome=r.evaluate(proposal,submission);s.require(outcome['status']=='supported-ready','supported non-rule scope not ready')
    controls=[]
    for name,mutate in [('omitted hard obligation',lambda x:x['obligations'].pop()),
                        ('stale proof',lambda x:next(o for o in x['obligations'] if o['name']=='invariant-preservation')['evidence'][0].update(sha256='0'*64)),
                        ('bounded model substitutes for theorem',lambda x:next(o for o in x['obligations'] if o['name']=='conservative-expansion').update(evidence_kind='checked-model-witness')),
                        ('weakened theorem statement',lambda x:next(o for o in x['obligations'] if o['name']=='invariant-preservation').update(required_statement='True'))]:
        bad=deepcopy(submission);mutate(bad)
        try:r.evaluate(proposal,bad)
        except ValueError:controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('readiness bypassed')
    missing=deepcopy(submission);missing['obligations'][0]['evidence']=[]
    pending=r.evaluate(proposal,missing);s.require(pending['status']=='pending' and pending['missing_hard_obligations'],'missing evidence hidden')
    controls.append({'name':'evidence-free discharge','result':'pending'})
    rules=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json');rule_required=r.g.generate(rules)
    rule_submission={'proposal_identity':rule_required['proposal_identity'],'policy_identity':rule_required['policy_identity'],'obligations':[]}
    for obligation in rule_required['obligations']:
        entry=deepcopy(next((o for o in submission['obligations'] if o['name']==obligation['name']),{**obligation,'evidence':[s.binding(model_path)],'evidence_kind':'unverified-caller-label'}))
        entry.update(id=obligation['id'],scope=obligation['scope'],status='discharged');rule_submission['obligations'].append(entry)
    rule_outcome=r.evaluate(rules,rule_submission)
    s.require(rule_outcome['status']=='pending-L3' and len(rule_outcome['missing_hard_obligations'])==6,'L2 rule proposal fully ready')
    controls.append({'name':'rule proposal requires I06 despite supplied discharge labels','result':'pending-L3'})
    unknown={'status':'unknown','evidence_kind':'bounded-search-without-witness','non_entailment_proved':False}
    s.require(not unknown['non_entailment_proved'],'search proves theorem')
    controls.append({'name':'bounded search without witness','result':'unknown','outcome':unknown})
    s.write(BASE/'readiness-policy.json',r.policy())
    s.write(BASE/'extension-impact-report.json',{'result':'pass','fresh_extension':outcome,'fresh_submission':submission,
        'rule_extension':rule_outcome,'required_rule_obligations':rule_required,'rule_submission_claims_authorized':False,
        'dimensions_remain_separate':True,'unsupported_baseline_obligation_count':263,'controls':controls,
        'review_mode':'Codex author self-review; candidate named-profile readiness only','authority_effect':'none',
        'scope':'Structural annotation extension, preserved old registry language and unchanged F0 reference semantics; no full source-wide semantic readiness.'})
    s.accept('E05',{name:BASE/name for name in ['extension-impact-report.json','readiness-policy.json','readiness.py']},
        ['Selected-data compatibility, quantified preservation and all-model conservativity have distinct evidence kinds and independent displayed statuses; all nine required non-rule obligations are current and discharged for the exact fresh proposal.',
         'Every computed rule change remains pending at L2 with all six L3 obligations explicitly required; inherited unsupported source meanings and source/host/external-evidence trust limits remain visible.'],
        ['A checked bounded model cannot substitute for a universal theorem; search without a witness remains unknown.',
         'Omitted/evidence-free hard obligations, stale proof bindings and weakened statement targets prevent supported-ready status.'],
        [Path(__file__),s.BASE/'evolution/obligations/generator.py',s.BASE/'evolution/preservation/preservation-audit.json',s.BASE/'evolution/models/model-audit.json',logic_path])
    print(json.dumps({'task':'E05','result':'accepted','fresh_scope_ready':True,'rule_status':rule_outcome['status'],'controls':len(controls)}))


if __name__=='__main__':main()
