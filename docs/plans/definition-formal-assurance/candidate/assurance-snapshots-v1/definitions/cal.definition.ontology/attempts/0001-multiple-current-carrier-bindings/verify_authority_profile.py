"""Actual reference-carrier probes,pure captured posture observations and hypothetical ontology guards."""
import ast,copy,json,typing
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['typed_nodes','typed_edges','endpoint_closure','context_assignment','source_provenance','confidence_split','promotion_gate','contradiction_drift_route','use_guidance','branch_separation','shorthand_normalization','source_current']
def qualification(x):return ['missing-'+n for n in AXES if x['hypotheses'].get(n) is not True]+(['actual-authority-truth-or-use-claim'] if x['actual_claim'] else [])
def profiles():
 base={'hypotheses':{n:True for n in AXES},'actual_claim':False};rows=[]
 def add(name,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=qualification(x);assert bool(errors)==reject;rows.append({'profile_name':name,'input':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_meaning_truth_or_authority_verified':False,'source_fidelity_accepted':False})
 add('allowed-only-under-all-explicit-hypotheses',lambda x:None)
 for n in AXES:add('missing-'+n,lambda x,n=n:x['hypotheses'].update({n:False}),True)
 add('actual-authority-truth-or-use-claim',lambda x:x.update(actual_claim=True),True)
 return rows
def frame_errors(x):
 errors=[]
 if x['branch_claims_collapsed'] or x['system_evidence_redefines_intent'] or x['intent_implies_implementation']:errors.append('business-system-bridge-boundary')
 if x['ontology_owns_transition'] or x['self_promotion']:errors.append('authority-transition-owner-boundary')
 if x['operational_label_primitive'] or x['operational_label_peer_branch'] or x['operational_label_lifecycle_alias']:errors.append('shorthand-promoted')
 if x['has_meaning_obligation'] and not x['meaning_route']:errors.append('missing-meaning-route')
 if x['has_posture_obligation'] and not x['posture_route']:errors.append('missing-posture-route')
 if x['has_operation_obligation'] and not x['operation_named']:errors.append('unnamed-operation')
 if x['no_concrete_obligation'] and not x['retirement_required']:errors.append('empty-phrase-not-retired-in-wording-policy')
 if x['confidence_axes_collapsed'] or x['posture_implies_confidence']:errors.append('confidence-posture-boundary')
 if x['actual_claim']:errors.append('actual-claim-unproved')
 return errors
def frames():
 base={'branch_claims_collapsed':False,'system_evidence_redefines_intent':False,'intent_implies_implementation':False,'ontology_owns_transition':False,'self_promotion':False,'operational_label_primitive':False,'operational_label_peer_branch':False,'operational_label_lifecycle_alias':False,'has_meaning_obligation':True,'meaning_route':True,'has_posture_obligation':True,'posture_route':True,'has_operation_obligation':True,'operation_named':True,'no_concrete_obligation':False,'retirement_required':False,'confidence_axes_collapsed':False,'posture_implies_confidence':False,'actual_claim':False};rows=[]
 def add(name,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=frame_errors(x);assert bool(errors)==reject,(name,errors);rows.append({'frame_name':name,'input':x,'errors':errors,'expected_rejection':reject,'universal_behavior_or_normalization_proof':False,'actual_runtime_execution':False})
 add('typed-meaning-posture-operation-routes-kept-separate',lambda x:None)
 for n in ['branch_claims_collapsed','system_evidence_redefines_intent','intent_implies_implementation','ontology_owns_transition','self_promotion','operational_label_primitive','operational_label_peer_branch','operational_label_lifecycle_alias','confidence_axes_collapsed','posture_implies_confidence','actual_claim']:add(n,lambda x,n=n:x.update({n:True}),True)
 for n in ['meaning_route','posture_route','operation_named']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('empty-phrase-retirement-required',lambda x:x.update(no_concrete_obligation=True,retirement_required=True))
 add('empty-phrase-without-retirement-requirement',lambda x:x.update(no_concrete_obligation=True),True)
 add('no-operation-obligation-no-implicit-operation',lambda x:x.update(has_operation_obligation=False,operation_named=False))
 add('unknown-confidence-recorded-without-calibration-claim',lambda x:None)
 return rows
def extract(raw,path,names,ns):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in selected}==set(names);exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns);return ns

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='ontology');pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','derived_runtime':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/graph.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-Ontology-Definition-carrier',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.ontology/v1'] and len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]))
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-valid',not list(validator.iter_errors(fixture)));ck('bound-generator-validator-digests-current',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'])
 renderer=extract(raw['generator'],paths['generator'],['render_artifact','render_instance'],{'json':json,'Any':typing.Any});before=copy.deepcopy(fixture);ck('two-fixture-renders-exact',renderer['render_instance'](artifact,fixture).encode()==renderer['render_instance'](artifact,fixture).encode()==raw['fixture_projection']);ck('artifact-projection-exact',renderer['render_artifact'](artifact).encode()==raw['artifact_projection']);ck('renderer-preserves-input',fixture==before)
 ck('closed-reference-manifest-not-inline-typed-graph',schema['additionalProperties'] is False and set(schema['required'])==set(schema['properties']) and all(schema['properties'][n]['items']['type']=='string' for n in ['node_refs','relation_refs','provenance_refs','branch_refs','role_assignment_refs']))
 code=raw['validator'].decode();tree=ast.parse(code);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');body=ast.get_source_segment(code,fn);ck('generic-validator-source-inspected-no-Ontology-reference-resolution',all(n not in body for n in ['node_refs','relation_refs','confidence_policy_ref','branch_refs','promotion_state']) and 'dump(root/"receipts/validation.json",receipt)' in body)
 native=raw['native_runtime'].decode();ck('native-semantic-governance-split-inspected',all(n in native for n in ['pub struct OntologyNodeSemanticState','pub struct OntologyRelationSemanticState','pub struct OntologyGovernanceState','pub semantic_definition_refs: Vec<DefinitionReference>','pub complete_resulting_semantic_state: OntologySemanticState','pub complete_resulting_governance_state: OntologyGovernanceState']))
 ck('native-selected-empty-profile-validation-inspected',all(n in native for n in ['fn validate_semantic_state','SEMANTIC_DEFINITION_REFS_EMPTY','PROFILE_REF_INVALID','test-empty-profile/v1','UNTYPED_RESIDUE','only the selected closed empty profile is admitted']))
 derived=raw['derived_runtime'].decode();ck('derived-query-currentness-limit-and-effect-boundaries-inspected',all(n in derived for n in ['def posture(entry)','def build(data)','def query(data','stale-source-envelope','graph["edges"] = []','"authority_effect": "none"','"replay_source": False','max_nodes <= 1000','max_edges <= 4000']))
 es=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not es,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in es],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-shape-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   es=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(es),'errors':es})
 ck('four-hostile-fixtures-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles));probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);es=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not es)==accept,(id,es);probes.append({'case_id':id,'record':x,'schema_accepted':not es,'expected_schema_acceptance':accept,'errors':es,'actual_meaning_evidence_confidence_authority_or_use_verified':False})
 probe('unresolved-node-relations-provenance-confidence',lambda x:x.update(node_refs=['absent:node'],relation_refs=['absent:relation'],provenance_refs=['absent:source'],confidence_policy_ref='absent:policy'),True)
 probe('fixture-provenance-reference-path-absent-not-resolved',lambda x:None,True)
 probe('same-string-node-and-relation-reference',lambda x:x.update(relation_refs=[x['node_refs'][0]]),True)
 probe('empty-branches-and-role-assignments',lambda x:x.update(branch_refs=[],role_assignment_refs=[]),True)
 probe('unregistered-edge-kind-reference',lambda x:x.update(relation_refs=['unregistered:kind']),True)
 probe('confidence-policy-without-evidence-commitment-values',lambda x:None,True)
 probe('opaque-version-and-scope',lambda x:x.update(ontology_version='unknown',scope_ref='unresolved:scope'),True)
 probe('contradictions-drift-or-use-guidance-not-structured',lambda x:x.update(governance_rules=['No specific route or use rule is given.']),True)
 probe('permission-sounding-governance-text',lambda x:x.update(governance_rules=['This ontology can promote every definition.']),True)
 probe('operational-ontology-name-does-not-normalize-it',lambda x:x.update(name='Operational Ontology'),True)
 probe('collapsed-business-system-bridge-branch-label',lambda x:x.update(branch_refs=['branch:everything']),True)
 probe('missing-real-world-evidence-and-membership',lambda x:x.update(node_refs=['ontology:itself'],relation_refs=['ontology:itself']),True)
 probe('same-id-revised-manifest-no-successor',lambda x:x.update(ontology_version='v2',successor_refs=[]),True)
 probe('empty-successor-refs',lambda x:x.update(successor_refs=[]),True)
 probe('permission-sounding-claim-ceiling',lambda x:x.update(claim_ceiling='All runtime and authority claims are true.'),True)
 for val in ['draft','review','admitted','superseded','retired']:probe('carrier-state-'+val,lambda x,val=val:x.update(promotion_state=val),True)
 for n in ['node_refs','relation_refs','provenance_refs','boundaries','governance_rules']:probe('empty-'+n,lambda x,n=n:x.update({n:[]}),False)
 for n in ['confidence_policy_ref','promotion_state','ontology_version','scope_ref','challenge_route']:probe('missing-'+n,lambda x,n=n:x.pop(n),False)
 for val in ['', '   ']:probe('blank-version-'+repr(val),lambda x,val=val:x.update(ontology_version=val),False)
 probe('duplicate-node-reference',lambda x:x['node_refs'].append(x['node_refs'][0]),False)
 probe('too-many-node-refs',lambda x:x.update(node_refs=[str(i) for i in range(101)]),False)
 probe('inline-node-in-reference-array',lambda x:x.update(node_refs=[{'id':'n1','type':'node','content':'meaning'}]),False)
 for n in ['evidence_confidence','commitment_confidence','next_gate_ref','use_obligations','implicit_admission','derived_authority']:probe('unsupported-extra-'+n,lambda x,n=n:x.update({n:'hyp:claim'}),False)
 for val in ['candidate','reviewed','promoted','demoted','deferred']:probe('source-state-without-accepted-carrier-map-'+val,lambda x,val=val:x.update(promotion_state=val),False)
 probe('authority-effect-admitted',lambda x:x.update(authority_effect='admitted'),False)
 probe('status-admitted',lambda x:x.update(status='admitted'),False)
 probe('wrong-kind',lambda x:x.update(kind='inventory'),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 # Extract only the source-bound pure posture function; do not import runtime/store/operations.
 posture=extract(raw['derived_runtime'],paths['derived_runtime'],['posture'],{})['posture'];doc=b.co.source_document(snap,source);entry={'identity':source['definition_id'],'version_ref':source['version_ref'],'category':'definition','kind':doc['classification']['semantic_kind'],'source':{'path':source['path'],'sha256':source['sha256'],'selector':'whole-file'},'decision_ref':'CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION','effective_state':'admitted-current','record':doc};posture_controls=[]
 def observe(id,change,accept=True):
  x=copy.deepcopy(entry);change(x);before=copy.deepcopy(x);err=None
  try:result=posture(x);actual=True
  except (KeyError,TypeError) as ex:result=None;err=type(ex).__name__;actual=False
  assert actual==accept,(id,err);assert x==before;posture_controls.append({'case_id':id,'input':x,'pure_posture_returned':actual,'expected_return':accept,'result':result,'error':err,'input_preserved':True,'actual_runtime_execution':False,'actual_axis_authentication_or_authority_created':False})
 observe('captured-admitted-Definition-entry-default-confidence-unobserved-runtime',lambda x:None)
 observe('arbitrary-confidence-value-passed-through',lambda x:x['record'].update(evidence_confidence='perfect'))
 observe('arbitrary-commitment-passed-through',lambda x:x['record'].update(commitment='fully-deployed'))
 observe('modified-classification-does-not-recompute-entry-kind',lambda x:x['record']['classification'].update(semantic_kind='operational-ontology'))
 observe('owner-ref-string-passed-through',lambda x:x['record'].update(owner_ref='owner:all-authority'))
 observe('source-digest-string-not-authenticated-here',lambda x:x['source'].update(sha256='0'*64))
 observe('arbitrary-status-becomes-domain-track',lambda x:x['record'].update(status='admitted'))
 observe('candidate-entry-status-remains-source-reported',lambda x:x.update(effective_state='candidate-unadmitted'))
 observe('promotion-looking-record-text-not-gate-proof',lambda x:x['record'].update(promotion_state='promoted'))
 observe('empty-record-does-not-prove-ontology',lambda x:x.update(record={}))
 observe('governance-rules-content-not-verified',lambda x:x['record'].update(governance_rules=['All meanings are true.']))
 observe('branch-and-reference-closure-not-evaluated',lambda x:x['record'].update(node_refs=['absent:node'],relation_refs=['absent:edge'],branch_refs=['branch:all']))
 observe('missing-required-identity-rejected',lambda x:x.pop('identity'),False)
 observe('missing-required-record-rejected',lambda x:x.pop('record'),False)
 report={'schema_version':'definition-assurance-Ontology-profile-checks/v1-candidate','status':'PASS-for-selected-carrier-posture-probes-and-hypothetical-ontology-guards','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py')],'runtime_bindings':runtime,'selected_inputs':refs,'actual_checks':checks,'actual_check_count':len(checks),'profiles':profiles(),'finite_ontology_frames':frames(),'schema_probes':probes,'negative_fixture_checks':hostiles,'pure_derived_posture_controls':posture_controls,'historical_source_current_definition_shape':shape,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_registry_selection':row,'exact_definition_binding':binding[0],'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'carrier_schema_ref':artifact['schema_ref'],'fixture_kind':fixture['kind'],'fixture_status':fixture['status'],'fixture_promotion_state':fixture['promotion_state'],'fixture_contains_absent_provenance_path':any(not (b.ROOT/path).exists() for path in fixture['provenance_refs']),'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'only_pure_generator_functions_and_posture_executed':True,'generator_module_or_materialization_writer_executed':False,'native_runtime_source_inspected':True,'native_runtime_executed':False,'derived_build_or_query_or_store_executed':False,'actual_runtime_execution':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Read-only current reference-manifest/schema/projection observations and pure captured posture function. Hypothetical qualification/normalization/branch/confidence frames are not universal proof. Derived posture trusts caller-reported axes,does not resolve references or confidence;native event structures remain separate. No real ontology truth,confidence calibration,promotion,actionable use,replay or runtime activation.'}
 b.unchanged(context['sources']+list(refs.values()));b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile checks differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'actual_checks':len(x['actual_checks']),'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_ontology_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_ontology_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'pure_posture_controls':len(x['pure_derived_posture_controls']),'pure_posture_returns':sum(y['pure_posture_returned'] for y in x['pure_derived_posture_controls']),'actual_runtime_execution':False},indent=2))
if __name__=='__main__':main()
