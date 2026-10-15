#!/usr/bin/env python3
"""Author candidate Lab protocol schemas; never mutate admitted contracts or runtime state."""
import copy,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREFIX='urn:cyberalchemy-lab:protocol:'
DRAFT='https://json-schema.org/draft/2020-12/schema'
S={'type':'string','minLength':1}; H={'type':'string','pattern':'^[a-f0-9]{64}$'}
N={'type':'integer','minimum':0}; B={'type':'boolean'}; DT={'type':'string','format':'date-time'}
NULL={'type':'null'}
CAT=['artifact-instance','typed-relation','definition','artifact-type','relation-kind']

def obj(p,required=None):return {'type':'object','additionalProperties':False,'properties':p,'required':list(p) if required is None else required}
def arr(p,minimum=0,unique=False):return {'type':'array','items':p,'minItems':minimum,**({'uniqueItems':True} if unique else {})}
def enum(*values):return {'enum':list(values)}
def nullable(p):return {'anyOf':[p,NULL]}
def ref(name):return {'$ref':PREFIX+name+':v1-candidate'}
def common(name):return {'$ref':PREFIX+'common:v1-candidate#/$defs/'+name}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def main():
 registry_path=ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
 registry=json.loads(registry_path.read_text())
 coverage=json.loads((ROOT/'docs/plans/0009-lab-integrated-roadmap/contract-coverage.json').read_text())
 entries=registry['admitted_contracts']; current=set(registry['current_by_identity'].values())
 schemas={}; catalog=[]; sources={}; domain_bindings=[]
 def source(p):
  p=p if p.is_absolute() else ROOT/p
  sources[str(p.relative_to(ROOT))]={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size}
  return sha(p)
 source(registry_path);source(ROOT/'docs/plans/0009-lab-integrated-roadmap/contract-coverage.json')
 for e in entries:
  sp=ROOT/e['schema_path'];dp=ROOT/e['artifact_path']
  if sha(sp)!=e['schema_sha256'] or sha(dp)!=e['artifact_sha256']:raise ValueError('registered contract drift: '+e['artifact_type_ref'])
  digest=source(sp);source(dp)
  domain_bindings.append({'carrier_ref':e['artifact_type_ref'],'schema_path':e['schema_path'],'schema_sha256':digest,'schema_selector':e.get('schema_selector'),
   'schema_resource_uri':'urn:cyberalchemy-lab:bound-schema:'+digest,'descriptor_path':e['artifact_path'],'descriptor_sha256':e['artifact_sha256'],
   'semantic_kind':e['semantic_kind'],'discriminator':e.get('instance_discriminator'),
   'write_posture':'current' if e['artifact_type_ref'] in current else 'historical-read-only','admission_decision_ref':e['admission_decision_ref']})
 # Legacy wrappers use repository-relative refs despite URL ids. Pin an explicit
 # offline compatibility mapping rather than dereferencing cyberalchemy.local.
 dependency_bindings=[]; pending=[ROOT/e['schema_path'] for e in domain_bindings];seen=set()
 while pending:
  parent=pending.pop()
  if parent in seen:continue
  seen.add(parent)
  def dependencies(v):
   if isinstance(v,dict):
    for k,x in v.items():
     if k=='$ref' and not x.startswith(('#','urn:','https:','http:','file:')):
      target=(parent.parent/x.split('#')[0]).resolve()
      if not target.is_relative_to(ROOT):raise ValueError('schema ref escapes repository')
      digest=source(target);pending.append(target)
      dependency_bindings.append({'source_path':str(parent.relative_to(ROOT)),'source_ref':x,'target_path':str(target.relative_to(ROOT)),'target_sha256':digest,'resolution':'explicit-repository-file-compatibility-binding'})
     else:dependencies(x)
   elif isinstance(v,list):
    for x in v:dependencies(x)
  dependencies(json.loads(parent.read_text()))
 dump(HERE/'schema-dependencies.json',{'schema_version':'lab-schema-dependencies/v1-candidate','authority_effect':'none','bindings':sorted(dependency_bindings,key=lambda x:(x['source_path'],x['source_ref']))})
 carrier_refs=[e['artifact_type_ref'] for e in entries]
 storage=[]
 for p in sorted((ROOT/'docs/proposals/0006-lab-artifact-storage/schemas').glob('*.schema.json')):
  value=json.loads(p.read_text());source(p)
  storage.append({'name':p.stem.replace('.schema',''),'path':str(p.relative_to(ROOT)),'resource_uri':value['$id'],'sha256':sha(p),'posture':'candidate-reused'})
 source(ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/sqlite-read-model.sql')
 memory_path=ROOT/'authority/artifact-types/candidates/0012-definition-complete-carrier-materialization/runtime/session-memory.schema.json'
 memory_digest=source(memory_path)
 legacy=[]
 for p in sorted((ROOT/'implementation/lab-runtime/v2/schemas').glob('*.schema.json')):
  legacy.append({'path':str(p.relative_to(ROOT)),'sha256':source(p),'posture':'existing-local-runtime-protocol-not-general-authority'})
 for p in [ROOT/'implementation/lab-runtime/v2/lab_runtime/operations.py',ROOT/'implementation/lab-runtime/v2/lab_runtime/store.py',ROOT/'implementation/lab-runtime/v2/lab_runtime/sources.py',ROOT/'implementation/lab-runtime/v2/lab_runtime/session.py',
 ROOT/'implementation/lab-runtime/v1/receipts/validation.json',ROOT/'implementation/lab-runtime/v2/receipts/validation.json',ROOT/'authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json',ROOT/'docs/plans/0009-lab-integrated-roadmap/dag.json',ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json']:
  source(p)
 for r in coverage['relations']:source(ROOT/r['source_path'])
 defs={
 'digest':H,'text':S,'time':DT,'nonnegative_integer':N,
 'binding':obj({'ref':S,'sha256':H}),
 'artifact_ref':obj({'scope_ref':S,'identity_ref':S,'version_ref':S,'carrier_ref':enum(*carrier_refs),'byte_sha256':H}),
 'source_cut':{'$ref':next(x['resource_uri'] for x in storage if x['name']=='artifact-package-manifest')+'#/properties/source_cut'},
 'actor':obj({'principal_ref':S,'role_assignment_refs':arr(obj({'ref':S,'sha256':H})),'agent_instance_ref':nullable(S),'session_ref':nullable(S),'assignment_ref':nullable(S)}),
 'budget':obj({'max_actions':N,'max_input_bytes':N,'max_output_bytes':N,'deadline':DT}),
 'authority_basis':obj({'authority_scope':enum('repository','operator-local','delegated-action'),'owner_principal_ref':S,'evidence_bindings':arr(obj({'ref':S,'sha256':H}),1),'policy_bindings':arr(obj({'ref':S,'sha256':H}),1),'scope_refs':arr(S,1,True),'expires_at':DT}),
 'gap':obj({'gap_ref':S,'subject_ref':S,'reason':S,'owner_route':S,'blocking_use':S}),
 'reference_check':obj({'source_version_ref':S,'selector':S,'requested_ref':S,'resolved_ref':nullable(obj({'scope_ref':S,'identity_ref':S,'version_ref':S,'carrier_ref':enum(*carrier_refs),'byte_sha256':H})),'posture':enum('resolved','historical','unresolved','ambiguous','excluded')}),
 'check':obj({'check_ref':S,'obligation_ref':S,'result':enum('pass','fail','not-evaluable'),'evidence_bindings':arr(obj({'ref':S,'sha256':H})),'claim_ceiling':S}),
 'content_binding':obj({'content_ref':S,'byte_sha256':H,'size_bytes':N,'media_type':S}),
 'execution_bounds':obj({'filesystem_scope_refs':arr(S),'network_scope_refs':{'type':'array','maxItems':0},'allowed_action_kinds':arr(S,1,True),'stop_conditions':arr(S,1),'budget':obj({'max_actions':N,'max_input_bytes':N,'max_output_bytes':N,'deadline':DT})}),
 'safe_relative_path':{'type':'string','minLength':1,'pattern':r'^(?!/)(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*//)(?!.*\\)[A-Za-z0-9._/-]*[A-Za-z0-9_-]$'},
 }
 schemas['common']={'$schema':DRAFT,'$id':PREFIX+'common:v1-candidate','title':'Candidate Lab protocol common definitions','$defs':defs}
 catalog.append({'name':'common','group':'foundation','purpose':'Shared exact bindings, cuts, actors, budgets and gaps','path':'schemas/common.schema.json','domain_carriers':[],'runtime_obligations':['O-EXACT','O-AUTHORITY','O-CUT']})
 defs['candidate_artifact_ref']=obj({'scope_ref':S,'identity_ref':S,'version_ref':S,'carrier_ref':S,'byte_sha256':H,'candidate_contract_binding':obj({'ref':S,'sha256':H})})
 bindings=arr(common('binding')); arts=arr(common('artifact_ref')); gaps=arr(common('gap')); cut=common('source_cut');actor=common('actor');budget=common('budget')
 def typed(kind):
  exact=next(t['current_ref'] for t in coverage['types'] if t['identity']=='cal.artifact-type.'+kind)
  return {'allOf':[common('artifact_ref'),{'properties':{'carrier_ref':{'const':exact}}}]}
 def add(name,group,purpose,properties,domain=(),obligations=(),rules=None):
  value=obj({'schema_version':{'const':'lab-'+name+'/v1-candidate'},**properties})
  value={'$schema':DRAFT,'$id':PREFIX+name+':v1-candidate','title':'Candidate Lab '+name,**value}
  if rules:value['allOf']=rules
  schemas[name]=value
  catalog.append({'name':name,'group':group,'purpose':purpose,'path':'schemas/'+name+'.schema.json','domain_carriers':['cal.artifact-type.'+k for k in domain],
    'runtime_obligations':list(dict.fromkeys(['O-EXACT',*obligations]))})
 def cond(field,value,props):return {'if':{'properties':{field:{'const':value}},'required':[field]},'then':{'properties':props,'required':list(props)}}
 def readonly(p):return {**p,'authority_effect':{'const':'none'}}
 defs['check']['allOf']=[cond('result','pass',{'evidence_bindings':arr(common('binding'),1)})]
 # Exact-body dispatch, with current and historical schema selectors preserved.
 branches=[]
 for e in domain_bindings:
  branches.append(obj({'carrier_ref':{'const':e['carrier_ref']},'body':{'$ref':e['schema_resource_uri']+(e['schema_selector'] or '')}}))
 schemas['domain-artifact']={'$schema':DRAFT,'$id':PREFIX+'domain-artifact:v1-candidate','title':'Dispatch to exact registered artifact contract','oneOf':branches}
 catalog.append({'name':'domain-artifact','group':'foundation','purpose':'Validate unchanged heterogeneous bodies under all exact registered carriers','path':'schemas/domain-artifact.schema.json','domain_carriers':carrier_refs,'runtime_obligations':['O-EXACT','O-CARRIER','O-REFERENCE']})
 add('artifact-envelope','foundation','Transport exact original content plus a body validated by its selected carrier',
  readonly({'artifact':common('artifact_ref'),'source_cut':cut,'content':common('content_binding'),'decoded_artifact':ref('domain-artifact'),'effective_admission_basis':bindings,'source_locator':S,'claim_ceiling':S}),obligations=('O-CARRIER','O-BYTES','O-AUTHORITY'))
 relation_branches=[]
 for r in coverage['relations']:
  q=r['qualifier_contract']
  pairs=[{'properties':{'source':{'properties':{'semantic_kind':{'const':p['source_kind']}}},'target':{'properties':{'semantic_kind':{'const':p['target_kind']}}}}} for p in r['exact_endpoint_pairs']]
  endpoint=obj({'artifact':common('artifact_ref'),'semantic_kind':S})
  branch=obj({'relation_kind_ref':{'const':r['ref']},'signature_sha256':{'const':r['source_sha256']},'axis_ref':{'const':r['axis_id']},'source':endpoint,'target':endpoint,'qualifiers':obj(q['properties'],q['required_axes'])})
  branch['allOf']=[{'anyOf':pairs}];relation_branches.append(branch)
 schemas['typed-connection']={'$schema':DRAFT,'$id':PREFIX+'typed-connection:v1-candidate','title':'Declared exact endpoint-pair and qualifier dispatcher','oneOf':relation_branches}
 catalog.append({'name':'typed-connection','group':'foundation','purpose':'Close all current Relation Kind endpoint pairs and current qualifier shapes','path':'schemas/typed-connection.schema.json','domain_carriers':['cal.artifact-type.typed-relation/v3','cal.artifact-type.relation-kind/v2'],'runtime_obligations':['O-EXACT','O-REFERENCE','O-RELATION','O-EXTENSION']})
 add('candidate-contract-binding','foundation','Bind prospective schemas/identity rules before their admission',readonly({'binding_ref':S,'candidate_carrier_ref':S,'descriptor':typed('artifact-type'),'schema_content_binding':common('content_binding'),'schema_selector':nullable(S),'identity_selector':S,'discriminator_binding':nullable(common('binding')),'semantic_kind':S,'relation_role_bindings':bindings,'predecessor_contract_binding':nullable(common('binding')),'semantic_owner_review_binding':common('binding'),'validation_report_binding':common('binding'),'posture':{'const':'candidate'}}),obligations=('O-CANDIDATE-CARRIER','O-CARRIER','O-REFERENCE','O-EXTENSION'))
 add('candidate-artifact','foundation','Transport a future-carrier body requiring dynamic pinned-schema validation',readonly({'artifact':common('candidate_artifact_ref'),'contract_binding':ref('candidate-contract-binding'),'content_binding':common('content_binding'),'decoded_body':{'type':'object'},'dynamic_validation_report_binding':common('binding'),'posture':{'const':'candidate'},'claim_ceiling':S}),obligations=('O-CANDIDATE-CARRIER','O-CARRIER','O-BYTES','O-REFERENCE'))
 add('carrier-endpoint-binding','foundation','Declare endpoint-kind mapping without inferring aliases or authority',readonly({'binding_ref':S,'carrier_ref':enum(*carrier_refs),'endpoint_kind':enum(*sorted({p[k] for r in coverage['relations'] for p in r['exact_endpoint_pairs'] for k in ('source_kind','target_kind')})),'identity_selector':S,'directional_role_bindings':bindings,'semantic_mapping_evidence_bindings':arr(common('binding'),1),'owner_review_binding':common('binding'),'source_cut':cut}),obligations=('O-CARRIER','O-RELATION','O-EXTENSION'))
 add('domain-lifecycle-mapping','foundation','Bind workflow transitions to exact domain status/evidence contracts',readonly({'mapping_ref':S,'workflow_definition_binding':common('binding'),'carrier_ref':enum(*carrier_refs),'state_selector':S,'state_value_mapping_bindings':arr(common('binding'),1),'completion_assessment_carrier':enum(*carrier_refs),'required_relation_bindings':bindings,'actor_route_bindings':arr(common('binding'),1),'owner_review_binding':common('binding'),'source_cut':cut}),obligations=('O-WORKFLOW','O-CARRIER','O-EVIDENCE','O-AUTHORITY'))
 add('error-result','foundation','Explicit failure, indeterminate result or missing obligation',readonly({'request_binding':common('binding'),'code':enum('invalid-contract','stale-cut','unresolved-reference','ambiguous-reference','unauthorized','expired-authority','revoked-authority','gate-required','conflict','invalid-connection','noncollapse-failed','closure-missing','indeterminate','recovery-required','unsupported-version','budget-exceeded','path-collision','private-material-excluded'),'message':S,'gaps':gaps,'retry_policy':enum('no-retry','idempotent-retry','reconcile-first'),'evidence_bindings':bindings}),obligations=('O-AUTHORITY','O-RECOVERY'))
 add('canonical-store-config','sources','Bind a scoped canonical store to independent profile and trust roots',readonly({'store_ref':S,'branch_ref':S,'authority_scope':enum('repository','operator-local'),'profile_binding':common('binding'),'trust_anchor_bindings':arr(common('binding'),1),'policy_bindings':arr(common('binding'),1),'allowed_categories':arr(enum(*CAT),1,True),'allowed_effects':arr(enum('admit','revise','withdraw'),1,True),'content_format_binding':common('binding'),'commit_protocol_binding':common('binding'),'recovery_contract_binding':common('binding'),'private_key_in_store':{'const':False},'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}}),obligations=('O-PROFILE','O-AUTHORITY','O-COMMIT','O-PRIVACY'))
 add('commit-head','sources','Identify committed history visibility without owning admission authority',readonly({'store_ref':S,'branch_ref':S,'sequence':N,'commit_binding':common('binding'),'config_binding':common('binding'),'profile_binding':common('binding'),'source_root_bindings':arr(common('binding'),1)}),obligations=('O-COMMIT','O-CUT','O-RECOVERY'))
 add('sqlite-projection-config','storage','Declare disposable DB compatibility, custody and complete generation checks',readonly({'config_ref':S,'database_scope_ref':S,'sql_schema_binding':common('binding'),'sqlite_compatibility_binding':common('binding'),'journal_mode':enum('delete','wal'),'foreign_keys_required':{'const':True},'same_host_required':{'const':True},'source_scope_refs':arr(S,1,True),'projector_binding':common('binding'),'source_verification_binding':common('binding'),'cache_body_bytes':B,'budget':budget,'canonical_replay_source':{'const':False}}),obligations=('O-PROJECTION','O-CUT','O-PRIVACY'))
 add('source-profile','sources','Independent exact source and executable compatibility selection',readonly({'profile_ref':S,'protocol_version':{'const':1},'source_cut':cut,'immutable_roots':arr(common('binding'),1),'catalog_binding':common('binding'),'implementation_binding':common('binding'),'compatible_protocol_refs':arr(S,1,True),'allowlist':arr(common('content_binding'),1),'lookup_bindings':bindings,'derivation_bindings':bindings,'review_basis':bindings,'challenge_route':S}),obligations=('O-PROFILE','O-CUT','O-CARRIER'))
 add('profile-transition','sources','Explicit successor branch without rewriting old history',readonly({'transition_ref':S,'old_profile':common('binding'),'new_profile':common('binding'),'old_cut':cut,'successor_branch_ref':S,'retained_refs':arts,'promoted_refs':arts,'revalidated_refs':arts,'conflict_refs':arts,'excluded_refs':arr(S),'authorization_basis':common('authority_basis'),'rollback_bindings':bindings,'silent_rebase_allowed':{'const':False}}),obligations=('O-PROFILE','O-AUTHORITY','O-RECOVERY'))
 add('candidate-workspace','sources','Isolate exact candidate closure and eligibility from admitted state',readonly({'workspace_ref':S,'base_cut':cut,'profile_binding':common('binding'),'material_bindings':arr(common('content_binding')),'candidate_refs':arr(common('candidate_artifact_ref')),'contract_bindings':bindings,'connection_bindings':bindings,'eligible_persistence_refs':arr({'oneOf':[common('artifact_ref'),common('candidate_artifact_ref')]}),'excluded_material_refs':arr(S),'reference_checks':arr(common('reference_check')),'validation_binding':nullable(common('binding')),'canonical_state_mutation':{'const':False}}),obligations=('O-CARRIER','O-REFERENCE','O-MEMORY','O-PRIVACY'))
 add('context-query','reads','Request bounded relevant context for an exact assignment',readonly({'request_ref':S,'actor':actor,'assignment':typed('agent-assignment'),'work':typed('work'),'coordination_context':typed('coordination-context'),'source_cut':cut,'intended_use':S,'selectors':arts,'exclusions':arr(S),'freshness_requirement':enum('current','exact-historical'),'budget':budget}),domain=('context-request/v1','coordination-context/v2'),obligations=('O-CUT','O-VIEW','O-AUTHORITY'))
 add('context-delivery','reads','Deliver source-bound Context/Ontology Views without granting authority',readonly({'request_binding':common('binding'),'source_cut':cut,'context_view':typed('context-view'),'ontology_view':typed('ontology-view'),'included_refs':arts,'excluded_refs':arr(S),'lesson_selection_binding':nullable(common('binding')),'freshness':enum('current','historical','stale'),'expires_at':DT,'scope_enforced':B,'posture':enum('ready','blocked'),'gaps':gaps,'claim_ceiling':S}),domain=('context-view/v1','ontology-view/v1'),obligations=('O-VIEW','O-CUT','O-MEMORY'),rules=[cond('posture','ready',{'scope_enforced':{'const':True}})])
 add('artifact-inspect-request','reads','Inspect one exact permitted artifact revision',readonly({'request_ref':S,'actor':actor,'artifact':common('artifact_ref'),'source_cut':cut,'include':arr(enum('body','contract','authority','relations','provenance','lifecycle','evidence','gaps'),1,True),'budget':budget}),obligations=('O-VIEW','O-AUTHORITY','O-CUT'))
 add('artifact-inspect-result','reads','Explain content and independent status facets',readonly({'request_binding':common('binding'),'envelope':ref('artifact-envelope'),'status_facets':obj({'admission':S,'domain':nullable(S),'implementation':nullable(S),'runtime_observation':nullable(S),'outcome':nullable(S)}),'connections':arr(ref('typed-connection')),'evidence_bindings':bindings,'gaps':gaps,'claim_ceiling':S}),obligations=('O-VIEW','O-CUT','O-CARRIER'))
 add('artifact-query','reads','Bound artifact discovery to selectors, scope and exact cut',readonly({'request_ref':S,'actor':actor,'source_cut':cut,'scope_refs':arr(S,1,True),'carrier_refs':arr(enum(*carrier_refs),1,True),'identity_refs':arr(S),'relation_kind_refs':arr(enum(*[r['ref'] for r in coverage['relations']]),0,True),'max_depth':N,'limit':{'type':'integer','minimum':1},'page_cursor':nullable(S),'budget':budget}),obligations=('O-VIEW','O-CUT','O-AUTHORITY'))
 add('artifact-query-result','reads','Return attributable discovery results with projection watermark',readonly({'request_binding':common('binding'),'source_cut':cut,'projection_generation':common('binding'),'results':arts,'connections':arr(ref('typed-connection')),'next_page_cursor':nullable(S),'gaps':gaps,'claim_ceiling':S}),obligations=('O-CUT','O-VIEW','O-PROJECTION'))
 add('authority-envelope','actors','Present references to actual authority for an assignment',readonly({'envelope_ref':S,'actor':actor,'basis':common('authority_basis'),'delegation_refs':arts,'bounds':common('execution_bounds'),'approval_gate_bindings':bindings,'revocation_source_bindings':bindings,'redelegation_allowed':B,'grants_from_envelope_itself':{'const':False}}),domain=('delegation/v1','role-assignment/v1','authority-boundary/v1'),obligations=('O-AUTHORITY','O-EXACT'))
 add('authority-evaluation','actors','Evaluate exact action against live scope, period, revocation and gates',readonly({'evaluation_ref':S,'request_binding':common('binding'),'authority_envelope_binding':common('binding'),'source_cut':cut,'evaluated_at':DT,'expires_at':DT,'posture':enum('permitted','denied','gate-required','indeterminate'),'checks':arr(common('check'),1),'evidence_bindings':bindings,'gaps':gaps}),obligations=('O-AUTHORITY','O-CUT'),rules=[cond('posture','permitted',{'checks':arr({'allOf':[common('check'),{'properties':{'result':{'const':'pass'}}}]},1),'evidence_bindings':arr(common('binding'),1)})])
 add('agent-session-open','actors','Create a bounded ephemeral machine Agent session',readonly({'request_ref':S,'actor':actor,'assignment':typed('agent-assignment'),'profile':typed('agent-profile'),'implementation':typed('implementation'),'capabilities':arr(typed('agent-capability')),'context_delivery_binding':common('binding'),'authority_envelope_binding':common('binding'),'source_cut':cut,'budget':budget,'memory_policy':obj({'persistence_allowed':{'const':False},'expires_with_session':{'const':True}})}),domain=('agent-session/v1','agent-instance/v1','agent-assignment/v1'),obligations=('O-MEMORY','O-AUTHORITY','O-VIEW'))
 add('agent-session-result','actors','Describe a new ephemeral session and durable-knowledge source',readonly({'request_binding':common('binding'),'session_ref':S,'agent_instance_ref':S,'assignment':typed('agent-assignment'),'context_delivery_binding':common('binding'),'source_cut':cut,'started_at':DT,'expires_at':DT,'memory_persistence_allowed':{'const':False},'durable_continuity_source':{'const':'project-state-via-context-and-ontology-views'},'posture':enum('active','blocked'),'gaps':gaps}),obligations=('O-MEMORY','O-AUTHORITY'))
 add('ephemeral-memory','actors','Session-only short memory; excluded from persistence/export',readonly({'memory':{'$ref':'urn:cyberalchemy-lab:bound-schema:'+memory_digest},'session_ref':S,'storage_class':{'const':'process-local-session-only'},'export_allowed':{'const':False},'durable_write_allowed':{'const':False}}),obligations=('O-MEMORY','O-PRIVACY'))
 add('agent-session-close','actors','Request termination without claiming memory already destroyed',readonly({'request_ref':S,'session_ref':S,'agent_instance_ref':S,'expected_session_binding':common('binding'),'requested_at':DT,'reason':enum('completed','cancelled','expired','failed','budget-exhausted'),'eligible_audit_bindings':bindings}),obligations=('O-MEMORY','O-RECOVERY'))
 add('agent-session-close-receipt','actors','Record actual termination, memory expiry and unresolved action residue',readonly({'request_binding':common('binding'),'session_ref':S,'agent_instance_ref':S,'ended_at':DT,'posture':enum('closed','blocked'),'retained_audit_bindings':bindings,'discarded_memory':B,'agent_identity_reuse_allowed':{'const':False},'unresolved_action_refs':arr(S),'residue_bindings':bindings,'claim_ceiling':S}),obligations=('O-MEMORY','O-RECOVERY'),rules=[cond('posture','closed',{'discarded_memory':{'const':True}})])
 add('tool-adapter-contract','actions','Bind tool input/output contracts and side-effect/retry scope',readonly({'adapter_ref':S,'tool':typed('tool'),'implementation':typed('implementation'),'input_schema_binding':common('binding'),'output_schema_binding':common('binding'),'allowed_action_kinds':arr(S,1,True),'effect_scope_refs':arr(S,1,True),'retry_semantics':enum('read-only','idempotent','non-idempotent'),'reconciliation_binding':common('binding'),'compensation_binding':nullable(common('binding')),'failure_mode_refs':arts,'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}}),domain=('tool/v1','implementation/v1'),obligations=('O-ACTION','O-AUTHORITY','O-RECOVERY'))
 add('action-request','actions','Ask dispatch of one exact bounded action',readonly({'request_ref':S,'actor':actor,'assignment':typed('agent-assignment'),'action_kind':S,'tool_adapter_binding':common('binding'),'input_bindings':arr(common('content_binding')),'source_cut':cut,'authority_envelope_binding':common('binding'),'idempotency_key':S,'expected_output_contracts':bindings,'bounds':common('execution_bounds')}),domain=('agent-action/v1','agent-assignment/v1'),obligations=('O-AUTHORITY','O-ACTION','O-RECOVERY'))
 add('action-receipt','actions','Attribute dispatch, outputs and uncertain completion',readonly({'receipt_ref':S,'request_binding':common('binding'),'authority_evaluation_binding':common('binding'),'actor':actor,'started_at':nullable(DT),'ended_at':nullable(DT),'posture':enum('denied','completed','failed','indeterminate'),'output_bindings':arr(common('content_binding')),'observation_refs':arts,'residue_bindings':bindings,'reconciliation_required':B,'retry_allowed':B,'claim_ceiling':S}),domain=('agent-action/v1','generated-output/v2'),obligations=('O-ACTION','O-RECOVERY','O-EVIDENCE'),rules=[cond('posture','indeterminate',{'reconciliation_required':{'const':True},'retry_allowed':{'const':False}}),cond('posture','denied',{'started_at':NULL,'output_bindings':{'type':'array','maxItems':0},'retry_allowed':{'const':False}}),cond('posture','completed',{'started_at':DT,'ended_at':DT,'reconciliation_required':{'const':False}})])
 add('recovery-request','actions','Reconcile uncertain action or known uncommitted residue',readonly({'request_ref':S,'actor':actor,'expected_cut':cut,'subject_binding':common('binding'),'recovery_kind':enum('canonical-commit','action-reconciliation','projection-rebuild','file-generation'),'recovery_contract_binding':common('binding'),'authority_basis':common('authority_basis'),'allowed_residue_bindings':bindings}),obligations=('O-RECOVERY','O-AUTHORITY'))
 add('recovery-receipt','actions','Record verified recovery and preserved committed state',readonly({'request_binding':common('binding'),'pre_cut':cut,'post_cut':cut,'posture':enum('recovered','blocked','indeterminate'),'observed_bindings':bindings,'removed_uncommitted_bindings':bindings,'committed_history_removed':{'const':False},'gaps':gaps,'claim_ceiling':S}),obligations=('O-RECOVERY','O-EVIDENCE'))
 target=obj({'operation':enum('admit','revise','withdraw'),'artifact':{'oneOf':[common('artifact_ref'),common('candidate_artifact_ref')]} ,'predecessor':nullable(common('artifact_ref')),'content':nullable(common('content_binding')),'candidate_binding':nullable(common('binding')),'requested_effect':S,'decision_core_binding':common('binding')})
 target['allOf']=[cond('operation','admit',{'predecessor':NULL,'content':common('content_binding'),'candidate_binding':common('binding')}),cond('operation','revise',{'predecessor':common('artifact_ref'),'content':common('content_binding'),'candidate_binding':common('binding')}),cond('operation','withdraw',{'predecessor':common('artifact_ref'),'content':NULL,'candidate_binding':NULL})]
 add('change-proposal','governance','Prepare exact artifact effects without applying authority',readonly({'proposal_ref':S,'actor':actor,'scope_ref':S,'base_cut':cut,'source_profile_binding':common('binding'),'workspace_binding':common('binding'),'targets':arr(target,1),'schema_bindings':bindings,'connection_proposals':arr(ref('typed-connection')),'evidence_bindings':bindings,'idempotency_key':S,'challenge_route':S}),obligations=('O-CARRIER','O-REFERENCE','O-AUTHORITY','O-RELATION','O-HASH'))
 add('validation-report','governance','Record scope-bounded structural/semantic/authority check evidence',readonly({'report_ref':S,'subject_binding':common('binding'),'source_cut':cut,'validator_binding':common('binding'),'checks':arr(common('check'),1),'reference_checks':arr(common('reference_check')),'gaps':gaps,'result':enum('pass','fail','not-evaluable'),'claim_ceiling':S}),obligations=('O-EVIDENCE','O-CARRIER'),rules=[cond('result','pass',{'checks':arr({'allOf':[common('check'),{'properties':{'result':{'const':'pass'}}}]},1),'gaps':{'type':'array','maxItems':0}})])
 add('proposal-review','governance','Show exact diff, consequences, examples and unresolved obligations',readonly({'proposal_binding':common('binding'),'source_cut':cut,'validation_report_binding':common('binding'),'stable_core_bindings':arr(common('binding'),1),'example_bindings':arr(common('binding'),1),'declared_consequence_bindings':bindings,'private_public_review_binding':common('binding'),'gaps':gaps,'posture':enum('ready','blocked')}),obligations=('O-HASH','O-AUTHORITY','O-PRIVACY','O-EVIDENCE'),rules=[cond('posture','ready',{'gaps':{'type':'array','maxItems':0}})])
 add('decision-core','governance','Keep independently governed exact target/effect cores acyclic',readonly({'decision_ref':S,'owner_role_ref':S,'accountable_principal_ref':S,'authority_boundary':typed('authority-boundary'),'scope':typed('decision-scope'),'targets':arr({'oneOf':[common('artifact_ref'),common('candidate_artifact_ref')]},1),'target_content_bindings':arr(common('content_binding'),1),'requested_effect':S,'evidence_bindings':arr(common('binding'),1),'invalidation_conditions':arr(S,1),'generated_output_digests_in_core':{'const':False}}),domain=('decision/v2','decision-scope/v2','authority-boundary/v1'),obligations=('O-HASH','O-AUTHORITY'))
 add('review-package','governance','One complete final checkpoint with independent exact members',readonly({'package_ref':S,'base_cut':cut,'manifest_binding':common('binding'),'decision_bundle':typed('decision-bundle'),'checkpoint':typed('decision-checkpoint'),'workflow_decision_profile':typed('workflow-decision-profile'),'ordered_core_bindings':arr(common('binding'),1),'validation_bindings':arr(common('binding'),1),'example_bindings':arr(common('binding'),1),'operational_instruction_bindings':bindings,'all_targets_materialized':{'const':True},'human_checkpoint_count':{'const':1},'atomicity_requirement':{'const':'all-or-nothing'},'invalidation_conditions':arr(S,1)}),domain=('decision-bundle/v1','decision-checkpoint/v1','workflow-decision-profile/v1'),obligations=('O-AUTHORITY','O-HASH','O-EVIDENCE','O-EXACT'))
 outcome=obj({'core_binding':common('binding'),'owner_principal_ref':S,'owner_role_ref':S,'selected_outcome':enum('approve-exact-effect','reject','defer'),'authorization_evidence_binding':common('binding')})
 proof_payload=obj({'review_package_binding':common('binding'),'proposal_binding':common('binding'),'base_cut':cut,'ordered_core_bindings':arr(common('binding'),1),'owner_principal_ref':S,'owner_role_refs':arr(S,1,True),'scope_refs':arr(S,1,True),'selected_outcome':{'const':'authorize-exact-selected-effects'},'authorized_at':DT})
 proof_channel={'oneOf':[
  obj({'kind':{'const':'owner-conversation'},'authorization_record_binding':common('binding'),'provenance_binding':common('binding')}),
  obj({'kind':{'const':'operator-signature'},'scheme':{'const':'Ed25519'},'public_key_binding':common('binding'),'signature':{'type':'string','pattern':'^[a-f0-9]{128}$'}}),
  obj({'kind':{'const':'existing-exact-authority'},'authority_artifact':common('artifact_ref'),'matching_evaluation_binding':common('binding')})]}
 add('authorization-proof','governance','Bind actual authorization channel to exact stable reviewed inputs',readonly({'proof_ref':S,'payload':proof_payload,'channel':proof_channel,'verification_contract_binding':common('binding'),'grants_from_schema_validity':{'const':False}}),obligations=('O-AUTHORITY','O-HASH','O-CUT'))
 add('checkpoint-resolution','governance','Record actual member outcomes without inventing owner signatures',readonly({'review_package_binding':common('binding'),'checkpoint_binding':common('binding'),'resolved_at':DT,'ordered_outcomes':arr(outcome,1),'authorization_channel':enum('owner-conversation','operator-signature','existing-exact-authority'),'channel_verification_binding':common('binding'),'all_required_members_authorized':B}),obligations=('O-AUTHORITY','O-HASH'),rules=[cond('all_required_members_authorized',True,{'ordered_outcomes':arr({'allOf':[outcome,{'properties':{'selected_outcome':{'const':'approve-exact-effect'}}}]},1)})])
 add('commit-request','governance','Request exact canonical application under one selected authority scope',readonly({'request_ref':S,'actor':actor,'authority_scope':enum('repository','operator-local'),'expected_cut':cut,'proposal_binding':common('binding'),'review_package_binding':common('binding'),'resolution_binding':common('binding'),'target_package_binding':common('binding'),'idempotency_key':S,'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}}),domain=('admission-transaction/v1',),obligations=('O-COMMIT','O-AUTHORITY','O-HASH','O-RECOVERY'))
 add('commit-record','governance','Persist distinct event changes, exact content and consequences',{'commit_ref':S,'scope_ref':S,'sequence':N,'previous_commit_sha256':nullable(H),'input_cut':cut,'proposal_binding':common('binding'),'resolution_binding':common('binding'),'content_package_binding':common('binding'),'decision_core_bindings':arr(common('binding'),1),'semantic_event_bindings':bindings,'governance_event_bindings':bindings,'consequence_bindings':bindings,'authorization_evidence_bindings':arr(common('binding'),1),'authority_effect':enum('local-artifact-admission','repository-artifact-admission'),'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}},domain=('admission-transaction/v1','project-state/v2'),obligations=('O-COMMIT','O-HASH','O-AUTHORITY','O-RECOVERY'))
 add('commit-receipt','governance','Acknowledge canonical commit independently of projections/exports',readonly({'request_binding':common('binding'),'commit_binding':nullable(common('binding')),'post_cut':cut,'posture':enum('committed','rejected','indeterminate'),'output_bindings':bindings,'projection_posture':enum('pending','applied','failed'),'file_generation_posture':enum('pending','applied','failed','not-selected'),'recovery_required':B,'gaps':gaps,'claim_ceiling':S}),obligations=('O-COMMIT','O-RECOVERY','O-PROJECTION'),rules=[cond('posture','committed',{'commit_binding':common('binding')}),cond('posture','indeterminate',{'recovery_required':{'const':True}})])
 transition=obj({'transition_ref':S,'from_state':S,'to_state':S,'actor_role_refs':arr(S,1,True),'input_carriers':arr(enum(*carrier_refs)),'output_carriers':arr(enum(*carrier_refs)),'authority_requirement_refs':arr(S,1),'precondition_refs':arr(S),'satisfaction_check_refs':arr(S,1),'relation_requirement_refs':arr(S),'failure_state':S,'indeterminate_state':S})
 add('workflow-definition','workflows','Declare transitions and obligations independently of admission posture',readonly({'workflow_type_ref':S,'version':S,'states':arr(S,1,True),'initial_state':S,'terminal_states':arr(S,1,True),'transitions':arr(transition,1),'decision_profile':typed('workflow-decision-profile'),'single_goal_coordination':{'const':True},'domain_mapping_bindings':bindings,'challenge_route':S}),domain=('governed-model/v1','contract/v1','lifecycle-profile/v1'),obligations=('O-WORKFLOW','O-AUTHORITY','O-EVIDENCE'))
 add('workflow-run','workflows','Bind a workflow instance to exact Work, coordination and observations',readonly({'run_ref':S,'definition_binding':common('binding'),'intent':typed('intent'),'intent_resolution':typed('intent-resolution'),'work':typed('work'),'coordination_context':typed('coordination-context'),'actor':actor,'source_cut':cut,'state':S,'event_bindings':bindings,'outcome_assessment':nullable(typed('work-outcome-assessment')),'gaps':gaps}),domain=('work/v1','coordination-context/v2','intent-resolution/v1'),obligations=('O-WORKFLOW','O-EVIDENCE','O-AUTHORITY'))
 add('workflow-transition','workflows','Request one exact permitted workflow step',readonly({'request_ref':S,'run_binding':common('binding'),'definition_binding':common('binding'),'transition_ref':S,'expected_state':S,'actor':actor,'input_artifacts':arts,'action_receipt_bindings':bindings,'authority_evaluation_binding':common('binding'),'satisfaction_report_binding':common('binding'),'source_cut':cut,'idempotency_key':S}),obligations=('O-WORKFLOW','O-AUTHORITY','O-EVIDENCE'))
 add('workflow-transition-receipt','workflows','Record observed workflow change without automatic artifact admission',readonly({'request_binding':common('binding'),'run_ref':S,'from_state':S,'to_state':S,'posture':enum('applied','blocked','indeterminate'),'event_binding':nullable(common('binding')),'output_artifact_refs':arts,'evidence_bindings':bindings,'gaps':gaps,'claim_ceiling':S}),obligations=('O-WORKFLOW','O-EVIDENCE','O-RECOVERY'),rules=[cond('posture','applied',{'event_binding':common('binding'),'evidence_bindings':arr(common('binding'),1)})])
 add('classification-request','learning','Propose one axis-qualified classification assignment',readonly({'request_ref':S,'actor':actor,'subject':common('artifact_ref'),'scheme':typed('classification-scheme'),'value':typed('classification-value'),'axis_ref':S,'basis_bindings':arr(common('binding'),1),'assignment_candidate_binding':common('binding'),'source_cut':cut}),domain=('classification-assignment/v1','classification-scheme/v1','classification-value/v1'),obligations=('O-CLASSIFICATION','O-EVIDENCE'))
 add('failure-assessment-request','learning','Propose assessment keeping occurrence/mode/cause/recovery separate',readonly({'request_ref':S,'actor':actor,'occurrence':typed('failure-occurrence'),'mode_assignment':typed('classification-assignment'),'cause_hypothesis_refs':arts,'evidence_bindings':arr(common('binding'),1),'assessment_candidate_binding':common('binding'),'incident_threshold_binding':nullable(common('binding')),'source_cut':cut}),domain=('failure-occurrence/v1','failure-assessment/v1','failure-control-binding/v1','incident/v1'),obligations=('O-FAILURE','O-EVIDENCE'))
 add('challenge-request','learning','Submit attributable challenge under the exact contestability contract',readonly({'request_ref':S,'actor':actor,'subject':common('artifact_ref'),'challenge_contract':typed('challenge-contract'),'ground':S,'evidence_bindings':arr(common('binding'),1),'eligibility_evaluation_binding':common('binding'),'challenge_candidate_binding':common('binding'),'source_cut':cut}),domain=('challenge-contract/v1','challenge-event/v1'),obligations=('O-CHALLENGE','O-AUTHORITY','O-EVIDENCE'))
 add('challenge-resolution','learning','Bind resolution to actual Decision and preserve semantic/governance distinction',readonly({'challenge':typed('challenge-event'),'resolution_decision':typed('decision'),'evidence_bindings':arr(common('binding'),1),'semantic_change_proposal_binding':nullable(common('binding')),'governance_change_proposal_binding':nullable(common('binding')),'unresolved_gaps':gaps,'source_cut':cut}),domain=('challenge-event/v1','decision/v2'),obligations=('O-CHALLENGE','O-AUTHORITY','O-ONTOLOGY'))
 lessonitem=obj({'lesson':typed('operational-lesson'),'applicability_check_binding':common('binding'),'posture':enum('selected','omitted','blocked'),'reason':S,'conflict_refs':arts,'expired':B})
 add('lesson-selection','learning','Explain eligible lesson selection without implying application or benefit',readonly({'selection_ref':S,'session_ref':S,'assignment':typed('agent-assignment'),'source_cut':cut,'items':arr(lessonitem),'instruction_precedence_binding':common('binding'),'claim_ceiling':S}),domain=('operational-lesson/v1',),obligations=('O-LESSON','O-MEMORY','O-EVIDENCE'))
 add('lesson-application-request','learning','Record an explicit proposed application of an exact lesson revision',readonly({'request_ref':S,'actor':actor,'session_ref':S,'lesson':typed('operational-lesson'),'selection_binding':common('binding'),'applicability_binding':common('binding'),'application_candidate_binding':common('binding'),'conflict_refs':arts,'override_basis':bindings,'source_cut':cut}),domain=('lesson-application/v1',),obligations=('O-LESSON','O-AUTHORITY'))
 add('lesson-assessment-request','learning','Assess predicted/observed outcomes and causal claim ceiling',readonly({'request_ref':S,'actor':actor,'application':typed('lesson-application'),'assessment_candidate_binding':common('binding'),'evidence_bindings':arr(common('binding'),1),'counterevidence_bindings':bindings,'causal_claim_ceiling':S,'source_cut':cut}),domain=('lesson-outcome-assessment/v1','improvement-signal/v1','improvement-target/v1'),obligations=('O-LESSON','O-EVIDENCE'))
 add('typed-extension-request','ontology','Declare missing pair/qualifier semantics and noncollapse review obligations',readonly({'request_ref':S,'actor':actor,'relation_kind_candidate':common('artifact_ref'),'prior_signature_binding':nullable(common('binding')),'unique_semantic_question':S,'axis_ref':S,'pair_contract_bindings':arr(common('binding'),1),'qualifier_domain_bindings':arr(common('binding'),1),'noncollapse_report_binding':common('binding'),'canonical_writable_authority_ref':S,'affected_carrier_successor_refs':arts,'semantic_owner_review_binding':common('binding'),'source_cut':cut}),domain=('relation-kind/v2','typed-relation/v3'),obligations=('O-EXTENSION','O-RELATION','O-AUTHORITY'))
 add('ontology-mapping','ontology','Preserve exact represented subjects and distinct edge authorities',readonly({'mapping_ref':S,'ontology_manifest':typed('ontology-manifest'),'artifact_carrier_refs':arr(enum(*carrier_refs),1,True),'node_profile_bindings':arr(common('binding'),1),'global_relation_signature_bindings':bindings,'local_edge_profile_bindings':bindings,'lab_history_stream_refs':arr(S,1,True),'ontology_history_stream_refs':arr(S,1,True),'representation_rules_binding':common('binding'),'global_relation_projection_writable':{'const':False}}),domain=('ontology-manifest/v1','ontology-node/v2','ontology-edge/v1'),obligations=('O-ONTOLOGY','O-RELATION','O-CUT'))
 add('ontology-project-request','ontology','Map exact committed Lab inputs to selected ontology representations',readonly({'request_ref':S,'actor':actor,'lab_source_cut':cut,'ontology_expected_cut':cut,'mapping_binding':common('binding'),'subject_refs':arts,'authorization_basis':common('authority_basis'),'idempotency_key':S}),obligations=('O-ONTOLOGY','O-AUTHORITY','O-CUT'))
 add('ontology-projection-receipt','ontology','Expose independent ontology watermark, exact mappings and gaps',readonly({'request_binding':common('binding'),'lab_source_cut':cut,'ontology_applied_cut':cut,'mapping_binding':common('binding'),'represented_refs':arts,'ontology_view':typed('ontology-view'),'posture':enum('applied','pending','blocked'),'gaps':gaps,'claim_ceiling':S}),obligations=('O-ONTOLOGY','O-CUT','O-EVIDENCE'))
 add('projection-refresh-request','storage','Request disposable SQLite projection rebuild at an exact cut',readonly({'request_ref':S,'source_cut':cut,'projector_binding':common('binding'),'contract_catalog_binding':common('binding'),'expected_generation_binding':nullable(common('binding')),'budget':budget}),obligations=('O-PROJECTION','O-CUT'))
 add('projection-query-status','storage','Return projection cut and independent source verification',readonly({'generation_binding':common('binding'),'source_cut':cut,'canonical_current_cut':cut,'posture':enum('ready','stale','building','invalidated'),'source_verification_binding':common('binding'),'canonical_replay_source':{'const':False},'gaps':gaps,'claim_ceiling':S}),obligations=('O-PROJECTION','O-CUT'))
 add('file-materialization-request','storage','Select exact export content and pinned rendering scope',readonly({'request_ref':S,'actor':actor,'source_cut':cut,'selection_ref':S,'artifact_refs':arts,'output_root_scope_ref':S,'mode':enum('byte-exact','rendered'),'renderer_binding':nullable(common('binding')),'managed_relative_paths':arr(common('safe_relative_path'),1,True),'overwrite_unmanaged_files':{'const':False},'include_session_memory':{'const':False},'privacy_review_binding':common('binding')}),obligations=('O-FILE','O-BYTES','O-PRIVACY','O-MEMORY'),rules=[cond('mode','rendered',{'renderer_binding':common('binding')}),cond('mode','byte-exact',{'renderer_binding':NULL})])
 add('file-materialization-receipt','storage','Acknowledge file generation separately from canonical commit',readonly({'request_binding':common('binding'),'manifest_binding':common('binding'),'source_cut':cut,'generation_ref':S,'posture':enum('published','staged','failed'),'output_bindings':arr(common('content_binding')),'canonical_replay_source':{'const':False},'unmanaged_files_overwritten':{'const':False},'gaps':gaps,'claim_ceiling':S}),obligations=('O-FILE','O-RECOVERY'))
 add('package-export-request','storage','Export selected complete portable content and dependencies',readonly({'request_ref':S,'actor':actor,'source_cut':cut,'artifact_refs':arts,'dependency_bindings':bindings,'privacy_review_binding':common('binding'),'include_session_memory':{'const':False},'include_private_credentials':{'const':False},'export_contract_binding':common('binding')}),obligations=('O-BYTES','O-PRIVACY','O-MEMORY','O-REFERENCE'))
 add('package-import-request','storage','Prepare independent exact import/adaptation effects',readonly({'request_ref':S,'actor':actor,'source_package_binding':common('binding'),'source_admission_basis':bindings,'target_base_cut':cut,'mapping_binding':common('binding'),'disposition_binding':common('binding'),'candidate_workspace_binding':common('binding'),'automatic_admission':{'const':False}}),domain=('source/v1','source-admission/v1'),obligations=('O-MIGRATION','O-AUTHORITY','O-REFERENCE'))
 disposition=obj({'source_binding':common('binding'),'posture':enum('imported-candidate','adapted-candidate','referenced','deferred','excluded','blocked'),'target_refs':arts,'reason':S,'dependency_bindings':bindings,'owner_route':S})
 add('migration-disposition','product','Account for every selected legacy item without claiming broad cutover',readonly({'manifest_ref':S,'source_scope_bindings':arr(common('binding'),1),'items':arr(disposition,1),'private_public_review_binding':common('binding'),'source_retirement_authorized':{'const':False},'claim_ceiling':S}),domain=('repository-migration-manifest/v1','context-migration-manifest/v2','canonical-package-manifest/v1'),obligations=('O-MIGRATION','O-PRIVACY','O-AUTHORITY'))
 add('capability-adoption-request','product','Separate realization/binding conformance and owner-local adoption',readonly({'request_ref':S,'actor':actor,'capability':typed('product-capability'),'binding':typed('capability-realization-binding'),'realization_refs':arts,'conformance_bindings':arr(common('binding'),1),'operational_scope_ref':S,'authority_basis':common('authority_basis'),'observation_contract_bindings':arr(common('binding'),1),'source_cut':cut,'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}}),domain=('product-capability/v1','capability-realization-binding/v2','implementation/v1'),obligations=('O-ADOPTION','O-AUTHORITY','O-EVIDENCE'))
 add('release-manifest','product','Bind exact release bytes, acceptance, pilot and selected effects',readonly({'release_ref':S,'product':typed('product-identity'),'thesis':typed('product-thesis'),'capability_refs':arr(typed('product-capability'),1),'implementation_bindings':arr(common('binding'),1),'package_bindings':arr(common('binding'),1),'acceptance_contract_bindings':arr(common('binding'),1),'pilot_evidence_bindings':arr(common('binding'),1),'privacy_review_binding':common('binding'),'validation_bindings':arr(common('binding'),1),'install_contract_binding':common('binding'),'supported_environment_bindings':arr(common('binding'),1),'release_decision_binding':nullable(common('binding')),'posture':enum('candidate','approved-exact-scope','blocked'),'external_effect_refs':{'type':'array','maxItems':0},'claim_ceiling':S}),obligations=('O-RELEASE','O-EVIDENCE','O-PRIVACY','O-AUTHORITY'),rules=[cond('posture','approved-exact-scope',{'release_decision_binding':common('binding')})])
 add('install-request','product','Request scoped install/upgrade/rollback without inferred service activation',readonly({'request_ref':S,'actor':actor,'operation':enum('install','upgrade','rollback'),'release_manifest_binding':common('binding'),'source_profile_binding':common('binding'),'target_environment_binding':common('binding'),'authority_basis':common('authority_basis'),'preimage_binding':common('binding'),'recovery_contract_binding':common('binding'),'private_custody_scope_ref':S,'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0}}),obligations=('O-INSTALL','O-AUTHORITY','O-RECOVERY','O-PRIVACY'))
 add('installation-receipt','product','Record observed local installation and recovery residue',readonly({'request_binding':common('binding'),'release_manifest_binding':common('binding'),'preimage_binding':common('binding'),'postimage_binding':nullable(common('binding')),'posture':enum('installed','rolled-back','failed','indeterminate'),'verification_bindings':bindings,'private_credentials_in_repository':{'const':False},'recovery_required':B,'gaps':gaps,'claim_ceiling':S}),obligations=('O-INSTALL','O-EVIDENCE','O-RECOVERY'),rules=[cond('posture','indeterminate',{'recovery_required':{'const':True}}),cond('posture','installed',{'postimage_binding':common('binding'),'verification_bindings':arr(common('binding'),1)})])
 add('protocol-package-manifest','foundation','Bind exact schemas, models, examples and retained domain contracts',readonly({'package_ref':S,'status':{'const':'candidate'},'schema_bindings':arr(common('binding'),1),'domain_catalog_binding':common('binding'),'workflow_model_bindings':arr(common('binding'),1),'obligation_catalog_binding':common('binding'),'source_baseline_binding':common('binding'),'authoring_receipt_binding':nullable(common('binding')),'claim_ceiling':S}),obligations=('O-HASH','O-CARRIER'))
 # Candidate review 0001: shape correctness before deriving API contracts.
 def prop(name,key,value):
  schemas[name]['properties'][key]=value
  if key not in schemas[name]['required']:schemas[name]['required'].append(key)
 def rule(name,value):schemas[name].setdefault('allOf',[]).append(value)
 sections=['body','contract','authority','relations','provenance','lifecycle','evidence','gaps']
 prop('artifact-inspect-result','artifact',common('artifact_ref'))
 prop('artifact-inspect-result','source_cut',cut)
 prop('artifact-inspect-result','included_sections',arr(enum(*sections),1,True))
 prop('artifact-inspect-result','envelope',nullable(ref('artifact-envelope')))
 prop('artifact-inspect-result','contract_binding',nullable(common('binding')))
 prop('artifact-inspect-result','authority_bindings',bindings)
 prop('artifact-inspect-result','provenance_bindings',bindings)
 for section,field,present,absent in [
  ('body','envelope',ref('artifact-envelope'),NULL),
  ('contract','contract_binding',common('binding'),NULL),
  ('authority','authority_bindings',bindings,{'type':'array','maxItems':0}),
  ('relations','connections',arr(ref('typed-connection')),{'type':'array','maxItems':0}),
  ('provenance','provenance_bindings',bindings,{'type':'array','maxItems':0}),
  ('evidence','evidence_bindings',bindings,{'type':'array','maxItems':0}),
  ('gaps','gaps',gaps,{'type':'array','maxItems':0})]:
  rule('artifact-inspect-result',{'if':{'properties':{'included_sections':{'contains':{'const':section}}},'required':['included_sections']},'then':{'properties':{field:present}},'else':{'properties':{field:absent}}})
 prop('artifact-query','freshness_requirement',enum('current','exact-historical','allow-stale'))
 prop('artifact-query','query_basis',enum('canonical','projection','prefer-projection'))
 prop('artifact-query-result','projection_generation',nullable(common('binding')))
 prop('artifact-query-result','query_basis',enum('canonical','projection'))
 prop('artifact-query-result','requested_source_cut',cut)
 prop('artifact-query-result','freshness',enum('current','historical','stale'))
 rule('artifact-query-result',cond('query_basis','canonical',{'projection_generation':NULL}))
 rule('artifact-query-result',cond('query_basis','projection',{'projection_generation':common('binding')}))
 for k in ['context_view','ontology_view']:prop('context-delivery',k,nullable(typed(k.replace('_','-'))))
 rule('context-delivery',cond('posture','ready',{'context_view':typed('context-view'),'ontology_view':typed('ontology-view')}))
 for k in ['session_ref','agent_instance_ref']:prop('agent-session-result',k,nullable(S))
 for k in ['started_at','expires_at']:prop('agent-session-result',k,nullable(DT))
 rule('agent-session-result',cond('posture','active',{'session_ref':S,'agent_instance_ref':S,'started_at':DT,'expires_at':DT}))
 rule('agent-session-result',cond('posture','blocked',{'session_ref':NULL,'agent_instance_ref':NULL,'started_at':NULL,'expires_at':NULL}))
 prop('agent-session-close-receipt','ended_at',nullable(DT))
 rule('agent-session-close-receipt',cond('posture','closed',{'ended_at':DT}))
 rule('agent-session-close-receipt',cond('posture','blocked',{'ended_at':NULL}))
 rule('recovery-receipt',cond('posture','recovered',{'observed_bindings':arr(common('binding'),1),'gaps':{'type':'array','maxItems':0}}))
 prop('recovery-receipt','retry_allowed',B)
 rule('recovery-receipt',cond('posture','indeterminate',{'retry_allowed':{'const':False}}))
 rule('commit-receipt',cond('posture','committed',{'recovery_required':{'const':False}}))
 rule('commit-receipt',cond('posture','rejected',{'commit_binding':NULL,'output_bindings':{'type':'array','maxItems':0},'projection_posture':{'const':'pending'},'file_generation_posture':{'const':'not-selected'}}))
 prop('workflow-transition-receipt','recovery_required',B)
 rule('workflow-transition-receipt',cond('posture','applied',{'recovery_required':{'const':False}}))
 rule('workflow-transition-receipt',cond('posture','blocked',{'event_binding':NULL,'output_artifact_refs':{'type':'array','maxItems':0},'recovery_required':{'const':False}}))
 rule('workflow-transition-receipt',cond('posture','indeterminate',{'recovery_required':{'const':True}}))
 prop('ontology-projection-receipt','posture',enum('applied','pending','blocked','indeterminate'))
 prop('ontology-projection-receipt','recovery_required',B)
 rule('ontology-projection-receipt',cond('posture','indeterminate',{'recovery_required':{'const':True}}))
 rule('ontology-projection-receipt',cond('posture','applied',{'recovery_required':{'const':False}}))
 prop('ontology-projection-receipt','ontology_view',nullable(typed('ontology-view')))
 prop('ontology-projection-receipt','ontology_applied_cut',nullable(cut))
 rule('ontology-projection-receipt',cond('posture','applied',{'ontology_view':typed('ontology-view'),'ontology_applied_cut':cut,'gaps':{'type':'array','maxItems':0}}))
 for k in ['generation_binding','source_verification_binding']:prop('projection-query-status',k,nullable(common('binding')))
 rule('projection-query-status',cond('posture','ready',{'generation_binding':common('binding'),'source_verification_binding':common('binding'),'gaps':{'type':'array','maxItems':0}}))
 prop('file-materialization-receipt','manifest_binding',nullable(common('binding')))
 prop('file-materialization-receipt','generation_ref',nullable(S))
 prop('file-materialization-receipt','posture',enum('published','staged','failed','indeterminate'))
 prop('file-materialization-receipt','recovery_required',B)
 for posture in ['published','staged']:rule('file-materialization-receipt',cond('posture',posture,{'manifest_binding':common('binding'),'generation_ref':S}))
 rule('file-materialization-receipt',cond('posture','published',{'output_bindings':arr(common('content_binding'),1),'recovery_required':{'const':False},'gaps':{'type':'array','maxItems':0}}))
 rule('file-materialization-receipt',cond('posture','indeterminate',{'recovery_required':{'const':True}}))
 prop('package-export-request','artifact_refs',arr(common('artifact_ref'),1))
 prop('capability-adoption-request','realization_refs',arr(common('artifact_ref'),1))
 prop('typed-extension-request','relation_kind_candidate',typed('relation-kind'))
 prop('typed-extension-request','affected_carrier_successor_refs',arr(typed('artifact-type')))
 rule('installation-receipt',cond('posture','installed',{'recovery_required':{'const':False}}))
 rule('installation-receipt',cond('posture','rolled-back',{'postimage_binding':common('binding'),'verification_bindings':arr(common('binding'),1),'recovery_required':{'const':False}}))
 errors=schemas['error-result']['properties']['code']['enum']
 errors.extend(['not-found','unsupported-operation','idempotency-conflict','integrity-failed','invalid-cursor','deadline-exceeded','adapter-failed'])
 for code in ['indeterminate','recovery-required']:rule('error-result',cond('code',code,{'retry_policy':{'const':'reconcile-first'}}))
 # Bootstrap and inspection are bounded reads; no Agent assignment is needed to discover a cut.
 add('lab-status-request','reads','Discover selected store/profile compatibility and current watermarks',readonly({'request_ref':S,'actor':actor,'scope_refs':arr(S,1,True),'source_cut':nullable(cut),'budget':budget}),obligations=('O-VIEW','O-CUT','O-PROFILE','O-AUTHORITY'))
 add('lab-status-result','reads','Report selected heads and declared versus implemented operation support',readonly({'request_binding':common('binding'),'source_cut':cut,'source_profile_binding':common('binding'),'catalog_binding':common('binding'),'supported_operations':arr(S,0,True),'implementation_posture':enum('declared-only','implemented-local'),'projection_status_binding':nullable(common('binding')),'gaps':gaps,'claim_ceiling':S}),obligations=('O-VIEW','O-CUT','O-PROFILE','O-EVIDENCE'))
 add('catalog-request','reads','Read exact contract/catalog bindings before artifact discovery',readonly({'request_ref':S,'actor':actor,'source_cut':cut,'carrier_refs':arr(enum(*carrier_refs),0,True),'include_relations':B,'limit':{'type':'integer','minimum':1},'page_cursor':nullable(S),'budget':budget}),obligations=('O-VIEW','O-CARRIER','O-CUT','O-AUTHORITY'))
 contract_entry=obj({'carrier_ref':enum(*carrier_refs),'schema_binding':common('binding'),'descriptor_binding':common('binding'),'schema_selector':nullable(S),'semantic_kind':S,'write_posture':enum('current','historical-read-only'),'admission_decision_ref':S})
 signature_entry=obj({'relation_kind_ref':enum(*[r['ref'] for r in coverage['relations']]),'axis_ref':S,'signature_binding':common('binding')})
 add('catalog-result','reads','Return pinned current/historical contracts and declared relation signatures',readonly({'request_binding':common('binding'),'source_cut':cut,'domain_catalog_binding':common('binding'),'contract_entries':arr(contract_entry),'relation_signatures':arr(signature_entry),'next_page_cursor':nullable(S),'gaps':gaps,'claim_ceiling':S}),obligations=('O-CARRIER','O-CUT','O-VIEW','O-RELATION'))
 add('session-inspect-request','actors','Inspect session metadata and audit references without exposing short memory',readonly({'request_ref':S,'actor':actor,'session_ref':S,'budget':budget}),obligations=('O-MEMORY','O-PRIVACY','O-AUTHORITY'))
 add('session-inspect-result','actors','Observe active/closed/expired session metadata and pending action residue',readonly({'request_binding':common('binding'),'session_ref':S,'agent_instance_ref':S,'assignment':typed('agent-assignment'),'source_cut':cut,'posture':enum('active','closing','closed','expired','indeterminate'),'opened_at':DT,'ended_at':nullable(DT),'last_receipt_binding':nullable(common('binding')),'unresolved_action_refs':arr(S),'short_memory_in_response':{'const':False},'gaps':gaps,'claim_ceiling':S}),obligations=('O-MEMORY','O-RECOVERY','O-AUTHORITY'),rules=[cond('posture','active',{'ended_at':NULL}),cond('posture','closed',{'ended_at':DT,'last_receipt_binding':common('binding')})])
 lookup={'oneOf':[obj({'call_binding':common('binding')}),obj({'operation':S,'idempotency_key':S})]}
 add('operation-inspect-request','actions','Look up only the caller-authorized invocation or scoped idempotency record',readonly({'request_ref':S,'actor':actor,'lookup':lookup,'budget':budget}),obligations=('O-RECOVERY','O-AUTHORITY','O-TRANSPORT'))
 add('operation-inspect-result','actions','Observe known operation result or uncertainty without dispatching it again',readonly({'request_binding':common('binding'),'original_call_binding':common('binding'),'operation':S,'posture':enum('pending','completed','failed','indeterminate'),'result_binding':nullable(common('binding')),'effect_evidence_bindings':bindings,'reconciliation_required':B,'retry_allowed':B,'gaps':gaps,'claim_ceiling':S}),obligations=('O-RECOVERY','O-EVIDENCE','O-AUTHORITY'),rules=[cond('posture','completed',{'result_binding':common('binding'),'reconciliation_required':{'const':False}}),cond('posture','indeterminate',{'reconciliation_required':{'const':True},'retry_allowed':{'const':False}}),cond('posture','pending',{'retry_allowed':{'const':False}})])
 api=[
 ('context.get','context-query','context-delivery','bounded-reader'),
 ('artifact.inspect','artifact-inspect-request','artifact-inspect-result','bounded-reader'),
 ('artifact.query','artifact-query','artifact-query-result','bounded-reader'),
 ('session.open','agent-session-open','agent-session-result','assigned-agent-or-operator'),
 ('session.close','agent-session-close','agent-session-close-receipt','assigned-agent-or-operator'),
 ('change.prepare','change-proposal','proposal-review','assigned-agent-or-operator'),
 ('change.validate','change-proposal','validation-report','assigned-agent-or-operator'),
 ('proposal.review','proposal-review','review-package','assigned-agent-or-operator'),
 ('checkpoint.resolve','checkpoint-resolution','validation-report','accountable-owner'),
 ('admission.apply','commit-request','commit-receipt','authorized-application-adapter'),
 ('action.evaluate','action-request','authority-evaluation','assigned-agent-or-operator'),
 ('action.dispatch','action-request','action-receipt','assigned-agent-or-operator'),
 ('action.reconcile','recovery-request','recovery-receipt','authorized-recovery-actor'),
 ('workflow.transition','workflow-transition','workflow-transition-receipt','assigned-agent-or-operator'),
 ('classification.prepare','classification-request','change-proposal','assigned-agent-or-operator'),
 ('failure.assess','failure-assessment-request','change-proposal','assigned-agent-or-operator'),
 ('challenge.submit','challenge-request','change-proposal','eligible-challenger'),
 ('challenge.resolve','challenge-resolution','change-proposal','accountable-owner'),
 ('lesson.select','context-query','lesson-selection','bounded-reader'),
 ('lesson.apply','lesson-application-request','change-proposal','assigned-agent-or-operator'),
 ('lesson.assess','lesson-assessment-request','change-proposal','assigned-agent-or-operator'),
 ('ontology.project','ontology-project-request','ontology-projection-receipt','authorized-representation-actor'),
 ('projection.refresh','projection-refresh-request','projection-query-status','projection-builder'),
 ('files.materialize','file-materialization-request','file-materialization-receipt','authorized-export-actor'),
 ('package.export','package-export-request','file-materialization-receipt','authorized-export-actor'),
 ('package.import','package-import-request','change-proposal','authorized-import-actor'),
 ('installation.execute','install-request','installation-receipt','authorized-local-operator')]
 api += [
 ('lab.status','lab-status-request','lab-status-result','bounded-reader'),
 ('catalog.get','catalog-request','catalog-result','bounded-reader'),
 ('session.inspect','session-inspect-request','session-inspect-result','session-owner-or-authorized-auditor'),
 ('operation.inspect','operation-inspect-request','operation-inspect-result','operation-owner-or-authorized-auditor'),
 ('typed.extension.prepare','typed-extension-request','change-proposal','assigned-agent-or-operator'),
 ('capability.adoption.prepare','capability-adoption-request','change-proposal','assigned-agent-or-operator'),
 ('release.prepare','release-manifest','proposal-review','assigned-agent-or-operator')]
 operation_names=[o[0] for o in api]
 for name,key in [('lab-status-result','supported_operations'),('operation-inspect-result','operation')]:
  prop(name,key,arr(enum(*operation_names),0,True) if key=='supported_operations' else enum(*operation_names))
 lookup['oneOf'][1]['properties']['operation']=enum(*operation_names)
 for suffix,index in [('request',1),('result',2)]:
  branches=[]
  for operation,request,response,caller in api:
   body=ref(request) if suffix=='request' else {'oneOf':[ref(response),ref('error-result')]}
   branches.append(obj({'schema_version':{'const':'lab-tool-service-'+suffix+'/v1-candidate'},'operation':{'const':operation},'caller_requirement':{'const':caller},'message':body}))
  name='tool-service-'+suffix
  schemas[name]={'$schema':DRAFT,'$id':PREFIX+name+':v1-candidate','title':'Closed Lab service '+suffix+' dispatcher','oneOf':branches}
  catalog.append({'name':name,'group':'interface','purpose':'Closed operation-specific '+suffix+' dispatch without implicit permissions','path':'schemas/'+name+'.schema.json','domain_carriers':[],'runtime_obligations':['O-EXACT','O-AUTHORITY','O-TRANSPORT']})
 dump(HERE/'service-contracts.json',{'schema_version':'lab-service-contracts/v1-candidate','authority_effect':'none','operations':[{'operation':o,'request_schema':PREFIX+r+':v1-candidate','success_schema':PREFIX+s+':v1-candidate','error_schema':PREFIX+'error-result:v1-candidate','caller_requirement':c} for o,r,s,c in api],'transport_selection':'Undecided; these names are candidate service responsibilities, not existing CLI or HTTP endpoints.'})
 for name,value in schemas.items():dump(HERE/'schemas'/f'{name}.schema.json',value)
 dump(HERE/'domain-bindings.json',{'schema_version':'lab-integrated-domain-bindings/v1-candidate','authority_effect':'none','current_count':len(current),'registered_version_count':len(entries),'bindings':domain_bindings})
 dump(HERE/'schema-catalog.json',{'schema_version':'lab-integrated-schema-catalog/v1-candidate','authority_effect':'none','status':'proposed','scope':'Complete protocol surface for selected local Agent/Lab workflows; no service, network deployment, distributed writing or unknown future effect scope.',
 'protocols':catalog,'reused_storage_schemas':storage,'reused_sql_schema':{'path':'docs/proposals/0006-lab-artifact-storage/schemas/sqlite-read-model.sql','sha256':sha(ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/sqlite-read-model.sql')},
 'ephemeral_memory_binding':{'path':str(memory_path.relative_to(ROOT)),'sha256':memory_digest,'resource_uri':'urn:cyberalchemy-lab:bound-schema:'+memory_digest},'legacy_local_protocols':legacy,
 'current_artifact_types':len(current),'registered_artifact_versions':len(entries),'relation_kinds':len(coverage['relations']),'exact_endpoint_pairs':sum(len(r['exact_endpoint_pairs']) for r in coverage['relations'])})
 source_list=[sources[k] for k in sorted(sources)]
 dump(HERE/'SOURCE-BASELINE.json',{'schema_version':'lab-integrated-schema-source-baseline/v1-candidate','authority_effect':'none','sources':source_list,'source_manifest_digest':hashlib.sha256(json.dumps(source_list,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
 print(json.dumps({'new_protocol_schemas':len(schemas),'domain_versions':len(entries),'current_types':len(current),'relations':len(coverage['relations']),'source_files':len(source_list)}))

if __name__=='__main__':main()
