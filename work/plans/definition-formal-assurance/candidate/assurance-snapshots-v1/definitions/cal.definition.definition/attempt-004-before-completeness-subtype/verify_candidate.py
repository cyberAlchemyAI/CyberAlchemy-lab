"""Independently evaluate typed Definition models, non-entailment and bounded metadata model pairs."""
import copy
import json
import build_candidate as b
import verifier as v
VALUES={'Record':['d'],'Identity':['id0','id1'],'VersionKey':['v0','v1'],'Term':['t0'],'Meaning':['m0','m1'],'AuthorityScope':['s0','s1'],'Owner':['o0','o1'],'Decision':['q0'],'Voice':['plain','domain'],'ArtifactType':['at0','at1'],'SemanticKind':['sk0','sk1'],'AuthorityKind':['ak0','ak1'],'LifecyclePosture':['lc0','lc1'],'ContextMembership':['cm0','cm1'],'Axis':['identity','artifact-type','semantic-kind','authority-kind','lifecycle','owner-scope','context-membership']}
CONSTANT_VALUES={'PlainVoice':'plain','DomainVoice':'domain','IdentityAxis':'identity','ArtifactTypeAxis':'artifact-type','SemanticKindAxis':'semantic-kind','AuthorityKindAxis':'authority-kind','LifecycleAxis':'lifecycle','OwnerScopeAxis':'owner-scope','ContextMembershipAxis':'context-membership'}

def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 predicates={name:[] for name in b.SIGNATURE}
 for name in ['Definition','SemanticArtifact','Versioned','OwnerScoped','DefinitionComplete','SchemaValid','EvidencePresent','SharedSemanticRole',*b.FORMAL_FLAGS,*b.PROSE_EXTRA]:predicates[name]=[['d']]
 predicates['InterpretiveVoice']=[['plain'],['domain']];predicates['AssignsNormativeMeaning']=[['d','t0','m0','s0']]
 functions={name:[{'args':['d'],'value':VALUES[sort][0]}] for name,sort in b.FIELDS.items()}
 functions.update({name:[{'args':['q0'],'value':VALUES[sort][0]}] for name,sort in b.DECISION_FIELDS.items()})
 return {'domains':copy.deepcopy(VALUES),'constants':copy.deepcopy(CONSTANT_VALUES),'functions':functions,'predicates':predicates}
def set_field(model,name,value,record='d'):
 next(row for row in model['functions'][name] if row['args']==[record])['value']=value
 if name in {'termOf','meaningOf','scopeOf'}:assignments(model)
def assignments(model):
 rows=[]
 for record in [x[0] for x in model['predicates']['Definition']]:
  values=[next(row['value'] for row in model['functions'][name] if row['args']==[record]) for name in ['termOf','meaningOf','scopeOf']];rows.append([record,*values])
 model['predicates']['AssignsNormativeMeaning']=rows

def second_record(model,definition=True):
 model['domains']['Record'].append('e')
 for name,sort in b.FIELDS.items():model['functions'][name].append({'args':['e'],'value':VALUES[sort][0]})
 if definition:
  for name,rows in model['predicates'].items():
   if b.SIGNATURE[name]==['Record'] and ['d'] in rows:rows.append(['e'])
 assignments(model)

