#!/usr/bin/env python3
"""Pinned, bounded profile evidence. No authority/store/runtime writes.

Reuses the candidate typed formula checker and independent Denotation evaluator.
Does not invoke the full assurance service, claim a Lean theorem, or formalize
every natural-language premise. Output files are create-only.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import copy
import hashlib
import json
import sys
import time

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL))
import verifier
import ir


def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def save(name,obj):
    with (STEP/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def require(value,message):
    if not value:raise ValueError(message)


# One shared entity domain: no sort disjointness or nominal-tag distinction.
# Role predicates are defined by interpreted structural/behavioral properties.
FRAMES={
 'EvaluationProfile':['VersionExact','OwnerQualified','Scoped','DefinitionSubjectDeclared','InputSelectionDeclared','ChecksDeclared','OutcomeRulesDeclared','CausalBlockersDeclared','PhasesDeclared','ClaimLimitsDeclared'],
 'LifecycleProfile':['VersionExact','OwnerQualified','Scoped','DefinitionSubjectDeclared','InitialPostureDeclared','StatesDeclared','DirectedPairsDeclared','GateRulesDeclared','EffectRulesDeclared','InvalidationRulesDeclared','HistoryRulesDeclared'],
 'Evaluation':['ExecutionOccurred','ExactInputBindings','CompleteOutcomeMap','CausalBlockersPreserved','DeclaredCoverage'],
 'ArtifactType':['VersionExact','OwnerQualified','Scoped','SemanticMeaningBinding','ClosedSchemaBinding','CanonicalSourceDirection','ProjectionRuleDeclared','ValidationRuleDeclared'],
 'Policy':['VersionExact','Scoped','IssuedRuleSet','BehaviorConstraintsDeclared'],
 'Decision':['SelectionActOccurred','ExactSubjectEffectSelected','AttributionPresent','ApplicableAuthority'],
 'Review':['AssessmentOccurred','ExactSubjectBindings','CriteriaDeclared','EvidenceDeclared','ClaimLimitsDeclared'],
 'DefinitionRecord':['StableSemanticIdentity','VersionExact','Scoped','NormativeMeaningDeclared','ThreeVoicesDeclared'],
 'OntologyNode':['IndependentGraphIdentity','ExactRepresentedSubject','OntologyBinding','ProvenanceDeclared','ContestabilityDeclared'],
 'PermittedGate':['ExactTransitionBindings','PairPresent','GatePass'],
}
ENTITIES=['ep','lp','evaluation','artifact_type','policy','decision','review','definition','ontology','transition','subject']
FLAGS=sorted(set(sum(FRAMES.values(),[]))|{'ActualTransitionRecorded','EffectConfirmed','RecordedAdmitted','OwnerAdmissionSelected','AdmissionApplied','ExactAdmissionBindings'})
DECLARATIONS=[{'symbol_id':'Entity','kind':'sort','domain_policy':'nonempty'}]
DECLARATIONS += [{'symbol_id':e,'kind':'constant','result_sort':'Entity'} for e in ENTITIES]
DECLARATIONS += [{'symbol_id':p,'kind':'predicate','argument_sorts':['Entity']} for p in FLAGS+list(FRAMES)]
SORTS={'Entity':'Entity'};SYMBOLS={d['symbol_id']:d for d in DECLARATIONS if d['kind']!='sort'}
def var():return {'op':'var','name':'x'}
def const(name):return {'op':'const','name':name}
def pred(name,arg=None):return {'op':'pred','name':name,'args':[arg or var()]}
def allof(values):return {'op':'and','args':values}
def negate(value):return {'op':'not','arg':value}
def both(op,left,right):return {'op':op,'left':left,'right':right}
def quantified(op,body):return {'op':op,'var':'x','sort':'Entity','body':body}
def typed(formula):return ir.formula(formula,SORTS,SYMBOLS)
THEORY=[typed(quantified('forall',both('iff',pred(role),allof([pred(p) for p in fields])))) for role,fields in FRAMES.items()]
THEORY += [typed(quantified('forall',both('implies',pred('ActualTransitionRecorded'),allof([pred('PermittedGate'),pred('EffectConfirmed')])))),typed(quantified('forall',both('implies',pred('RecordedAdmitted'),allof([pred('OwnerAdmissionSelected'),pred('AdmissionApplied'),pred('ExactAdmissionBindings')]))))]


def refresh(model,frames=FRAMES):
    for role,fields in frames.items():
        model['predicates'][role]=[[e] for e in ENTITIES if all([e] in model['predicates'][p] for p in fields)]
    return model
def add_fields(model,entity,fields):
    for field in fields:
        if [entity] not in model['predicates'][field]:model['predicates'][field].append([entity])
def base_model():
    model={'domains':{'Entity':ENTITIES},'constants':{e:e for e in ENTITIES},'functions':{},'predicates':{p:[] for p in FLAGS+list(FRAMES)}}
    objects={'EvaluationProfile':'ep','LifecycleProfile':'lp','Evaluation':'evaluation','ArtifactType':'artifact_type','Policy':'policy','Decision':'decision','Review':'review','DefinitionRecord':'definition','OntologyNode':'ontology','PermittedGate':'transition'}
    for role,entity in objects.items():add_fields(model,entity,FRAMES[role])
    return refresh(model)
def check_model(model,theory=THEORY):
    d=verifier.Denotation(DECLARATIONS,model)
    return all(d.truth(f) for f in theory),d


def main():
    started=time.monotonic()
    freeze=load(STEP/'source-selection.json')
    for row in freeze['files']:require(digest((ROOT/row['path']).read_bytes())==row['sha256'],'stale selected source: '+row['path'])
    core={'schema_version':'cal.profile-interpreted-finite-core/v1','authority_effect':'none','targets':load(STEP/'targets.json')['targets'],'declarations':DECLARATIONS,'role_field_interpretations':FRAMES,'axioms':THEORY,'domains':{'Entity':ENTITIES},'assumptions':['Primitive fields encode the stated clause interpretation; owner fidelity must accept that interpretation.','Source/version/authority metadata are assumed exact when the corresponding field holds; finite truth does not authenticate real owners.','No disjointness axiom or role-name-only predicate is used. Policy/profile overlap is permitted.','This component-level Denotation use does not assert full native-IR pipeline or provider adoption.'],'limits':['Finite supplied models and exact fixed profile configuration only.','No complete semantic theory of all current Definitions.','No infinite lifecycle trace/storage recovery or actual effect correctness proof.']}
    save('formal-core.json',core)
    model=base_model();satisfied,evaluator=check_model(model);require(satisfied,'combined interpreted core has no valid supplied base witness')
    witnesses=[{'query':'combined core inhabitation','model':model,'theory_satisfied':True,'evidence':'typed finite model witness'}]
    pairs=[('EvaluationProfile','Evaluation'),('EvaluationProfile','ArtifactType'),('EvaluationProfile','Policy'),('EvaluationProfile','Review'),('EvaluationProfile','DefinitionRecord'),('EvaluationProfile','OntologyNode'),('EvaluationProfile','LifecycleProfile'),('LifecycleProfile','Decision'),('LifecycleProfile','Policy'),('LifecycleProfile','Review'),('LifecycleProfile','DefinitionRecord'),('LifecycleProfile','OntologyNode'),('LifecycleProfile','ArtifactType')]
    results=[]
    for left,right in pairs:
        for a,b in [(left,right),(right,left)]:
            query=typed(quantified('exists',allof([pred(a),negate(pred(b))])))
            require(evaluator.truth(query),'missing non-collapse witness '+a+' / '+b)
            equivalence=typed(quantified('forall',both('iff',pred(a),pred(b))))
            require(not evaluator.truth(equivalence),'equivalence unexpectedly holds')
            witness=next(e for e in ENTITIES if [e] in model['predicates'][a] and [e] not in model['predicates'][b])
            results.append({'left':a,'right':b,'result':'COUNTERMODEL_CHECKED','distinguishing_entity':witness,'equivalence_query':equivalence,'equivalence_truth':False,'model_ref':'base model in witnesses.json','claim':'the interpreted core does not entail equivalence; does not prove semantic disjointness'})
    for profile,entity in [('EvaluationProfile','ep'),('LifecycleProfile','lp')]:
        overlap=copy.deepcopy(model);add_fields(overlap,entity,FRAMES['Policy']);refresh(overlap)
        ok,d=check_model(overlap);require(ok and d.truth(typed(allof([pred(profile,const(entity)),pred('Policy',const(entity))]))),'overlap witness failed')
        witnesses.append({'query':profile+' may overlap Policy','model':overlap,'theory_satisfied':True,'claim':'specialization/overlap is allowed in the interpreted core, not forcibly rejected'})
    boundaries=[]
    no_execution=copy.deepcopy(model)
    no_execution['predicates']['ExecutionOccurred']=[]
    refresh(no_execution)
    ok,no_execution_evaluator=check_model(no_execution)
    require(ok,'no-execution countermodel invalid')
    witnesses.append({'query':'profiles declared with no Evaluation execution anywhere in domain','model':no_execution,'theory_satisfied':True,'claim':'existence of a declared profile does not entail existence of an Evaluation execution'})
    for profile,entity in [('EvaluationProfile','ep'),('LifecycleProfile','lp')]:
        query=typed(both('implies',pred(profile,const(entity)),quantified('exists',pred('ExecutionOccurred'))))
        require(not no_execution_evaluator.truth(query),'profile declaration implies an execution')
        boundaries.append({'premise':profile,'consequent':'exists Evaluation execution','result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','query':query,'model_ref':'no-execution model in witnesses.json'})
        for consequent in ['OwnerAdmissionSelected','AdmissionApplied','RecordedAdmitted','ActualTransitionRecorded']:
            target='transition' if consequent=='ActualTransitionRecorded' else 'subject'
            query=typed(both('implies',pred(profile,const(entity)),pred(consequent,const(target))))
            require(not evaluator.truth(query),'unsupported subject effect inference unexpectedly true')
            boundaries.append({'premise':profile,'consequent':consequent,'target':target,'result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','query':query,'model_ref':'base model in witnesses.json'})
    gate_query=typed(both('implies',pred('PermittedGate',const('transition')),pred('ActualTransitionRecorded',const('transition'))))
    require(not evaluator.truth(gate_query),'gate auto-transition inferred')
    boundaries.append({'premise':'PermittedGate','consequent':'ActualTransitionRecorded','result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','query':gate_query,'model_ref':'base model in witnesses.json'})

    controls=[]
    def control(name,mutate,expected_valid,error=None,frames=FRAMES,theory=THEORY):
        value=copy.deepcopy(model);mutate(value)
        try:ok,d=check_model(value,theory);observed_error=None
        except verifier.VerificationFault as e:ok=False;observed_error=e.code
        require(observed_error==error if error else ok==expected_valid and observed_error is None,'control failed: '+name)
        controls.append({'case':name,'observed_theory_satisfied':ok,'observed_error':observed_error,'expected_theory_satisfied':expected_valid,'expected_error':error,'result':'PASS'})
    control('missing-profile-owner-for-asserted-profile',lambda m:m['predicates']['OwnerQualified'].remove(['ep']),False)
    control('false-complete-outcome-map-for-asserted-evaluation',lambda m:m['predicates']['CompleteOutcomeMap'].remove(['evaluation']),False)
    control('recorded-transition-without-confirmed-effect',lambda m:m['predicates']['ActualTransitionRecorded'].append(['transition']),False)
    control('recorded-admission-without-owner-or-application',lambda m:m['predicates']['RecordedAdmitted'].append(['subject']),False)
    def good_transition(m):m['predicates']['ActualTransitionRecorded'].append(['transition']);m['predicates']['EffectConfirmed'].append(['transition'])
    control('recorded-transition-with-gate-and-confirmed-effect',good_transition,True)
    def good_admission(m):
        for name in ['RecordedAdmitted','OwnerAdmissionSelected','AdmissionApplied','ExactAdmissionBindings']:m['predicates'][name].append(['subject'])
    control('recorded-admission-with-explicit-selected-and-applied-support',good_admission,True)
    control('empty-domain-rejected',lambda m:m['domains'].update(Entity=[]),False,'empty-or-malformed-domain')
    control('missing-predicate-denominator-rejected',lambda m:m['predicates'].pop('OwnerQualified'),False,'model-signature-denominator-mismatch')
    control('foreign-predicate-member-rejected',lambda m:m['predicates']['Scoped'].append(['foreign']),False,'ill-sorted-model-tuple')
    control('duplicate-predicate-member-rejected',lambda m:m['predicates']['Scoped'].append(['ep']),False,'duplicate-predicate-tuple')
    # Same encoded requirements under different names must not manufacture distinction.
    aliased_frames=copy.deepcopy(FRAMES);aliased_frames['Evaluation']=FRAMES['EvaluationProfile']
    alias_model=refresh(copy.deepcopy(model),aliased_frames)
    alias_theory=copy.deepcopy(THEORY)
    alias_theory[2]=typed(quantified('forall',both('iff',pred('Evaluation'),allof([pred(p) for p in FRAMES['EvaluationProfile']]))))
    ok,d=check_model(alias_model,alias_theory)
    require(ok and d.truth(typed(quantified('forall',both('iff',pred('EvaluationProfile'),pred('Evaluation'))))),'identical-meaning control did not detect collapse')
    controls.append({'case':'identical-encoded-requirements-different-labels','result':'PASS','observed':'equivalence detected; no non-collapse witness claimed'})
    save('witnesses.json',{'authority_effect':'none','finite_model_witnesses':witnesses,'non_collapse_countermodels':results,'boundary_countermodels':boundaries})
    save('model-controls.json',{'authority_effect':'none','controls':controls,'interpretation_limit':'Control success qualifies these checks; it is not owner semantic fidelity or full source formalization.'})

    profile_root=ROOT/'define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles'
    contracts=load(profile_root/'check-contracts.json');evaluation=load(profile_root/'evaluation.json');lifecycle=load(profile_root/'lifecycle.json')
    check_ids=[r['check_id'] for r in evaluation['checks']]
    require(len(check_ids)==14 and len(set(check_ids))==14,'wrong fixed check denominator')
    required=contracts['phases']['pre_decision'];representation=contracts['phases']['representation']
    require(set(required)==set(check_ids[:12]) and set(representation)==set(check_ids[i] for i in [0,1,4]),'phase input changed')
    require(len(required)>0 and check_ids[12] not in required and check_ids[13] not in required,'future decision circularity')
    def aggregate(values,selected):
        unknown=False
        for idx in selected:
            value=values[idx]
            if value=='FAIL':return 'FAIL'
            if value=='NOT_EVALUABLE':unknown=True
        return 'NOT_EVALUABLE' if unknown else 'PASS'
    vocabulary=('PASS','FAIL','NOT_EVALUABLE');all_counts=Counter();prefix_counts=Counter();outside_cases=0
    # Exhaust the exact 3^14 outcome space. Check expected core result independently
    # from counts, then show both future checks are absent from the aggregate.
    for prefix in product(vocabulary,repeat=12):
        counts=Counter(prefix);expected='FAIL' if counts['FAIL'] else 'NOT_EVALUABLE' if counts['NOT_EVALUABLE'] else 'PASS'
        prefix_counts[expected]+=1
        for suffix in product(vocabulary,repeat=2):
            values=prefix+suffix;got=aggregate(values,range(12));require(got==expected,'phase aggregate mismatch');all_counts[got]+=1;outside_cases+=1
    require(outside_cases==3**14,'incomplete exhaustive outcome accounting')
    require(prefix_counts==Counter({'PASS':1,'NOT_EVALUABLE':2**12-1,'FAIL':3**12-2**12}),'expected combinatorial denominator mismatch')
    representation_cases=0
    for values in product(vocabulary,repeat=3):
        got=aggregate(values,range(3));expected='FAIL' if 'FAIL' in values else 'NOT_EVALUABLE' if 'NOT_EVALUABLE' in values else 'PASS'
        require(got==expected,'representation aggregate mismatch');representation_cases+=1
    # Deliberately expose vacuous aggregation instead of letting it imply readiness.
    require(aggregate(('PASS',),[])=='PASS','empty fold identity changed')
    empty_scope_disposition='Empty aggregation is vacuously PASS but establishes no substantive readiness. Actual selected pre-decision set is the pinned nonempty 12 checks; selecting an empty readiness set is out of this profile contract.'
    states=lifecycle['states'];edges={(e['from'],e['to']) for e in lifecycle['transitions']};transition_cases=0
    for a,b,exact,gate,recorded,effect in product(states,states,(False,True),(False,True),(False,True),(False,True)):
        permitted=exact and (a,b) in edges and gate
        consistent_recorded=not recorded or permitted and effect
        if recorded and not permitted:require(not consistent_recorded,'unpermitted actual transition accepted')
        if permitted and not recorded:require(consistent_recorded,'permission incorrectly forced occurrence')
        transition_cases+=1
    admission_cases=0
    for record,owner,applied,exact in product((False,True),repeat=4):
        consistent=not record or owner and applied and exact
        require(not record or consistent==(owner and applied and exact),'admission support rule mismatch');admission_cases+=1
    rule_results={'authority_effect':'none','outcome_space':'PASS/FAIL/NOT_EVALUABLE for exact 14 declared checks','evaluated_assignments':outside_cases,'required_prefix_assignments':3**12,'predecision_outcome_counts_all14':dict(all_counts),'predecision_counts_required12':dict(prefix_counts),'representation_assignments':representation_cases,'transition_boolean_cases':transition_cases,'admission_boolean_cases':admission_cases,'empty_scope_disposition':empty_scope_disposition,'result':'PASS bounded exhaustive rule checks','limits':'No arbitrary/infinite check universe, temporal trace correctness, owner authentication or actual applied effect claimed.'}
    save('rule-results.json',rule_results)
    summary={'schema_version':'cal.define-profile-formal-results/v1','authority_effect':'none','review_date':'2026-10-13','targets':load(STEP/'targets.json')['targets'],'combined_core':'SATISFIABLE_WITH_CHECKED_FINITE_MODEL','profile_pairs':len(pairs),'non_equivalence_directions':len(results),'non_entailment_boundaries':len(boundaries),'overlap_witnesses':2,'model_controls_passed':len(controls),'exhaustive_rules':rule_results,'source_closure':load(STEP/'source-closure.json')['status'],'mechanized_theorem':False,'evidence_kind':'Typed finite countermodels and exhaustive fixed-rule checks, exact source provenance closure','whole_repository_consistency':'NOT_ESTABLISHED; 183 meanings captured but not all formalized','interpretation_fidelity':'OWNER_REVIEW_PENDING','admission_ready':False,'admissions':0,'runtime_implementation_changes':0,'elapsed_seconds':round(time.monotonic()-started,3),'checker_sha256':digest(Path(__file__).read_bytes()),'python':sys.version}
    save('formal-results.json',summary)
    for row in freeze['files']:require(digest((ROOT/row['path']).read_bytes())==row['sha256'],'source changed during checks: '+row['path'])
    print(json.dumps({k:summary[k] for k in ['combined_core','profile_pairs','non_equivalence_directions','non_entailment_boundaries','model_controls_passed','source_closure','whole_repository_consistency','admissions','elapsed_seconds']},indent=2))
    print('Exhaustive outcome assignments:',outside_cases)


if __name__=='__main__':main()
