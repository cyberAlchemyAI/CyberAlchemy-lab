"""Exact CAV2-D20 Craft Method recursive typed construction and owner closure declarations."""
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

def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary typed eleven-tuple,stage,source,view,residue,recomposition and owner-closure declarations. Actual construction,conformance,determinism and owner authority remain independent.','explanatory':'Notation,plain-language intuition and domain examples are explanatory;no actual construction or authority inferred.','deferred':'The authority-scope map and candidate migration ceiling remain explicit unresolved source obligations.'}
 for row in selected_clauses(doc):
  cid='CRM-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent supplied selected/outside,root/child,implementation/prerequisite,open/nonopen and pending/closed population obligations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity and owner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CAV2-D20-CraftMethod-recursive-typed-construction-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'CRM-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Method,Product,Project,construction,source,conformance,residue and closure owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no prior whole theory or accepted source/consumer map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'root-child-prerequisite-and-owner-closure','scenario':'A bounded Craft Method supplies eleven typed coordinates. One child follows CAV2-D65;another carries typed prerequisite residue. Child evidence and residue recompose into the parent. One owner closure is declared and another remains pending.','expected_interpretation':'Necessary declarations hold;actual prerequisite adequacy,construction,conformance,owner permission and closure remain independent.','rationale':'Typed references and declared relationships are distinct from operational truth.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'view-replaces-canonical-source','scenario':'A generated view is nominated as the replacement writable canonical source.','expected_interpretation':'The directionality boundary fails.','rationale':'A generated view cannot confer reverse canonical authority.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});query_ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Craft-not-ActualSourceFidelity','Craft-not-ActualAuthority']
  if clause['source_selector'] in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:targets+=['Stage-not-ActualConstructionSuccess','Recompose-not-ActualResiduePropagation','Closure-not-ActualOwnerAuthorization']
  if 'boundary' in clause['source_selector']:targets+=['Stage-not-ActualConformance','View-not-ActualNoReverseAuthority']
  if 'testable_conditions' in clause['source_selector']:targets+=['Stage-not-ActualPredecessorEvidenceResolution','View-not-ActualDeterministicReproduction','Residue-not-ActualOwnerRouteValidity']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in query_ids,target
   obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'eleven-distinct-typed-coordinate-nominations-with-separate-generic-Method-and-scope','stages':'exact-subject-identity-type-source-construction-predecessor-result-evidence-with-root-child-separation','prerequisite':'implementation-bearing-follows-CAV2-D65-or-exact-typed-prerequisite-residue','views':'exact-machine-canonical-input-and-two-equal-render-digest-nominations-with-no-reverse-authority','residue':'typed-and-conditionally-owner-routed-when-open','recomposition':'exact-child-parent-evidence-residue-and-scope-within-nominations-without-identity-collapse','closure':'owner-controlled-continuation-with-exact-decision-evidence-only-when-closed','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary typed recursive construction declarations only;actual construction,conformance,determinism,residue adequacy,owner authority,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
