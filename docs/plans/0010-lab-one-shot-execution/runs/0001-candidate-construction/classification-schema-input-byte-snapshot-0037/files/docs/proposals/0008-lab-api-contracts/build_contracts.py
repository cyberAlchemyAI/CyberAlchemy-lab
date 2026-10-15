#!/usr/bin/env python3
"""Author local Lab API contracts and illustrative messages; no API implementation."""
import copy,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE.parent/'0007-lab-integrated-schema-package'
PREFIX='urn:cyberalchemy-lab:api:'
PROTO='urn:cyberalchemy-lab:protocol:'
DRAFT='https://json-schema.org/draft/2020-12/schema'
S={'type':'string','minLength':1};N={'type':'integer','minimum':0};DT={'type':'string','format':'date-time'};B={'type':'boolean'};NULL={'type':'null'}
H={'type':'string','pattern':'^[a-f0-9]{64}$'}
ID={'type':'string','minLength':1,'maxLength':256,'pattern':'^[A-Za-z0-9][A-Za-z0-9:._/-]*$'}

def obj(p):return {'type':'object','additionalProperties':False,'properties':p,'required':list(p)}
def arr(p,min=0):return {'type':'array','items':p,'minItems':min}
def nullable(p):return {'anyOf':[p,NULL]}
def common(n):return {'$ref':PROTO+'common:v1-candidate#/$defs/'+n}
def api(n):return {'$ref':PREFIX+n+':v1-candidate'}
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'ref':str(p.relative_to(ROOT)),'sha256':sha(p)}
def condition(k,v,p):return {'if':{'properties':{k:{'const':v}},'required':[k]},'then':{'properties':p}}
def schema(n,p):return {'$schema':DRAFT,'$id':PREFIX+n+':v1-candidate','title':'Candidate local Lab API '+n,**p}