def controls():
 results=[]
 def add(name,change,T=True,I=True,error=None):
  model=base_model();change(model);results.append({'case_id':name,'model':model,'expected_T':T,'expected_I':I,'expected_error':error})
 add('complete-valid-evidenced-but-unadmitted-unpromoted',lambda model:None)
 add('complete-and-admitted-not-forbidden',lambda model:model['predicates'].update(Admitted=[['d']]))
 for name in b.FORMAL_FLAGS+b.PROSE_EXTRA+['SemanticArtifact','Versioned','OwnerScoped']:
  add('missing-'+name,lambda model,name=name:model['predicates'].__setitem__(name,[]),T=False)
 def incomplete(model):model['predicates'].update(StableId=[],DefinitionComplete=[])
 add('incomplete-record-is-not-a-complete-population',incomplete,I=False)
 for name in b.PROSE_EXTRA:
  def absent(model,name=name):model['predicates'][name]=[];model['predicates']['DefinitionComplete']=[]
  add('ten-formal-fields-force-completeness-despite-absent-'+name,absent,T=False,I=False)
 add('extra-normative-meaning-is-rejected',lambda model:model['predicates']['AssignsNormativeMeaning'].append(['d','t0','m1','s0']),T=False)
 add('missing-normative-assignment-is-rejected',lambda model:model['predicates'].update(AssignsNormativeMeaning=[]),T=False)
 def meaning_change(model,new_version):
  second_record(model);set_field(model,'meaningOf','m1','e')
  if new_version:set_field(model,'versionOf','v1','e')
 add('meaning-change-requires-new-version',lambda model:meaning_change(model,False),T=False)
 add('new-semantic-version-permits-meaning-change',lambda model:meaning_change(model,True))
 add('same-meaning-observations-do-not-force-new-version',lambda model:second_record(model))
 for name in ['WeakensNormative','ExpandsNormative']:
  add('interpretive-voice-'+name,lambda model,name=name:model['predicates'].__setitem__(name,[['d','plain']]),T=False)
 add('canonical-authority-with-no-promotion-is-rejected',lambda model:model['predicates'].update(CanonicalAuthority=[['d']]),T=False)
 for name,wrong in [('decisionIdentity','id1'),('decisionVersion','v1'),('decisionOwner','o1'),('decisionScope','s1')]:
  def bad_decision(model,name=name,wrong=wrong):model['predicates'].update(CanonicalAuthority=[['d']],OwnerPromotion=[['q0']]);set_field(model,name,wrong,'q0')
  add('promotion-mismatch-'+name,bad_decision,T=False)
 for name in ['StandaloneGlossary','StandaloneOntologyNode','StandaloneQuotation','StandaloneIndexRow','StandaloneNarrative','StandaloneGeneratedSummary','StandaloneGlossaryHint']:
  add(name+'-cannot-supply-Definition-by-itself',lambda model,name=name:model['predicates'].__setitem__(name,[['d']]),T=False)
 add('nonshared-context-local-expression-excluded',lambda model:model['predicates'].update(ContextLocalOnly=[['d']],SharedSemanticRole=[]),T=False)
 add('dependent-axis-without-explicit-relation-rejected',lambda model:model['predicates'].update(DependentAxis=[['d','identity','authority-kind']]),T=False)
 add('explicit-relation-is-necessary-not-canonical-validity-proof',lambda model:model['predicates'].update(DependentAxis=[['d','identity','authority-kind']],ExplicitTypedAxisRelation=[['d','identity','authority-kind']]))
 add('convenience-label-needs-generated-projection',lambda model:model['predicates'].update(ConvenienceLabel=[['d']]),T=False)
 add('generated-convenience-label-does-not-promote',lambda model:model['predicates'].update(ConvenienceLabel=[['d']],GeneratedProjection=[['d']]))
 add('ill-sorted-function-value-rejected',lambda model:set_field(model,'meaningOf','s0'),error='ill-sorted-function-result')
 add('non-total-function-rejected',lambda model:model['functions']['meaningOf'].clear(),error='nontotal-function')
 return results

