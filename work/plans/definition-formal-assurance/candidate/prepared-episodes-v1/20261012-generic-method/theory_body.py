SCOPE='scope:candidate:CAV2-D32-Method-explicit-form-field-identification-separate-decisions-v1'
SORTS=['MethodReference','ScopeReference','InputCollectionReference','ActionCollectionReference','RoleCollectionReference','GateCollectionReference','OutputCollectionReference','EvidenceCollectionReference','ResidueRuleReference','ValidationRuleReference','RecompositionRuleReference','BoundaryReference','MethodFormReference','FieldReference','AdmissionReference','ApplicationReference','DecisionReference','Token']
CONSTANTS={'EMPTY':'Token'}
METHOD_FIELDS={'methodScope':'ScopeReference','methodInputs':'InputCollectionReference','methodActions':'ActionCollectionReference','methodRoles':'RoleCollectionReference','methodGates':'GateCollectionReference','methodOutputs':'OutputCollectionReference','methodEvidence':'EvidenceCollectionReference','methodResidueRule':'ResidueRuleReference','methodValidationRule':'ValidationRuleReference','methodRecompositionRule':'RecompositionRuleReference','methodBoundary':'BoundaryReference'}
NAMED_FIELDS={'methodGenericForm':'MethodFormReference'}
ADMISSION_FIELDS={'admissionMethod':'MethodReference','admissionDecision':'DecisionReference'}
APPLICATION_FIELDS={'applicationMethod':'MethodReference','applicationDecision':'DecisionReference'}
GROUPS=[(METHOD_FIELDS,'MethodReference'),(NAMED_FIELDS,'MethodReference'),(ADMISSION_FIELDS,'AdmissionReference'),(APPLICATION_FIELDS,'ApplicationReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
METHOD_EXCLUDED=['MethodIsOneOffTaskDeclared','MethodIsTechniqueDeclared','MethodIsChecklistDeclared','MethodIsEngineDeclared','MethodIsPipelineDeclared','MethodIsLifecycleLabelDeclared','MethodIsProductDeclared','MethodIsProjectDeclared','MethodIsGoalDeclared','MethodIsAuthorityGrantDeclared','MethodIsWorkflowDeclared','MethodIdentityGrantsExecutionDeclared','NamedMethodInheritsExecutionAuthorityDeclared']
ADMISSION_EXCLUDED=['AdmissionIsApplicationDeclared','AdmissionRecordExecutesMethodDeclared']
APPLICATION_EXCLUDED=['ApplicationIsAdmissionDeclared','ApplicationIdentityGrantsExecutionDeclared']
METHOD_ACTUAL=['GovernedRepeatability','TransformationFidelity','ScopeFidelity','InputCollectionFidelity','ActionCollectionFidelity','RoleCollectionFidelity','GateCollectionFidelity','OutputCollectionFidelity','EvidenceCollectionFidelity','ResidueRuleAdequacy','ValidationRuleAdequacy','RecompositionRuleAdequacy','BoundaryFidelity','FieldIdentifiability','SpecializationFidelity','AdmissionApplicationSeparation','ExecutionPermission','Execution','ValidationSuccess','ResiduePreservation','RecompositionSuccess','SourceFidelity','Authority','WholeProof']
ADMISSION_ACTUAL=['MethodAdmissionValidity','DecisionValidity','Permission','Authority','Proof']
APPLICATION_ACTUAL=['ApplicationValidity','DecisionValidity','Permission','Execution','OutputSuccess','ValidationSuccess','ResiduePreservation','RecompositionSuccess','BoundaryConformance','Authority']
PRIMARY=[('Method','MethodReference',METHOD_EXCLUDED,METHOD_ACTUAL),('Admission','AdmissionReference',ADMISSION_EXCLUDED,ADMISSION_ACTUAL),('Application','ApplicationReference',APPLICATION_EXCLUDED,APPLICATION_ACTUAL)]
TRANSFORMS=['MethodTransformsIntentDeclared','MethodTransformsEvidenceDeclared','MethodTransformsStateDeclared','MethodTransformsResidueDeclared']
FLAGS={'Method':['MethodApplicable','MethodInScopeDeclared','MethodGovernedRepeatableTransformationDeclared','MethodNamedDeclared']+TRANSFORMS,'Admission':['AdmissionApplicable','AdmissionInScopeDeclared','AdmissionDecisionRoleDeclared'],'Application':['ApplicationApplicable','ApplicationInScopeDeclared','ApplicationDecisionRoleDeclared']}
SIGNATURE={}
for prefix,sort,excluded,actual in PRIMARY:SIGNATURE.update({n:[sort] for n in FLAGS[prefix]+excluded+[prefix+'Actual'+n for n in actual]})
for sort in SORTS:
 if sort not in [x[1] for x in PRIMARY]+['Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'MethodSpecializesFormDeclared':['MethodReference','MethodFormReference'],'FormMinimumCoordinatesDeclared':['MethodFormReference'],'MethodReusableFieldDeclared':['MethodReference','FieldReference'],'MethodSpecializedFieldDeclared':['MethodReference','FieldReference'],'MethodFieldIdentifiableDeclared':['MethodReference','FieldReference'],'AdmissionDecisionForMethodDeclared':['DecisionReference','MethodReference'],'ApplicationDecisionForMethodDeclared':['DecisionReference','MethodReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
M=var('m');A=var('a');P=var('p');F=var('f')
MAP={'MethodReference':'MethodApplicable','AdmissionReference':'AdmissionApplicable','ApplicationReference':'ApplicationApplicable'}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,name,z):return allof([(sort,name)],implies(pred(member(sort),name),z))
def eligible(prefix,sort,name):return allof([(sort,name)],iff(pred(prefix+'Applicable',name),pred(prefix+'InScopeDeclared',name)))
MAPP=pred('MethodApplicable',M);AAPP=pred('AdmissionApplicable',A);PAPP=pred('ApplicationApplicable',P)
ROOT_RULE=both(eligible('Method','MethodReference','m'),selected('MethodReference','m',both(guard('MethodReference',M),exact(METHOD_FIELDS,M),pred('MethodGovernedRepeatableTransformationDeclared',M),either(*[pred(n,M) for n in TRANSFORMS]))))
FORM=fn('methodGenericForm',M)
NAMED_RULE=selected('MethodReference','m',implies(pred('MethodNamedDeclared',M),both(exact(NAMED_FIELDS,M),pred('FormMinimumCoordinatesDeclared',FORM),pred('MethodSpecializesFormDeclared',M,FORM))))
IDENTIFIABILITY_RULE=selected('MethodReference','m',allof([('FieldReference','f')],implies(either(pred('MethodReusableFieldDeclared',M,F),pred('MethodSpecializedFieldDeclared',M,F)),both(guard('FieldReference',F),pred('MethodFieldIdentifiableDeclared',M,F)))))
ADM=fn('admissionMethod',A);AD=fn('admissionDecision',A);APM=fn('applicationMethod',P);APD=fn('applicationDecision',P)
ADMISSION_RULE=both(eligible('Admission','AdmissionReference','a'),selected('AdmissionReference','a',both(guard('AdmissionReference',A),exact(ADMISSION_FIELDS,A),pred('AdmissionDecisionRoleDeclared',A),pred('AdmissionDecisionForMethodDeclared',AD,ADM))))
APPLICATION_RULE=both(eligible('Application','ApplicationReference','p'),selected('ApplicationReference','p',both(guard('ApplicationReference',P),exact(APPLICATION_FIELDS,P),pred('ApplicationDecisionRoleDeclared',P),pred('ApplicationDecisionForMethodDeclared',APD,APM))))
DECISION_SEPARATION_RULE=allof([('AdmissionReference','a'),('ApplicationReference','p')],implies(both(AAPP,PAPP),neg(eq(AD,APD))))
BOUNDARIES=both(*[selected(sort,name,both(*[neg(pred(n,name)) for n in excluded])) for (prefix,sort,excluded,actual),name in zip(PRIMARY,['m','a','p'])])
THEORY={'root':ROOT_RULE,'named-specialization':NAMED_RULE,'field-identifiability':IDENTIFIABILITY_RULE,'admission':ADMISSION_RULE,'application':APPLICATION_RULE,'separate-decisions':DECISION_SEPARATION_RULE,'boundaries':BOUNDARIES}
LOSSES=[
'Exact C29 generic Method Definition admission does not accept this translation,admit a Method instance,apply it or grant execution authority.',
'CAV2-D32 generic Method and CAV2-D20 Craft Method retain separate identities,eleven-field forms and qualified meanings.',
'The eleven minimum fields are explicit typed nominations,not an executed workflow,engine,pipeline or complete operational state machine.',
'Plural inputs,actions,roles,gates,outputs and evidence nominate collection specifications;no element/cardinality/nonempty-member or disjoint-content assumptions are invented.',
'Declared intent,evidence,state and residue transformation alternatives are inclusive;no exactly-one partition or every-Method-transforms-everything rule is imposed.',
'Governed repeatability is a necessary declaration;actual reusable operation,validation and successful outputs remain independent.',
'Named Methods nominate the minimum generic form and declared specialization;no actual specialization fidelity or inherited execution authority follows.',
'An unnamed generic Method leaves its unused specialization field unbound without a fabricated named Method or form record.',
'Reusable and specialized field references must be identifiable when selected;real field names,coordinate-to-field maps and content fidelity remain pending.',
'Reusable and specialized roles may overlap,and unclassified additional fields are not forbidden;the source does not require a disjoint exhaustive partition.',
'Admission and application records nominate their own Methods and decisions;actual owner validity,admission,application and permission remain separate.',
'Selected admission and application decision references are separated across the two roles;reuse within a role is not forbidden and actual batching/owner maps remain pending.',
'An application need not fabricate a selected admission record or claim execution,and a Method specification need not fabricate either record.',
'Residue,validation,recomposition and boundary rules are present as typed nominations;actual adequacy,continuity and conformance remain unproved.',
'Methods remain separate from one-off tasks,techniques,checklists,lifecycle labels,Products,Projects,Goals,workflows,engines,pipelines and authority grants.',
'The nonnormative example that a Method may use tools/workflows is explanatory;no universal tool prohibition is invented from it.',
'C29 positive semantic foundation effects and later C30/C31 type/carrier/identity conformance admissions retain separate scopes without accepting this formal translation.',
'Source-body candidate admission labels and historical chain evidence remain separate from current C29 exact scoped source-use admission.',
'Relocated external selected lines2114-2180 match their bound digest;wholefile drift and path relocation do not transfer private meaning or legacy authority.',
'Current Method Binding and related carrier meanings need separately accepted source-to-form,field,decision,role,evidence,residue,validation and application maps.',
'Complete source accounting and finite T/I witnesses do not establish common denotations,source fidelity,whole translation,whole proof or episode completion.'
]
def required_populations():
 def w(sort,name,z):return exists([(sort,name)],both(pred(member(sort),name),z))
 def field(z):return exists([('MethodReference','m'),('FieldReference','f')],both(MAPP,z))
 return {'Method':('MethodReference',w('MethodReference','m',MAPP)),'OutsideMethod':('MethodReference',exists([('MethodReference','m')],neg(MAPP))),'NamedMethod':('MethodReference',w('MethodReference','m',pred('MethodNamedDeclared',M))),'GenericUnnamedMethod':('MethodReference',w('MethodReference','m',neg(pred('MethodNamedDeclared',M)))),**{n:('MethodReference',w('MethodReference','m',pred(n,M))) for n in TRANSFORMS},'ReusableField':('FieldReference',field(pred('MethodReusableFieldDeclared',M,F))),'SpecializedField':('FieldReference',field(pred('MethodSpecializedFieldDeclared',M,F))),'BothFieldRoles':('FieldReference',field(both(pred('MethodReusableFieldDeclared',M,F),pred('MethodSpecializedFieldDeclared',M,F)))),'AdditionalUnclassifiedField':('FieldReference',field(both(pred('FieldReferenceDeclared',F),neg(pred('MethodReusableFieldDeclared',M,F)),neg(pred('MethodSpecializedFieldDeclared',M,F))))),'Admission':('AdmissionReference',w('AdmissionReference','a',AAPP)),'OutsideAdmission':('AdmissionReference',exists([('AdmissionReference','a')],neg(AAPP))),'Application':('ApplicationReference',w('ApplicationReference','p',PAPP)),'OutsideApplication':('ApplicationReference',exists([('ApplicationReference','p')],neg(PAPP))),'ApplicationWithoutSelectedAdmission':('ApplicationReference',w('ApplicationReference','p',neg(exists([('AdmissionReference','a')],both(AAPP,eq(ADM,APM)))))),'AdmissionApplicationSameMethodSeparateDecisions':('ApplicationReference',exists([('AdmissionReference','a'),('ApplicationReference','p')],both(AAPP,PAPP,eq(ADM,APM),neg(eq(AD,APD))))),'IndependentAuthority':('MethodReference',w('MethodReference','m',pred('MethodActualAuthority',M))),'MethodWithoutActualOutcomes':('MethodReference',w('MethodReference','m',both(*[neg(pred('MethodActual'+n,M)) for n in METHOD_ACTUAL]))),'NamedWithoutActualSpecialization':('MethodReference',w('MethodReference','m',both(pred('MethodNamedDeclared',M),neg(pred('MethodActualSpecializationFidelity',M))))),'ApplicationWithoutActualExecution':('ApplicationReference',w('ApplicationReference','p',neg(pred('ApplicationActualExecution',P))))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for (prefix,sort,excluded,names),vn in zip(PRIMARY,['m','a','p']):
  value=var(vn);app=pred(prefix+'Applicable',value)
  for n in names:
   scope=both(app,pred('MethodNamedDeclared',value)) if prefix=='Method' and n=='SpecializationFidelity' else app;label='named-Method-specialization' if prefix=='Method' and n=='SpecializationFidelity' else 'selected-'+prefix.lower();target=pred(prefix+'Actual'+n,value)
   rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,vn)],implies(scope,target)),'witness_condition':exists([(sort,vn)],both(scope,neg(target))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(ROOT_RULE,['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,IDENTIFIABILITY_RULE),['operational']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(IDENTIFIABILITY_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/1':(both(ADMISSION_RULE,APPLICATION_RULE,DECISION_SEPARATION_RULE),['operational']),'/voices/scientific_formal/testable_conditions/0':(ROOT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(ROOT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(BOUNDARIES,['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(BOUNDARIES,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows
