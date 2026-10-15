"""Planned finite controls for a normalized research aggregate;actual outcomes remain independent."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 aggregates=['questionAggregate','claimAggregate','outsideAggregate'];contexts=['contextQuestion','contextClaim','contextOutside'];topics=['topicQuestion','topicClaim','topicOutside'];questions=['question','otherQuestion','outsideQuestion'];claims=['claim','otherClaim','outsideClaim'];scope=['scope','outsideScope'];projects=['project','outsideProject'];goals=['goalOne','goalTwo','outsideGoal'];sources=['sourceQuestion','sourceClaim','sourceOutside'];observations=['obsQuestion','obsClaim','obsOutside'];methods=['method','outsideMethod'];items=['supportQuestion','counterQuestion','supportClaim','counterClaim','itemOutside'];limits=['limitQuestion','limitClaim','limitOutside'];findings=['findingQuestion','findingClaim','findingOutside'];routes=['ownerRoute','challengeRoute','outsideRoute'];times=['created','updated','outsideTime'];tokens=['empty','semantic.evidence-set','definition','type.definition','scope.knowledge-development','CAV2-D61','reference','same-label']
 domains={'Aggregate':aggregates,'DefinitionContext':contexts,'Topic':topics,'Question':questions,'Claim':claims,'Scope':scope,'Project':projects,'Goal':goals,'SourceMaterial':sources,'Observation':observations,'Method':methods,'EvidenceItem':items,'Limitation':limits,'FreshnessCondition':['freshness','outsideFreshness'],'ApplicabilityCondition':['applicability','outsideApplicability'],'Finding':findings,'SiblingTarget':['siblingFinding','siblingInquiry','siblingRun'],'Route':routes,'Time':times,'Token':tokens}
 def suffix(a):return 'Question' if a=='questionAggregate' else 'Claim' if a=='claimAggregate' else 'Outside'
 def outside(x):return x=='outsideAggregate' or x.endswith('Outside')
 def selected(x,a,z):return z if outside(x) else a
 maps={'aggregateDefinitionContext':lambda a:'context'+suffix(a),'contextConcept':lambda c:'semantic.evidence-set','contextKind':lambda c:'definition','contextCarrier':lambda c:'type.definition','contextOwnerScope':lambda c:'scope.knowledge-development','contextLineage':lambda c:'CAV2-D61','aggregateTopic':lambda a:'topic'+suffix(a),'topicQuestion':lambda t:'question' if t=='topicQuestion' else 'otherQuestion' if t=='topicClaim' else 'outsideQuestion','topicClaim':lambda t:'claim' if t=='topicClaim' else 'otherClaim' if t=='topicQuestion' else 'outsideClaim','aggregateScope':lambda a:selected(a,'scope','outsideScope'),'aggregateProject':lambda a:selected(a,'project','outsideProject'),'aggregateMethod':lambda a:selected(a,'method','outsideMethod'),'aggregateFreshness':lambda a:selected(a,'freshness','outsideFreshness'),'aggregateApplicability':lambda a:selected(a,'applicability','outsideApplicability'),'aggregateCreated':lambda a:selected(a,'created','outsideTime'),'aggregateUpdated':lambda a:selected(a,'updated','outsideTime'),'aggregateOwnerRoute':lambda a:selected(a,'ownerRoute','outsideRoute'),'aggregateChallengeRoute':lambda a:selected(a,'challengeRoute','outsideRoute'),'evidenceTopic':lambda e:'topicQuestion' if e.endswith('Question') else 'topicClaim' if e.endswith('Claim') else 'topicOutside','evidenceScope':lambda e:selected(e,'scope','outsideScope'),'findingTopic':lambda f:'topic'+f.removeprefix('finding')}
 for n in b.FUNCTIONS:
  if n not in maps:maps[n]=lambda value:'same-label' if value in ['questionAggregate','claimAggregate','question','claim'] else 'reference'
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};active=aggregates[:-1]
 for n in ['EvidenceSet','AggregateRecordDeclared','BoundedInvestigationDeclared','AttributableDeclared','EphemeralRecordDeclared','SupportingCollectionDeclared','CounterevidenceCollectionDeclared','SourceCollectionDeclared','ObservationCollectionDeclared','LimitationCollectionDeclared','FindingReferencesDeclared']:predicates[n]=[[a] for a in active]
 predicates.update(DefinitionContextDeclared=[[c] for c in contexts[:-1]],AcceptedSourceRelationDeclared=[[c] for c in contexts[:-1]],TopicDeclared=[[t] for t in topics[:-1]],QuestionTopicDeclared=[['topicQuestion']],ClaimTopicDeclared=[['topicClaim']],QuestionDeclared=[['question']],ClaimDeclared=[['claim']],ScopeDeclared=[['scope']],ProjectDeclared=[['project']],GoalDeclared=[['goalOne'],['goalTwo']],SourceDeclared=[[s] for s in sources[:-1]],ObservationDeclared=[[o] for o in observations[:-1]],MethodDeclared=[['method']],EvidenceItemDeclared=[[e] for e in items[:-1]],LimitationDeclared=[[l] for l in limits[:-1]],FreshnessConditionDeclared=[['freshness']],ApplicabilityConditionDeclared=[['applicability']],FindingDeclared=[[f] for f in findings[:-1]],RouteDeclared=[[r] for r in routes[:-1]],TimeDeclared=[[t] for t in times[:-1]],GoalLinked=[['questionAggregate','goalOne'],['questionAggregate','goalTwo'],['claimAggregate','goalOne']],SourceIncluded=[[a,'source'+suffix(a)] for a in active],ObservationIncluded=[[a,'obs'+suffix(a)] for a in active],SupportingEvidenceIncluded=[[a,'support'+suffix(a)] for a in active],CounterevidenceIncluded=[[a,'counter'+suffix(a)] for a in active],LimitationIncluded=[[a,'limit'+suffix(a)] for a in active],FindingReferenced=[[a,'finding'+suffix(a)] for a in active],FindingDerivesFrom=[['finding'+suffix(a),a] for a in active],PromotionDeclared=[['questionAggregate']],SiblingMeaningAssignmentDeclared=[['questionAggregate','siblingFinding']],ExplicitSiblingReferenceDeclared=[['questionAggregate','siblingFinding']])
 return {'domains':domains,'constants':{'EMPTY':'empty','SEMANTIC_EVIDENCE_SET':'semantic.evidence-set','DEFINITION_KIND':'definition','TYPE_DEFINITION':'type.definition','KNOWLEDGE_SCOPE':'scope.knowledge-development','CAV2_D61':'CAV2-D61'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('question-and-claim-normalized-research-aggregate-without-actual-outcomes',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['claimAggregate']),I=True)
 add('matching-printed-handles-do-not-collapse-record-topic-or-finding',lambda m:None,I=True)
 add('overlapping-support-and-counterevidence',lambda m:m['predicates']['CounterevidenceIncluded'].append(['questionAggregate','supportQuestion']),I=True)
 add('independent-reversed-created-updated-refs-no-ordering-proof',lambda m:(setfn(m,'aggregateCreated','questionAggregate','updated'),setfn(m,'aggregateUpdated','questionAggregate','created')),I=True)
 def both_topic(m):m['predicates']['ClaimTopicDeclared'].append(['topicQuestion']);m['predicates']['ClaimDeclared'].append(['otherClaim'])
 add('question-and-claim-topic-labels-not-exclusive',both_topic,I=True)
 add('outside-normalization-context-not-governing',lambda m:setfn(m,'contextKind','contextOutside','reference'),I=True)
 for n in ['SourceIncluded','ObservationIncluded','SupportingEvidenceIncluded','CounterevidenceIncluded','LimitationIncluded','FindingReferenced']:
  add('one-aggregate-empty-optional-members-'+n,lambda m,n=n:m['predicates'].update({n:[x for x in m['predicates'][n] if x[0]!='claimAggregate']}),I=True)
 for n in ['AggregateRecordDeclared','BoundedInvestigationDeclared','AttributableDeclared','EphemeralRecordDeclared','SupportingCollectionDeclared','CounterevidenceCollectionDeclared','SourceCollectionDeclared','ObservationCollectionDeclared','LimitationCollectionDeclared','FindingReferencesDeclared']:add('missing-aggregate-'+n,lambda m,n=n:m['predicates'][n].remove(['questionAggregate']),T=False)
 for n,value in [('DefinitionContextDeclared','contextQuestion'),('AcceptedSourceRelationDeclared','contextQuestion'),('TopicDeclared','topicQuestion'),('QuestionDeclared','question'),('ClaimDeclared','claim'),('ScopeDeclared','scope'),('ProjectDeclared','project'),('MethodDeclared','method'),('FreshnessConditionDeclared','freshness'),('ApplicabilityConditionDeclared','applicability'),('TimeDeclared','created'),('TimeDeclared','updated'),('RouteDeclared','ownerRoute'),('RouteDeclared','challengeRoute')]:add('missing-selected-'+n+'-'+value,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 for n in ['contextConcept','contextKind','contextCarrier','contextOwnerScope','contextLineage']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'contextQuestion','reference'),T=False)
 for n,arg in [('aggregateHandle','questionAggregate'),('contextHandle','contextQuestion'),('topicHandle','topicQuestion'),('questionHandle','question'),('claimHandle','claim'),('scopeHandle','scope'),('projectHandle','project'),('methodHandle','method'),('freshnessHandle','freshness'),('applicabilityHandle','applicability'),('timeHandle','created'),('timeHandle','updated'),('routeHandle','ownerRoute'),('routeHandle','challengeRoute')]:add('empty-selected-handle-'+n+'-'+arg,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('topic-with-neither-question-nor-claim-kind',lambda m:m['predicates']['QuestionTopicDeclared'].remove(['topicQuestion']),T=False)
 add('no-Goal-links',lambda m:m['predicates'].update(GoalLinked=[x for x in m['predicates']['GoalLinked'] if x[0]!='questionAggregate']),T=False)
 add('linked-Goal-not-declared',lambda m:m['predicates']['GoalDeclared'].remove(['goalOne']),T=False)
 add('linked-Goal-handle-empty',lambda m:setfn(m,'goalHandle','goalOne','empty'),T=False)
 for decl,arg in [('SourceDeclared','sourceQuestion'),('ObservationDeclared','obsQuestion'),('EvidenceItemDeclared','supportQuestion'),('LimitationDeclared','limitQuestion'),('FindingDeclared','findingQuestion')]:add('included-member-without-'+decl,lambda m,decl=decl,arg=arg:m['predicates'][decl].remove([arg]),T=False)
 for n,arg in [('sourceHandle','sourceQuestion'),('sourceProvenanceRef','sourceQuestion'),('observationHandle','obsQuestion'),('observationOriginRef','obsQuestion'),('evidenceHandle','supportQuestion'),('evidenceProvenanceRef','supportQuestion'),('limitationHandle','limitQuestion'),('findingHandle','findingQuestion')]:add('empty-member-handle-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,value in [('evidenceTopic','topicClaim'),('evidenceScope','outsideScope')]:
  for e in ['supportQuestion','counterQuestion']:add('wrong-'+n+'-'+e,lambda m,n=n,value=value,e=e:setfn(m,n,e,value),T=False)
 add('finding-wrong-question-topic',lambda m:setfn(m,'findingTopic','findingQuestion','topicClaim'),T=False)
 add('finding-not-declared-derived-from-aggregate',lambda m:m['predicates']['FindingDerivesFrom'].remove(['findingQuestion','questionAggregate']),T=False)
 add('sibling-meaning-assignment-without-explicit-ref',lambda m:m['predicates'].update(ExplicitSiblingReferenceDeclared=[]),T=False)
 add('explicit-sibling-ref-handle-empty',lambda m:setfn(m,'siblingHandle','siblingFinding','empty'),T=False)
 add('Research-outcome-field-present',lambda m:m['predicates']['OutcomeFieldPresent'].append(['questionAggregate']),T=False)
 for n in b.ROLES:add('collapsed-role-'+n,lambda m,n=n:m['predicates'][n].append(['questionAggregate']),T=False)
 add('no-plural-Goal-example-T-without-I',lambda m:m['predicates']['GoalLinked'].remove(['questionAggregate','goalTwo']),I=False)
 add('no-counterevidence-example-T-without-I',lambda m:m['predicates'].update(CounterevidenceIncluded=[]),I=False)
 add('no-Promotion-example-T-without-I',lambda m:m['predicates'].update(PromotionDeclared=[]),I=False)
 add('missing-total-context-function-entry',lambda m:m['functions']['aggregateDefinitionContext'].pop(),error='nontotal-function')
 add('ill-sorted-aggregate-topic-result',lambda m:setfn(m,'aggregateTopic','questionAggregate','scope'),error='ill-sorted-function-result')
 add('ill-sorted-semantic-identity-constant',lambda m:m['constants'].update(SEMANTIC_EVIDENCE_SET='questionAggregate'),error='ill-sorted-constant')
 add('wrong-finding-derivation-arity',lambda m:m['predicates'].update(FindingDerivesFrom=[['findingQuestion']]),error='ill-sorted-model-tuple')
 add('duplicate-source-membership-tuple',lambda m:m['predicates']['SourceIncluded'].append(['questionAggregate','sourceQuestion']),error='duplicate-predicate-tuple')
 add('empty-Question-domain',lambda m:m['domains'].update(Question=[]),error='empty-or-malformed-domain')
 add('duplicate-project-function-tuple',lambda m:m['functions']['aggregateProject'].append(copy.deepcopy(m['functions']['aggregateProject'][0])),error='duplicate-function-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py',b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py']]
    core=load('t.json')['payload'];typed=load('static-ir.json');packet=load('correspondence.json');counts=load('denominator.json')
    if not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted interpretation/IR')
    account=b.co.check(packet,snap,required_dependencies=[x['version_ref'] for x in core['depends_on']],required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not account['character_accounting_complete'] or not b.r.same_json(account,load('correspondence-check.json')):raise ValueError('Incomplete source account')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or owner fidelity')
    T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
    if len(T)!=counts['encoded_clauses'] or len(I)!=counts['required_populations']:raise ValueError('Changed theory/population denominator')
    ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
    def evaluate(model):
        e=v.Denotation(typed['declarations'],model)
        tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T]
        pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in tc),all(x['truth'] for x in pc),tc,pc
    results=[]
    for case in controls():
        model=qualify(case['model'],ids)
        try:
            t,i,tc,pc=evaluate(model)
            if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
            result={'case_id':case['case_id'],'status':'independently-evaluated-authored-model','model':model,'model_sha256':b.ir.digest(model),
                    'primary_theory_satisfied':t,'required_population_satisfied':i,'primary_clause_results':tc,'population_results':pc}
        except v.VerificationFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-model-structure','code':error.code,'model':model,'model_sha256':b.ir.digest(model)}
        results.append(result)
    queries=[];composed=b.ir.compose([typed])
    for q in load('query-policy.json')['queries']:
        model=base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.evidence/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-EvidenceSet-model-controls/v1-candidate','status':'PASS-for-exact-authored-EvidenceSet-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Declared normalized bounded research aggregates with separate question-or-claim,source,observation,Goal/Project,method,counterevidence,limitations,freshness/applicability,Finding refs,time/routes and sibling guards checked on supplied models. Actual investigation,synthesis,truth,admission,authority,execution and accepted source/consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
