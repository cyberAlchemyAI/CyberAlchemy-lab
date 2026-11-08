"""Fresh actual-profile checks behind the independently derived bundle policy."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import time
import bundle_contract as b
v=b.v;s=b.s;i=b.i;g=b.g;d=i.c.d
sys.path.insert(0,str(s.BASE/'evolution/preservation'))
import projection as p
sys.path.insert(0,str(s.BASE/'coverage/carrier'))
from check_coverage import table

BODIES={'invariant-preservation':'Registry.Evolution.audited_preservation',
 'conservative-expansion':'Registry.Models.audited_conservativity',
 'protected-root-independence':'Relational.Logic.admission_roots_do_not_change_instance_meaning',
 'typed-rule-profile':'Inference.Captured.theory_valid',
 'derivation-soundness':'Inference.audited_derivation_soundness',
 'closure-adequacy':'Inference.audited_closure_adequacy',
 'protected-lineage':'Inference.audited_protected_lineage',
 'rule-extension-compatibility':'Inference.Extension.audited_rule_conservativity'}
CONCRETE={'typed-rule-profile':'Inference.TheoryValid Inference.Captured.theory',
 'protected-root-independence':'∀ (g : Relational.Graph) (roots : List Relational.AdmissionRoot) (e : Relational.Assertion), Relational.InstanceValid (Relational.Logic.withAdmissionRoots g roots) e ↔ Relational.InstanceValid g e'}


def compile_carrier(proposal):
 carrier=g.carrier(proposal)
 for branch in carrier['allOf']:
  payload=branch['then']['properties']['payload']
  if not payload['oneOf']:
   # JSON Schema forbids an empty oneOf array. One false schema has exactly
   # the required empty denotation, while retaining the declaration's fields.
   payload['oneOf']=[False]
 g.c.jsonschema.Draft202012Validator.check_schema(carrier)
 return carrier


def carrier_table(carrier):
 # Adapt the accepted predecessor's structural reader for the valid false
 # sentinel. Only this inspection copy uses an empty alternatives list.
 inspection=deepcopy(carrier)
 for branch in inspection['allOf']:
  payload=branch['then']['properties']['payload']
  if payload['oneOf']==[False]:payload['oneOf']=[]
 return table(inspection)


def compile_registry(build,modules):
 # The captured declaration modules retain their exact accepted sources. Some
 # large finite decidability proofs need more than the predecessor's 60 seconds
 # on a loaded host. This bounded local runner changes scheduling, not proofs.
 lean=s.lean_path();logs=[]
 for name,source in modules:
  target=build/(name+'.lean');target.write_bytes(Path(source).read_bytes())
  started=time.monotonic()
  result=subprocess.run([str(lean),'-j1','-o',str(target.with_suffix('.olean')),str(target)],
   cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=180)
  output=result.stdout+result.stderr
  s.require(result.returncode==0 and 'warning:' not in output,'Lean registry module failed: '+name+'\n'+output)
  logs.append({'module':name,'source':s.binding(source),'olean_sha256':s.digest(target.with_suffix('.olean')),
   'output':output,'elapsed_seconds':time.monotonic()-started,'timeout_seconds':180,'workers':1})
 return logs


def compile_registry_generated(build,name,source):
 audit=i.c.c.policy()
 s.require(audit.source_policy(source),'forbidden proof bypass in generated registry module: '+name)
 path=build/(name+'.lean');path.write_text(source)
 started=time.monotonic()
 result=subprocess.run([str(s.lean_path()),'-j1','-o',str(path.with_suffix('.olean')),str(path)],
  cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=180)
 output=result.stdout+result.stderr
 s.require(result.returncode==0 and 'warning:' not in output,'registry kernel replay failed: '+name+'\n'+output)
 s.require(audit.policy_accepts(output),'registry replay contains an unapproved axiom')
 return {'module':name,'generated_source_sha256':s.digest(path),'olean_sha256':s.digest(path.with_suffix('.olean')),
  'output':output,'axioms':audit.axiom_report(output),'elapsed_seconds':time.monotonic()-started,
  'timeout_seconds':180,'workers':1}


def structural_graph_valid(registry,graph):
 nodes={};ids=set();definitions={k['id']:k for k in registry['kinds']}
 for node in graph['nodes']:
  key=g.c.r.key(node['ref'])
  if key in nodes or node['kind'] not in registry['node_kinds'] or not node['content_identity']:return False
  nodes[key]=node
 for edge in graph['assertions']:
  if not edge['id'] or edge['id'] in ids:return False
  ids.add(edge['id']);decl=definitions.get(edge['kind'])
  source=nodes.get(g.c.r.key(edge['source']));target=nodes.get(g.c.r.key(edge['target']))
  if decl is None or source is None or target is None:return False
  if edge['kind_version']!=decl['version'] or {'source_kind':source['kind'],'target_kind':target['kind']} not in decl['pairs']:return False
  if set(edge['qualifiers'])!=set(decl['fields']) or not all(isinstance(q,str) and q for q in edge['qualifiers'].values()):return False
 return True


def registry_source(proposal):
 old=proposal['before']['registry'];new=proposal['after']['registry'];added=new['kinds'][len(old['kinds']):]
 text='import RegistrySnapshot\nimport Preservation\nimport ConservativeExpansion\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Bundle\n'
 text+='def added : List Kind := '+d.rows(added,p.kind_lean)+'\n'
 text+='def expanded : Theory := Models.expandedTheory Snapshot.captured added\n'
 text+='theorem added_valid : ∀ k ∈ added, KindValid Snapshot.captured.nodeKinds k := by decide\n'
 text+='theorem expanded_valid : TheoryValid expanded := by\n  refine ⟨Snapshot.valid_snapshot.1, Snapshot.valid_snapshot.2.1, by decide, ?_⟩\n  intro k hk\n  change k ∈ Snapshot.captured.kinds ++ added at hk\n  rcases List.mem_append.mp hk with old | fresh\n  · exact Snapshot.valid_snapshot.2.2.2 k old\n  · exact added_valid k fresh\n'
 text+='def extension : Evolution.FreshExtension Snapshot.captured expanded := { added := added, nodes_equal := rfl, kinds_append := rfl, fresh_ids := by decide, base_valid := Snapshot.valid_snapshot, expanded_valid := expanded_valid }\n'
 text+='theorem actual_preservation : ∀ graph, Evolution.OldLanguage Snapshot.captured graph → (Inv expanded graph ↔ Inv Snapshot.captured graph) := Evolution.preserves_old_language extension\n'
 text+='theorem actual_conservativity : ∀ model, Inv Snapshot.captured model → ∃ expansion, Inv expanded expansion ∧ Models.oldReduct Snapshot.captured expansion = model := Models.expands_every_base_model Snapshot.captured added expanded_valid\n'
 text+='abbrev DataValid (r : Theory) (g : Graph) : Prop := (g.nodes.map Node.ref).Nodup ∧ (∀ n ∈ g.nodes, n.ref.id ≠ "" ∧ n.ref.version ≠ "" ∧ n.contentIdentity ≠ "" ∧ n.kind ∈ r.nodeKinds) ∧ (g.assertions.map Assertion.id).Nodup ∧ ∀ e ∈ g.assertions, InstanceValid r g e\n'
 text+='instance (r : Theory) (g : Graph) : Decidable (DataValid r g) := by unfold DataValid; infer_instance\n'
 for label,stage,theory in [('before','before','Snapshot.captured'),('after','after','expanded')]:
  graph=proposal[stage]['graph'];accepted=structural_graph_valid(proposal[stage]['registry'],graph)
  text+='def '+label+'Graph : Graph := '+p.graph_lean(graph)+'\n'
  if accepted:
   text+='theorem '+label+'_valid : Inv '+theory+' '+label+'Graph := by\n  exact ⟨'+('Snapshot.valid_snapshot' if stage=='before' else 'expanded_valid')+', by decide, by decide, by decide, by decide⟩\n'
   text+='theorem '+label+'_result : checkGraph '+theory+' '+label+'Graph = true := (graph_checker_iff _ _).mpr '+label+'_valid\n'
  else:
   text+='theorem '+label+'_data_invalid : ¬ DataValid '+theory+' '+label+'Graph := by decide\n'
   text+='theorem '+label+'_invalid : ¬ Inv '+theory+' '+label+'Graph := fun h => '+label+'_data_invalid h.2\n'
   text+='theorem '+label+'_result : checkGraph '+theory+' '+label+'Graph = false := by simp [checkGraph, '+label+'_invalid]\n'
  text+='#print axioms '+label+'_result\n'
 text+='#print axioms actual_preservation\n#print axioms actual_conservativity\nend Registry.Bundle\n'
 return text


def project_f0(graph):
 # Exact supported-edge projection; structural checking covers the full graph.
 # Independently supplied root truth stays in the reference audit, not inference.
 selected=deepcopy(graph);selected['assertions']=[e for e in selected['assertions'] if e['kind'] in g.c.r.SUPPORTED]
 tokens={e['qualifiers'].get('conformance_evidence_refs',e['qualifiers'].get('application_receipt_ref')) for e in selected['assertions']}
 selected['assessments']=[a for a in selected['assessments'] if a['ref'] in tokens]
 needed={g.c.r.key(e[side]) for e in selected['assertions'] for side in ['source','target']}
 needed.update(g.c.r.key(a[side]) for a in selected['assessments'] for side in ['subject','target'])
 selected['nodes']=[n for n in selected['nodes'] if g.c.r.key(n['ref']) in needed]
 s.require(all(n['kind'] in d.NODE_KINDS for n in selected['nodes']),'unsupported F0 endpoint interpretation')
 selected['admission_roots']=[]
 for edge in selected['assertions']:edge.pop('kind_version')
 return {'schema_version':'relational-checker.normal-form/v1','graph':selected}


class Replay:
 def __init__(self,proposal,build,output):
  self.proposal=deepcopy(proposal);self.build=Path(build);self.output=Path(output)
  self.required=g.generate(proposal);self.classification=self.required['classification']
  self.captured=i.capture(proposal) if self.classification['rule_change'] else None
  self.logs=[];self.owned_bindings=[];self.registry_ready=False;self.registry_modules_ready=False;self.core_ready=False;self.rule_cache={}
  self.write('captured-proposal.json',proposal)

 def write(self,name,value):
  path=self.output/name;s.write(path,value);binding=s.binding(path);self.owned_bindings.append(binding);return binding

 def persist_source(self,module,label=None):
  path=self.output/((label or module)+'.lean');path.write_bytes((self.build/(module+'.lean')).read_bytes())
  binding=s.binding(path);self.owned_bindings.append(binding);return binding

 def audit_generated(self):
  # Check the verifier's own registered outputs, not arbitrary user data that
  # happens to contain path/hash-looking fields. Earlier evidence stays bound.
  for binding in self.owned_bindings:v.safe_binding(binding,limit=64*1024*1024)

 def core(self):
  if not self.core_ready:
   self.logs+=v.prepare(self.proposal,self.build)
   self.logs+=s.compile_lean(self.build,[(name,path) for name,path in d.core_modules() if name not in {'RelationalInput','RelationalSemantics'}])
   self.core_ready=True

 def registry(self):
  self.core()
  if not self.registry_ready:
   modules=[(name,path) for name,path in p.captured_modules() if name not in {'RelationalInput','RegistryChecker'}]
   if not self.registry_modules_ready:
    self.logs+=compile_registry(self.build,modules);self.registry_modules_ready=True
   self.logs.append(compile_registry_generated(self.build,'BundleRegistry',registry_source(self.proposal)))
   self.registry_ready=True
  return self.persist_source('BundleRegistry')

 def references(self,stage):
  result=g.c.r.resolve(self.proposal[stage]['graph'],self.proposal[stage]['registry'])
  added=set(self.classification['added_kind_ids'])
  unknown=[row for row in result['unsupported'] if row['relation_kind'] not in added]
  return result,unknown

 def generic(self,name,entry,loaded):
  if entry['method']=='proof-submission':
   result=v.check(self.proposal,loaded['proof-submission'])
   return result.get('accepted',False),result
  self.core();descriptor=v.CATALOG[name]
  target=descriptor[1] if descriptor[2]=='definition-value' else CONCRETE[name]
  source='import '+descriptor[0]+'\ntheorem submitted : '+target+' := '+BODIES[name]+'\n'
  result=v.audit_text(source,self.build,descriptor)
  result['generated_proof_source']=source
  return result['accepted'],result

 def rule_checks(self):
  self.core()
  if not self.rule_cache:
   captured=self.captured;after=captured['after_input'];normal=captured['after_normal']
   query={'predicate':'Admitted','version':'v1','terms':[after['facts'][0]['terms'][0],*after['domain'][-3:]]}
   computed=i.c.compute(after)
   if computed['status']!='candidate-complete':
    self.rule_cache={'unknown':computed};return self.rule_cache
   closure=deepcopy(computed['bundle']);closure['negative_query']=query
   checked=i.c.check(after,closure,self.build)
   lineage=i.lineage.check(after,query,self.build)
   conservative=i.conservativity_source(captured)
   log=i.c.c.compile_generated(self.build,'CapturedRuleConservativity',conservative);self.logs.append(log)
   self.rule_cache={'closure':checked,'closure_bundle':closure,'lineage':lineage,'query':query,
    'conservativity':log,'normal':normal,'after':after,
    'sources':[self.persist_source(m) for m in ['ClosureQuery','LineageQuery','CapturedRuleConservativity','InferenceFixture']]}
  return self.rule_cache

 def model(self,name,entry,loaded):
  if self.captured:
   rule=self.rule_checks()
   if 'unknown' in rule:return None,rule
   expected={'kind':'model-existence'} if name=='inhabited-model' else {'kind':'non-entailment','premise':rule['after']['facts'][0],'conclusion':rule['query']}
   witness=loaded['model-witness']['witness'] if entry['method']=='checked-model-witness' else {
    'schema':'relational.inference-model/v1','normal_form_identity':rule['normal']['normal_form_identity'],
    'model':deepcopy(rule['closure_bundle']['closure']),'claim':expected}
   normalized=i.w.normalize_witness(rule['normal'],witness)
   if name=='independence-witnesses':
    s.require(normalized['premise']==i.c.c.captured_atom(rule['normal'],expected['premise']) and normalized['conclusion']==i.c.c.captured_atom(rule['normal'],expected['conclusion']),'countermodel weakens or changes independently required ground implication')
   result=i.w.check(rule['after'],witness,self.build)
   result['required_claim']=expected;result['witness']=witness;result['source']=self.persist_source('ModelQuery',name+'-ModelQuery')
   return result['accepted'] and (name!='independence-witnesses' or result['non_entailment_proved']),result
  self.registry()
  witness=loaded['model-witness']['witness'] if entry['method']=='checked-model-witness' else {'proposal_identity':g.c.identity(self.proposal),'graph':self.proposal['before']['graph'],'claim':{'kind':'model-existence'}}
  s.require(set(witness)=={'proposal_identity','graph','claim'} and witness['claim']=={'kind':'model-existence'},'unsupported registry witness statement')
  reference,unknown=g.c.r.resolve(witness['graph'],self.proposal['after']['registry']),[]
  added=set(self.classification['added_kind_ids'])
  unknown=[x for x in reference['unsupported'] if x['relation_kind'] not in added]
  if unknown:return None,{'status':'unsupported','unsupported':unknown}
  accepted=structural_graph_valid(self.proposal['after']['registry'],witness['graph']) and bool(witness['graph']['nodes']) and bool(witness['graph']['assertions'])
  source='import BundleRegistry\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Registry Registry.Bundle\ndef witness : Graph := '+p.graph_lean(witness['graph'])+'\n'
  if accepted:
   source+='theorem checked_model : Inv expanded witness ∧ witness.nodes ≠ [] ∧ witness.assertions ≠ [] := by\n  exact ⟨⟨expanded_valid, by decide, by decide, by decide, by decide⟩, by decide, by decide⟩\n#print axioms checked_model\n'
  else:
   source+='theorem rejected_model : ¬ (DataValid expanded witness ∧ witness.nodes ≠ [] ∧ witness.assertions ≠ []) := by decide\n#print axioms rejected_model\n'
  log=compile_registry_generated(self.build,'BundleModel',source);self.logs.append(log)
  return accepted and not reference['errors'],{'accepted':accepted and not reference['errors'],'kernel_result':log,'reference_validation':reference,'witness':witness,'source':self.persist_source('BundleModel')}

 def execute(self,name,entry,loaded):
  if entry['method']=='bounded-search':
   return 'unknown','bounded-search',{'execution':'completed','provider_document':loaded['search-result'],
    'reason':'Untrusted search output supplies no checked witness and cannot discharge a hard obligation.'}
  if name=='baseline-current':return 'satisfied','verified-checker',{'baseline_identity':self.proposal['baseline_identity'],'verified_by':'complete independently recomputed dependency manifest'}
  if name=='computed-classification':return 'satisfied','verified-checker',self.classification
  if name=='source-profile-projection':
   result=g.source_projection(self.proposal)
   for stage in ['before','after']:
    reference,unknown=self.references(stage)
    if unknown:return 'unsupported','none',{'unsupported_source_meanings':unknown,'stage':stage}
   if self.captured:result['captured_rule_profile']=self.captured
   return 'satisfied','verified-checker',result
  if name=='carrier-projection':
   carrier=compile_carrier(self.proposal);actual=carrier_table(carrier)
   for row in self.proposal['after']['registry']['kinds']:
    s.require(actual[row['id']]['pairs']==row['pairs'] and actual[row['id']]['qualifiers']['required']==row['fields'] and set(actual[row['id']]['qualifiers']['properties'])==set(row['fields']) and actual[row['id']]['qualifiers']['additionalProperties'] is False,'carrier declaration mismatch')
   return 'satisfied','verified-checker',{'carrier_identity':g.c.identity(carrier),'kind_count':len(actual),'ordered_pairs':sum(len(r['pairs']) for r in actual.values()),'schema_validated':True,'source':self.write('compiled-carrier-schema.json',carrier)}
  if name=='selected-data-compatibility':
   source=self.registry();results={};accepted=True
   for stage in ['before','after']:
    reference,unknown=self.references(stage)
    if unknown:return 'unsupported','none',{'unsupported':unknown,'stage':stage}
    structural=structural_graph_valid(self.proposal[stage]['registry'],self.proposal[stage]['graph'])
    kernel=d.check(project_f0(self.proposal[stage]['graph']),self.build) if structural and not reference['errors'] else {'accepted_result':False,'reason':'Typed structural/reference checks failed before F0 projection.'}
    results[stage]={'reference':reference,'registry_valid':structural,'F0_projection':kernel}
    accepted=accepted and structural and not reference['errors'] and kernel['accepted_result']
   return ('satisfied' if accepted else 'violated'),'verified-checker',{'stages':results,'source':source,'claim_ceiling':'Full closed-string structural graph plus exact supported F0 edge/reference projection; no full-source-wide semantics.'}
  if name in b.WITNESS_TARGETS:
   accepted,result=self.model(name,entry,loaded)
   return ('unknown' if accepted is None else 'satisfied' if accepted else 'violated'),'checked-model-witness',result
  accepted,proof=self.generic(name,entry,loaded)
  if not accepted:return 'violated','none',proof
  extra={}
  if name in {'invariant-preservation','conservative-expansion'}:
   extra['actual_registry_instantiation']=self.registry()
  if name in {'closure-adequacy','protected-lineage','rule-extension-compatibility'}:
   rule=self.rule_checks()
   if 'unknown' in rule:return 'unknown','none',rule
   extra['actual_inference_sources']=rule['sources']
   if name=='closure-adequacy' and not rule['closure']['accepted']:return 'violated','none',rule['closure']
   if name=='protected-lineage' and not rule['lineage']['accepted']:return 'violated','none',rule['lineage']
  if name=='typed-rule-profile':extra['normal_form_identity']=self.captured['after_normal']['normal_form_identity']
  return 'satisfied','kernel-proof',{'exact_proof':proof,**extra}