def qualified(model,ids):return {'domains':{ids[name]:values for name,values in model['domains'].items()},'constants':{ids[name]:value for name,value in model['constants'].items()},'functions':{ids[name]:rows for name,rows in model['functions'].items()},'predicates':{ids[name]:rows for name,rows in model['predicates'].items()}}
def verify(write=False):
 files=[b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py',b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py'];bindings=[b.ref(path) for path in files];runtime=v.f.current_bindings();context=load('context.json')
 for reference in context['sources']:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Changed selected input')
 snap=b.snapshot();b.r.verify(snap,b.ROOT);packet=load('correspondence.json');envelope=load('t.json');core=envelope['payload'];typed=load('static-ir.json')
 if b.c.validate(envelope,'interpretation')['status']!='structurally-valid' or not b.r.same_json(packet['interpretation'],core) or not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)):raise ValueError('Interpretation/IR substitution or malformed inputs')
 correspondence=b.co.check(packet,snap,required_dependencies=[row['version_ref'] for row in core['depends_on']],required_conflicts=[row['finding_id'] for row in packet['source_precedence']['conflicts']])
 if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence,load('correspondence-check.json')):raise ValueError('Wrong source clause denominator')
 if core['assumptions'] or core['source_fidelity']!='pending':raise ValueError('Fabricated premise or source fidelity')
 ids={row['symbol_id']:b.ir.qualified(core['source'],core['scope'],row['symbol_id']) for row in core['declarations']};T=[row for row in typed['clauses'] if row['disposition']=='encoded'];I=[row for row in typed['populations'] if row['requirement']=='required'];results=[]
 def evaluate(model):
  evaluator=v.Denotation(typed['declarations'],model);clauses=[{'clause_id':row['clause_id'],'truth':evaluator.truth(row['formal_statement'])} for row in T];populations=[{'population_id':row['population_id'],'truth':evaluator.truth(row['statement'])} for row in I];return all(row['truth'] for row in clauses),all(row['truth'] for row in populations),clauses,populations
 for control in controls():
  model=qualified(control['model'],ids)
  try:
   theory,population,clauses,populations=evaluate(model)
   if control['expected_error'] is not None or theory is not control['expected_T'] or population is not control['expected_I']:raise ValueError('Wrong semantic control: '+control['case_id'])
   result={'case_id':control['case_id'],'model':model,'model_sha256':b.ir.digest(model),'status':'independently-evaluated-authored-model','theory_satisfied':theory,'population_satisfied':population,'clause_results':clauses,'population_results':populations}
  except v.VerificationFault as error:
   if error.code!=control['expected_error']:raise
   result={'case_id':control['case_id'],'model':model,'model_sha256':b.ir.digest(model),'status':'rejected-model-structure','code':error.code,'theory_satisfied':None,'population_satisfied':None}
  results.append(result)
 # Metalevel non-entailment queries are deliberately separate from T.
 base=qualified(base_model(),ids);evaluator=v.Denotation(typed['declarations'],base);queries=[]
 for query in load('query-policy.json')['queries']:
  target=v.renamed(query['target'],ids);condition=v.renamed(query['witness_condition'],ids)
  if query['selected_in_T'] is not False or evaluator.truth(target) is not False or evaluator.truth(condition) is not True:raise ValueError('Non-entailment target assumed or not witnessed')
  queries.append({'query_id':query['query_id'],'target_false':True,'witness_condition_true':True,'model_sha256':b.ir.digest(base),'status':'independently-evaluated-authored-countermodel','mechanized_proof':False})
 pairs=[]
 for field in ['identityOf','artifactTypeOf','semanticKindOf','authorityKindOf','lifecycleOf','scopeOf','contextMembershipOf']:
  left=base_model();second_record(left,definition=False);right=copy.deepcopy(left);set_field(right,field,VALUES[b.FIELDS[field]][1],'e');lm=qualified(left,ids);rm=qualified(right,ids)
  if evaluate(lm)[:2]!=(True,True) or evaluate(rm)[:2]!=(True,True):raise ValueError('Metadata model pair fails full selected T/I')
  changed=[name for name in b.FIELDS if left['functions'][name]!=right['functions'][name]]
  if changed!=[field]:raise ValueError('More than one observation varied')
  pairs.append({'field':field,'left_model':lm,'right_model':rm,'left_sha256':b.ir.digest(lm),'right_sha256':b.ir.digest(rm),'both_T_and_I_satisfied':True,'scope':'generic additional record e; base Definition d unchanged','claim_ceiling':'Shows this selected abstract T does not fix the generic-record observation from the other fields. No canonical Definition value-validity or all-model axis-independence theorem.'})
 prior=json.loads((b.BASE/'definitions/cal.definition.axiom/delivery-manifest.json').read_bytes())
 for reference in prior['files']+context['sources']+bindings:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Closing source/checker/prior-delivery drift')
 b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Closing runtime drift')
 report={'schema_version':'definition-assurance-definition-model-controls/v1-candidate','status':'PASS-for-exact-authored-record-models-and-query-separation','authority_effect':'none','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending','source_fidelity':'pending','input_refs':[b.ref(b.UNIT/name) for name in ['t.json','correspondence.json','static-ir.json','query-policy.json']],'checker_bindings':bindings,'runtime_bindings':runtime,'source_units':len(packet['source_units']),'mapped_clauses':len(core['clauses']),'encoded_clause_ids':[row['clause_id'] for row in T],'required_population_ids':[row['population_id'] for row in I],'deferred_clause_ids':correspondence['unresolved_clauses'],'unresolved_population_ids':[row['population_id'] for row in core['populations'] if row['requirement']=='unresolved'],'results':results,'control_count':len(results),'nonentailment_countermodels':queries,'bounded_metadata_pairs':pairs,'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'claim_ceiling':'Independent E03 denotation of authored finite record structures, explicit non-entailment witnesses and seven generic-record model pairs. Axis carrier has seven values; this is not a native P02 profile search. No actual owner promotion, exhaustive search, canonical field independence, source fidelity or unbounded theorem.'}
 if write:b.put('model-controls.json',report)
 return report

def main():
 write='--write' in b.sys.argv;result=verify(write)
 if not write and not b.r.same_json(result,load('model-controls.json')):raise ValueError('Fresh independent replay differs')
 print(json.dumps({'result':result['status'],'controls':result['control_count'],'nonentailment_countermodels':len(result['nonentailment_countermodels']),'generic_metadata_model_pairs':len(result['bounded_metadata_pairs']),'source_units':result['source_units'],'mapped_clauses':result['mapped_clauses'],'encoded_clauses':len(result['encoded_clause_ids']),'deferred_clauses':len(result['deferred_clause_ids']),'required_populations':2,'unresolved_populations':len(result['unresolved_population_ids']),'prior_candidate_files_preserved':result['prior_candidate_files_preserved'],'source_files_current':201,'whole_translation':'pending','semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
