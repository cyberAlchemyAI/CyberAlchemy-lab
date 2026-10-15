import copy,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def getfn(m,name,arg):return next(row['value'] for row in m['functions'][name] if row['args']==[arg])
def setfn(m,name,arg,value):next(row for row in m['functions'][name] if row['args']==[arg])['value']=value
def refresh(m):
 for fields,carrier in b.GROUPS:
  for name in fields:m['predicates'][name+'BindingDeclared']=[[row['args'][0],row['value']] for row in m['functions'][name]]
 claims=[row[0] for row in m['predicates']['ClaimApplicable']]
 m['predicates']['IntentTraceTargetDeclared']=[list(row) for row in sorted({(getfn(m,'claimIntent',claim),getfn(m,'claimTraceTarget',claim)) for claim in claims})]
def base_model():
 domains={sort:[sort+'0',sort+'1',sort+'Outside'] for sort in b.SORTS}
 domains.update(IntentReference=['intent'+str(i) for i in range(8)]+['intentOutside'],MeaningReference=['semanticIntent','meaningOther','meaningOutside'],CoordinationScopeReference=['coordination','ownerScopeOther','ownerScopeOutside'],CarrierTypeReference=['definitionType','carrierOther','carrierOutside'],SourceSectionReference=['D39','sectionOther','sectionOutside'],OutputHypothesisReference=['hypInitial','hypDeferred','hypCode','hypOther','hypChanged','hypAlternative','hypOutside'],RevisionRouteReference=['route0','route1','route2','routeOutside'],AttributorReference=['actor0','actor1','actorOutside'],SiblingTargetReference=['sibling0','sibling1','siblingOutside'],ChangeReference=['change0','change1','change2','changeOutside'],ReasonReference=['reason0','reason1','reason2','reasonOutside'],ClaimReference=['claimArtifact','claimDecision','claimResidue','claimRoute','claimShared','claimOutside'],TraceTargetReference=['targetArtifact','targetDecision','targetResidue','targetRoute','targetOutside'],Token=['empty','token'])
 m={'domains':domains,'constants':{'EMPTY':'empty','NORMALIZED_MEANING':'semanticIntent','COORDINATION_SCOPE':'coordination','DEFINITION_CARRIER':'definitionType','BOUND_SOURCE_SECTION':'D39'},'functions':{},'predicates':{name:[] for name in b.SIGNATURE}}
 for name,(args,result) in b.FUNCTIONS.items():m['functions'][name]=[{'args':[arg],'value':'token' if name in b.HANDLES.values() else domains[result][0]} for arg in domains[args[0]]]
 for sort in b.SORTS:
  if sort!='Token':m['predicates'][sort+'Declared']=[[value] for value in domains[sort]]
 selected=domains['IntentReference'][:-1]
 for name in ['IntentApplicable','IntentInScopeDeclared','IntentAttributableDeclared','IntentRouteBoundedDeclared','IntentRevisableDeclared','IntentTraceableDeclared',*['Intent'+facet+'SeparatelyGovernedDeclared' for facet in b.FACETS]]:m['predicates'][name]=[[value] for value in selected]
 m['predicates']['CanonicalIntentDeclared']=[['intent'+str(i)] for i in [0,1,2,3,6]]
 for row in m['predicates']['CanonicalIntentDeclared']:m['predicates']['IntentOriginatesFromSectionDeclared'].append([row[0],'D39'])
 for i,mode in enumerate(b.MODES):m['predicates']['IntentOrientation'+mode+'Declared'].append(['intent'+str(i)])
 m['predicates']['IntentOrientationPurposeDeclared'] += [['intent4'],['intent5'],['intent7']];m['predicates']['IntentOrientationProblemPressureDeclared'] += [['intent4'],['intent6']]
 m['predicates']['IntentAttributionDeclared']=[[value,'actor1' if value=='intent1' else 'actor0'] for value in selected]
 for intent,hyp in [('intent1','hypDeferred'),('intent2','hypCode'),('intent3','hypOther'),('intent4','hypOther'),('intent5','hypChanged'),('intent6','hypAlternative')]:setfn(m,'intentOutputHypothesis',intent,hyp)
 setfn(m,'intentRevisionRoute','intent5','route1');setfn(m,'intentRevisionRoute','intent6','route2')
 m['predicates']['HypothesisCodeOutputDeclared']=[['hypCode']];m['predicates']['HypothesisDeferredQuestionDeclared']=[['hypDeferred']];m['predicates']['HypothesisFinalShapeSettledDeclared']=[['hypCode'],['hypOther']]
 m['predicates']['IntentActualMutationAuthority']=[['intent4']]
 m['predicates']['IntentExplicitSiblingReferenceDeclared']=[['intent0','sibling0'],['intent1','sibling1']];m['predicates']['IntentUsesSiblingMeaningDeclared']=[['intent0','sibling0']]
 for name in ['ChangeApplicable','ChangeInScopeDeclared']:m['predicates'][name]=[['change0'],['change1'],['change2']]
 for change,original,after,hyp,route in [('change0','intent0','intent5','hypChanged','route1'),('change1','intent1','intent1','hypDeferred','route0'),('change2','intent3','intent6','hypAlternative','route2')]:
  for name,value in [('changeOriginalIntent',original),('changeAfterIntent',after),('changeDesiredHypothesis',hyp),('changeRevisionRoute',route)]:setfn(m,name,change,value)
 m['predicates']['ChangeExplanationReasonDeclared']=[['change0','reason0'],['change0','reason1'],['change2','reason2']];m['predicates']['RouteRecordsChangeReasonDeclared']=[['route1','change0','reason0'],['route1','change0','reason1'],['route2','change2','reason2']]
 claims=domains['ClaimReference'][:-1]
 for name in ['ClaimApplicable','ClaimInScopeDeclared','ClaimSatisfactionClaimDeclared']:m['predicates'][name]=[[value] for value in claims]
 for i,kind in enumerate(b.TRACE_KINDS):
  claim='claim'+kind if kind!='NextRoute' else 'claimRoute';m['predicates']['ClaimTraceKind'+kind+'Declared'].append([claim]);setfn(m,'claimIntent',claim,'intent'+str(i));setfn(m,'claimTraceTarget',claim,'target'+kind if kind!='NextRoute' else 'targetRoute')
 setfn(m,'claimIntent','claimShared','intent0');setfn(m,'claimTraceTarget','claimShared','targetArtifact');m['predicates']['ClaimTraceKindArtifactDeclared'].append(['claimShared']);m['predicates']['ClaimTraceKindDecisionDeclared'].append(['claimShared']);m['predicates']['ClaimActualSatisfaction']=[['claimShared']]
 refresh(m);return m
