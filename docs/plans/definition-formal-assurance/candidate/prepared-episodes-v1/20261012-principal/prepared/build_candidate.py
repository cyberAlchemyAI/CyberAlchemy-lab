"""Exact Principal recognition,reference,represented-subject and current-grant declarations."""
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
SCOPE='scope:candidate:principal-recognition-reference-subject-current-grant-v1'
SORTS=['PrincipalReference','PrincipalIdentityReference','BoundaryReference','IssuerReference','ScopeReference','PrincipalUseReference','RepresentationReference','SubjectReference','SubjectIdentityReference','LifecycleReference','SubjectKindReference','AuthorizationReference','GrantReference','TimeReference','Token']
CONSTANTS={'EMPTY':'Token'}
PRINCIPAL_FIELDS={'principalIdentity':'PrincipalIdentityReference','principalBoundary':'BoundaryReference','principalScope':'ScopeReference','principalIssuer':'IssuerReference'}
BOUNDARY_FIELDS={'boundaryIssuer':'IssuerReference','boundaryScope':'ScopeReference'}
USE_FIELDS={'usePrincipal':'PrincipalReference','useIdentity':'PrincipalIdentityReference','useIssuerBoundary':'BoundaryReference'}
REPRESENTATION_FIELDS={'representationPrincipal':'PrincipalReference','representationBeforeSubject':'SubjectReference','representationAfterSubject':'SubjectReference'}
SUBJECT_FIELDS={'subjectIdentity':'SubjectIdentityReference','subjectLifecycle':'LifecycleReference','subjectKind':'SubjectKindReference'}
AUTHORIZATION_FIELDS={'authorizationPrincipal':'PrincipalReference','authorizationScope':'ScopeReference','authorizationTime':'TimeReference'}
AUTHORIZATION_GRANT_FIELDS={'authorizationGrant':'GrantReference'}
GRANT_FIELDS={'grantIssuer':'IssuerReference'}
GROUPS=[(PRINCIPAL_FIELDS,'PrincipalReference'),(BOUNDARY_FIELDS,'BoundaryReference'),(USE_FIELDS,'PrincipalUseReference'),(REPRESENTATION_FIELDS,'RepresentationReference'),(SUBJECT_FIELDS,'SubjectReference'),(AUTHORIZATION_FIELDS,'AuthorizationReference'),(AUTHORIZATION_GRANT_FIELDS,'AuthorizationReference'),(GRANT_FIELDS,'GrantReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
ROOT_EXCLUDED=['PrincipalProvesPersonIdentityDeclared','PrincipalProvesAgentCapabilityDeclared','PrincipalProvesRoleAssignmentDeclared','PrincipalIdentityCreatesOwnershipDeclared','PrincipalIdentityCreatesPermissionDeclared','PrincipalIdentityGrantsAuthorityDeclared','PrincipalIdentityGrantsUnrestrictedAuthorityDeclared','PrincipalIsPersonDeclared','PrincipalIsActorDeclared','PrincipalIsAgentDeclared','PrincipalIsTeamDeclared','PrincipalIsRoleDeclared','ParentMeaningGrantsAuthorityDeclared','DefinitionAdmissionAcceptsTranslationDeclared','RecognitionReferenceAuthenticatesIssuerDeclared','RecognitionBoundaryGrantsAuthorityDeclared','PrincipalDefinitionCreatesCarrierDeclared','PrincipalDefinitionCreatesInstanceDeclared','PrincipalDefinitionCreatesRelationDeclared','PrincipalDefinitionCreatesPolicyDeclared','PrincipalDefinitionCreatesDecisionDeclared','RuntimeEffectGrantedDeclared','PublicationEffectGrantedDeclared','ReleaseEffectGrantedDeclared','DeploymentEffectGrantedDeclared','ExternalEffectGrantedDeclared']
USE_EXCLUDED=['UseReferenceAuthenticatesIdentityDeclared','UseIssuerLabelAuthenticatesBoundaryDeclared','UseIdentityCreatesRoleDeclared','UseIdentityCreatesCapabilityDeclared','UseIdentityCreatesOwnershipDeclared','UseIdentityCreatesPermissionDeclared','UseIdentityCreatesAuthorityDeclared']
REP_EXCLUDED=['RepresentationMergesSubjectIdentityDeclared','RepresentationChangesSubjectLifecycleDeclared','RepresentationTransfersSubjectAuthorityDeclared','RepresentationProvesPersonOrAgentIdentityDeclared']
AUTH_EXCLUDED=['AuthorizationInferredFromPrincipalIdentityDeclared','GrantReferenceAuthenticatesIssuerDeclared','GrantLabelProvesCurrentnessDeclared','ScopeLabelProvesApplicabilityDeclared','AuthorizationGrantsBeyondSelectedScopeDeclared','CurrentGrantDeclarationProvesActualAuthorityDeclared','AuthorizationDeclarationCreatesExternalEffectDeclared','AuthorizationCreatesUnrestrictedAuthorityDeclared']
ROOT_ACTUAL=['RecognizedIdentity','BoundaryRecognition','IssuerAuthenticity','IdentityResolution','PersonIdentity','AgentCapability','RoleAssignment','Ownership','Permission','Authority','GrantAuthority','Authentication','Authorization','Accountability','SubjectIndependence','SourceFidelity','ConsumerAlignment','SharedConsistency','Proof','Admission','Activation','Publication','Deployment','ExternalEffect']
USE_ACTUAL=['IdentityResolution','IssuerResolution','BoundaryAuthenticity','IdentityFidelity','OneIdentityResolution','SourceFidelity','Permission','Authority']
REP_ACTUAL=['SubjectIdentityPreservation','LifecyclePreservation','SubjectIndependence','SubjectResolution','KindFidelity','Authority']
AUTH_ACTUAL=['Authorization','GrantResolution','GrantCurrentness','GrantIssuerAuthenticity','GrantScopeApplicability','GrantPrincipalApplicability','ScopeFidelity','Permission','Authority','ExternalEffect']
SIGNATURE={n:['PrincipalReference'] for n in ['PrincipalApplicable','PrincipalInScopeDeclared','PrincipalGovernedDeclared','PrincipalRecognizedIdentityDeclared','PrincipalBoundedScopeDeclared','PrincipalIdentityBackedDeclared','PrincipalRecordBackedDeclared',*ROOT_EXCLUDED,*['PrincipalActual'+n for n in ROOT_ACTUAL]]}
SIGNATURE.update({n:['PrincipalUseReference'] for n in ['UseApplicable','UseInScopeDeclared','UseRecordedDeclared','UseExactResolutionDeclared',*USE_EXCLUDED,*['UseActual'+n for n in USE_ACTUAL]]})
SIGNATURE.update({n:['RepresentationReference'] for n in ['RepresentationApplicable','RepresentationInScopeDeclared','RepresentationRecordedDeclared',*REP_EXCLUDED,*['RepresentationActual'+n for n in REP_ACTUAL]]})
SIGNATURE.update({n:['AuthorizationReference'] for n in ['AuthorizationApplicable','AuthorizationInScopeDeclared','AuthorizationRecordedDeclared','AuthorizationConsequentialDeclared','AuthorizationExactCurrentGrantDeclared',*AUTH_EXCLUDED,*['AuthorizationActual'+n for n in AUTH_ACTUAL]]})
for sort in SORTS:
 if sort not in ['PrincipalReference','PrincipalUseReference','RepresentationReference','AuthorizationReference','Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'PrincipalIdentityGovernedDeclared':['PrincipalIdentityReference'],'BoundaryRecordedDeclared':['BoundaryReference'],'BoundaryAuthenticationDeclared':['BoundaryReference'],'BoundaryAuthorizationDeclared':['BoundaryReference'],'BoundaryOwnershipDeclared':['BoundaryReference'],'BoundaryAccountabilityDeclared':['BoundaryReference'],'SubjectGovernedDeclared':['SubjectReference'],'KindPersonDeclared':['SubjectKindReference'],'KindTeamDeclared':['SubjectKindReference'],'KindServiceDeclared':['SubjectKindReference'],'KindAgentDeclared':['SubjectKindReference'],'GrantRecordedDeclared':['GrantReference'],'GrantCurrentAtDeclared':['GrantReference','TimeReference'],'GrantAppliesToPrincipalDeclared':['GrantReference','PrincipalReference'],'GrantAppliesToScopeDeclared':['GrantReference','ScopeReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
P=var('p');U=var('u');R=var('r');A=var('a');P_APP=pred('PrincipalApplicable',P);U_APP=pred('UseApplicable',U);R_APP=pred('RepresentationApplicable',R);A_APP=pred('AuthorizationApplicable',A);CONSEQ=pred('AuthorizationConsequentialDeclared',A)
def guard(sort,value):
 member={'PrincipalReference':'PrincipalApplicable','PrincipalUseReference':'UseApplicable','RepresentationReference':'RepresentationApplicable','AuthorizationReference':'AuthorizationApplicable'}.get(sort,sort+'Declared')
 return both(pred(member,value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'value')],iff(pred(n+'BindingDeclared',value,'value'),eq(var('value'),fn(n,value))))) for n,sort in fields.items()])
