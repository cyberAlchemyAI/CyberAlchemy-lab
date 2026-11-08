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
