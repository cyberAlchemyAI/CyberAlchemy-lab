SCOPE='scope:candidate:CAV2-D20-CraftMethod-recursive-typed-construction-v1'
SORTS=['CraftReference','MethodReference','ScopeReference','ProductReference','ProjectReference','ContextReference','ProductIntentReference','DomainMeaningReference','SystemSpecificationReference','RealizationSelectionReference','ConstructionReference','ConformanceReference','OperationReference','RecoveryEvolutionReference','OwnerContinuationReference','LedgerStateReference','StageReference','SubjectReference','IdentityReference','TypeReference','SourceReference','EvidenceReference','ViewReference','CanonicalInputReference','DigestReference','ResidueReference','OwnerRouteReference','RecompositionReference','ClosureReference','OwnerReference','DecisionReference','Token']
CONSTANTS={'EMPTY':'Token'}
CRAFT_FIELDS={'craftGenericMethod':'MethodReference','craftScope':'ScopeReference','craftContext':'ContextReference','craftProductIntent':'ProductIntentReference','craftDomainMeaning':'DomainMeaningReference','craftSystemSpecification':'SystemSpecificationReference','craftRealizationSelection':'RealizationSelectionReference','craftConstruction':'ConstructionReference','craftConformance':'ConformanceReference','craftOperation':'OperationReference','craftRecoveryEvolution':'RecoveryEvolutionReference','craftOwnerContinuation':'OwnerContinuationReference','craftLedgerState':'LedgerStateReference'}
SCOPE_FIELDS={'scopeProduct':'ProductReference','scopeProject':'ProjectReference'}
STAGE_FIELDS={'stageMethod':'CraftReference','stageSubject':'SubjectReference','stageCanonicalSource':'SourceReference','stagePredecessorEvidence':'EvidenceReference','stageResultEvidence':'EvidenceReference','stageConstruction':'ConstructionReference'}
SUBJECT_FIELDS={'subjectIdentity':'IdentityReference','subjectType':'TypeReference'}
PARENT_FIELDS={'stageParent':'StageReference'}
PREREQ_FIELDS={'stagePrerequisiteResidue':'ResidueReference'}
VIEW_FIELDS={'viewMethod':'CraftReference','viewInput':'CanonicalInputReference','viewFirstDigest':'DigestReference','viewSecondDigest':'DigestReference'}
INPUT_FIELDS={'inputSource':'SourceReference','inputDigest':'DigestReference'}
RESIDUE_FIELDS={'residueMethod':'CraftReference','residueType':'TypeReference'}
OPEN_FIELDS={'residueOwnerRoute':'OwnerRouteReference'}
RECOMPOSE_FIELDS={'recompositionChild':'StageReference','recompositionParent':'StageReference','recompositionEvidence':'EvidenceReference','recompositionResidue':'ResidueReference'}
CONTINUATION_FIELDS={'continuationOwner':'OwnerReference'}
CLOSURE_FIELDS={'closureMethod':'CraftReference','closureOwner':'OwnerReference','closureContinuation':'OwnerContinuationReference'}
CLOSED_FIELDS={'closureDecision':'DecisionReference','closureEvidence':'EvidenceReference'}
GROUPS=[(CRAFT_FIELDS,'CraftReference'),(SCOPE_FIELDS,'ScopeReference'),(STAGE_FIELDS,'StageReference'),(SUBJECT_FIELDS,'SubjectReference'),(PARENT_FIELDS,'StageReference'),(PREREQ_FIELDS,'StageReference'),(VIEW_FIELDS,'ViewReference'),(INPUT_FIELDS,'CanonicalInputReference'),(RESIDUE_FIELDS,'ResidueReference'),(OPEN_FIELDS,'ResidueReference'),(RECOMPOSE_FIELDS,'RecompositionReference'),(CONTINUATION_FIELDS,'OwnerContinuationReference'),(CLOSURE_FIELDS,'ClosureReference'),(CLOSED_FIELDS,'ClosureReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
CRAFT_EXCLUDED=['CraftIsProductDeclared','CraftIsProjectDeclared','CraftIsDotCraftStateDeclared','CraftIsGeneratorDeclared','CraftIsRuntimeDeclared','CraftIsPublicCapabilityDeclared','CraftIsFeatureDeclared','CraftIsTaskRunnerDeclared','CraftIsAuthoritySourceDeclared','CraftLedgerIsMethodDeclared','CraftMergesProductProjectMethodDeclared','CraftDefinitionAdmitsDefinitionDeclared','CraftDefinitionAuthorizesBuildDeclared','CraftDefinitionProvesConformanceDeclared','CraftDefinitionGrantsPermissionDeclared']
STAGE_EXCLUDED=['ConstructionIsConformanceDeclared','ConstructionProvesRuntimeDeclared','ConformanceIsAdoptionDeclared','AdoptionIsPermissionDeclared','StageCanonicalSourceReplacedByViewDeclared','StageMergesChildParentIdentitiesDeclared']
VIEW_EXCLUDED=['GeneratedViewIsCanonicalSourceDeclared','ViewWritesBackCanonicalAuthorityDeclared','ViewDigestEqualityProvesDeterminismDeclared','ViewShapeProvesConformanceDeclared']
RESIDUE_EXCLUDED=['ResidueTypeLabelProvesAdequacyDeclared','ResidueOwnerRouteGrantsAuthorityDeclared','PrerequisiteResidueIsPermissionDeclared']
RECOMPOSE_EXCLUDED=['RecompositionMergesChildParentIdentityDeclared','RecompositionDeletesResidueDeclared','RecompositionProvesParentConformanceDeclared']
CLOSURE_EXCLUDED=['ClosureLabelIsOwnerAuthorizationDeclared','ClosureProvesRuntimeDeclared','ClosureAdoptsMethodDeclared','ClosureGrantsPermissionDeclared','ClosurePublishesImplementationDeclared']
CRAFT_ACTUAL=['MethodSpecialization','TypedIdentityPreservation','CanonicalSourceAuthority','ConstructionConformanceSeparation','ViewDerivation','ResidueAdequacy','ChildParentRecomposition','OwnerControlledClosure','LedgerContinuity','NoIdentityMerge','SourceFidelity','Authority','Proof','Adoption','Permission']
STAGE_ACTUAL=['TypedIdentityPreservation','CanonicalSourceAuthority','PredecessorEvidenceResolution','CAV2D65Following','PrerequisiteResidueAdequacy','ConstructionSuccess','Conformance','RuntimeEvidence','Adoption','Permission','Authority']
VIEW_ACTUAL=['MachineCanonicalInputFidelity','SourceAuthority','DeterministicReproduction','GeneratedDerivation','NoReverseAuthority','Conformance','Authority']
RESIDUE_ACTUAL=['TypedResidueFidelity','OwnerRouteValidity','PrerequisiteAdequacy','ResidueContinuity','Authority']
RECOMPOSE_ACTUAL=['ChildParentBinding','EvidenceAdequacy','ResiduePropagation','IdentityNonCollapse','ParentConformance','Authority']
CLOSURE_ACTUAL=['OwnerAuthorization','EvidenceAdequacy','MethodClosure','RuntimeConformance','Adoption','Permission','Authority']
PRIMARY=[('Craft','CraftReference',CRAFT_EXCLUDED,CRAFT_ACTUAL),('Stage','StageReference',STAGE_EXCLUDED,STAGE_ACTUAL),('View','ViewReference',VIEW_EXCLUDED,VIEW_ACTUAL),('Residue','ResidueReference',RESIDUE_EXCLUDED,RESIDUE_ACTUAL),('Recompose','RecompositionReference',RECOMPOSE_EXCLUDED,RECOMPOSE_ACTUAL),('Closure','ClosureReference',CLOSURE_EXCLUDED,CLOSURE_ACTUAL)]
FLAGS={'Craft':['CraftApplicable','CraftInScopeDeclared','CraftMethodSpecializationDeclared','CraftRecursiveChainDeclared','CraftTypedIdentityPreservedDeclared','CraftCanonicalAuthorityPreservedDeclared','CraftConstructionConformanceSeparateDeclared','CraftViewDerivationDeclared','CraftTypedResidueDeclared','CraftChildParentRecompositionDeclared','CraftOwnerClosureDeclared','CraftLedgerContinuityDeclared'],
'Stage':['StageApplicable','StageInScopeDeclared','StageRootDeclared','StageChildDeclared','StageImplementationBearingDeclared','StageFollowsCAV2D65Declared','StageTypedIdentityPreservedDeclared','StageCanonicalAuthorityPreservedDeclared'],
'View':['ViewApplicable','ViewInScopeDeclared','ViewDerivedDeclared','ViewUsesMachineCanonicalInputDeclared'],
'Residue':['ResidueApplicable','ResidueInScopeDeclared','ResidueOpenDeclared','ResidueTypedDeclared','ResiduePrerequisiteDeclared'],
'Recompose':['RecomposeApplicable','RecomposeInScopeDeclared','RecomposeRecordedDeclared'],
'Closure':['ClosureApplicable','ClosureInScopeDeclared','ClosureClosedDeclared','ClosureOwnerControlsDeclared']}
SIGNATURE={}
for prefix,sort,excluded,actual in PRIMARY:SIGNATURE.update({n:[sort] for n in FLAGS[prefix]+excluded+[prefix+'Actual'+n for n in actual]})
for sort in SORTS:
 if sort not in [x[1] for x in PRIMARY]+['Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'ScopeBoundedDeclared':['ScopeReference'],'ScopeWithinDeclared':['ScopeReference','ScopeReference'],'IdentityTypeBindingDeclared':['IdentityReference','TypeReference'],'SourceCanonicalAuthoritativeDeclared':['SourceReference'],'EvidenceResolvedDeclared':['EvidenceReference'],'ParentEvidenceBindingDeclared':['StageReference','EvidenceReference'],'InputMachineCanonicalDeclared':['CanonicalInputReference'],'RecomposeResiduePropagatedDeclared':['RecompositionReference','ResidueReference'],'ClosureDecisionOwnerMethodDeclared':['DecisionReference','OwnerReference','CraftReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
def xor(a,z):return both(either(a,z),neg(both(a,z)))
M=var('m');S=var('s');V=var('v');R=var('r');X=var('x');C=var('c')
MAP={'CraftReference':'CraftApplicable','StageReference':'StageApplicable','ViewReference':'ViewApplicable','ResidueReference':'ResidueApplicable','RecompositionReference':'RecomposeApplicable','ClosureReference':'ClosureApplicable'}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,varname,z):return allof([(sort,varname)],implies(pred(member(sort),varname),z))
def eligible(prefix,sort,varname):return allof([(sort,varname)],iff(pred(prefix+'Applicable',varname),pred(prefix+'InScopeDeclared',varname)))
MAPP=pred('CraftApplicable',M);SAPP=pred('StageApplicable',S);VAPP=pred('ViewApplicable',V);RAPP=pred('ResidueApplicable',R);XAPP=pred('RecomposeApplicable',X);CAPP=pred('ClosureApplicable',C)
ROOT_RULE=both(eligible('Craft','CraftReference','m'),selected('CraftReference','m',both(guard('CraftReference',M),exact(CRAFT_FIELDS,M),exact(SCOPE_FIELDS,fn('craftScope',M)),pred('ScopeBoundedDeclared',fn('craftScope',M)),*[pred(n,M) for n in FLAGS['Craft'] if n not in ['CraftApplicable','CraftInScopeDeclared']])))
SM=fn('stageMethod',S);SUB=fn('stageSubject',S);PARENT=fn('stageParent',S);PRE=fn('stagePrerequisiteResidue',S)
STAGE_RULE=both(eligible('Stage','StageReference','s'),selected('StageReference','s',both(guard('StageReference',S),exact(STAGE_FIELDS,S),exact(SUBJECT_FIELDS,SUB),pred('IdentityTypeBindingDeclared',fn('subjectIdentity',SUB),fn('subjectType',SUB)),pred('StageTypedIdentityPreservedDeclared',S),pred('StageCanonicalAuthorityPreservedDeclared',S),pred('SourceCanonicalAuthoritativeDeclared',fn('stageCanonicalSource',S)),pred('EvidenceResolvedDeclared',fn('stagePredecessorEvidence',S)),eq(fn('stageConstruction',S),fn('craftConstruction',SM)),xor(pred('StageRootDeclared',S),pred('StageChildDeclared',S)),implies(pred('StageChildDeclared',S),both(exact(PARENT_FIELDS,S),neg(eq(S,PARENT)),pred('ParentEvidenceBindingDeclared',PARENT,fn('stagePredecessorEvidence',S)))))))
PREREQUISITE_RULE=selected('StageReference','s',implies(both(pred('StageImplementationBearingDeclared',S),neg(pred('StageFollowsCAV2D65Declared',S))),both(exact(PREREQ_FIELDS,S),pred('ResidueTypedDeclared',PRE),pred('ResiduePrerequisiteDeclared',PRE),eq(fn('residueMethod',PRE),SM))))
IN=fn('viewInput',V)
VIEW_RULE=both(eligible('View','ViewReference','v'),selected('ViewReference','v',both(guard('ViewReference',V),exact(VIEW_FIELDS,V),exact(INPUT_FIELDS,IN),pred('InputMachineCanonicalDeclared',IN),pred('SourceCanonicalAuthoritativeDeclared',fn('inputSource',IN)),pred('ViewDerivedDeclared',V),pred('ViewUsesMachineCanonicalInputDeclared',V),eq(fn('viewFirstDigest',V),fn('viewSecondDigest',V)))))
RESIDUE_RULE=both(eligible('Residue','ResidueReference','r'),selected('ResidueReference','r',both(guard('ResidueReference',R),exact(RESIDUE_FIELDS,R),pred('ResidueTypedDeclared',R),implies(pred('ResidueOpenDeclared',R),exact(OPEN_FIELDS,R)))))
CH=fn('recompositionChild',X);PA=fn('recompositionParent',X);XR=fn('recompositionResidue',X);CM=fn('stageMethod',CH);PM=fn('stageMethod',PA)
RECOMPOSE_RULE=both(eligible('Recompose','RecompositionReference','x'),selected('RecompositionReference','x',both(guard('RecompositionReference',X),exact(RECOMPOSE_FIELDS,X),pred('RecomposeRecordedDeclared',X),pred('StageChildDeclared',CH),eq(fn('stageParent',CH),PA),neg(eq(CH,PA)),eq(fn('recompositionEvidence',X),fn('stageResultEvidence',CH)),eq(fn('residueMethod',XR),CM),pred('RecomposeResiduePropagatedDeclared',X,XR),pred('ScopeWithinDeclared',fn('craftScope',CM),fn('craftScope',PM)))))
CCM=fn('closureMethod',C);CO=fn('closureOwner',C);CONT=fn('closureContinuation',C);DEC=fn('closureDecision',C)
CLOSURE_RULE=both(eligible('Closure','ClosureReference','c'),selected('ClosureReference','c',both(guard('ClosureReference',C),exact(CLOSURE_FIELDS,C),exact(CONTINUATION_FIELDS,CONT),eq(CONT,fn('craftOwnerContinuation',CCM)),eq(CO,fn('continuationOwner',CONT)),pred('ClosureOwnerControlsDeclared',C),implies(pred('ClosureClosedDeclared',C),both(exact(CLOSED_FIELDS,C),pred('ClosureDecisionOwnerMethodDeclared',DEC,CO,CCM),pred('EvidenceResolvedDeclared',fn('closureEvidence',C)))))))
BOUNDARIES=both(*[selected(sort,varname,both(*[neg(pred(n,varname)) for n in excluded])) for (prefix,sort,excluded,actual),varname in zip(PRIMARY,['m','s','v','r','x','c'])])
THEORY={'root':ROOT_RULE,'stage':STAGE_RULE,'implementation-prerequisite':PREREQUISITE_RULE,'view':VIEW_RULE,'residue':RESIDUE_RULE,'recompose':RECOMPOSE_RULE,'closure':CLOSURE_RULE,'boundaries':BOUNDARIES}
LOSSES=[
'Exact C29 Craft Method Definition/source use admission does not accept this translation,bind/adopt Method or execute construction.',
'CAV2-D20 Craft Method specializes the separate CAV2-D32 generic Method;their whole theories and identities are not merged.',
'Eleven tuple fields are proposed independent nominations;formal M_Craft(S) is not an executed process or complete operational state machine.',
'Bounded Product/Project scope remains separately typed;Method,Product,Project,ledger,generator,runtime and capability do not collapse.',
'Stage subject identity/type nominations and preserved-identity flags do not force parent/child stages to share identities or artifact types.',
'Canonical source authority is separately declared per stage/input;no global one-source-for-all-construction rule is invented.',
'Each stage has exact predecessor evidence;root stages may cite external prerequisite evidence without a fabricated parent stage.',
'Child stages nominate a distinct parent and exact parent evidence relation;actual ordering,well-foundedness and termination remain unproved.',
'Implementation-bearing construction either follows declared CAV2-D65 or carries an exact typed prerequisite residue;residue is not permission.',
'Nonimplementation and declared-following cases leave unused prerequisite fields unbound without fabricated residue records.',
'Generated views nominate machine-canonical input/source and equal declared render digests;actual deterministic generation remains independent.',
'Equal digest references are not computed cryptographic equality or proof that a real generator reproduces canonical inputs.',
'Every selected residue has type;open residues have exact owner route while closed/unused routes are not fabricated.',
'Recomposition binds child,parent,evidence,residue and bounded child/parent method scopes;different child scopes and subject identities are allowed.',
'Child residue propagation is a necessary relation without actual parent conformance,residue deletion or identity merge inferred.',
'Closure nominates owner/continuation and requires exact owner-method decision/evidence only when declared closed;pending closure fabricates no approval.',
'Owner-controlled closure is not runtime conformance,adoption,permission or publication and actual owner authority remains independent.',
'C29 positive14Definition1ArtifactType4ownerbinding1chain admissions are preserved without erasing their separate owners/effects.',
'C29 selected chain0002 is current while source-body chain0001 evidence remains historical;S2evaluable-not-executed stays distinct.',
'External legacy path relocation is byte-observed;exact line scope and Product identity digests do not transfer legacy authority or private meaning.',
'Current MethodBinding/Product/Project/Craft consumers need separate accepted source-to-carrier and lifecycle maps.',
'Complete source accounting and supplied finite T/I models do not establish shared denotations,source fidelity,whole translation or whole proof.'
]
def required_populations():
 def w(sort,varname,z):return exists([(sort,varname)],both(pred(member(sort),varname),z))
 return {'CraftScope':('CraftReference',w('CraftReference','m',MAPP)),'OutsideCraft':('CraftReference',exists([('CraftReference','m')],neg(MAPP))),'IndependentAuthority':('CraftReference',w('CraftReference','m',pred('CraftActualAuthority',M))),'CraftWithoutActualOutcomes':('CraftReference',w('CraftReference','m',both(*[neg(pred('CraftActual'+n,M)) for n in CRAFT_ACTUAL]))),'Stage':('StageReference',w('StageReference','s',SAPP)),'OutsideStage':('StageReference',exists([('StageReference','s')],neg(SAPP))),'RootStage':('StageReference',w('StageReference','s',pred('StageRootDeclared',S))),'ChildStage':('StageReference',w('StageReference','s',pred('StageChildDeclared',S))),'ImplementationFollowingC65':('StageReference',w('StageReference','s',both(pred('StageImplementationBearingDeclared',S),pred('StageFollowsCAV2D65Declared',S)))),'ImplementationWithPrerequisiteResidue':('StageReference',w('StageReference','s',both(pred('StageImplementationBearingDeclared',S),neg(pred('StageFollowsCAV2D65Declared',S))))),'NonimplementationStage':('StageReference',w('StageReference','s',neg(pred('StageImplementationBearingDeclared',S)))),'GeneratedView':('ViewReference',w('ViewReference','v',VAPP)),'OutsideView':('ViewReference',exists([('ViewReference','v')],neg(VAPP))),'ViewWithoutActualDeterminism':('ViewReference',w('ViewReference','v',neg(pred('ViewActualDeterministicReproduction',V)))),'OpenResidue':('ResidueReference',w('ResidueReference','r',pred('ResidueOpenDeclared',R))),'NonopenResidue':('ResidueReference',w('ResidueReference','r',neg(pred('ResidueOpenDeclared',R)))),'OutsideResidue':('ResidueReference',exists([('ResidueReference','r')],neg(RAPP))),'PrerequisiteResidue':('ResidueReference',w('ResidueReference','r',pred('ResiduePrerequisiteDeclared',R))),'Recomposition':('RecompositionReference',w('RecompositionReference','x',XAPP)),'OutsideRecomposition':('RecompositionReference',exists([('RecompositionReference','x')],neg(XAPP))),'DifferentChildParentScopes':('RecompositionReference',w('RecompositionReference','x',neg(eq(fn('craftScope',CM),fn('craftScope',PM))))),'SameChildParentScopeAllowed':('RecompositionReference',w('RecompositionReference','x',eq(fn('craftScope',CM),fn('craftScope',PM)))),'DifferentChildParentSubjectIdentity':('RecompositionReference',w('RecompositionReference','x',neg(eq(fn('subjectIdentity',fn('stageSubject',CH)),fn('subjectIdentity',fn('stageSubject',PA)))))),'PendingClosure':('ClosureReference',w('ClosureReference','c',neg(pred('ClosureClosedDeclared',C)))),'DeclaredClosedClosure':('ClosureReference',w('ClosureReference','c',pred('ClosureClosedDeclared',C))),'OutsideClosure':('ClosureReference',exists([('ClosureReference','c')],neg(CAPP)))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for (prefix,sort,excluded,names),vn in zip(PRIMARY,['m','s','v','r','x','c']):
  value=var(vn);app=pred(prefix+'Applicable',value)
  for n in names:
   cond=None;label='selected-'+prefix.lower()
   if prefix=='Stage' and n=='CAV2D65Following':cond=both(pred('StageImplementationBearingDeclared',S),pred('StageFollowsCAV2D65Declared',S));label='implementation-following-C65'
   if prefix=='Stage' and n=='PrerequisiteResidueAdequacy':cond=both(pred('StageImplementationBearingDeclared',S),neg(pred('StageFollowsCAV2D65Declared',S)));label='implementation-with-prerequisite-residue'
   if prefix=='Residue' and n=='OwnerRouteValidity':cond=pred('ResidueOpenDeclared',R);label='open-residue'
   if prefix=='Closure' and n in ['OwnerAuthorization','EvidenceAdequacy','MethodClosure']:cond=pred('ClosureClosedDeclared',C);label='declared-closed-closure'
   scope=app if cond is None else both(app,cond);target=pred(prefix+'Actual'+n,value);rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,vn)],implies(scope,target)),'witness_condition':exists([(sort,vn)],both(scope,neg(target))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(ROOT_RULE,['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,RECOMPOSE_RULE,CLOSURE_RULE),['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(BOUNDARIES,['operational']),'/boundaries/2':(BOUNDARIES,['operational']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(PREREQUISITE_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/2':(VIEW_RULE,['operational']),'/voices/scientific_formal/testable_conditions/0':(STAGE_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(VIEW_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(RESIDUE_RULE,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred'
  rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows

