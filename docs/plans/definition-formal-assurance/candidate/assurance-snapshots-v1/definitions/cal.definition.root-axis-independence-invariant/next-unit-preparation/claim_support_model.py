"""Independent Claim-Support bound/remediation finite controls; no actual truth or authority."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 claims=['cGood','cPartial','cPrivate','cIndirect','cDisputed','cWeaker','cNoneCandidate','cNoneHypothesis','cOutside'];active=claims[:-1];supported=claims[:6]
 packages=['pGood','pPartial','pPrivate','pIndirect','pDisputed','pWeaker','pEmpty','pOutside'];items=['iCitation','iValidation','iWitness','iDecision','iPremise','iFormal'];interpreters=['intDomain','intValidator','intResearch','intOwner','intConstitution','intOutside']
 constants={'EMPTY':'empty','MEANING_ID':'claim-support-id','MEANING_KIND':'invariant-kind','MEANING_CARRIER':'invariant-carrier','MEANING_SCOPE':'shared-owner-scope','SOURCE_D38':'D38'}
 domains={'Invariant':['inv'],'Claim':claims,'ClaimType':['type','outsideType'],'Context':['context','outsideContext'],'Interpreter':interpreters,'SupportPackage':packages,'SupportItem':items,'Strength':['low','supported','overclaim'],'Token':list(constants.values())+['reference','same-label']}
 cp=dict(zip(supported,packages[:6]));ci=dict(zip(supported,interpreters[:5]+['intDomain']));meta=dict(zip(['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D38']))
 maps={n:(lambda v,n=n:constants[meta[n]]) for n in meta}
 maps.update(claimInvariant=lambda c:'inv',claimType=lambda c:'outsideType' if c=='cOutside' else 'type',claimContext=lambda c:'outsideContext' if c=='cOutside' else 'context',claimInterpreter=lambda c:ci.get(c,'intOutside' if c=='cOutside' else 'intDomain'),claimPackage=lambda c:cp.get(c,'pOutside' if c=='cOutside' else 'pEmpty'),claimHandle=lambda c:'same-label',claimTreatmentReference=lambda c:'reference',interpreterType=lambda x:'outsideType' if x=='intOutside' else 'type',interpreterContext=lambda x:'outsideContext' if x=='intOutside' else 'context',interpreterHandle=lambda x:'reference',packageType=lambda p:'outsideType' if p=='pOutside' else 'type',packageContext=lambda p:'outsideContext' if p=='pOutside' else 'context',packageInterpreter=lambda p:ci[supported[packages.index(p)]] if p in packages[:6] else ('intOutside' if p=='pOutside' else 'intDomain'),packageHandle=lambda p:'reference' if p in packages[:6] else 'empty',itemType=lambda i:'type',itemContext=lambda i:'context',itemHandle=lambda i:'reference')
 for d in b.DIMENSIONS:
  maps['claim'+d+'Strength']=lambda c:'overclaim' if c=='cWeaker' else ('low' if c in claims[6:] else 'supported')
  maps['package'+d+'Strength']=lambda p:'supported' if p in packages[:6] else 'low'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['ClaimSupportInvariant','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:predicates[n]=[['inv']]
 for n in ['ClaimApplicable','WordingInScopeDeclared','ClaimTypeDeclared']:predicates[n]=[[c] for c in active]
 predicates.update(ContextDeclared=[['context']],InterpreterDeclared=[[i] for i in interpreters[:-1]],PackageDeclared=[[p] for p in packages[:6]],ClaimHasSupport=[[c] for c in supported],ClaimCitesPackage=[[c] for c in supported],WithinDeclaredSupportBound=[[c] for c in supported[:-1]],CompatibleClaim=[[c] for c in supported[:-1]],HonestWordingDeclared=[[c] for c in supported[:-1]],RiskyClaim=[[c] for c in active[1:]],SupportItemIncluded=[[p,i] for p in packages[:6] for i in items],AllowedStrength=[[i,'type',left,right] for i in interpreters[:-1] for left,right in [('low','supported'),('supported','supported'),('low','low')]])
 for n,x in zip(b.INTERPRETER_KINDS,interpreters):predicates[n]=[[x]]
 for n,x in zip(b.ITEM_KINDS,items):predicates[n]=[[x]]
 for n,x in zip(b.POSTURES,supported[1:]):predicates[n]=[[x]]
 predicates.update(DowngradeDeclared=[['cPartial']],ResidueFlagDeclared=[['cPrivate']],GateRouteDeclared=[['cIndirect']],GoverningBlockDeclared=[['cDisputed']],CandidateWordingDeclared=[['cWeaker'],['cNoneCandidate']],HypothesisWordingDeclared=[['cNoneHypothesis']])
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('plural-support-domain-bounds-and-explicit-risk-treatment',lambda m:None,I=True)
 for n in b.INV_OUTCOMES:add('independent-Invariant-actual-'+n,lambda m,n=n:m['predicates']['InvariantActual'+n].append(['inv']))
 for n in b.CLAIM_OUTCOMES:add('independent-Claim-actual-'+n,lambda m,n=n:m['predicates']['ClaimActual'+n].append(['cGood']),I=True)
 add('support-kind-overlap-allowed',lambda m:m['predicates']['FormalProofSupport'].append(['iCitation']),I=True)
 add('interpreter-kind-overlap-allowed',lambda m:m['predicates']['OwnerDecisionInterpreter'].append(['intDomain']),I=True)
 add('remediation-alternatives-may-overlap',lambda m:m['predicates']['GateRouteDeclared'].append(['cPrivate']),I=True)
 add('outside-scope-package-map-unconstrained',lambda m:setfn(m,'claimPackage','cOutside','pGood'),I=True)
 add('domain-strength-relation-not-numeric-total-order',lambda m:m['predicates']['AllowedStrength'].append(['intOwner','type','supported','low']),I=True)
 for n in ['ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'inv','empty'),T=False)
 for n in ['WordingInScopeDeclared','ClaimTypeDeclared']:add('missing-applicability-'+n,lambda m,n=n:m['predicates'][n].remove(['cGood']),T=False)
 add('missing-context-declaration',lambda m:m['predicates']['ContextDeclared'].clear(),T=False)
 add('missing-interpreter-declaration',lambda m:m['predicates']['InterpreterDeclared'].remove(['intDomain']),T=False)
 for n,value in [('interpreterType','outsideType'),('interpreterContext','outsideContext'),('interpreterHandle','empty')]:add('wrong-interpreter-'+n,lambda m,n=n,value=value:setfn(m,n,'intDomain',value),T=False)
 add('interpreter-no-eligible-kind',lambda m:m['predicates']['DomainInterpreter'].clear(),T=False)
 add('empty-claim-handle',lambda m:setfn(m,'claimHandle','cGood','empty'),T=False)
 add('support-without-citation',lambda m:m['predicates']['ClaimCitesPackage'].remove(['cGood']),T=False)
 add('support-without-declared-package',lambda m:m['predicates']['PackageDeclared'].remove(['pGood']),T=False)
 add('cited-package-with-support-denied',lambda m:m['predicates']['ClaimHasSupport'].remove(['cGood']),T=False)
 for n,value in [('packageType','outsideType'),('packageContext','outsideContext'),('packageInterpreter','intOutside'),('packageHandle','empty')]:add('wrong-support-package-'+n,lambda m,n=n,value=value:setfn(m,n,'pGood',value),T=False)
 add('empty-cited-support-item-set',lambda m:m['predicates'].update(SupportItemIncluded=[x for x in m['predicates']['SupportItemIncluded'] if x[0]!='pGood']),T=False)
 for n,value in [('itemType','outsideType'),('itemContext','outsideContext'),('itemHandle','empty')]:add('wrong-included-item-'+n,lambda m,n=n,value=value:setfn(m,n,'iCitation',value),T=False)
 add('support-item-with-no-eligible-kind',lambda m:m['predicates']['SourceCitationSupport'].clear(),T=False)
 for d in b.DIMENSIONS:add('overclaimed-'+d+'-dimension',lambda m,d=d:setfn(m,'claim'+d+'Strength','cGood','overclaim'),T=False)
 add('support-bound-with-no-domain-comparison',lambda m:m['predicates']['AllowedStrength'].remove(['intDomain','type','supported','supported']),T=False)
 add('weaker-claim-marked-within-bound',lambda m:m['predicates']['WithinDeclaredSupportBound'].append(['cWeaker']),T=False)
 add('compatible-without-honest-wording',lambda m:m['predicates']['HonestWordingDeclared'].remove(['cGood']),T=False)
 add('compatible-claim-label-denied',lambda m:m['predicates']['CompatibleClaim'].remove(['cGood']),T=False)
 add('absent-support-risk-denied',lambda m:m['predicates']['RiskyClaim'].remove(['cNoneCandidate']),T=False)
 add('good-support-spurious-risk',lambda m:m['predicates']['RiskyClaim'].append(['cGood']),T=False)
 for posture,claim,treatment in zip(b.POSTURES,['cPartial','cPrivate','cIndirect','cDisputed','cWeaker'],['DowngradeDeclared','ResidueFlagDeclared','GateRouteDeclared','GoverningBlockDeclared','CandidateWordingDeclared']):add('risk-without-treatment-'+posture,lambda m,claim=claim,treatment=treatment:m['predicates'][treatment].remove([claim]),T=False)
 add('risk-empty-treatment-reference',lambda m:setfn(m,'claimTreatmentReference','cPrivate','empty'),T=False)
 def absent_only_gate(m):m['predicates']['CandidateWordingDeclared'].remove(['cNoneCandidate']);m['predicates']['GateRouteDeclared'].append(['cNoneCandidate'])
 add('absent-support-gate-does-not-replace-default-wording',absent_only_gate,T=False)
 for n in ['FormalProofOnlyRole','MaximalCertaintyRequiredRole']:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['inv']),T=False)
 def no_formal_kind(m):m['predicates']['FormalProofSupport'].clear();m['predicates']['WitnessSupport'].append(['iFormal'])
 add('formal-proof-kind-not-mandatory-for-every-package',no_formal_kind,I=False)
 def bounded_weaker(m):
  for d in b.DIMENSIONS:setfn(m,'claim'+d+'Strength','cWeaker','supported')
  m['predicates']['WithinDeclaredSupportBound'].append(['cWeaker'])
 add('declared-weaker-posture-still-needs-treatment-when-strength-bounded',bounded_weaker,I=True)
 add('missing-total-function-entry',lambda m:m['functions']['claimPackage'].pop(),error='nontotal-function')
 add('ill-sorted-package-result',lambda m:setfn(m,'claimPackage','cGood','context'),error='ill-sorted-function-result')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='context'),error='ill-sorted-constant')
 add('wrong-comparison-arity',lambda m:m['predicates'].update(AllowedStrength=[['intDomain','type','low']]),error='ill-sorted-model-tuple')
 add('duplicate-claim-tuple',lambda m:m['predicates']['ClaimApplicable'].append(['cGood']),error='duplicate-predicate-tuple')
 add('empty-strength-domain',lambda m:m['domains'].update(Strength=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['claimPackage'].append(copy.deepcopy(m['functions']['claimPackage'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.root-axis-independence-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ClaimSupport-model-controls/v1-candidate','status':'PASS-for-exact-authored-ClaimSupport-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed domain-interpreted claim/support comparisons,plural support and interpreter kinds,explicit weak-support remediation and absent-support defaults checked on supplied models. Actual truth,authority,evidence adequacy,publication,validation,gate clearance,execution,owner fidelity and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
