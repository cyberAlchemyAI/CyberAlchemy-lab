"""Prepared Capability Instance source-qualified tuple,owner,contexts,claims and recursion guards."""
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

# Prepared source code only. Assemble/evaluate after Project full seal and audit.
SCOPE='scope:candidate:CapabilityInstance-exact-parent-owner-context-claims-recursion-handoff-v1'
SORTS=['InstanceReference','IdentityReference','ProductCapabilityVersionReference','ProductCapabilityReference','CoordinationContextReference','BoundedContextCollectionReference','BoundedContextReference','AuthorityClaimReference','AuthorityLaneReference','InheritedContractReference','ExtensionScopeReference','AdoptionDecisionReference','ConstructionBindingReference','ConformanceCollectionReference','LifecycleReference','DriftRouteReference','RecompositionRouteReference','RecursionContractReference','TerminalHandoffReference','LocalOwnerReference','BudgetReference','StopRuleReference','Token']
CONSTANTS={'EMPTY':'Token','PARENT_LANE':'AuthorityLaneReference','INSTANCE_LANE':'AuthorityLaneReference'}
INSTANCE_FIELDS={
'instanceIdentity':'IdentityReference',
'instanceCapabilityVersion':'ProductCapabilityVersionReference',
'instanceCoordinationContext':'CoordinationContextReference',
'instanceBoundedContexts':'BoundedContextCollectionReference',
'instanceParentAuthorityClaim':'AuthorityClaimReference',
'instanceAuthorityClaim':'AuthorityClaimReference',
'instanceInheritedContract':'InheritedContractReference',
'instanceExtensionScope':'ExtensionScopeReference',
'instanceAdoptionDecision':'AdoptionDecisionReference',
'instanceConstructionBinding':'ConstructionBindingReference',
'instanceConformanceRefs':'ConformanceCollectionReference',
'instanceLifecycle':'LifecycleReference',
'instanceDriftRoute':'DriftRouteReference',
'instanceRecompositionRoute':'RecompositionRouteReference',
'instanceRecursionContract':'RecursionContractReference',
'instanceTerminalHandoff':'TerminalHandoffReference'}
OWNER_FIELDS={'instanceLocalOwner':'LocalOwnerReference'}
LANE_FIELDS={'instanceParentLane':'AuthorityLaneReference','instanceLocalLane':'AuthorityLaneReference'}
VERSION_FIELDS={'versionParentCapability':'ProductCapabilityReference'}
PARENT_FIELDS={'parentCapabilityIdentity':'IdentityReference'}
RECURSION_FIELDS={'recursionBudget':'BudgetReference','recursionStopRule':'StopRuleReference'}
GROUPS=[(INSTANCE_FIELDS,'InstanceReference'),(OWNER_FIELDS,'InstanceReference'),(LANE_FIELDS,'InstanceReference'),(VERSION_FIELDS,'ProductCapabilityVersionReference'),(PARENT_FIELDS,'ProductCapabilityReference'),(RECURSION_FIELDS,'RecursionContractReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()}
HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'}
FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
FLAGS=['InstanceApplicable','InstanceInScopeDeclared','InstanceRealizationDeclared','InstanceSpecializationDeclared','InstanceOwnerLocalDeclared','InstanceCoordinationContextDeclared','InstanceSemanticContextsDeclared','InstanceClaimsSeparatedDeclared']
EXCLUDED=['InstanceIsProductCapabilityDeclared','InstanceIsBoundedContextDeclared','InstanceIsCoordinationContextDeclared','InstanceIsProjectDeclared','InstanceIsGoalDeclared','InstanceIsDirectoryDeclared','InstanceIsComponentDeclared','InstanceIsDeploymentDeclared','InstanceIsConformanceResultDeclared','InstanceIsAuthorityGrantDeclared','ParentClaimGrantsInstanceAuthorityDeclared','ConformanceInterpretedAsAuthorityDeclared','CopiedFolderEstablishesRecursionDeclared','InstanceAdmissionActivatesLifecycleDeclared']
ACTUAL=['IdentityFidelity','ParentVersionExactness','Realization','Specialization','LocalOwnership','OwnerAuthorization','CoordinationContextResolution','SemanticContextResolution','AuthorityLaneSeparation','ContractInheritance','ExtensionPermission','Adoption','ConstructionCompletion','Conformance','LifecycleOperation','DriftHandling','Recomposition','BudgetEnforcement','Termination','TerminalHandoff','Instantiation','Binding','Authority','SourceFidelity','ConsumerAlignment','WholeProof']
SIGNATURE={n:['InstanceReference'] for n in FLAGS+EXCLUDED+['InstanceActual'+n for n in ACTUAL]}
for sort in SORTS:
 if sort not in ['InstanceReference','Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({
'OwnerLocalToCoordinationContextDeclared':['LocalOwnerReference','CoordinationContextReference'],
'BoundedContextCollectionContainsDeclared':['BoundedContextCollectionReference','BoundedContextReference'],
'InstanceSemanticContextReferenceDeclared':['InstanceReference','BoundedContextReference'],
'ParentClaimAtLaneDeclared':['InstanceReference','AuthorityLaneReference','AuthorityClaimReference'],
'InstanceClaimAtLaneDeclared':['InstanceReference','AuthorityLaneReference','AuthorityClaimReference'],
'ParentCapabilityActualAuthority':['ProductCapabilityReference'],
'RecursionHasBudgetDeclared':['RecursionContractReference'],
'RecursionHasStopDeclared':['RecursionContractReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
MAP={'InstanceReference':'InstanceApplicable'}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):
 return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,name,z):return allof([(sort,name)],implies(pred(member(sort),name),z))
I=var('i');C=var('c');L=var('lane');A=var('claim')
APP=pred('InstanceApplicable',I)
VERSION=fn('instanceCapabilityVersion',I)
PARENT=fn('versionParentCapability',VERSION)
RECURSION=fn('instanceRecursionContract',I)
ROOT_RULE=both(
 allof([('InstanceReference','i')],iff(APP,pred('InstanceInScopeDeclared',I))),
 selected('InstanceReference','i',both(guard('InstanceReference',I),exact(INSTANCE_FIELDS,I),
  either(pred('InstanceRealizationDeclared',I),pred('InstanceSpecializationDeclared',I)),
  pred('InstanceCoordinationContextDeclared',I),pred('InstanceSemanticContextsDeclared',I))))
OWNER_RULE=selected('InstanceReference','i',both(exact(OWNER_FIELDS,I),
 pred('InstanceOwnerLocalDeclared',I),
 pred('OwnerLocalToCoordinationContextDeclared',fn('instanceLocalOwner',I),fn('instanceCoordinationContext',I))))
# At least one semantic context follows the positive genus's contexts-present
# condition; no exact size, disjointness or world-resolution assertion follows.
CONTEXT_RULE=selected('InstanceReference','i',both(
 exists([('BoundedContextReference','c')],pred('InstanceSemanticContextReferenceDeclared',I,C)),
 allof([('BoundedContextReference','c')],both(
  iff(pred('InstanceSemanticContextReferenceDeclared',I,C),pred('BoundedContextCollectionContainsDeclared',fn('instanceBoundedContexts',I),C)),
  implies(pred('InstanceSemanticContextReferenceDeclared',I,C),guard('BoundedContextReference',C))))))
PARENT_RULE=selected('InstanceReference','i',both(exact(VERSION_FIELDS,VERSION),
 exact(PARENT_FIELDS,PARENT),neg(eq(fn('instanceIdentity',I),fn('parentCapabilityIdentity',PARENT)))))
# Two claims share a candidate carrier. Separation is represented by explicit
# lane bindings, not by nominally disjoint sorts or unequal printed claim text.
# Whether concrete consumers require different claim record IDs is unresolved.
CLAIM_RULE=both(
 guard('AuthorityLaneReference',const('PARENT_LANE')),
 guard('AuthorityLaneReference',const('INSTANCE_LANE')),
 neg(eq(const('PARENT_LANE'),const('INSTANCE_LANE'))),
 selected('InstanceReference','i',both(exact(LANE_FIELDS,I),
  eq(fn('instanceParentLane',I),const('PARENT_LANE')),
  eq(fn('instanceLocalLane',I),const('INSTANCE_LANE')),
  pred('InstanceClaimsSeparatedDeclared',I),
  allof([('AuthorityLaneReference','lane'),('AuthorityClaimReference','claim')],both(
   iff(pred('ParentClaimAtLaneDeclared',I,L,A),both(eq(L,fn('instanceParentLane',I)),eq(A,fn('instanceParentAuthorityClaim',I)))),
   iff(pred('InstanceClaimAtLaneDeclared',I,L,A),both(eq(L,fn('instanceLocalLane',I)),eq(A,fn('instanceAuthorityClaim',I)))))))))
RECURSION_RULE=selected('InstanceReference','i',both(
 either(pred('RecursionHasBudgetDeclared',RECURSION),pred('RecursionHasStopDeclared',RECURSION)),
 implies(pred('RecursionHasBudgetDeclared',RECURSION),exact({'recursionBudget':'BudgetReference'},RECURSION)),
 implies(pred('RecursionHasStopDeclared',RECURSION),exact({'recursionStopRule':'StopRuleReference'},RECURSION))))
BOUNDARIES=selected('InstanceReference','i',both(*[neg(pred(n,I)) for n in EXCLUDED]))
THEORY={'root-positive-genus-and-sixteen-coordinates':ROOT_RULE,'owner-locality-companion':OWNER_RULE,
'explicit-semantic-context-membership':CONTEXT_RULE,'one-exact-parent-version-and-distinct-identity':PARENT_RULE,
'parent-and-instance-claim-lanes':CLAIM_RULE,'recursion-budget-or-stop':RECURSION_RULE,'role-and-authority-boundaries':BOUNDARIES}
LOSSES=[
'Exact C18 positive Definition admission and C17 source-use admission are separate from accepted interpretation,instance adoption,construction,conformance or authority.',
'All sixteen tuple coordinates retain exact declared typed bindings;concrete reference resolution and real-world denotations remain pending.',
'The positive genus requires owner locality and realization or specialization;the disjunction is inclusive and its classification is not evidence of actual realization.',
'Local owner is explicit in the normative statement and first test but absent as a named tuple coordinate;the candidate companion doesnot rewrite the canonical tuple.',
'The Definition semantic owner,parent capability owner andinstance local owner are separate roles;no owner orauthorization is inferred from a schema owner field.',
'Each selected instance nominates one exact Product Capability version with one declared parent reference;no global latest-version or unique-instance rule follows.',
'Instance andparent use one candidate identity carrier for required inequality;actual alias resolution andaccepted cross-definition common-carrier maps remain pending.',
'Explicit coordination context andatleastone nominated semantic context retain the source positive contexts-present condition;theiractual resolution is independent.',
'Bounded context collections have exact selected membership;no exact cardinality,disjointness orglobal complete enumeration is introduced.',
'Authority claims share a candidate carrier with separately bound parent andinstance lanes;different principals,strength labels orclaim contents are not required.',
'Concrete claim record equality andscope policy require owner review;two nominally disjoint sorts cannotprove actual authority separation.',
'Inherited contract,extension scope andadoption decision are declared bindings;actual inheritance,permission andadoption require separate evidence.',
'Construction binding retains the D65 obligation without asserting an unreviewed stage map,successful construction oractual runtime realization.',
'Conformance references remain distinct from conformance results,admission andauthority;no unsupported collection cardinality oractual conformance is inferred.',
'Lifecycle,drift and recomposition nominate typed carriers;labels donotprove activation,correct state transitions,drift detection orsuccessful recomposition.',
'Recursion requires a budget orstop inclusively with the source recomposition route;budget-only,stop-only andoverlap must remain independently expressible.',
'Budget andstop references do notestablish numeric adequacy,well-founded recursion,fixed-point semantics oractual termination.',
'Terminal handoff retains a necessary declared binding;actual transfer,completion andrecipient authority remain independent.',
'Instance isnot its Product Capability,contexts,Project,Goal,directory,component,deployment,conformance result orauthority grant.',
'Copied folder structure doesnotestablish recursion andparent claim orconformance doesnotgrant instance authority.',
'Independently justified actual authority andconformance remain possible;non-inference isnot a universal prohibition on authorized orconformant instances.',
'D64 andD67 preserve exact C17 admitted H2 selectors andtheir current relocated excerptbytes;whole-producer authenticity andunselected source meanings are notassumed.',
'No whole Product Capability,Coordination/Bounded Context,construction,conformance orParent-Instance theory is silently imported.',
'Actual realization,ownerlocality,adoption,construction,conformance,lifecycle,recursion/handoff,fidelity andwhole proof remain independent query targets.',
'Conformance-to-authority andparent-authority-to-instance-authority have separate conditional queries with positive antecedent witnesses;unconditional authority nonentailment doesnot substitute for either.',
'Original T/O/E/R/J requirements and source-owner/consumer maps remain outstanding after successful finite declaration checks.']
def declarations():
 return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def required_populations():
 def witness(body):return exists([('InstanceReference','i')],both(APP,body))
 budget=pred('RecursionHasBudgetDeclared',RECURSION);stop=pred('RecursionHasStopDeclared',RECURSION)
 return {
 'Instance':('InstanceReference',witness(APP)),
 'OutsideInstance':('InstanceReference',exists([('InstanceReference','i')],neg(APP))),
 'Realization':('InstanceReference',witness(pred('InstanceRealizationDeclared',I))),
 'Specialization':('InstanceReference',witness(pred('InstanceSpecializationDeclared',I))),
 'OverlappingRealizationSpecialization':('InstanceReference',witness(both(pred('InstanceRealizationDeclared',I),pred('InstanceSpecializationDeclared',I)))),
 'SharedExactParentVersion':('InstanceReference',exists([('InstanceReference','i'),('InstanceReference','other')],both(APP,pred('InstanceApplicable','other'),neg(eq(I,var('other'))),eq(VERSION,fn('instanceCapabilityVersion','other'))))),
 'MultipleSemanticContexts':('BoundedContextReference',exists([('InstanceReference','i'),('BoundedContextReference','c'),('BoundedContextReference','other')],both(APP,pred('InstanceSemanticContextReferenceDeclared',I,C),pred('InstanceSemanticContextReferenceDeclared',I,'other'),neg(eq(C,var('other')))))),
 'BudgetOnly':('InstanceReference',witness(both(budget,neg(stop)))),
 'StopOnly':('InstanceReference',witness(both(stop,neg(budget)))),
 'BudgetAndStop':('InstanceReference',witness(both(budget,stop))),
 'DeclaredRecursionWithoutActualTermination':('InstanceReference',witness(neg(pred('InstanceActualTermination',I)))),
 'DeclaredHandoffWithoutActualHandoff':('InstanceReference',witness(neg(pred('InstanceActualTerminalHandoff',I)))),
 'WithoutActualOutcomes':('InstanceReference',witness(both(*[neg(pred('InstanceActual'+n,I)) for n in ACTUAL]))),
 'IndependentAuthority':('InstanceReference',witness(pred('InstanceActualAuthority',I))),
 'ParentAuthorityWithoutInstanceAuthority':('InstanceReference',witness(both(pred('ParentCapabilityActualAuthority',PARENT),neg(pred('InstanceActualAuthority',I))))),
 'ConformanceWithoutAuthority':('InstanceReference',witness(both(pred('InstanceActualConformance',I),neg(pred('InstanceActualAuthority',I))))),
 'ExplicitOwnerWithoutAuthorization':('LocalOwnerReference',witness(neg(pred('InstanceActualOwnerAuthorization',I)))),
 'UnreferencedDeclaredVersion':('ProductCapabilityVersionReference',exists([('ProductCapabilityVersionReference','v')],both(pred('ProductCapabilityVersionReferenceDeclared','v'),neg(exists([('InstanceReference','i')],both(APP,eq(VERSION,var('v'))))))))}
def query_specs():
 rows=[{'query_id':'Instance-not-Actual'+n,
 'target':allof([('InstanceReference','i')],implies(APP,pred('InstanceActual'+n,I))),
 'witness_condition':exists([('InstanceReference','i')],both(APP,neg(pred('InstanceActual'+n,I)))),
 'selected_in_T':False,'source_condition':'selected-instance','source_fidelity':'pending'} for n in ACTUAL]
 for name,antecedent in [('Conformance',pred('InstanceActualConformance',I)),('ParentAuthority',pred('ParentCapabilityActualAuthority',PARENT))]:
  rows.append({'query_id':'Instance-'+name+'-does-not-imply-Authority',
   'target':allof([('InstanceReference','i')],implies(both(APP,antecedent),pred('InstanceActualAuthority',I))),
   'witness_condition':exists([('InstanceReference','i')],both(APP,antecedent,neg(pred('InstanceActualAuthority',I)))),
   'selected_in_T':False,'source_condition':'selected-instance-with-actual-'+name,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={
 '/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),
 '/voices/scientific_formal/formal_expression':(both(ROOT_RULE,OWNER_RULE,CONTEXT_RULE,PARENT_RULE,CLAIM_RULE,RECURSION_RULE,BOUNDARIES),['axiomatic-implicit']),
 '/scope/applicability':(both(ROOT_RULE,OWNER_RULE,CONTEXT_RULE,PARENT_RULE),['genus-differentia']),
 '/scope/exclusions/0':(BOUNDARIES,['operational']),
 '/scope/exclusions/1':(BOUNDARIES,['operational']),
 '/voices/scientific_formal/boundary_conditions/0':(PARENT_RULE,['operational']),
 '/voices/scientific_formal/boundary_conditions/1':(RECURSION_RULE,['operational']),
 '/voices/scientific_formal/boundary_conditions/2':(CLAIM_RULE,['operational']),
 '/voices/scientific_formal/testable_conditions/0':(both(ROOT_RULE,OWNER_RULE,CONTEXT_RULE,PARENT_RULE,RECURSION_RULE),['operational']),
 '/voices/scientific_formal/testable_conditions/1':(BOUNDARIES,['operational']),
 '/boundaries/0':(BOUNDARIES,['operational']),
 '/boundaries/1':(BOUNDARIES,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']))
  disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred'
  rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows


# Native builder entrypoint code. Assemble only after Project actual audit0.
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context)
 snap=snapshot();r.verify(snap,ROOT);source=context['source_selection']
 assert source['definition_id']=='cal.definition.capability-instance' and source['sha256']=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5'
 doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={
 'encoded':'Necessary owner-local version-exact realization/specialization,complete sixteen coordinates,context presence,parent identity,claim lanes,recursion alternatives andhandoff declarations;actual outcomes remain independent.',
 'explanatory':'Notation,intuition andexamples explain the source without creating instance authority oractual realization.',
 'deferred':'The authority-scope mapping andcandidate no-effect ceiling remain explicit source obligations,checked independently where possible.'}
 for row in selected_clauses(doc):
  cid='CI-'+str(len(clauses)+1).zfill(3);disp=row['disposition']
  clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]})
  links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']]
 primary=next(x['clause_id'] for x in clauses if x['source_selector']=='/voices/scientific_formal/normative_statement')
 req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent realization/specialization,local owner,contexts,shared exact parent,claim lanes,budget/stop andnoninferential outcome examples.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity andowner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CapabilityInstance-exact-parent-owner-context-claims-recursion-handoff-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'CI-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner withcapability,instance,context,authority,construction,conformance andrecursion owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no whole prior theory oraccepted common carrier map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'owner-context-parent-claims-budget-stop-and-handoff','scenario':'Four selected instances include realization,specialization andoverlap,shared parent versions,explicit local owners andsemantic context membership,separate claim lanes,andbudget-only/stop-only/both recursion cases. Actual conformance andparent authority canexist without instance authority.','expected_interpretation':'Necessary declarations hold withindependently supported authority possible;no actual realization,adoption,construction,conformance,recursion orfidelity inferred.','rationale':'Preserve positive genus andconditional forbidden-inference witnesses.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'nonempty-recursion-handle-with-neither-budget-nor-stop','scenario':'A selected instance still nominates a declared nonempty recursion contract butneither budget norstop isdeclared.','expected_interpretation':'The required recursion alternative fails independently of the handle.','rationale':'A named reference doesnot supply the required recursion contract contents.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  sel=clause['source_selector'];targets=['Instance-not-ActualSourceFidelity','Instance-not-ActualAuthority']
  if sel in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:
   targets += ['Instance-not-ActualRealization','Instance-not-ActualLocalOwnership','Instance-not-ActualAdoption','Instance-not-ActualConstructionCompletion','Instance-not-ActualConformance','Instance-not-ActualTermination','Instance-not-ActualTerminalHandoff','Instance-Conformance-does-not-imply-Authority','Instance-ParentAuthority-does-not-imply-Authority']
  if sel=='/voices/scientific_formal/boundary_conditions/0':targets+=['Instance-not-ActualParentVersionExactness','Instance-not-ActualIdentityFidelity']
  if sel=='/voices/scientific_formal/boundary_conditions/1':targets+=['Instance-not-ActualBudgetEnforcement','Instance-not-ActualTermination','Instance-not-ActualRecomposition']
  if sel=='/voices/scientific_formal/boundary_conditions/2':targets+=['Instance-not-ActualAuthorityLaneSeparation','Instance-ParentAuthority-does-not-imply-Authority']
  if sel=='/voices/scientific_formal/testable_conditions/0':targets+=['Instance-not-ActualLocalOwnership','Instance-not-ActualCoordinationContextResolution','Instance-not-ActualSemanticContextResolution','Instance-not-ActualConstructionCompletion','Instance-not-ActualTermination','Instance-not-ActualRecomposition','Instance-not-ActualTerminalHandoff']
  if sel=='/voices/scientific_formal/testable_conditions/1':targets+=['Instance-Conformance-does-not-imply-Authority']
  if sel=='/boundaries/1':targets+=['Instance-not-ActualInstantiation','Instance-not-ActualTermination']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in ids,target
   obligations.append({'source':source,'selector':sel,'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'sixteen-exact-source-coordinates','owner':'explicit-companion-condition-not-a-canonical-tuple-rewrite','positive_genus':'inclusive-owner-local-realization-or-specialization-of-one-exact-parent-version','identity':'shared-carrier-Instance-versus-Parent-inequality','contexts':'explicit-coordination-andnominated-semantic-context-membership','claims':'shared-claim-carrier-separate-bound-parent-andinstance-lanes','recursion':'inclusive-budget-or-stop-with-recomposition-andterminal-handoff','actual_outcome_queries_assumed_in_T':False,'conditioned_authority_queries':2,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary instance tuple/owner/context/parent/claim/recursion/handoff declarations only;actual realization,adoption,conformance,authority,fidelity andwhole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context)
 print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()

