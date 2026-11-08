"""Supplied Receipt exact records,complete membership and comparison models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg]
 next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Receipt=['rFull','rEmpty','rIndependent','rOutside'],ReceiptIdentity=['idFull','idEmpty','idOutside'],ValidationEventReference=['eventFull','eventEmpty','eventOutside'],InputOccurrence=['iOld','iRepeated','iNew','iOutside'],InputReference=['inputOld','inputNew','inputOutside'],DeclaredCheck=['c0','c1','c2','cOutside'],OutcomeReference=['o0','o1','o2','oRepeated','oOutside'],AuthorityEffect=['effectNone','effectOther'],Observation=['aFirst','aSecond','aOutside'],InputComparison=['xChanged','xInvalid','xBoth','xOutside'],RecordOnlyComparison=['yStable','yIndependent','yOutside'],Digest=['dSubject','dProfile','dValidator','dOld','dNew','dRecord','dOutside'],Token=['empty','reference','stateA','stateB'])
 constants={'EMPTY':'empty','NONE':'effectNone'};maps={}
 for n,s in b.FIELDS.items():maps[n]=lambda r,s=s:domains[s][-1] if r=='rOutside' else domains[s][0]
 maps['receiptIdentity']=lambda r:'idOutside' if r=='rOutside' else 'idEmpty' if r=='rEmpty' else 'idFull'
 maps['receiptEvent']=lambda r:'eventOutside' if r=='rOutside' else 'eventEmpty' if r=='rEmpty' else 'eventFull'
 maps['receiptEffect']=lambda r:'effectOther' if r=='rOutside' else 'effectNone'
 for part,s in [('Subject','SubjectReference'),('Profile','CriteriaProfile'),('Validator','ValidatorReference')]:
  maps[part.lower()+'Digest']=lambda ref,part=part,s=s:'dOutside' if ref==domains[s][-1] else 'd'+part
  maps['receipt'+part+'Digest']=lambda r,part=part:maps[part.lower()+'Digest'](maps['receipt'+part](r))
  maps['event'+part]=lambda e,s=s:domains[s][-1] if e=='eventOutside' else domains[s][0]
 maps['eventEnvironment']=lambda e:'environmentreferenceOutside' if e=='eventOutside' else 'environmentreferenceA'
 maps['inputReference']=lambda i:'inputOutside' if i=='iOutside' else 'inputNew' if i=='iNew' else 'inputOld';maps['inputReferenceDigest']=lambda ref:'dOutside' if ref=='inputOutside' else 'dNew' if ref=='inputNew' else 'dOld';maps['inputDigest']=lambda i:'dOutside' if i=='iOutside' else 'dNew' if i=='iNew' else 'dOld';maps['recordedInputDigest']=lambda r,i:maps['inputDigest'](i)
 maps['outcomeEvent']=lambda o:'eventOutside' if o=='oOutside' else 'eventFull';maps['outcomeCheck']=lambda o:'cOutside' if o=='oOutside' else 'c0' if o in ['o0','oRepeated'] else 'c1' if o=='o1' else 'c2'
 maps['blockerCheck']=lambda blocker:'cOutside' if blocker=='causalblockerreferenceOutside' else 'c1';maps['observationReceipt']=lambda a:'rOutside' if a=='aOutside' else 'rFull';maps['observationContentDigest']=lambda a:'dOutside' if a=='aOutside' else 'dRecord'
 maps['comparisonReceipt']=lambda x:'rOutside' if x=='xOutside' else 'rFull';maps['comparisonOldInput']=lambda x:'iOutside' if x=='xOutside' else 'iOld';maps['comparisonNewInput']=lambda x:'iOutside' if x=='xOutside' else 'iNew'
 maps['recordComparisonReceipt']=lambda y:'rOutside' if y=='yOutside' else 'rIndependent' if y=='yIndependent' else 'rFull'
 for n in ['recordBeforeSubject','recordAfterSubject']:maps[n]=lambda y:'subjectreferenceOutside' if y=='yOutside' else 'subjectreferenceA'
 for n in ['recordBeforeAuthority','recordAfterAuthority']:maps[n]=lambda y:'authoritystateOutside' if y=='yOutside' else 'authoritystateA'
 for n in ['recordBeforeLifecycle','recordAfterLifecycle']:maps[n]=lambda y:'lifecyclestateOutside' if y=='yOutside' else 'lifecyclestateA'
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};selected=['rFull','rEmpty','rIndependent'];full=['rFull','rIndependent']
 for n in ['ReceiptApplicable','ReceiptInScopeDeclared','CompleteRecordDeclared']:predicates[n]=[[r] for r in selected]
 predicates['ReportedPASSDeclared']=[['rFull']]
 for n,s in b.FIELDS.items():predicates[s+'Declared']=[[x] for x in dict.fromkeys(maps[n](r) for r in selected)]
 for s in ['AuthorityEffect','InputOccurrence','InputReference','DeclaredCheck','OutcomeReference','EvidenceReference','CausalBlockerReference','Digest','AuthorityState','LifecycleState']:predicates[s+'Declared']=[[x] for x in domains[s] if x!=domains[s][-1]]
 # AuthorityEffect's final member is an outside effect; exact selected effect is NONE.
 predicates.update(EventInputDeclared=[['eventFull',i] for i in ['iOld','iRepeated']],ReceiptInputRecorded=[[r,i] for r in full for i in ['iOld','iRepeated']],EventCheckDeclared=[['eventFull',c] for c in ['c0','c1','c2']],EventOutcomeDeclared=[['eventFull',o] for o in ['o0','o1','o2']],ReceiptOutcomeRecorded=[[r,o] for r in full for o in ['o0','o1','o2']],CheckDependsOnDeclared=[['eventFull','c0','c1'],['eventFull','c1','c2']],EventEvidenceDeclared=[['eventFull','evidencereferenceA']],ReceiptEvidenceRecorded=[[r,'evidencereferenceA'] for r in full],EventBlockerDeclared=[['eventFull','causalblockerreferenceA']],ReceiptBlockerRecorded=[[r,'causalblockerreferenceA'] for r in full])
 for n in ['ObservationApplicable','ObservationInScopeDeclared']:predicates[n]=[['aFirst'],['aSecond']]
 for n in ['InputComparisonApplicable','InputComparisonInScopeDeclared','InputChangedDeclared']:predicates[n]=[['xChanged'],['xInvalid'],['xBoth']]
 predicates['BindingChangedDeclared']=[['xChanged'],['xBoth']];predicates['OldBindingInvalidatedDeclared']=[['xInvalid'],['xBoth']]
 for n in ['RecordOnlyComparisonApplicable','RecordOnlyComparisonInScopeDeclared']:predicates[n]=[['yStable'],['yIndependent']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-records-complete-chain-multiplicity-observations-and-both-change-strategies',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-Receipt-actual-'+n,lambda m,n=n:m['predicates']['ReceiptActual'+n].append(['rIndependent']),I=True)
 for prefix,member,actual in [('Observation','aSecond',b.OBS_ACTUAL),('InputComparison','xBoth',b.INPUT_ACTUAL),('RecordOnlyComparison','yIndependent',b.RECORD_ACTUAL)]:
  for n in actual:add('independent-'+prefix+'-actual-'+n,lambda m,n=n,prefix=prefix,member=member:m['predicates'][prefix+'Actual'+n].append([member]),I=True)
 for s,member in [('Receipt','rOutside'),('Observation','aOutside'),('InputComparison','xOutside'),('RecordOnlyComparison','yOutside')]:add('outside-empty-'+s+'-handle',lambda m,s=s,member=member:setfn(m,b.HANDLES[s],member,'empty'),I=True)
 add('outside-observation-different-content-unconstrained',lambda m:setfn(m,'observationContentDigest','aOutside','dNew'),I=True)
 add('outside-record-only-comparison-changed-authority',lambda m:setfn(m,'recordAfterAuthority','yOutside','authoritystateA'),I=True)
 add('repeated-receipt-identity-does-not-identify-events',lambda m:setfn(m,'receiptIdentity','rEmpty','idFull'),I=True)
 def repeated(m):
  m['predicates']['EventOutcomeDeclared'].append(['eventFull','oRepeated']);m['predicates']['ReceiptOutcomeRecorded'].extend([[r,'oRepeated'] for r in ['rFull','rIndependent']])
 add('multiple-outcomes-for-one-check-permitted',repeated,I=True)
 add('declared-dependency-cycle-does-not-imply-malformed-record',lambda m:m['predicates']['CheckDependsOnDeclared'].append(['eventFull','c2','c0']),I=True)
 add('declared-self-dependency-does-not-import-acyclic-policy',lambda m:m['predicates']['CheckDependsOnDeclared'].append(['eventFull','c0','c0']),I=True)
 add('reported-PASS-can-be-absent-with-complete-record',lambda m:m['predicates']['ReportedPASSDeclared'].clear(),I=False)
 add('input-change-can-declare-both-strategies',lambda m:m['predicates']['OldBindingInvalidatedDeclared'].append(['xChanged']),I=True)
 for n in ['ReceiptInScopeDeclared','CompleteRecordDeclared']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['rFull']),T=False)
 add('receipt-scope-declared-without-membership',lambda m:m['predicates']['ReceiptApplicable'].remove(['rFull']),T=False)
 for s in b.FIELDS.values():add('missing-selected-component-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 add('receipt-effect-other-than-NONE',lambda m:setfn(m,'receiptEffect','rFull','effectOther'),T=False)
 add('undeclared-selected-effect',lambda m:m['predicates']['AuthorityEffectDeclared'].clear(),T=False)
 for part in ['Subject','Profile','Validator','Environment']:add('event-record-'+part+'-mismatch',lambda m,part=part:setfn(m,'event'+part,'eventFull',m['domains'][b.FIELDS['receipt'+part]][-1]),T=False)
 for part in ['Subject','Profile','Validator']:add('recorded-'+part+'-digest-mismatch',lambda m,part=part:setfn(m,'receipt'+part+'Digest','rFull','dNew'),T=False)
 add('undeclared-selected-digest',lambda m:m['predicates']['DigestDeclared'].remove(['dSubject']),T=False)
 add('missing-recorded-input-occurrence',lambda m:m['predicates']['ReceiptInputRecorded'].remove(['rFull','iRepeated']),T=False)
 add('missing-event-input-but-record-still-includes-it',lambda m:m['predicates']['EventInputDeclared'].remove(['eventFull','iOld']),T=False)
 add('extra-unbound-receipt-input',lambda m:m['predicates']['ReceiptInputRecorded'].append(['rFull','iOutside']),T=False)
 add('input-occurrence-digest-does-not-match-exact-reference',lambda m:setfn(m,'inputReferenceDigest','inputOld','dNew'),T=False)
 add('new-input-occurrence-digest-does-not-match-exact-reference',lambda m:setfn(m,'inputDigest','iNew','dRecord'),T=False)
 add('recorded-input-digest-mismatch',lambda m:setfn(m,'recordedInputDigest',['rFull','iOld'],'dNew'),T=False)
 for s,member in [('InputOccurrence','iOld'),('InputReference','inputOld')]:add('undeclared-input-'+s,lambda m,s=s,member=member:m['predicates'][s+'Declared'].remove([member]),T=False)
 add('missing-dependent-check-outcome',lambda m:m['predicates']['ReceiptOutcomeRecorded'].remove(['rFull','o1']),T=False)
 add('missing-event-outcome-but-receipt-keeps-it',lambda m:m['predicates']['EventOutcomeDeclared'].remove(['eventFull','o1']),T=False)
 add('extra-unbound-receipt-outcome',lambda m:m['predicates']['ReceiptOutcomeRecorded'].append(['rFull','oOutside']),T=False)
 add('outcome-bound-to-wrong-event',lambda m:setfn(m,'outcomeEvent','o1','eventEmpty'),T=False)
 add('outcome-bound-to-undeclared-check',lambda m:setfn(m,'outcomeCheck','o1','cOutside'),T=False)
 add('missing-declared-check-record',lambda m:m['predicates']['EventCheckDeclared'].remove(['eventFull','c1']),T=False)
 add('new-declared-check-with-no-outcome',lambda m:m['predicates']['EventCheckDeclared'].append(['eventFull','cOutside']),T=False)
 add('dependency-endpoint-not-declared',lambda m:m['predicates']['CheckDependsOnDeclared'].append(['eventFull','c0','cOutside']),T=False)
 add('missing-recorded-evidence',lambda m:m['predicates']['ReceiptEvidenceRecorded'].remove(['rFull','evidencereferenceA']),T=False)
 add('extra-unbound-evidence',lambda m:m['predicates']['ReceiptEvidenceRecorded'].append(['rFull','evidencereferenceOutside']),T=False)
 add('missing-recorded-causal-blocker',lambda m:m['predicates']['ReceiptBlockerRecorded'].remove(['rFull','causalblockerreferenceA']),T=False)
 add('extra-unbound-causal-blocker',lambda m:m['predicates']['ReceiptBlockerRecorded'].append(['rFull','causalblockerreferenceOutside']),T=False)
 add('blocker-check-not-declared',lambda m:setfn(m,'blockerCheck','causalblockerreferenceA','cOutside'),T=False)
 for s in ['OutcomeReference','EvidenceReference','CausalBlockerReference','DeclaredCheck']:add('missing-member-declaration-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 for n in b.ROLES:add('Receipt-meaning-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['rFull']),T=False)
 handle_members={'Receipt':'rFull',**{s:base_model()['functions'][n][0]['value'] for n,s in b.FIELDS.items()},'AuthorityEffect':'effectNone','InputOccurrence':'iOld','InputReference':'inputOld','DeclaredCheck':'c1','OutcomeReference':'o1','EvidenceReference':'evidencereferenceA','CausalBlockerReference':'causalblockerreferenceA','Digest':'dSubject','Observation':'aFirst','InputComparison':'xChanged','RecordOnlyComparison':'yStable','AuthorityState':'authoritystateA','LifecycleState':'lifecyclestateA'}
 for s,member in handle_members.items():add('empty-selected-'+s+'-handle',lambda m,s=s,member=member:setfn(m,b.HANDLES[s],member,'empty'),T=False)
 for prefix,member in [('Observation','aFirst'),('InputComparison','xChanged'),('RecordOnlyComparison','yStable')]:
  add('missing-'+prefix+'-scope',lambda m,prefix=prefix,member=member:m['predicates'][prefix+'InScopeDeclared'].remove([member]),T=False)
  add(prefix+'-declared-without-membership',lambda m,prefix=prefix,member=member:m['predicates'][prefix+'Applicable'].remove([member]),T=False)
 add('selected-observation-bound-to-outside-receipt',lambda m:setfn(m,'observationReceipt','aFirst','rOutside'),T=False)
 add('same-receipt-observation-content-changed',lambda m:setfn(m,'observationContentDigest','aSecond','dNew'),T=False)
 add('input-comparison-bound-to-outside-receipt',lambda m:setfn(m,'comparisonReceipt','xChanged','rOutside'),T=False)
 add('comparison-old-input-not-in-original-receipt',lambda m:setfn(m,'comparisonOldInput','xChanged','iNew'),T=False)
 add('comparison-input-change-not-declared',lambda m:m['predicates']['InputChangedDeclared'].remove(['xChanged']),T=False)
 add('comparison-new-digest-not-changed',lambda m:setfn(m,'comparisonNewInput','xChanged','iRepeated'),T=False)
 add('changed-input-neither-changed-nor-invalidated-binding',lambda m:m['predicates']['BindingChangedDeclared'].remove(['xChanged']),T=False)
 add('invalidated-input-with-no-remaining-strategy',lambda m:m['predicates']['OldBindingInvalidatedDeclared'].remove(['xInvalid']),T=False)
 add('record-only-comparison-bound-to-outside-receipt',lambda m:setfn(m,'recordComparisonReceipt','yStable','rOutside'),T=False)
 for n in ['recordBeforeSubject','recordAfterSubject']:add('record-only-'+n+'-changed',lambda m,n=n:setfn(m,n,'yStable','subjectreferenceOutside'),T=False)
 add('record-only-authority-label-changed',lambda m:setfn(m,'recordAfterAuthority','yStable','authoritystateOutside'),T=False)
 add('record-only-lifecycle-label-changed',lambda m:setfn(m,'recordAfterLifecycle','yStable','lifecyclestateOutside'),T=False)
 for state in ['AuthorityState','LifecycleState']:add('missing-comparison-state-declaration-'+state,lambda m,state=state:m['predicates'][state+'Declared'].clear(),T=False)
 add('authority-comparison-uses-lifecycle-state',lambda m:setfn(m,'recordBeforeAuthority','yStable','lifecyclestateA'),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('ReceiptApplicable'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['receiptEvent'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(NONE='rFull'),error='ill-sorted-constant')
 add('wrong-membership-arity',lambda m:m['predicates'].update(ReceiptOutcomeRecorded=[['rFull']]),error='ill-sorted-model-tuple')
 add('duplicate-Receipt-tuple',lambda m:m['predicates']['ReceiptApplicable'].append(['rFull']),error='duplicate-predicate-tuple')
 add('empty-Observation-domain',lambda m:m['domains'].update(Observation=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['receiptEvent'].append(copy.deepcopy(m['functions']['receiptEvent'][0])),error='duplicate-function-tuple')
 add('duplicate-three-argument-dependency',lambda m:m['predicates']['CheckDependsOnDeclared'].append(['eventFull','c0','c1']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.validation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ValidationReceipt-model-controls/v1-candidate','status':'PASS-for-exact-authored-ValidationReceipt-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact Receipt,event/scalar/input records,complete declared membership and observation/input/record-only comparison guards checked on supplied models. Actual temporal immutability,storage,causal adequacy,Conformance,authority,owner fidelity and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
