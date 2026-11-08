"""Exact Constraint Cycle Safety watch,governance stop and reviewed exception declarations."""
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
SCOPE='scope:candidate:constraint-cycle-safety-watch-reviewed-exception-v1'
SORTS=['InvariantInstanceReference','NormalizedIdentityReference','ScopeReference','ArtifactTypeReference','SourceReference','SourceRelationReference','ProposalReference','ProposalKindReference','OwnerReference','ExceptionReference','EvidenceReference','ConstraintSemanticsReference','ReviewReference','WitnessReference','ResidueReference','ValidatorReference','ReviewerReference','Token']
CONSTANTS={'EMPTY':'Token','NORMALIZED_ID':'NormalizedIdentityReference','SHARED_SCOPE':'ScopeReference','INVARIANT_TYPE':'ArtifactTypeReference','SOURCE_D28':'SourceReference'}
INSTANCE_FIELDS={'instanceIdentity':'NormalizedIdentityReference','instanceScope':'ScopeReference','instanceType':'ArtifactTypeReference','instanceSourceRelation':'SourceRelationReference'}
RELATION_FIELDS={'sourceRelationIdentity':'NormalizedIdentityReference','sourceRelationTarget':'SourceReference'}
PROPOSAL_FIELDS={'proposalOwner':'OwnerReference','proposalScope':'ScopeReference','proposalKind':'ProposalKindReference'}
OPTIONAL_EXCEPTION_FIELDS={'proposalException':'ExceptionReference'}
EXCEPTION_FIELDS={'exceptionProposal':'ProposalReference','exceptionOwner':'OwnerReference','exceptionScope':'ScopeReference','exceptionEvidence':'EvidenceReference','exceptionSemantics':'ConstraintSemanticsReference','exceptionReview':'ReviewReference','exceptionWitness':'WitnessReference','exceptionResidue':'ResidueReference'}
REVIEW_FIELDS={'reviewProposal':'ProposalReference','reviewScope':'ScopeReference','reviewWitness':'WitnessReference'}
VALIDATOR_FIELDS={'witnessValidator':'ValidatorReference'}
REVIEWER_FIELDS={'witnessReviewer':'ReviewerReference'}
RESIDUE_FIELDS={'residueType':'ArtifactTypeReference'}
GROUPS=[(INSTANCE_FIELDS,'InvariantInstanceReference'),(RELATION_FIELDS,'SourceRelationReference'),(PROPOSAL_FIELDS,'ProposalReference'),(OPTIONAL_EXCEPTION_FIELDS,'ProposalReference'),(EXCEPTION_FIELDS,'ExceptionReference'),(REVIEW_FIELDS,'ReviewReference'),(VALIDATOR_FIELDS,'WitnessReference'),(REVIEWER_FIELDS,'WitnessReference'),(RESIDUE_FIELDS,'ResidueReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
INSTANCE_EXCLUDED=['InstanceSilentSiblingMergeDeclared','DefinitionAdmissionAcceptsTranslationDeclared','InstanceClassificationGrantsAuthorityDeclared','InvariantCreatesCarrierDeclared','InvariantCreatesInstanceDeclared','InvariantCreatesRuntimeDeclared','PublicationEffectGrantedDeclared','DeploymentEffectGrantedDeclared','ExternalEffectGrantedDeclared']
PROPOSAL_EXCLUDED=['GuardIsContextualityTheoremDeclared','GuardIsSpectralPresheafCheckerDeclared','GuardBansCyclicNonValueRelationsDeclared','GuardBansAcyclicValueConstraintsDeclared','GuardPromotesLiveEdgeFamilyDeclared','GuardCreatesActualAuthorityDeclared','SourceMeaningSilentlyMergedDeclared','HarmlessShapeProvesPermissionDeclared','ReviewLabelProvesSafetyDeclared']
EXCEPTION_EXCLUDED=['ExceptionLabelProvesConstraintSatisfiableDeclared','WitnessLabelProvesObstructionAbsentDeclared','ResidueLabelProvesActualOwnerAcceptanceDeclared','ExceptionCreatesUnrestrictedAuthorityDeclared','ExceptionPromotesLiveEdgeFamilyDeclared']
INSTANCE_ACTUAL=['IdentityFidelity','ClassificationFidelity','SourceRelationFidelity','SourceCurrentness','DefinitionShape','ProjectionFidelity','SourceFidelity','Authority','Proof','Admission','Activation','ExternalEffect']
PROPOSAL_ACTUAL=['ValueConstraintClassification','CyclePermissionFidelity','Acyclicity','GovernanceStop','PromotionBlocked','ReviewComplete','ConstraintSafety','NoObstruction','OwnerAuthorization','ConsumerAlignment','SharedConsistency','Authority','Proof','Activation','ExternalEffect']
EXCEPTION_ACTUAL=['SourceEvidenceAdequacy','ConstraintSemanticsFidelity','ReviewAdequacy','WitnessValidity','TypedResidueFidelity','OwnerAcceptance','ConstraintSatisfiability','Authority']
VALUE_AXES=['Value','Label','AuthorityState','SchemaField','ValidationOutcome']
PFLAGS=['ProposalApplicable','ProposalInScopeDeclared','ProposalGovernedDeclared','ProposalRelationDeclared','ProposalEdgeTypeDeclared','ProposalOntologyMovementDeclared','ProposalValueConstrainingDeclared','ProposalCyclePermissionDeclared','ProposalExplicitAcyclicityDeclared','ProposalEffectiveCyclePermittedDeclared','ProposalWatchTriggeredDeclared','ProposalGovernanceStoppedDeclared','ProposalPromotionBlockedDeclared','ProposalReviewRequiredDeclared','ProposalReviewCompletedDeclared','ProposalExceptionPresentDeclared','ProposalInfluenceApprovedDeclared','ProposalPromotionApprovedDeclared']+['ProposalConstrains'+n+'Declared' for n in VALUE_AXES]
SIGNATURE={n:['InvariantInstanceReference'] for n in ['InstanceApplicable','InstanceInScopeDeclared','InstanceGovernedDeclared','InstanceSourceDigestsCurrentDeclared','InstanceDefinitionSchemaValidDeclared','InstanceProjectionExactDeclared',*INSTANCE_EXCLUDED,*['InstanceActual'+n for n in INSTANCE_ACTUAL]]}
SIGNATURE.update({n:['ProposalReference'] for n in PFLAGS+PROPOSAL_EXCLUDED+['ProposalActual'+n for n in PROPOSAL_ACTUAL]})
for sort in SORTS:
 if sort not in ['InvariantInstanceReference','ProposalReference','Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({n:['ExceptionReference'] for n in ['ExceptionRecordedDeclared','ExceptionExplicitOwnerDecisionDeclared',*EXCEPTION_EXCLUDED,*['ExceptionActual'+n for n in EXCEPTION_ACTUAL]]})
SIGNATURE.update({'SourceRelationAcceptedDeclared':['SourceRelationReference'],'SourceEvidencePresentDeclared':['EvidenceReference'],'ConstraintSemanticsNamedDeclared':['ConstraintSemanticsReference'],'ReviewRecordedDeclared':['ReviewReference'],'ReviewSatisfiabilityDeclared':['ReviewReference'],'ReviewObstructionDeclared':['ReviewReference'],'ReviewValidatorOrReviewerCatchNamedDeclared':['ReviewReference'],'WitnessRecordedDeclared':['WitnessReference'],'WitnessValidatorDeclared':['WitnessReference'],'WitnessReviewerDeclared':['WitnessReference'],'ResidueTypedDeclared':['ResidueReference'],'OwnerAcceptsRemainingResidueDeclared':['OwnerReference','ResidueReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
I=var('i');P=var('p');IAPP=pred('InstanceApplicable',I);PAPP=pred('ProposalApplicable',P)
def pf(n):return fn(n,P)
EXC=pf('proposalException');OWNER=pf('proposalOwner');PSCOPE=pf('proposalScope');REV=fn('exceptionReview',EXC);WIT=fn('exceptionWitness',EXC);RES=fn('exceptionResidue',EXC)
WATCH=pred('ProposalWatchTriggeredDeclared',P);EXCP=pred('ProposalExceptionPresentDeclared',P)
def member(sort):return {'InvariantInstanceReference':'InstanceApplicable','ProposalReference':'ProposalApplicable'}.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'v')],iff(pred(n+'BindingDeclared',value,'v'),eq(var('v'),fn(n,value))))) for n,sort in fields.items()])
def ip(z):return allof([('InvariantInstanceReference','i')],implies(IAPP,z))
def pp(z):return allof([('ProposalReference','p')],implies(PAPP,z))
INSTANCE_GENUS=allof([('InvariantInstanceReference','i')],both(iff(IAPP,pred('InstanceInScopeDeclared',I)),implies(IAPP,both(guard('InvariantInstanceReference',I),pred('InstanceGovernedDeclared',I),exact(INSTANCE_FIELDS,I),eq(fn('instanceIdentity',I),const('NORMALIZED_ID')),eq(fn('instanceScope',I),const('SHARED_SCOPE')),eq(fn('instanceType',I),const('INVARIANT_TYPE')),exact(RELATION_FIELDS,fn('instanceSourceRelation',I)),eq(fn('sourceRelationIdentity',fn('instanceSourceRelation',I)),const('NORMALIZED_ID')),eq(fn('sourceRelationTarget',fn('instanceSourceRelation',I)),const('SOURCE_D28')),pred('SourceRelationAcceptedDeclared',fn('instanceSourceRelation',I))))))
PROPOSAL_GENUS=allof([('ProposalReference','p')],both(iff(PAPP,pred('ProposalInScopeDeclared',P)),implies(PAPP,both(guard('ProposalReference',P),pred('ProposalGovernedDeclared',P),exact(PROPOSAL_FIELDS,P),either(pred('ProposalRelationDeclared',P),pred('ProposalEdgeTypeDeclared',P),pred('ProposalOntologyMovementDeclared',P))))))
VALUE_CLASSIFICATION=pp(iff(pred('ProposalValueConstrainingDeclared',P),either(*[pred('ProposalConstrains'+n+'Declared',P) for n in VALUE_AXES])))
CYCLE_CLASSIFICATION=pp(iff(pred('ProposalEffectiveCyclePermittedDeclared',P),both(pred('ProposalCyclePermissionDeclared',P),neg(pred('ProposalExplicitAcyclicityDeclared',P)))))
WATCH_CLASSIFICATION=pp(iff(WATCH,both(pred('ProposalValueConstrainingDeclared',P),pred('ProposalEffectiveCyclePermittedDeclared',P))))
STOP_RULE=pp(implies(WATCH,both(pred('ProposalGovernanceStoppedDeclared',P),pred('ProposalPromotionBlockedDeclared',P),pred('ProposalReviewRequiredDeclared',P))))
EXCEPTION_RULE=pp(implies(EXCP,both(exact(OPTIONAL_EXCEPTION_FIELDS,P),exact(EXCEPTION_FIELDS,EXC),pred('ExceptionRecordedDeclared',EXC),pred('ExceptionExplicitOwnerDecisionDeclared',EXC),eq(fn('exceptionProposal',EXC),P),eq(fn('exceptionOwner',EXC),OWNER),eq(fn('exceptionScope',EXC),PSCOPE),pred('SourceEvidencePresentDeclared',fn('exceptionEvidence',EXC)),pred('ConstraintSemanticsNamedDeclared',fn('exceptionSemantics',EXC)),exact(REVIEW_FIELDS,REV),pred('ReviewRecordedDeclared',REV),either(pred('ReviewSatisfiabilityDeclared',REV),pred('ReviewObstructionDeclared',REV)),pred('ReviewValidatorOrReviewerCatchNamedDeclared',REV),eq(fn('reviewProposal',REV),P),eq(fn('reviewScope',REV),PSCOPE),eq(fn('reviewWitness',REV),WIT),pred('WitnessRecordedDeclared',WIT),either(pred('WitnessValidatorDeclared',WIT),pred('WitnessReviewerDeclared',WIT)),implies(pred('WitnessValidatorDeclared',WIT),exact(VALIDATOR_FIELDS,WIT)),implies(pred('WitnessReviewerDeclared',WIT),exact(REVIEWER_FIELDS,WIT)),exact(RESIDUE_FIELDS,RES),pred('ResidueTypedDeclared',RES),pred('OwnerAcceptsRemainingResidueDeclared',OWNER,RES),pred('ProposalReviewCompletedDeclared',P))))
INFLUENCE_RULE=pp(implies(both(WATCH,either(pred('ProposalInfluenceApprovedDeclared',P),pred('ProposalPromotionApprovedDeclared',P))),both(EXCP,pred('ProposalReviewCompletedDeclared',P))))
SOURCE_RECORD_TESTS=ip(both(pred('InstanceSourceDigestsCurrentDeclared',I),pred('InstanceDefinitionSchemaValidDeclared',I),pred('InstanceProjectionExactDeclared',I)))
INSTANCE_BOUNDARIES=ip(both(*[neg(pred(n,I)) for n in INSTANCE_EXCLUDED]))
PROPOSAL_BOUNDARIES=pp(both(*[neg(pred(n,P)) for n in PROPOSAL_EXCLUDED]))
EXCEPTION_BOUNDARIES=pp(implies(EXCP,both(*[neg(pred(n,EXC)) for n in EXCEPTION_EXCLUDED])))
THEORY={'instance-genus':INSTANCE_GENUS,'proposal-genus':PROPOSAL_GENUS,'value-classification':VALUE_CLASSIFICATION,'cycle-classification':CYCLE_CLASSIFICATION,'watch-classification':WATCH_CLASSIFICATION,'stop':STOP_RULE,'exception':EXCEPTION_RULE,'influence':INFLUENCE_RULE,'source-tests':SOURCE_RECORD_TESTS,'instance-boundaries':INSTANCE_BOUNDARIES,'proposal-boundaries':PROPOSAL_BOUNDARIES,'exception-boundaries':EXCEPTION_BOUNDARIES}
LOSSES=[
'Exact C53 source/admission overlay does not promote edge families,grant authority,accept formal translation or prove contextuality.',
'Canonical Invariant instance and proposed relation/edge/movement are separate sorted carriers;no instance or proposal created by source admission.',
'Normalized identity,shared scope,invariant type and accepted CAV2-D28 source relations are proposed classification nominations;no silent sibling merge.',
'Five value-constraining axes are inclusive;their actual meanings and completeness need owner-reviewed source maps.',
'Effective cycle permission is proposed as declared permission without an explicit acyclicity constraint;actual graph cycles and enforcement remain independent.',
'Watch trigger is exact value-constraining plus effective cycle permission;this interpretation of formal/normative wording needs precedence review.',
'Watch-triggered proposals remain stopped,blocked and review-required even after a recorded exception;historical stop versus later permission timing needs an accepted map.',
'Pending risky proposals need no fabricated exception,evidence,review,witness or residue;unused total fields do not assert those records exist.',
'Only declared influence/promotion approval under the watch requires the exact exception and completed review;harmless proposals are not granted actual permission.',
'Exception requires exact proposal,owner,scope,evidence,semantics,review,witness and residue fields;no globally unique exception or owner is assumed.',
'Exception owner/proposal/scope and review proposal/scope/witness coherence are proposed necessary correspondence,not real authorization.',
'Satisfiability review or obstruction review is inclusive;review does not imply a satisfiable constraint system or absence of obstruction.',
'Validator witness or reviewer witness is inclusive with conditional fields;unused alternatives do not fabricate a validator or reviewer.',
'Typed residue and declared owner acceptance preserve required review coordinates;actual residue adequacy and owner acceptance remain independent.',
'No constraint-system solver,cycle detector,spectral-presheaf checker,contextuality theorem or actual edge promotion is executed.',
'Non-value cyclic proposals and acyclic value constraints remain permitted by the guard;separate governance may still restrict them.',
'Instance source-digest,schema-valid and exact-projection declarations are distinct from actual source checks and actual semantic fidelity.',
'Exact upstream section bytes and C53 source-use admission are evidence only;private routing content/meaning is not copied into primary T.',
'Scientific watch/exception logic and plain-language prove-safe phrasing require source-owner precedence;plain intuition is not a theorem.',
'Historical normalization scaffold/candidate ceiling remains visible under C53 current overlay;it is not permission for canonical mutation.',
'All dependencies remain separately qualified;no whole theories,common denotation model or accepted consumer map is imported.',
'Complete character accounting and supplied finite T/I controls do not establish whole translation,source fidelity or whole-definition proof.'
]
def required_populations():
 def wi(z):return exists([('InvariantInstanceReference','i')],both(IAPP,z))
 def wp(z):return exists([('ProposalReference','p')],both(PAPP,z))
 return {'SelectedInvariant':('InvariantInstanceReference',wi(IAPP)),'OutsideInvariant':('InvariantInstanceReference',exists([('InvariantInstanceReference','i')],neg(IAPP))),'InvariantWithoutActualOutcomes':('InvariantInstanceReference',wi(both(*[neg(pred('InstanceActual'+n,I)) for n in INSTANCE_ACTUAL]))),'IndependentAuthority':('InvariantInstanceReference',wi(pred('InstanceActualAuthority',I))),'SelectedProposal':('ProposalReference',wp(PAPP)),'OutsideProposal':('ProposalReference',exists([('ProposalReference','p')],neg(PAPP))),'RelationProposal':('ProposalReference',wp(pred('ProposalRelationDeclared',P))),'EdgeTypeProposal':('ProposalReference',wp(pred('ProposalEdgeTypeDeclared',P))),'MovementProposal':('ProposalReference',wp(pred('ProposalOntologyMovementDeclared',P))),'CyclicNonValue':('ProposalReference',wp(both(pred('ProposalEffectiveCyclePermittedDeclared',P),neg(pred('ProposalValueConstrainingDeclared',P))))),'AcyclicValue':('ProposalReference',wp(both(pred('ProposalValueConstrainingDeclared',P),neg(pred('ProposalEffectiveCyclePermittedDeclared',P))))),'ExplicitAcyclicValue':('ProposalReference',wp(both(pred('ProposalValueConstrainingDeclared',P),pred('ProposalCyclePermissionDeclared',P),pred('ProposalExplicitAcyclicityDeclared',P)))),'RiskPendingException':('ProposalReference',wp(both(WATCH,neg(EXCP)))),'RiskReviewedException':('ProposalReference',wp(both(WATCH,EXCP))),'WatchWithoutActualSafety':('ProposalReference',wp(both(WATCH,neg(pred('ProposalActualConstraintSafety',P))))),'HarmlessWithoutApproval':('ProposalReference',wp(both(neg(WATCH),neg(pred('ProposalInfluenceApprovedDeclared',P)),neg(pred('ProposalPromotionApprovedDeclared',P))))),'ValidatorOnlyWitness':('ProposalReference',wp(both(EXCP,pred('WitnessValidatorDeclared',WIT),neg(pred('WitnessReviewerDeclared',WIT))))),'ReviewerOnlyWitness':('ProposalReference',wp(both(EXCP,pred('WitnessReviewerDeclared',WIT),neg(pred('WitnessValidatorDeclared',WIT))))),'BothWitnessAlternatives':('ProposalReference',wp(both(EXCP,pred('WitnessReviewerDeclared',WIT),pred('WitnessValidatorDeclared',WIT)))),'SatisfiabilityOnlyReview':('ProposalReference',wp(both(EXCP,pred('ReviewSatisfiabilityDeclared',REV),neg(pred('ReviewObstructionDeclared',REV))))),'ObstructionOnlyReview':('ProposalReference',wp(both(EXCP,pred('ReviewObstructionDeclared',REV),neg(pred('ReviewSatisfiabilityDeclared',REV))))),'BothReviewAlternatives':('ProposalReference',wp(both(EXCP,pred('ReviewObstructionDeclared',REV),pred('ReviewSatisfiabilityDeclared',REV)))),'ValueOnlyAxis':('ProposalReference',wp(pred('ProposalConstrainsValueDeclared',P))),'LabelAxis':('ProposalReference',wp(pred('ProposalConstrainsLabelDeclared',P))),'AuthorityStateAxis':('ProposalReference',wp(pred('ProposalConstrainsAuthorityStateDeclared',P))),'SchemaFieldAxis':('ProposalReference',wp(pred('ProposalConstrainsSchemaFieldDeclared',P))),'ValidationOutcomeAxis':('ProposalReference',wp(pred('ProposalConstrainsValidationOutcomeDeclared',P)))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for n in INSTANCE_ACTUAL:
  target=pred('InstanceActual'+n,I);rows.append({'query_id':'Instance-not-Actual'+n,'target':allof([('InvariantInstanceReference','i')],implies(IAPP,target)),'witness_condition':exists([('InvariantInstanceReference','i')],both(IAPP,neg(target))),'source_condition':'selected-invariant','selected_in_T':False,'source_fidelity':'pending'})
 for n in PROPOSAL_ACTUAL:
  scope=both(PAPP,WATCH) if n in ['GovernanceStop','PromotionBlocked','ReviewComplete','ConstraintSafety','NoObstruction'] else PAPP;target=pred('ProposalActual'+n,P);rows.append({'query_id':'Proposal-not-Actual'+n,'target':allof([('ProposalReference','p')],implies(scope,target)),'witness_condition':exists([('ProposalReference','p')],both(scope,neg(target))),'source_condition':'watch-triggered-proposal' if n in ['GovernanceStop','PromotionBlocked','ReviewComplete','ConstraintSafety','NoObstruction'] else 'selected-proposal','selected_in_T':False,'source_fidelity':'pending'})
 for n in EXCEPTION_ACTUAL:
  scope=both(PAPP,WATCH,EXCP);target=pred('ExceptionActual'+n,EXC);rows.append({'query_id':'Exception-not-Actual'+n,'target':allof([('ProposalReference','p')],implies(scope,target)),'witness_condition':exists([('ProposalReference','p')],both(scope,neg(target))),'source_condition':'watch-triggered-recorded-exception','selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';texts=dict(co.string_leaves(doc));rows=[]
 chosen={'/boundaries/0':(PROPOSAL_BOUNDARIES,['operational']),'/scope/applicability':(both(PROPOSAL_GENUS,VALUE_CLASSIFICATION,CYCLE_CLASSIFICATION,WATCH_CLASSIFICATION,STOP_RULE,EXCEPTION_RULE,INFLUENCE_RULE),['operational']),'/scope/authority_scope_ref':(INSTANCE_GENUS,['operational']),'/scope/exclusions/0':(both(INSTANCE_BOUNDARIES,PROPOSAL_BOUNDARIES,EXCEPTION_BOUNDARIES),['operational']),'/scope/exclusions/1':(INSTANCE_BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(PROPOSAL_BOUNDARIES,['operational']),F:(both(VALUE_CLASSIFICATION,CYCLE_CLASSIFICATION,WATCH_CLASSIFICATION,STOP_RULE,EXCEPTION_RULE,INFLUENCE_RULE,PROPOSAL_BOUNDARIES,EXCEPTION_BOUNDARIES),['axiomatic-implicit']),'/voices/scientific_formal/testable_conditions/0':(INSTANCE_GENUS,['operational']),'/voices/scientific_formal/testable_conditions/1':(ip(pred('InstanceSourceDigestsCurrentDeclared',I)),['operational']),'/voices/scientific_formal/testable_conditions/2':(ip(pred('InstanceDefinitionSchemaValidDeclared',I)),['operational']),'/voices/scientific_formal/testable_conditions/3':(ip(pred('InstanceProjectionExactDeclared',I)),['operational'])}
 for unit in co.inventory(doc):
  sel=unit['selector'];text=texts[sel]
  if sel==N:
   marker='\n\nBound source-semantic basis:\n\n';cut=text.index(marker);parts=[(0,text[:cut],INSTANCE_GENUS,['genus-differentia']),(cut,text[cut:],both(PROPOSAL_GENUS,VALUE_CLASSIFICATION,CYCLE_CLASSIFICATION,WATCH_CLASSIFICATION,STOP_RULE,EXCEPTION_RULE,INFLUENCE_RULE,INSTANCE_BOUNDARIES,PROPOSAL_BOUNDARIES,EXCEPTION_BOUNDARIES),['axiomatic-implicit'])]
  else:
   formula,forms=chosen.get(sel,(None,['unresolved']));parts=[(0,text,formula,forms)]
  for start,excerpt,formula,forms in parts:
   disp='encoded' if formula is not None else ('explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred')
   rows.append({'source_selector':sel,'start_character':start,'excerpt':excerpt,'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 for row in selected_clauses(doc):
  cid='CCS-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];why={'encoded':'Necessary classified-instance,typed value/cycle watch,stop and exact reviewed exception declarations;actual safety,obstruction,review adequacy,owner acceptance and effects independent.','explanatory':'Scientific notation,plain intuition and domain examples remain explanatory;prove-safe phrasing is not a contextuality theorem.','deferred':'Historical reconstructed candidate ceiling under exact C53 overlay and source-owner correspondence remain explicit;no authority inferred.'}[disp]
  clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':why});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Selected/outside,harmless/risky,typed review alternatives and independent outcomes are separate candidate coverage obligations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe and source/consumer denotations remain pending owner review.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:constraint-cycle-safety-watch-reviewed-exception-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'CCS-FINDING-'+str(i+1).zfill(3),'issue':z,'resolution':'unresolved','review_ref':None} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified invariant,source,relation,review,witness,residue and governance meanings;no whole theories or accepted maps imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'watch-stopped-with-recorded-reviewed-exception','scenario':'A value-constraining proposal permits effective cycles;it records a governance stop and an exact owner/evidence/semantics/review/witness/residue exception before declared influence approval.','expected_interpretation':'Necessary declarations hold without actual safety,owner acceptance or authority inferred.','rationale':'Watch,review and independent actual safety stay distinct.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'risky-influence-without-exception','scenario':'A watched proposal declares influence approval without a recorded exception.','expected_interpretation':'Influence guard fails.','rationale':'Dangerous proposals require exact review coordinates before influence.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Instance-not-ActualSourceFidelity','Proposal-not-ActualAuthority']
  if clause['source_selector']=='/voices/scientific_formal/normative_statement':targets+=['Proposal-not-ActualConstraintSafety','Exception-not-ActualOwnerAcceptance']
  if clause['source_selector'] in ['/scope/applicability','/voices/scientific_formal/formal_expression']:targets+=['Proposal-not-ActualGovernanceStop','Proposal-not-ActualReviewComplete','Exception-not-ActualReviewAdequacy','Exception-not-ActualWitnessValidity','Exception-not-ActualConstraintSatisfiability']
  if clause['source_selector'].endswith('/testable_conditions/1'):targets+=['Instance-not-ActualSourceCurrentness']
  if clause['source_selector'].endswith('/testable_conditions/2'):targets+=['Instance-not-ActualDefinitionShape']
  if clause['source_selector'].endswith('/testable_conditions/3'):targets+=['Instance-not-ActualProjectionFidelity']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'cycle_permission':'effective-iff-declared-permission-and-not-explicit-acyclicity','watch':'value-constraining-and-effective-cycle-permission','exception':'exact-owner-proposal-scope-evidence-semantics-review-witness-typed-residue-with-conditional-alternatives','timing':'historical-stop-and-review-required-retained-before-declared-influence-approval','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary typed watch,stop and reviewed-exception declarations only;actual safety,obstruction,owner acceptance,authority,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()

