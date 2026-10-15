"""Prepared Implementation source-qualified technical realization, scope, version use and noninference guards."""
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


SCOPE='scope:candidate:Implementation-technical-realization-nominations-version-use-scope-noninference-v1'
SORTS=['ImplementationReference','IdentityReference','RevisionReference','OwnerReference','LifecycleReference','SourceBindingReference','PostureReference','InterfaceCollectionReference','InterfaceReference','EvidenceCollectionReference','EvidenceReference','ScopeReference','UseReference','DefinitionVersionReference','Token']
CONSTANTS={'EMPTY':'Token','SELECTED_DEFINITION':'DefinitionVersionReference'}
FIELDS={'implementationIdentity':'IdentityReference','implementationVersion':'RevisionReference','implementationOwner':'OwnerReference','implementationLifecycle':'LifecycleReference','implementationSourceBinding':'SourceBindingReference','implementationBuildOrDeploymentPosture':'PostureReference','implementationInterfaces':'InterfaceCollectionReference','implementationEvidence':'EvidenceCollectionReference','implementationScope':'ScopeReference'}
USE_FIELDS={'useImplementation':'ImplementationReference','useDefinitionVersion':'DefinitionVersionReference','useScope':'ScopeReference'}
GROUPS=[(FIELDS,'ImplementationReference'),(USE_FIELDS,'UseReference')]
FUNCTIONS={name:([carrier],sort) for fields,carrier in GROUPS for name,sort in fields.items()}
HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'}
FUNCTIONS.update({name:([sort],'Token') for sort,name in HANDLES.items()})
EXCLUDED=['ImplementationIs'+name+'Declared' for name in ['Product','ProductCapability','Agent','Model','Tool','RuntimeInstance','ConformanceProof','ValueProof']]
INFERRED=['Admission','Authority','Success','IdentityEquivalence','ExternalEffect']
FACETS=['Identity','Lifecycle','Evidence','Authority','RelationEffects']
CONTRACTS=['CarrierShape','RelationAvailability','RuntimeBehavior','AuthorityEffect']
ACTUAL=['IdentityFidelity','VersionResolution','OwnerQualification','OwnerAuthorization','LifecycleOperation','SourceBindingAuthenticity','BuildCorrectness','DeploymentSuccess','InterfaceResolution','InterfaceOperation','EvidenceAuthenticity','EvidenceAdequacy','ScopeResolution','ScopeCompliance','Governance','TechnicalRealization','Conformance','ProductValue','RuntimeInstantiation','AuthorityEffect','ArtifactTypeAdmission','InstanceAdmission','RelationAdmission','PolicyDecisionAdmission','RuntimeActivation','Publication','Release','IdentityEquivalence','ExternalEffect','SourceFidelity','WholeProof']
USE_ACTUAL=['DefinitionResolution','SuccessorAdmissionAuthenticity','ScopeCompliance','ApplicabilityCompliance','ExclusionCompliance','AuthorityEffect','ClaimSupport','SourceFidelity','WholeProof']
SIGNATURE={name:['ImplementationReference'] for name in ['ImplementationApplicable','ImplementationInScopeDeclared','ImplementationTechnicalRealizationDeclared','ImplementationStableIdentityDeclared','ImplementationBoundedScopeDeclared','ImplementationGovernedIdentityDeclared','ImplementationGovernedRecordDeclared',*EXCLUDED,*['Implementation'+name+'SeparatelyGovernedDeclared' for name in FACETS],*['Implementation'+name+'NeedsSeparateContractDeclared' for name in CONTRACTS],*['ImplementationTermInfers'+name+'Declared' for name in INFERRED],*['ImplementationActual'+name for name in ACTUAL]]}
SIGNATURE.update({name:['UseReference'] for name in ['UseApplicable','UseInScopeDeclared','UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared',*['UseTermInfers'+name+'Declared' for name in INFERRED],*['UseActual'+name for name in USE_ACTUAL]]})
SIGNATURE.update(PostureBuildDeclared=['PostureReference'],PostureDeploymentDeclared=['PostureReference'],DefinitionVersionAdmissionDeclared=['DefinitionVersionReference'])
for sort in SORTS:
 if sort!='Token':SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({name+'BindingDeclared':[carrier,sort] for name,sort in fields.items()})