# description, effect kind, exact-cut selectors, operation-specific preconditions and outcomes
DETAILS={
'lab.status':('Discover the selected source profile, cut and available implementation surface','read-only',['/source_cut'],['Authorize inspection of all selected scopes.','A null cut selects the current scoped cut at read start; a supplied cut selects an exact historical read.'],['Return the captured cut and exact catalog/profile bindings.','Distinguish declared operations from observed implemented support.']),
'catalog.get':('Read current/historical artifact contracts and declared relation signatures','read-only',['/source_cut'],['Bind cursor to principal, scope, request selectors and exact cut.','An empty carrier selection requests all eligible catalog entries within the page budget.'],['Return pinned schema/descriptor bindings and current/historical posture.','Return only eligible relation signatures when requested.']),
'artifact.inspect':('Inspect selected sections and independent status facets of one exact revision','read-only',['/source_cut'],['Resolve exact artifact identity, revision, carrier and bytes.','Authorize each selected section; excluded sections carry no body or bindings.'],['Included sections are a subset of the request, with disclosed authorized omissions.','Body/header/contract identities agree; effective admission is evidence-derived.']),
'artifact.query':('Find eligible exact revisions and typed connections at a declared cut','read-only',['/source_cut'],['Apply scope, carrier, identity, relation, depth, paging and byte limits.','A projection must verify its generation and disclose its applied cut; stale use requires allow-stale.'],['Return canonical or projected read basis and requested/applied cut and freshness.','A cursor binds the actual cut, generation, selectors, caller and scope.']),
'context.get':('Deliver bounded Context and Ontology Views for one assignment','read-only',['/source_cut'],['Resolve assignment, Work and one-Goal Coordination Context.','Verify included sources, exclusions, lesson applicability, privacy and budgets.'],['Ready requires actual view bindings and enforced scope.','Context grants no authority; blocked delivery may have no views.']),
'session.open':('Open one ephemeral machine Agent session for an exact assignment','ephemeral-session',['/source_cut'],['Verify profile/implementation/capabilities, authority envelope, assignment and delivered context.','Verify context and authority expiration and effective budgets.'],['Active creation returns a new session/instance and observed timestamps.','Blocked creation returns no created identity; short memory is never durable.']),
'session.close':('Terminate a selected session and dispose of its short memory','ephemeral-session',[],['Verify current session binding and actual caller ownership or delegated termination authority.','Identify unresolved actions; closing a session does not resolve their effects.'],['Closed requires observed termination and memory disposal.','Retain only eligible audit references and unresolved residue.']),
'session.inspect':('Read session metadata and unresolved action references','read-only',[],['Authorize session ownership or an exact audit scope.','Never expose short memory, private credentials or a session dump.'],['Return observed metadata/receipt references; absence is scoped not-found.','Expired and uncertain states remain distinct from verified closed.']),
'change.prepare':('Stage exact artifact effects in a candidate workspace','candidate-write',['/base_cut'],['Verify workspace, current profile, exact targets/predecessors and complete schema closure.','Verify typed connections or return an explicit gap; candidate staging grants no admission.'],['Return exact proposal review bindings, examples and declared consequences.','No canonical head or admission status changes.']),
'change.validate':('Validate a candidate proposal under exact contracts and required obligations','candidate-write',['/base_cut'],['Pin validators, source cut and candidate closure.','Select the checks required for this use; authoring checks cannot satisfy operational checks.'],['Return attributable pass/fail/not-evaluable checks, unresolved references and claim ceiling.','Persist only eligible candidate evidence under caller-authorized workspace scope.']),
'proposal.review':('Assemble the exact package for the final owner checkpoint','candidate-write',['/source_cut'],['Verify actual materialized targets, stable Decision cores, examples, validation and private/public review.','Resolve the Workflow Decision Profile and all independently required owner roles.'],['Return one complete review package with exact member bindings and invalidation conditions.','It contains no fabricated authorization, pilot results or future unknown targets.']),
'checkpoint.resolve':('Verify and record actual owner outcomes for exact reviewed members','candidate-write',[],['Verify the actual authorization channel and provenance for each required member owner.','Match exact package, core order, scope, target bytes and current cut; do not infer authorization from caller text.'],['Return a validation report for the recorded resolution.','All-required-authorized is true only when every required member approves its exact effect.']),
'admission.apply':('Apply one exact authorized canonical artifact transaction','canonical-commit',['/expected_cut'],['Verify proposal/package/resolution, owner authority, complete closure and expected current head.','Serialize publication and bind local versus repository authority; zero activation and external effects.'],['Commit exact immutable content/events and publish one canonical head or report uncertainty.','Projection/file outcomes are separately reported and cannot undo a committed transaction.']),
'action.evaluate':('Evaluate current authority for one bounded tool action','read-only',['/source_cut'],['Resolve adapter/input contracts, assignment, scopes, gates, revocation and expiry.','Bind actual authenticated caller; self-declared capability or role does not permit an action.'],['Return permitted/denied/gate-required/indeterminate with exact check evidence.','No dispatch or admission occurs.']),
'action.dispatch':('Run one currently permitted local tool action','local-action',['/source_cut'],['Re-evaluate authority and bounds immediately before dispatch.','Verify adapter retry/recovery scope; forbid network/external/activation effects and writes to admission state outside its publisher.'],['Observe actual outputs and completion/failure/uncertainty.','Indeterminate effects require reconciliation before another dispatch.']),
'action.reconcile':('Reconcile selected uncertain effects or verified recovery residue','recovery',['/expected_cut'],['Authorize only the selected recovery contract and allowed residue.','Observe the actual state; do not replay a non-idempotent action to discover its outcome.'],['Return observed recovery bindings or preserved uncertainty.','Never delete committed history or infer a failed action had no effect.']),
'operation.inspect':('Read the scoped invocation/idempotency record after uncertainty','read-only',[],['Resolve by exact call binding or principal-scoped operation/key.','Authorize operation owner or selected auditor; no cross-principal enumeration.'],['Return known pending/completed/failed/indeterminate result and effect evidence.','Lookup never redispatches the operation; unknown records return scoped not-found.']),
'workflow.transition':('Apply one permitted coordination transition with observed satisfaction','workflow-write',['/source_cut'],['Resolve actual lifecycle mappings, decision profile, actor routes and all transition checks.','Match current run revision/state and satisfaction evidence; block unbound template workflows.'],['Record observed transition and candidate outputs under the selected coordination authority.','No automatic output admission; indeterminate transition requires recovery.']),
'classification.prepare':('Prepare an axis-qualified Classification Assignment','candidate-write',['/source_cut'],['Verify exact subject, scheme, value, axis, applicability and basis.','Do not merge independent classification dimensions or claim causality.'],['Return an exact candidate change proposal for the assignment.']),
'failure.assess':('Prepare evidenced failure assessment and response scope','candidate-write',['/source_cut'],['Verify occurrence, mode assignment, evidence, cause hypotheses and incident threshold.','Separate observation, classification, cause and control/recovery conclusions.'],['Return a bounded candidate assessment proposal with explicit evidence and uncertainty.']),
'challenge.submit':('Prepare an eligible challenge under its exact Challenge Contract','candidate-write',['/source_cut'],['Verify challenged revision, eligibility, grounds, evidence and contract routes.','Disclose only information allowed by the challenger scope.'],['Return a candidate Challenge Event proposal preserving the original subject and history.']),
'challenge.resolve':('Prepare consequences of an actual challenge resolution Decision','candidate-write',['/source_cut'],['Verify actual resolution Decision authority and Challenge Contract obligations.','Keep semantic and governance consequences distinct.'],['Return candidate exact effects with unresolved gaps; no automatic authority promotion.']),
'lesson.select':('Select applicable lessons for the current bounded assignment','read-only',['/source_cut'],['Use the Context Query assignment and exclusions; resolve its active session from trusted context.','Verify applicability, expiry, conflicts and instruction precedence.'],['Return selected/omitted/blocked lesson revisions with reasons.','Selection is neither application nor proof of effectiveness.']),
'lesson.apply':('Prepare a recorded application of an exact lesson revision','candidate-write',['/source_cut'],['Verify session, selection, applicability and any conflict override basis.','Keep lesson instructions within actual delegated action bounds.'],['Return a candidate Lesson Application proposal with attribution.']),
'lesson.assess':('Prepare assessment of a recorded lesson application','candidate-write',['/source_cut'],['Resolve application and observed evidence/counterevidence.','Bind outcome method and causal claim ceiling.'],['Return an outcome assessment proposal; broader effectiveness needs its own evidence.']),
'typed.extension.prepare':('Prepare a declared typed connection extension for owner review','candidate-write',['/source_cut'],['Verify Relation Kind candidate, unique semantic question, orthogonal axis and exact pair/qualifier contracts.','Resolve noncollapse evidence, writable authority, owner review and impacted Artifact Type successors.'],['Return explicit candidate extension effects.','Unregistered new connections remain non-writable until exact required admission.']),
'ontology.project':('Apply selected ontology representations with an independent cut','ontology-representation',['/lab_source_cut','/ontology_expected_cut'],['Verify represented source revisions, mapping/profile closure and ontology authority.','Global typed relation projections remain read-only; local edges obey their own declared profile.'],['Return observed represented references, ontology watermark/view or pending/blocked/uncertain state.','Ontology representation confers no Lab admission authority.']),
'projection.refresh':('Build and select a complete disposable SQLite generation','projection-write',['/source_cut'],['Resolve projector, exact schema/catalog, source verification and expected generation.','Verify complete generation, foreign keys, integrity, watermarks and compatibility before switching visibility.'],['Return observed ready/stale/building/invalidated generation metadata.','Canonical history remains the replay source; projection failure is not canonical rollback.']),
'files.materialize':('Generate selected managed byte exports or pinned rendered files','managed-file-write',['/source_cut'],['Verify exact byte closure or renderer, output scope, paths/symlinks and privacy.','Preserve unmanaged files and exclude session memory; pin complete managed output selection.'],['Stage/publish a managed generation with observed output hashes or report failure/uncertainty.','Generated files grant no admission and are not the canonical replay source.']),
'package.export':('Export selected portable original content and complete dependencies','managed-file-write',['/source_cut'],['Verify selected original bytes and the complete required dependency closure.','Resolve export destination from the exact export contract; exclude credentials/session memory.'],['Return a managed generation receipt binding exported package bytes and dependencies.','Exported source admission evidence does not admit the package in another target.']),
'package.import':('Prepare selected source import/adaptation in a candidate workspace','candidate-write',['/target_base_cut'],['Verify source package, source admission basis, mapping, disposition and dependency closure.','Apply target custody/privacy rules and preserve exact source provenance.'],['Return a candidate target proposal with complete selected-item accounting.','No automatic admission or source retirement.']),
'capability.adoption.prepare':('Prepare exact capability realization and owner-local adoption declarations','candidate-write',['/source_cut'],['Verify capability, realization binding, nonempty implementations, conformance and scoped owner authority.','Bind actual observation contract and operational scope; no activation in this operation.'],['Return candidate exact adoption/binding effects.','Actual operational usefulness must be observed under separately valid action scope.']),
'release.prepare':('Prepare an exact candidate release for its final review','candidate-write',[],['Require candidate posture and actual package, acceptance, pilot, privacy, environment and installation bindings.','A candidate missing any required evidence remains blocked; do not fabricate release approval.'],['Return a candidate proposal review; release Decision remains independently required.','No publication, installation, external effect or activation occurs.']),
'installation.execute':('Install/upgrade/rollback a selected local package under exact authority','local-install',[],['Verify exact release approval, profile, environment, authority, preimage and recovery contract.','Keep credentials in private custody; activation/external effects are zero.'],['Return observed installed/rolled-back/failed/indeterminate postimage evidence.','Installation does not infer a running service or operational acceptance.']),
}

