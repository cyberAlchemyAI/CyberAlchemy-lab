"""Regenerate revision obligations from exact selected inputs; labels cannot waive checks."""
import copy
import json
from pathlib import Path
import contracts as c
import invalidation as i
import obligations as o
import ir
import resolver as r

SIDE_KEYS={'epoch_ref','theory_ref','relations_ref','populations_ref','bindings_ref','assumptions_ref'}
LABELS={'initial','unchanged','representation-only','additive','meaning-change','constraint-change'}
MAX_INPUT_BYTES=64_000_000
MAX_CLAIMS=256
class RevisionFault(ValueError):
 def __init__(self,code,path=''):self.code=code;self.path=path

def require(value,code,path=''):
 if not value:raise RevisionFault(code,path)
def exact(value,keys,code):require(type(value) is dict and set(value)==set(keys),code)
def equal(a,b):return r.same_json(a,b)
def subset(a,b):return set(i.digest(x) for x in a)<=set(i.digest(x) for x in b)
def typed(theory,assumptions,required):
 declarations=theory['declarations'];require(type(declarations) is list,'malformed-declarations');symbols={};sorts={}
 for row in declarations:
  require(type(row) is dict and type(row.get('kind')) is str,'malformed-declaration');kind=row['kind'];keys={'kind','symbol_id','scope'}
  if kind=='sort':keys.add('domain_policy')
  elif kind in {'predicate','relation'}:keys.add('argument_sorts')
  elif kind=='constant':keys.add('result_sort')
  elif kind=='total-function':keys.update({'argument_sorts','result_sort'})
  else:raise RevisionFault('unsupported-declaration-kind')
  exact(row,keys,'malformed-declaration');ir.name(row['symbol_id']);require(row['symbol_id'] not in symbols and row['scope']==theory['scope'],'duplicate-or-unscoped-declaration');symbols[row['symbol_id']]=row
  if kind=='sort':require(row['domain_policy']=='nonempty','unsupported-domain-policy');sorts[row['symbol_id']]=row['symbol_id']
 for row in declarations:
  if 'argument_sorts' in row:require(type(row['argument_sorts']) is list and all(type(x) is str and x in sorts for x in row['argument_sorts']),'unbound-signature-sort')
  if 'result_sort' in row:require(type(row['result_sort']) is str and row['result_sort'] in sorts,'unbound-signature-sort')
 non_sorts={key:row for key,row in symbols.items() if row['kind']!='sort'}
 for formula in theory['statements']+assumptions['assumptions']+[x['statement'] for x in required['logical_manifest']['obligations']]:ir.formula(formula,sorts,non_sorts)
 return {'status':'selected-formulas-typed','authority_effect':'none','semantic_ready':False}

class Inputs:
 def __init__(self,root):self.root=r.resolve_root(root);self.raw={};self.refs={};self.bytes=0
 def load(self,ref,epoch=False):
  i.reference(ref);raw=i._epoch_raw(self.root,ref) if epoch else r.read_bytes(self.root,ref['path']);require(r.digest(raw)==ref['sha256'],'stale-selected-revision-input',ref['path'])
  if ref['path'] in self.raw:require(self.raw[ref['path']]==raw and self.refs[ref['path']]==ref,'revision-read-race',ref['path'])
  else:self.bytes+=len(raw);require(self.bytes<=MAX_INPUT_BYTES,'revision-input-byte-limit');self.raw[ref['path']]=raw;self.refs[ref['path']]=copy.deepcopy(ref)
  value=r.parse(raw,ref['path']);return i.validate_epoch(value) if epoch else value
 def closing(self):
  for path,raw in self.raw.items():
   actual=i._epoch_raw(self.root,self.refs[path],verify_hash=False) if path.endswith('.json') and len(raw)>4_000_000 else r.read_bytes(self.root,path)
   require(actual==raw,'revision-input-changed-during-check',path)