SIGNATURE.update(InterfaceCollectionContainsDeclared=['InterfaceCollectionReference','InterfaceReference'],EvidenceCollectionContainsDeclared=['EvidenceCollectionReference','EvidenceReference'],ImplementationInterfaceLinkDeclared=['ImplementationReference','InterfaceReference'],ImplementationEvidenceLinkDeclared=['ImplementationReference','EvidenceReference'],DefinitionVersionAdmittedSuccessorDeclared=['DefinitionVersionReference','DefinitionVersionReference'],UseScopeWithinImplementationDeclared=['ScopeReference','ScopeReference'])
MAP={'ImplementationReference':'ImplementationApplicable','UseReference':'UseApplicable'}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(name,value)),allof([(sort,'target')],iff(pred(name+'BindingDeclared',value,'target'),eq(var('target'),fn(name,value))))) for name,sort in fields.items()])
def selected(sort,name,body):return allof([(sort,name)],implies(pred(member(sort),name),body))
X=var('x');U=var('u');APP=pred('ImplementationApplicable',X);USE=pred('UseApplicable',U)
ROOT_RULE=both(allof([('ImplementationReference','x')],iff(APP,pred('ImplementationInScopeDeclared',X))),selected('ImplementationReference','x',both(guard('ImplementationReference',X),exact(FIELDS,X),pred('ImplementationTechnicalRealizationDeclared',X),pred('ImplementationStableIdentityDeclared',X),pred('ImplementationBoundedScopeDeclared',X),either(pred('ImplementationGovernedIdentityDeclared',X),pred('ImplementationGovernedRecordDeclared',X)))))
POSTURE_RULE=selected('ImplementationReference','x',either(pred('PostureBuildDeclared',fn('implementationBuildOrDeploymentPosture',X)),pred('PostureDeploymentDeclared',fn('implementationBuildOrDeploymentPosture',X))))
COLLECTION_RULE=selected('ImplementationReference','x',both(*[allof([(sort,'item')],both(iff(pred('Implementation'+kind+'LinkDeclared',X,'item'),pred(kind+'CollectionContainsDeclared',fn('implementation'+field,X),'item')),implies(pred('Implementation'+kind+'LinkDeclared',X,'item'),guard(sort,var('item'))))) for kind,field,sort in [('Interface','Interfaces','InterfaceReference'),('Evidence','Evidence','EvidenceReference')]]))
FACET_RULE=selected('ImplementationReference','x',both(*[pred('Implementation'+name+'SeparatelyGovernedDeclared',X) for name in FACETS]))
BOUNDARIES=selected('ImplementationReference','x',both(*[neg(pred(name,X)) for name in EXCLUDED]))
CONTRACT_RULE=selected('ImplementationReference','x',both(*[pred('Implementation'+name+'NeedsSeparateContractDeclared',X) for name in CONTRACTS]))
ROOT_NONINFERENCE=selected('ImplementationReference','x',both(*[neg(pred('ImplementationTermInfers'+name+'Declared',X)) for name in INFERRED]))
USE_NONINFERENCE=selected('UseReference','u',both(*[neg(pred('UseTermInfers'+name+'Declared',U)) for name in INFERRED]))
VERSION_ALLOWED=either(eq(fn('useDefinitionVersion',U),const('SELECTED_DEFINITION')),both(pred('DefinitionVersionAdmittedSuccessorDeclared',const('SELECTED_DEFINITION'),fn('useDefinitionVersion',U)),pred('DefinitionVersionAdmissionDeclared',fn('useDefinitionVersion',U))))
USE_SCOPE=selected('UseReference','u',both(pred('UseWithinApplicabilityDeclared',U),pred('UseRespectsExclusionsDeclared',U),pred('UseScopeWithinImplementationDeclared',fn('useScope',U),fn('implementationScope',fn('useImplementation',U)))))
USE_RULE=both(guard('DefinitionVersionReference',const('SELECTED_DEFINITION')),pred('DefinitionVersionAdmissionDeclared',const('SELECTED_DEFINITION')),allof([('UseReference','u')],iff(USE,pred('UseInScopeDeclared',U))),selected('UseReference','u',both(guard('UseReference',U),exact(USE_FIELDS,U),VERSION_ALLOWED)),USE_SCOPE)
THEORY={'governed-technical-realization-coordinates':ROOT_RULE,'build-or-deployment-posture-inclusive':POSTURE_RULE,'interface-and-evidence-nominations':COLLECTION_RULE,'separately-governed-five-facets':FACET_RULE,'role-and-proof-boundaries':BOUNDARIES,'separate-contract-requirements':CONTRACT_RULE,'exact-Definition-or-admitted-successor-use':USE_RULE,'term-alone-does-not-infer-effects':both(ROOT_NONINFERENCE,USE_NONINFERENCE)}
LOSSES=[
'C65 positively admits the exact Definition; the immutable candidate body and its embedded candidate-unadmitted review posture are separate and do not accept this translation.',
'The integrated-model review whole-file bytes are preserved as context only; its selected-capability narrative does not create a mandatory Capability endpoint in the Definition.',
'Proposed sorts and nine realization coordinates preserve source distinctions without creating canonical Definitions or accepted denotations.',
'Governed identity or record is inclusive; selected realizations still nominate stable identity, version and bounded scope.',
'Stable identity and record version are separate coordinates; no unique successor, global version order, immutable-build rule or universal identity-injectivity theorem is introduced.',
'Owner, lifecycle and source-binding nominations do not establish authentic principal binding, effective lifecycle or source provenance.',
'Build or deployment posture is inclusive; both may be declared and neither declaration proves a correct build or successful deployment.',
'Interface and evidence membership relations are explicit proposed nominations. No unsupported minimum membership or adequacy requirement is inferred from nonempty collection handles.',
'Evidence may be shared across realizations and versions; evidence binding does not supply conformance proof, successful execution or Product value.',
'Identity, lifecycle, evidence, authority and relation effects retain separately governed declarations; actual governance remains an independent target.',
'Separate admitted-contract requirements are necessary declarations, not admissions of a carrier, relation, runtime or authority grant.',
'Implementation stays distinct from Product, Product Capability, Agent, model, Tool, runtime instance and proof of conformance or value; nominal sorted separation requires accepted maps.',
'Exact Definition-use selection is version-qualified; an opaque reference does not prove actual resolution or applicability.',
'Admitted-successor use requires separate successor and admission declarations. Hypothetical finite branch controls nominate no real successor Definition, decision or canonical admission.',
'Use scope may be narrower than the realization scope through an explicit containment declaration; no global scope algebra or equal-scope requirement is invented.',
'No term-alone inference of admission, authority, success, identity equivalence or external effect is allowed; independently justified actual effects remain possible.',
'Technical realization, build, deployment, interface operation, evidence adequacy, conformance, value and permission require their own evidence and accepted meanings.',
'The Rust and 2.1 example is explanatory; it does not restrict all Implementations to Rust, mandate a build, or prove admitted deployment.',
'No whole prior Product, Capability, Tool, Agent, Source, Evidence, scope, lifecycle or authority theory is imported into this primary candidate.',
'Coverage populations and supplied countermodels establish their reported finite calculations, not actual enumeration, source fidelity, shared consistency or whole proof.',
'Original T/O/E/R/J artifacts, owner and consumer maps, cycle classification and final complete episode review remain required after this stage.'
]
def declarations():return [{'kind':'sort','symbol_id':name,'scope':SCOPE,'domain_policy':'nonempty'} for name in SORTS]+[{'kind':'constant','symbol_id':name,'scope':SCOPE,'result_sort':sort} for name,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':name,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for name,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':name,'scope':SCOPE,'argument_sorts':args} for name,args in SIGNATURE.items()]
def required_populations():
 def xw(body):return exists([('ImplementationReference','x')],both(APP,body))
 def uw(body):return exists([('UseReference','u')],both(USE,body))
 gi,gr=pred('ImplementationGovernedIdentityDeclared',X),pred('ImplementationGovernedRecordDeclared',X);posture=fn('implementationBuildOrDeploymentPosture',X);build,deploy=pred('PostureBuildDeclared',posture),pred('PostureDeploymentDeclared',posture)
 rows={'Implementation':('ImplementationReference',xw(APP)),'OutsideImplementation':('ImplementationReference',exists([('ImplementationReference','x')],neg(APP))),'GovernedIdentityOnly':('ImplementationReference',xw(both(gi,neg(gr)))),'GovernedRecordOnly':('ImplementationReference',xw(both(gr,neg(gi)))),'BothGovernedIdentityAndRecord':('ImplementationReference',xw(both(gi,gr))),'BuildPostureOnly':('PostureReference',xw(both(build,neg(deploy)))),'DeploymentPostureOnly':('PostureReference',xw(both(deploy,neg(build)))),'BothPostures':('PostureReference',xw(both(build,deploy))),'EmptyInterfaceNominations':('InterfaceCollectionReference',xw(neg(exists([('InterfaceReference','item')],pred('ImplementationInterfaceLinkDeclared',X,'item'))))),'MultipleInterfaceNominations':('InterfaceReference',xw(exists([('InterfaceReference','item'),('InterfaceReference','other')],both(pred('ImplementationInterfaceLinkDeclared',X,'item'),pred('ImplementationInterfaceLinkDeclared',X,'other'),neg(eq(var('item'),var('other'))))))),'EmptyEvidenceNominations':('EvidenceCollectionReference',xw(neg(exists([('EvidenceReference','item')],pred('ImplementationEvidenceLinkDeclared',X,'item'))))),'SharedEvidence':('EvidenceReference',exists([('ImplementationReference','x'),('ImplementationReference','other'),('EvidenceReference','item')],both(APP,pred('ImplementationApplicable','other'),neg(eq(X,var('other'))),pred('ImplementationEvidenceLinkDeclared',X,'item'),pred('ImplementationEvidenceLinkDeclared','other','item')))),'DistinctVersionsSameIdentity':('RevisionReference',exists([('ImplementationReference','x'),('ImplementationReference','other')],both(APP,pred('ImplementationApplicable','other'),neg(eq(X,var('other'))),eq(fn('implementationIdentity',X),fn('implementationIdentity','other')),neg(eq(fn('implementationVersion',X),fn('implementationVersion','other')))))),'WithoutActualOutcomes':('ImplementationReference',xw(both(*[neg(pred('ImplementationActual'+name,X)) for name in ACTUAL]))),'IndependentAuthority':('ImplementationReference',xw(pred('ImplementationActualAuthorityEffect',X))),'Use':('UseReference',uw(USE)),'OutsideUse':('UseReference',exists([('UseReference','u')],neg(USE))),'ExactSourceUse':('DefinitionVersionReference',uw(eq(fn('useDefinitionVersion',U),const('SELECTED_DEFINITION')))),'NarrowerScopeNomination':('ScopeReference',uw(both(pred('UseScopeWithinImplementationDeclared',fn('useScope',U),fn('implementationScope',fn('useImplementation',U))),neg(eq(fn('useScope',U),fn('implementationScope',fn('useImplementation',U))))))),'UseWithoutActualOutcomes':('UseReference',uw(both(*[neg(pred('UseActual'+name,U)) for name in USE_ACTUAL]))),'IndependentUseAuthority':('UseReference',uw(pred('UseActualAuthorityEffect',U)))}
 return rows