services=json.loads((SOURCE/'service-contracts.json').read_text())['operations']
assert set(DETAILS)=={x['operation'] for x in services}
errors=json.loads((SOURCE/'schemas/error-result.schema.json').read_text())['properties']['code']['enum']
COMMON_ERRORS=['invalid-contract','unauthorized','unsupported-version','budget-exceeded','deadline-exceeded','integrity-failed','adapter-failed','not-found']
operations=[]
for x in services:
    op=x['operation'];description,effect,cuts,pre,post=DETAILS[op]
    codes=list(COMMON_ERRORS)
    if cuts:codes+=['stale-cut','unresolved-reference','ambiguous-reference','closure-missing']
    if effect!='read-only':codes+=['conflict','idempotency-conflict','expired-authority','revoked-authority','gate-required','indeterminate','recovery-required']
    if op in ['artifact.query','catalog.get']:codes+=['invalid-cursor']
    if op in ['artifact.query','artifact.inspect','change.prepare','change.validate','typed.extension.prepare','ontology.project','workflow.transition']:codes+=['invalid-connection','noncollapse-failed']
    if effect in ['managed-file-write','local-install']:codes+=['path-collision','private-material-excluded']
    if op=='action.evaluate':codes+=['expired-authority','revoked-authority','gate-required','indeterminate']
    codes=list(dict.fromkeys(codes));assert set(codes)<=set(errors)
    def bound(uri):
        name=uri.removeprefix(PROTO).removesuffix(':v1-candidate');return {'resource_uri':uri,**bind(SOURCE/'schemas'/f'{name}.schema.json')}
    record={'operation':op,'description':description,'request_schema':bound(x['request_schema']),'result_schema':bound(x['success_schema']),'error_schema':bound(x['error_schema']),
      'authority':{'caller_requirement':x['caller_requirement'],'trusted_channel_required':True,'message_claims_grant_authority':False,'required_obligation_refs':['O-AUTHORITY','O-TRANSPORT','O-EXACT']},
      'effect_kind':effect,'repository_admission_possible':op=='admission.apply','runtime_activations':0,'external_effect_refs':[],
      'source_cut_selectors':cuts,'preconditions':pre,'postconditions':post,'idempotency_required':effect!='read-only',
      'idempotency_namespace':['authenticated-principal','authority-scope','selected-scope','operation'],
      'inner_idempotency_selector':'/idempotency_key' if op in ['change.prepare','action.dispatch','admission.apply','workflow.transition','ontology.project'] else None,
      'idempotency_rule':'Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.',
      'allowed_error_codes':codes,'deadline_rule':'Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.',
      'completion_rule':'A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.',
      'implementation_status':'candidate-contract-only'}
    operations.append(record);dump(HERE/'operations'/f'{op}.json',record)

