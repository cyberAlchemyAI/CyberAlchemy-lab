"""Versioned allowed answers, common-carrier label controls and preservation frames."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:classification-value-scoped-meaning-v1'
SORTS=['Value','Axis','SchemeVersion','CommonToken','MeaningToken','DefinitionVersion','PolicyRef','State','Use']
POLICIES=['applicability','exclusions','mapping']
FUNCTIONS={'axisAt':(['Value','State'],'Axis'),'schemeAt':(['Value','State'],'SchemeVersion'),'identityAt':(['Value','State'],'CommonToken'),'labelAt':(['Value','State'],'CommonToken'),'meaningAt':(['Value','State'],'MeaningToken'),'definitionAt':(['Value','State'],'DefinitionVersion'),**{n+'Policy':(['Value'],'PolicyRef') for n in POLICIES},'useDefinition':(['Use'],'DefinitionVersion')}
FLAGS=['ClassificationValue','GovernedIdentity','GovernedRecord','BoundedScope','GovernedAllowedAnswer','HasMeaningContract','HasApplicabilityContract','HasExclusionsContract','HasMappingsContract']
OUTCOMES=['ActuallyAdmitted','AuthorityGranted','RuntimeActivated','ClassificationTrue','ConsumerSucceeded','ExternalEffect']
SIGNATURE={n:['Value'] for n in FLAGS+OUTCOMES}
SIGNATURE.update(PresentValue=['Value','State'],Binding=['Value','Axis','SchemeVersion','State'],AxisDeclaredIn=['Axis','SchemeVersion'],AllowedAnswer=['Value','Axis','SchemeVersion'],DeclaredPolicy=['Value','PolicyRef'],AllowedLabelChange=['Value','State','State'],AllowedLabelOnlyCoalescence=['Value','Value','State'],UsesClassificationValue=['Use'],AdmittedDefinitionSuccessor=['DefinitionVersion'])
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
VALUE=pred('ClassificationValue','v');PRESENT=both(VALUE,pred('PresentValue','v','s'))
GENUS=allof([('Value','v')],implies(VALUE,both(either(pred('GovernedIdentity','v'),pred('GovernedRecord','v')),pred('BoundedScope','v'))))
CHARACTERISTIC=allof([('Value','v')],implies(VALUE,both(*[pred(n,'v') for n in ['GovernedAllowedAnswer','HasMeaningContract','HasApplicabilityContract','HasExclusionsContract','HasMappingsContract']],*[pred('DeclaredPolicy','v',fn(n+'Policy','v')) for n in POLICIES])))
BOUND=allof([('Value','v'),('State','s')],implies(pred('PresentValue','v','s'),both(VALUE,pred('AxisDeclaredIn',fn('axisAt','v','s'),fn('schemeAt','v','s')),pred('AllowedAnswer','v',fn('axisAt','v','s'),fn('schemeAt','v','s')),pred('Binding','v',fn('axisAt','v','s'),fn('schemeAt','v','s'),'s'))))
EXACT=allof([('Value','v'),('Axis','a'),('SchemeVersion','sv'),('State','s')],implies(pred('Binding','v','a','sv','s'),both(PRESENT,eq(var('a'),fn('axisAt','v','s')),eq(var('sv'),fn('schemeAt','v','s')))))
FRAME=allof([('Value','v'),('State','s'),('State','t')],implies(pred('AllowedLabelChange','v','s','t'),both(PRESENT,pred('PresentValue','v','t'),*[eq(fn(n,'v','s'),fn(n,'v','t')) for n in ['axisAt','schemeAt','identityAt','meaningAt','definitionAt']])) )
PAIR=both(PRESENT,pred('ClassificationValue','w'),pred('PresentValue','w','s'),eq(fn('labelAt','v','s'),fn('labelAt','w','s')))
DIFFERENT=either(*[neg(eq(fn(n,'v','s'),fn(n,'w','s'))) for n in ['axisAt','schemeAt','identityAt','meaningAt']])
LABEL_POLICY=allof([('Value','v'),('Value','w'),('State','s')],implies(both(PAIR,DIFFERENT),neg(pred('AllowedLabelOnlyCoalescence','v','w','s'))))
USE=allof([('Use','u')],implies(pred('UsesClassificationValue','u'),either(eq(fn('useDefinition','u'),const('selectedDefinition')),pred('AdmittedDefinitionSuccessor',fn('useDefinition','u')))))
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
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT)
 source=source_ref(snap,'cal.definition.classification-value');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets += [text.index('Its label is not')]
  if sel==F:offsets += [text.index('ClassificationValue(x) =/=>')]
  offsets.append(len(text));assert offsets==sorted(set(offsets))
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional'];why='Exact applicability/exclusion/meaning, identity/label mapping, reference resolution, source-owner precedence and independently governed effect/inference compliance require review.'
   if sel==N and start==0:formula=both(CHARACTERISTIC,BOUND,EXACT,FRAME);why='Candidate necessary governed allowed-answer/policy conditions; present values bind exactly one declared axis and Scheme version. Selected pure label changes preserve identity, meaning, exact axis/version and Definition reference. Policy names and finite frame are not actual semantics/resolution/runtime proof.'
   elif sel==N and start>0:formula=LABEL_POLICY;why='Selected allowed label-only coalescence cannot collapse differently scoped/bound/identified/interpreted present values because their labels match. Equal label strings may occur; explicit reviewed bridges and actual consumer behavior remain separate obligations.'
   elif sel==F and start==0:formula=GENUS;why='Preserve governed identity OR governed record and bounded scope as necessary conditions; no biconditional, mandatory conjunction or actual admission.'
   elif sel=='/voices/scientific_formal/testable_conditions/0':formula=USE;why='Selected uses resolve this exact Definition constant or a separately supplied admitted successor; label or prefix matching supplies no successor admission.'
   elif sel=='/scope/applicability':formula=both(CHARACTERISTIC,BOUND,EXACT);why='Selected bounded value contract applies to exact allowed answers. Mappings/applicability/exclusions are declared role references, not complete policy denotation.'
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];why='Source intuition/identifiers/examples retained: result-posture and evidence-posture questions differ; display text does not establish identity, truth or authority.'
   if formula is not None:
    disposition='encoded';roles=['constraint'] if sel==N and start>0 or sel.endswith('/testable_conditions/0') else ['definition'];forms=['axiomatic-implicit']
    if sel==N and start==0:forms.append('operational');roles.append('constraint')
   cid='CLV-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
 uses=[('definition',N,'Exact Definition resolution and answer meaning references need independently reviewed identity/version maps.'),('classification-axis',N,'Value answers one exact axis question, not a name-only enum or another question.'),('classification-scheme',N,'Allowed-value sets and version compatibility do not silently reinterpret old meanings.'),('classification-assignment',N,'An allowed answer is not an attributable exact subject-revision assignment or its outcome.'),('classification',N,'Classification judgment and truth are separate from allowed-value vocabulary.'),('classification-orthogonality-invariant',N,'Similar labels cannot silently collapse independent questions; semantic common-carrier maps remain unresolved.'),('schema','/boundaries/1','Closed value carrier shape does not resolve exact axis/Scheme/Definition reference semantics.'),('policy',N,'Applicability/exclusion/mapping rules require separately chosen interpretation and authorization.'),('evidence',F,'Evidence and conviction do not make an allowed answer true of a subject.'),('authority',F,'Term, shape, admitted source and permitted display update do not grant authority or effects.'),('identity-carrier',N,'Stable governed value identity is distinct from label, answer Definition and classified subject.'),('identity-lineage',N,'Stable meaning across revisions and explicit successor/mapping histories require exact lineage.'),('typed-relation','/boundaries/1','Hierarchy, membership, successor and instance projections need separately admitted relation contracts.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':res,'definedness_policy':None} for n,(args,res) in FUNCTIONS.items()]+[{'kind':'constant','symbol_id':'selectedDefinition','scope':SCOPE,'result_sort':'DefinitionVersion'}]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required={'ClassificationValue':('Value',exists([('Value','v')],VALUE)),'PresentAllowedAnswer':('Value',exists([('Value','v'),('State','s')],PRESENT)),'SameLabelsDistinctAxesAndMeanings':('Value',exists([('Value','v'),('Value','w'),('State','s')],both(PAIR,neg(eq(fn('axisAt','v','s'),fn('axisAt','w','s'))),neg(eq(fn('identityAt','v','s'),fn('identityAt','w','s'))),neg(eq(fn('meaningAt','v','s'),fn('meaningAt','w','s')))))),'PureDisplayChange':('Value',exists([('Value','v'),('State','s'),('State','t')],both(pred('AllowedLabelChange','v','s','t'),neg(eq(fn('labelAt','v','s'),fn('labelAt','v','t')))))),'DefinitionUse':('Use',exists([('Use','u')],pred('UsesClassificationValue','u')))}
 populations=[{'population_id':'POP-'+n,'carrier':carrier,'predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Connected hypothetical governed value, colliding labels with distinct scoped identities/meanings, display-change and exact-use witnesses prevent vacuity; no world values or assignments created.','review_ref':None} for n,(carrier,statement) in required.items()]
 for n,args in SIGNATURE.items():
  if n in required:continue
  populations.append({'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Existence/exemption and exact policy/effect/reference/bridge populations require owner review; no fake empty-world exemption or label uniqueness.','review_ref':None})
 core={'interpretation_id':'interpretation:classification-value-scoped-meaning-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:classification-value-identity-label-binding-candidate'}
 descriptions=[('CLV-MEANING-001','Meaning tokens, exact answer Definition/version and value/axis/Scheme identity need source-owner denotation and common-carrier maps.'),('CLV-LABEL-002','Allowed label-only coalescence and pure display-change frames are selected normative semantics, not actual consumers refraining from unsupported inference or runtime preservation.'),('CLV-POLICY-003','Applicability/exclusions/mappings and optional hierarchy/compatibility require separately chosen rule/bridge denotation; a reference is not executed policy.'),('CLV-PRECEDENCE-004','Whole-file candidate review proposes internal axis/value records until independent lifecycle and additional value content. Current standalone carrier admission, normalized Definition and review require explicit precedence; historical review gaps are stale.'),('CLV-RESOLUTION-005','Current carrier strings do not themselves resolve exact axes/Scheme versions/Definition meanings, parents or mappings. Selected fixtures are not one literal joined Scheme/Value/Assignment model.'),('CLV-CLOSURE-006','Thirteen authored uses and complete aligned semantic closure remain unreviewed; identity/reference/successor/common-meaning equivalence cannot be supplied by nominal symbols.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with value/axis/scheme/assignment/identity/policy/artifact-type/authority owners'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Thirteen authored semantic uses lack independently reviewed complete denominator/common-carrier maps.','Meaning, identity, policy and instance-reference resolution remain open.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'same-label-distinct-answers-pure-display-change','scenario':'Two values answer different axes with the same display token but distinct identity/meaning. One display label changes while exact value bindings persist.','expected_interpretation':'Equal display tokens do not authorize coalescence; pure display change preserves identity/meaning/version/axis/Definition.','rationale':'Label is a projection, not identity.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'display-rename-changes-axis-version-or-meaning','scenario':'A claimed label-only update changes axis, Scheme version, identity, meaning or answer Definition, or matching labels authorize merging distinct meanings.','expected_interpretation':'Selected allowed frame/coalescence condition fails.','rationale':'Stable text or a matching label does not preserve meaning.','related_clause_ids':encoded}],'known_losses':['No approved identity/meaning/reference/bridge denotation.','No complete policy/hierarchy/mapping or assignment interpretation.','No actual consumer/no-inference/runtime compliance or meaning-aligned closure.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[{'query_id':'value-not-'+n,'target':allof([('Value','v')],implies(VALUE,pred(n,'v'))),'witness_condition':exists([('Value','v')],both(VALUE,neg(pred(n,'v')))),'selected_in_T':False} for n in OUTCOMES]
 for name,left,right,equal in [('equal-labels-not-identity-equivalence',fn('identityAt','v','s'),fn('identityAt','w','s'),True),('equal-labels-not-meaning-equivalence',fn('meaningAt','v','s'),fn('meaningAt','w','s'),True),('label-is-not-mandatorily-the-identity-token',fn('labelAt','v','s'),fn('identityAt','v','s'),True)]:
  bindings=[('Value','v'),('Value','w'),('State','s')];condition=PAIR
  queries.append({'query_id':name,'target':allof(bindings,implies(condition,eq(left,right))),'witness_condition':exists(bindings,both(condition,neg(eq(left,right)))),'selected_in_T':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
