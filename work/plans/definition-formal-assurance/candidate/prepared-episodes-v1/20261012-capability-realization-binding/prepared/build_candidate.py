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

# Source-qualified proposed descriptors; these do not create canonical Definitions.
SCOPE='scope:candidate:CapabilityRealizationBinding-exact-endpoints-canonical-authority-projection-succession-v1'
SORTS=['BindingRevisionReference','CapabilityRevisionReference','ImplementationCollectionReference','ImplementationRevisionReference','RealizationRoleReference','AdoptionPostureReference','CompatibilityReference','EvidenceCollectionReference','DeploymentApplicabilityReference','OwnerReference','LifecycleReference','SuccessionRouteReference','ChallengeHandlingReference','AssociationReference','CanonicalAuthorityReference','DigestReference','ProjectionReference','ChangeReference','EvidenceRoleReference','Token']
CONSTANTS={'EMPTY':'Token',**{n+'_ROLE':'EvidenceRoleReference' for n in ['ADOPTION','CONFORMANCE','DEPLOYMENT','OUTCOME']}}
FIELDS={'bindingCapabilityRevision':'CapabilityRevisionReference','bindingImplementationRevisions':'ImplementationCollectionReference','bindingRealizationRole':'RealizationRoleReference','bindingAdoptionPosture':'AdoptionPostureReference','bindingCompatibility':'CompatibilityReference','bindingConformanceEvidence':'EvidenceCollectionReference','bindingDeploymentApplicability':'DeploymentApplicabilityReference','bindingOwner':'OwnerReference','bindingLifecycle':'LifecycleReference','bindingSuccessionRoute':'SuccessionRouteReference','bindingChallengeHandling':'ChallengeHandlingReference','bindingAssociation':'AssociationReference','bindingCanonicalAuthority':'CanonicalAuthorityReference','bindingAdoptionEvidence':'EvidenceCollectionReference','bindingDeploymentEvidence':'EvidenceCollectionReference','bindingOutcomeEvidence':'EvidenceCollectionReference'}
PROJECTION_FIELDS={'bindingProjection':'ProjectionReference','bindingDigest':'DigestReference'}
ASSOCIATION_FIELDS={'associationCanonicalAuthority':'CanonicalAuthorityReference'}
PROJECTION_RECORD_FIELDS={'projectionBinding':'BindingRevisionReference','projectionAssociation':'AssociationReference','projectionDigest':'DigestReference'}
CHANGE_FIELDS={'changeOriginalBinding':'BindingRevisionReference','changeDesiredCapability':'CapabilityRevisionReference','changeDesiredImplementations':'ImplementationCollectionReference','changeDesiredAdoptionPosture':'AdoptionPostureReference'}
SUCCESSOR_FIELDS={'changeSuccessorBinding':'BindingRevisionReference'}
GROUPS=[(FIELDS,'BindingRevisionReference'),(PROJECTION_FIELDS,'BindingRevisionReference'),(ASSOCIATION_FIELDS,'AssociationReference'),(PROJECTION_RECORD_FIELDS,'ProjectionReference'),(CHANGE_FIELDS,'ChangeReference'),(SUCCESSOR_FIELDS,'ChangeReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()}
HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'}
FUNCTIONS.update({name:([sort],'Token') for sort,name in HANDLES.items()})
EXCLUDED=['BindingIsProductCapabilityDeclared','BindingIsImplementationDeclared','BindingConfersAuthorityEffectDeclared','BindingPostureProvesAdoptionDeclared','BindingConformanceProvesDeploymentDeclared']
ACTUAL=['EndpointResolution','Canonicality','LifecycleOperation','Realization','Adoption','Deployment','Conformance','SuccessfulOperation','ProductValue','OwnerAuthorization','Compatibility','EvidenceAuthenticity','Governance','Boundedness','AuthorityEffect','Admission','RuntimeActivation','Publication','SourceFidelity','ConsumerAlignment','WholeProof']
PROJECTION_ACTUAL=['Authenticity','DigestCorrectness','ReadOnlyEnforcement','SemanticAlignment','Publication','AuthorizedUse','WholeProof']
CHANGE_ACTUAL=['SuccessorCreation','EndpointResolution','HistoryAuthenticity','Adoption','WholeProof']
SIGNATURE={n:['BindingRevisionReference'] for n in ['BindingApplicable','BindingInScopeDeclared','BindingLifecycleBearingDeclared','BindingCanonicalAssociationDeclared','BindingGovernedDeclared','BindingBoundedDeclared','BindingHasProjectionDeclared',*EXCLUDED,*['BindingActual'+n for n in ACTUAL]]}
SIGNATURE.update({n:['ProjectionReference'] for n in ['ProjectionApplicable','ProjectionInScopeDeclared','ProjectionReadOnlyDeclared','ProjectionSecondWritableAuthorityDeclared',*['ProjectionActual'+n for n in PROJECTION_ACTUAL]]})
SIGNATURE.update({n:['ChangeReference'] for n in ['ChangeApplicable','ChangeInScopeDeclared',*['ChangeActual'+n for n in CHANGE_ACTUAL]]})
for sort in SORTS:
 if sort!='Token':SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update(ImplementationCollectionContainsDeclared=['ImplementationCollectionReference','ImplementationRevisionReference'],BindingImplementationMemberDeclared=['BindingRevisionReference','ImplementationRevisionReference'],CapabilityRevisionExactDeclared=['CapabilityRevisionReference'],ImplementationRevisionExactDeclared=['ImplementationRevisionReference'],CanonicalAuthorityForAssociationDeclared=['AssociationReference','CanonicalAuthorityReference'],ProjectionForBindingDeclared=['BindingRevisionReference','ProjectionReference'],EvidenceForPurposeDeclared=['BindingRevisionReference','EvidenceRoleReference','EvidenceCollectionReference'],SuccessorBindingRevisionDeclared=['BindingRevisionReference','BindingRevisionReference'])
MAP={'BindingRevisionReference':'BindingApplicable','ProjectionReference':'ProjectionApplicable','ChangeReference':'ChangeApplicable'}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'target')],iff(pred(n+'BindingDeclared',value,'target'),eq(var('target'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,name,body):return allof([(sort,name)],implies(pred(member(sort),name),body))
B=var('b');P=var('p');C=var('c');M=var('m');A=var('a');E=var('e')
APP=pred('BindingApplicable',B);PROJ=pred('ProjectionApplicable',P);CH=pred('ChangeApplicable',C)
CAP=fn('bindingCapabilityRevision',B);COL=fn('bindingImplementationRevisions',B);ASSOC=fn('bindingAssociation',B)
ROOT_RULE=both(allof([('BindingRevisionReference','b')],iff(APP,pred('BindingInScopeDeclared',B))),selected('BindingRevisionReference','b',both(guard('BindingRevisionReference',B),exact(FIELDS,B),pred('BindingLifecycleBearingDeclared',B),pred('BindingCanonicalAssociationDeclared',B))))
GOVERNANCE=selected('BindingRevisionReference','b',both(pred('BindingGovernedDeclared',B),pred('BindingBoundedDeclared',B)))
def collection_guard(collection):return both(guard('ImplementationCollectionReference',collection),exists([('ImplementationRevisionReference','m')],pred('ImplementationCollectionContainsDeclared',collection,M)),allof([('ImplementationRevisionReference','m')],implies(pred('ImplementationCollectionContainsDeclared',collection,M),both(guard('ImplementationRevisionReference',M),pred('ImplementationRevisionExactDeclared',M)))))
ENDPOINT_RULE=selected('BindingRevisionReference','b',both(pred('CapabilityRevisionExactDeclared',CAP),collection_guard(COL),allof([('ImplementationRevisionReference','m')],iff(pred('BindingImplementationMemberDeclared',B,M),pred('ImplementationCollectionContainsDeclared',COL,M)))))
AUTHORITY_RULE=selected('BindingRevisionReference','b',both(exact(ASSOCIATION_FIELDS,ASSOC),eq(fn('bindingCanonicalAuthority',B),fn('associationCanonicalAuthority',ASSOC)),allof([('CanonicalAuthorityReference','a')],iff(pred('CanonicalAuthorityForAssociationDeclared',ASSOC,A),eq(A,fn('associationCanonicalAuthority',ASSOC))))))
EVIDENCE_FIELDS={'ADOPTION':'bindingAdoptionEvidence','CONFORMANCE':'bindingConformanceEvidence','DEPLOYMENT':'bindingDeploymentEvidence','OUTCOME':'bindingOutcomeEvidence'}
roles=list(EVIDENCE_FIELDS)
EVIDENCE_RULE=both(*[guard('EvidenceRoleReference',const(n+'_ROLE')) for n in roles],*[neg(eq(const(x+'_ROLE'),const(y+'_ROLE'))) for i,x in enumerate(roles) for y in roles[i+1:]],selected('BindingRevisionReference','b',allof([('EvidenceRoleReference','role'),('EvidenceCollectionReference','e')],iff(pred('EvidenceForPurposeDeclared',B,'role',E),either(*[both(eq(var('role'),const(n+'_ROLE')),eq(E,fn(field,B))) for n,field in EVIDENCE_FIELDS.items()])))))
PROJECTION_RULE=both(allof([('ProjectionReference','p')],iff(PROJ,pred('ProjectionInScopeDeclared',P))),selected('BindingRevisionReference','b',both(allof([('ProjectionReference','p')],iff(pred('ProjectionForBindingDeclared',B,P),both(pred('BindingHasProjectionDeclared',B),eq(P,fn('bindingProjection',B))))),implies(pred('BindingHasProjectionDeclared',B),both(exact(PROJECTION_FIELDS,B),exact(PROJECTION_RECORD_FIELDS,fn('bindingProjection',B)),eq(fn('projectionBinding',fn('bindingProjection',B)),B),eq(fn('projectionAssociation',fn('bindingProjection',B)),ASSOC),eq(fn('projectionDigest',fn('bindingProjection',B)),fn('bindingDigest',B)))))),selected('ProjectionReference','p',both(guard('ProjectionReference',P),exact(PROJECTION_RECORD_FIELDS,P),pred('ProjectionReadOnlyDeclared',P),neg(pred('ProjectionSecondWritableAuthorityDeclared',P)),pred('BindingHasProjectionDeclared',fn('projectionBinding',P)),eq(fn('bindingProjection',fn('projectionBinding',P)),P))))
def collection_difference(left,right):return exists([('ImplementationRevisionReference','m')],either(both(pred('ImplementationCollectionContainsDeclared',left,M),neg(pred('ImplementationCollectionContainsDeclared',right,M))),both(pred('ImplementationCollectionContainsDeclared',right,M),neg(pred('ImplementationCollectionContainsDeclared',left,M)))))
ORIGINAL=fn('changeOriginalBinding',C);SUCCESSOR=fn('changeSuccessorBinding',C)
CAP_DELTA=neg(eq(fn('bindingCapabilityRevision',ORIGINAL),fn('changeDesiredCapability',C)))
IMPL_DELTA=collection_difference(fn('bindingImplementationRevisions',ORIGINAL),fn('changeDesiredImplementations',C))
POSTURE_DELTA=neg(eq(fn('bindingAdoptionPosture',ORIGINAL),fn('changeDesiredAdoptionPosture',C)))
DELTA=either(CAP_DELTA,IMPL_DELTA,POSTURE_DELTA)
SUCCESSION_RULE=both(allof([('ChangeReference','c')],iff(CH,pred('ChangeInScopeDeclared',C))),selected('ChangeReference','c',both(guard('ChangeReference',C),exact(CHANGE_FIELDS,C),pred('CapabilityRevisionExactDeclared',fn('changeDesiredCapability',C)),collection_guard(fn('changeDesiredImplementations',C)),implies(DELTA,both(exact(SUCCESSOR_FIELDS,C),neg(eq(ORIGINAL,SUCCESSOR)),pred('SuccessorBindingRevisionDeclared',ORIGINAL,SUCCESSOR),eq(fn('bindingCapabilityRevision',SUCCESSOR),fn('changeDesiredCapability',C)),neg(collection_difference(fn('bindingImplementationRevisions',SUCCESSOR),fn('changeDesiredImplementations',C))),eq(fn('bindingAdoptionPosture',SUCCESSOR),fn('changeDesiredAdoptionPosture',C)))))))
BOUNDARIES=selected('BindingRevisionReference','b',both(*[neg(pred(n,B)) for n in EXCLUDED]))
THEORY={'root-positive-association-and-fields':ROOT_RULE,'governed-and-bounded':GOVERNANCE,'exact-endpoints-and-member-cardinality':ENDPOINT_RULE,'single-canonical-association-authority':AUTHORITY_RULE,'separate-evidence-purpose-roles':EVIDENCE_RULE,'optional-readonly-digest-bound-projection':PROJECTION_RULE,'endpoint-or-posture-change-successor':SUCCESSION_RULE,'role-and-effect-boundaries':BOUNDARIES}
LOSSES=[
'Positive C66 Definition admission is separate from interpretation fidelity, Artifact Type rebinding, instance adoption and any authority effect.',
'Binding is a lifecycle-bearing canonical association; proposed descriptor projections do not rewrite its source or prove actual canonical operation.',
'One exact Capability revision and one-or-more Implementation revision members retain the positive genus; opaque handles and nonempty collections alone do not resolve endpoints.',
'Implementation endpoint change is compared extensionally over nominated revision members; distinct collection handles with equal members do not require a successor.',
'Realization role, posture, compatibility, applicability, owner, lifecycle, succession and challenge are separately typed without inventing a posture taxonomy or real owner authorization.',
'Adoption, conformance, deployment and outcome evidence have distinct purpose roles on one candidate collection carrier; different evidence IDs or disjoint content are not required.',
'Exactly one nominated canonical authority per selected association is explicitly quantified; declaration does not authenticate or authorize that authority.',
'Multiple Binding revisions may share one association authority; no unique latest Binding or global version order is invented.',
'A Typed Relation projection is optional and at most one per selected Binding; unused total-function values do not make a projection mandatory.',
'Projection refers to the exact selected Binding and association and matches its nominated digest; hash equality does not establish cryptographic authenticity or semantic alignment.',
'Projection is declared read-only and cannot declare second writable authority; actual write prevention and authorized use need separate evidence.',
'Selected change desired-state fields stay independent from successor reference, so changed endpoints or posture cannot evade succession by updating one record in place.',
'A changed Capability endpoint, Implementation member set or adoption posture requires a distinct successor revision and exact desired endpoint/posture counterparts.',
'No-change cases may retain the original revision or select a successor for another reason; the source condition is necessary, not a biconditional forbidding other succession.',
'Succession declarations do not create a revision, authenticate retained history or imply unique successors, acyclic global lineage or successful adoption.',
'Governed and bounded declarations are necessary source conditions, not proof of actual governance, physical bounds, permission or budget enforcement.',
'Binding is neither Capability nor Implementation; role exclusions do not depend on nominal sort names or automatically establish cross-system identity maps.',
'Actual adoption, deployment, conformance, successful operation, Product value and authority effect are independent query targets, not premises of T.',
'Candidate upstream Step3 source posture and immutable candidate claim ceiling remain separate from current positive C66 overlays.',
'No whole prior Capability, Implementation, Typed Relation, canonical-representation or authority theory is silently imported.',
'Required T/I populations are finite supplied coverage examples; they do not enumerate actual Bindings, implementations, projections or changes.',
'Original T/O/E/R/J requirements, consumer/owner maps, semantic-cycle review, source fidelity and whole proofs remain outstanding after the typed stage.']
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':s} for n,s in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def required_populations():
 def bw(body):return exists([('BindingRevisionReference','b')],both(APP,body))
 def cw(body):return exists([('ChangeReference','c')],both(CH,body))
 return {'Binding':('BindingRevisionReference',bw(APP)),'OutsideBinding':('BindingRevisionReference',exists([('BindingRevisionReference','b')],neg(APP))),'OneImplementation':('ImplementationRevisionReference',bw(exists([('ImplementationRevisionReference','m')],both(pred('ImplementationCollectionContainsDeclared',COL,M),allof([('ImplementationRevisionReference','other')],implies(pred('ImplementationCollectionContainsDeclared',COL,'other'),eq(var('other'),M))))))),'MultipleImplementations':('ImplementationRevisionReference',bw(exists([('ImplementationRevisionReference','m'),('ImplementationRevisionReference','other')],both(pred('ImplementationCollectionContainsDeclared',COL,M),pred('ImplementationCollectionContainsDeclared',COL,'other'),neg(eq(M,var('other'))))))),'WithoutProjection':('BindingRevisionReference',bw(neg(pred('BindingHasProjectionDeclared',B)))),'WithProjection':('BindingRevisionReference',bw(pred('BindingHasProjectionDeclared',B))),'SharedEvidenceDifferentPurposes':('EvidenceCollectionReference',bw(eq(fn('bindingAdoptionEvidence',B),fn('bindingConformanceEvidence',B)))),'WithoutActualOutcomes':('BindingRevisionReference',bw(both(*[neg(pred('BindingActual'+n,B)) for n in ACTUAL]))),'IndependentAuthorityEffect':('BindingRevisionReference',bw(pred('BindingActualAuthorityEffect',B))),'ConformanceWithoutAuthorityEffect':('BindingRevisionReference',bw(both(pred('BindingActualConformance',B),neg(pred('BindingActualAuthorityEffect',B))))),'Projection':('ProjectionReference',exists([('ProjectionReference','p')],PROJ)),'OutsideProjection':('ProjectionReference',exists([('ProjectionReference','p')],neg(PROJ))),'ProjectionWithoutActualOutcomes':('ProjectionReference',exists([('ProjectionReference','p')],both(PROJ,*[neg(pred('ProjectionActual'+n,P)) for n in PROJECTION_ACTUAL]))),'CapabilityChange':('ChangeReference',cw(CAP_DELTA)),'ImplementationChange':('ChangeReference',cw(IMPL_DELTA)),'PostureChange':('ChangeReference',cw(POSTURE_DELTA)),'NoChangeAliasedCollection':('ChangeReference',cw(both(neg(DELTA),neg(eq(fn('bindingImplementationRevisions',ORIGINAL),fn('changeDesiredImplementations',C)))))),'ChangeWithoutActualOutcomes':('ChangeReference',cw(both(*[neg(pred('ChangeActual'+n,C)) for n in CHANGE_ACTUAL]))),'OutsideChange':('ChangeReference',exists([('ChangeReference','c')],neg(CH)))}
def query_specs():
 rows=[]
 for prefix,sort,name,app,outcomes in [('Binding','BindingRevisionReference','b',APP,ACTUAL),('Projection','ProjectionReference','p',PROJ,PROJECTION_ACTUAL),('Change','ChangeReference','c',CH,CHANGE_ACTUAL)]:
  for outcome in outcomes:rows.append({'query_id':prefix+'-not-Actual'+outcome,'target':allof([(sort,name)],implies(app,pred(prefix+'Actual'+outcome,name))),'witness_condition':exists([(sort,name)],both(app,neg(pred(prefix+'Actual'+outcome,name)))),'selected_in_T':False,'source_condition':'selected-'+prefix.lower(),'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(GOVERNANCE,['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,ENDPOINT_RULE,AUTHORITY_RULE,EVIDENCE_RULE),['genus-differentia']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(PROJECTION_RULE,['operational']),'/voices/scientific_formal/testable_conditions/0':(ENDPOINT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(AUTHORITY_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(EVIDENCE_RULE,['operational'])}
 for prefix in ['/boundaries/','/voices/scientific_formal/boundary_conditions/']:
  chosen[prefix+'0']=(both(ROOT_RULE,BOUNDARIES),['axiomatic-implicit']);chosen[prefix+'1']=(both(AUTHORITY_RULE,PROJECTION_RULE),['operational']);chosen[prefix+'2']=(SUCCESSION_RULE,['operational'])
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred'
  rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context)
 snap=snapshot();r.verify(snap,ROOT);source=context['source_selection']
 assert source['definition_id']=='cal.definition.capability-realization-binding' and source['sha256']=='8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd'
 doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={
 'encoded':'Necessary version-exact lifecycle-bearing association,member cardinality,single canonical authority,evidence roles,optional read-only digest-bound projection and change-triggered succession declarations;actual outcomes remain independent.',
 'explanatory':'Notation,intuition andexamples explain the source without creating authority effects oractual realization.',
 'deferred':'The authority-scope mapping andcandidate no-effect ceiling remain explicit source obligations,checked independently where possible.'}
 for row in selected_clauses(doc):
  cid='CRB-'+str(len(clauses)+1).zfill(3);disp=row['disposition']
  clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]})
  links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']]
 primary=next(x['clause_id'] for x in clauses if x['source_selector']=='/voices/scientific_formal/normative_statement')
 req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent endpoint cardinality,evidence roles,optional projections,changed versus aliased member sets,succession and noninferential outcome examples.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity andowner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CapabilityRealizationBinding-exact-association-projection-succession-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'CRB-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with capability,implementation,canonical-relation,projection,lifecycle,evidence andsuccession owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no whole prior theory oraccepted common carrier map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'exact-association-endpoints-authority-projection-and-successor','scenario':'Six Binding revisions include single and multiple Implementation endpoints,shared evidence contents under distinct purposes,optional read-only digest-bound projections,Capability/member/posture changes and an aliased unchanged member set.','expected_interpretation':'Necessary association and succession declarations hold without actual adoption,deployment,conformance,operation,value or authority inferred.','rationale':'Preserve positive cardinality,canonical authority,optional projection and nonvacuous change witnesses.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'changed-implementation-set-with-inplace-successor','scenario':'A selected change nominates an altered Implementation member set but names the original Binding revision as its successor.','expected_interpretation':'The necessary distinct-successor and intended-state guard fails.','rationale':'Desired-state fields are independent of the successor reference,preventing a vacuous in-place-change test.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  sel=clause['source_selector'];targets=['Binding-not-ActualSourceFidelity','Binding-not-ActualAuthorityEffect']
  if sel in ['/voices/scientific_formal/normative_statement','/scope/applicability']:
   targets += ['Binding-not-ActualAdoption','Binding-not-ActualDeployment','Binding-not-ActualConformance','Binding-not-ActualSuccessfulOperation','Binding-not-ActualProductValue','Binding-not-ActualEndpointResolution','Binding-not-ActualCanonicality']
  if sel=='/voices/scientific_formal/formal_expression':targets+=['Binding-not-ActualGovernance','Binding-not-ActualBoundedness']
  if sel.endswith('/1') and ('boundary' in sel or sel.startswith('/boundaries/') or sel.startswith('/scope/exclusions/')):targets+=['Projection-not-ActualAuthenticity','Projection-not-ActualDigestCorrectness','Projection-not-ActualReadOnlyEnforcement']
  if sel.endswith('/2') and ('boundary' in sel or sel.startswith('/boundaries/')):targets+=['Change-not-ActualSuccessorCreation','Change-not-ActualHistoryAuthenticity']
  if sel=='/voices/scientific_formal/testable_conditions/0':targets+=['Binding-not-ActualEndpointResolution']
  if sel=='/voices/scientific_formal/testable_conditions/1':targets+=['Binding-not-ActualCanonicality']
  if sel=='/voices/scientific_formal/testable_conditions/2':targets+=['Binding-not-ActualAdoption','Binding-not-ActualConformance','Binding-not-ActualDeployment','Binding-not-ActualProductValue','Binding-not-ActualEvidenceAuthenticity']
  if sel=='/scope/exclusions/2':targets+=['Binding-not-ActualAdmission','Binding-not-ActualRuntimeActivation','Binding-not-ActualPublication']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in ids,target
   obligations.append({'source':source,'selector':sel,'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False,'implementation_member_change_is_extensional':True,'evidence_roles_share_common_collection_carrier':True,'projection_optional':True,'successor_distinct_only_when_required_change':True,'actual_digest_authenticity_proved':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary association/endpoints/canonical-authority/evidence/projection/succession declarations only;actual adoption,deployment,conformance,operation,value,authority,fidelity andwhole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context)
 print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()

