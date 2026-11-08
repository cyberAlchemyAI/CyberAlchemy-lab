"""Exact CAV2-D32 generic Method explicit specification,field roles and separate decisions."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
def var(n):return {'op':'var','name':n}
def const(n):return {'op':'const','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return either(neg(a),z)
def eq(a,z):return {'op':'eq','left':a,'right':z}
def bind(bindings,body):
 for op,sort,name in reversed(bindings):body={'op':op,'sort':sort,'var':name,'body':body}
 return body
def allof(bindings,body):return bind([('forall',sort,name) for sort,name in bindings],body)
def exists(bindings,body):return bind([('exists',sort,name) for sort,name in bindings],body)
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,sort_keys=True,separators=(',',':'));out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input '+x['path'])
def external_current(context):
 for x in context['external_sources']:
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('External source drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
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
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary generic Method eleven-field collection-specification,named-form,field-identification and separate decision declarations. Actual repeatability,application,permission,rule adequacy and authority remain independent.','explanatory':'Notation,plain-language intuition and domain examples are explanatory;no actual Method application or authority inferred.','deferred':'The authority-scope map and candidate migration ceiling remain explicit unresolved source obligations.'}
 for row in selected_clauses(doc):
  cid='GMD-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent Method,named specialization,field roles,admission and application population obligations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity and owner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CAV2-D32-Method-explicit-form-field-identification-separate-decisions-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'GMD-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Method,Product,Project,Goal,role,gate,evidence,residue,validation and application owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no prior whole theory or accepted source/consumer map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'explicit-generic-and-named-Methods-separate-decisions','scenario':'Two Method specifications supply eleven typed coordinates. One named Method specializes the minimum form. Reusable and specialized field roles overlap. One admission and two application records have separate decisions;one application has no selected admission record.','expected_interpretation':'Necessary declarations hold without actual repeatability,application,validation,permission,field fidelity or authority inferred.','rationale':'Specifications,roles,collections,admission and application remain independent.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'admission-application-decision-collapse','scenario':'An application record uses the selected admission decision reference.','expected_interpretation':'The declaration-level decision separation fails.','rationale':'Method admission and application are separate decisions.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}

 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});query_ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Method-not-ActualSourceFidelity','Method-not-ActualAuthority']
  if clause['source_selector'] in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:targets+=['Method-not-ActualGovernedRepeatability','Method-not-ActualSpecializationFidelity','Application-not-ActualExecution']
  if 'boundary' in clause['source_selector']:targets+=['Method-not-ActualAdmissionApplicationSeparation','Application-not-ActualPermission']
  if 'testable_conditions' in clause['source_selector']:targets+=['Method-not-ActualInputCollectionFidelity','Method-not-ActualResidueRuleAdequacy','Application-not-ActualValidationSuccess']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in query_ids,target
   obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'eleven-distinct-typed-coordinate-nominations-with-plural-collection-specifications','named':'conditional-exact-generic-form-and-minimum-coordinate-specialization','field_roles':'conditional-identifiability-with-overlap-and-unclassified-fields-permitted','decisions':'separate-selected-admission-application-decision-references-with-no-fabricated-unused-record','transformations':'inclusive-intent-evidence-state-residue-declared-alternatives','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary Method specification,field identification and separate decision declarations only;actual repeatability,application,permission,rule adequacy,owner authority,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