# All wire calls are correlated; trusted context is resolved by the adapter, not supplied as authority.
call_branches=[];reply_branches=[]
for op in operations:
    request={'$ref':op['request_schema']['resource_uri']}
    if op['operation']=='release.prepare':request={'allOf':[request,{'properties':{'posture':{'const':'candidate'}}}]}
    props={'schema_version':{'const':'lab-api-call/v1-candidate'},'call_id':ID,'operation':{'const':op['operation']},'caller_context_ref':ID,
      'expected_source_cut':nullable(common('source_cut')) if op['operation'] in ['lab.status','session.close','session.inspect','operation.inspect'] else common('source_cut'),'deadline':DT,'max_response_bytes':{'type':'integer','minimum':4096},'idempotency_key':ID if op['idempotency_required'] else NULL,'message':request}
    call_branches.append(obj(props))
    for kind,body in [('result',{'$ref':op['result_schema']['resource_uri']}),('error',{'allOf':[{'$ref':op['error_schema']['resource_uri']},{'properties':{'code':{'enum':op['allowed_error_codes']}}}]})]:
        reply_branches.append(obj({'schema_version':{'const':'lab-api-reply/v1-candidate'},'call_id':ID,'operation':{'const':op['operation']},'request_binding':common('binding'),
          'trusted_context_binding':common('binding'),'handler_binding':common('binding'),'observed_at':DT,'kind':{'const':kind},'message':body}))
