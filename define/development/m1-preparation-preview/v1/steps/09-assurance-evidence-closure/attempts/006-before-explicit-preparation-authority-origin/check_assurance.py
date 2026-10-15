#!/usr/bin/env python3
"""Execute typed finite witnesses and bounded semantic-contract cases.

Reuses native IR formula typing and the independently implemented Denotation.
It does not invoke the full provider, authenticate owners or apply authority.
"""
from pathlib import Path
from itertools import product,combinations
from collections import Counter
import copy
import hashlib
import json
import sys
import time

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
sys.path.insert(0,str(ROOT/'craft/formalization/candidates/definition-assurance-v1'))
import ir
import verifier

def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,d):
    with (STEP/name).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def require(v,message):
    if not v:raise ValueError(message)

def main():
    started=time.monotonic()
    freeze=load(STEP/'source-selection.json')
    for f in freeze['files']:require(sha(ROOT/f['path'])==f['sha256'],'changed selected input '+f['path'])
    selected=load(STEP/'interpretations.json');frames=selected['frames'];roles=list(frames)
    entities=roles+['input','subject','gate']
    concepts=['concept_incident','concept_work','concept_completeness','concept_exclusivity','undeclared_concept']
    tags=['reuse','specialize','propose','open']
    complete_fields=['StableSemanticIdentity','Scoped','FormalVoice','NonNormativePlainVoice','NonNormativeDomainVoice','BoundariesDeclared','AdmittedSourceStanding','RegistryPostimageResolved','GeneratedIndexResolved','CurrentDriftRoute']
    unary=sorted(set(sum(frames.values(),[])+complete_fields+['PrimaryConsumersDeclared','OwnerAdmissionSelected','AdmissionApplied','ExactAdmissionBindings','CanonicalAuthority','TransitionRecorded','EffectConfirmed','ExactTransitionBinding','DeclaredDirectedPair','GatePass','MayExecute','ConsumerReady','GoalAchieved','SuccessfulOutcomeEvidence','GoalOwnerTransition','ConformingDefinitionComplete','DefineProductInstance','HandlingTag']))
    unary+=roles
    relations={'RequiredConcept':2,'Disposition':3,'PayloadMatches':3,'LineagePreserved':2,'DeclaredConceptCoverage':2,'CapturedSourceGaps':2,'ConsumerReviewable':2,'ConformingDefineResult':2}
    declarations=[{'symbol_id':s,'kind':'sort','domain_policy':'nonempty'} for s in ['Entity','Concept','Handling']]
    declarations+=[{'symbol_id':'entity_'+e,'kind':'constant','result_sort':'Entity'} for e in entities]
    declarations+=[{'symbol_id':e,'kind':'constant','result_sort':'Concept'} for e in concepts]
    declarations+=[{'symbol_id':e,'kind':'constant','result_sort':'Handling'} for e in tags]
    declarations+=[{'symbol_id':p,'kind':'predicate','argument_sorts':['Handling'] if p=='HandlingTag' else ['Entity']} for p in unary]
    relation_sorts={'RequiredConcept':['Entity','Concept'],'Disposition':['Entity','Concept','Handling'],'PayloadMatches':['Entity','Concept','Handling']}
    declarations+=[{'symbol_id':p,'kind':'predicate','argument_sorts':relation_sorts.get(p,['Entity']*n)} for p,n in relations.items()]
    symbols={d['symbol_id']:d for d in declarations if d['kind']!='sort'}
    def var(x='x'):return {'op':'var','name':x}
    def const(x):return {'op':'const','name':'entity_'+x if x in entities else x}
    def pred(p,*args):return {'op':'pred','name':p,'args':list(args) or [var()]}
    def allof(*args):return {'op':'and','args':list(args)}
    def anyof(*args):return {'op':'or','args':list(args)}
    def not_(arg):return {'op':'not','arg':arg}
    def binary(op,a,b):return {'op':op,'left':a,'right':b}
    def eq(a,b):return binary('eq',a,b)
    def quant(op,name,body,sort='Entity'):return {'op':op,'var':name,'sort':sort,'body':body}
    def typed(f):return ir.formula(f,{s:s for s in ['Entity','Concept','Handling']},symbols)
    x,c,d,t=map(var,['x','c','d','t'])
    tag_rule=quant('forall','x',binary('iff',pred('HandlingTag',x),anyof(*(eq(x,const(a)) for a in tags))),'Handling')
    nonempty=quant('exists','c',pred('RequiredConcept',x,c),'Concept')
    exactly_one=quant('forall','c',binary('implies',pred('RequiredConcept',x,c),quant('exists','d',allof(pred('HandlingTag',d),pred('Disposition',x,c,d),quant('forall','t',binary('implies',pred('Disposition',x,c,t),eq(t,d)),'Handling')),'Handling')),'Concept')
    matching=quant('forall','c',quant('forall','d',binary('implies',pred('Disposition',x,c,d),pred('PayloadMatches',x,c,d)),'Handling'),'Concept')
    no_undeclared=quant('forall','c',quant('forall','d',binary('implies',pred('Disposition',x,c,d),allof(pred('RequiredConcept',x,c),pred('HandlingTag',d))),'Handling'),'Concept')
    payload_domain=allof(quant('forall','c',binary('iff',quant('exists','d',pred('PayloadMatches',x,c,d),'Handling'),pred('RequiredConcept',x,c)),'Concept'),quant('forall','c',quant('forall','d',binary('implies',pred('PayloadMatches',x,c,d),pred('Disposition',x,c,d)),'Handling'),'Concept'))
    derived={'ConceptSetNonempty':nonempty,'EveryConceptSingleDisposition':exactly_one,'EveryDispositionPayloadMatches':matching,'PayloadDomainExactlyConcepts':payload_domain,'NoUndeclaredConceptHandling':no_undeclared}
    theory=[typed(quant('forall','x',binary('iff',pred(role),allof(*(pred(p) for p in fields))))) for role,fields in frames.items()]
    theory += [typed(tag_rule)]+[typed(not_(eq(const(a),const(b)))) for a,b in combinations(['reuse','specialize','propose','open'],2)]
    theory += [typed(quant('forall','x',binary('iff',pred(feature),body))) for feature,body in derived.items()]
    # Preserve the canonical completeness expression, with separate normative
    # consumer/owner obligations. No source selector is silently changed.
    complete_formula=allof(*(pred(p) for p in complete_fields))
    theory += [typed(quant('forall','x',binary('iff',pred('ConformingDefinitionComplete'),complete_formula))),
        typed(quant('forall','x',binary('implies',pred('ConformingDefinitionComplete'),allof(pred('Definition'),pred('PrimaryConsumersDeclared'))))),
        typed(quant('forall','x',binary('implies',pred('CanonicalAuthority'),allof(pred('OwnerAdmissionSelected'),pred('AdmissionApplied'),pred('ExactAdmissionBindings'))))),
        typed(quant('forall','x',binary('implies',pred('TransitionRecorded'),allof(pred('ExactTransitionBinding'),pred('DeclaredDirectedPair'),pred('GatePass'),pred('EffectConfirmed'))))),
        typed(quant('forall','x',binary('implies',pred('GoalAchieved'),allof(pred('SuccessfulOutcomeEvidence'),pred('GoalOwnerTransition'))))),
        typed(quant('forall','x',binary('iff',pred('DefineProductInstance'),allof(pred('Define'),pred('ProductCapability')))))]
    result_body=allof(pred('Pack',d),pred('LineagePreserved',x,d),pred('DeclaredConceptCoverage',x,d),pred('CapturedSourceGaps',x,d),pred('ConsumerReviewable',x,d))
    theory += [typed(quant('forall','x',quant('forall','d',binary('iff',pred('ConformingDefineResult',x,d),result_body))))]
    model={'domains':{'Entity':entities,'Concept':concepts,'Handling':tags},'constants':{**{'entity_'+e:e for e in entities},**{e:e for e in concepts+tags}},'functions':{},'predicates':{p:[] for p in unary+list(relations)}}
    def add(m,p,*values):
        values=list(values)
        if values not in m['predicates'][p]:m['predicates'][p].append(values)
    for role,fields in frames.items():
        for p in fields:
            if p not in derived:add(model,p,role)
    for tag in ['reuse','specialize','propose','open']:add(model,'HandlingTag',tag)
    for concept,tag in zip(concepts[:4],tags):
        add(model,'RequiredConcept','Pack',concept);add(model,'Disposition','Pack',concept,tag);add(model,'PayloadMatches','Pack',concept,tag)
    for p in complete_fields+['PrimaryConsumersDeclared']:add(model,p,'Definition')
    for p in ['LineagePreserved','DeclaredConceptCoverage','CapturedSourceGaps','ConsumerReviewable']:add(model,p,'input','Pack')
    for p in ['ExactTransitionBinding','DeclaredDirectedPair','GatePass']:add(model,p,'gate')
    def refresh(m,selected_frames=frames):
        # Relational features are evaluated independently in ordinary Python;
        # typed formulas then check the resulting model using native Denotation.
        for p in derived:m['predicates'][p]=[]
        for e in entities:
            cs=[row[1] for row in m['predicates']['RequiredConcept'] if row[0]==e]
            ds=[row for row in m['predicates']['Disposition'] if row[0]==e]
            ps=[row for row in m['predicates']['PayloadMatches'] if row[0]==e]
            if cs:add(m,'ConceptSetNonempty',e)
            if all(len([row for row in ds if row[1]==c])==1 and [next(row[2] for row in ds if row[1]==c)] in m['predicates']['HandlingTag'] for c in cs):add(m,'EveryConceptSingleDisposition',e)
            if all(row in m['predicates']['PayloadMatches'] for row in ds):add(m,'EveryDispositionPayloadMatches',e)
            if set(row[1] for row in ps)==set(cs) and all(row in ds for row in ps):add(m,'PayloadDomainExactlyConcepts',e)
            if all(row[1] in cs and [row[2]] in m['predicates']['HandlingTag'] for row in ds):add(m,'NoUndeclaredConceptHandling',e)
        for role,fields in selected_frames.items():m['predicates'][role]=[[e] for e in entities if all([e] in m['predicates'][p] for p in fields)]
        m['predicates']['ConformingDefinitionComplete']=[[e] for e in entities if all([e] in m['predicates'][p] for p in complete_fields)]
        m['predicates']['DefineProductInstance']=[[e] for e in entities if [e] in m['predicates']['Define'] and [e] in m['predicates']['ProductCapability']]
        m['predicates']['ConformingDefineResult']=[]
        for a in entities:
            for b in entities:
                if [b] in m['predicates']['Pack'] and all([a,b] in m['predicates'][p] for p in ['LineagePreserved','DeclaredConceptCoverage','CapturedSourceGaps','ConsumerReviewable']):add(m,'ConformingDefineResult',a,b)
        return m
    def verify(m,selected_theory=theory):
        den=verifier.Denotation(declarations,m)
        return all(den.truth(f) for f in selected_theory),den
    refresh(model);ok,den=verify(model);require(ok,'joint core model does not satisfy interpreted theory')
    save('formal-core.json',{'schema_version':'cal.define-assurance-interpreted-core/v1','authority_effect':'none','declarations':declarations,'axioms':theory,'frames':frames,
        'relational_pack_features':derived,'conditional_result_rule':result_body,'source_clause_map':'clause-correspondence.json',
        'assumptions':selected['assumptions'],'limits':selected['limits'],'owner_fidelity':'Fresh interpretation pending final review'})
    pair_results=[]
    for a,b in selected['comparison_pairs']:
        equivalent=typed(quant('forall','x',binary('iff',pred(a),pred(b))))
        require(not den.truth(equivalent),'unexpected equivalence '+a+'/'+b)
        for left,right in [(a,b),(b,a)]:
            query=typed(quant('exists','x',allof(pred(left),not_(pred(right)))))
            require(den.truth(query),'no directed witness '+left+'/'+right)
            witness=next(e for e in entities if [e] in model['predicates'][left] and [e] not in model['predicates'][right])
            pair_results.append({'left':left,'right':right,'query':query,'witness':witness,'result':'FINITE_COUNTERMODEL_CHECKED','equivalence_truth':False,
                'claim':'Interpreted theory does not force equivalence; not proof of full-source disjointness'})
    witnesses=[{'name':'joint interpreted scope','model':model,'theory_satisfied':True}]
    overlap_specs=[('Pack','GovernedModel'),('Define','ProductCapability'),('EvaluationProfile','Policy'),('LifecycleProfile','Policy')]
    overlaps=[]
    for a,b in overlap_specs:
        m=copy.deepcopy(model)
        for p in frames[b]:add(m,p,a)
        refresh(m);ok,dn=verify(m);require(ok and dn.truth(typed(allof(pred(a,const(a)),pred(b,const(a))))),'overlap rejected '+a+'/'+b)
        witnesses.append({'name':a+' overlap '+b,'model':m,'theory_satisfied':True})
        overlaps.append({'left':a,'right':b,'result':'OVERLAP_MODEL_CHECKED'})
    no_execution=copy.deepcopy(model);no_execution['predicates']['ExecutionOccurred']=[];refresh(no_execution);ok,nd=verify(no_execution);require(ok,'no-execution world invalid')
    witnesses.append({'name':'declared contracts and conforming saved result without runtime execution','model':no_execution,'theory_satisfied':True})
    boundaries=[]
    for role in ['Pack','Define','Definition','EvaluationProfile','LifecycleProfile']:
        for flag in ['MayExecute','ConsumerReady','OwnerAdmissionSelected','AdmissionApplied','CanonicalAuthority','GoalAchieved']:
            query=typed(binary('implies',pred(role,const(role)),pred(flag,const('subject'))))
            require(not den.truth(query),'unexpected effect inference '+role+'/'+flag)
            boundaries.append({'premise':role,'consequent':flag,'query':query,'result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','model':'joint interpreted scope'})
        query=typed(binary('implies',pred(role,const(role)),quant('exists','x',pred('ExecutionOccurred'))))
        require(not nd.truth(query),'declaration implies runtime execution')
        boundaries.append({'premise':role,'consequent':'exists runtime execution','query':query,'result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','model':'no-execution world'})
    for name,premise,consequent in [
        ('Definition completeness is not admission',pred('ConformingDefinitionComplete',const('Definition')),pred('CanonicalAuthority',const('Definition'))),
        ('Conforming result is not Goal achievement',pred('ConformingDefineResult',const('input'),const('Pack')),pred('GoalAchieved',const('subject'))),
        ('Gate satisfaction is not transition recording',allof(*(pred(p,const('gate')) for p in ['ExactTransitionBinding','DeclaredDirectedPair','GatePass'])),pred('TransitionRecorded',const('gate')))]:
        query=typed(binary('implies',premise,consequent));require(not den.truth(query),name)
        boundaries.append({'premise':name,'query':query,'result':'NON_ENTAILMENT_COUNTERMODEL_CHECKED','model':'joint interpreted scope'})
    controls=[]
    def control(name,mutate,expected=False):
        m=copy.deepcopy(model);mutate(m)
        try:observed,_=verify(m);error=None
        except verifier.VerificationFault as e:observed=False;error=e.code
        require(observed==expected,'wrong rejection control '+name)
        controls.append({'case':name,'expected_theory_satisfied':expected,'observed_theory_satisfied':observed,'error':error,'result':'PASS'})
    control('missing declared concept handling',lambda m:m['predicates']['Disposition'].pop())
    control('duplicate different handling for one concept',lambda m:add(m,'Disposition','Pack','concept_incident','open'))
    control('undeclared concept disposition',lambda m:add(m,'Disposition','Pack','undeclared_concept','reuse'))
    control('unmatched disposition payload',lambda m:m['predicates']['PayloadMatches'].pop())
    control('extra undeclared payload key',lambda m:add(m,'PayloadMatches','Pack','undeclared_concept','open'))
    control('extra non-selected disposition payload',lambda m:add(m,'PayloadMatches','Pack','concept_incident','open'))
    control('missing validation scope on asserted Pack',lambda m:m['predicates']['ValidationScopeDeclared'].remove(['Pack']))
    control('false conforming result without lineage',lambda m:m['predicates']['LineagePreserved'].remove(['input','Pack']))
    control('missing consumer on asserted complete Definition',lambda m:m['predicates']['PrimaryConsumersDeclared'].remove(['Definition']))
    control('admitted authority without owner or application',lambda m:add(m,'CanonicalAuthority','subject'))
    control('transition without confirmed effect',lambda m:add(m,'TransitionRecorded','gate'))
    control('Goal achieved without evidence/owner transition',lambda m:add(m,'GoalAchieved','subject'))
    control('empty Entity population',lambda m:m['domains'].update(Entity=[]))
    control('missing model signature predicate',lambda m:m['predicates'].pop('OwnerQualified'))
    control('foreign relation endpoint',lambda m:add(m,'RequiredConcept','Pack','foreign'))
    # Different labels with identical encoded requirements must collapse.
    alias_frames=copy.deepcopy(frames);alias_frames['Define']=frames['Pack']
    alias_model=refresh(copy.deepcopy(model),alias_frames);alias_theory=copy.deepcopy(theory)
    alias_theory[roles.index('Define')]=typed(quant('forall','x',binary('iff',pred('Define'),allof(*(pred(p) for p in frames['Pack'])))))
    ok,dn=verify(alias_model,alias_theory);require(ok and dn.truth(typed(quant('forall','x',binary('iff',pred('Define'),pred('Pack'))))),'label-only collapse control failed')
    controls.append({'case':'identical requirements under different role labels','result':'PASS','observed':'equivalence detected; no non-collapse claimed'})
    # Specialization is not forced to alter meaning: application route remains
    # separate from a complete proposed semantic-change route.
    case_results=[]
    masks=range(16);payload_cases=0;valid_payload_cases=0
    for disposition_masks in product(masks,repeat=4):
        single=all(mask in [1,2,4,8] for mask in disposition_masks)
        for payload_bits in range(16):
            predicate=single and payload_bits==15
            independently_counted=all(mask.bit_count()==1 for mask in disposition_masks) and all((payload_bits>>i)&1 for i in range(4))
            require(predicate==independently_counted,'handling/payload rule mismatch')
            payload_cases+=1;valid_payload_cases+=int(predicate)
    require(payload_cases==16**4*16 and valid_payload_cases==4**4,'bounded disposition denominator wrong')
    case_results.append({'case_population':'four required concepts; every subset of four handling tags and payload-presence bits','cases':payload_cases,'conforming_assignments':valid_payload_cases,'result':'PASS','limit':'Not exhaustive over arbitrary concept universes or arbitrary payload meanings'})
    reference_cases=0;reference_valid=0
    for refs in product(range(4),repeat=4):
        # 0 unresolved/no gap, 1 exact resolved, 2 declared gap, 3 both.
        good=all(value!=0 for value in refs)
        require(good==all((v&1) or (v&2) for v in refs),'reference/gap rule mismatch')
        reference_cases+=1;reference_valid+=int(good)
    case_results.append({'case_population':'four references, resolved/gap bit combinations','cases':reference_cases,'conforming_assignments':reference_valid,'result':'PASS'})
    posture_cases=0
    for tag,posture,gap in product(tags,['admitted','candidate','unknown'],(False,True)):
        acceptable=(tag not in ['reuse','specialize'] or posture=='admitted') and (posture!='unknown' or gap)
        if tag in ['reuse','specialize'] and posture=='candidate':require(not acceptable,'candidate meaning counted as admitted parent/reuse')
        posture_cases+=1
    case_results.append({'case_population':'four handling dispositions with admitted/candidate/unknown source posture and visible-gap bit','cases':posture_cases,'result':'PASS','limit':'Recorded reference posture is distinct from truth, action authority and actual human identity'})
    specialize_cases=0
    for mode,changed,parent,application,proposal in product(['application','semantic-change','unknown'],(False,True),(False,True),(False,True),(False,True)):
        valid=(mode=='application' and not changed and parent and application) or (mode=='semantic-change' and changed and parent and proposal)
        if mode=='application' and changed:require(not valid,'semantic change smuggled through application route')
        if mode=='semantic-change' and not proposal:require(not valid,'missing complete proposal accepted')
        specialize_cases+=1
    case_results.append({'case_population':'specialization mode, meaning-change, parent, application and complete proposed representation','cases':specialize_cases,'result':'PASS','limit':'Proposal completeness here is declared representation evidence, not DefinitionComplete/admission'})
    result_cases=0
    for flags in product((False,True),repeat=6):
        pack,lineage,concepts,standing,reviewable,interrupted=flags
        # An interrupted attempt can retain an earlier saved Pack; it does not
        # by itself establish a conforming result for this attempt.
        conforming=pack and lineage and concepts and standing and reviewable
        if not pack:require(not conforming,'attempt with no Pack reported conforming')
        result_cases+=1
    case_results.append({'case_population':'pack/lineage/coverage/source-gaps/reviewability plus independent interruption flag','cases':result_cases,'result':'PASS','limit':'No actual attempt/provider execution or transport success inferred'})
    foundation_cases=0;v1_equivalent=0
    for carrier in ['v1','v2','other']:
        for schema_ok,gen_ok,standing,compatible,source_ok in product((False,True),repeat=5):
            proposed=(carrier in ['v1','v2']) and schema_ok and gen_ok and standing and compatible and source_ok
            legacy=(carrier=='v1') and schema_ok
            if carrier=='other':require(not proposed,'arbitrary schema shortcut accepted')
            if carrier=='v1' and gen_ok and standing and compatible and source_ok:
                require(proposed==legacy,'v1 compatibility counterexample');v1_equivalent+=1
            if carrier=='v2' and not standing:require(not proposed,'unadopted v2 profile treated ready')
            foundation_cases+=1
    case_results.append({'case_population':'declared v1/v2/unsupported carrier and exact schema/generator/profile-standing/compatibility/source booleans','cases':foundation_cases,'legacy_v1_equivalence_slice':v1_equivalent,'result':'PASS','limit':'Legacy equivalence is conditional on matching applicable bindings and prerequisites, not a global behavioral theorem'})
    require(time.monotonic()-started<60,'assurance execution exceeded selected 60 second bound')
    save('witnesses.json',{'authority_effect':'none','finite_models':witnesses,'pairs':pair_results,'overlaps':overlaps,'boundaries':boundaries})
    save('controls.json',{'authority_effect':'none','controls':controls})
    save('bounded-cases.json',{'authority_effect':'none','case_populations':case_results,'complete_accounting':True})
    summary={'schema_version':'cal.define-closure-assurance-results/v1','authority_effect':'none','review_date':'2026-10-14',
        'joint_core':'SATISFIABLE_WITH_CHECKED_FINITE_MODEL','comparison_pairs':len(selected['comparison_pairs']),'directed_non_equivalence_witnesses':len(pair_results),
        'non_entailment_boundaries':len(boundaries),'overlap_witnesses':len(overlaps),'controls_passed':len(controls),'case_populations':case_results,
        'conditional_foundation_compatibility':'PASS bounded exact-binding slices; current historical source premises are separately preserved',
        'mechanized_theorem':False,'whole_repository_consistency':'NOT_ESTABLISHED','fresh_interpretation_fidelity':'FINAL_OWNER_REVIEW_PENDING',
        'admission_ready':False,'admissions':0,'runtime_implementation_changes':0,'elapsed_seconds':round(time.monotonic()-started,3),
        'checker_sha256':sha(Path(__file__)),'python':sys.version,'limits':selected['limits']}
    save('assurance-results.json',summary)
    for f in freeze['files']:require(sha(ROOT/f['path'])==f['sha256'],'input changed during assurance '+f['path'])
    print(json.dumps({k:summary[k] for k in ['joint_core','comparison_pairs','directed_non_equivalence_witnesses','non_entailment_boundaries','controls_passed','elapsed_seconds','admissions']}))

if __name__=='__main__':main()
