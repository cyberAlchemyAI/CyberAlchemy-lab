"""Candidate Product assessment with explicit unsupported and missing-pilot residue.

This separate private profile never claims the original ready-only adapter
passed, a pilot was performed, or an accountable owner decided a release.
"""
import copy
import json
from pathlib import Path
import profiles as P
import bundle as B
import coordination as CC
from jsonschema import Draft202012Validator
IMPLEMENTATION_SHA='5fc53fd2fc2b0e733fe60782b9c2d9e778e65fb26f8b43e4176d3474b14036c8'
ASSESSMENT_SHA='79692eb26045e20e07240e937802339dca7c8521feacf22830372660fbfdbf85'

def implementation(profile):
    raw=(P.RETAINED/'engineering/workflow/implementation.json').read_bytes()
    P.need(P.sha(raw)==IMPLEMENTATION_SHA,'actual retained implementation declaration differs')
    body=json.loads(raw);Draft202012Validator(profile['module'].carrier('implementation')[1]).validate(body)
    P.need(body['payload']['execution_entrypoint_ref'].endswith(profile['manifest']['output_source_sha256']),
           'retained implementation does not name actual corrected source')
    identity=body['node_id'];return {'scope_ref':profile['scope_ref'],'identity_ref':identity,'version_ref':identity+'@candidate.1',
      'carrier_ref':'cal.artifact-type.implementation/v1','byte_sha256':P.sha(raw)},raw

