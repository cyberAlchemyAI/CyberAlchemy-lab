"""Contestability Policy normalized axes, review fields and sibling confidence/residue boundaries."""
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
SCOPE='scope:candidate:ContestabilityPolicy-normalized-review-surface-fields-and-confidence-residue-boundaries-v1'
SORTS=['Entity','Field','Token']
FIELDS=['challenge_response','valid_challenge_modes','contradiction_edges','validation_edges','owner_route','resolution_gate','blocking_questions','challenge_residue_route']
OPTIONAL={'contradiction_edges':'ContradictionLinksPresent','validation_edges':'ValidationLinksPresent'}
CONSTANTS={'EMPTY':'Token','CP_ID':'Token',**{'F_'+n:'Field' for n in FIELDS}}
FUNCTIONS={'fieldValue':(['Entity','Field'],'Token'),'normalizedIdValue':(['Entity'],'Token'),'evidenceConfidenceValue':(['Entity'],'Token'),'commitmentConfidenceValue':(['Entity'],'Token')}
QUALIFIERS=['ExplicitReviewSurface','AttachedToGovernedObject','DescribesChallengePathsWithoutSilentMeaningOrConfidenceChange']
ROLES=['VerdictRole','ConfidenceScoreRole','ProofOfTruthRole','PromotionDecisionRole','OntologyOwnerOverrideRole']
OUTCOMES=['ActualAuthority','ActualAdmission','TruthEstablished','ProofEstablished','SourceOwnerAccepted','RuntimeActivated','ExternalEffect','ActualOwnerResolution','ActualConfidenceChange']
SIGNATURE={n:['Entity'] for n in ['ContestabilityPolicy',*QUALIFIERS,*ROLES,*OUTCOMES,'CanonicalInstance','NormalizedPolicyKind','SharedAuthorityScope','PolicyCarrier','PreservesExactD40Relation','SilentSiblingIdentityMerge','ContainsOwnConfidence','ContainsOwnResidue','IntroducesThirdConfidenceAxis','RawDeclaredComplete',*OPTIONAL.values(),'SubjectConfidenceSibling','SubjectResidueSibling','UnresolvedChallengeResidue','ActualResidueRetained','OwnerReviewClosed','OwnerReviewWaived','OwnerReviewDemoted','ActualPromotion']}
SIGNATURE.update(DeclaresField=['Entity','Field'],AttachedSubject=['Entity','Entity'],FiledChallenge=['Entity','Entity'],QualifiedOwnerResolution=['Entity','Entity'])
CP=pred('ContestabilityPolicy','p')
def field(n,p='p'):return fn('fieldValue',p,const('F_'+n))
def listed(f):return either(*[eq(f,const('F_'+n)) for n in FIELDS])
NORMALIZED=allof([('Entity','p')],implies(CP,both(pred('NormalizedPolicyKind','p'),pred('SharedAuthorityScope','p'),pred('PolicyCarrier','p'),eq(fn('normalizedIdValue','p'),const('CP_ID')))))
CANONICAL=allof([('Entity','p')],implies(pred('CanonicalInstance','p'),both(CP,pred('PreservesExactD40Relation','p'),neg(pred('SilentSiblingIdentityMerge','p')))))
GENUS=allof([('Entity','p')],{'op':'iff','left':CP,'right':both(*[pred(n,'p') for n in QUALIFIERS])})
DECLARATION=allof([('Entity','p')],implies(CP,allof([('Field','f')],implies(listed(var('f')),pred('DeclaresField','p','f')))))
VALUES=allof([('Entity','p')],implies(CP,both(*[neg(eq(field(n),const('EMPTY'))) if n not in OPTIONAL else implies(pred(OPTIONAL[n],'p'),neg(eq(field(n),const('EMPTY')))) for n in FIELDS])))
EXCLUSION=allof([('Entity','p')],implies(CP,both(*[neg(pred(n,'p')) for n in ['ContainsOwnConfidence','ContainsOwnResidue','IntroducesThirdConfidenceAxis']])))
NONCOLLAPSE=allof([('Entity','p')],implies(CP,both(*[neg(pred(n,'p')) for n in ROLES])))
THEORY=[NORMALIZED,CANONICAL,GENUS,DECLARATION,VALUES,EXCLUSION,NONCOLLAPSE]
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=source_ref(snap,'cal.definition.contestability-policy');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
 header=texts[N].split('\n\n')[0]
 genus='A challenge contract is the explicit review surface attached to a\nCyberAlchemy v2 node, candidate, claim, or authority artifact that states how\nthe object may be challenged, contradicted, validated, blocked, or routed for\nowner review without silently changing its meaning or confidence.'
 declaration='A challenge contract must declare the valid challenge response, admissible\nchallenge modes, contradiction and validation links when present, owner route,\nresolution gate, blocking questions, and challenge residue route.'
 exclusion="It does not\ncontain the object's own confidence or residue and does not introduce a third\nconfidence axis."
 tuple_text='ChallengeContract =\n  (challenge_response, valid_challenge_modes, contradiction_edges,\n   validation_edges, owner_route, resolution_gate, blocking_questions,\n   challenge_residue_route)'
 selected=[(N,header,both(NORMALIZED,CANONICAL),['axiomatic-implicit']),(N,genus,GENUS,['genus-differentia']),(N,declaration,both(DECLARATION,VALUES),['axiomatic-implicit','operational']),(N,exclusion,EXCLUSION,['axiomatic-implicit']),(F,tuple_text,DECLARATION,['axiomatic-implicit']),(F,"The object's own confidence and residue are not part of the challenge\ncontract.",EXCLUSION,['axiomatic-implicit'])]+[(sel,texts[sel].split(' It names')[0],NONCOLLAPSE,['axiomatic-implicit']) for sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0']]
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];cuts={0,len(text)}
  for selector,excerpt,_,_ in selected:
   if selector==sel:start=text.index(excerpt);cuts.update([start,start+len(excerpt)])
  points=sorted(cuts)
  for start,end in zip(points,points[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Accepted normalized Policy/Definition/carrier and ChallengeContract identity,field/link presence,confidence/residue/owner/action and temporal trace semantics remain unresolved.'
   for selector,chosen,statement,selected_forms in selected:
    if sel==selector and excerpt==chosen:formula=statement;disposition='encoded';forms=selected_forms;roles=['definition'];why='Candidate source characterization: separate normalized identity axes,review-surface genus,eight declared fields,six unconditional/two conditional nonempty values,sibling confidence/residue exclusion and five-role noncollapse. No actual reference resolution or owner outcome.'
   if formula is None and (sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/')):disposition='explanatory';roles=['explanation-example'];why='Historical source context and named confidence axes stay explanatory; no import of actual node policy or evidence/commitment semantics.'
   cid='CP-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 names=['definition','challenge-contract','challenge-event','policy','ontology','ontology-node','ontology-edge','ontology-view','projection-specification','constitution','authority','authority-claim','authority-boundary','authority-surface','authority-promotion','decision','decision-scope','gate','evidence','evidence-set','residue','residue-escalation-method','residue-measurement','identity-carrier','identity-relation','typed-relation','relation-kind','classification','classification-scheme','classification-orthogonality-invariant','context','validation','validation-receipt','semantic-event-history','governance-event-history','canonical-representation-invariant']
 deps=[source_ref(snap,'cal.definition.'+n) for n in names];target=next(x['clause_id'] for x in clauses if x['formal_statement']==GENUS);dl=[{'clause_id':target,'dependency_ref':dep,'kind':'semantic-use','rationale':'Exact authored use for '+name+' requires independent denotation/owner/scope review; no alias or carrier equivalence follows.'} for name,dep in zip(names,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required={'ContestabilityPolicy':exists([('Entity','p')],CP),'RawDeclaredWithoutPolicy':exists([('Entity','p')],both(pred('RawDeclaredComplete','p'),neg(CP))),'DistinctSameFieldPolicies':exists([('Entity','p'),('Entity','q')],both(CP,pred('ContestabilityPolicy','q'),neg(eq(var('p'),var('q'))),allof([('Field','f')],eq(fn('fieldValue','p','f'),fn('fieldValue','q','f'))))),
 'NoLinksEmptyOptionalValues':exists([('Entity','p')],both(CP,*[both(neg(pred(flag,'p')),eq(field(n),const('EMPTY'))) for n,flag in OPTIONAL.items()])),
 'PresentLinksNonemptyValues':exists([('Entity','p')],both(CP,*[both(pred(flag,'p'),neg(eq(field(n),const('EMPTY')))) for n,flag in OPTIONAL.items()])),
 'SubjectConfidenceSeparate':exists([('Entity','p'),('Entity','s')],both(CP,pred('AttachedSubject','p','s'),pred('SubjectConfidenceSibling','s'),neg(eq(fn('evidenceConfidenceValue','s'),const('EMPTY'))),neg(eq(fn('commitmentConfidenceValue','s'),const('EMPTY'))))),
 'SubjectOwnResidueSeparate':exists([('Entity','p'),('Entity','s')],both(CP,pred('AttachedSubject','p','s'),pred('SubjectResidueSibling','s'))),
 'FiledWithoutAutomaticPromotion':exists([('Entity','e'),('Entity','p')],both(CP,pred('FiledChallenge','e','p'),neg(pred('ActualPromotion','p')))),
 'UnresolvedRetainedWithoutResolution':exists([('Entity','p')],both(CP,pred('UnresolvedChallengeResidue','p'),pred('ActualResidueRetained','p'),*[neg(pred(n,'p')) for n in ['OwnerReviewClosed','OwnerReviewWaived','OwnerReviewDemoted']])),
 'UnresolvedNotActuallyRetainedGap':exists([('Entity','p')],both(CP,pred('UnresolvedChallengeResidue','p'),neg(pred('ActualResidueRetained','p')))),
 'CanonicalExactSourcePreserved':exists([('Entity','p')],both(CP,pred('CanonicalInstance','p'),pred('PreservesExactD40Relation','p')))}
 populations=[{'population_id':'POP-'+n,'carrier':'Entity','predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Supplied static candidate nonvacuity or limitation witness; no actual policy,review,confidence change or residue handling established.','review_ref':None} for n,statement in required.items()]
 populations += [{'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Real population and accepted field/owner/identity/action/trace denotation remain pending.','review_ref':None} for n,args in SIGNATURE.items() if n not in required]
 core={'interpretation_id':'interpretation:ContestabilityPolicy-review-surface-normalized-axes-and-sibling-boundaries-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:ContestabilityPolicy-hypothetical-reviewed-surface-and-confidence-residue-frame-v1'}
 descriptions=['Source normalized Policy header and older ChallengeContract basis need accepted precedence; current independent ChallengeContract identity is not an alias closure.','Eight declared fields and six unconditional/two conditional nonempty Tokens lack accepted structured response/mode/link/gate/route semantics.','Normalized identity,scope,carrier and preserved D40 relations need mappings independent of printed labels and current generic Definition/Policy shape.','Genus and attachment markers do not establish actual object eligibility,challenge grounds,filing,review or outcome.','Sibling evidence/commitment confidence and object residue do not belong to contract; third-axis prohibition requires a typed actual-field map.','Unresolved challenge residue must remain attached until qualified owner closure/waiver/demotion; full temporal semantics and actual enforcement are deferred,not lowered into a factual static predicate.','Verdict,score,truth proof,promotion Decision and ontology override roles remain distinct with actual owner/gate movement unresolved.','All semantic uses,shared meaning and source-owner fidelity remain independently reviewable; no universal or actual authority proof.']
 findings=[{'finding_id':'CP-FINDING-'+str(i+1).zfill(3),'selectors':[N,F,'/scope/applicability'],'description':why,'status':'unresolved','owner_route':'role:definition-owner with Policy,ChallengeContract,confidence,residue and temporal owner-review owners'} for i,why in enumerate(descriptions)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['36 authored uses require independent shared-meaning review.','Static candidate does not implement temporal residue retention,owner review,confidence frame or generic carrier equivalence.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'review-surface-field-and-sibling-boundaries','scenario':'A supplied canonical review surface declares eight fields and leaves object confidence/residue separate.','expected_interpretation':'Candidate characterization without actual owner review,outcome or temporal preservation.','rationale':'Source definition and real behavior have different claim strength.','related_clause_ids':[target]}],'counterexamples':[{'case_id':'route-record-mistaken-for-identity-or-resolution','scenario':'A raw route or field record is mistaken for qualified policy identity or a real residue resolution.','expected_interpretation':'Separate genus,identity,owner/gate and history maps need evidence.','rationale':'No actual review or closure follows from record shape.','related_clause_ids':[target]}],'known_losses':descriptions,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError('Incomplete/malformed correspondence '+json.dumps(account))
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':sum(x['disposition']=='encoded' for x in clauses),'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'source_precedence_reviewed':False,'mechanized_proof':False,'known_losses':descriptions})
 queries=[]
 def q(id,target,witness):queries.append({'query_id':id,'target':target,'witness_condition':witness,'selected_in_T':False,'source_fidelity':'pending'})
 for n in OUTCOMES+['ActualPromotion']:q('review-surface-does-not-entail-'+n,allof([('Entity','p')],implies(CP,pred(n,'p'))),required['ContestabilityPolicy'])
 q('raw-fields-not-qualified-policy',allof([('Entity','p')],implies(pred('RawDeclaredComplete','p'),CP)),required['RawDeclaredWithoutPolicy'])
 q('same-fields-not-policy-identity',allof([('Entity','p'),('Entity','q')],implies(both(CP,pred('ContestabilityPolicy','q'),allof([('Field','f')],eq(fn('fieldValue','p','f'),fn('fieldValue','q','f')))),eq(var('p'),var('q')))),required['DistinctSameFieldPolicies'])
 q('static-definition-not-universal-actual-residue-retention',allof([('Entity','p')],implies(both(CP,pred('UnresolvedChallengeResidue','p')),pred('ActualResidueRetained','p'))),required['UnresolvedNotActuallyRetainedGap'])
 put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':len(required),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 comparative=[source_ref(snap,'cal.definition.'+n) for n in ['definition','challenge-contract','challenge-event','policy','ontology-node','residue','constitution','authority-promotion']]
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comparative,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comparative]+[ref(BASE/'definitions/cal.definition.constitution'/n) for n in ['t.json','static-ir.json','REVIEW.md','delivery-manifest.json']],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':[],'source_fidelity':'pending','claim_ceiling':'Exact independent identities and selected D40/D23 context. No ChallengeContract alias,Policy carrier,confidence/residue closure or owner authority imported.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
