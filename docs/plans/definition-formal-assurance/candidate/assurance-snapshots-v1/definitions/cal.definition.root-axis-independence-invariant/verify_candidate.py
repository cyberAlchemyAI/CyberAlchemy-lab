"""Independent Root-Axis governed-pair and explicit-bridge finite controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 pairs=['pNone','pTyped','pGate','pSchema','pValidator','pOwner','pOutside'];bridges=['bEmpty','bTyped','bGate','bSchema','bValidator','bOwner','bOutside'];active=pairs[1:-1];declared=bridges[1:-1]
 constants={'EMPTY':'empty','MEANING_ID':'root-axis-id','MEANING_KIND':'invariant-kind','MEANING_CARRIER':'invariant-carrier','MEANING_SCOPE':'shared-owner-scope','SOURCE_D29':'D29'}
 domains={'Invariant':['inv'],'Context':['context','outsideContext'],'Decision':['decision','outsideDecision'],'Axis':['left','right','outsideAxis'],'Pair':pairs,'Move':['leftMove','rightMove','outsideMove'],'Bridge':bridges,'Scope':['scope','outsideScope'],'Evidence':['evidence','outsideEvidence'],'Token':list(constants.values())+['reference','direction','effect','same-axis-label']}
 bp=dict(zip(pairs,bridges));meta=dict(zip(['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D29']));maps={n:(lambda v,n=n:constants[meta[n]]) for n in meta}
 maps.update(contextScope=lambda c:'scope' if c=='context' else 'outsideScope',decisionContext=lambda d:'context' if d=='decision' else 'outsideContext',axisHandle=lambda a:'same-axis-label',pairInvariant=lambda p:'inv',pairContext=lambda p:'outsideContext' if p=='pOutside' else 'context',pairDecision=lambda p:'outsideDecision' if p=='pOutside' else 'decision',pairSourceAxis=lambda p:'left',pairTargetAxis=lambda p:'right',pairFirstMove=lambda p:'leftMove',pairSecondMove=lambda p:'rightMove',pairBridge=lambda p:bp[p],pairTypedCouplingReference=lambda p:'reference',pairClassificationReference=lambda p:'reference',pairLifecycleReference=lambda p:'reference',moveAxis=lambda m:{'leftMove':'left','rightMove':'right','outsideMove':'outsideAxis'}[m],moveContext=lambda m:'outsideContext' if m=='outsideMove' else 'context',moveDecision=lambda m:'outsideDecision' if m=='outsideMove' else 'decision',bridgeContext=lambda x:'outsideContext' if x=='bOutside' else 'context',bridgeDecision=lambda x:'outsideDecision' if x=='bOutside' else 'decision',bridgeSourceAxis=lambda x:'left',bridgeTargetAxis=lambda x:'right',bridgeEvidence=lambda x:'evidence' if x in declared else 'outsideEvidence',bridgeEffect=lambda x:'effect' if x in declared else 'empty',bridgeDirection=lambda x:'direction' if x in declared else 'empty',evidenceHandle=lambda x:'reference' if x=='evidence' else 'empty')
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['RootAxisInvariant','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:predicates[n]=[['inv']]
 for n in ['PairGoverned','GovernanceConsiderationDeclared','RelevantAxesSelected']:predicates[n]=[[p] for p in pairs[:-1]]
 predicates.update(ContextGoverned=[['context']],AxisDeclaredInContext=[['context','left'],['context','right']],AxisRelevantForDecision=[['decision','left'],['decision','right']],PairHasBridge=[[p] for p in active],BridgeDeclared=[[x] for x in declared],BridgeDirectionNamed=[[x] for x in declared[:-1]],BridgeSymmetryNamed=[['bOwner']],IndependentVariationDeclared=[['pNone']],ClaimedCrossAxisInference=[[p] for p in active],InferenceNotSilent=[[p] for p in active],DecisionDependsOnCochange=[['pTyped'],['pGate']],TypedCouplingRepresented=[['pTyped'],['pGate']],ValidMoveDeclared=[['leftMove'],['rightMove']],ClassificationQuestion=[['pNone']],ClassificationReferenceDeclared=[['pNone']],LifecycleQuestion=[['pSchema']],LifecycleReferenceDeclared=[['pSchema']],NonIndependentAxesQuestion=[['pGate']])
 for n,x in zip(b.KINDS,declared):predicates[n]=[[x]]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('independent-moves-and-five-exact-bridge-kinds',lambda m:None,I=True)
 for n in b.INV_OUTCOMES:add('independent-Invariant-actual-'+n,lambda m,n=n:m['predicates']['InvariantActual'+n].append(['inv']))
 for n in b.PAIR_OUTCOMES:add('independent-Pair-actual-'+n,lambda m,n=n:m['predicates']['PairActual'+n].append(['pTyped']),I=True)
 add('bridge-kind-overlap-permitted',lambda m:m['predicates']['GateBridge'].append(['bTyped']),I=True)
 add('direction-and-symmetry-may-both-be-named',lambda m:m['predicates']['BridgeSymmetryNamed'].append(['bTyped']),I=True)
 add('equal-axis-labels-distinct-axis-identities',lambda m:None,I=True)
 add('two-valid-moves-without-cross-axis-inference',lambda m:None,I=True)
 add('gate-dependent-decision-uses-separate-typed-coupling-reference',lambda m:None,I=True)
 for n in ['ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'inv','empty'),T=False)
 for n in ['GovernanceConsiderationDeclared','RelevantAxesSelected']:add('missing-governed-pair-'+n,lambda m,n=n:m['predicates'][n].remove(['pTyped']),T=False)
 add('missing-governed-context',lambda m:m['predicates']['ContextGoverned'].clear(),T=False)
 add('wrong-decision-context',lambda m:setfn(m,'decisionContext','decision','outsideContext'),T=False)
 add('collapsed-axis-identities',lambda m:setfn(m,'pairTargetAxis','pTyped','left'),T=False)
 for n,args in [('AxisDeclaredInContext',['context','left']),('AxisRelevantForDecision',['decision','right'])]:add('missing-'+n,lambda m,n=n,args=args:m['predicates'][n].remove(args),T=False)
 for n,arg,value in [('moveAxis','leftMove','outsideAxis'),('moveContext','rightMove','outsideContext'),('moveDecision','leftMove','outsideDecision')]:add('wrong-bound-move-'+n,lambda m,n=n,arg=arg,value=value:setfn(m,n,arg,value),T=False)
 add('empty-named-axis-handle',lambda m:setfn(m,'axisHandle','left','empty'),T=False)
 add('claimed-bridge-without-declaration',lambda m:m['predicates']['BridgeDeclared'].remove(['bTyped']),T=False)
 add('declared-bridge-not-marked-present',lambda m:m['predicates']['PairHasBridge'].remove(['pTyped']),T=False)
 for n,value in [('bridgeContext','outsideContext'),('bridgeDecision','outsideDecision'),('bridgeSourceAxis','outsideAxis'),('bridgeTargetAxis','left')]:add('wrong-bridge-'+n,lambda m,n=n,value=value:setfn(m,n,'bTyped',value),T=False)
 add('bridge-with-no-eligible-kind',lambda m:m['predicates']['TypedCouplingBridge'].clear(),T=False)
 add('missing-bridge-direction-or-symmetry',lambda m:m['predicates']['BridgeDirectionNamed'].remove(['bTyped']),T=False)
 for n in ['bridgeDirection','bridgeEffect']:add('empty-bridge-'+n,lambda m,n=n:setfn(m,n,'bTyped','empty'),T=False)
 add('empty-evidence-reference',lambda m:setfn(m,'evidenceHandle','evidence','empty'),T=False)
 add('uncoupled-pair-missing-independent-variation-declaration',lambda m:m['predicates']['IndependentVariationDeclared'].clear(),T=False)
 add('cross-axis-inference-without-bridge',lambda m:m['predicates']['ClaimedCrossAxisInference'].append(['pNone']),T=False)
 add('silent-cross-axis-inference',lambda m:m['predicates']['InferenceNotSilent'].remove(['pTyped']),T=False)
 add('cross-axis-inference-without-valid-starting-move',lambda m:m['predicates']['ValidMoveDeclared'].remove(['leftMove']),T=False)
 add('dependent-decision-without-separate-typed-coupling',lambda m:m['predicates']['TypedCouplingRepresented'].remove(['pGate']),T=False)
 add('dependent-decision-empty-coupling-reference',lambda m:setfn(m,'pairTypedCouplingReference','pGate','empty'),T=False)
 add('classification-question-missing-reference-declaration',lambda m:m['predicates']['ClassificationReferenceDeclared'].clear(),T=False)
 add('classification-question-empty-reference',lambda m:setfn(m,'pairClassificationReference','pNone','empty'),T=False)
 add('lifecycle-question-missing-reference-declaration',lambda m:m['predicates']['LifecycleReferenceDeclared'].clear(),T=False)
 add('lifecycle-question-empty-reference',lambda m:setfn(m,'pairLifecycleReference','pSchema','empty'),T=False)
 for n in b.ROLES:add('forbidden-scientific-or-isolation-role-'+n,lambda m,n=n:m['predicates'][n].append(['inv']),T=False)
 add('outside-pair-not-forced-through-bridge-maps',lambda m:setfn(m,'pairBridge','pOutside','bTyped'),I=True)
 def no_symmetry(m):m['predicates']['BridgeSymmetryNamed'].clear();m['predicates']['BridgeDirectionNamed'].append(['bOwner'])
 add('named-forward-bridges-need-separate-symmetry-witness',no_symmetry,I=False)
 add('independent-second-move-witness-needed',lambda m:m['predicates']['ValidMoveDeclared'].remove(['rightMove']),I=False)
 add('missing-total-function-entry',lambda m:m['functions']['pairBridge'].pop(),error='nontotal-function')
 add('ill-sorted-bridge-result',lambda m:setfn(m,'pairBridge','pTyped','decision'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='context'),error='ill-sorted-constant')
 add('wrong-axis-context-arity',lambda m:m['predicates'].update(AxisDeclaredInContext=[['context']]),error='ill-sorted-model-tuple')
 add('duplicate-pair-tuple',lambda m:m['predicates']['PairGoverned'].append(['pTyped']),error='duplicate-predicate-tuple')
 add('empty-axis-domain',lambda m:m['domains'].update(Axis=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['pairBridge'].append(copy.deepcopy(m['functions']['pairBridge'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.policy/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-RootAxis-model-controls/v1-candidate','status':'PASS-for-exact-authored-RootAxis-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed Root-Axis governed decision pairs,named explicit bridge guards and separate typed-coupling/question routes checked on supplied models. Actual semantic independence,scientific claims,authorization,bridge admission,execution,owner fidelity and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
