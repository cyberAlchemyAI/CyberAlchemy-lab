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
