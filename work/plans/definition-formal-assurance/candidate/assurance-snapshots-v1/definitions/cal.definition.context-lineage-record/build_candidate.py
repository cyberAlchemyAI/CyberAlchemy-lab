"""Context identity, typed anchors, kind/cardinality and normative-change boundaries."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
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
 with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
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
SCOPE='scope:candidate:ContextLineageRecord-closed-disposition-and-history-no-inference-v1'
SORTS=['Entity','Field','Kind','Token']
FIELDS=['id','predecessor_context_ref','successor_context_refs','lineage_kind','source_version','destination_versions','preserved_scope','changed_scope','decision_ref','evidence_refs','effective_boundary','challenge_route','residue']
KINDS=['PRESERVED','SUCCESSOR','SPLIT','MERGED','SUPERSEDED','WITHDRAWN']
CONSTANTS={'EMPTY':'Token',**{'F_'+n:'Field' for n in FIELDS},**{n:'Kind' for n in KINDS}}
FUNCTIONS={'fieldValue':(['Entity','Field'],'Token'),'lineageKindValue':(['Entity'],'Kind')}
QUALIFIERS=['ImmutableStatement','OwnerQualified','RelatesExactContextIdentities','OneTypedLineageDisposition','IncludesVersionReferences','IncludesIndependentScopeStatements','IncludesDecisionEvidence','IncludesEffectiveBoundary','IncludesChallengeRoute','IncludesResidue']
ROLES=['MigrationManifestRole','SourceAdmissionRole','ContextMapRole','AliasRole','RedirectRole','GitRenameRole','EquivalenceProofRole','PromotionDecisionRole','DeletePermissionRole']
OUTCOMES=['ActualLineageEstablished','ActualSemanticEquivalence','ActualAdmission','ActualDeletionPermission','ActualMigrationCompleted','ActualOwnerResolution','ActualVersionResolution','ActualIdentityContinuity','ActualHistoryRetained','ActualImmutabilityGuaranteed','ActualAuthority','ActualRuntimeEffect']
SIGNATURE={n:['Entity'] for n in ['ContextLineageRecord',*QUALIFIERS,*ROLES,*OUTCOMES,'RecordsIdentityHistory','InfersEquivalence','InfersAdmission','PredecessorVersionExact','SuccessorVersionsExact','PreservedScopeIndependentlyStated','ChangedScopeIndependentlyStated','HistoryRetentionRequired','DirectoryContinuous','RawDeclaredComplete','PredecessorPresent']}
SIGNATURE['DeclaresField']=['Entity','Field']
LR=pred('ContextLineageRecord','r')
def field(n):return fn('fieldValue','r',const('F_'+n))
def allowed(value,names):return either(*[eq(value,const(n)) for n in names])
GENUS=allof([('Entity','r')],{'op':'iff','left':LR,'right':both(*[pred(n,'r') for n in QUALIFIERS])})
DECLARATION=allof([('Entity','r')],implies(LR,allof([('Field','f')],implies(allowed(var('f'),['F_'+n for n in FIELDS]),pred('DeclaresField','r','f')))))
KIND_ENUM=allof([('Entity','r')],implies(LR,both(allowed(fn('lineageKindValue','r'),KINDS),both(*[neg(eq(const(a),const(z))) for i,a in enumerate(KINDS) for z in KINDS[i+1:]]))))
REQUIRED_FIELDS=allof([('Entity','r')],implies(LR,both(*[neg(eq(field(n),const('EMPTY'))) for n in ['decision_ref','evidence_refs','challenge_route']])))
IDENTITY_HISTORY=allof([('Entity','r')],implies(LR,pred('RecordsIdentityHistory','r')))
NO_INFERENCE=allof([('Entity','r')],implies(LR,both(neg(pred('InfersEquivalence','r')),neg(pred('InfersAdmission','r')))))
EXACT_VERSIONS=allof([('Entity','r')],implies(LR,both(pred('PredecessorVersionExact','r'),pred('SuccessorVersionsExact','r'))))
SCOPES=allof([('Entity','r')],implies(LR,both(pred('PreservedScopeIndependentlyStated','r'),pred('ChangedScopeIndependentlyStated','r'))))
NONCOLLAPSE=allof([('Entity','r')],implies(LR,both(*[neg(pred(n,'r')) for n in ROLES])))
HISTORY=allof([('Entity','r')],implies(both(LR,allowed(fn('lineageKindValue','r'),['WITHDRAWN','SUPERSEDED'])),pred('HistoryRetentionRequired','r')))
THEORY=[GENUS,DECLARATION,KIND_ENUM,REQUIRED_FIELDS,IDENTITY_HISTORY,NO_INFERENCE,EXACT_VERSIONS,SCOPES,NONCOLLAPSE,HISTORY]
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT);source=source_ref(snap,'cal.definition.context-lineage-record');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';norm=texts[N];formal=texts[F]
 first,second=norm.split('. ',1);first+='.'
 chosen=[(N,first,both(GENUS,DECLARATION),['genus-differentia','axiomatic-implicit']),(N,second,both(IDENTITY_HISTORY,NO_INFERENCE),['axiomatic-implicit']),(F,formal.split(';')[0],DECLARATION,['axiomatic-implicit']),(F,'lineage_kind in {preserved, successor, split, merged, superseded, withdrawn}',KIND_ENUM,['finite-enumeration']),(F,'Lineage does not imply Equivalence or Admission.',NO_INFERENCE,['axiomatic-implicit']),('/voices/scientific_formal/boundary_conditions/0',texts['/voices/scientific_formal/boundary_conditions/0'],EXACT_VERSIONS,['axiomatic-implicit']),('/voices/scientific_formal/boundary_conditions/1',texts['/voices/scientific_formal/boundary_conditions/1'],SCOPES,['axiomatic-implicit']),('/voices/scientific_formal/testable_conditions/0',texts['/voices/scientific_formal/testable_conditions/0'],KIND_ENUM,['finite-enumeration']),('/voices/scientific_formal/testable_conditions/1',texts['/voices/scientific_formal/testable_conditions/1'],REQUIRED_FIELDS,['axiomatic-implicit']),('/voices/scientific_formal/testable_conditions/2',texts['/voices/scientific_formal/testable_conditions/2'],NO_INFERENCE,['axiomatic-implicit']),('/boundaries/0',texts['/boundaries/0'],NONCOLLAPSE,['axiomatic-implicit']),('/boundaries/1',texts['/boundaries/1'],HISTORY,['axiomatic-implicit','operational'])]
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];cuts={0,len(text)}
  for selector,excerpt,_,_ in chosen:
   if selector==sel:start=text.index(excerpt);cuts.update([start,start+len(excerpt)])
  points=sorted(cuts)
  for start,end in zip(points,points[1:]):
   excerpt=text[start:end];statement=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Actual owner,context/version/scope/evidence maps,disposition cardinality and universal immutable/history behavior remain pending.'
   for selector,selected,formula,selected_forms in chosen:
    if sel==selector and excerpt==selected:statement=formula;disposition='encoded';forms=selected_forms;roles=['definition'];why='Candidate genus,declared tuple,distinct closed kinds,opaque decision/evidence/challenge presence,exact-version/scope markers,no-inference and normative history retention. Does not assert actual outcomes or bind real identities.'
   if statement is None and (sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/')):disposition='explanatory';roles=['explanation-example'];why='Selected intuition and examples do not establish an actual split,context placement,owner or migration.'
   cid='CLR-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':statement,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 names=['context','bounded-context','coordination-context','context-map','context-migration-manifest','identity-carrier','identity-relation','identity-lineage','semantic-equivalence','decision','evidence','residue','authority','authority-promotion','source','source-admission','typed-relation','relation-kind','representation-revision','semantic-event-history','governance-event-history']
 available={x['definition_id'] for x in snap['current_entries']};missing=[n for n in names if 'cal.definition.'+n not in available];deps=[source_ref(snap,'cal.definition.'+n) for n in names if 'cal.definition.'+n in available];primary=clauses[0]['clause_id']
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 def haskind(k):return exists([('Entity','r')],both(LR,eq(fn('lineageKindValue','r'),const(k))))
 required={'ContextLineageRecord':exists([('Entity','r')],LR),**{n.title()+'Disposition':haskind(n) for n in KINDS},'OptionalPredecessorAbsent':exists([('Entity','r')],both(LR,neg(pred('PredecessorPresent','r')))),'RawFieldsWithoutLineage':exists([('Entity','r')],both(pred('RawDeclaredComplete','r'),neg(LR))),'LineageWithoutActualOutcomes':exists([('Entity','r')],both(LR,*[neg(pred(n,'r')) for n in OUTCOMES])),'DirectoryWithoutIdentityContinuity':exists([('Entity','r')],both(pred('DirectoryContinuous','r'),neg(pred('ActualIdentityContinuity','r')))),'RequiredHistoryWithoutActualRetention':exists([('Entity','r')],both(LR,pred('HistoryRetentionRequired','r'),neg(pred('ActualHistoryRetained','r'))))}
 populations=[{'population_id':'POP-'+n,'carrier':'Entity','predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Supplied disposition,optional predecessor and no-actual-outcome witnesses; actual populations unaccepted.','review_ref':None} for n,z in required.items()]+[{'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual owner/context/version/scope/field and history denotation pending.','review_ref':None} for n,args in SIGNATURE.items() if n not in required]
 core={'interpretation_id':'interpretation:ContextLineageRecord-closed-disposition-no-inference-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:ContextLineageRecord-qualified-history-v1'}
 losses=['Genus iff and opaque qualification/immutability/version/scope markers need source-owner meaning approval.','13 declared fields,optional predecessor and separate lists need actual record maps; source gives no universal successor cardinality or pairing algorithm.','Six lineage tags have explicit candidate distinctness; preserved/successor/split/merged/superseded/withdrawn semantics need independent review.','Nonempty decision/evidence/challenge Tokens do not authenticate owners,decisions,evidence or routes.','No-inference flags do not negate independently established actual equivalence/admission facts.','Normative withdrawal/supersession retention and immutable markers do not prove temporal preservation or forbid all actual deletion under separate authority.','D29/D66 exact historical source selections are recorded references; current external bytes and context identity reinterpretation remain unverified.','All authored dependencies require independent mapping; unavailable exact identities: '+','.join(missing)]
 findings=[{'finding_id':'CLR-FINDING-'+str(i+1).zfill(3),'selectors':[N,F,'/boundaries/0','/scope/applicability'],'description':why,'status':'unresolved','owner_route':'role:definition-owner with context,lineage,evidence and lifecycle owners'} for i,why in enumerate(losses)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Exact authored use requires independent meaning/role alignment.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':losses},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'qualified-split-disposition','scenario':'A hypothetical immutable split record declares exact identities,versions,scope,decision evidence and challenge.','expected_interpretation':'Typed identity-history statement without inferred equivalence/admission.','rationale':'Candidate declaration is not actual resolution or transition.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'directory-continuity-as-identity-proof','scenario':'A Git rename or directory continuity is treated as lineage,identity equivalence or deletion permission.','expected_interpretation':'Role boundary and nonentailment separate those claims.','rationale':'Filesystem observations do not establish semantic identity.','related_clause_ids':[primary]}],'known_losses':losses,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account.get('character_accounting_complete'),account
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=[]
 for n in OUTCOMES:queries.append({'query_id':'lineage-not-'+n,'target':allof([('Entity','r')],implies(LR,pred(n,'r'))),'witness_condition':required['LineageWithoutActualOutcomes'],'selected_in_T':False,'source_fidelity':'pending'})
 queries += [{'query_id':'directory-continuity-not-semantic-identity','target':allof([('Entity','r')],implies(pred('DirectoryContinuous','r'),pred('ActualIdentityContinuity','r'))),'witness_condition':required['DirectoryWithoutIdentityContinuity'],'selected_in_T':False,'source_fidelity':'pending'},{'query_id':'raw-tuple-not-lineage','target':allof([('Entity','r')],implies(pred('RawDeclaredComplete','r'),LR)),'witness_condition':required['RawFieldsWithoutLineage'],'selected_in_T':False,'source_fidelity':'pending'}]
 put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':len(required),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'source_precedence_reviewed':False,'mechanized_proof':False,'known_losses':losses,'unavailable_exact_dependency_labels':missing})
 comp=[source_ref(snap,'cal.definition.'+n) for n in ['context','bounded-context','coordination-context','context-map','context-migration-manifest','identity-relation']]
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comp,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comp]+[ref(BASE/'definitions/cal.definition.context'/n) for n in ['t.json','static-ir.json','REVIEW.md','delivery-manifest.json']],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':[],'source_fidelity':'pending','claim_ceiling':'Distinct Context,DDD,Coordination,Map,Migration and IdentityRelation candidates; no shared lineage/identity/meaning accepted.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
