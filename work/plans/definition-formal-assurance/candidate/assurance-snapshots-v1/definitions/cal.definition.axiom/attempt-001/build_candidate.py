"""Author exact Axiom clause splits and a typed static candidate; no described proposition is adopted."""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:axiom-static-v1'
SORTS=['Proposition','SystemContext','DownstreamItem']
SIGNATURE={'Axiom':['Proposition','SystemContext'],'Foundational':['Proposition'],'TakenAsGiven':['Proposition','SystemContext'],'InternallyDerived':['Proposition','SystemContext'],'HeldTrue':['Proposition','SystemContext'],'WorldDomainSubject':['Proposition'],'SystemBehaviorConstraint':['Proposition','SystemContext'],'LowVeracityBet':['Proposition','SystemContext'],'Grounds':['Proposition','DownstreamItem','SystemContext'],'PremiseItem':['DownstreamItem'],'InvariantItem':['DownstreamItem'],'ConstitutionRuleItem':['DownstreamItem'],'AxiomSelfEnforces':['Proposition','SystemContext'],'ItemSelfEnforces':['DownstreamItem','SystemContext'],'ActualWorldTruth':['Proposition']}
def var(name):return {'op':'var','name':name}
def pred(name,*args):return {'op':'pred','name':name,'args':[var(x) for x in args]}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(sort,name,body):return quant('forall',sort,name,body)
def exists(sort,name,body):return quant('exists',sort,name,body)
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(arg):return {'op':'not','arg':arg}
def implication(left,right):return {'op':'implies','left':left,'right':right}
def axiom_requires(body):return every('Proposition','p',every('SystemContext','s',implication(pred('Axiom','p','s'),body)))
def allowed(item):return either(pred('PremiseItem',item),pred('InvariantItem',item),pred('ConstitutionRuleItem',item))
def family():
 pair=exists('DownstreamItem','i',exists('DownstreamItem','j',both(neg({'op':'eq','left':var('i'),'right':var('j')}),pred('Grounds','p','i','s'),pred('Grounds','p','j','s'),allowed('i'),allowed('j'))))
 return both(pair,every('DownstreamItem','k',implication(pred('Grounds','p','k','s'),allowed('k'))))
BASIC=axiom_requires(both(pred('Foundational','p'),pred('TakenAsGiven','p','s'),neg(pred('InternallyDerived','p','s')),pred('HeldTrue','p','s'),family()))
SUBJECT=axiom_requires(both(pred('WorldDomainSubject','p'),neg(pred('SystemBehaviorConstraint','p','s'))))
BET=axiom_requires(both(pred('HeldTrue','p','s'),neg(pred('LowVeracityBet','p','s'))))
NO_SELF=both(axiom_requires(neg(pred('AxiomSelfEnforces','p','s'))),every('DownstreamItem','i',every('SystemContext','s',implication(pred('InvariantItem','i'),neg(pred('ItemSelfEnforces','i','s'))))))
FAMILY=axiom_requires(family())

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(name,value):
 path=UNIT/name
 with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 return ref(path)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def source_ref(snap,identity):return {k:next(row for row in snap['current_entries'] if row['definition_id']==identity)[k] for k in ['definition_id','version_ref','path','sha256']}
def split_specs(text,markers):
 offsets=[0]+[text.index(marker) for marker in markers]+[len(text)]
 if sorted(set(offsets))!=offsets:raise ValueError('Nonunique or unordered reviewed source splits')
 return list(zip(offsets,offsets[1:]))
