"""Finite generic Method specifications,overlapping field roles and separate decision models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+'0',sort[0].lower()+sort[1:]+'1',sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS};ds.update(MethodReference=['m0','m1','mOutside'],MethodFormReference=['form0','form1','formOutside'],FieldReference=['f0','f1','f2','f3','f4','fOutside'],AdmissionReference=['a0','a1','aOutside'],ApplicationReference=['p0','p1','pOutside'],DecisionReference=['d0','d1','d2','dOutside'],Token=['empty','ref','other']);maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,sort in b.METHOD_FIELDS.items():table(n,{'m0':ds[sort][0],'m1':ds[sort][1]})
 table('methodGenericForm',{'m1':'form0'});table('admissionMethod',{'a0':'m0','a1':'m0'});table('admissionDecision',{'a0':'d0','a1':'d0'});table('applicationMethod',{'p0':'m0','p1':'m1'});table('applicationDecision',{'p0':'d1','p1':'d2'})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in [x[1] for x in b.PRIMARY]+['Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['MethodApplicable','MethodInScopeDeclared','MethodGovernedRepeatableTransformationDeclared']:preds[n]=[['m0'],['m1']]
 preds['MethodNamedDeclared']=[['m1']];preds['MethodTransformsIntentDeclared']=[['m0']];preds['MethodTransformsEvidenceDeclared']=[['m0']];preds['MethodTransformsStateDeclared']=[['m1']];preds['MethodTransformsResidueDeclared']=[['m1']]
 for n in b.FLAGS['Admission']:preds[n]=[['a0']]
 for n in b.FLAGS['Application']:preds[n]=[['p0'],['p1']]
 preds['MethodSpecializesFormDeclared']=[['m1','form0']];preds['FormMinimumCoordinatesDeclared']=[['form0']]
 preds['MethodReusableFieldDeclared']=[['m0','f0'],['m1','f1'],['m1','f3']];preds['MethodSpecializedFieldDeclared']=[['m1','f2'],['m1','f3']];preds['MethodFieldIdentifiableDeclared']=[['m0','f0'],['m1','f1'],['m1','f2'],['m1','f3']]
 preds['AdmissionDecisionForMethodDeclared']=[['d0','m0']];preds['ApplicationDecisionForMethodDeclared']=[['d1','m0'],['d2','m1']];preds['MethodActualAuthority']=[['m1']]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-eleven-field-Method-overlapping-roles-separate-decisions')
 add('no-selected-Method-admission-application',lambda m:m['predicates'].update({prefix+suffix:[] for prefix,sort,e,a in b.PRIMARY for suffix in ['Applicable','InScopeDeclared']}),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(MethodActualAuthority=[]),I=False)
 add('no-admission-records-application-does-not-fabricate-one',lambda m:m['predicates'].update(AdmissionApplicable=[],AdmissionInScopeDeclared=[]),I=False)
 add('no-application-records-Method-does-not-fabricate-one',lambda m:m['predicates'].update(ApplicationApplicable=[],ApplicationInScopeDeclared=[]),I=False)
 add('no-field-role-records-Method-still-has-explicit-tuple',lambda m:m['predicates'].update(MethodReusableFieldDeclared=[],MethodSpecializedFieldDeclared=[]),I=False)
 for (prefix,sort,excluded,names),target in zip(b.PRIMARY,['m1','a0','p0']):
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
  for n in excluded:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   outside=base_model()['domains'][sort][-1];add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('unnamed-Method-unused-form-binding-absent',lambda m:m['predicates'].update(methodGenericFormBindingDeclared=[x for x in m['predicates']['methodGenericFormBindingDeclared'] if x[0]!='m0']))
 add('unused-form-handle-empty',lambda m:setfn(m,b.HANDLES['MethodFormReference'],'formOutside','empty'))
 add('unclassified-additional-field-handle-unused',lambda m:setfn(m,b.HANDLES['FieldReference'],'f4','empty'))
 add('outside-Method-field-role-not-a-selected-obligation',lambda m:m['predicates']['MethodReusableFieldDeclared'].append(['mOutside','fOutside']))
 add('overlap-field-roles-remain-valid',lambda m:None)
 add('no-exclusive-transformation-alternative',lambda m:m['predicates']['MethodTransformsStateDeclared'].append(['m0']))
 def same_role(m):
  for n in b.FLAGS['Admission']:m['predicates'][n].append(['a1'])
 add('same-role-admission-decision-reuse-not-forbidden',same_role)
 add('separate-decisions-required-even-across-different-Methods',lambda m:change(m,'applicationDecision','p1','d0'),T=False,I=None)
 add('same-Method-admission-application-decision-collapse',lambda m:change(m,'applicationDecision','p0','d0'),T=False,I=None)
 add('named-specialization-missing',lambda m:m['predicates']['MethodSpecializesFormDeclared'].remove(['m1','form0']),T=False,I=None)
 add('minimum-form-coordinates-missing',lambda m:m['predicates']['FormMinimumCoordinatesDeclared'].remove(['form0']),T=False,I=None)
 add('reusable-field-not-identifiable',lambda m:m['predicates']['MethodFieldIdentifiableDeclared'].remove(['m0','f0']),T=False,I=None)
 add('specialized-field-not-identifiable',lambda m:m['predicates']['MethodFieldIdentifiableDeclared'].remove(['m1','f2']),T=False,I=None)
 add('marked-field-undeclared',lambda m:m['predicates']['FieldReferenceDeclared'].remove(['f0']),T=False,I=None)
 add('marked-field-empty-handle',lambda m:setfn(m,b.HANDLES['FieldReference'],'f0','empty'),T=False,I=None)
 add('no-declared-transformation-alternative',lambda m:m['predicates'].update({n:[x for x in m['predicates'][n] if x[0]!='m0'] for n in b.TRANSFORMS}),T=False,I=None)
 for n,arg in [('MethodGovernedRepeatableTransformationDeclared','m0'),('AdmissionDecisionRoleDeclared','a0'),('ApplicationDecisionRoleDeclared','p0')]:add('missing-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,row in [('AdmissionDecisionForMethodDeclared',['d0','m0']),('ApplicationDecisionForMethodDeclared',['d1','m0'])]:add('missing-exact-'+n,lambda m,n=n,row=row:m['predicates'][n].remove(row),T=False,I=None)
 targets=[(b.METHOD_FIELDS,'m0'),(b.NAMED_FIELDS,'m1'),(b.ADMISSION_FIELDS,'a0'),(b.APPLICATION_FIELDS,'p0')]
 for fields,arg in targets:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value);add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][b.member(sort)].remove([value]),T=False,I=None)
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=base_model()['domains'][sort][0]:setfn(m,n,value,'empty'),T=False,I=None)
 for name,mutate,code in [('empty-domain',lambda m:m['domains'].update(MethodReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('ApplicationReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('methodScope'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['methodScope'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'methodScope','m0','foreign'),'ill-sorted-function-result'),('function-argument',lambda m:m['functions']['methodScope'][0].update(args=['foreign']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['MethodApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('predicate-arity',lambda m:m['predicates']['MethodSpecializesFormDeclared'].append(['m1']),'ill-sorted-model-tuple')]:add('malformed-'+name,mutate,error=code)
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
    prior=json.loads((b.BASE/'definitions/CAV2-D20/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-GenericMethod-model-controls/v1-candidate','status':'PASS-for-exact-authored-GenericMethod-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary generic Method eleven-field/collection/field-identification/named-form/separate-decision declarations checked on supplied models;actual repeatability,application,permission,validation,field fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
