#!/usr/bin/env python3
"""Review complete named inference evidence before workflow integration."""
from copy import deepcopy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'inference/integration'))
import integration as i
s=i.s
BASE=Path(__file__).resolve().parent


def check_review(payload):
    profile=payload['root_policy'];closure=payload['closure'];lineage=payload['lineage'];independence=payload['independence']
    s.require(profile['coordinates']==['targetVersion(id,version)','effect','scope','capturedAuthorityEpoch'],'root tuple dimensions missing or ambiguous')
    s.require(profile['matching']=='Exact literal tuple equality, no wildcards, inherited scopes or version/epoch conversion.','root matching weakened')
    s.require(profile['conformance_is_root'] is False and profile['conformance_implies_not_admitted'] is False,'root policy conflates conformance and authority')
    s.require(profile['existing_admission_may_coexist_with_conformance'] is True and profile['root_observation_automatically_adds_admission'] is False,'existing admission/root distinction lost')
    s.require(closure['required_statement']=='Inference.RequiredClosureAdequacy','closure statement weakened')
    s.require({'Inference.ground_instances_complete','Inference.checked_closure_exact','Inference.saturation_sufficient_fuel','Inference.saturation_never_exhausts'}<=set(closure['formal_theorems']),'saturation completeness/termination proof missing')
    s.require(lineage['required_statement']=='Inference.RequiredProtectedLineage' and 'Inference.protected_lineage' in lineage['formal_theorems'],'generic lineage proof missing')
    s.require(lineage['conformance_implies_not_admitted'] is False and lineage['positive_existing_admission_coexistence_checked'] is True,'overstrong negative authority axiom introduced')
    s.require(independence['required_statement']=='Inference.RequiredCountermodelSoundness','countermodel theorem weakened')
    s.require(all(c['result']['non_entailment_proved'] for c in independence['semantic_non_entailment']),'semantic countermodel evidence missing')
    s.require(independence['profile_non_derivability']['non_derivability_proved'],'profile negative lacks complete closure')
    search=independence['failed_bounded_search']
    s.require(search['status']=='unknown' and not search['non_entailment_proved'] and not search['non_derivability_proved'],'failed search mistaken for proof')
    s.require(independence['positive_coexistence']['result']['accepted'],'conformance/admission coexistence model missing')
    return True


