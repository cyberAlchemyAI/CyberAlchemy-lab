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
   iff(pred('InstanceClaimAtLaneDeclared',I,L,A),both(eq(L,fn('instanceLocalLane',I)),eq(A,fn('instanceAuthorityClaim',I))))))))
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
 'ConformanceWithoutAuthority':('InstanceReference',witness(both(pred('InstanceActualConformance',I),neg(pred('InstanceActualAuthority',I))))),
 'ExplicitOwnerWithoutAuthorization':('LocalOwnerReference',witness(neg(pred('InstanceActualOwnerAuthorization',I)))),
 'UnreferencedDeclaredVersion':('ProductCapabilityVersionReference',exists([('ProductCapabilityVersionReference','v')],both(pred('ProductCapabilityVersionReferenceDeclared','v'),neg(exists([('InstanceReference','i')],both(APP,eq(VERSION,var('v'))))))))}
def query_specs():
 return [{'query_id':'Instance-not-Actual'+n,
 'target':allof([('InstanceReference','i')],implies(APP,pred('InstanceActual'+n,I))),
 'witness_condition':exists([('InstanceReference','i')],both(APP,neg(pred('InstanceActual'+n,I)))),
 'selected_in_T':False,'source_condition':'selected-instance','source_fidelity':'pending'} for n in ACTUAL]
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

