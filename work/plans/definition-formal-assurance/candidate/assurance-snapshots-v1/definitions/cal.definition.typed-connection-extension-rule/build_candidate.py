"""Exact Typed Connection Extension Rule closed ordered-pair/version/qualifier/authority declarations."""
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
SCOPE='scope:candidate:typed-connection-extension-closed-ordered-pairs-exact-contracts-v1'
SORTS=['ContractReference','RelationKindReference','QuestionReference','EndpointKindReference','EndpointContractReference','PairReference','DirectionReference','QualifierSchemaReference','ValueDomainReference','CrossConstraintReference','AuthorityReference','ContestabilityReference','OwnerReference','EvidenceReference','LifecycleEffectReference','ValidationEffectReference','AuthorityEffectRuleReference','ProposalReference','ScopeReference','OntologyContractReference','InstanceReference','ObjectReference','QualifierValuesReference','Token']
CONSTANTS={'EMPTY':'Token'}
CONTRACT_FIELDS={'contractKind':'RelationKindReference','contractQuestion':'QuestionReference','contractScope':'ScopeReference'}
ENDPOINT_FIELDS={'endpointKind':'EndpointKindReference'}
PAIR_FIELDS={'pairContract':'ContractReference','pairSourceKind':'EndpointKindReference','pairTargetKind':'EndpointKindReference','pairSourceEndpoint':'EndpointContractReference','pairTargetEndpoint':'EndpointContractReference','pairDirection':'DirectionReference','pairSchema':'QualifierSchemaReference','pairValues':'ValueDomainReference','pairConstraints':'CrossConstraintReference','pairAuthority':'AuthorityReference','pairContestability':'ContestabilityReference','pairOwner':'OwnerReference','pairEvidence':'EvidenceReference','pairLifecycle':'LifecycleEffectReference','pairValidation':'ValidationEffectReference','pairEffectRules':'AuthorityEffectRuleReference'}
PROPOSAL_FIELDS={'proposalSourceKind':'EndpointKindReference','proposalTargetKind':'EndpointKindReference','proposalDirection':'DirectionReference','proposalScope':'ScopeReference','proposalOwner':'OwnerReference','proposalEvidence':'EvidenceReference'}
GLOBAL_FIELDS={'proposalPredecessor':'ContractReference','proposalSuccessor':'ContractReference','proposalNewPair':'PairReference'}
LOCAL_FIELDS={'proposalOntology':'OntologyContractReference'}
INSTANCE_FIELDS={'instanceContract':'ContractReference','instanceSource':'ObjectReference','instanceTarget':'ObjectReference','instanceDirection':'DirectionReference','instanceQualifiers':'QualifierValuesReference'}
INSTANCE_PAIR_FIELDS={'instancePair':'PairReference'}
OBJECT_FIELDS={'objectKind':'EndpointKindReference'}
GROUPS=[(CONTRACT_FIELDS,'ContractReference'),(ENDPOINT_FIELDS,'EndpointContractReference'),(PAIR_FIELDS,'PairReference'),(PROPOSAL_FIELDS,'ProposalReference'),(GLOBAL_FIELDS,'ProposalReference'),(LOCAL_FIELDS,'ProposalReference'),(INSTANCE_FIELDS,'InstanceReference'),(INSTANCE_PAIR_FIELDS,'InstanceReference'),(OBJECT_FIELDS,'ObjectReference')]
FUNCTIONS={n:([carrier],sort) for fs,carrier in GROUPS for n,sort in fs.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
CONTRACT_EXCLUDED=['ContractCartesianAuthorizationDeclared','ContractWildcardAuthorizationDeclared','ContractDirectoryNamingAuthorizationDeclared','ContractObservedHistoryAuthorizationDeclared','DefinitionAdmissionAdmitsConnectionDeclared','DefinitionCreatesRuntimeDeclared']
PAIR_EXCLUDED=['PairIsObjectRelationInstanceDeclared','EndpointAdmissionCreatesConnectionDeclared','ConnectionAdmitsEndpointCarrierDeclared','ConnectionAdmitsQualifierSchemaDeclared','ConnectionCreatesRelationInstanceDeclared','ConnectionValidatesRelationInstanceDeclared','ConnectionAdmitsRelationInstanceDeclared','ConnectionActivatesRelationInstanceDeclared','ConnectionProvesRelationInstanceDeclared','PairDualWritableAuthorityDeclared','PairAuthorityLabelGrantsRightsDeclared']
PROPOSAL_EXCLUDED=['LocalUseCreatesGlobalConnectionDeclared','SharedNamingCreatesConnectionDeclared','CandidateValidationAdmitsConnectionDeclared','EndpointRegistrationCreatesConnectionDeclared','SecondProjectionCreatesAuthorityDeclared','ProposalCreatesActualAuthorityDeclared','ProposalCreatesRuntimeDeclared','ProposalCreatesPublicationDeclared','ProposalCreatesExternalEffectDeclared']
INSTANCE_EXCLUDED=['StructuralConformanceAdmitsConnectionDeclared','InstanceLabelProvesActualConformanceDeclared','ConnectionAdmissionProvesInstanceDeclared','InstanceCreatesUnrestrictedAuthorityDeclared']
CONTRACT_ACTUAL=['FiniteClosedSet','EffectiveVersionResolution','QuestionFidelity','PairSetFidelity','IndexProjectionFidelity','SourceFidelity','Authority','Proof']
PAIR_ACTUAL=['OrderedPairFidelity','EndpointResolution','EndpointAdmission','QualifierSchemaValidity','ValueDomainValidity','CrossConstraintValidity','CanonicalAuthorityFidelity','Contestability','OwnerValidity','EvidenceAdequacy','LifecycleValidity','ValidationAdequacy','GlobalAvailability','Authority']
PROPOSAL_ACTUAL=['PredecessorResolution','SuccessorBinding','SameQuestion','NoCollapse','QualifierCompatibility','LocalScopeFidelity','GlobalAdmission','GlobalEffectiveness','OwnerAuthorization','Authority']
INSTANCE_ACTUAL=['EndpointObjectResolution','EndpointKindFidelity','DirectionFidelity','QualifierValidation','PairMembership','ContractAdmission','Conformance','Activation','Authority','Proof']
CFLAGS=['ContractApplicable','ContractInScopeDeclared','ContractGlobalDeclared','ContractFiniteDeclared','ContractClosedDeclared','ContractAdmittedDeclared','ContractEffectiveDeclared']
RFLAGS=['PairApplicable','PairInScopeDeclared','PairAvailableDeclared','PairStructureDeclared','PairTypedRelationCanonicalDeclared','PairSpecializedCanonicalDeclared','PairSpecializedPresentDeclared','PairProjectsAsDeclared','PairRepresentedByDeclared','PairTypedRelationWritableDeclared','PairSpecializedWritableDeclared','PairQualifierNoCollapseDeclared']
PFLAGS=['ProposalApplicable','ProposalInScopeDeclared','ProposalGlobalDeclared','ProposalLocalDeclared','ProposalReuseDeclared','ProposalDistinctDeclared','ProposalRejectedDeclared','ProposalCandidateValidatedDeclared','ProposalAdmissionRecordedDeclared','ProposalGlobalAvailableDeclared']
IFLAGS=['InstanceApplicable','InstanceInScopeDeclared','InstanceConformingDeclared']
SIGNATURE={n:['ContractReference'] for n in CFLAGS+CONTRACT_EXCLUDED+['ContractActual'+n for n in CONTRACT_ACTUAL]}
SIGNATURE.update({n:['PairReference'] for n in RFLAGS+PAIR_EXCLUDED+['PairActual'+n for n in PAIR_ACTUAL]})
SIGNATURE.update({n:['ProposalReference'] for n in PFLAGS+PROPOSAL_EXCLUDED+['ProposalActual'+n for n in PROPOSAL_ACTUAL]})
SIGNATURE.update({n:['InstanceReference'] for n in IFLAGS+INSTANCE_EXCLUDED+['InstanceActual'+n for n in INSTANCE_ACTUAL]})
for sort in SORTS:
 if sort not in ['ContractReference','PairReference','ProposalReference','InstanceReference','Token']:SIGNATURE[sort+'Declared']=[sort]
for fs,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fs.items()})
SIGNATURE.update({'KindRegisteredDeclared':['EndpointKindReference'],'KindWildcardDeclared':['EndpointKindReference'],'KindCatchAllDeclared':['EndpointKindReference'],'EndpointResolvedDeclared':['EndpointContractReference'],'EndpointAdmittedCarrierDeclared':['EndpointContractReference'],'EndpointGovernedInternalDeclared':['EndpointContractReference'],'EndpointPermittedByContractDeclared':['ContractReference','EndpointContractReference'],'SchemaClosedDeclared':['QualifierSchemaReference'],'PairValueDomainBoundDeclared':['PairReference','ValueDomainReference'],'PairCrossConstraintBoundDeclared':['PairReference','CrossConstraintReference'],'AuthorityTypedRelationDeclared':['AuthorityReference'],'AuthoritySpecializedDeclared':['AuthorityReference'],'ContestOwnerRouteDeclared':['ContestabilityReference','OwnerReference'],'PairQuestionFitsDeclared':['PairReference','QuestionReference'],'OntologyExactScopedDeclared':['OntologyContractReference','ScopeReference'],'ProposalExactAdmissionDeclared':['ProposalReference','ContractReference','PairReference'],'ConnDeclared':['ContractReference','EndpointKindReference','EndpointKindReference'],'AvailableConnDeclared':['ContractReference','EndpointKindReference','EndpointKindReference'],'SourceIndexDeclared':['ContractReference','EndpointKindReference'],'TargetIndexDeclared':['ContractReference','EndpointKindReference'],'PairSchemaValidatedDeclared':['PairReference','QualifierValuesReference'],'PairValuesAcceptedDeclared':['PairReference','QualifierValuesReference'],'PairCrossConstraintsSatisfiedDeclared':['PairReference','QualifierValuesReference']})
for n in ['RelationKind','Pair','Qualifiers','Endpoints','Instance']:SIGNATURE['ContestCovers'+n+'Declared']=['ContestabilityReference']
def iff(a,z):return {'op':'iff','left':a,'right':z}
def xor(a,z):return both(either(a,z),neg(both(a,z)))
C=var('c');R=var('r');P=var('p');I=var('i');S=var('s');T=var('t')
CAPP=pred('ContractApplicable',C);RAPP=pred('PairApplicable',R);PAPP=pred('ProposalApplicable',P);IAPP=pred('InstanceApplicable',I)
def member(sort):return {'ContractReference':'ContractApplicable','PairReference':'PairApplicable','ProposalReference':'ProposalApplicable','InstanceReference':'InstanceApplicable'}.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def cs(z):return allof([('ContractReference','c')],implies(CAPP,z))
def rs(z):return allof([('PairReference','r')],implies(RAPP,z))
def ps(z):return allof([('ProposalReference','p')],implies(PAPP,z))
def ins(z):return allof([('InstanceReference','i')],implies(IAPP,z))
def rf(n):return fn(n,R)
def pf(n):return fn(n,P)
RC=rf('pairContract');SK=rf('pairSourceKind');TK=rf('pairTargetKind');SE=rf('pairSourceEndpoint');TE=rf('pairTargetEndpoint');AUTH=rf('pairAuthority');CONTEST=rf('pairContestability')
GLOBAL=pred('ProposalGlobalDeclared',P);LOCAL=pred('ProposalLocalDeclared',P);PRED=pf('proposalPredecessor');SUCC=pf('proposalSuccessor');NEW=pf('proposalNewPair');REUSE=pred('ProposalReuseDeclared',P);DISTINCT=pred('ProposalDistinctDeclared',P);REJECT=pred('ProposalRejectedDeclared',P)
def conn(c,s,t):return pred('ConnDeclared',c,s,t)
def eligible(c,ep,k):return both(exact(ENDPOINT_FIELDS,ep),eq(fn('endpointKind',ep),k),pred('EndpointResolvedDeclared',ep),either(pred('EndpointAdmittedCarrierDeclared',ep),both(pred('EndpointGovernedInternalDeclared',ep),pred('EndpointPermittedByContractDeclared',c,ep))),neg(pred('KindWildcardDeclared',k)),neg(pred('KindCatchAllDeclared',k)))
CONTRACT_RULE=allof([('ContractReference','c')],both(iff(CAPP,pred('ContractInScopeDeclared',C)),implies(CAPP,both(guard('ContractReference',C),exact(CONTRACT_FIELDS,C),pred('ContractGlobalDeclared',C),pred('ContractFiniteDeclared',C),pred('ContractClosedDeclared',C),implies(pred('ContractEffectiveDeclared',C),pred('ContractAdmittedDeclared',C))))))
CATALOGUE=cs(allof([('EndpointKindReference','s'),('EndpointKindReference','t')],both(iff(conn(C,S,T),exists([('PairReference','r')],both(RAPP,eq(RC,C),eq(SK,S),eq(TK,T)))),iff(pred('AvailableConnDeclared',C,S,T),both(conn(C,S,T),pred('ContractAdmittedDeclared',C),pred('ContractEffectiveDeclared',C))))))
INDEXES=cs(both(allof([('EndpointKindReference','s')],iff(pred('SourceIndexDeclared',C,S),exists([('EndpointKindReference','t')],conn(C,S,T)))),allof([('EndpointKindReference','t')],iff(pred('TargetIndexDeclared',C,T),exists([('EndpointKindReference','s')],conn(C,S,T))))))
PAIR_STRUCTURE=both(guard('PairReference',R),exact(PAIR_FIELDS,R),eligible(RC,SE,SK),eligible(RC,TE,TK),pred('SchemaClosedDeclared',rf('pairSchema')),pred('PairValueDomainBoundDeclared',R,rf('pairValues')),pred('PairCrossConstraintBoundDeclared',R,rf('pairConstraints')),pred('ContestOwnerRouteDeclared',CONTEST,rf('pairOwner')),*[pred('ContestCovers'+n+'Declared',CONTEST) for n in ['RelationKind','Pair','Qualifiers','Endpoints','Instance']],pred('PairQuestionFitsDeclared',R,fn('contractQuestion',RC)),pred('PairQualifierNoCollapseDeclared',R))
PAIR_DEFINITION=allof([('PairReference','r')],both(iff(RAPP,pred('PairInScopeDeclared',R)),implies(RAPP,iff(pred('PairStructureDeclared',R),PAIR_STRUCTURE))))
PAIR_RULE=rs(both(pred('PairStructureDeclared',R),iff(pred('PairAvailableDeclared',R),both(pred('ContractAdmittedDeclared',RC),pred('ContractEffectiveDeclared',RC)))))
AUTHORITY_RULE=rs(both(xor(pred('PairTypedRelationCanonicalDeclared',R),pred('PairSpecializedCanonicalDeclared',R)),iff(pred('PairTypedRelationCanonicalDeclared',R),pred('AuthorityTypedRelationDeclared',AUTH)),iff(pred('PairSpecializedCanonicalDeclared',R),pred('AuthoritySpecializedDeclared',AUTH)),implies(pred('PairSpecializedCanonicalDeclared',R),pred('PairSpecializedPresentDeclared',R)),iff(pred('PairProjectsAsDeclared',R),pred('PairSpecializedCanonicalDeclared',R)),iff(pred('PairRepresentedByDeclared',R),both(pred('PairTypedRelationCanonicalDeclared',R),pred('PairSpecializedPresentDeclared',R))),iff(pred('PairTypedRelationWritableDeclared',R),pred('PairTypedRelationCanonicalDeclared',R)),iff(pred('PairSpecializedWritableDeclared',R),pred('PairSpecializedCanonicalDeclared',R))))
PROPOSAL_GENUS=allof([('ProposalReference','p')],both(iff(PAPP,pred('ProposalInScopeDeclared',P)),implies(PAPP,both(guard('ProposalReference',P),exact(PROPOSAL_FIELDS,P),xor(GLOBAL,LOCAL)))))
GLOBAL_RULE=ps(implies(GLOBAL,both(exact(GLOBAL_FIELDS,P),pred('ContractAdmittedDeclared',PRED),pred('ContractEffectiveDeclared',PRED),eq(fn('pairContract',NEW),SUCC),eq(fn('pairSourceKind',NEW),pf('proposalSourceKind')),eq(fn('pairTargetKind',NEW),pf('proposalTargetKind')),eq(fn('pairDirection',NEW),pf('proposalDirection')),eq(fn('pairOwner',NEW),pf('proposalOwner')),eq(fn('pairEvidence',NEW),pf('proposalEvidence')),eq(fn('contractScope',SUCC),pf('proposalScope')),either(REUSE,DISTINCT,REJECT),neg(both(REUSE,DISTINCT)),neg(both(REUSE,REJECT)),neg(both(DISTINCT,REJECT)),implies(REUSE,both(eq(fn('contractKind',PRED),fn('contractKind',SUCC)),eq(fn('contractQuestion',PRED),fn('contractQuestion',SUCC)),pred('PairQuestionFitsDeclared',NEW,fn('contractQuestion',PRED)),pred('PairQualifierNoCollapseDeclared',NEW),neg(conn(PRED,pf('proposalSourceKind'),pf('proposalTargetKind'))),allof([('EndpointKindReference','s'),('EndpointKindReference','t')],iff(conn(SUCC,S,T),either(conn(PRED,S,T),both(eq(S,pf('proposalSourceKind')),eq(T,pf('proposalTargetKind')))))))),implies(DISTINCT,neg(eq(fn('contractKind',PRED),fn('contractKind',SUCC)))),implies(REJECT,neg(pred('ProposalGlobalAvailableDeclared',P))),implies(pred('ProposalAdmissionRecordedDeclared',P),pred('ProposalExactAdmissionDeclared',P,SUCC,NEW)),implies(pred('ProposalGlobalAvailableDeclared',P),both(neg(REJECT),pred('ProposalAdmissionRecordedDeclared',P),pred('ContractAdmittedDeclared',SUCC),pred('ContractEffectiveDeclared',SUCC),pred('PairAvailableDeclared',NEW))))))
SIGNATURE['ProposalGlobalStructureDeclared']=['ProposalReference']
GLOBAL_STRUCTURE=GLOBAL_RULE['body']['args'][1]['args'][1]
assert GLOBAL_STRUCTURE['op']=='and'
GLOBAL_DEFINITION=ps(implies(GLOBAL,iff(pred('ProposalGlobalStructureDeclared',P),GLOBAL_STRUCTURE)))
GLOBAL_RULE=ps(implies(GLOBAL,pred('ProposalGlobalStructureDeclared',P)))
LOCAL_RULE=ps(implies(LOCAL,both(exact(LOCAL_FIELDS,P),pred('OntologyExactScopedDeclared',pf('proposalOntology'),pf('proposalScope')),neg(pred('ProposalGlobalAvailableDeclared',P)),neg(pred('ProposalAdmissionRecordedDeclared',P)))))
INSTANCE_GENUS=allof([('InstanceReference','i')],both(iff(IAPP,pred('InstanceInScopeDeclared',I)),implies(IAPP,both(guard('InstanceReference',I),exact(INSTANCE_FIELDS,I),exact(OBJECT_FIELDS,fn('instanceSource',I)),exact(OBJECT_FIELDS,fn('instanceTarget',I))))))
IR=fn('instancePair',I);IC=fn('instanceContract',I);IQ=fn('instanceQualifiers',I)
INSTANCE_RULE=ins(implies(pred('InstanceConformingDeclared',I),both(exact(INSTANCE_PAIR_FIELDS,I),eq(fn('pairContract',IR),IC),eq(fn('pairSourceKind',IR),fn('objectKind',fn('instanceSource',I))),eq(fn('pairTargetKind',IR),fn('objectKind',fn('instanceTarget',I))),eq(fn('pairDirection',IR),fn('instanceDirection',I)),pred('ContractAdmittedDeclared',IC),pred('ContractEffectiveDeclared',IC),pred('AvailableConnDeclared',IC,fn('objectKind',fn('instanceSource',I)),fn('objectKind',fn('instanceTarget',I))),pred('PairSchemaValidatedDeclared',IR,IQ),pred('PairValuesAcceptedDeclared',IR,IQ),pred('PairCrossConstraintsSatisfiedDeclared',IR,IQ))))
BOUNDARIES=both(cs(both(*[neg(pred(n,C)) for n in CONTRACT_EXCLUDED])),rs(both(*[neg(pred(n,R)) for n in PAIR_EXCLUDED])),ps(both(*[neg(pred(n,P)) for n in PROPOSAL_EXCLUDED])),ins(both(*[neg(pred(n,I)) for n in INSTANCE_EXCLUDED])))
THEORY={'contract':CONTRACT_RULE,'catalogue':CATALOGUE,'indexes':INDEXES,'pair-definition':PAIR_DEFINITION,'pair':PAIR_RULE,'authority':AUTHORITY_RULE,'proposal-genus':PROPOSAL_GENUS,'global-definition':GLOBAL_DEFINITION,'global':GLOBAL_RULE,'local':LOCAL_RULE,'instance-genus':INSTANCE_GENUS,'instance':INSTANCE_RULE,'boundaries':BOUNDARIES}
LOSSES=[
'Exact C64 Definition admission does not admit RelationKind contracts,endpoints,pairs,qualifier schemas,instances or this formal translation.',
'Contract,pair row,proposal and object relation instance are separate sorted carriers;ordered kind pairs are not instance edges.',
'Finite closed catalogue is proposed as exact selected-row membership plus a finite declaration;finite model domains do not prove unbounded-source finiteness.',
'Source/target indexes are existential discovery projections and cannot authorize their Cartesian product.',
'Endpoint kinds/contracts,direction,schemas,value domains,cross-constraints,authority,contestability,owner,evidence,lifecycle,validation,effect rules and question references need accepted denotations.',
'Endpoint eligibility permits admitted carrier or explicitly permitted governed internal record alternatives;actual resolution/admission remains independent.',
'Wildcard/catch-all endpoint flags are excluded on selected pair kinds;real naming and classifier maps remain unresolved.',
'PairStructure and ProposalGlobalStructure are definitional abbreviations whose full exact guards remain in primary theory;they are not authenticated semantic facts.',
'Closed schema,pair-specific value domain and cross-constraint bindings are necessary declarations,not executed qualifier validation.',
'Canonical TypedRelation versus specialized authority is exclusive;projects-as/represented-by and writable flags are proposed exact mappings,not actual write grants.',
'Generic authority without a specialized carrier does not fabricate specialized presence or represented-by mappings.',
'Contestability covers relation kind,pair,qualifiers,endpoints and instance with exact owner route;actual contest access and owner authority remain independent.',
'Global and ontology-local proposal scopes are exclusive;local ontology nomination does not add a global row or grant global availability.',
'Global proposals bind exact effective predecessor,successor,new row and source/target/direction/owner/evidence/scope coordinates.',
'Reuse requires same kind/question and noncollapsing qualifier compatibility;successor exact old-pairs-plus-one-new-pair is an explicit proposed preservation interpretation.',
'Distinct kind proposals require different nominated kind;the source does not invent globally unique question-to-kind cardinality.',
'Changed-question same-kind proposals can remain rejected;rejected proposals acquire no global availability and need an accepted rejection/runtime map.',
'Candidate validation is independent of exact successor admission;available proposals require exact admission binding and admitted/effective successor.',
'Admitted contracts may remain ineffective;admission is necessary for effectiveness without invented automatic activation.',
'Conforming-instance declarations require actual-kind nominations,available exact ordered pair,direction and three qualifier guards;actual conformance/validation independent.',
'Nonconforming-instance unused pair fields and local unused global fields do not fabricate carriers,contracts or relations.',
'Exact local upstream Definitions and symbolic consumer routes stay separate evidence;no whole upstream theories or private routing meaning imported.',
'Complete character accounting and supplied finite T/I controls do not prove whole translation,shared denotations,source fidelity or whole-definition proof.'
]
def required_populations():
 def wc(z):return exists([('ContractReference','c')],both(CAPP,z))
 def wr(z):return exists([('PairReference','r')],both(RAPP,z))
 def wp(z):return exists([('ProposalReference','p')],both(PAPP,z))
 def wi(z):return exists([('InstanceReference','i')],both(IAPP,z))
 return {'GlobalContract':('ContractReference',wc(CAPP)),'OutsideContract':('ContractReference',exists([('ContractReference','c')],neg(CAPP))),'CandidateContract':('ContractReference',wc(neg(pred('ContractAdmittedDeclared',C)))),'AdmittedEffectiveContract':('ContractReference',wc(both(pred('ContractAdmittedDeclared',C),pred('ContractEffectiveDeclared',C)))),'DeclaredPair':('PairReference',wr(RAPP)),'OutsidePair':('PairReference',exists([('PairReference','r')],neg(RAPP))),'CandidatePairUnavailable':('PairReference',wr(neg(pred('PairAvailableDeclared',R)))),'AdmittedPairAvailable':('PairReference',wr(pred('PairAvailableDeclared',R))),'TypedRelationAuthority':('PairReference',wr(pred('PairTypedRelationCanonicalDeclared',R))),'SpecializedAuthority':('PairReference',wr(pred('PairSpecializedCanonicalDeclared',R))),'TypedWithSpecializedProjection':('PairReference',wr(both(pred('PairTypedRelationCanonicalDeclared',R),pred('PairSpecializedPresentDeclared',R)))),'TypedWithoutSpecialized':('PairReference',wr(both(pred('PairTypedRelationCanonicalDeclared',R),neg(pred('PairSpecializedPresentDeclared',R))))),'AdmittedEndpointCarrier':('PairReference',wr(pred('EndpointAdmittedCarrierDeclared',SE))),'PermittedInternalEndpoint':('PairReference',wr(both(pred('EndpointGovernedInternalDeclared',TE),pred('EndpointPermittedByContractDeclared',RC,TE)))),'GlobalReuseProposal':('ProposalReference',wp(both(GLOBAL,REUSE))),'GlobalDistinctProposal':('ProposalReference',wp(both(GLOBAL,DISTINCT))),'LocalProposal':('ProposalReference',wp(LOCAL)),'OutsideProposal':('ProposalReference',exists([('ProposalReference','p')],neg(PAPP))),'ValidatedUnadmittedProposal':('ProposalReference',wp(both(GLOBAL,pred('ProposalCandidateValidatedDeclared',P),neg(pred('ProposalAdmissionRecordedDeclared',P))))),'AdmittedAvailableProposal':('ProposalReference',wp(both(GLOBAL,pred('ProposalAdmissionRecordedDeclared',P),pred('ProposalGlobalAvailableDeclared',P)))),'ConformingInstance':('InstanceReference',wi(pred('InstanceConformingDeclared',I))),'NonconformingInstance':('InstanceReference',wi(neg(pred('InstanceConformingDeclared',I)))),'OutsideInstance':('InstanceReference',exists([('InstanceReference','i')],neg(IAPP))),'IndependentAuthority':('PairReference',wr(pred('PairActualAuthority',R))),'PairWithoutActualOutcomes':('PairReference',wr(both(*[neg(pred('PairActual'+n,R)) for n in PAIR_ACTUAL]))),'UnconnectedRegisteredKind':('EndpointKindReference',exists([('EndpointKindReference','k')],both(pred('KindRegisteredDeclared','k'),allof([('ContractReference','c'),('EndpointKindReference','t')],implies(CAPP,both(neg(conn(C,var('k'),T)),neg(conn(C,T,var('k'))))))))),'CartesianCrossPairNotDeclared':('ContractReference',wc(exists([('EndpointKindReference','s'),('EndpointKindReference','t')],both(pred('SourceIndexDeclared',C,S),pred('TargetIndexDeclared',C,T),neg(conn(C,S,T)))))),'ReversePairNotImplicit':('PairReference',wr(neg(conn(RC,TK,SK))))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for prefix,carrier,varname,names,app in [('Contract','ContractReference','c',CONTRACT_ACTUAL,CAPP),('Pair','PairReference','r',PAIR_ACTUAL,RAPP),('Proposal','ProposalReference','p',PROPOSAL_ACTUAL,PAPP),('Instance','InstanceReference','i',INSTANCE_ACTUAL,IAPP)]:
  for n in names:
   condition=None;label='selected-'+prefix.lower()
   if prefix=='Pair' and n=='GlobalAvailability':condition=pred('PairAvailableDeclared',R);label='declared-available-pair'
   if prefix=='Proposal' and n in ['PredecessorResolution','SuccessorBinding','GlobalAdmission','GlobalEffectiveness','NoCollapse','QualifierCompatibility']:condition=GLOBAL;label='global-proposal'
   if prefix=='Proposal' and n=='SameQuestion':condition=both(GLOBAL,REUSE);label='global-reuse-proposal'
   if prefix=='Proposal' and n=='LocalScopeFidelity':condition=LOCAL;label='ontology-local-proposal'
   if prefix=='Instance' and n in ['Conformance','PairMembership','DirectionFidelity','QualifierValidation','ContractAdmission']:condition=pred('InstanceConformingDeclared',I);label='declared-conforming-instance'
   scope=app if condition is None else both(app,condition);value=var(varname);target=pred(prefix+'Actual'+n,value);rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(carrier,varname)],implies(scope,target)),'witness_condition':exists([(carrier,varname)],both(scope,neg(target))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 rows=[]
 primary=both(*THEORY.values());formal=both(CATALOGUE,INDEXES,PAIR_RULE,AUTHORITY_RULE,GLOBAL_RULE,LOCAL_RULE,INSTANCE_RULE,BOUNDARIES)
 bounds=[PAIR_RULE,INDEXES,BOUNDARIES,PAIR_RULE,PAIR_RULE,LOCAL_RULE,AUTHORITY_RULE,PAIR_RULE,GLOBAL_RULE,BOUNDARIES,GLOBAL_RULE,BOUNDARIES]
 sci=[CATALOGUE,INDEXES,GLOBAL_RULE,PAIR_RULE,PAIR_RULE,AUTHORITY_RULE,LOCAL_RULE,PAIR_RULE,both(PAIR_RULE,GLOBAL_RULE)]
 tests=[CATALOGUE,PAIR_RULE,INDEXES,GLOBAL_RULE,PAIR_RULE,PAIR_RULE,LOCAL_RULE,AUTHORITY_RULE,PAIR_RULE,BOUNDARIES,GLOBAL_RULE,GLOBAL_RULE]
 excl=[BOUNDARIES,INDEXES,GLOBAL_RULE,PAIR_RULE,LOCAL_RULE,AUTHORITY_RULE,GLOBAL_RULE]
 for unit in co.inventory(doc):
  sel=unit['selector'];text=dict(co.string_leaves(doc))[sel];formula=None;forms=['unresolved']
  if sel=='/voices/scientific_formal/normative_statement':formula=primary;forms=['genus-differentia']
  elif sel=='/voices/scientific_formal/formal_expression':formula=formal;forms=['axiomatic-implicit']
  elif sel.startswith('/boundaries/'):formula=bounds[int(sel.split('/')[-1])];forms=['operational']
  elif sel.startswith('/voices/scientific_formal/boundary_conditions/'):formula=sci[int(sel.split('/')[-1])];forms=['operational']
  elif sel.startswith('/voices/scientific_formal/testable_conditions/'):formula=tests[int(sel.split('/')[-1])];forms=['operational']
  elif sel=='/scope/applicability':formula=both(PROPOSAL_GENUS,GLOBAL_RULE,LOCAL_RULE);forms=['operational']
  elif sel.startswith('/scope/exclusions/'):formula=excl[int(sel.split('/')[-1])];forms=['operational']
  disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred'
  rows.append({'source_selector':sel,'start_character':0,'excerpt':text,'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows

def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 for row in selected_clauses(doc):
  cid='TCX-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];why={'encoded':'Necessary exact ordered-pair/version/endpoint/qualifier/canonical-authority/global-local/instance declarations;actual resolution,validation,admission,conformance and authority independent.','explanatory':'Scientific notation,plug-and-wire intuition and domain examples remain explanatory;no actual global connection or authority inferred.','deferred':'C64 candidate ceiling and authority-scope correspondence remain explicit;no connection admission or authority inferred.'}[disp]
  clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':why});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Selected/outside,candidate/admitted,ordered-pair,canonical-authority,global/local and conforming/nonconforming scenarios are independent candidate coverage obligations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe and source/consumer denotations remain pending owner review.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:typed-connection-extension-closed-ordered-pairs-exact-contracts-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'TCX-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with RelationKind,endpoint,qualifier,canonical-authority,contestability,lifecycle,validation and ontology owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified RelationKind,endpoint,qualifier,canonical-authority,contestability,lifecycle,validation,ontology and governance meanings;no whole theories or accepted maps imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'candidate-reuse-and-admitted-distinct-pair','scenario':'A candidate reuse proposal preserves the predecessor ordered pairs and adds one exact pair;an independently admitted distinct-kind contract supplies an available pair. Local proposals remain scoped.','expected_interpretation':'Necessary typed declarations hold without real pair availability,resolution,qualifier validation or authority inferred.','rationale':'Ordered pairs,contract versions and global/local authority stay separate.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'cartesian-cross-pair-inference','scenario':'A discovery source-kind/target-kind cross pair is added without a selected declared row.','expected_interpretation':'Exact catalogue closure fails.','rationale':'Separate indexes cannot authorize their Cartesian product.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}

 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Contract-not-ActualSourceFidelity','Pair-not-ActualAuthority']
  if clause['source_selector'] in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:targets+=['Pair-not-ActualOrderedPairFidelity','Proposal-not-ActualSuccessorBinding','Instance-not-ActualConformance']
  if 'boundary' in clause['source_selector']:targets+=['Pair-not-ActualCanonicalAuthorityFidelity','Pair-not-ActualEndpointResolution']
  if 'testable_conditions' in clause['source_selector']:targets+=['Pair-not-ActualQualifierSchemaValidity','Proposal-not-ActualGlobalAdmission']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'catalogue':'exact-selected-ordered-row-membership-with-existential-discovery-indexes','availability':'admitted-and-effective-contract-separate-from-candidate-pair-set','reuse':'same-kind-question-and-exact-old-pairs-plus-one-new-pair','authority':'exclusive-generic-or-specialized-with-conditional-projection-and-single-writer','scope_separation':'global-and-exact-ontology-local-with-unused-fields-not-fabricated','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary ordered-pair/version/qualifier/authority/global-local declarations only;real resolution,admission,validation,conformance,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()