def main():
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:
  if ref(ROOT/row['path'])!=row:raise ValueError('Changed context input')
 snap=snapshot();r.verify(snap,ROOT);src=source_ref(snap,'cal.definition.axiom');doc=co.source_document(snap,src);units=co.inventory(doc);texts=dict(co.string_leaves(doc));clauses=[];links=[];views=[]
 N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';B='/boundaries/0';BC='/voices/scientific_formal/boundary_conditions/0';A='/scope/applicability'
 specs={}
 specs[N]=list(zip(split_specs(texts[N],['An axiom is a **foundational','such that revising','Its defining\nsubject']),[
  (None,'deferred',['proof-obligation'],['non-definitional'],'Normalization record, classification, owner and source-preservation obligations refer to the Definition artifact, not an adopted proposition.'),
  (BASIC,'encoded',['definition'],['axiomatic-implicit'],'Necessary static conditions on a proposition classified as an axiom in an explicit system context. At least two distinct permitted downstream items is a candidate reading of family and the explicit single-item exclusion.'),
  (None,'deferred',['proof-obligation'],['operational'],'Revising a proposition and forcing reconsideration of everything built on it needs explicit change, transitive dependency and obligation semantics; no proxy Boolean is substituted.'),
  (SUBJECT,'encoded',['definition'],['axiomatic-implicit'],'World/domain subject and exclusion of a system behavior constraint are static context predicates. They do not verify actual-world truth or counterfactual system influence.')]))
 for selector in [B,BC]:
  specs[selector]=list(zip(split_specs(texts[selector],['It is **not** a premise:','It is **not** a constitution','It is **not** a definition','An axiom and the invariants','A constitution authorizes']),[
   (SUBJECT,'encoded',['definition'],['axiomatic-implicit'],'Static subject distinction; no imported full Invariant equivalence or non-collapse theorem.'),
   (BET,'encoded',['definition'],['axiomatic-implicit'],'Held-true posture excludes a low-veracity bet in this selected context; canonical Premise lifecycle and promotion remain separate.'),
   (None,'deferred',['proof-obligation'],['non-definitional'],'An Axiom proposition and an authoritative scoped Constitution artifact require explicit cross-carrier relationship and adoption semantics.'),
   (None,'deferred',['proof-obligation'],['non-definitional'],'Assigning meaning is a Definition-artifact operation; no mere nominal sort partition is used to prove semantic distinction.'),
   (NO_SELF,'encoded',['definition'],['axiomatic-implicit'],'No self-enforcement by the Axiom proposition or the selected InvariantItem proxy; this is a classification constraint, not a theorem about real executors.'),
   (None,'deferred',['proof-obligation'],['operational'],'Constitution authorization, selected validators and actual enforcement need exact owner versions, selectors and effect semantics.')]))
 # Keep the formal display's prose, code delimiters and ordering fully accounted.
 specs[F]=list(zip(split_specs(texts[F],['subject(A) =','system can violate','genesis:','justification:','```\n\nThe **fan-out**']),[
  (BASIC,'encoded',['definition'],['axiomatic-implicit'],'Display restates given/underived/high-posture and permitted fan-out; it does not insert the represented proposition into the theory.'),
  (SUBJECT,'encoded',['definition'],['axiomatic-implicit'],'Explicit static world/domain subject projection.'),
  (None,'deferred',['proof-obligation'],['non-definitional'],'System-can-violate and wrong-premise/not-code-bug are modal, causal and explanatory boundaries; static profile cannot establish them.'),
  (None,'explanatory',['explanation-example'],['non-definitional'],'Discovery direction explains asking why an invariant holds; it is not a rule adopting its conclusion.'),
  (None,'deferred',['proof-obligation'],['operational'],'Actual axiom-to-invariant-to-constitution justification requires canonical downstream meaning and governed adoption, beyond primitive item tags.'),
  (FAMILY,'encoded',['definition'],['axiomatic-implicit'],'Explicitly excludes zero or one downstream item. Distinct item identity is required; duplicate tags or repeated references cannot supply a second consequence.')]))
 specs[A]=list(zip(split_specs(texts[A],['(1) can the system','(2) Is','(3) Does']),[
  (None,'explanatory',['explanation-example'],['non-definitional'],'Applicability introduction gives intuition and terminology for the static conditions.'),
  (None,'deferred',['proof-obligation'],['non-definitional'],'Counterfactual ability of the system to make the proposition false requires a specified causal/modal model.'),
  (BET,'encoded',['definition'],['axiomatic-implicit'],'Believed-true versus bet remains a commitment posture, independent of objective world truth.'),
  (axiom_requires(exists('DownstreamItem','i',pred('Grounds','p','i','s'))),'encoded',['definition'],['axiomatic-implicit'],'The applicability test rules out an inert proposition. It alone does not settle how many downstream kinds are required.')]))
 for unit in units:
  selector=unit['selector'];text=texts[selector]
  segments=specs.get(selector)
  if segments is None:
   meta=selector.startswith('/scope/') or selector=='/claim_ceiling' or selector.startswith('/voices/scientific_formal/testable_conditions/')
   disposition='deferred' if meta else 'explanatory';roles=['proof-obligation'] if meta else ['explanation-example']
   rationale='Record/provenance/admission or source-validation obligation remains separate from proposition semantics.' if meta else 'Non-normative explanation, scenario, notation or projection metadata; no proposition is selected as a premise.'
   segments=[((0,len(text)),(None,disposition,roles,['non-definitional'],rationale))]
  for (start,end),(formula,disposition,roles,forms,rationale) in segments:
   identity='AXI-'+str(len(clauses)+1).zfill(3);excerpt=text[start:end];clause={'clause_id':identity,'source_selector':selector,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale};clauses.append(clause);links.append({'unit_id':unit['unit_id'],'clause_id':identity,'end_character':end,'excerpt':excerpt});views.append({'clause_id':identity,'source_selector':selector,'start_character':start,'end_character':end,'disposition':disposition,'rationale':rationale})
 declarations=[{'kind':'sort','symbol_id':name,'scope':SCOPE,'domain_policy':'nonempty'} for name in SORTS]+[{'kind':'predicate' if len(args)<2 else 'relation','symbol_id':name,'scope':SCOPE,'argument_sorts':args} for name,args in SIGNATURE.items()]
 dependencies=[source_ref(snap,id) for id in ['cal.definition.premise','cal.definition.invariant','cal.definition.constitution','cal.definition.definition']]
 dependency_links=[]
 for dependency,marker in zip(dependencies,['It is **not** a premise:','An axiom is **not** an invariant','It is **not** a constitution','It is **not** a definition']):
  clause=next(row for row in links if row['excerpt'].startswith(marker));dependency_links.append({'clause_id':clause['clause_id'],'dependency_ref':dependency,'kind':'semantic-use','rationale':'Author-declared comparison uses this exact sibling meaning; primitive proxies do not import its full interpretation. Joint closure and cross-carrier coupling remain pending.'})
 population=exists('Proposition','p',exists('SystemContext','s',pred('Axiom','p','s')))
 core={'interpretation_id':'interpretation:axiom-static-v1','source':src,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':dependencies,'relations':[],'assumptions':[],'populations':[{'population_id':'POP-AXIOM-HYPOTHETICAL','carrier':'Proposition','predicate_ref':None,'requirement':'required','statement':population,'scope':SCOPE,'rationale':'At least one hypothetical classified proposition/context is required to avoid empty-class vacuity. No real axiom or actual-world truth is asserted.','review_ref':None}],'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:static-first-order-candidate'}
 conflicts=[{'finding_id':'AXI-FAMILY-001','selectors':[N,F,A],'description':'At least two distinct consequences follows the explicit single-item exclusion; whether all three downstream kinds must occur is not fixed. Candidate uses two from permitted kinds, pending owner interpretation.','status':'unresolved','owner_route':'role:definition-owner must choose family cardinality/kind coverage against exact source bytes.'},{'finding_id':'AXI-TRUTH-002','selectors':[N,F,'/voices/plain_language/explanation'],'description':'Held true, high commitment/veracity and external truth must not be conflated. Candidate encodes descriptive belief posture and leaves ActualWorldTruth unconstrained; it neither adopts nor proves any represented proposition.','status':'unresolved','owner_route':'role:definition-owner must confirm posture-versus-world-truth interpretation and any external truth assumptions.'},{'finding_id':'AXI-LAYER-003','selectors':[N,'/claim_ceiling'],'description':'Normalization/canonical-record obligations refer to the Definition artifact while target meaning concerns propositions. Source internal candidate posture and Lab registry provenance are preserved without equating layers.','status':'unresolved','owner_route':'role:definition-owner must confirm layer separation and reconcile canonical source posture in a versioned decision.'},{'finding_id':'AXI-DYNAMICS-004','selectors':[N,F,A],'description':'Revision impact, causal non-violation and governed enforcement have no sound static-only substitute. Corresponding clauses remain deferred for specialized semantics.','status':'unresolved','owner_route':'role:definition-owner and formalization implementer must select exact change/modal/deontic contracts and future proof profile.'}]
 case_clauses=[row['clause_id'] for row in clauses if row['formal_statement'] is not None]
 instances=[{'case_id':'creative-demand-foundation','scenario':'In a hypothetical creative-campaign planning context, a team holds the proposition about uneven creative outcomes as a foundational given, derives two distinct design consequences, and does not treat it as a software behavior constraint or a low-veracity bet.','expected_interpretation':'Can satisfy the selected static necessary conditions. Actual statistical truth, derivation correctness, source fidelity and whether both consequences form a sufficient family require separate evidence.','rationale':'Uses source plain-language intuition without making an empirical claim or adopting the proposition in this formal theory.','related_clause_ids':case_clauses}]
 counterexamples=[{'case_id':'one-restated-invariant','scenario':'A proposition has high commitment but grounds only one system invariant, referenced twice under different tags.','expected_interpretation':'Fails the distinct-two-item fan-out constraint; duplicate references do not make a family.','rationale':'Exercises the explicit formal-display exclusion of a restatement of one invariant.','related_clause_ids':case_clauses},{'case_id':'working-bet','scenario':'The team adopts a low-veracity working bet to proceed and labels it an axiom.','expected_interpretation':'Fails the selected Axiom belief-posture constraint; canonical Premise meaning and lifecycle are not silently merged.','rationale':'Separates working adoption, belief posture and external truth.','related_clause_ids':case_clauses},{'case_id':'behavior-rule','scenario':'A rule requires every transaction to preserve an identifier and can be violated by buggy code. It is labelled an axiom.','expected_interpretation':'Fails the static non-system-behavior subject condition; actual invariance and causal failure need their own semantics.','rationale':'Prevents a system must-hold from becoming a world-domain proposition through its label.','related_clause_ids':case_clauses}]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dependency_links,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Four exact direct semantic comparison dependencies authored; their full interpretations/transitive dependencies are not imported or closed.','Primitive downstream item kinds and belief/subject predicates need independent denotation and owner agreement; no identity map to sibling classifiers is asserted.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':conflicts,'review_ref':None},'review_packet':{'instances':instances,'counterexamples':counterexamples,'known_losses':['Static necessary-condition projection, not a complete biconditional classifier or whole-source translation.','Modal/causal non-violation, temporal revision impact, governed enforcement and Definition-record obligations remain deferred.','Primitive grounding tags do not prove real derivations or instantiate canonical Premise/Invariant/Constitution/Definition semantics.','No proposition described by an Axiom is inserted into selected assumptions or asserted objectively true.'],'review_status':'pending','review_ref':None}}
 report=co.check(packet,snap,required_dependencies=[dep['version_ref'] for dep in dependencies],required_conflicts=[row['finding_id'] for row in conflicts])
 if not report.get('character_accounting_complete') or report['status']!='correspondence-pending':raise ValueError(json.dumps(report))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 put('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core});put('correspondence.json',packet);put('static-ir.json',typed);put('correspondence-check.json',report);put('clause-analysis.json',{'authority_effect':'none','source':src,'source_units':len(units),'clauses':views,'findings':conflicts,'whole_definition_translation':'pending','owner_fidelity':'pending','selected_proposition_assumptions':0})
 print(json.dumps({'result':'candidate-authored-and-typed','source_units':len(units),'mapped_clauses':len(clauses),'encoded_clauses':sum(row['formal_statement'] is not None for row in clauses),'deferred_clauses':len(report['unresolved_clauses']),'direct_semantic_dependencies':len(dependencies),'selected_assumptions':0,'whole_translation':'pending','semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
