"""Regenerate the authored Axiom IR and independently evaluate exact synthetic controls."""
import copy
import json
import build_candidate as b
import verifier as v

def read(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 predicates={name:[] for name in b.SIGNATURE}
 predicates.update(Axiom=[['p','s']],Foundational=[['p']],TakenAsGiven=[['p','s']],HeldTrue=[['p','s']],HighVeracityPosture=[['p','s']],WorldDomainSubject=[['p']],Grounds=[['p','i','s'],['p','j','s']],PremiseItem=[['i']],InvariantItem=[['j']])
 return {'domains':{'Proposition':['p'],'SystemContext':['s'],'DownstreamItem':['i','j']},'constants':{},'functions':{},'predicates':predicates}
def qualify(model,ids):return {'domains':{ids[k]:value for k,value in model['domains'].items()},'constants':{},'functions':{},'predicates':{ids[k]:value for k,value in model['predicates'].items()}}
def controls():
 result=[]
 def case(name,modify,T=True,I=True,error=None):
  model=base_model();modify(model);result.append({'case_id':name,'model':model,'expected_theory':T,'expected_population':I,'expected_error':error})
 case('held-true-with-world-truth-undetermined',lambda model:None)
 case('held-true-with-world-truth-true',lambda model:model['predicates'].update(ActualWorldTruth=[['p']]))
 for name in ['Foundational','TakenAsGiven','HeldTrue','HighVeracityPosture','WorldDomainSubject']:
  case('missing-'+name,lambda model,name=name:model['predicates'].__setitem__(name,[]),T=False,I=name not in {'Foundational','WorldDomainSubject'})
 for name in ['InternallyDerived','LowVeracityBet','SystemBehaviorConstraint','AxiomSelfEnforces']:
  case('forbidden-'+name,lambda model,name=name:model['predicates'].__setitem__(name,[['p','s']]),T=False)
 case('invariant-item-cannot-self-enforce',lambda model:model['predicates'].update(ItemSelfEnforces=[['j','s']]),T=False)
 case('one-consequence-is-insufficient',lambda model:model['predicates'].update(Grounds=[['p','i','s']]),T=False)
 case('two-kind-labels-on-one-item-are-not-two-items',lambda model:model['predicates'].update(Grounds=[['p','i','s']],InvariantItem=[['i']]),T=False)
 case('zero-consequences-is-inert',lambda model:model['predicates'].update(Grounds=[]),T=False)
 case('consequence-of-no-permitted-kind',lambda model:model['predicates'].update(InvariantItem=[]),T=False)
 case('absence-of-one-downstream-kind-is-currently-permitted',lambda model:model['predicates'].update(ConstitutionRuleItem=[]))
 case('empty-axiom-class-is-not-inhabited',lambda model:model['predicates'].update(Axiom=[]),I=False)
 def scoped(model,classified):
  model['domains']['SystemContext'].append('s2')
  if classified:model['predicates']['Axiom'].append(['p','s2'])
 case('posture-does-not-transfer-to-new-classified-context',lambda model:scoped(model,True),T=False)
 case('unclassified-context-does-not-create-axiom-obligations',lambda model:scoped(model,False))
 case('ill-sorted-grounding-reference',lambda model:model['predicates'].update(Grounds=[['p','i','p']]),error='ill-sorted-model-tuple')
 case('duplicate-grounding-tuple',lambda model:model['predicates']['Grounds'].append(['p','i','s']),error='duplicate-predicate-tuple')
 return result

def verify(write=False):
 files=[b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py',b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py'];bindings=[b.ref(path) for path in files];runtime=v.f.current_bindings()
 context=read('context.json')
 for reference in context['sources']:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Changed source/context input')
 snap=b.snapshot();b.r.verify(snap,b.ROOT);envelope=read('t.json');packet=read('correspondence.json');core=envelope['payload'];typed=read('static-ir.json')
 structural=b.c.validate(envelope,'interpretation')
 if structural['status']!='structurally-valid' or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted or malformed selected interpretation')
 regenerated=b.ir.compile_interpretation(core,snap)
 if not b.r.same_json(typed,regenerated):raise ValueError('IR failed exact source-qualified regeneration')
 versions=[dep['version_ref'] for dep in core['depends_on']];findings=[finding['finding_id'] for finding in packet['source_precedence']['conflicts']];correspondence=b.co.check(packet,snap,required_dependencies=versions,required_conflicts=findings)
 if not b.r.same_json(correspondence,read('correspondence-check.json')) or not correspondence['character_accounting_complete']:raise ValueError('Incomplete or stale clause accounting')
 if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Described proposition was adopted or owner fidelity fabricated')
 ids={decl['symbol_id']:b.ir.qualified(core['source'],core['scope'],decl['symbol_id']) for decl in core['declarations']}
 T=[clause for clause in typed['clauses'] if clause['disposition']=='encoded'];I=[pop for pop in typed['populations'] if pop['requirement']=='required'];unresolved=[pop['population_id'] for pop in core['populations'] if pop['requirement']=='unresolved'];results=[]
 for control in controls():
  model=qualify(control['model'],ids)
  try:
   evaluator=v.Denotation(typed['declarations'],model);truths=[{'clause_id':clause['clause_id'],'truth':evaluator.truth(clause['formal_statement'])} for clause in T];population_truths=[{'population_id':pop['population_id'],'truth':evaluator.truth(pop['statement'])} for pop in I];theory=all(row['truth'] for row in truths);population=all(row['truth'] for row in population_truths)
   if control['expected_error'] is not None or theory is not control['expected_theory'] or population is not control['expected_population']:raise ValueError('Incorrect model control '+control['case_id'])
   row={'case_id':control['case_id'],'model':model,'model_sha256':b.ir.digest(model),'status':'independently-evaluated-authored-model','theory_satisfied':theory,'required_population_satisfied':population,'clause_results':truths,'population_results':population_truths,'execution':'complete'}
  except v.VerificationFault as fault:
   if fault.code!=control['expected_error']:raise
   row={'case_id':control['case_id'],'model':model,'model_sha256':b.ir.digest(model),'status':'rejected-model-structure','code':fault.code,'theory_satisfied':None,'required_population_satisfied':None,'execution':'rejected'}
  results.append(row)
 prior=json.loads((b.BASE/'units/I03/delivery-manifest.json').read_bytes())
 for reference in prior['files']:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Changed earlier sealed delivery')
 for reference in context['sources']+bindings:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Closing selected-input/checker drift')
 b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Closing runtime drift')
 report={'schema_version':'definition-assurance-axiom-model-controls/v1-candidate','status':'PASS-for-authored-models-and-exact-static-clause-accounting','authority_effect':'none','semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending','whole_definition_translation':'pending','snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'interpretation_ref':b.ref(b.UNIT/'t.json'),'correspondence_ref':b.ref(b.UNIT/'correspondence.json'),'static_ir_ref':b.ref(b.UNIT/'static-ir.json'),'checker_bindings':bindings,'runtime_bindings':runtime,'source_units':len(packet['source_units']),'mapped_clauses':len(core['clauses']),'encoded_clause_ids':[row['clause_id'] for row in T],'required_population_ids':[pop['population_id'] for pop in I],'unresolved_population_ids':unresolved,'deferred_clause_ids':correspondence['unresolved_clauses'],'direct_semantic_dependencies':core['depends_on'],'findings':findings,'results':results,'control_count':len(results),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'claim_ceiling':'Exact authored hypothetical models evaluated against thirteen necessary static clauses and three selected required populations using independent E03 denotation. No provider enumeration, native finite-provider witness claim, completeness/exhaustion, actual-world truth, full semantic closure, owner acceptance or whole-definition proof.'}
 if write:b.put('model-controls.json',report)
 return report

def main():
 write='--write' in b.sys.argv;report=verify(write)
 if not write:
  stored=read('model-controls.json')
  if not b.r.same_json(stored,report):raise ValueError('Fresh independent model checks do not reproduce stored result')
 print(json.dumps({'result':report['status'],'controls':report['control_count'],'source_units':report['source_units'],'mapped_clauses':report['mapped_clauses'],'encoded_clauses':len(report['encoded_clause_ids']),'required_populations':len(report['required_population_ids']),'unresolved_populations':len(report['unresolved_population_ids']),'deferred_clauses':len(report['deferred_clause_ids']),'prior_candidate_files_preserved':report['prior_candidate_files_preserved'],'source_files_current':201,'semantic_ready':False,'whole_translation':'pending'},indent=2,sort_keys=True))
if __name__=='__main__':main()