def load_side(inputs,selection):
 exact(selection,SIDE_KEYS,'malformed-revision-side');side={key.removesuffix('_ref'):inputs.load(ref,epoch=key=='epoch_ref') for key,ref in selection.items()}
 theory=side['theory'];nodes={x['definition_id']:x for x in side['epoch']['nodes']}
 exact(theory,{'theory_id','sources','declarations','statements','assumption_set_id','scope','change_class','prior_theory_ref'},'malformed-revision-theory')
 require(type(theory['sources']) is list and theory['sources'],'nonempty-theory-sources-required')
 for source in theory['sources']:
  require(type(source) is dict and source.get('definition_id') in nodes and equal(source,nodes[source['definition_id']]['source']),'theory-epoch-source-substitution')
 exact(side['assumptions'],{'assumption_set_id','assumptions','authority_effect'},'malformed-revision-assumptions');require(side['assumptions']['authority_effect']=='none' and side['assumptions']['assumption_set_id']==theory['assumption_set_id'] and type(side['assumptions']['assumptions']) is list,'assumption-context-substitution')
 require(type(side['relations']) is list and type(side['populations']) is list and type(side['bindings']) is dict,'malformed-revision-policy-inputs')
 for request in side['relations']:
  mapping=request.get('relation',{}).get('alignment',{}).get('map_ref')
  if mapping is not None:inputs.load(mapping)
 if theory['prior_theory_ref'] is not None:inputs.load(theory['prior_theory_ref'])
 return side