api_schemas={
 'api-call':schema('api-call',{'oneOf':call_branches}),
 'api-reply':schema('api-reply',{'oneOf':reply_branches}),
 'transport-error':schema('transport-error',obj({'schema_version':{'const':'lab-api-transport-error/v1-candidate'},'call_id':nullable(ID),'request_byte_sha256':nullable(H),
  'code':{'enum':['malformed-json','invalid-envelope','unauthenticated-channel','unsupported-protocol','unsupported-operation','invalid-call-id','input-too-large','deadline-exceeded']},
  'public_message':{'type':'string','minLength':1,'maxLength':1024},'effect_may_have_started':B,'recovery_policy':{'enum':['no-retry','inspect-first']},'authority_effect':{'const':'none'}})),
 'trusted-call-context':schema('trusted-call-context',obj({'schema_version':{'const':'lab-trusted-call-context/v1-candidate'},'context_ref':ID,'host_instance_ref':ID,'connection_ref':ID,
  'principal_ref':S,'role_assignment_bindings':arr(common('binding')),'authority_scope':{'enum':['repository','operator-local','delegated-action']},'scope_refs':arr(S,1),
  'source_profile_binding':common('binding'),'authentication_evidence_binding':common('binding'),'policy_bindings':arr(common('binding'),1),
  'agent_instance_ref':nullable(S),'session_ref':nullable(S),'assignment_ref':nullable(S),'expires_at':DT,
  'limits':obj({'max_request_bytes':{'type':'integer','minimum':4096},'max_response_bytes':{'type':'integer','minimum':4096},'max_actions':N,'deadline':DT}),
  'origin':{'const':'verified-local-adapter'},'accept_client_supplied_authority_context':{'const':False},'private_credentials_in_context':{'const':False}})),
}
api_schemas['transport-error']['allOf']=[condition('effect_may_have_started',True,{'recovery_policy':{'const':'inspect-first'}})]
for code in ['malformed-json','invalid-envelope','unauthenticated-channel','unsupported-protocol','unsupported-operation','invalid-call-id','input-too-large']:
    api_schemas['transport-error']['allOf'].append(condition('code',code,{'effect_may_have_started':{'const':False},'recovery_policy':{'const':'no-retry'}}))
for n,v in api_schemas.items():dump(HERE/'schemas'/f'{n}.schema.json',v)