def query_specs():
 rows=[]
 for prefix,sort,name,app,outcomes in [('Implementation','ImplementationReference','x',APP,ACTUAL),('Use','UseReference','u',USE,USE_ACTUAL)]:
  for outcome in outcomes:rows.append({'query_id':prefix+'-not-Actual'+outcome,'target':allof([(sort,name)],implies(app,pred(prefix+'Actual'+outcome,name))),'witness_condition':exists([(sort,name)],both(app,neg(pred(prefix+'Actual'+outcome,name)))),'selected_in_T':False,'source_condition':'selected-'+prefix.lower(),'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(ROOT_RULE,POSTURE_RULE,COLLECTION_RULE,BOUNDARIES),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,ROOT_NONINFERENCE),['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,POSTURE_RULE,COLLECTION_RULE),['genus-differentia']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(ROOT_NONINFERENCE,['operational']),'/voices/scientific_formal/boundary_conditions/0':(both(ROOT_RULE,POSTURE_RULE,COLLECTION_RULE),['operational']),'/voices/scientific_formal/boundary_conditions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/2':(FACET_RULE,['operational']),'/voices/scientific_formal/testable_conditions/0':(USE_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(both(ROOT_RULE,USE_SCOPE),['operational']),'/voices/scientific_formal/testable_conditions/2':(both(ROOT_NONINFERENCE,USE_NONINFERENCE),['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(CONTRACT_RULE,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  selector=unit['selector'];formula,forms=chosen.get(selector,(None,['unresolved']));disposition='encoded' if formula is not None else 'explanatory' if selector.startswith('/voices/') and any(name in selector for name in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':selector,'start_character':0,'excerpt':texts[selector],'formula':formula,'forms':forms,'disposition':disposition,'unit_id':unit['unit_id']})
 return rows

def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection']
 assert source['definition_id']=='cal.definition.implementation' and source['sha256']=='c25fcb2b31e8fee007261a645627fe8aae61d5778a51781a35cc549dc7aa79c1'
 doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary technical realization, nominated coordinates, inclusive posture, explicit member links, separated governance, exact scoped uses and noninference declarations; actual outcomes remain independent.','explanatory':'Notation, intuition and examples explain the source without becoming authority or requiring Rust, deployment or Capability bindings.','deferred':'Authority scope and candidate no-effect ceiling remain explicit source obligations.'}
 for row in selected_clauses(doc):
  cid='IMPL-'+str(len(clauses)+1).zfill(3);disposition=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disposition,'forms':row['forms'],'roles':['definition'] if disposition=='encoded' else ['explanation-example'] if disposition=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disposition]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,name) for name in context['direct_dependency_names']];primary=next(row['clause_id'] for row in clauses if row['source_selector']=='/voices/scientific_formal/normative_statement');req=required_populations()
 populations=[{'population_id':'POP-REQ-'+name,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':formula,'scope':SCOPE,'rationale':'Independent governed-mode, inclusive posture, member cardinality, shared evidence, version, use, scope and noninferential outcome witnesses.','review_ref':None} for name,(carrier,formula) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+name,'carrier':args[0],'predicate_ref':name if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual populations and accepted owner or consumer denotations remain unresolved.','review_ref':None} for name,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:Implementation-technical-nominations-scoped-version-use-noninference-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'IMPL-FINDING-'+str(i+1).zfill(3),'description':loss,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with technical-realization, identity, source, lifecycle, owner, interface, evidence, build, deployment and authority owners'} for i,loss in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency; no accepted common carrier or whole prior theory imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'governed-technical-realization-and-scoped-use','scenario':'Four selected realization references cover governed identity or record, build or deployment posture, empty and multiple interface nominations, shared evidence and independently possible authority. Three selected uses nominate the exact current Definition and equal or narrower scopes.','expected_interpretation':'Necessary declarations hold without actual technical operation, build, deployment, conformance, value, admission or source fidelity inferred.','rationale':'Nonvacuous coverage separates realization, use and actual outcomes.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'unknown-version-use-without-admitted-successor','scenario':'A selected use nominates another hypothetical Definition version without a declared admitted-successor relationship.','expected_interpretation':'The exact-version or admitted-successor guard fails.','rationale':'A well-formed version handle alone is insufficient.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[row['version_ref'] for row in deps],required_conflicts=[row['finding_id'] for row in findings]);assert account['character_accounting_complete']
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(name,value)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  selector=clause['source_selector'];targets=['Implementation-not-ActualSourceFidelity','Implementation-not-ActualWholeProof']
  if selector in ['/voices/scientific_formal/normative_statement','/scope/applicability','/voices/scientific_formal/boundary_conditions/0']:
   targets+=['Implementation-not-ActualTechnicalRealization','Implementation-not-ActualOwnerQualification','Implementation-not-ActualSourceBindingAuthenticity','Implementation-not-ActualBuildCorrectness','Implementation-not-ActualDeploymentSuccess','Implementation-not-ActualInterfaceOperation','Implementation-not-ActualEvidenceAdequacy']
  if selector=='/voices/scientific_formal/formal_expression':targets+=['Implementation-not-ActualGovernance','Implementation-not-ActualScopeCompliance','Implementation-not-ActualAuthorityEffect']
  if selector.startswith('/boundaries/') or selector.startswith('/scope/exclusions/') or '/boundary_conditions/' in selector:targets+=['Implementation-not-ActualAuthorityEffect','Implementation-not-ActualConformance','Implementation-not-ActualProductValue','Implementation-not-ActualRuntimeInstantiation']
  if selector.endswith('/boundary_conditions/2'):targets+=['Implementation-not-ActualLifecycleOperation','Implementation-not-ActualEvidenceAuthenticity']
  if selector.endswith('/testable_conditions/0'):targets+=['Use-not-ActualDefinitionResolution','Use-not-ActualSuccessorAdmissionAuthenticity']
  if selector.endswith('/testable_conditions/1'):targets+=['Use-not-ActualScopeCompliance','Use-not-ActualApplicabilityCompliance','Use-not-ActualExclusionCompliance']
  if selector.endswith('/testable_conditions/2'):targets+=['Implementation-not-ActualArtifactTypeAdmission','Implementation-not-ActualInstanceAdmission','Implementation-not-ActualIdentityEquivalence','Implementation-not-ActualExternalEffect','Use-not-ActualAuthorityEffect']
  if selector=='/claim_ceiling':targets+=['Implementation-not-ActualArtifactTypeAdmission','Implementation-not-ActualInstanceAdmission','Implementation-not-ActualRelationAdmission','Implementation-not-ActualPolicyDecisionAdmission','Implementation-not-ActualRuntimeActivation','Implementation-not-ActualPublication','Implementation-not-ActualRelease','Implementation-not-ActualExternalEffect']
  link=next(row for row in links if row['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in {row['query_id'] for row in queries};obligations.append({'source':source,'selector':selector,'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{name+'_clauses':sum(row['disposition']==name for row in clauses) for name in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(row['formal_statement'],sort_keys=True) for row in clauses if row['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False,'governed_identity_or_record_inclusive':True,'build_or_deployment_posture_inclusive':True,'empty_member_nominations_allowed':True,'shared_evidence_allowed':True,'narrower_use_scope_allowed':True,'hypothetical_successor_is_actual_admission':False,'mandatory_capability_endpoint_added':False,'successor_or_global_version_policy_added':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':row['path'],'sha256':row['sha256']} for row in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'embedded_review_context':context['embedded_review_source'],'source_fidelity':'pending','claim_ceiling':'Necessary technical-realization, nomination, separated governance and scoped Definition-use guards only; actual outcomes, admitted successor resolution, accepted denotations, fidelity and whole proof remain pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
