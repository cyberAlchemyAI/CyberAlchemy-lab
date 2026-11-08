"""Whole selected-theory finite regression, with independent model checks and coverage gaps."""
import base64
from pathlib import Path
import contracts as c
import diff as d
import invalidation as i
import ir
import resolver as r
import verifier as v
from providers import finite as f

SELECTION_KEYS={'schema_version','authority_effect','revision_selection_ref','revision_result_ref','input_ir_refs','alignment_refs','renaming_ref','cardinalities_ref','profile_ref','toolchain_ref','budgets','scope_policy'}
ASSUMED_ROLES={'definition','selected-axiom','selected-premise','constraint'}
MAX_QUERIES=1024
MAX_REPORT_BYTES=16_000_000
class RegressionFault(ValueError):
 def __init__(self,code,path=''):self.code=code;self.path=path

def require(condition,code,path=''):
 if not condition:raise RegressionFault(code,path)
def exact(value,keys,code):require(type(value) is dict and set(value)==set(keys),code)
def engine_files():return [Path(__file__),Path(d.__file__),Path(i.__file__),Path(ir.__file__),Path(v.__file__),Path(v.o.__file__),v.o.RULES,Path(c.__file__),Path(r.__file__)]
def prepare(root,selection):
 exact(selection,SELECTION_KEYS,'malformed-regression-selection');c.bounded_tree(selection);require(selection['schema_version']=='definition-assurance-regression-selection/v1-candidate' and selection['authority_effect']=='none','invalid-regression-boundary');require(type(selection['scope_policy']) is str and selection['scope_policy'] in {'selected-inputs-only','all-current-required'},'unsupported-regression-scope-policy');require(type(selection['input_ir_refs']) is list and selection['input_ir_refs'] and type(selection['alignment_refs']) is list,'nonempty-regression-inputs-required')
 inputs=d.Inputs(root);revision_selection=inputs.load(selection['revision_selection_ref']);stored=inputs.load(selection['revision_result_ref']);fresh=d.generate(root,revision_selection)
 expected=stored['result'] if type(stored) is dict and stored.get('status')=='candidate-revision-generated' else stored
 require(d.equal(expected,fresh),'stale-or-substituted-revision-requirements')
 side=revision_selection['proposal'];epoch=inputs.load(side['epoch_ref'],epoch=True);snapshot_ref=epoch['selection']['snapshot_ref'];snapshot=next(x for x in epoch['captured_artifacts'] if x['ref']==snapshot_ref);snapshot=r.parse(base64.b64decode(snapshot['content_base64']),'source-snapshot')
 theory=fresh['effective_proposal_theory'];inputs.load(side['theory_ref']);assumptions=inputs.load(side['assumptions_ref']);endpoints=inputs.load(side['bindings_ref'])
 originals=[inputs.load(ref) for ref in selection['input_ir_refs']]
 require(len({ref['path'] for ref in selection['input_ir_refs']})==len(originals),'duplicate-regression-input-reference')
 for item in originals:ir.verify_ir(item);ir.compile_interpretation(item['input_core'],snapshot)
 require(sorted(i.digest(item['source']) for item in originals)==sorted(i.digest(source) for source in theory['sources']),'regression-interpretation-source-denominator-mismatch')
 for ref in selection['alignment_refs']:inputs.load(ref)
 subject=ir.compose(originals,selection['alignment_refs'],root);renaming=inputs.load(selection['renaming_ref']);mapping=v.signature_map(theory,subject,originals,renaming,endpoints)
 # Independently selected source-qualified clauses are compiled together. Proof claims are not premises.
 T=v.renamed(theory['statements']+assumptions['assumptions'],mapping);clause_accounts=[];extra_queries=[];pending_clauses=[]
 for clause in subject['clauses']:
  key=clause['namespace']+':'+clause['clause_id'];statement=clause['formal_statement'];roles=set(clause['roles'])
  if statement is None or clause['disposition']!='encoded':disposition='pending-source-clause';pending_clauses.append(key)
  elif roles&ASSUMED_ROLES:
   require(not roles&{'proof-obligation','derived-claim','hypothesis','observation-measurement','explanation-example','unresolved'},'ambiguous-assumed-and-claim-clause-role',key);T.append(statement);disposition='included-in-joint-theory'
  elif roles&{'proof-obligation','derived-claim','hypothesis','observation-measurement'}:
   disposition='additional-universal-claim';extra_queries.append({'obligation_id':'clause:'+key,'statement':statement,'minimum_strength':'mechanized-theorem'})
  else:disposition='pending-logical-role';pending_clauses.append(key)
  clause_accounts.append({'clause_key':key,'roles':sorted(roles),'disposition':disposition,'statement_sha256':ir.digest(statement) if statement is not None else None})
 assumption_accounts=[];interpretation_populations=[]
 for original in originals:
  for population in original['populations']:
   key=original['source']['version_ref']+':'+population['population_id']
   require(population['requirement'] in {'required','exempt'},'unresolved-interpretation-population-policy',key)
   if population['requirement']=='required':
    require(population['statement'] is not None,'missing-required-interpretation-population',key);interpretation_populations.append({'obligation_id':'interpretation-population:'+key,'statement':ir.remap_formula(population['statement'],subject['sort_alignment']),'minimum_strength':'model-witness'})
  for assumption in original['assumptions']:
   statement=ir.remap_formula(assumption['statement'],subject['sort_alignment']);assumption_accounts.append({'source':original['source'],'assumption_id':assumption['assumption_id'],'selected':assumption['selected'],'statement':statement})
   if assumption['selected']:T.append(statement)
 for formula in T:ir.check_composed_formula(subject,formula)
 required=fresh['proposal_required_set'];logical=required['logical_manifest']['obligations'];I=v.renamed([row['statement'] for row in logical if row['obligation_id'].startswith('population:')],mapping)+[row['statement'] for row in interpretation_populations]
 for population in I:ir.check_composed_formula(subject,population)
 queries=[{'obligation_id':row['obligation_id'],'statement':v.renamed(row['statement'],mapping),'minimum_strength':row['minimum_strength']} for row in logical]+extra_queries+interpretation_populations
 require(len(queries)<=MAX_QUERIES and len({row['obligation_id'] for row in queries})==len(queries),'regression-query-denominator-limit-or-duplicate')
 for query in queries:ir.check_composed_formula(subject,query['statement'])
 queries.sort(key=lambda row:(0 if row['obligation_id']=='query:consistency' else 1 if row['obligation_id']=='query:joint-population' else 2,row['obligation_id']))
 require({row['obligation_id'] for row in queries}>={'query:consistency','query:joint-population'},'missing-global-regression-prerequisite')
 cards=inputs.load(selection['cardinalities_ref']);sorts={row['symbol_id'] for row in subject['declarations'] if row['kind']=='sort'};require(type(cards) is dict and set(cards)==sorts and all(type(x) is int and 1<=x<=3 for x in cards.values()),'malformed-regression-cardinalities')
 require(d.equal(inputs.load(selection['profile_ref']),r.parse(f.POLICY_PATH.read_bytes(),'provider-policy')),'regression-profile-substitution');toolchain=inputs.load(selection['toolchain_ref']);exact(toolchain,{'bindings'},'malformed-regression-toolchain');require(d.equal(toolchain['bindings'],f.current_bindings()),'regression-runtime-substitution');limits=f.load_limits(selection['budgets'])
 current={node['definition_id'] for node in epoch['nodes']};included={source['definition_id'] for source in theory['sources']};coverage={'global_current_source_nodes':len(current),'selected_logical_sources':len(included),'included_interpretations':len(originals),'missing_current_interpretations':sorted(current-included),'pending_source_clauses':pending_clauses,'pending_source_fidelity':[source['definition_id'] for source in theory['sources']],'semantic_dependency_closure':'not-established','scope_policy':selection['scope_policy'],'global_result':'unresolved-missing-current-interpretations' if current-included else 'requires-source-fidelity-and-semantic-closure'}
 return {'root':inputs.root,'inputs':inputs,'selection':selection,'revision':fresh,'epoch':epoch,'snapshot':snapshot,'subject':subject,'originals':originals,'mapping':mapping,'T':T,'I':I,'queries':queries,'cards':cards,'limits':limits,'provider_bindings':toolchain['bindings'],'clause_accounts':clause_accounts,'assumption_accounts':assumption_accounts,'coverage':coverage,'engine_files':engine_files(),'engine_bytes':[file.read_bytes() for file in engine_files()]}