def selected(z):return allof([('PrincipalReference','p')],implies(P_APP,z))
def use_selected(z):return allof([('PrincipalUseReference','u')],implies(U_APP,z))
def rep_selected(z):return allof([('RepresentationReference','r')],implies(R_APP,z))
def auth_selected(z):return allof([('AuthorizationReference','a')],implies(A_APP,z))
IDENTITY=fn('principalIdentity',P);BOUNDARY=fn('principalBoundary',P);BEFORE=fn('representationBeforeSubject',R);AFTER=fn('representationAfterSubject',R);AUTH_PRINCIPAL=fn('authorizationPrincipal',A);GRANT=fn('authorizationGrant',A);AUTH_SCOPE=fn('authorizationScope',A);AUTH_TIME=fn('authorizationTime',A)
GENUS=allof([('PrincipalReference','p')],both(iff(P_APP,pred('PrincipalInScopeDeclared',P)),implies(P_APP,both(guard('PrincipalReference',P),exact(PRINCIPAL_FIELDS,P),pred('PrincipalGovernedDeclared',P),pred('PrincipalRecognizedIdentityDeclared',P),pred('PrincipalBoundedScopeDeclared',P),either(pred('PrincipalIdentityBackedDeclared',P),pred('PrincipalRecordBackedDeclared',P)),pred('PrincipalIdentityGovernedDeclared',IDENTITY),exact(BOUNDARY_FIELDS,BOUNDARY),pred('BoundaryRecordedDeclared',BOUNDARY),either(*[pred(n,BOUNDARY) for n in ['BoundaryAuthenticationDeclared','BoundaryAuthorizationDeclared','BoundaryOwnershipDeclared','BoundaryAccountabilityDeclared']]),eq(fn('principalIssuer',P),fn('boundaryIssuer',BOUNDARY))))))
USE_ELIGIBILITY=allof([('PrincipalUseReference','u')],iff(U_APP,pred('UseInScopeDeclared',U)))
USE_RULE=use_selected(both(guard('PrincipalUseReference',U),exact(USE_FIELDS,U),pred('UseRecordedDeclared',U),pred('UseExactResolutionDeclared',U),eq(fn('useIdentity',U),fn('principalIdentity',fn('usePrincipal',U))),eq(fn('useIssuerBoundary',U),fn('principalBoundary',fn('usePrincipal',U)))))
REP_ELIGIBILITY=allof([('RepresentationReference','r')],iff(R_APP,pred('RepresentationInScopeDeclared',R)))
def subject_record(z):return both(guard('SubjectReference',z),exact(SUBJECT_FIELDS,z),pred('SubjectGovernedDeclared',z))
REP_RULE=rep_selected(both(guard('RepresentationReference',R),exact(REPRESENTATION_FIELDS,R),pred('RepresentationRecordedDeclared',R),subject_record(BEFORE),subject_record(AFTER)))
PRESERVATION=rep_selected(both(eq(fn('subjectIdentity',BEFORE),fn('subjectIdentity',AFTER)),eq(fn('subjectLifecycle',BEFORE),fn('subjectLifecycle',AFTER))))
AUTH_ELIGIBILITY=allof([('AuthorizationReference','a')],iff(A_APP,pred('AuthorizationInScopeDeclared',A)))
AUTH_RULE=auth_selected(both(guard('AuthorizationReference',A),exact(AUTHORIZATION_FIELDS,A),pred('AuthorizationRecordedDeclared',A)))
GRANT_RULE=auth_selected(implies(CONSEQ,both(exact(AUTHORIZATION_GRANT_FIELDS,A),pred('AuthorizationExactCurrentGrantDeclared',A),exact(GRANT_FIELDS,GRANT),pred('GrantRecordedDeclared',GRANT),pred('GrantCurrentAtDeclared',GRANT,AUTH_TIME),pred('GrantAppliesToPrincipalDeclared',GRANT,AUTH_PRINCIPAL),pred('GrantAppliesToScopeDeclared',GRANT,AUTH_SCOPE))))
ROOT_BOUNDARIES=selected(both(*[neg(pred(n,P)) for n in ROOT_EXCLUDED]))
USE_BOUNDARIES=use_selected(both(*[neg(pred(n,U)) for n in USE_EXCLUDED]))
REP_BOUNDARIES=rep_selected(both(*[neg(pred(n,R)) for n in REP_EXCLUDED]))
AUTH_BOUNDARIES=auth_selected(both(*[neg(pred(n,A)) for n in AUTH_EXCLUDED]))
THEORY={'genus':GENUS,'use-eligibility':USE_ELIGIBILITY,'use':USE_RULE,'representation-eligibility':REP_ELIGIBILITY,'representation':REP_RULE,'preservation':PRESERVATION,'authorization-eligibility':AUTH_ELIGIBILITY,'authorization':AUTH_RULE,'grant':GRANT_RULE,'root-boundaries':ROOT_BOUNDARIES,'use-boundaries':USE_BOUNDARIES,'representation-boundaries':REP_BOUNDARIES,'authorization-boundaries':AUTH_BOUNDARIES}
LOSSES=[
 'Exact C65 Principal Definition admission does not create identities,recognition,authorization,grants,carriers or accept this translation.',
 'Governed identity recognized at a boundary is necessary declaration structure,not actual authentication or authorization.',
 'Principal,identity,boundary,issuer,scope,use,representation,subject,subject identity,lifecycle,kind,authorization,grant,time and Token are proposed qualified sorts.',
 'Inclusive governed identity-or-record flags need source-owner precedence correspondence to the positive identity genus.',
 'Four recognition alternatives are inclusive,not a disjoint enum;overlapping authentication/authorization/ownership/accountability boundaries remain possible.',
 'Principal and recognition-boundary scope nominations are separate;no unsupported scope equality is imposed.',
 'Principal issuer agrees with the nominated boundary issuer by declaration;actual issuer authenticity remains independent.',
 'Selected reference use has exact principal,one identity and issuer-boundary nominations;this does not impose global one-Principal-per-person or boundary uniqueness.',
 'Exact reference-resolution declarations do not authenticate the referenced identity or actual lookup result.',
 'Abstract selected Principal roots may have no modeled reference use,representation or authorization;finite scope does not enumerate all real Principals.',
 'Represented subjects retain independent typed identity/lifecycle coordinates;Principal and subject identity carriers are not collapsed.',
 'Before/after subject references may differ when identity/lifecycle agree;actual preservation and continuity need accepted maps.',
 'Subject kind may change independently while identity/lifecycle remain preserved;no unsupported kind-preservation axiom is invented.',
 'Named Person/Team/service/Agent kinds are modeled separately without requiring every possible subject to lie in a closed four-kind taxonomy.',
 'Every selected authorization names Principal,scope and evaluation-time references;time has no invented ordering or timestamp validity.',
 'Only consequential authorization activates exact current grant requirements;unused nonconsequential grant selectors do not fabricate authority.',
 'CurrentAt is a grant/time relation,not a single timestamp function;real validity intervals,revocation and currentness remain separate.',
 'Grant applicability to Principal and scope are relations,not global single-Principal/single-scope grant cardinalities.',
 'Grant issuer may differ from the Principal recognition issuer;delegation and independent grant authority need accepted scope maps.',
 'Identity/reference/recognition/representation/authorization declarations do not prove Person identity,Agent capability,Role,ownership,permission or authority.',
 'Exact local actor-model-review and integrated consumer stay review evidence;no private routing-package meaning or runtime evidence is imported.',
 'Complete character accounting and supplied finite T/I controls do not accept shared denotations,source fidelity,whole translation or whole-definition proof.'
]
def required_populations():
 def withp(z):return exists([('PrincipalReference','p')],both(P_APP,z))
 def withu(z):return exists([('PrincipalUseReference','u')],both(U_APP,z))
 def withr(z):return exists([('RepresentationReference','r')],both(R_APP,z))
 def witha(z):return exists([('AuthorizationReference','a')],both(A_APP,z))
 ps={'SelectedPrincipal':('PrincipalReference',withp(P_APP)),'OutsidePrincipal':('PrincipalReference',exists([('PrincipalReference','p')],neg(P_APP))),'PrincipalWithoutActualOutcomes':('PrincipalReference',withp(both(*[neg(pred('PrincipalActual'+n,P)) for n in ROOT_ACTUAL]))),'IndependentAuthority':('PrincipalReference',withp(pred('PrincipalActualAuthority',P))),'IdentityOnlyPrincipal':('PrincipalReference',withp(both(pred('PrincipalIdentityBackedDeclared',P),neg(pred('PrincipalRecordBackedDeclared',P))))),'RecordOnlyPrincipal':('PrincipalReference',withp(both(pred('PrincipalRecordBackedDeclared',P),neg(pred('PrincipalIdentityBackedDeclared',P))))),'IdentityAndRecordPrincipal':('PrincipalReference',withp(both(pred('PrincipalIdentityBackedDeclared',P),pred('PrincipalRecordBackedDeclared',P)))),'PrincipalWithoutAuthorization':('PrincipalReference',withp(neg(exists([('AuthorizationReference','a')],both(A_APP,eq(AUTH_PRINCIPAL,P)))))),'ReferenceUse':('PrincipalUseReference',withu(U_APP)),'OutsideReferenceUse':('PrincipalUseReference',exists([('PrincipalUseReference','u')],neg(U_APP))),'UseWithoutActualOutcomes':('PrincipalUseReference',withu(both(*[neg(pred('UseActual'+n,U)) for n in USE_ACTUAL]))),'Representation':('RepresentationReference',withr(R_APP)),'OutsideRepresentation':('RepresentationReference',exists([('RepresentationReference','r')],neg(R_APP))),'DifferentSubjectReferencesPreserved':('RepresentationReference',withr(neg(eq(BEFORE,AFTER)))),'SameSubjectReferencePreserved':('RepresentationReference',withr(eq(BEFORE,AFTER))),'RepresentationWithoutActualOutcomes':('RepresentationReference',withr(both(*[neg(pred('RepresentationActual'+n,R)) for n in REP_ACTUAL]))),'ConsequentialAuthorization':('AuthorizationReference',witha(CONSEQ)),'NonconsequentialAuthorization':('AuthorizationReference',witha(neg(CONSEQ))),'OutsideAuthorization':('AuthorizationReference',exists([('AuthorizationReference','a')],neg(A_APP))),'ConsequentialWithoutActualOutcomes':('AuthorizationReference',witha(both(CONSEQ,*[neg(pred('AuthorizationActual'+n,A)) for n in AUTH_ACTUAL]))),'GrantIssuerDifferentFromRecognitionIssuer':('AuthorizationReference',witha(both(CONSEQ,neg(eq(fn('grantIssuer',GRANT),fn('principalIssuer',AUTH_PRINCIPAL)))))),'OverlappingRecognitionKinds':('PrincipalReference',withp(both(pred('BoundaryAuthorizationDeclared',BOUNDARY),pred('BoundaryOwnershipDeclared',BOUNDARY))))}
 for n in ['Authentication','Authorization','Ownership','Accountability']:ps[n+'Recognition']=('PrincipalReference',withp(pred('Boundary'+n+'Declared',BOUNDARY)))
 return ps
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for carrier,prefix,names,varname,app in [('PrincipalReference','Principal',ROOT_ACTUAL,'p',P_APP),('PrincipalUseReference','Use',USE_ACTUAL,'u',U_APP),('RepresentationReference','Representation',REP_ACTUAL,'r',R_APP),('AuthorizationReference','Authorization',AUTH_ACTUAL,'a',both(A_APP,CONSEQ))]:
  value=var(varname)
  for n in names:rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(carrier,varname)],implies(app,pred(prefix+'Actual'+n,value))),'witness_condition':exists([(carrier,varname)],both(app,neg(pred(prefix+'Actual'+n,value)))),'source_condition':'selected-consequential-authorization' if prefix=='Authorization' else 'selected-'+prefix.lower(),'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
 chosen={N:(both(*THEORY.values()),['genus-differentia']),F:(GENUS,['axiomatic-implicit']),'/scope/applicability':(GENUS,['operational']),'/scope/exclusions/0':(GENUS,['operational']),'/scope/exclusions/1':(PRESERVATION,['operational']),'/scope/exclusions/2':(both(ROOT_BOUNDARIES,GRANT_RULE),['operational']),'/scope/exclusions/3':(ROOT_BOUNDARIES,['operational']),'/boundaries/0':(GENUS,['operational']),'/boundaries/1':(PRESERVATION,['operational']),'/boundaries/2':(both(ROOT_BOUNDARIES,GRANT_RULE),['operational']),'/voices/scientific_formal/boundary_conditions/0':(GENUS,['operational']),'/voices/scientific_formal/boundary_conditions/1':(PRESERVATION,['operational']),'/voices/scientific_formal/boundary_conditions/2':(both(ROOT_BOUNDARIES,GRANT_RULE),['operational']),'/voices/scientific_formal/testable_conditions/0':(USE_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(GRANT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(ROOT_BOUNDARIES,['operational'])}
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];formula=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Authority-scope correspondence and retained candidate claim ceiling need owner maps;no actual recognition or grant.'
  if sel in chosen:formula,forms=chosen[sel];disposition='encoded';roles=['definition'];why='Necessary Principal recognition/reference,independent subject identity/lifecycle and consequential-current-grant/scope declarations;actual recognition,identity,rights and authority remain independent.'
  elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):disposition='explanatory';forms=['unresolved'];roles=['explanation-example'];why='Notation,intuition and human Principal/machine Agent file-update example remain explanatory;no actual recognition,authorization or grant inferred.'
  cid='PRIN-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(text.encode()),'start_character':0,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':len(text),'excerpt':text})
 deps=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);required=required_populations();populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Authored Principal/use/representation/authorization,identity-or-record,recognition kinds,independent issuer/scope and current-grant witnesses.','review_ref':None} for n,(carrier,z) in required.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual Principal/identity/boundary/issuer/subject/grant/time/scope universes and shared source denotations require acceptance.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:principal-recognition-reference-subject-current-grant-v1','profile_ref':'profile:principal-recognition-reference-subject-current-grant-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'PRIN-FINDING-'+str(i).zfill(3),'description':x,'selectors':[N,F,'/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Principal,issuer,recognition,reference,subject,grant,scope and consumer owners'} for i,x in enumerate(LOSSES,1)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Qualified identity/recognition/grant/Role/capability/governance meanings;no whole upstream theories or accepted operational maps imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'recognized-Principal-with-exact-current-scoped-grant','scenario':'A reference nominates exact governed Principal identity and issuer boundary;consequential authorization cites a current grant applicable to its Principal and scope.','expected_interpretation':'Necessary declarations hold without actual issuer authenticity,Person identity,permission or authority inferred.','rationale':'Recognition and independent grant authority remain separate.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'consequential-authorization-stale-grant','scenario':'A consequential authorization nominates a grant lacking currentness at its evaluation time.','expected_interpretation':'Necessary current-grant guard fails.','rationale':'A Principal identity and grant label cannot replace current scope-specific applicability.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account.get('character_accounting_complete') is True,account
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  sel=clause['source_selector'];targets=['Principal-not-ActualRecognizedIdentity','Principal-not-ActualAuthority']
  if sel in [N,F]:targets+=['Principal-not-ActualPersonIdentity','Principal-not-ActualAgentCapability','Principal-not-ActualRoleAssignment']
  if sel=='/voices/scientific_formal/testable_conditions/0':targets+=['Use-not-ActualIdentityResolution','Use-not-ActualIssuerResolution','Use-not-ActualOneIdentityResolution']
  if sel in ['/scope/exclusions/1','/boundaries/1','/voices/scientific_formal/boundary_conditions/1']:targets+=['Representation-not-ActualSubjectIdentityPreservation','Representation-not-ActualLifecyclePreservation']
  if sel in ['/scope/exclusions/2','/boundaries/2','/voices/scientific_formal/boundary_conditions/2','/voices/scientific_formal/testable_conditions/1']:targets+=['Authorization-not-ActualGrantCurrentness','Authorization-not-ActualGrantScopeApplicability','Authorization-not-ActualAuthority']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:obligations.append({'source':source,'selector':sel,'start_character':0,'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False});counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(required),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'recognition':'inclusive-four-boundary-alternatives-with-exact-identity-issuer-nominations','reference':'one-exact-Principal-identity-and-issuer-boundary-per-selected-use','subject':'independent-before-after-identity-and-lifecycle-preserved-kind-not-forced-equal','grant':'consequential-only-exact-currentAt-Principal-and-scope-applicability-relations','scopes':'Principal-recognition-and-authorization-scopes-separate-no-unsupported-equality','issuers':'grant-issuer-independent-of-recognition-issuer','actual_query_scopes':'Principal-use-representation-and-consequential-authorization-separate','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 comp=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comp,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comp]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary governed recognition,exact references,independent subjects and consequential current scoped grant declarations only;actual recognition,issuer authenticity,grant authority,permission,fidelity and proof pending.'});c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