contract={
 'schema_version':'lab-api-contracts/v1-candidate','status':'candidate','authority_effect':'none','implementation_status':'not-implemented-by-this-package',
 'api_version':'1-candidate','transport':{'kind':'local-call','primary_interface':'handle(call, adapter_resolved_trusted_context)','optional_adapter':'Authenticated local stdio with one UTF-8 JSON object per line; framing LF is excluded from byte hashes.','network_listener':False,'notifications_allowed':False,'batch_calls_allowed':False},
 'call_schema_binding':bind(HERE/'schemas/api-call.schema.json'),'reply_schema_binding':bind(HERE/'schemas/api-reply.schema.json'),
 'transport_error_schema_binding':bind(HERE/'schemas/transport-error.schema.json'),'trusted_context_schema_binding':bind(HERE/'schemas/trusted-call-context.schema.json'),
 'schema_package_binding':bind(SOURCE/'package-manifest.json'),'schema_review_binding':bind(SOURCE/'reviews/0001/REVIEW.md'),
 'hash_policy':{'wire_binding':'SHA-256 of exact received UTF-8 JSON call bytes, excluding adapter framing; exact bytes must be preserved under private retention policy.',
   'idempotency_fingerprint':'SHA-256 of RFC 8785 JCS UTF-8 bytes of {api_version, operation, authenticated_principal_ref, authority_scope, selected_scope_refs, source_profile_binding, expected_source_cut, message}.',
   'canonicalization_reference':'https://www.rfc-editor.org/rfc/rfc8785','control_payload_only':True,'canonicalize_original_artifact_bytes':False,
   'excluded_from_fingerprint':['call_id','caller_context_ref','outer deadline','max_response_bytes','idempotency_key'],
   'numeric_policy':'Reject duplicate keys, invalid Unicode and control values incompatible with JCS/I-JSON; do not coerce original artifact bytes or silently round exact integers.'},
 'global_rules':['The outer expected source cut agrees with the primary message cut or referenced review/package cut; verify secondary ontology heads and environment preimages independently.','Resolve trusted caller context through the actual authenticated local channel; body actor/role claims must match or be rejected.',
   'Verify live scope, source cut, expiry, revocation, gates and budget immediately before effects; a cached permit is not standing authority.',
   'Correlate response call_id, operation and request binding with the exact input; no authority follows from a result envelope.',
   'Enforce the declared inner command-key selector against the envelope; nested proposal/action keys in validation/evaluation calls remain separate material bindings; never retry under a changed payload and the same key.',
   'Durable idempotency records share crash-consistent effect/recovery evidence. After loss or uncertainty, inspect/reconcile; never recreate a missing key and blindly redispatch.',
   'Read operations can be retried at the same exact cut within current permission; requesting latest again is a new observation.',
   'Reject effectful calls expired before execution; if an effect may have started, preserve uncertainty, inspect and reconcile before retry.',
   'A committed canonical transaction remains committed when a later projection or file generation fails.',
   'Short session memory and private credentials never enter replies, exports, logs or canonical artifacts; eligible audit evidence is governed separately.',
   'Unknown/unbound workflows, endpoint mappings and prospective contracts block only affected selected uses; no implicit alias or schema fallback.',
   'Record enough public outcome metadata for scoped inspection while retaining private provenance and secrets outside the repository.'],
 'operations':operations,
 'claim_ceiling':'Candidate local API contract authoring only; no handler/server, live authentication/signature verification, idempotency implementation, runtime validation, deployment, admission or pilot acceptance.'}
# Schema for the machine-readable contract catalog itself.
resource_binding=obj({'resource_uri':{'type':'string','format':'uri'},'ref':S,'sha256':H})
op_model=obj({'operation':{'enum':[o['operation'] for o in operations]},'description':S,'request_schema':resource_binding,'result_schema':resource_binding,'error_schema':resource_binding,
 'authority':obj({'caller_requirement':{'enum':sorted({o['authority']['caller_requirement'] for o in operations})},'trusted_channel_required':{'const':True},'message_claims_grant_authority':{'const':False},'required_obligation_refs':arr(S,1)}),
 'effect_kind':{'enum':sorted({o['effect_kind'] for o in operations})},'repository_admission_possible':B,'runtime_activations':{'const':0},'external_effect_refs':{'type':'array','maxItems':0},
 'source_cut_selectors':arr({'type':'string','pattern':'^/'}),'preconditions':arr(S,1),'postconditions':arr(S,1),'idempotency_required':B,'inner_idempotency_selector':nullable(S),'idempotency_namespace':arr(S,1),'idempotency_rule':S,
 'allowed_error_codes':arr({'enum':errors},1),'deadline_rule':S,'completion_rule':S,'implementation_status':{'const':'candidate-contract-only'}})
