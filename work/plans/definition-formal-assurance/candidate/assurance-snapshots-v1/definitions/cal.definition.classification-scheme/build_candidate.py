"""Candidate versioned governed contracts and guarded old-assignment preservation."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:classification-scheme-version-preservation-v1'
SORTS=['SchemeVersion','SchemeFamily','Axis','Value','DefinitionVersion','PolicyRef','OwnerRoute','ScopeRef','ChallengeRoute','Assignment','SubjectRevision','MeaningToken','State','Use']
POLICIES=['cardinality','applicability','exclusions','assignment','evidence','hierarchy','mapping','compatibility']
FUNCTIONS={'schemeFamily':(['SchemeVersion'],'SchemeFamily'),'schemeOwner':(['SchemeVersion'],'OwnerRoute'),'schemeScope':(['SchemeVersion'],'ScopeRef'),'schemeChallenge':(['SchemeVersion'],'ChallengeRoute'),**{n+'Policy':(['SchemeVersion'],'PolicyRef') for n in POLICIES},'assignmentVersionAt':(['Assignment','State'],'SchemeVersion'),'assignmentAxisAt':(['Assignment','State'],'Axis'),'assignmentValueAt':(['Assignment','State'],'Value'),'assignmentSubjectAt':(['Assignment','State'],'SubjectRevision'),'assignmentMeaningAt':(['Assignment','State'],'MeaningToken'),'useDefinition':(['Use'],'DefinitionVersion')}
FLAGS=['ClassificationScheme','GovernedIdentity','GovernedRecord','BoundedScope','VersionedContract','HasAxesContract','HasValuesContract','HasDefinitionsContract','HasOwnerContract','HasChallengeContract']
OUTCOMES=['ActuallyAdmitted','AuthorityGranted','RuntimeActivated','ClassificationTrue','ConsumerSucceeded','ExternalEffect']
SIGNATURE={n:['SchemeVersion'] for n in FLAGS+OUTCOMES}
SIGNATURE.update(DeclaredPolicy=['SchemeVersion','PolicyRef'],AxisIn=['Axis','SchemeVersion'],ValueIn=['Axis','Value','SchemeVersion'],DefinitionIn=['DefinitionVersion','SchemeVersion'],PresentVersion=['SchemeVersion','State'],PresentAssignment=['Assignment','State'],AllowedVersionIntroduction=['SchemeVersion','State','State'],UsesClassificationScheme=['Use'],AdmittedDefinitionSuccessor=['DefinitionVersion'])
def var(n):return {'op':'var','name':n}
def const(n):return {'op':'const','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def bind(bindings,body):
 for op,sort,name in reversed(bindings):body={'op':op,'sort':sort,'var':name,'body':body}
 return body
def allof(bindings,body):return bind([('forall',sort,name) for sort,name in bindings],body)
def exists(bindings,body):return bind([('exists',sort,name) for sort,name in bindings],body)
SCHEME=pred('ClassificationScheme','v')
GENUS=allof([('SchemeVersion','v')],implies(SCHEME,both(either(pred('GovernedIdentity','v'),pred('GovernedRecord','v')),pred('BoundedScope','v'))))
CONTRACT=allof([('SchemeVersion','v')],implies(SCHEME,both(*[pred(n,'v') for n in ['VersionedContract','HasAxesContract','HasValuesContract','HasDefinitionsContract','HasOwnerContract','HasChallengeContract']],*[pred('DeclaredPolicy','v',fn(n+'Policy','v')) for n in POLICIES])))
AV=fn('assignmentVersionAt','a','s')
ASSIGNMENT_TYPING=allof([('Assignment','a'),('State','s')],implies(pred('PresentAssignment','a','s'),both(pred('ClassificationScheme',AV),pred('PresentVersion',AV,'s'),pred('AxisIn',fn('assignmentAxisAt','a','s'),AV),pred('ValueIn',fn('assignmentAxisAt','a','s'),fn('assignmentValueAt','a','s'),AV))))
OLD=both(pred('PresentAssignment','a','s'),pred('PresentVersion',AV,'s'),pred('ClassificationScheme',AV))
RETAIN=both(pred('PresentAssignment','a','t'),pred('PresentVersion',AV,'t'),*[eq(fn(n,'a','s'),fn(n,'a','t')) for n in ['assignmentVersionAt','assignmentAxisAt','assignmentValueAt','assignmentSubjectAt','assignmentMeaningAt']])
FRAME=allof([('SchemeVersion','v'),('State','s'),('State','t')],implies(pred('AllowedVersionIntroduction','v','s','t'),both(SCHEME,neg(pred('PresentVersion','v','s')),pred('PresentVersion','v','t'),allof([('Assignment','a')],implies(OLD,RETAIN)))))
USE=allof([('Use','u')],implies(pred('UsesClassificationScheme','u'),either(eq(fn('useDefinition','u'),const('selectedDefinition')),pred('AdmittedDefinitionSuccessor',fn('useDefinition','u')))))
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input: '+x['path'])
def external_current(context):
 for x in context['external_sources']:
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('External source drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT)
 source=source_ref(snap,'cal.definition.classification-scheme');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets += [text.index('A new Scheme version')]
  if sel==F:offsets += [text.index('ClassificationScheme(x) =/=>')]
  offsets.append(len(text));assert offsets==sorted(set(offsets))
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional'];why='Exact applicability/exclusion, policy denotation, named contract parts, source-owner precedence, no-inference behavior and separately governed effects require independent review; no source admission supplies this interpretation approval.'
   if sel==N and start==0:formula=both(CONTRACT,ASSIGNMENT_TYPING);why='Necessary versioned contract-part and policy-reference conditions plus selected exact axis/value/version typing. References name obligations; they do not execute policies, assert all axes have one value or require nonempty hierarchies/mappings.'
   elif sel==N and start>0:formula=FRAME;why='Candidate allowed version introduction adds a fresh exact version while retaining every selected existing old assignment, its version/axis/value/subject revision/meaning and old version. Guarded normative frame; explicit migrations may create separate successor records. No actual runtime or unbounded trace proof.'
   elif sel==F and start==0:formula=GENUS;why='Preserve governed identity OR governed record and bounded scope as necessary conditions, not a biconditional, mandatory conjunction, identity injectivity or claim of actual admission.'
   elif sel=='/voices/scientific_formal/testable_conditions/0':formula=USE;why='Every selected use resolves the exact Definition constant or a separately supplied admitted successor. Printed names/version prefixes do not establish successor admission or source fidelity.'
   elif sel=='/scope/applicability':formula=CONTRACT;why='Selected governed contract includes axes/value/Definition contracts, eight policy roles, owner/challenge; detailed policy denotations and cardinality remain unresolved.'
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];why='Source intuition, examples, subject notation and workspace retained; an example closed-value scheme does not impose universal single-valued/global closed-world classification.'
   if formula is not None:disposition='encoded';roles=['constraint'] if sel==N and start>0 or sel.endswith('/testable_conditions/0') else ['definition'];forms=['operational'] if sel==N and start>0 else ['axiomatic-implicit']
   cid='CSC-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
 uses=[('definition',N,'Exact Definition version/resolved admitted successor and meaning contracts are distinct from labels and schema versions.'),('classification-axis',N,'Axes are scoped owned dimensions; Scheme contract does not collapse them into status/authority.'),('classification-value',N,'Allowed values require exact axis/Scheme-version agreement, not equal printed strings.'),('classification-assignment',N,'Versioned assignment identity/subject revision/basis and correction history need immutable-record mapping.'),('classification',N,'Classification is a scoped semantic judgment, not identity equivalence or admission.'),('classification-orthogonality-invariant',N,'Independent questions and coupling rules need aligned meaning; axis lists alone do not prove orthogonality.'),('schema','/boundaries/1','Closed carrier shape and format discriminator do not implement policy/version-preservation semantics.'),('policy',N,'Cardinality/applicability/exclusion/assignment/evidence/hierarchy/mapping/compatibility require separately selected rule semantics.'),('evidence',N,'Evidence policy/reference presence does not supply truth or operational compliance.'),('authority',F,'Term, contract typing and admitted source do not infer authority or effects.'),('identity-lineage',N,'Predecessor/successor/version and corrected assignment history need independent identity and lineage maps.'),('typed-relation','/boundaries/1','Hierarchy/mapping/compatibility/challenge relations require separately governed exact endpoints/Kind/qualifiers.'),('governed-model',N,'A versioned contract is a bounded governed model; constituent contract-part and own review obligations remain distinct.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':res,'definedness_policy':None} for n,(args,res) in FUNCTIONS.items()]+[{'kind':'constant','symbol_id':'selectedDefinition','scope':SCOPE,'result_sort':'DefinitionVersion'}]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required={'ClassificationScheme':('SchemeVersion',exists([('SchemeVersion','v')],SCHEME)),'AssignedAxis':('Assignment',exists([('Assignment','a'),('State','s')],pred('PresentAssignment','a','s'))),'SameFamilyVersions':('SchemeVersion',exists([('SchemeVersion','v'),('SchemeVersion','w')],both(SCHEME,pred('ClassificationScheme','w'),neg(eq(var('v'),var('w'))),eq(fn('schemeFamily','v'),fn('schemeFamily','w'))))),'PreservedOldAssignment':('Assignment',exists([('Assignment','a'),('State','s'),('State','t'),('SchemeVersion','v')],both(pred('AllowedVersionIntroduction','v','s','t'),OLD,neg(eq(AV,var('v')))))),'DefinitionUse':('Use',exists([('Use','u')],pred('UsesClassificationScheme','u')))}
 populations=[{'population_id':'POP-'+n,'carrier':carrier,'predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Connected hypothetical versioned-contract/use/assignment/introduction witnesses prevent vacuity. These are not created/admitted world records.','review_ref':None} for n,(carrier,statement) in required.items()]
 for n,args in SIGNATURE.items():
  if n in required:continue
  populations.append({'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Existence/exemption and exact policy/model/authority scope need independent review; no actual effect or per-axis universal cardinality inferred.','review_ref':None})
 core={'interpretation_id':'interpretation:classification-scheme-version-preservation-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:classification-scheme-versioned-contract-candidate'}
 descriptions=[('CSC-POLICY-001','Eight typed policy references name cardinality/applicability/exclusion/assignment/evidence/hierarchy/mapping/compatibility roles; their executable meaning and completeness remain open.'),('CSC-VERSION-002','Exact Scheme version and assignment meaning token require reviewed identity/reference maps; carrier format schema_version is not an instance version.'),('CSC-FRAME-003','AllowedVersionIntroduction is a selected normative no-silent-change action. General migration/correction/challenge operations, traces, atomicity and runtime compliance need separate contracts; no universal runtime theorem.'),('CSC-PRECEDENCE-004','Whole-file candidate classification review proposes one-or-more axes/minimum content and historical gaps; current normalized Definition and admitted carrier precedence require review. Schema accepts empty lists/rule strings; historical no-admission gaps are not current truth.'),('CSC-CLOSURE-005','Thirteen authored semantic uses, policy/axis/value/assignment lineage and common-carrier closure remain unreviewed.'),('CSC-INFERENCE-006','Non-entailment of admission/authority/truth/success/effects does not establish actual consumers refrain from forbidden inference or approved scope membership.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with classification/scheme/assignment/policy/lineage/artifact-type/authority owners'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Thirteen selected semantic uses lack reviewed complete denominator/common-carrier maps.','Policy denotation, instance-version resolution and immutable assignment/history mapping remain open.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'new-version-old-assignment-retained','scenario':'Add sv2 while old assignment a remains bound to sv1/old subject revision/axis/value/meaning. An explicitly selected migration may create a separate successor under sv2.','expected_interpretation':'Old record/meaning retained, exact fresh version bound. No assignment write or permission created.','rationale':'Version evolution requires preserved old interpretations.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'new-version-reinterprets-old-assignment','scenario':'An upgrade keeps old assignment label but changes its version, axis, value, subject revision or meaning token.','expected_interpretation':'Selected allowed introduction fails the preservation frame.','rationale':'Stable label alone does not preserve meaning.','related_clause_ids':encoded}],'known_losses':['No owner-approved policy or version/meaning semantics.','No complete immutable assignment/correction implementation or unbounded operational proof.','No approved source precedence, common-carrier alignment, world truth or consumer no-inference compliance.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[{'query_id':'scheme-not-'+n,'target':allof([('SchemeVersion','v')],implies(SCHEME,pred(n,'v'))),'witness_condition':exists([('SchemeVersion','v')],both(SCHEME,neg(pred(n,'v')))),'selected_in_T':False} for n in OUTCOMES]
 # Policy roles may share a reference; distinct printed role names do not force distinct identities.
 for name,left,right in [('all-policy-roles-distinct',fn('cardinalityPolicy','v'),fn('compatibilityPolicy','v'))]:
  queries.append({'query_id':name,'target':allof([('SchemeVersion','v')],implies(SCHEME,neg(eq(left,right)))),'witness_condition':exists([('SchemeVersion','v')],both(SCHEME,eq(left,right))),'selected_in_T':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