def run(root,selection,cancelled=None,before_final_check=None):
 prepared=None;base={'authority_effect':'none','semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'semantic_closure':'not-established','unbounded_conclusion':None}
 try:
  files=engine_files();initial_bytes=[file.read_bytes() for file in files];prepared=prepare(root,selection);rows=[];prerequisites=True;failed=False;incomplete=False;universal_pending=False
  for query in prepared['queries']:
   identity=query['obligation_id'];prerequisite=identity in {'query:consistency','query:joint-population'}
   if not prerequisites:
    rows.append({'obligation_id':identity,'minimum_strength':query['minimum_strength'],'status':'blocked-by-global-prerequisites','reason':'Entire selected T and T plus joint required populations must have checked witnesses first.','native_result':None,'verification':None});continue
   populations=[] if identity=='query:consistency' else prepared['I'];mode='witness' if query['minimum_strength']=='model-witness' else 'countermodel'
   native=f.search(prepared['subject'],prepared['T'],populations,query['statement'],prepared['cards'],mode,budgets=selection['budgets'],cancelled=cancelled,selected_inputs=prepared['originals'],selected_alignments=selection['alignment_refs'],alignment_root=root,snapshot=prepared['snapshot'],live_root=root)
   checked=None
   if native['status'] in {'witness-found','countermodel-found'}:
    require(native.get('input_bindings',{}).get('snapshot_sha256')==ir.digest(prepared['snapshot']),'regression-native-snapshot-substitution')
    checked=v.witness(prepared['subject'],native,prepared['T'],populations,query['statement'],prepared['cards'],mode,prepared['provider_bindings'],selected_inputs=prepared['originals'],alignments=selection['alignment_refs'],root=root,cancelled=cancelled)
    status='independently-checked-witness' if mode=='witness' else 'independently-checked-counterexample'
    if mode!='witness':failed=True
   elif native['status'] in {'bounded-no-theory-model','bounded-no-admissible-model','bounded-no-witness'}:
    status='reported-finite-scope-failure-unverified-exhaustion';failed=True
   elif native['status']=='bounded-no-countermodel':status='reported-bounded-no-counterexample-unverified';universal_pending=True
   else:status='incomplete-no-logical-conclusion';incomplete=True
   if prerequisite and status!='independently-checked-witness':prerequisites=False
   rows.append({'obligation_id':identity,'minimum_strength':query['minimum_strength'],'status':status,'native_result':native,'verification':checked})
  if before_final_check:before_final_check()
  prepared['inputs'].closing();i.live_recheck(prepared['epoch'],root);require(initial_bytes==[file.read_bytes() for file in files] and d.equal(prepared['provider_bindings'],f.current_bindings()),'regression-active-build-or-runtime-drift')
  require([row['obligation_id'] for row in rows]==[q['obligation_id'] for q in prepared['queries']],'regression-required-query-substitution')
  outcome='finite-scope-regression-failed' if failed else 'regression-incomplete' if incomplete else 'universal-evidence-pending' if universal_pending else 'selected-existential-regression-checked'
  selected_outcome=outcome
  if selection['scope_policy']=='all-current-required' and prepared['coverage']['missing_current_interpretations']:outcome='all-current-regression-unresolved'
  affected=set(prepared['revision']['invalidated_current_definitions']);included={item['source']['definition_id'] for item in prepared['originals']}
  result={**base,'schema_version':'definition-assurance-regression-result/v1-candidate','status':outcome,'selected_scope_status':selected_outcome,'coverage':prepared['coverage'],'revision_sha256':prepared['revision']['revision_sha256'],'required_set_sha256':prepared['revision']['proposal_required_set']['required_set_sha256'],'subject_ir_sha256':prepared['subject']['ir_sha256'],'joint_theory_sha256':ir.digest(prepared['T']),'joint_population_sha256':ir.digest(prepared['I']),'joint_theory_statements':prepared['T'],'joint_population_statements':prepared['I'],'clause_accounts':prepared['clause_accounts'],'assumption_accounts':prepared['assumption_accounts'],'required_query_ids':[q['obligation_id'] for q in prepared['queries']],'results':rows,'pending_administrative_and_semantic_gates':prepared['revision']['proposal_required_set']['administrative_and_semantic_gates']+prepared['revision']['supplemental_gates'],'pending_revision_theorems':prepared['revision']['revision_claim_obligations'],'affected_neighbours_in_selected_regression':sorted(affected&included),'affected_neighbours_unresolved_outside_selected_regression':sorted(affected-included),'provider_limits':prepared['limits'],'claim_ceiling':'Full selected T and joint I at one exact finite cardinality vector. Supplied models independently checked; provider exhaustion/absence not independently verified or lifted to an unbounded theorem. Missing current interpretations, source fidelity and semantic closure remain pending.'}
  if len(ir.canonical(result))>MAX_REPORT_BYTES:return {**base,'status':'regression-resource-limit','required_query_ids':result['required_query_ids'],'results':[{'obligation_id':key,'status':'unresolved-output-limit','native_result':None,'verification':None} for key in result['required_query_ids']],'coverage':prepared['coverage']}
  return result
 except (RegressionFault,d.RevisionFault,i.InvalidationFault,r.CaptureFault,ir.IRFault,v.VerificationFault,c.InputError) as error:
  return {**base,'status':'regression-unresolved','required_query_ids':[q['obligation_id'] for q in prepared['queries']] if prepared else [],'results':[],'diagnostics':[{'code':error.code,'path':getattr(error,'path','')}],'claim_ceiling':'No retained model support after input/verification failure.'}
 except (OSError,ValueError,TypeError,KeyError,AttributeError,RecursionError) as error:return {**base,'status':'regression-unresolved','required_query_ids':[q['obligation_id'] for q in prepared['queries']] if prepared else [],'results':[],'diagnostics':[{'code':type(error).__name__}],'claim_ceiling':'Execution or malformed input; no logical absence conclusion.'}

def run_selected(root,selection_ref,**kwargs):
 try:
  i.reference(selection_ref);raw=r.read_bytes(root,selection_ref['path']);require(r.digest(raw)==selection_ref['sha256'],'stale-regression-selection');result=run(root,r.parse(raw,selection_ref['path']),**kwargs);require(r.read_bytes(root,selection_ref['path'])==raw,'regression-selection-changed-during-check');return result
 except (RegressionFault,i.InvalidationFault,r.CaptureFault,c.InputError) as error:return {'status':'regression-unresolved','authority_effect':'none','semantic_ready':False,'results':[],'required_query_ids':[],'diagnostics':[{'code':error.code,'path':getattr(error,'path','')}]}
 except (OSError,ValueError,TypeError,KeyError,AttributeError) as error:return {'status':'regression-unresolved','authority_effect':'none','semantic_ready':False,'results':[],'required_query_ids':[],'diagnostics':[{'code':type(error).__name__}]}