root_props={'schema_version':{'const':'lab-api-contracts/v1-candidate'},'status':{'const':'candidate'},'authority_effect':{'const':'none'},'implementation_status':{'const':'not-implemented-by-this-package'},'api_version':{'const':'1-candidate'},
 'transport':obj({'kind':{'const':'local-call'},'primary_interface':S,'optional_adapter':S,'network_listener':{'const':False},'notifications_allowed':{'const':False},'batch_calls_allowed':{'const':False}}),
 **{k:common('binding') for k in ['call_schema_binding','reply_schema_binding','transport_error_schema_binding','trusted_context_schema_binding','schema_package_binding','schema_review_binding','schema_authoring_receipt_binding']},
 'hash_policy':obj({'wire_binding':S,'idempotency_fingerprint':S,'canonicalization_reference':{'const':'https://www.rfc-editor.org/rfc/rfc8785'},'control_payload_only':{'const':True},'canonicalize_original_artifact_bytes':{'const':False},'excluded_from_fingerprint':arr(S,1),'numeric_policy':S}),
 'global_rules':arr(S,1),'operations':arr(op_model,34),'claim_ceiling':S}
root_props['operations']['maxItems']=34
catalog_schema=schema('api-contract-catalog',obj(root_props))
dump(HERE/'schemas/api-contract-catalog.schema.json',catalog_schema)
api_schemas['api-contract-catalog']=catalog_schema
dump(HERE/'api-contracts.json',contract)