def controls():
 baseline=base_model();rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  model=copy.deepcopy(baseline);mutation(model);rows.append({'case_id':name,'model':model,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,name,arg,value):setfn(m,name,arg,value);refresh(m)
 add('seven-coordinates-canonical-and-noncanonical-explained-changes-four-trace-kinds')
 for prefix,outcomes,subject in [('Intent',b.ACTUAL,'intent0'),('Change',b.CHANGE_ACTUAL,'change0'),('Claim',b.CLAIM_ACTUAL,'claimArtifact')]:
  for outcome in outcomes:add('independently-supported-'+prefix+outcome,lambda m,prefix=prefix,outcome=outcome,subject=subject:m['predicates'][prefix+'Actual'+outcome].append([subject]))
 for name in b.EXCLUDED:
  add('selected-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['intent0']),T=False,I=None);add('outside-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['intentOutside']))
 for name in b.INFERRED:
  predicate='IntentTermInfers'+name+'Declared';add('selected-term-inference-'+name,lambda m,predicate=predicate:m['predicates'][predicate].append(['intent0']),T=False,I=None);add('outside-term-inference-'+name,lambda m,predicate=predicate:m['predicates'][predicate].append(['intentOutside']))
 def clear_selected(m):
  for name in ['IntentApplicable','IntentInScopeDeclared','ChangeApplicable','ChangeInScopeDeclared','ClaimApplicable','ClaimInScopeDeclared']:m['predicates'][name]=[]
  refresh(m)
 add('no-selected-intents-changes-or-claims',clear_selected,I=False)
 for label,names in [('changes',['ChangeApplicable','ChangeInScopeDeclared']),('claims',['ClaimApplicable','ClaimInScopeDeclared'])]:
  add('no-selected-'+label,lambda m,names=names:(m['predicates'].update({name:[] for name in names}),refresh(m)),I=False)
 for name in ['IntentAttributableDeclared','IntentRouteBoundedDeclared','IntentRevisableDeclared','IntentTraceableDeclared','IntentInScopeDeclared',*['Intent'+facet+'SeparatelyGovernedDeclared' for facet in b.FACETS]]:add('missing-'+name,lambda m,name=name:m['predicates'][name].remove(['intent0']),T=False,I=None)
 add('no-orientation-mode',lambda m:m['predicates']['IntentOrientationPurposeDeclared'].remove(['intent0']),T=False,I=None)
 add('mixed-orientation-reduced-to-pressure',lambda m:m['predicates']['IntentOrientationPurposeDeclared'].remove(['intent4']),I=False)
 add('attribution-declaration-missing',lambda m:m['predicates'].update(IntentAttributionDeclared=[row for row in m['predicates']['IntentAttributionDeclared'] if row[0]!='intent0']),T=False,I=None)
 add('nominated-attributor-undeclared',lambda m:m['predicates']['AttributorReferenceDeclared'].remove(['actor0']),T=False,I=None)
 add('nominated-attributor-handle-empty',lambda m:setfn(m,b.HANDLES['AttributorReference'],'actor0','empty'),T=False,I=None)
 add('canonical-source-section-link-missing',lambda m:m['predicates']['IntentOriginatesFromSectionDeclared'].remove(['intent0','D39']),T=False,I=None)
 for name,wrong in [('intentMeaning','meaningOther'),('intentOwnerScope','ownerScopeOther'),('intentCarrierType','carrierOther')]:
  add('canonical-classification-mismatch-'+name,lambda m,name=name,wrong=wrong:change(m,name,'intent0',wrong),T=False,I=None)
  add('noncanonical-unused-classification-'+name,lambda m,name=name,wrong=wrong:change(m,name,'intent4',wrong))
  add('noncanonical-unused-binding-'+name,lambda m,name=name:m['predicates'].update({name+'BindingDeclared':[row for row in m['predicates'][name+'BindingDeclared'] if row[0]!='intent4']}))
 add('additional-explicit-source-section-permitted',lambda m:m['predicates']['IntentOriginatesFromSectionDeclared'].append(['intent0','sectionOther']))
 add('sibling-use-without-explicit-reference',lambda m:m['predicates']['IntentExplicitSiblingReferenceDeclared'].remove(['intent0','sibling0']),T=False,I=None)
 add('silent-sibling-merge',lambda m:m['predicates']['IntentSilentlyMergesSiblingDeclared'].append(['intent0','sibling0']),T=False,I=None)
 add('sibling-use-undeclared-target',lambda m:m['predicates']['SiblingTargetReferenceDeclared'].remove(['sibling0']),T=False,I=None)
 def no_reasons(m,change):
  m['predicates']['ChangeExplanationReasonDeclared']=[row for row in m['predicates']['ChangeExplanationReasonDeclared'] if row[0]!=change];m['predicates']['RouteRecordsChangeReasonDeclared']=[row for row in m['predicates']['RouteRecordsChangeReasonDeclared'] if row[1]!=change]
 add('changed-output-no-declared-explanation',lambda m:no_reasons(m,'change0'),T=False,I=None)
 add('changed-output-route-does-not-record-why',lambda m:m['predicates'].update(RouteRecordsChangeReasonDeclared=[row for row in m['predicates']['RouteRecordsChangeReasonDeclared'] if row[1]!='change0']),T=False,I=None)
 add('changed-output-after-is-before',lambda m:change(m,'changeAfterIntent','change0','intent0'),T=False,I=None)
 add('changed-output-wrong-after-hypothesis',lambda m:change(m,'changeDesiredHypothesis','change0','hypOther'),T=False,I=None)
 add('changed-output-route-does-not-match-after',lambda m:change(m,'changeRevisionRoute','change0','route0'),T=False,I=None)
 def one_reason(m):m['predicates']['ChangeExplanationReasonDeclared'].remove(['change0','reason1']);m['predicates']['RouteRecordsChangeReasonDeclared'].remove(['route1','change0','reason1'])
 add('single-explanation-still-valid',one_reason,I=False)
 add('no-output-change-unused-reason-can-be-absent',lambda m:no_reasons(m,'change1'))
 add('no-output-change-extra-explanation-permitted',lambda m:(m['predicates']['ChangeExplanationReasonDeclared'].append(['change1','reason2']),m['predicates']['RouteRecordsChangeReasonDeclared'].append(['route0','change1','reason2'])))
 add('claim-trace-link-missing',lambda m:m['predicates']['IntentTraceTargetDeclared'].remove(['intent0','targetArtifact']),T=False,I=None)
 add('claim-no-kind-nomination',lambda m:m['predicates']['ClaimTraceKindResidueDeclared'].remove(['claimResidue']),T=False,I=None)
 add('claim-targets-unselected-intent',lambda m:change(m,'claimIntent','claimArtifact','intentOutside'),T=False,I=None)
 add('claim-not-declared-satisfaction-claim',lambda m:m['predicates']['ClaimSatisfactionClaimDeclared'].remove(['claimArtifact']),T=False,I=None)
 for name in ['ChangeInScopeDeclared','ClaimInScopeDeclared']:add('scope-declaration-mismatch-'+name,lambda m,name=name:m['predicates'][name].remove(['change0' if name.startswith('Change') else 'claimArtifact']),T=False,I=None)
 for fields,arg in [(b.FIELDS,'intent0'),(b.CLASS_FIELDS,'intent0'),(b.CHANGE_FIELDS,'change0'),(b.CLAIM_FIELDS,'claimArtifact')]:
  for name,sort in fields.items():
   value=getfn(baseline,name,arg);other=next(x for x in baseline['domains'][sort] if x!=value)
   add('missing-exact-binding-'+name,lambda m,name=name,arg=arg:m['predicates'].update({name+'BindingDeclared':[row for row in m['predicates'][name+'BindingDeclared'] if row[0]!=arg]}),T=False,I=None)
   add('conflicting-exact-binding-'+name,lambda m,name=name,arg=arg,other=other:m['predicates'][name+'BindingDeclared'].append([arg,other]),T=False,I=None)
   if sort not in b.MAP:add('undeclared-selected-target-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
   add('empty-selected-handle-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
 for name,sort in b.CONSTANTS.items():
  if name=='EMPTY':continue
  value=baseline['constants'][name];add('undeclared-source-constant-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None);add('empty-source-constant-handle-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
 for sort,arg in [('IntentReference','intent0'),('ChangeReference','change0'),('ClaimReference','claimArtifact')]:add('empty-selected-root-handle-'+sort,lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False,I=None)
 for name,mutation,error in [('empty-domain',lambda m:m['domains'].update(IntentReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('MeaningReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('intentSource'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['intentRevisionRoute'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'intentPurpose','intent0','foreign'),'ill-sorted-function-result'),('predicate-arity',lambda m:m['predicates']['RouteRecordsChangeReasonDeclared'].append(['route1','change0']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['IntentApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('missing-constant',lambda m:m['constants'].pop('BOUND_SOURCE_SECTION'),'model-signature-denominator-mismatch')]:add('malformed-'+name,mutation,error=error)
 return rows
def qualify(model,ids):return {bucket:{ids[name]:value for name,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}

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
    prior=json.loads((b.BASE/'definitions/cal.definition.implementation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Intent-model-controls/v1-candidate','status':'PASS-for-exact-authored-Intent-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary Intent classification, seven-coordinate nominations, explained revision, explicit claim trace and noninference guards checked on supplied models; actual outcomes, fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