def construct(profile,*,product,capability,principal,seed):
    P.guard(profile);scope=profile['scope_ref'];P.need(profile['kind']=='engineering','original engineering Work profile required')
    ph,pr=product;ch,cr=capability;pb=json.loads(pr);cb=json.loads(cr)
    P.need(ph['byte_sha256']==P.sha(pr) and ch['byte_sha256']==P.sha(cr) and ph['identity_ref']==pb['product_id']
           and ch['identity_ref']==cb['node_id'] and ph['scope_ref']==ch['scope_ref']==scope,
           'exact selected Product/Capability original differs')
    Draft202012Validator(json.loads((P.ROOT/'authority/artifact-types/product-identity/v2/schema.json').read_bytes())).validate(pb)
    Draft202012Validator(profile['module'].carrier('product-capability')[1]).validate(cb)
    ih,ir=implementation(profile);ib=json.loads(ir)
    P.need(ch['version_ref'] in ib['payload']['realizes_capability_refs'],'retained implementation belongs to another Capability')
    assessment_raw=(P.RETAINED/'engineering/workflow/work-outcome-assessment.json').read_bytes()
    P.need(P.sha(assessment_raw)==ASSESSMENT_SHA,'independently selected unsupported original assessment differs')
    actual=json.loads(assessment_raw);P.need(actual['payload']['disposition']=='unsupported' and actual['payload']['subject_ref'] in (profile['original_work']['identity_ref'],profile['original_work']['version_ref']),
      'actual retained Work assessment meaning differs')
    # Re-execute the retained reader's compile and exact seven-evidence checks;
    # no implementation behavior, pilot or original experiment is re-executed.
    _,_,actual_producer=B.construct(profile)
    observed=actual_producer['origins']['transition:engineering:implemented']['later_computation']
    base=P.ROOT/'authority/artifact-types/capability-realization-binding/v2'
    binding=json.loads((base/'fixtures/valid/record.json').read_bytes());identity='capability-realization-binding:negative-local-product:'+seed
    binding.update(node_id=identity,scope_ref=scope,owner_ref=principal,owner_route='route:private-candidate-product-review',
      capability_ref=ch['identity_ref'],capability_version_ref=ch['version_ref'],binding_version='local-negative-candidate.1',
      realization_refs=[{'realization_kind':'implementation','realization_ref':ih['version_ref'],'owner_ref':ib['owner_ref'],
        'contract_ref':ib['payload']['conforms_to_schema_refs'][0]}],adoption_decision_ref=None,binding_state='candidate',status='candidate-unadmitted',
      observation_refs=['actual-retained-producer:'+P.RESULT_SHA,'actual-retained-unsupported-assessment:'+ASSESSMENT_SHA],conformance_refs=[],successor_refs=[],
      contract={'input_contract_refs':copy.deepcopy(ib['payload']['conforms_to_schema_refs']),
        'output_contract_refs':['protocol:W03-exact-implementation-bytes'],'context_policy_refs':['policy:private-negative-product-assessment']},
      limitations=['Candidate association of an exactly observed retained implementation only.',
        'The retained original Work assessment remains unsupported with FLAG evidence.',
        'No actual human pilot, current liveness, full Product conformance, adoption or release is established.'])
    Draft202012Validator(json.loads((base/'schema.json').read_bytes())).validate(binding)
    work_assessment=copy.deepcopy(actual);aid='work-outcome-assessment:negative-local-product:'+seed
    work_assessment.update(node_id=aid,owner_ref=principal,name='Retained implementation outcome and missing pilot evidence',successor_refs=[],
      evidence_refs=['actual-retained-unsupported-assessment:'+ASSESSMENT_SHA,'actual-retained-producer:'+P.RESULT_SHA],
      claim_ceiling='The original Work/Goal and unsupported outcome remain unchanged. This new candidate records pilot-readiness gaps; no pilot was performed or human benefit measured.')
    work_assessment['payload'].update(disposition='unsupported',subject_ref=profile['original_work']['version_ref'],
      expected_result_ref=actual['payload']['expected_result_ref'],observed_result_ref='actual-retained-unsupported-assessment:'+ASSESSMENT_SHA,
      gap_refs=list(dict.fromkeys(actual['payload']['gap_refs']+['gap:actual-human-pilot-not-performed','gap:current-Product-conformance-not-established'])),
      evidence_refs=['actual-retained-unsupported-assessment:'+ASSESSMENT_SHA,'actual-retained-producer:'+P.RESULT_SHA])
    Draft202012Validator(profile['module'].carrier('work-outcome-assessment')[1]).validate(work_assessment)
    # An unadmitted recommendation draft is tested separately; it cannot
    # discharge the original exact-owner-outcome obligation or third transition.
    decision,schema=CC.CC.fixture('decision','v2');did='decision:negative-local-product-recommendation:'+seed
    decision.update(node_id=did,owner_ref=principal,scope_ref=scope,evidence_refs=['actual-retained-unsupported-assessment:'+ASSESSMENT_SHA],relation_refs=[],successor_refs=[],
      name='Candidate recommendation to defer actual owner release review',claim_ceiling='Unadmitted metadata recommendation only; no accountable owner outcome, adoption, release or authority effect.')
    decision['payload'].update(decision_maker_ref=principal,subject_refs=[identity+'@local-negative-candidate.1',aid+'@local-negative-candidate.1'],
      selected_outcome='Recommend deferral to the actual accountable owner; no owner outcome is recorded.',declared_effect_refs=[],
      evidence_basis_refs=['actual-retained-unsupported-assessment:'+ASSESSMENT_SHA])
    # The original v2 contract may require a declared Effect even for a draft;
    # do not invent one merely to satisfy an owner outcome. Record exact refusal.
    draft_errors=sorted(e.message for e in Draft202012Validator(json.loads(schema.read_bytes())).iter_errors(decision))
    raws={};transitions={}
    for ref,body,carrier in [('transition:product-adoption-release:candidate-assessed',binding,'cal.artifact-type.capability-realization-binding/v2'),
      ('transition:product-adoption-release:pilot-assessed',work_assessment,'cal.artifact-type.work-outcome-assessment/v1')]:
        raw=P.enc(body);h={'scope_ref':scope,'identity_ref':body['node_id'],'version_ref':body['node_id']+'@local-negative-candidate.1','carrier_ref':carrier,'byte_sha256':P.sha(raw)}
        B.S.original_carriers().output(h,raw,scope_ref=scope,transition_ref=ref);raws[h['version_ref']]=raw;transitions[ref]=[h]
    receipt={'schema_version':'lab-private-negative-product-assessment/v1','original_work':profile['original_work'],
      'original_producer_source_cut':profile['original_producer_source_cut'],'selected_product':ph,'selected_capability':ch,'selected_observed_implementation':ih,
      'actual_original_assessment_sha256':ASSESSMENT_SHA,'actual_original_assessment_disposition':'unsupported','later_original_computation':observed,
      'human_pilot_performed':False,'actual_pilot_result_available':False,'local_pilot_phase_meaning':'Assess missing pilot-readiness evidence; retain unsupported original Work outcome.',
      'original_ready_only_adapter_invoked':False,'original_Work_Goal_or_outcome_rewritten':False,'transitions':transitions,
      'excluded_original_transition':{'transition_ref':'transition:product-adoption-release:release-reviewed','required_role':'role:accountable-owner',
        'required_obligation':'obligation:exact-owner-outcome','reason':'Actual accountable owner release outcome is outside this local fixture grant; absent human pilot and unsupported original Work remain explicit.'},
      'unadmitted_recommendation_draft':decision,'recommendation_schema_errors':draft_errors,'actual_owner_outcome':None,'canonical_admissions':0,'authority_effect':'none'}
    P.guard(profile);return transitions,raws,receipt,(ih,ir)
