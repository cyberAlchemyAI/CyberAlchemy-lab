"""Supplied typed Provenance trails,gaps,ordering and independent actual outcomes."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS}
 domains.update(Meaning=['m0','mOutside'],ProvenanceRecord=['rFull','rPartial','rEmpty','rOutside'],Path=['pFull','pPartial','pEmpty','pOutside'],Step=['s'+str(i) for i in range(8)]+['t0','t1','sOutside'],Position=['pos'+str(i) for i in range(10)]+['posOutside'],RelationKind=[n.lower() for n in b.LABELS]+['customKind','kindOutside'],Handler=['handlerA','handlerBoth','handlerProcess','handlerOutside'],Posture=['postureA','postureDifferent','postureOutside'],MissingSegment=['g0','gOutside'],AuthorityUse=['u0','uOutside'],Token=['empty','reference','extra','semantic.provenance','definition','type.definition','scope.lineage','CAV2-D35'])
 constants={'EMPTY':'empty','MEANING_ID':'semantic.provenance','MEANING_KIND':'definition','MEANING_CARRIER':'type.definition','MEANING_SCOPE':'scope.lineage','SOURCE_D35':'CAV2-D35'};constants.update({n.upper():n.lower() for n in b.LABELS})
 active=domains['Step'][:-1];maps={}
 for n,k in zip(b.META,['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D35']):maps[n]=lambda m,k=k:constants[k] if m=='m0' else 'extra'
 maps.update(recordMeaning=lambda r:'mOutside' if r=='rOutside' else 'm0',recordObject=lambda r:'objectOutside' if r=='rOutside' else 'objectA',recordPath=lambda r:{'rFull':'pFull','rPartial':'pPartial','rEmpty':'pEmpty','rOutside':'pOutside'}[r],recordContext=lambda r:'contextOutside' if r=='rOutside' else 'contextA',stepPath=lambda s:'pOutside' if s=='sOutside' else 'pPartial' if s.startswith('t') else 'pFull',stepPosition=lambda s:'posOutside' if s=='sOutside' else 'pos'+str(active.index(s)),stepSource=lambda s:'sourceOutside' if s=='sOutside' else 'sourceA',stepRelation=lambda s:'kindOutside' if s=='sOutside' else b.LABELS[int(s[1:])].lower() if s.startswith('s') else 'derivation',stepOperation=lambda s:'operationOutside' if s=='sOutside' else 'operationA',stepHandler=lambda s:'handlerOutside' if s=='sOutside' else 'handlerBoth' if s=='s0' else 'handlerProcess' if s=='s1' else 'handlerA',stepPosture=lambda s:'postureOutside' if s=='sOutside' else 'postureDifferent' if s=='s1' else 'postureA',missingPath=lambda g:'pPartial' if g=='g0' else 'pOutside',missingResidue=lambda g:'residueA' if g=='g0' else 'residueOutside',missingOwnerRoute=lambda g:'ownerRouteA' if g=='g0' else 'ownerRouteOutside',useRecord=lambda u:'rFull' if u=='u0' else 'rOutside')
 # Default names derive from lowercasing the whole descriptive sort.
 maps['missingOwnerRoute']=lambda g:'ownerrouteA' if g=='g0' else 'ownerrouteOutside'
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys()
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['ProvenanceMeaning','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:predicates[n]=[['m0']]
 for n in ['ProvenanceRecordApplicable','RecordInScopeDeclared','OriginTransformationChainDeclared']:predicates[n]=[[r] for r in ['rFull','rPartial','rEmpty']]
 for n in ['PathApplicable','PathInScopeDeclared','TypedPathDeclared']:predicates[n]=[[p] for p in ['pFull','pPartial','pEmpty']]
 for n in ['StepApplicable','StepInScopeDeclared','PreciseSourceRelationDeclared']:predicates[n]=[[s] for s in active]
 for n in ['MissingSegmentApplicable','MissingSegmentInScopeDeclared']:predicates[n]=[['g0']]
 for n in ['AuthorityUseApplicable','AuthorityUseInScopeDeclared','TypedPrecisionForUseDeclared']:predicates[n]=[['u0']]
 predicates.update(ObjectDeclared=[['objectA']],ContextDeclared=[['contextA']],PositionDeclared=[[p] for p in domains['Position'][:-1]],SourceReferenceDeclared=[['sourceA']],RelationTypeDeclared=[[r] for r in domains['RelationKind'][:-1]],OperationDeclared=[['operationA']],OwnerDeclared=[['handlerA'],['handlerBoth']],ProcessDeclared=[['handlerBoth'],['handlerProcess']],PostureDeclared=[['postureA'],['postureDifferent']],ExplicitResidueDeclared=[['residueA']],OwnerRouteDeclared=[['ownerrouteA']],CompleteTrailDeclared=[['pFull']],IncompleteTrailDeclared=[['pPartial']])
 predicates['StepBeforeDeclared']=[[a,z] for i,a in enumerate(active) for z in active[i+1:] if maps['stepPath'](a)==maps['stepPath'](z)]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('complete-partial-empty-ordered-trails-and-owner-routed-gap',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-record-actual-'+n,lambda m,n=n:m['predicates']['RecordActual'+n].append(['rEmpty']),I=True)
 add('independently-authorized-use-is-allowed',lambda m:m['predicates']['UseActualAuthority'].append(['u0']),I=False)
 add('repeated-source-refs-do-not-break-path-order',lambda m:None,I=True)
 add('owner-and-process-labels-can-overlap',lambda m:None,I=True)
 add('empty-path-does-not-force-complete-or-incomplete-posture',lambda m:None,I=True)
 add('step-posture-can-differ-without-conferred-authority',lambda m:None,I=True)
 add('outside-record-empty-handle',lambda m:setfn(m,'provenanceRecordHandle','rOutside','empty'),I=True)
 add('outside-step-empty-source-handle',lambda m:setfn(m,'sourceHandle','sourceOutside','empty'),I=True)
 add('outside-gap-need-not-have-residue-route',lambda m:setfn(m,'ownerRouteHandle','ownerrouteOutside','empty'),I=True)
 add('unlisted-relation-kind-can-be-declared',lambda m:setfn(m,'stepRelation','s0','customKind'),I=False)
 add('cross-path-order-declarations-do-not-force-shared-order',lambda m:m['predicates']['StepBeforeDeclared'].append(['s0','t0']),I=True)
 def explicit_sibling(m):m['predicates']['SiblingMeaningAssignmentDeclared']=[['m0','extra']];m['predicates']['ExplicitSiblingReferenceDeclared']=[['m0','extra']]
 add('explicit-sibling-reference-preserves-separate-meaning',explicit_sibling,I=True)
 for n in ['ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in b.META:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'m0','extra'),T=False)
 for n in ['RecordInScopeDeclared','OriginTransformationChainDeclared']:add('missing-record-'+n,lambda m,n=n:m['predicates'][n].remove(['rFull']),T=False)
 add('record-declared-scope-without-membership',lambda m:m['predicates']['ProvenanceRecordApplicable'].remove(['rFull']),T=False)
 for n in ['ObjectDeclared','ContextDeclared']:add('missing-record-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('record-binds-outside-meaning',lambda m:setfn(m,'recordMeaning','rFull','mOutside'),T=False)
 add('record-binds-outside-path',lambda m:setfn(m,'recordPath','rFull','pOutside'),T=False)
 for n in ['PathInScopeDeclared','TypedPathDeclared']:add('missing-path-'+n,lambda m,n=n:m['predicates'][n].remove(['pFull']),T=False)
 for n in ['StepInScopeDeclared','PreciseSourceRelationDeclared']:add('missing-step-'+n,lambda m,n=n:m['predicates'][n].remove(['s0']),T=False)
 for n in ['PositionDeclared','SourceReferenceDeclared','RelationTypeDeclared','OperationDeclared','PostureDeclared']:add('missing-step-component-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 def unhandled(m):m['predicates']['OwnerDeclared'].remove(['handlerBoth']);m['predicates']['ProcessDeclared'].remove(['handlerBoth'])
 add('step-without-owner-or-process',unhandled,T=False)
 add('step-binds-outside-path',lambda m:setfn(m,'stepPath','s0','pOutside'),T=False)
 for sort,arg in [('Meaning','m0'),('ProvenanceRecord','rFull'),('Object','objectA'),('Path','pFull'),('Step','s0'),('Position','pos0'),('Source','sourceA'),('RelationKind','sourceevidence'),('Operation','operationA'),('Handler','handlerBoth'),('Posture','postureA'),('MissingSegment','g0'),('Residue','residueA'),('OwnerRoute','ownerrouteA'),('Context','contextA'),('AuthorityUse','u0')]:add('empty-selected-'+sort+'-handle',lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False)
 add('self-preceding-step',lambda m:m['predicates']['StepBeforeDeclared'].append(['s0','s0']),T=False)
 add('two-step-order-cycle',lambda m:m['predicates']['StepBeforeDeclared'].append(['s1','s0']),T=False)
 add('distinct-steps-share-position',lambda m:setfn(m,'stepPosition','s1','pos0'),T=False)
 add('uncomparable-distinct-steps',lambda m:m['predicates']['StepBeforeDeclared'].remove(['s0','s1']),T=False)
 def reversed_nontransitive(m):m['predicates']['StepBeforeDeclared'].remove(['s0','s2']);m['predicates']['StepBeforeDeclared'].append(['s2','s0'])
 add('pairwise-order-without-transitivity',reversed_nontransitive,T=False)
 for n in ['MissingSegmentInScopeDeclared','ExplicitResidueDeclared','OwnerRouteDeclared']:add('missing-gap-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('gap-binds-outside-path',lambda m:setfn(m,'missingPath','g0','pOutside'),T=False)
 def no_gap(m):m['predicates']['MissingSegmentApplicable']=[];m['predicates']['MissingSegmentInScopeDeclared']=[]
 add('incomplete-trail-without-explicit-gap',no_gap,T=False)
 add('complete-trail-with-selected-gap',lambda m:m['predicates']['CompleteTrailDeclared'].append(['pPartial']),T=False)
 for n in ['AuthorityUseInScopeDeclared','TypedPrecisionForUseDeclared']:add('missing-use-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('use-binds-outside-record',lambda m:setfn(m,'useRecord','u0','rOutside'),T=False)
 for n in b.ROLES:add('provenance-meaning-collapsed-to-'+n,lambda m,n=n:m['predicates'][n].append(['m0']),T=False)
 add('sibling-assignment-without-explicit-reference',lambda m:m['predicates']['SiblingMeaningAssignmentDeclared'].append(['m0','extra']),T=False)
 add('collapsed-source-evidence-and-adaptation-labels',lambda m:m['constants'].update(LOCALADAPTATION='sourceevidence'),T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('ProvenanceMeaning'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['stepSource'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='sourceA'),error='ill-sorted-constant')
 add('wrong-order-arity',lambda m:m['predicates'].update(StepBeforeDeclared=[['s0']]),error='ill-sorted-model-tuple')
 add('duplicate-record-tuple',lambda m:m['predicates']['ProvenanceRecordApplicable'].append(['rFull']),error='duplicate-predicate-tuple')
 add('empty-path-domain',lambda m:m['domains'].update(Path=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['stepSource'].append(copy.deepcopy(m['functions']['stepSource'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.measurement-result/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Provenance-model-controls/v1-candidate','status':'PASS-for-exact-authored-Provenance-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed declared Provenance records,strict per-path step ordering,five-field projections,owner-routed gaps and necessary typed-use guards checked on supplied models. Actual completeness,truth,proof,trust,validation,credit,authority,owner acceptance and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