def generate(root,selection,before_final_check=None):
 exact(selection,{'schema_version','authority_effect','baseline','proposal','declared_change','claims'},'malformed-revision-selection');c.bounded_tree(selection)
 require(selection['schema_version']=='definition-assurance-revision-selection/v1-candidate' and selection['authority_effect']=='none','invalid-revision-boundary');require(type(selection['declared_change']) is str and selection['declared_change'] in LABELS,'unsupported-declared-change');require(type(selection['claims']) is list and len(selection['claims'])<=MAX_CLAIMS,'malformed-revision-claims')
 engine_files=[Path(__file__),Path(o.__file__),o.RULES,Path(ir.__file__),Path(i.__file__),Path(c.__file__),Path(r.__file__),Path(o.p.__file__),o.p.PROFILE,o.POLICY_RECEIPT];engine_bytes=[x.read_bytes() for x in engine_files]
 inputs=Inputs(root);old=load_side(inputs,selection['baseline']);new=load_side(inputs,selection['proposal']);epoch_plan=i.compare_epochs(old['epoch'],new['epoch'])
 old_theory=old['theory'];raw_theory=new['theory'];old_required=o.generate(old_theory,old['relations'],old['populations'],old['bindings'],inputs.root);typed(old_theory,old['assumptions'],old_required)
 fields={'source':not equal(old_theory['sources'],raw_theory['sources']),'signature':not equal(old_theory['declarations'],raw_theory['declarations']),'statement':not equal(old_theory['statements'],raw_theory['statements']),'premise':not equal(old['assumptions'],new['assumptions']),'coupling':not equal(old['relations'],new['relations']),'population':not equal(old['populations'],new['populations']) or not equal(old['bindings'],new['bindings']),'scope':old_theory['scope']!=raw_theory['scope'],'theory-identity':old_theory['theory_id']!=raw_theory['theory_id']}
 binding_changes=[key for key in SIDE_KEYS-{'epoch_ref'} if selection['baseline'][key]!=selection['proposal'][key]]
 representation=[key for key in binding_changes if equal(old[key.removesuffix('_ref')],new[key.removesuffix('_ref')])]
 changed=any(fields.values()) or bool(epoch_plan['direct_deltas'] or epoch_plan['global_changes'] or binding_changes)
 monotone=all(subset(old_theory[key],raw_theory[key]) for key in ['sources','declarations','statements']) and old_theory['scope']==raw_theory['scope'] and not fields['premise'] and subset(old['relations'],new['relations']) and subset(old['populations'],new['populations']) and all(key in new['bindings'] and equal(value,new['bindings'][key]) for key,value in old['bindings'].items())
 extension=monotone and (len(raw_theory['sources'])>len(old_theory['sources']) or len(raw_theory['declarations'])>len(old_theory['declarations']))
 if not changed:derived='unchanged'
 elif extension:derived='additive'
 elif fields['source'] or fields['signature'] or fields['scope'] or fields['theory-identity'] or any(x['changed_content_parts'] for x in epoch_plan['direct_deltas']):derived='meaning-change'
 elif fields['statement'] or fields['premise'] or fields['coupling'] or fields['population']:derived='constraint-change'
 else:derived='representation-only'
 effective=copy.deepcopy(raw_theory)
 if derived=='unchanged':effective['change_class']=old_theory['change_class'];effective['prior_theory_ref']=old_theory['prior_theory_ref']
 else:effective['change_class']='meaning-change' if derived=='representation-only' else derived;effective['prior_theory_ref']=copy.deepcopy(selection['baseline']['theory_ref'])
 # A declared label is explanatory only. This candidate effective subject cannot mutate the source theory.
 generated=o.generate(effective,new['relations'],new['populations'],new['bindings'],inputs.root);typing=typed(effective,new['assumptions'],generated)
 old_context=i.digest({'theory':old_theory,'assumptions':old['assumptions'],'relations':old['relations'],'populations':old['populations'],'bindings':old['bindings'],'epoch':old['epoch']['epoch_sha256']})
 new_context=i.digest({'theory':effective,'assumptions':new['assumptions'],'relations':new['relations'],'populations':new['populations'],'bindings':new['bindings'],'epoch':new['epoch']['epoch_sha256']})
 ledger=[]
 for category,a,b,key in [('logical',old_required['logical_manifest']['obligations'],generated['logical_manifest']['obligations'],'obligation_id'),('gate',old_required['administrative_and_semantic_gates'],generated['administrative_and_semantic_gates'],'gate_id'),('query',old_required['query_requirements'],generated['query_requirements'],'obligation_id')]:
  before={x[key]:x for x in a};after={x[key]:x for x in b}
  for identity in sorted(set(before)|set(after)):
   x,y=before.get(identity),after.get(identity);status='new' if x is None else 'removed-pending-retirement-review' if y is None else 'unchanged' if equal(x,y) and old_context==new_context else 'replaced-context-or-target'
   ledger.append({'category':category,'requirement_id':identity,'status':status,'baseline_requirement':x,'proposal_requirement':y,'baseline_context_sha256':old_context,'proposal_context_sha256':new_context,'prior_evidence_inherited':False})
 supplemental=[];gates=[]
 def gate(key,check,subject,strength='source-review'):gates.append({'gate_id':key,'check':check,'subject':subject,'minimum_strength':strength,'status':'required','authority_effect':'none'})
 subject={'baseline':selection['baseline'],'proposal':selection['proposal'],'effective_theory_sha256':i.digest(effective)}
 if changed:gate('revision:binding-review','revision-input-binding-review',subject,'structural')
 if any(fields[k] for k in ['source','signature','scope','theory-identity']):gate('revision:meaning-review','meaning-change-review',subject)
 if any(fields[k] for k in ['statement','premise','coupling','population']):gate('revision:constraint-review','constraint-change-review',subject)
 if epoch_plan['global_regression_required'] or changed:gate('revision:global-regression','whole-selected-theory-regression',subject,'model-witness')
 if selection['declared_change'] in {'additive','meaning-change','constraint-change'}:
  check={'additive':'conservativity','meaning-change':'meaning-change-review','constraint-change':'constraint-change-review'}[selection['declared_change']];gate('revision:declared:'+check,check,subject,'mechanized-theorem' if check=='conservativity' else 'source-review')
 for previous_gate in old_required['administrative_and_semantic_gates']:
  if previous_gate['check'] in {'conservativity','meaning-change-review','constraint-change-review'}:gate('revision:prior-policy:'+previous_gate['gate_id'],previous_gate['check'],{'baseline_requirement':previous_gate,'baseline_context_sha256':old_context,'disposition':'Retained requirement; no prior evidence inherited or retirement approval inferred.'},previous_gate['minimum_strength'])
 retired=[x for x in ledger if x['status']=='removed-pending-retirement-review']
 if retired:gate('revision:retirement-review','obsolete-requirement-retirement-review',{'ledger_sha256':i.digest(retired),'requirements':retired})
 claims=copy.deepcopy(selection['claims'])
 if derived=='additive':claims.append({'claim_id':'policy:derived-additive-conservativity','kind':'conservativity','targets':[],'embedding_ref':None})
 if claims:gate('revision:baseline-admissibility','baseline-consistency-and-joint-population',{'baseline_theory_ref':selection['baseline']['theory_ref'],'baseline_assumptions_ref':selection['baseline']['assumptions_ref'],'baseline_context_sha256':old_context,'baseline_required_set_sha256':old_required['required_set_sha256'],'required_queries':[row for row in old_required['logical_manifest']['obligations'] if row['obligation_id'] in {'query:consistency','query:joint-population'}]},'model-witness')
 seen=set();source_versions={x['version_ref'] for x in old_theory['sources']+raw_theory['sources']};prior_ids={x['obligation_id'] for x in old_required['logical_manifest']['obligations']}
 for claim in claims:
  exact(claim,{'claim_id','kind','targets','embedding_ref'},'malformed-revision-claim');identity=claim['claim_id'];require(i.text(identity) and identity not in seen,'duplicate-revision-claim');seen.add(identity);require(type(claim['kind']) is str and claim['kind'] in {'preservation','conservativity','identity-equivalence'},'unsupported-revision-claim');targets=claim['targets'];require(type(targets) is list and all(i.text(x) for x in targets) and (claim['kind']=='identity-equivalence' or len(set(targets))==len(targets)),'malformed-claim-targets')
  if claim['kind']=='preservation':require(targets and set(targets)<=prior_ids,'unbound-preservation-target')
  elif claim['kind']=='conservativity':require(not targets,'conservativity-cannot-shrink-old-signature')
  else:require(len(targets)==2 and targets[0] in {s['version_ref'] for s in old_theory['sources']} and targets[1] in {s['version_ref'] for s in raw_theory['sources']},'unbound-identity-equivalence-target')
  mapping=inputs.load(claim['embedding_ref']) if claim['embedding_ref'] is not None else None
  descriptor={'kind':claim['kind'],'baseline_theory_ref':selection['baseline']['theory_ref'],'proposal_theory_ref':selection['proposal']['theory_ref'],'effective_proposal_theory_sha256':i.digest(effective),'baseline_context_sha256':old_context,'proposal_context_sha256':new_context,'old_signature':old_theory['declarations'],'new_signature':effective['declarations'],'selected_target_ids':targets,'embedding_ref':claim['embedding_ref'],'embedding_data_sha256':i.digest(mapping) if mapping is not None else None,'meaning':{'preservation':'Every admissible proposal model, via reviewed old-signature interpretation, satisfies the explicitly selected old targets.','conservativity':'Every admissible baseline model has an admissible proposal expansion whose reviewed reduct equals that baseline model; old-language consequences require separate proof.','identity-equivalence':'Exactly the selected old/new source interpretations agree under a reviewed carrier/signature mapping; names alone supply no identity.'}[claim['kind']]}
  if claim['kind']=='identity-equivalence':descriptor['selected_source_pair']={'baseline_source':next(s for s in old_theory['sources'] if s['version_ref']==targets[0]),'proposal_source':next(s for s in raw_theory['sources'] if s['version_ref']==targets[1])}
  supplemental.append({'obligation_id':'revision-claim:'+identity,'descriptor':descriptor,'minimum_strength':'mechanized-theorem','status':'required','proof_encoding':'pending-explicit-cross-theory-contract','semantic_ready':False});gate('revision:embedding:'+identity,'cross-theory-embedding-review',descriptor)
 all_nodes={x['definition_id'] for x in new['epoch']['nodes']};scope_ids={x['definition_id'] for x in old_theory['sources']+raw_theory['sources']};seeds=set(epoch_plan['invalidated_current_definitions']+epoch_plan['affected_prior_only_definitions'])|(scope_ids if changed else set());reverse={x:set() for x in {a for edge in epoch_plan['propagation_edges'] for a in edge}|all_nodes|seeds}
 for consumer,dependency in epoch_plan['propagation_edges']:reverse[dependency].add(consumer)
 affected=i.d.closure(seeds,reverse)
 result={'schema_version':'definition-assurance-revision-requirements/v1-candidate','authority_effect':'none','semantic_ready':False,'evidence_verified':False,'declared_change':selection['declared_change'],'raw_proposal_change_class':raw_theory['change_class'],'raw_proposal_prior_theory_ref':raw_theory['prior_theory_ref'],'derived_change':derived,'label_matches_derived_change':selection['declared_change']==derived,'observed_content_changes':fields,'representation_binding_changes':representation,'invalidation_plan':epoch_plan,'invalidated_current_definitions':sorted(set(affected)&all_nodes),'global_regression_required':bool(changed or epoch_plan['global_regression_required']),'baseline_required_set':old_required,'effective_proposal_theory':effective,'proposal_required_set':generated,'requirement_ledger':ledger,'supplemental_gates':sorted(gates,key=lambda x:x['gate_id']),'revision_claim_obligations':supplemental,'selected_formulas_typing':typing,'engine_bindings':[{'path':x.relative_to(Path(__file__).resolve().parents[4]).as_posix(),'sha256':r.digest(raw)} for x,raw in zip(engine_files,engine_bytes)],'logical_scope_sources':len(effective['sources']),'global_current_source_nodes':len(all_nodes),'source_fidelity':'pending','semantic_closure':'not-established','claim_ceiling':'Exact revision classification and regenerated requirements only. No evidence inheritance, model expansion proof, identity equivalence, source fidelity, semantic admission or complete episode.'};result['revision_sha256']=i.digest(result)
 if before_final_check:before_final_check()
 inputs.closing();i.live_recheck(new['epoch'],inputs.root);require(engine_bytes==[x.read_bytes() for x in engine_files],'revision-engine-changed-during-check');return result

