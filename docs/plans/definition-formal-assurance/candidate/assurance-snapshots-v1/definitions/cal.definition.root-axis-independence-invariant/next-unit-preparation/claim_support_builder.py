"""Typed domain-interpreted claim/support bounds and declared remediation;actual truth/authority stay separate."""
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
SCOPE='scope:candidate:claim-support-domain-bounds-remediation-v1'
SORTS=['Invariant','Claim','ClaimType','Context','Interpreter','SupportPackage','SupportItem','Strength','Token']
CONSTANTS={n:'Token' for n in ['EMPTY','MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D38']}
FUNCTIONS={n:(['Invariant'],'Token') for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource']}
DIMENSIONS=['Asserted','AuthorityEffect','ValidationStatus','PublicationPosture']
FUNCTIONS.update(claimInvariant=(['Claim'],'Invariant'),claimType=(['Claim'],'ClaimType'),claimContext=(['Claim'],'Context'),claimInterpreter=(['Claim'],'Interpreter'),claimPackage=(['Claim'],'SupportPackage'),claimHandle=(['Claim'],'Token'),claimTreatmentReference=(['Claim'],'Token'),interpreterType=(['Interpreter'],'ClaimType'),interpreterContext=(['Interpreter'],'Context'),interpreterHandle=(['Interpreter'],'Token'),packageType=(['SupportPackage'],'ClaimType'),packageContext=(['SupportPackage'],'Context'),packageInterpreter=(['SupportPackage'],'Interpreter'),packageHandle=(['SupportPackage'],'Token'),itemType=(['SupportItem'],'ClaimType'),itemContext=(['SupportItem'],'Context'),itemHandle=(['SupportItem'],'Token'))
FUNCTIONS.update({n:(['Claim'],'Strength') for n in ['claim'+d+'Strength' for d in DIMENSIONS]})
FUNCTIONS.update({n:(['SupportPackage'],'Strength') for n in ['package'+d+'Strength' for d in DIMENSIONS]})
ITEM_KINDS=['SourceCitationSupport','ValidationRunSupport','WitnessSupport','OwnerDecisionSupport','AcceptedPremiseSupport','FormalProofSupport']
INTERPRETER_KINDS=['DomainInterpreter','ValidatorInterpreter','ResearchStandardInterpreter','OwnerDecisionInterpreter','ConstitutionInterpreter']
TREATMENTS=['DowngradeDeclared','HypothesisWordingDeclared','CandidateWordingDeclared','ResidueFlagDeclared','GateRouteDeclared','GoverningBlockDeclared']
POSTURES=['PartialSupport','PrivateSupport','IndirectSupport','DisputedSupport','WeakerSupport']
INV_OUTCOMES=['Authority','Admission','Activation','ExternalEffect','Truth','OwnerFidelity','ConsumerAlignment']
CLAIM_OUTCOMES=['Truth','Authority','SupportAdequacy','Publication','Validation','GateClearance','GoverningAuthorization','RemediationExecuted','ConsumerAlignment','GlobalConsistency']
SIGNATURE={n:['Invariant'] for n in ['ClaimSupportInvariant','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge','FormalProofOnlyRole','MaximalCertaintyRequiredRole',*['InvariantActual'+n for n in INV_OUTCOMES]]}
SIGNATURE.update({n:['Claim'] for n in ['ClaimApplicable','WordingInScopeDeclared','ClaimTypeDeclared','ClaimHasSupport','ClaimCitesPackage','WithinDeclaredSupportBound','CompatibleClaim','HonestWordingDeclared','RiskyClaim',*TREATMENTS,*POSTURES,*['ClaimActual'+n for n in CLAIM_OUTCOMES]]})
SIGNATURE.update(ContextDeclared=['Context'],InterpreterDeclared=['Interpreter'],PackageDeclared=['SupportPackage'],**{n:['Interpreter'] for n in INTERPRETER_KINDS},**{n:['SupportItem'] for n in ITEM_KINDS},SupportItemIncluded=['SupportPackage','SupportItem'],AllowedStrength=['Interpreter','ClaimType','Strength','Strength'])
C=pred('ClaimSupportInvariant','v');A=pred('ClaimApplicable','c');PKG=fn('claimPackage','c');TYPE=fn('claimType','c');CTX=fn('claimContext','c');INT=fn('claimInterpreter','c');HAS=pred('ClaimHasSupport','c');BOUND=pred('WithinDeclaredSupportBound','c');RISK=pred('RiskyClaim','c');COMP=pred('CompatibleClaim','c')
NORMALIZED=allof([('Invariant','v')],{'op':'iff','left':C,'right':both(pred('ClassificationPreserved','v'),pred('SourceRelationsPreserved','v'),pred('NoSilentSiblingMerge','v'),*[eq(fn(n,'v'),const(k)) for n,k in zip(['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D38'])])})
GENUS=allof([('Claim','c')],{'op':'iff','left':A,'right':both(pred('WordingInScopeDeclared','c'),pred('ClaimTypeDeclared','c'))})
STRUCTURE=allof([('Claim','c')],implies(A,both(pred('ClaimSupportInvariant',fn('claimInvariant','c')),pred('ContextDeclared',CTX),pred('InterpreterDeclared',INT),eq(fn('interpreterType',INT),TYPE),eq(fn('interpreterContext',INT),CTX),either(*[pred(n,INT) for n in INTERPRETER_KINDS]),neg(eq(fn('interpreterHandle',INT),const('EMPTY'))),neg(eq(fn('claimHandle','c'),const('EMPTY'))))))
PRESENCE=allof([('Claim','c')],implies(A,{'op':'iff','left':HAS,'right':both(pred('ClaimCitesPackage','c'),pred('PackageDeclared',PKG))}))
SUPPORT=allof([('Claim','c')],implies(both(A,HAS),both(eq(fn('packageType',PKG),TYPE),eq(fn('packageContext',PKG),CTX),eq(fn('packageInterpreter',PKG),INT),neg(eq(fn('packageHandle',PKG),const('EMPTY'))),exists([('SupportItem','i')],pred('SupportItemIncluded',PKG,'i')))))
ITEMS=allof([('Claim','c'),('SupportItem','i')],implies(both(A,HAS,pred('SupportItemIncluded',PKG,'i')),both(eq(fn('itemType','i'),TYPE),eq(fn('itemContext','i'),CTX),neg(eq(fn('itemHandle','i'),const('EMPTY'))),either(*[pred(n,'i') for n in ITEM_KINDS]))))
COMPARISON=allof([('Claim','c')],implies(A,{'op':'iff','left':BOUND,'right':both(HAS,*[pred('AllowedStrength',INT,TYPE,fn('claim'+d+'Strength','c'),fn('package'+d+'Strength',PKG)) for d in DIMENSIONS])}))
COMPATIBILITY=allof([('Claim','c')],implies(A,{'op':'iff','left':COMP,'right':both(HAS,BOUND,pred('HonestWordingDeclared','c'))}))
RISK_RULE=allof([('Claim','c')],implies(A,{'op':'iff','left':RISK,'right':either(neg(HAS),*[pred(n,'c') for n in POSTURES],both(HAS,neg(BOUND)))}))
REMEDIATION=allof([('Claim','c')],implies(both(A,RISK),both(either(*[pred(n,'c') for n in TREATMENTS]),neg(eq(fn('claimTreatmentReference','c'),const('EMPTY'))))))
DEFAULT=allof([('Claim','c')],implies(both(A,neg(HAS)),either(pred('CandidateWordingDeclared','c'),pred('HypothesisWordingDeclared','c'))))
NONCOLLAPSE=allof([('Invariant','v')],implies(C,both(neg(pred('FormalProofOnlyRole','v')),neg(pred('MaximalCertaintyRequiredRole','v')))))
THEORY=[NORMALIZED,GENUS,STRUCTURE,PRESENCE,SUPPORT,ITEMS,COMPARISON,COMPATIBILITY,RISK_RULE,REMEDIATION,DEFAULT,NONCOLLAPSE]
def required_populations():
 out={'InvariantWitness':exists([('Invariant','v')],C),'InvariantWithoutActualOutcomes':exists([('Invariant','v')],both(C,*[neg(pred('InvariantActual'+n,'v')) for n in INV_OUTCOMES])),'CompatibleClaimWitness':exists([('Claim','c')],both(A,COMP)),'CompatibleClaimWithoutActualOutcomes':exists([('Claim','c')],both(A,COMP,*[neg(pred('ClaimActual'+n,'c')) for n in CLAIM_OUTCOMES])),'OutsideApplicableScope':exists([('Claim','c')],neg(A))}
 for n in ['Candidate','Hypothesis']:out['AbsentSupport'+n]=exists([('Claim','c')],both(A,neg(HAS),pred(n+'WordingDeclared','c')))
 for n in POSTURES:out[n+'Witness']=exists([('Claim','c')],both(A,HAS,RISK,pred(n,'c')))
 for n in TREATMENTS:out[n+'Witness']=exists([('Claim','c')],both(A,RISK,pred(n,'c')))
 for n in ITEM_KINDS:out[n+'Witness']=exists([('Claim','c'),('SupportItem','i')],both(A,HAS,pred('SupportItemIncluded',PKG,'i'),pred(n,'i')))
 for n in INTERPRETER_KINDS:out[n+'Witness']=exists([('Claim','c')],both(A,pred(n,INT)))
 return out
LOSSES=['Normalized D38 source lineage and invariant identity need source-owner precedence;neither legacy label nor reclassification grants equivalence.','Claim applicability,type,context and interpreter populations remain proposed;current carriers are separately qualified.','Strength is a domain-interpreted relation,not a numeric universal score,total order or automatically accepted epistemic ranking.','Asserted strength,authority effect,validation status and publication posture have distinct candidate maps;actual meanings need acceptance.','Cited declared package and included nonempty support references are presence/coherence guards,not evidence adequacy or truth.','Six support kinds need accepted source/item denotations;formal proof is not the only support and maximal certainty is not required.','Absent support defaults to candidate/hypothesis declarations;actual downgrade,wording change and governing permission remain independent.','Partial/private/indirect/disputed/weaker support triggers an explicit remediation alternative;these labels are not equivalent,exclusive or automatically adequate.','Declared gate route,residue or governing block does not prove gate clearance,remediation execution,publication or actual authority.','Exact C53/local D38 observations and finite witness/countermodels do not establish source-owner fidelity,consumer alignment,joint common denotations or whole-definition proof.']
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=source_ref(snap,'cal.definition.claim-support-compatibility-invariant');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';parts=texts[N].split('\n\n')
 chosen=[(N,parts[0],NORMALIZED,['genus-differentia','axiomatic-implicit']),(N,parts[2],both(GENUS,STRUCTURE,PRESENCE,SUPPORT,ITEMS,COMPARISON,COMPATIBILITY),['axiomatic-implicit']),(N,parts[3],both(RISK_RULE,REMEDIATION,DEFAULT),['axiomatic-implicit','operational']),(F,texts[F],both(COMPARISON,DEFAULT),['axiomatic-implicit']),('/scope/applicability',texts['/scope/applicability'],both(GENUS,STRUCTURE),['operational']),('/voices/scientific_formal/boundary_conditions/0',texts['/voices/scientific_formal/boundary_conditions/0'],NONCOLLAPSE,['axiomatic-implicit'])]
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];cuts={0,len(text)}
  for selector,excerpt,_,_ in chosen:
   if selector==sel:start=text.index(excerpt);cuts.update([start,start+len(excerpt)])
  for start,end in zip(sorted(cuts),sorted(cuts)[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Accepted claim/type/context/interpreter/strength/package/item/treatment and actual outcomes require separate owner review.'
   for selector,chosen_excerpt,statement,selected_forms in chosen:
    if sel==selector and excerpt==chosen_excerpt:formula=statement;disposition='encoded';forms=selected_forms;roles=['definition'];why='Typed declared support comparison and remediation guards;actual truth,authority,support adequacy,publication,validation and execution stay outside T.'
   if sel.startswith('/voices/scientific_formal/testable_conditions/') or sel=='/claim_ceiling':roles=['observation-measurement'];why='Artifact identity/source digest/schema/projection/historical-posture checks are separate observations,not actual epistemic or authority axioms.'
   if formula is None and (sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/')):disposition='explanatory';roles=['explanation-example'];why='Honest-wording intuition and retained source-domain examples do not establish truth,actual authority or source-role equivalence.'
   cid='CSI-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 deps=[source_ref(snap,'cal.definition.'+n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required=required_populations();populations=[{'population_id':'POP-'+n,'carrier':'Invariant' if n.startswith('Invariant') else 'Claim','predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Explicit compatible,risky,absent-support,plural support/interpreter and outside-scope witnesses;not an epistemic or operational proof.','review_ref':None} for n,z in required.items()]+[{'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual denotations and accepted population maps remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'interpretation_id':'interpretation:claim-support-domain-bounds-remediation-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:claim-support-domain-bounds-remediation-v1'}
 findings=[{'finding_id':'CSI-FINDING-'+str(i+1).zfill(3),'selectors':[N,F,'/scope/applicability'],'description':why,'status':'unresolved','owner_route':'role:definition-owner with claim,support,interpreter,gate and consumer owners'} for i,why in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Qualified claims,support kinds,interpreter,strength,remediation and consumer maps require independent acceptance.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'qualified-claim-support-and-remediation','scenario':'A cited support package may carry several evidence kinds;its domain-specific bound and honest wording do not establish truth or publication authority.','expected_interpretation':'Declared claim/support comparison with explicit remediation,not actual certainty or governing authorization.','rationale':'Support references and declared compatibility are not truth or actual authority.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'overclaim-from-command-success','scenario':'A successful validation command or named citation is treated as proof of truth,whole-system readiness or actual publication authority.','expected_interpretation':'Exact claimed dimensions require a declared support bound and weakness remediation;actual outcomes stay independent.','rationale':'The source allows plural support types and uncertainty while requiring honest wording relative to declared support.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete'],account
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=[]
 for prefix,sort,varname,guard,witness,names in [('Invariant','Invariant','v',C,required['InvariantWithoutActualOutcomes'],INV_OUTCOMES),('Claim','Claim','c',A,required['CompatibleClaimWithoutActualOutcomes'],CLAIM_OUTCOMES)]:
  for n in names:queries.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,varname)],implies(guard,pred(prefix+'Actual'+n,varname))),'witness_condition':witness,'selected_in_T':False,'source_fidelity':'pending'})
 put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});selector='/boundaries/0';excerpt=texts[selector];clause=next(x for x in clauses if x['source_selector']==selector);put('source-query-obligation.json',{'authority_effect':'none','obligations':[{'source':source,'selector':selector,'start_character':0,'end_character':len(excerpt),'excerpt':excerpt,'excerpt_sha256':r.digest(excerpt.encode()),'clause_id':clause['clause_id'],'query_id':'Claim-not-ActualTruth','selected_in_T':False}],'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':len(required),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'source_precedence_reviewed':False,'mechanized_proof':False,'actual_outcome_queries_assumed_in_T':False,'artifact_tests_are_observations':True,'strength_relation_is_numeric_or_total_order_assumed':False,'all_support_is_formal_proof_assumed':False,'maximal_certainty_required':False,'treatment_declaration_proves_execution':False,'support_or_interpreter_kind_exclusivity_assumed':False})
 comp=[source_ref(snap,'cal.definition.'+n) for n in ['definition','invariant','provenance','evidence','evidence-set','constitution','premise','decision','validation','gate','residue','interface-claim-support-compatibility-invariant']];put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comp,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comp]+context['sources'][5:],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Qualified D38 source and separately selected claim/support/interpreter/treatment meanings;no accepted universal strength order,actual truth/authority or consumer map.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
