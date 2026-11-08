"""Exact Identity Lineage tuple,rename/successor and subject-kind contract declarations."""
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
SCOPE='scope:candidate:identity-lineage-exact-epochs-rename-successor-kind-contract-v1'
SORTS=['LineageReference','LineageIdReference','KindDefinitionReference','EpochReference','IdentityReference','NameReference','LineageKindReference','DecisionReference','OwnerReference','EvidenceReference','NonEffectsReference','ContractReference','ScopeReference','Token']
CONSTANTS={'EMPTY':'Token'}
LINEAGE_FIELDS={'lineageIdentifier':'LineageIdReference','lineageSubjectKind':'KindDefinitionReference','lineagePredecessor':'EpochReference','lineageSuccessor':'EpochReference','lineageKind':'LineageKindReference','lineageOwnerDecision':'DecisionReference','lineageEvidence':'EvidenceReference','lineageNonEffects':'NonEffectsReference','lineageContract':'ContractReference'}
EPOCH_FIELDS={'epochIdentity':'IdentityReference','epochName':'NameReference','epochSubjectKind':'KindDefinitionReference'}
DECISION_FIELDS={'decisionOwner':'OwnerReference'}
CONTRACT_FIELDS={'contractSubjectKind':'KindDefinitionReference','contractScope':'ScopeReference'}
GROUPS=[(LINEAGE_FIELDS,'LineageReference'),(EPOCH_FIELDS,'EpochReference'),(DECISION_FIELDS,'DecisionReference'),(CONTRACT_FIELDS,'ContractReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
EXCLUDED=['LineageIsGenericAliasListDeclared','LineageInfersIdentityFromAliasDeclared','LineageInfersIdentityFromSimilarNamesDeclared','LineageInfersIdentityFromPathsDeclared','LineageInfersIdentityFromSharedOwnerDeclared','LineageInfersIdentityFromSimilarContentDeclared','LineageInfersIdentityFromHistoryDeclared','ContextContractUsedForProductByAnalogyDeclared','LineageGrantsAdmissionDeclared','LineageTransfersAuthorityDeclared','LineageDeletesSubjectDeclared','LineageAutomaticallySupersedesSubjectDeclared','ParentMeaningGrantsAuthorityDeclared','DefinitionAdmissionAcceptsTranslationDeclared','EndpointReferencesAuthenticateContinuityDeclared','OwnerDecisionReferenceGrantsAuthorityDeclared','EvidenceReferenceProvesContinuityDeclared','ContractReferenceProvesAdmissionDeclared','LineageDefinitionCreatesCarrierDeclared','LineageDefinitionCreatesInstanceDeclared','RuntimeEffectGrantedDeclared','PublicationEffectGrantedDeclared','ReleaseEffectGrantedDeclared','DeploymentEffectGrantedDeclared','ExternalEffectGrantedDeclared']
RENAME_EXCLUDED=['RenameCreatesNewProductDeclared','RenameCreatesNewProjectDeclared','RenameCreatesNewMethodDeclared','RenameCreatesNewGoalDeclared','RenameCreatesNewContextDeclared']
ACTUAL=['Continuity','ImmutableStorage','SubjectKindFidelity','LineageKindFidelity','PredecessorResolution','SuccessorResolution','IdentityFidelity','NameFidelity','SameIdentityContinuity','Rename','SuccessorIdentity','OwnerDecisionAuthenticity','OwnerAuthorization','EvidenceAdequacy','NonEffectsPreservation','SubjectKindScope','GeneralizedContractAdmission','GeneralizedContractApplicability','ContractAuthenticity','NoNewProduct','NoNewProject','NoNewMethod','NoNewGoal','NoNewContext','NoAdmission','NoAuthorityTransfer','NoDeletion','NoAutomaticSupersession','SourceFidelity','ConsumerAlignment','SharedConsistency','Proof','Authority','ExternalEffect']
SIGNATURE={n:['LineageReference'] for n in ['LineageApplicable','LineageInScopeDeclared','LineageGovernedDeclared','LineageTypedDeclared','LineageImmutableDeclared','LineageEvidenceBackedDeclared','LineageContinuityRecordDeclared','LineageExactEndpointsResolvedDeclared','LineageSameIdentityRenameDeclared','LineageSuccessorIdentityDeclared','LineageOtherKindDeclared','LineageGeneralizedContractSelectedDeclared',*EXCLUDED,*RENAME_EXCLUDED,*['LineageActual'+n for n in ACTUAL]]}
for sort in SORTS:
 if sort not in ['LineageReference','Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'DecisionRecordedDeclared':['DecisionReference'],'ContractRecordedDeclared':['ContractReference'],'ContractContextSpecificDeclared':['ContractReference'],'ContractGeneralizedDeclared':['ContractReference'],'ContractAdmissionRecordedDeclared':['ContractReference'],'KindContextDeclared':['KindDefinitionReference'],'KindProductDeclared':['KindDefinitionReference'],'KindSameIdentityRenameDeclared':['LineageKindReference'],'KindSuccessorIdentityDeclared':['LineageKindReference'],'KindOtherDeclared':['LineageKindReference'],'ContractCoversSubjectKindDeclared':['ContractReference','KindDefinitionReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
L=var('l');APP=pred('LineageApplicable',L)
def lf(n):return fn(n,L)
KIND=lf('lineageSubjectKind');PRE=lf('lineagePredecessor');POST=lf('lineageSuccessor');LINEAGE_KIND=lf('lineageKind');DECISION=lf('lineageOwnerDecision');CONTRACT=lf('lineageContract');RENAME_APP=pred('LineageSameIdentityRenameDeclared',L);SUCCESSOR_APP=pred('LineageSuccessorIdentityDeclared',L);OTHER_APP=pred('LineageOtherKindDeclared',L);GENERAL_APP=pred('LineageGeneralizedContractSelectedDeclared',L)
def guard(sort,value):return both(pred('LineageApplicable',value) if sort=='LineageReference' else pred(sort+'Declared',value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'value')],iff(pred(n+'BindingDeclared',value,'value'),eq(var('value'),fn(n,value))))) for n,sort in fields.items()])
def selected(z):return allof([('LineageReference','l')],implies(APP,z))
ELIGIBILITY=allof([('LineageReference','l')],iff(APP,pred('LineageInScopeDeclared',L)))
GENUS=selected(both(guard('LineageReference',L),exact(LINEAGE_FIELDS,L),*[pred(n,L) for n in ['LineageGovernedDeclared','LineageTypedDeclared','LineageImmutableDeclared','LineageEvidenceBackedDeclared','LineageContinuityRecordDeclared']],exact(EPOCH_FIELDS,PRE),exact(EPOCH_FIELDS,POST),exact(DECISION_FIELDS,DECISION),pred('DecisionRecordedDeclared',DECISION),exact(CONTRACT_FIELDS,CONTRACT),pred('ContractRecordedDeclared',CONTRACT)))
KIND_RULE=selected(both(iff(RENAME_APP,pred('KindSameIdentityRenameDeclared',LINEAGE_KIND)),iff(SUCCESSOR_APP,pred('KindSuccessorIdentityDeclared',LINEAGE_KIND)),iff(OTHER_APP,pred('KindOtherDeclared',LINEAGE_KIND)),either(RENAME_APP,SUCCESSOR_APP,OTHER_APP),neg(both(RENAME_APP,SUCCESSOR_APP)),neg(both(RENAME_APP,OTHER_APP)),neg(both(SUCCESSOR_APP,OTHER_APP))))
ENDPOINTS=selected(pred('LineageExactEndpointsResolvedDeclared',L))
CONTRACT_RULE=selected(both(iff(GENERAL_APP,pred('ContractGeneralizedDeclared',CONTRACT)),implies(neg(GENERAL_APP),both(eq(fn('contractSubjectKind',CONTRACT),KIND),eq(fn('epochSubjectKind',PRE),KIND),eq(fn('epochSubjectKind',POST),KIND),implies(pred('ContractContextSpecificDeclared',CONTRACT),both(pred('KindContextDeclared',KIND),neg(pred('KindProductDeclared',KIND)))))),implies(GENERAL_APP,both(pred('ContractAdmissionRecordedDeclared',CONTRACT),*[pred('ContractCoversSubjectKindDeclared',CONTRACT,z) for z in [KIND,fn('epochSubjectKind',PRE),fn('epochSubjectKind',POST)]]))))
RENAME=selected(implies(RENAME_APP,both(eq(fn('epochIdentity',PRE),fn('epochIdentity',POST)),neg(eq(fn('epochName',PRE),fn('epochName',POST))),*[neg(pred(n,L)) for n in RENAME_EXCLUDED])))
SUCCESSOR=selected(implies(SUCCESSOR_APP,neg(eq(fn('epochIdentity',PRE),fn('epochIdentity',POST)))))
BOUNDARIES=selected(both(*[neg(pred(n,L)) for n in EXCLUDED]))
THEORY={'eligibility':ELIGIBILITY,'genus':GENUS,'lineage-kind':KIND_RULE,'endpoints':ENDPOINTS,'contract':CONTRACT_RULE,'rename':RENAME,'successor':SUCCESSOR,'boundaries':BOUNDARIES}
LOSSES=[
 'Exact current C29 Definition admission does not instantiate continuity,admit carriers/endpoints or accept this formal translation.',
 'Immutable typed evidence-backed continuity genus is represented by necessary declarations,not real storage,identity truth or unbounded retention.',
 'Lineage,identifier,kind Definition,epoch,identity,name,kind,Decision,owner,evidence,non-effects,contract and scope are proposed qualified sorts.',
 'The eight formal tuple coordinates are preserved;an extra contract nomination is a proposed explicit subject-kind/generalization map.',
 'One predecessor/successor tuple per record does not impose global uniqueness,complete alias coverage or a universal identity registry.',
 'Exact endpoint resolution is a necessary declaration;actual lookup,authentic identity and current epoch fidelity remain independent.',
 'Subject-kind and lineage-kind references are distinct;kind classifiers are proposed denotations requiring exact owner correspondence.',
 'Rename/successor/other are mutually exclusive candidate categories;other remains open to declared source-specific lineage kinds.',
 'Rename requires equal declared endpoint identity and unequal declared name,without universally denying independently supported identity for similar objects.',
 'Successor uses distinct declared identity coordinates as a proposed distinction;the abbreviated formal expression explicitly states rename only.',
 'Other lineage kinds receive no invented rename or successor identity/name constraint;their accepted semantics remain unresolved.',
 'No universal unequal endpoint references are imposed for rename;identity/name selector coherence determines whether such a nomination can satisfy T.',
 'Subject-kind-specific contract nominates the same kind as both endpoints;actual kind and contract applicability remain independent.',
 'Context-specific contract requires Context kind and excludes Product in the nongeneralized branch;no analogy supplies cross-kind scope.',
 'An explicitly generalized contract has recorded admission and coverage declarations for bound/predecessor/successor kinds;actual admission and coverage need independent evidence.',
 'Generalization does not authenticate its owner,transfer endpoint authority or imply all other subject kinds are covered.',
 'Owner Decision and recorded owner are nominated without requiring globally one subject per Decision or authenticating authority from labels.',
 'One EvidenceReference is a proposed aggregate evidence nomination,not cardinality one for actual evidence_refs or sufficient supporting evidence.',
 'NonEffectsReference preserves declared non-effects without proving actual absence of admission,transfer,deletion or supersession.',
 'Exact local Definition_v1/Product_v1/chain0001 source bytes and symbolic C29 chain0002 consumer remain separate from later carrier/instance overlays.',
 'Examples,Craft rename and Context evolution remain explanatory;no actual Product continuity or owner decision is executed.',
 'Finite T/I witnesses and complete character accounting do not accept source fidelity,shared meanings,whole translation or whole-definition proof.'
]
def required_populations():
 def withl(z):return exists([('LineageReference','l')],both(APP,z))
 return {'SelectedLineage':('LineageReference',withl(APP)),'OutsideLineage':('LineageReference',exists([('LineageReference','l')],neg(APP))),'LineageWithoutActualOutcomes':('LineageReference',withl(both(*[neg(pred('LineageActual'+n,L)) for n in ACTUAL]))),'IndependentAuthority':('LineageReference',withl(pred('LineageActualAuthority',L))),'SameIdentityRename':('LineageReference',withl(RENAME_APP)),'SuccessorIdentity':('LineageReference',withl(SUCCESSOR_APP)),'OtherLineageKind':('LineageReference',withl(OTHER_APP)),'SubjectKindSpecificContract':('LineageReference',withl(neg(GENERAL_APP))),'GeneralizedContract':('LineageReference',withl(GENERAL_APP)),'ContextSpecificLineage':('LineageReference',withl(both(neg(GENERAL_APP),pred('ContractContextSpecificDeclared',CONTRACT)))),'ProductSpecificLineage':('LineageReference',withl(both(neg(GENERAL_APP),pred('KindProductDeclared',KIND)))),'GeneralizedDifferentEndpointKinds':('LineageReference',withl(both(GENERAL_APP,neg(eq(fn('epochSubjectKind',PRE),fn('epochSubjectKind',POST)))))),'SuccessorSameNameAllowed':('LineageReference',withl(both(SUCCESSOR_APP,eq(fn('epochName',PRE),fn('epochName',POST))))),'OtherKindSameIdentityAllowed':('LineageReference',withl(both(OTHER_APP,eq(fn('epochIdentity',PRE),fn('epochIdentity',POST))))),'OtherKindDifferentIdentityAllowed':('LineageReference',withl(both(OTHER_APP,neg(eq(fn('epochIdentity',PRE),fn('epochIdentity',POST)))))),'RenameWithoutActualContinuity':('LineageReference',withl(both(RENAME_APP,neg(pred('LineageActualSameIdentityContinuity',L))))),'GeneralizedWithoutActualAdmission':('LineageReference',withl(both(GENERAL_APP,neg(pred('LineageActualGeneralizedContractAdmission',L)))))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for n in ACTUAL:
  condition=None;label='all-selected-lineages'
  if n in ['SameIdentityContinuity','Rename','NoNewProduct','NoNewProject','NoNewMethod','NoNewGoal','NoNewContext']:condition=RENAME_APP;label='same-identity-rename'
  elif n=='SuccessorIdentity':condition=SUCCESSOR_APP;label='successor-identity'
  elif n in ['GeneralizedContractAdmission','GeneralizedContractApplicability']:condition=GENERAL_APP;label='explicit-generalized-contract-selected'
  scope=APP if condition is None else both(APP,condition)
  rows.append({'query_id':'Lineage-not-Actual'+n,'target':allof([('LineageReference','l')],implies(scope,pred('LineageActual'+n,L))),'witness_condition':exists([('LineageReference','l')],both(scope,neg(pred('LineageActual'+n,L)))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
 chosen={N:(both(*THEORY.values()),['genus-differentia']),F:(both(GENUS,RENAME,BOUNDARIES),['axiomatic-implicit']),'/scope/applicability':(GENUS,['operational']),'/scope/exclusions/0':(selected(neg(pred('LineageIsGenericAliasListDeclared',L))),['operational']),'/scope/exclusions/1':(CONTRACT_RULE,['operational']),'/scope/exclusions/2':(BOUNDARIES,['operational']),'/boundaries/0':(selected(neg(pred('LineageInfersIdentityFromAliasDeclared',L))),['operational']),'/boundaries/1':(CONTRACT_RULE,['operational']),'/boundaries/2':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(KIND_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/1':(GENUS,['operational']),'/voices/scientific_formal/boundary_conditions/2':(CONTRACT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/0':(ENDPOINTS,['operational']),'/voices/scientific_formal/testable_conditions/1':(both(KIND_RULE,RENAME,SUCCESSOR),['operational']),'/voices/scientific_formal/testable_conditions/2':(BOUNDARIES,['operational'])}
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];formula=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Authority-scope correspondence and retained candidate claim ceiling require owner maps;no actual continuity instance.'
  if sel in chosen:formula,forms=chosen[sel];disposition='encoded';roles=['definition'];why='Necessary typed lineage tuple,exact endpoint,rename/successor,subject-kind/generalized-contract and non-effect declarations;real continuity,kind,admission and authority outcomes independent.'
  elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):disposition='explanatory';forms=['unresolved'];roles=['explanation-example'];why='Notation,intuition,Craft Product rename and Context successor examples remain explanatory;no actual continuity,authority or instance inferred.'
  cid='IDL-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(text.encode()),'start_character':0,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':len(text),'excerpt':text})
 deps=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);required=required_populations();populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Authored selected/outside,rename/successor/other,subject-kind-specific/generalized,independent authority and continuity/admission witnesses.','review_ref':None} for n,(carrier,z) in required.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual lineage/epoch/identity/kind/contract/owner/evidence universes and shared source denotations require acceptance.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:identity-lineage-exact-epochs-rename-successor-kind-contract-v1','profile_ref':'profile:identity-lineage-exact-epochs-rename-successor-kind-contract-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'IDL-FINDING-'+str(i).zfill(3),'description':x,'selectors':[N,F,'/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with lineage,identity epoch,subject-kind,contract,Decision,evidence and consumer owners'} for i,x in enumerate(LOSSES,1)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Qualified lineage/identity/subject-kind/contract/governance meanings;no whole upstream theories or accepted operational maps imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'same-identity-rename-with-exact-owned-evidence-tuple','scenario':'Exact predecessor/successor epochs retain declared identity while names differ under a subject-kind-specific lineage contract.','expected_interpretation':'Necessary tuple/kind/rename/non-effect guards hold without actual continuity or authority inferred.','rationale':'Rename is distinct from successor identity and independent carrier/instance admission.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'rename-changes-identity','scenario':'A record classified same-identity rename has different endpoint identity coordinates.','expected_interpretation':'Necessary rename preservation fails.','rationale':'Similar names,owner,content or history cannot replace exact identity preservation.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account.get('character_accounting_complete') is True,account
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  sel=clause['source_selector'];targets=['Lineage-not-ActualContinuity','Lineage-not-ActualAuthority']
  if sel in [N,F]:targets+=['Lineage-not-ActualImmutableStorage','Lineage-not-ActualOwnerAuthorization','Lineage-not-ActualEvidenceAdequacy']
  if sel in ['/scope/exclusions/1','/boundaries/1','/voices/scientific_formal/boundary_conditions/2']:targets+=['Lineage-not-ActualGeneralizedContractAdmission','Lineage-not-ActualSubjectKindScope']
  if sel=='/voices/scientific_formal/testable_conditions/0':targets+=['Lineage-not-ActualPredecessorResolution','Lineage-not-ActualSuccessorResolution']
  if sel=='/voices/scientific_formal/testable_conditions/1':targets+=['Lineage-not-ActualSameIdentityContinuity','Lineage-not-ActualRename','Lineage-not-ActualSuccessorIdentity','Lineage-not-ActualNoNewProduct']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:obligations.append({'source':source,'selector':sel,'start_character':0,'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False});counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(required),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'exact-eight-source-coordinates-plus-explicit-contract-map','rename':'equal-identity-different-name-with-five-no-new-kind-declarations','successor':'distinct-declared-identity-proposed-different-from-rename','other_kind':'no-invented-identity-or-name-equality-rule','contract':'subject-kind-specific-unless-explicit-generalized-recorded-admission-and-coverage','actual_queries':'ten-conditioned-on-rename-successor-or-generalization','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 comp=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comp,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comp]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary exact lineage tuple,rename/successor,subject-kind/generalized-contract and non-effects declarations only;actual continuity,lookup,immutable storage,authority,fidelity and proof pending.'});c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