def compare_submission(root,selection,submitted):
 expected=generate(root,selection);require(equal(expected,submitted),'revision-requirement-denominator-or-binding-substitution');return {'status':'revision-requirements-identical','authority_effect':'none','semantic_ready':False,'evidence_verified':False}

def analyze_selected(root,ref,before_final_check=None):
 try:
  i.reference(ref);raw=r.read_bytes(root,ref['path']);require(r.digest(raw)==ref['sha256'],'stale-revision-selection');result=generate(root,r.parse(raw,ref['path']),before_final_check);require(r.read_bytes(root,ref['path'])==raw,'revision-selection-changed-during-check');return {'status':'candidate-revision-generated','authority_effect':'none','semantic_ready':False,'result':result}
 except (RevisionFault,i.InvalidationFault,r.CaptureFault,o.ObligationFault,o.p.PolicyFault,ir.IRFault,c.InputError) as error:return {'status':'revision-unresolved','authority_effect':'none','semantic_ready':False,'result':None,'diagnostics':[{'code':error.code,'path':getattr(error,'path','')}]}
 except (OSError,ValueError,TypeError,KeyError,AttributeError,RecursionError) as error:return {'status':'revision-unresolved','authority_effect':'none','semantic_ready':False,'result':None,'diagnostics':[{'code':type(error).__name__}]}
