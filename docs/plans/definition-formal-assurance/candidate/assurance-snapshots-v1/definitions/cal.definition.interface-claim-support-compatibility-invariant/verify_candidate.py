"""Independent supplied Interface claim models; necessary guards never prove actual outcomes."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 claims=['cValid','cMatched']+['cClass'+str(i) for i in range(5)]+['cDirect'+n for n in b.DIRECT]+['cHuman'+n for n in b.HUMAN]+['cHumanDet','cWeakDown','cWeakRoute','cWeakBlock','cDense','cOutside'];active=claims[:-1];classes=['k'+str(i) for i in range(5)]+['kOutside'];constants=dict(zip(b.CONSTANTS,['empty','interface-id','invariant-kind','invariant-carrier','ux-scope','D47']))
 domains={'Invariant':['inv'],'InterfaceClaim':claims,'ClaimClass':classes,'EvidenceKind':['browserEvidence','outsideEvidence'],'ProxyLimit':['limit','outsideLimit'],'OwnerRoute':['ownerRoute','outsideRoute'],'Residue':['residue','outsideResidue'],'Context':['context','outsideContext'],'Token':list(constants.values())+['reference','same-label']}
 meta=dict(zip(b.META,['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D47']));maps={n:(lambda v,n=n:constants[meta[n]]) for n in meta}
 def kind(c):
  if c=='cOutside':return 'kOutside'
  if c.startswith('cClass'):return 'k'+c[-1]
  if c.startswith('cHuman'):return 'k3'
  return 'k0'
 maps.update(claimInvariant=lambda c:'inv',claimClass=kind,claimEvidence=lambda c:'outsideEvidence' if c=='cOutside' else 'browserEvidence',claimLimit=lambda c:'outsideLimit' if c=='cOutside' else 'limit',claimOwnerRoute=lambda c:'outsideRoute' if c=='cOutside' else 'ownerRoute',claimResidue=lambda c:'outsideResidue' if c=='cOutside' else 'residue',claimContext=lambda c:'outsideContext' if c=='cOutside' else 'context')
 for n in ['claimHandle','classHandle','evidenceHandle','limitHandle','routeHandle','residueHandle','contextHandle','calibrationHandle','approvalHandle','treatmentHandle']:maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['InterfaceClaimSupportInvariant','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:predicates[n]=[['inv']]
 for n in ['InterfaceClaimApplicable','UXClaimInScopeDeclared']:predicates[n]=[[c] for c in active]
 for n,k in zip(b.CLASSES,classes):predicates[n]=[[k]]
 predicates.update(EvidenceKindDeclared=[['browserEvidence']],BrowserEvidenceKind=[['browserEvidence']],ProxyLimitDeclared=[['limit']],ProxyLimitStatesUnproven=[['limit']],OwnerRouteDeclared=[['ownerRoute']],ResidueDeclared=[['residue']],ContextDeclared=[['context']],ClassEvidenceMatches=[[k,'browserEvidence','context'] for k in classes[:-1]],ValidClaimDeclared=[['cValid']],BrowserEvidenceUsedDeclared=[[c] for c in active if c.startswith('cDirect') or c.startswith('cHuman')],DeterministicAuthorityPostureDeclared=[['cHumanDet']],CalibratedFixturesDeclared=[['cHumanDet']],OwnerApprovalDeclared=[['cHumanDet']],WeakerEvidenceDeclared=[[c] for c in ['cWeakDown','cWeakRoute','cWeakBlock']],DowngradeDeclared=[['cWeakDown']],RouteDeclared=[['cWeakRoute']],BlockDeclared=[['cWeakBlock']],DenseExpertBlockDeclared=[['cDense']],FalsePositiveCalibrationDeclared=[['cDense']])
 for n in b.DIRECT:predicates['Direct'+n+'Topic']=[['cDirect'+n]]
 for n in b.HUMAN:predicates['Human'+n+'Topic']=[['cHuman'+n]]
 predicates['HumanCognitiveTopic'].append(['cHumanDet'])
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('five-class-tuple-necessary-guards-and-separated-human-preparation',lambda m:None,I=True)
 for n in b.INV_OUTCOMES:add('independent-Invariant-actual-'+n,lambda m,n=n:m['predicates']['InvariantActual'+n].append(['inv']))
 for n in b.CLAIM_OUTCOMES:add('independent-Claim-actual-'+n,lambda m,n=n:m['predicates']['ClaimActual'+n].append(['cMatched']),I=True)
 add('class-label-overlap-allowed',lambda m:m['predicates']['NotAutomatableClass'].append(['k0']),I=True)
 add('direct-and-human-topic-labels-may-overlap',lambda m:m['predicates']['HumanCognitiveTopic'].append(['cDirectPageLoad']),I=True)
 add('response-alternatives-may-overlap',lambda m:m['predicates']['BlockDeclared'].append(['cWeakDown']),I=True)
 add('matching-does-not-force-declared-validity',lambda m:None,I=True)
 add('outside-scope-empty-tuple-handle',lambda m:setfn(m,'classHandle','kOutside','empty'),I=True)
 add('outside-human-declared-posture-not-authority-axiom',lambda m:m['predicates']['DeterministicAuthorityPostureDeclared'].append(['cDense']),I=True)
 add('unmatched-human-preparation-without-declared-validity',lambda m:m['predicates']['ClassEvidenceMatches'].remove(['k3','browserEvidence','context']),I=True)
 add('fixture-and-approval-labels-not-universally-required',lambda m:m['predicates']['CalibratedFixturesDeclared'].append(['cDirectPageLoad']),I=True)
 for n in ['ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in b.META:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'inv','empty'),T=False)
 add('missing-UX-scope-declaration',lambda m:m['predicates']['UXClaimInScopeDeclared'].remove(['cValid']),T=False)
 add('scope-declared-applicability-denied',lambda m:m['predicates']['InterfaceClaimApplicable'].remove(['cValid']),T=False)
 add('unclassified-selected-class',lambda m:m['predicates']['HardGateClass'].clear(),T=False)
 for n in ['EvidenceKindDeclared','ProxyLimitDeclared','OwnerRouteDeclared','ResidueDeclared','ContextDeclared']:add('missing-tuple-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n,arg in [('claimHandle','cValid'),('classHandle','k0'),('evidenceHandle','browserEvidence'),('limitHandle','limit'),('routeHandle','ownerRoute'),('residueHandle','residue'),('contextHandle','context')]:add('empty-tuple-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('valid-declared-class-evidence-mismatch',lambda m:m['predicates']['ClassEvidenceMatches'].remove(['k0','browserEvidence','context']),T=False)
 def unstated_not_valid(m):setfn(m,'claimLimit','cMatched','outsideLimit');m['predicates']['ProxyLimitDeclared'].append(['outsideLimit'])
 add('not-valid-declared-claim-still-needs-unproven-limit',unstated_not_valid,T=False)
 add('valid-declared-proxy-does-not-state-unproven',lambda m:m['predicates']['ProxyLimitStatesUnproven'].clear(),T=False)
 add('browser-used-without-browser-kind',lambda m:m['predicates']['BrowserEvidenceKind'].clear(),T=False)
 for n in ['CalibratedFixturesDeclared','OwnerApprovalDeclared']:add('human-deterministic-missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['calibrationHandle','approvalHandle']:add('human-deterministic-empty-'+n,lambda m,n=n:setfn(m,n,'cHumanDet','empty'),T=False)
 for claim,treatment in [('cWeakDown','DowngradeDeclared'),('cWeakRoute','RouteDeclared'),('cWeakBlock','BlockDeclared')]:add('weaker-evidence-missing-'+treatment,lambda m,claim=claim,treatment=treatment:m['predicates'][treatment].remove([claim]),T=False)
 add('weaker-evidence-empty-treatment-ref',lambda m:setfn(m,'treatmentHandle','cWeakDown','empty'),T=False)
 add('dense-block-without-false-positive-calibration',lambda m:m['predicates']['FalsePositiveCalibrationDeclared'].clear(),T=False)
 add('dense-block-empty-calibration-ref',lambda m:setfn(m,'calibrationHandle','cDense','empty'),T=False)
 for n in b.ROLES:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['inv']),T=False)
 def sibling(m):m['predicates']['SiblingMeaningAssignmentDeclared']=[['inv','reference']];m['predicates']['ExplicitSiblingReferenceDeclared']=[['inv','reference']]
 add('explicit-sibling-declaration-not-adoption',sibling,I=True)
 add('sibling-assignment-without-reference',lambda m:m['predicates']['SiblingMeaningAssignmentDeclared'].append(['inv','reference']),T=False)
 def empty_sibling(m):m['predicates']['SiblingMeaningAssignmentDeclared']=[['inv','empty']];m['predicates']['ExplicitSiblingReferenceDeclared']=[['inv','empty']]
 add('sibling-empty-reference',empty_sibling,T=False)
 def no_human_posture(m):m['predicates']['DeterministicAuthorityPostureDeclared'].clear();m['predicates']['CalibratedFixturesDeclared'].clear();m['predicates']['OwnerApprovalDeclared'].clear()
 add('human-preparation-needs-no-global-authority-declarations',no_human_posture,I=False)
 add('no-valid-declaration-not-forced-by-match',lambda m:m['predicates']['ValidClaimDeclared'].clear(),I=False)
 add('missing-symbol',lambda m:m['predicates'].pop('ValidClaimDeclared'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['claimClass'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='context'),error='ill-sorted-constant')
 add('wrong-matching-arity',lambda m:m['predicates'].update(ClassEvidenceMatches=[['k0','browserEvidence']]),error='ill-sorted-model-tuple')
 add('duplicate-claim-tuple',lambda m:m['predicates']['InterfaceClaimApplicable'].append(['cValid']),error='duplicate-predicate-tuple')
 add('empty-proxy-domain',lambda m:m['domains'].update(ProxyLimit=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['claimClass'].append(copy.deepcopy(m['functions']['claimClass'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.finding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-InterfaceClaimSupport-model-controls/v1-candidate','status':'PASS-for-exact-authored-InterfaceClaimSupport-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed Interface claim/evidence class matching,necessary validity and browser/human calibration/approval guards,declared weakness responses and dense-expert false-positive safeguards checked on supplied models. Actual truth,adequacy,human outcomes,calibration,approval,authority,execution,owner fidelity and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