def main():
    predecessors=[]
    for task_id in ['I01','I02','I03','I04','I05','I06']:
        task=s.task(task_id);s.require(task['status']=='accepted','missing accepted inference task: '+task_id)
        binding=task['validation']['acceptance_ref'];s.check_binding(binding);receipt=s.read(s.ROOT/binding['path'])
        for b in receipt['artifacts']+receipt['dependency_bindings']:s.check_binding(b)
        predecessors.append(binding)
    proposal=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')
    report=s.read(s.BASE/'inference/integration/rule-extension-report.json');captured=i.capture(proposal)
    s.require(report['result']=='pass' and report['proposal_identity']==captured['proposal_identity'],'wrong or failed actual rule report')
    s.require(report['normal_form_identity']==captured['after_normal']['normal_form_identity'],'rule inference snapshot drift')
    i.verify_dependencies(proposal,s.read(s.BASE/'inference/integration/dependency-manifest.json'))
    integrated=i.validate_submission(proposal,report['submission'],report['normal_form_identity'])
    s.require(not integrated['missing_hard_obligations'] and len(integrated['required']['obligations'])==15,'rule obligations incomplete')
    payload={'root_policy':s.read(s.BASE/'inference/profile/protected-root-policy.json'),
        'closure':s.read(s.BASE/'inference/closure/closure-controls.json'),
        'lineage':s.read(s.BASE/'inference/protected/lineage-audit.json'),
        'independence':s.read(s.BASE/'inference/independence/non-entailment-report.json')}
    check_review(payload);controls=[]
    for name,mutate in [('missing closure adequacy',lambda x:x['closure'].update(formal_theorems=[])),
                        ('missing root coordinate',lambda x:x['root_policy']['coordinates'].pop()),
                        ('conformance used as authority root',lambda x:x['root_policy'].update(conformance_is_root=True)),
                        ('overstrong negative admission axiom',lambda x:x['root_policy'].update(conformance_implies_not_admitted=True)),
                        ('bounded search mislabeled non-entailment',lambda x:x['independence']['failed_bounded_search'].update(non_entailment_proved=True))]:
        bad=deepcopy(payload);mutate(bad)
        try:check_review(bad)
        except ValueError:controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('invalid inference gate accepted: '+name)
    s.write(BASE/'l3-review.json',{'result':'accepted','review_mode':'Codex author self-review; candidate gate only',
        'predecessors':predecessors,'proposal_identity':captured['proposal_identity'],
        'normal_form_identity':captured['after_normal']['normal_form_identity'],
        'approved_inference_profile':'Finite positive typed function-free range-restricted Horn rules over exact captured domain and roots.',
        'approved_extension_profile':'Captured ReviewSignal fresh-head/old-body proposal with complete 15-obligation evidence; no general permission for old-head or fresh recursive changes.',
        'proof_guarantees':['Generic derivation certificate soundness','Complete finite grounding and exact least closure',
            'Sufficient finite saturation bound','Every protected/carrier derivation retains an exact independent root',
            'Checked exact implication countermodels and coexistence','Every base model expands for the named rule-extension profile'],
        'negative_claims':{'semantic_non_entailment':'Checked model satisfies exact theory and premise with conclusion false.',
            'finite_profile_non_derivability':'Absence only from a kernel-certified complete least closure.',
            'unsuccessful_search':'Unknown; no theorem or absence claim.'},
        'trust_boundary':['Source meaning and unary conformance abstraction','Parser, host projection, canonical hashing, runtime and OS',
            'Independently supplied evidence/authority truth; no issuer authentication or real admission'],
        'remaining_semantics':'263 inherited source-level obligations remain unsupported outside the named profile.',
        'workflow_handoff':['R01 command/outcome contracts','R02 isolated untrusted proof verification','R03 independent bundle completeness',
            'R04 CLI/CI','R05 current application baseline','R06 shadow pilot and human review','G4 supported-use review'],
        'full_rule_readiness':'Requires this current accepted G3 receipt plus current I06 evidence; actual post-acceptance evaluation is checked by this runner.',
        'controls':controls,'authority_effect':'none'})
    s.accept('G3',{'l3-review.json':BASE/'l3-review.json','review.py':Path(__file__)},
        ['All six inference predecessor receipts and bound exports are accepted/current. The actual rule proposal has all 15 mandatory obligations, general soundness/closure/lineage proofs, exact scoped witnesses and universally quantified model expansion evidence.',
         'Semantic countermodel non-entailment, exact finite-profile closure absence and failed-search unknown are reviewed separately. Literal four-coordinate roots, positive admission/conformance coexistence and source/parser/runtime/external-truth limits remain explicit; public proof replay is left to R02/R03.'],
        ['Missing saturation adequacy/termination, omitted root dimensions, conformance-as-root, a negative admission axiom and mislabeled failed search all prevent gate acceptance.'],
        [s.BASE/'inference/integration/integration.py',s.BASE/'inference/integration/dependency-manifest.json',
         s.BASE/'inference/profile/protected-root-policy.json',s.BASE/'inference/independence/non-entailment-report.json'])
    final=i.r.evaluate(proposal,report['submission'],scope='full')
    s.require(final['status']=='supported-ready' and final['rule_scope_ready'],'post-gate scoped readiness did not become reproducible')
    print(json.dumps({'task':'G3','result':'accepted','controls':len(controls),'actual_rule_readiness':final['status'],
                     'required_obligations':len(final['required']['obligations']),'authority_effect':'none'}))


if __name__=='__main__':main()
