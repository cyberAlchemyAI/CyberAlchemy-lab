"""Planned supplied controls for exact-time dimensional comparison declarations."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 suffixes=[*b.DIMENSIONS,'Later','Outside'];assessments=['a'+n for n in suffixes];slots=['s'+n for n in suffixes];sets=['es'+n for n in suffixes];items=['e'+n for n in suffixes];dims=['dim'+n for n in b.DIMENSIONS];values=['v'+n+k for n in b.DIMENSIONS for k in ['Declared','Observed']];subjects=['subject','outsideSubject'];scopes=['scope','outsideScope'];times=['time','laterTime','outsideTime'];owners=['owner','outsideOwner'];by_suffix=lambda x:x.removeprefix('a').removeprefix('s').removeprefix('es').removeprefix('e')
 def dim_name(x):
  for n in suffixes:
   if x in ['a'+n,'s'+n,'es'+n,'e'+n]:return 'Version' if n in ['Later','Outside'] else n
  raise ValueError(x)
 def selected(x,main,outside):return outside if x.endswith('Outside') else main
 def time(x):return 'outsideTime' if x.endswith('Outside') else 'laterTime' if x.endswith('Later') else 'time'
 domains={'Assessment':assessments,'Subject':subjects,'Scope':scopes,'Time':times,'Dimension':dims,'ComparisonSlot':slots,'Value':values,'EvidenceSet':sets,'Evidence':items,'Owner':owners,'Token':['empty','reference','same-label']}
 maps={'assessmentSubject':lambda a:selected(a,'subject','outsideSubject'),'assessmentScope':lambda a:selected(a,'scope','outsideScope'),'assessmentTime':time,'assessmentEvidenceSet':lambda a:'es'+a[1:],'assessmentOwner':lambda a:selected(a,'owner','outsideOwner'),'assessmentHandle':lambda a:'reference','subjectHandle':lambda s:'same-label','scopeHandle':lambda q:'reference','timeHandle':lambda t:'reference','ownerHandle':lambda o:'reference','evidenceSetHandle':lambda e:'reference','evidenceHandle':lambda e:'reference','slotAssessment':lambda s:'a'+s[1:],'slotSubject':lambda s:selected(s,'subject','outsideSubject'),'slotScope':lambda s:selected(s,'scope','outsideScope'),'slotTime':time,'slotDimension':lambda s:'dim'+dim_name(s),'slotDeclaredValue':lambda s:'v'+dim_name(s)+'Declared','slotObservedValue':lambda s:'v'+dim_name(s)+('Declared' if s=='sCondition' else 'Observed'),'slotHandle':lambda s:'reference','valueDimension':lambda value:next('dim'+n for n in b.DIMENSIONS if value in ['v'+n+'Declared','v'+n+'Observed']),'valueHandle':lambda value:'same-label','evidenceSetSubject':lambda e:selected(e,'subject','outsideSubject'),'evidenceSetScope':lambda e:selected(e,'scope','outsideScope'),'evidenceSetTime':time,'evidenceSubject':lambda e:selected(e,'subject','outsideSubject'),'evidenceScope':lambda e:selected(e,'scope','outsideScope'),'evidenceTime':time}
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};active=assessments[:-1]
 for n in ['DriftAssessment','AssessmentRecordDeclared','ComparisonDeclared','GovernedIdentityOrRecord']:predicates[n]=[[a] for a in active]
 predicates.update(SubjectDeclared=[['subject']],BoundedScopeDeclared=[['scope']],ExactTimeDeclared=[['time'],['laterTime']],OwnerDeclared=[['owner']],EvidenceSetDeclared=[[e] for e in sets[:-1]],SlotDeclared=[[s] for s in slots[:-1]],ValueDeclared=[[value] for value in values],MismatchDeclared=[[s] for s in slots[:-1] if s!='sCondition'],SlotIncluded=[[a,s] for a,s in zip(active,slots[:-1])],EvidenceMember=[[es,e] for es,e in zip(sets[:-1],items[:-1])],EvidenceBearsOnSlot=[[e,s] for e,s in zip(items[:-1],slots[:-1])])
 constants={'EMPTY':'empty',**{'DIM_'+n.upper():'dim'+n for n in b.DIMENSIONS}}
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('six-dimensions-exact-time-matched-and-mismatched',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['aVersion']),I=True)
 add('same-reference-labels-do-not-collapse-values',lambda m:None,I=True)
 add('outside-slot-time-map-not-governing',lambda m:setfn(m,'slotTime','sOutside','laterTime'),I=True)
 add('unrelated-included-evidence-does-not-replace-selected-witness',lambda m:m['predicates']['EvidenceMember'].append(['esVersion','eOutside']),I=True)
 for n in ['AssessmentRecordDeclared','ComparisonDeclared','GovernedIdentityOrRecord']:add('missing-assessment-'+n,lambda m,n=n:m['predicates'][n].remove(['aVersion']),T=False)
 for n,value in [('SubjectDeclared','subject'),('BoundedScopeDeclared','scope'),('ExactTimeDeclared','time'),('OwnerDeclared','owner'),('EvidenceSetDeclared','esVersion')]:add('missing-selected-'+n,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 for n,arg in [('assessmentHandle','aVersion'),('subjectHandle','subject'),('scopeHandle','scope'),('timeHandle','time'),('ownerHandle','owner'),('evidenceSetHandle','esVersion')]:add('missing-handle-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,value in [('evidenceSetSubject','outsideSubject'),('evidenceSetScope','outsideScope'),('evidenceSetTime','laterTime')]:add('wrong-selected-'+n,lambda m,n=n,value=value:setfn(m,n,'esVersion',value),T=False)
 add('assessment-without-included-comparison-slot',lambda m:m['predicates']['SlotIncluded'].remove(['aVersion','sVersion']),T=False)
 add('slot-not-declared',lambda m:m['predicates']['SlotDeclared'].remove(['sVersion']),T=False)
 for n,value in [('slotAssessment','aCondition'),('slotSubject','outsideSubject'),('slotScope','outsideScope'),('slotTime','laterTime')]:add('wrong-slot-'+n,lambda m,n=n,value=value:setfn(m,n,'sVersion',value),T=False)
 for value in ['vVersionDeclared','vVersionObserved']:add('missing-declared-comparison-value-'+value,lambda m,value=value:m['predicates']['ValueDeclared'].remove([value]),T=False)
 for value in ['vVersionDeclared','vVersionObserved']:add('wrong-comparison-value-dimension-'+value,lambda m,value=value:setfn(m,'valueDimension',value,'dimCondition'),T=False)
 for n,arg in [('slotHandle','sVersion'),('valueHandle','vVersionDeclared'),('valueHandle','vVersionObserved')]:add('missing-slot-or-value-handle-'+n+'-'+arg,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,args in [('EvidenceMember',['esVersion','eVersion']),('EvidenceBearsOnSlot',['eVersion','sVersion'])]:add('comparison-without-'+n,lambda m,n=n,args=args:m['predicates'][n].remove(args),T=False)
 for n,value in [('evidenceSubject','outsideSubject'),('evidenceScope','outsideScope'),('evidenceTime','laterTime')]:add('wrong-supporting-'+n,lambda m,n=n,value=value:setfn(m,n,'eVersion',value),T=False)
 add('supporting-evidence-without-handle',lambda m:setfn(m,'evidenceHandle','eVersion','empty'),T=False)
 add('mismatch-label-absent-on-unequal-mapped-values',lambda m:m['predicates']['MismatchDeclared'].remove(['sVersion']),T=False)
 add('mismatch-label-on-equal-mapped-values',lambda m:m['predicates']['MismatchDeclared'].append(['sCondition']),T=False)
 def extra_slot(m):m['predicates']['SlotIncluded'].append(['aVersion','sOutside'])
 add('extra-comparison-with-wrong-bindings-and-no-evidence',extra_slot,T=False)
 def retire(m,a):
  for n in ['DriftAssessment','AssessmentRecordDeclared','ComparisonDeclared']:m['predicates'][n].remove([a])
 add('no-matched-example-T-does-not-imply-witness-policy',lambda m:retire(m,'aCondition'),I=False)
 add('no-currentness-dimension-example-T-does-not-imply-witness-policy',lambda m:retire(m,'aCurrentness'),I=False)
 add('no-later-time-example-T-does-not-imply-witness-policy',lambda m:retire(m,'aLater'),I=False)
 add('missing-total-time-function-entry',lambda m:m['functions']['assessmentTime'].pop(),error='nontotal-function')
 add('ill-sorted-declared-value-result',lambda m:setfn(m,'slotDeclaredValue','sVersion','time'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='vVersionDeclared'),error='ill-sorted-constant')
 add('wrong-evidence-membership-arity',lambda m:m['predicates'].update(EvidenceMember=[['esVersion']]),error='ill-sorted-model-tuple')
 add('duplicate-slot-inclusion-tuple',lambda m:m['predicates']['SlotIncluded'].append(['aVersion','sVersion']),error='duplicate-predicate-tuple')
 add('empty-comparison-slot-domain',lambda m:m['domains'].update(ComparisonSlot=[]),error='empty-or-malformed-domain')
 add('duplicate-subject-function-tuple',lambda m:m['functions']['assessmentSubject'].append(copy.deepcopy(m['functions']['assessmentSubject'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.conformance/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-DriftAssessment-model-controls/v1-candidate','status':'PASS-for-exact-authored-DriftAssessment-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact subject/scope/time/dimension declared/observed comparison slots and included evidence bindings checked on supplied models. Mismatch labels do not create actual mismatch validity,cause,severity,failure,correction authority or required remediation. Actual time/values/evidence adequacy,consumer/carrier maps,source-owner fidelity and common denotations remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
