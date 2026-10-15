"""Canonical axis purpose, nonredundancy, explicit coupling and no silent advancement."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:classification-orthogonality-v1'
SORTS=['Kind','Axis','Purpose','OwnerRoute','Relation','EvidenceRef','EffectDescription','Label','Object','State','AxisValue']
FUNCTIONS={'couplingKind':(['Relation'],'Kind'),'axisPurpose':(['Axis'],'Purpose'),'axisOwner':(['Axis'],'OwnerRoute'),'couplingSource':(['Relation'],'Axis'),'couplingTarget':(['Relation'],'Axis'),'couplingOwner':(['Relation'],'OwnerRoute'),'axisValueAt':(['Object','Axis','State'],'AxisValue')}
AXIS_FLAGS=['CanonicalAxis','AdmissibleAxis','NamedAxis','OwnedAxis','DistinctOperationalPurpose','RedundantAxis','AuthorityAxis','ReviewedAxis','KnownNoData','DataAvailable','NamedUniqueQuestion','NamedRoutingDecision','NamedValidationEffect']
OUTCOMES=['ActuallyAdmitted','AuthorityGranted','RuntimeActivated','Published','StatisticalIndependenceProved','HilbertOrthogonalityProved','ContextualityObstructionProved','CrossDocumentConsistencyProved']
SIGNATURE={n:['Axis'] for n in AXIS_FLAGS+OUTCOMES}
SIGNATURE.update(NamedKind=['Kind'],ExplicitKind=['Relation'],TypedCoupling=['Relation'],ExplicitDirection=['Relation'],ExplicitOwner=['Relation'],CanonicalLabel=['Label'],ConvenienceLabel=['Label'],GeneratedProjection=['Label'],RedundantLabel=['Label'],Dependent=['Axis','Axis'],SilentInference=['Axis','Axis'],HasEvidence=['Relation','EvidenceRef'],HasEffectDescription=['Relation','EffectDescription'],AllowedAxisChange=['Object','Axis','State','State'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Axis','a',body)
def axes(body):return every(quant('forall','Axis','z',body))
def witness(body):return quant('exists','Axis','a',body)
SELECTED=either(pred('CanonicalAxis','a'),pred('AdmissibleAxis','a'))
CANONICAL=pred('CanonicalAxis','a')
QUALITIES=both(pred('NamedAxis','a'),pred('OwnedAxis','a'),pred('DistinctOperationalPurpose','a'),neg(pred('RedundantAxis','a')))
PURPOSE=every(implies(SELECTED,QUALITIES))
DISTINCT_PURPOSE=axes(implies(both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(var('a'),var('z')))),neg(eq(fn('axisPurpose','a'),fn('axisPurpose','z')))))
VECTOR=both(pred('TypedCoupling','r'),pred('ExplicitKind','r'),pred('NamedKind',fn('couplingKind','r')),pred('ExplicitDirection','r'),pred('ExplicitOwner','r'),quant('exists','EvidenceRef','e',pred('HasEvidence','r','e')),quant('exists','EffectDescription','eff',pred('HasEffectDescription','r','eff')),eq(fn('couplingSource','r'),var('a')),eq(fn('couplingTarget','r'),var('z')))
COUPLED=quant('exists','Relation','r',VECTOR)
DEPENDENCY=axes(implies(both(SELECTED,pred('Dependent','a','z')),COUPLED))
NO_SILENT=axes(implies(both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(var('a'),var('z')))),neg(pred('SilentInference','a','z'))))
LABELS=quant('forall','Label','l',both(implies(pred('CanonicalLabel','l'),neg(pred('RedundantLabel','l'))),implies(pred('ConvenienceLabel','l'),both(pred('GeneratedProjection','l'),neg(pred('CanonicalLabel','l'))))))
NODATA=every(implies(both(pred('ReviewedAxis','a'),pred('KnownNoData','a')),either(pred('NamedUniqueQuestion','a'),pred('NamedRoutingDecision','a'),pred('NamedValidationEffect','a'))))
DATA_SEPARATION=every(implies(pred('KnownNoData','a'),neg(pred('DataAvailable','a'))))
FRAME=quant('forall','Object','o',axes(quant('forall','State','s',quant('forall','State','t',implies(both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(var('a'),var('z'))),pred('AuthorityAxis','z'),pred('AllowedAxisChange','o','a','s','t'),neg(COUPLED)),eq(fn('axisValueAt','o','z','s'),fn('axisValueAt','o','z','t')))))))
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
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('Selected external bytes drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT)
 source=source_ref(snap,'cal.definition.classification-orthogonality-invariant');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:
   offsets += [text.index('Target-specific normative meaning:'),text.index('Bound source-semantic basis:'),text.index('A classification is orthogonal')]
  elif sel==F:offsets += [text.index('When data exists,'),text.index('In this definition, orthogonality')]
  elif sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0']:offsets += [text.index('This term does not authorize'),text.index('The imported house_project')]
  offsets.append(len(text));assert offsets==sorted(set(offsets));
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional'];why='Exact source identity/carrier/owner/admission, mathematical bridge, inherited formula precedence and source fidelity need review; none is supplied by a convenient label or a finite witness.'
   if sel==N and excerpt.startswith('Target-specific'):formula=both(PURPOSE,DISTINCT_PURPOSE,NO_SILENT,DEPENDENCY,LABELS);why='Candidate source-precedence selection: distinct semantic purposes, no redundant canonical label, explicit dependency, generated convenience labels and no silent cross-axis inference. Meaning uniqueness is scoped, not global printed-string injectivity.'
   elif sel==N and excerpt.startswith('Bound source'):formula=PURPOSE;why='Admissibility and canonical-axis flags require an owned named nonredundant distinct operational purpose; necessary conditions do not confer actual admission.'
   elif sel==N and excerpt.startswith('A classification is orthogonal'):formula=both(DEPENDENCY,FRAME);why='Selected allowed change preserves a different authority-axis value unless a complete ordered coupling is explicitly present. This normative frame is not actual compliance, declared dependence does not force co-change, and before-downstream ordering remains deferred.'
   elif sel==F and excerpt.startswith('When data exists,'):formula=both(NODATA,DATA_SEPARATION);why='Known lack of data during review requires a named question/routing decision/validation effect. Available data may support metrics but statistics are not mandatory for exploration. Unknown availability is not an absent-data fact.'
   elif sel=='/scope/applicability':formula=both(PURPOSE,DEPENDENCY);why='Adding taxonomy/status/confidence/maturity/source-role/node-type/task-kind labels must retain a distinct operational purpose and explicit unavoidable dependency; exact axis meanings remain owner-reviewed.'
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];why='Intuition, historical framing and identifiers retained; source lineage does not merge sibling identities, admit an imported vocabulary or establish independence.'
   if formula is not None:disposition='encoded';roles=['constraint'];forms=['operational'] if sel==N and excerpt.startswith('A classification is orthogonal') else ['axiomatic-implicit']
   cid='COI-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel and (sel!=N or x['start_character']>0))
 uses=[('definition',N,'Exact source meaning and sibling identity are separate.'),('invariant',N,'Must-hold selected constraint differs from actual compliance or proof.'),('classification-axis',N,'Owned independently valued dimension and distinct purpose require exact sibling alignment.'),('typed-coupling-invariant',N,'Dependencies must be explicit before governing work; static representation does not prove temporal ordering.'),('typed-relation',N,'Ordered coupling vector and independent owner/evidence/effect are interpreted meanings.'),('relation-kind',N,'Meaning/direction of dependent classification bridge requires exact Kind.'),('schema','/boundaries/0','Schema rules are declared bridges, not automatic authority or identity equivalence.'),('projection-specification',N,'Convenience labels are generated, not new canonical truths.'),('root-axis-independence-invariant',N,'Changing one axis must not silently advance another authority axis.'),('governance-axis-independence-invariant','/scope/applicability','Maturity/confidence/evidence/provenance/owner are separate governance dimensions.'),('residue-measurement','/boundaries/0','Shannon-style classification evidence and Hilbert-style machinery require distinct registers and explicit bridge/residue.'),('evidence',F,'Statistical/retrieval measurements are optional evidence, not whole independence or truth.'),('authority','/scope/applicability','Admission/authority posture cannot be inferred from classification alone.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':res,'definedness_policy':None} for n,(args,res) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required={'CanonicalAxis':witness(CANONICAL),'DistinctCanonicalAxes':witness(quant('exists','Axis','z',both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(var('a'),var('z'))))))}
 populations=[{'population_id':'POP-'+n,'carrier':'Axis','predicate_ref':n if n in SIGNATURE else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Hypothetical distinct canonical axes make the independence/purpose comparison non-vacuous; no live axes or admission created.','review_ref':None} for n,statement in required.items()]
 for n,args in SIGNATURE.items():
  if n in required:continue
  populations.append({'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Specific dependent/label/measurement/review/outcome populations need scope/existence or exemption review; no live population invented.','review_ref':None})
 core={'interpretation_id':'interpretation:classification-orthogonality-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:classification-axis-purpose-and-bridge-candidate'}
 descriptions=[('COI-PRECEDENCE-001','Formal-expression unique-distinction OR every-dependency-recorded may permit an unrecorded dependency; candidate keeps target-specific normative dependency obligation. Boundary schema-rule/residue alternatives need compatible reviewed semantics.'),('COI-PURPOSE-002','Distinct semantic purpose in selected scope needs common Purpose map and review; different question strings, Kind IDs or nominal scopes are not proof of meaning distinction.'),('COI-STATISTICS-003','Optional mutual-information/entropy/retrieval evidence is not proof of operational independence; known no-data and unknown availability are separate.'),('COI-MATH-004','Classification independence and Hilbert projector orthogonality/contextuality are different formal objects; no equivalence or bridge from a shared word.'),('COI-FRAME-005','Exact allowed-state/frame/bridge bindings and before-downstream ordering require review; finite frames are not live or unbounded temporal compliance.'),('COI-IDENTITY-006','Shared CAV2-D22 source with Classification Axis does not merge target identities, invariant carrier or owner purpose; normalized classification and imported house_project vocabularies remain scoped.'),('COI-CLOSURE-007','Thirteen authored uses, required populations, complete dependency denominator and jointly aligned meanings remain pending.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with classification/axis/coupling/authority/schema/projection/measurement owners'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Thirteen authored uses lack independent completeness and exact cross-definition maps.','Operational independence and statistical/Hilbert registers have no reviewed semantic bridge.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'distinct-maturity-and-evidence-axis','scenario':'A maturity change leaves evidence confidence unchanged unless a separately explicit ordered bridge is selected.','expected_interpretation':'Distinct owned purposes and no silent co-change; a convenience label is generated; no promotion or statistics inferred.','rationale':'Independent dimensions may interact through explicit reviewed representations.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'unique-question-with-unrecorded-dependent-axis','scenario':'A new axis has a different printed question but relies on another axis without a typed representative.','expected_interpretation':'Distinct words do not prove unique meaning; dependence still needs explicit representation under this candidate normative precedence.','rationale':'The inherited OR branch cannot silently bypass the target-specific obligation.','related_clause_ids':encoded}],'known_losses':['No reviewed semantic-purpose uniqueness or full source precedence decision.','No temporal before-downstream or actual frame compliance proof.','No Shannon/Hilbert bridge or empirical independence theorem.','No complete dependency closure, imported taxonomy adoption, normalized invariant carrier or owner fidelity.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[{'query_id':'canonical-axis-not-'+n,'target':every(implies(CANONICAL,pred(n,'a'))),'witness_condition':witness(both(CANONICAL,neg(pred(n,'a')))),'selected_in_T':False} for n in OUTCOMES]
 queries.append({'query_id':'distinct-purpose-not-distinct-owner','target':axes(implies(both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(fn('axisPurpose','a'),fn('axisPurpose','z')))),neg(eq(fn('axisOwner','a'),fn('axisOwner','z'))))),'witness_condition':witness(quant('exists','Axis','z',both(CANONICAL,pred('CanonicalAxis','z'),neg(eq(fn('axisPurpose','a'),fn('axisPurpose','z'))),eq(fn('axisOwner','a'),fn('axisOwner','z'))))),'selected_in_T':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