# These examples are schema shapes. Fingerprints use only ASCII object keys and exact small integers;
# Python sorting here is not presented as a general RFC 8785 canonicalizer.
trusted={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'example:trusted-context','host_instance_ref':'example:host','connection_ref':'example:connection',
 'principal_ref':'example:principal','role_assignment_bindings':[],'authority_scope':'operator-local','scope_refs':['example:scope'],
 'source_profile_binding':{'ref':'example:source-profile','sha256':'0'*64},'authentication_evidence_binding':{'ref':'example:authentication','sha256':'0'*64},
 'policy_bindings':[{'ref':'example:policy','sha256':'0'*64}],'agent_instance_ref':None,'session_ref':None,'assignment_ref':None,'expires_at':'2026-10-07T12:00:00Z',
 'limits':{'max_request_bytes':1000000,'max_response_bytes':1000000,'max_actions':1,'deadline':'2026-10-07T12:00:00Z'},'origin':'verified-local-adapter','accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
dump(HERE/'examples/trusted-context.json',trusted)
index=[]
for op in operations:
    name=op['operation'];req_name=op['request_schema']['resource_uri'].removeprefix(PROTO).removesuffix(':v1-candidate');res_name=op['result_schema']['resource_uri'].removeprefix(PROTO).removesuffix(':v1-candidate')
    message=copy.deepcopy(json.loads((SOURCE/'examples'/f'{req_name}.json').read_text()))
    if 'actor' in message:
        message['actor'].update(principal_ref=trusted['principal_ref'],role_assignment_refs=trusted['role_assignment_bindings'],agent_instance_ref=trusted['agent_instance_ref'],session_ref=trusted['session_ref'],assignment_ref=trusted['assignment_ref'])
    if name=='artifact.query':
        message.update(carrier_refs=['cal.artifact-type.definition/v2'],scope_refs=['example:scope'],limit=25,max_depth=1,page_cursor=None,query_basis='canonical',freshness_requirement='current')
    if name=='artifact.inspect':
        message['artifact']=copy.deepcopy(json.loads((SOURCE/'examples/artifact-inspect-result.json').read_text())['artifact'])
    if name=='catalog.get':message['page_cursor']=None
    key='example:'+name+':key' if op['idempotency_required'] else None
    if op['inner_idempotency_selector']:message['idempotency_key']=key
    expected_cut=message.get(op['source_cut_selectors'][0].removeprefix('/')) if op['source_cut_selectors'] else None
    if expected_cut is None and name not in ['lab.status','session.close','session.inspect','operation.inspect']:
        expected_cut=json.loads((SOURCE/'examples/artifact-query.json').read_text())['source_cut']
    call={'schema_version':'lab-api-call/v1-candidate','call_id':'example:'+name+':call','operation':name,'caller_context_ref':trusted['context_ref'],'expected_source_cut':expected_cut,'deadline':'2026-10-07T12:00:00Z','max_response_bytes':1000000,'idempotency_key':key,'message':message}
    directory=HERE/'examples'/name;dump(directory/'request.json',call)
    request_binding={'ref':'call:example:connection:'+call['call_id'],'sha256':sha(directory/'request.json')}
    dump(directory/'message.json',message)
    message_binding={'ref':'message:'+call['call_id'],'sha256':sha(directory/'message.json')}
    result=copy.deepcopy(json.loads((SOURCE/'examples'/f'{res_name}.json').read_text()))
    if 'request_binding' in result:result['request_binding']=message_binding
    reply={'schema_version':'lab-api-reply/v1-candidate','call_id':call['call_id'],'operation':name,'request_binding':request_binding,'trusted_context_binding':{'ref':'example:trusted-context','sha256':sha(HERE/'examples/trusted-context.json')},'handler_binding':{'ref':'example:unimplemented-handler','sha256':'0'*64},'observed_at':'2026-10-07T10:00:00Z','kind':'result','message':result}
    dump(directory/'response.json',reply)
    error=json.loads((SOURCE/'examples/error-result.json').read_text());error['request_binding']=message_binding;error['code']='invalid-contract';error['retry_policy']='no-retry'
    failed=copy.deepcopy(reply);failed.update(kind='error',message=error);dump(directory/'error-response.json',failed)
    payload={'api_version':contract['api_version'],'operation':name,'authenticated_principal_ref':trusted['principal_ref'],'authority_scope':trusted['authority_scope'],'selected_scope_refs':trusted['scope_refs'],'source_profile_binding':trusted['source_profile_binding'],'expected_source_cut':expected_cut,'message':message}
    # A demonstration binding for this restricted illustrative value subset only.
    subset=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    index.append({'operation':name,'request':str((directory/'request.json').relative_to(HERE)),'response':str((directory/'response.json').relative_to(HERE)),'error_response':str((directory/'error-response.json').relative_to(HERE)),
      'message':str((directory/'message.json').relative_to(HERE)),'wire_request_sha256':request_binding['sha256'],'message_sha256':message_binding['sha256'],'illustrative_subset_fingerprint_sha256':hashlib.sha256(subset).hexdigest(),'claim_ceiling':'Illustrative schema shape; no actual authority, signature, handler execution or operational result.'})
dump(HERE/'examples/index.json',{'schema_version':'lab-api-examples/v1-candidate','authority_effect':'none','examples':index})
for name,code,effect in [('malformed','malformed-json',False),('uncertain-timeout','deadline-exceeded',True)]:
    dump(HERE/'examples'/f'transport-{name}.json',{'schema_version':'lab-api-transport-error/v1-candidate','call_id':None if not effect else 'example:uncertain-call','request_byte_sha256':None if not effect else '0'*64,'code':code,'public_message':'Illustrative boundary error only; no real call executed.','effect_may_have_started':effect,'recovery_policy':'inspect-first' if effect else 'no-retry','authority_effect':'none'})
contract['schema_authoring_receipt_binding']=bind(SOURCE/'receipts/schema-authoring.json')
dump(HERE/'api-contracts.json',contract)
print(json.dumps({'operations':len(operations),'api_envelope_schemas':len(api_schemas),'operation_message_examples':len(operations)*3,'transport_examples':2}))
