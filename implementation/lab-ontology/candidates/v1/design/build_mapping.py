#!/usr/bin/env python3
"""Produce closed ontology mapping design; no ontology event is appended."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];PACKAGE=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text())
def put(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def binding(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
impact=load(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json')
kinds=sorted({c['semantic_kind'] for c in impact['carriers']}|{'artifact-type','definition','relation-kind','typed-relation'})
local={
 'cites-source':[[k,'source-file'] for k in kinds],
 'uses-contract':[[k,'artifact-type'] for k in kinds if k not in ['artifact-type','definition','relation-kind']],
 'admitted-by':[[k,'decision'] for k in kinds],
 'authorizes-recorded-effect':[['decision','source-file']],
 'defined-by':[['artifact-type','definition']],
 'implemented-by':[[k,'implementation-symbol'] for k in kinds],
 'transition-from':[['project-state','project-state']],
 'challenges-revision':[['challenge-event',k] for k in kinds],
 'uses-challenge-contract':[['challenge-event','challenge-contract']],
}
profile={'schema_version':'lab-ontology-mapping-profile/v1-candidate','profile_ref':'profile:lab-ontology-representation/v1-candidate','authority_effect':'none','replay_source':False,'executable':False,
 'scope':{'source_profile_binding':binding(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/profiles/d75/profile.json'),'selection':'Exact selected admitted/historical subject inventory; explicit candidate inputs remain candidate. Never all repository files.','carrier_inventory_binding':binding(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json'),'supported_subject_kinds':kinds,'excluded':['Private operator keys','Session short memory','Live runtime state without observation','Unselected repository files']},
 'namespaces':{'governed_subject':'lab.governed-subject','local_evidence':'lab.local-evidence','implementation_symbol':'lab.implementation-symbol'},
 'node_identity':{'fields':['ontology_ref','namespace','represented_kind','identity_ref','version_ref','represented_byte_sha256'],'encoding':'Length-prefixed UTF-8 fields hashed with SHA-256; labels never contribute. Original byte source and selected schema selectors remain separate provenance bindings.','prefix':'ontology-node:','historical_rule':'Keep distinct exact revision representations; never silently resolve a historical version to latest.','missing_exact_revision':'unresolved'},
 'domain_carrier_mappings':[{'carrier_ref':c['carrier_ref'],'semantic_kind':c['semantic_kind'],'identity_selector':c['identity_selector'],'schema_binding':{'path':c['schema_path'],'sha256':c['schema_sha256']},'write_posture':c['write_posture'],'representation':'exact-governed-subject-revision','mapping_posture':'candidate-profile; no domain alias created'} for c in impact['carriers']],
 'global_edge':{'source':'Exact admitted Typed Relation revision, resolved Relation Kind and exact ordered pair in selected effective cut.','identity_fields':['ontology_ref','typed_relation_identity_ref','typed_relation_version_ref','typed_relation_byte_sha256'],'endpoint_rule':'Resolve both exact endpoint revisions and preserve direction, qualifiers, evidence, lifecycle and admission. Invalid/unresolved endpoints remain diagnostics outside confirmed traversal.','authority_rule':'Projection is read only. Never creates an authoritative Typed Relation or expands global endpoint signatures.','eligible_admission':['admitted-current'],'historical_mode':'May show historical/withdrawn relations with explicit effective posture; exclude from current confirmed paths.','signature_source_binding':binding(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json')},
 'local_edges':{'status':'candidate closed profile; require exact profile admission before governed ontology-event use','signatures':local,'direction':'directed','authority_effect':'none','allowed_qualifiers':{'cites-source':['source_binding'],'uses-contract':['schema_binding'],'admitted-by':['decision_binding','admission_overlay_binding'],'authorizes-recorded-effect':['authorization_binding','recorded_scope'],'defined-by':['definition_binding'],'implemented-by':['source_binding','selector','alignment_evidence_binding'],'transition-from':['project_semantic_event_binding','state_digest_bindings'],'challenges-revision':['challenge_event_binding','response_state'],'uses-challenge-contract':['challenge_contract_binding']},'value_rule':'Each qualifier is an exact byte binding or an explicitly scoped source value. Text labels are never authority or executable checks.'},
 'history_domains':{'project_semantic':'Exact Project semantic history identity, cursor and digest','project_governance':'Exact Project governance history identity, cursor and digest','ontology_semantic':'Exact ontology semantic event cursor, canonical event-set digest and stream heads','ontology_governance':'Exact ontology governance event cursor and event-set digest; each governance event joins an exact semantic event identity/digest/cursor','rule':'No cross-domain cursor substitution. Missing ontology events mean no Ontology Cut or lifecycle state has been established.'},
 'challenge_join':{'event_carrier':'cal.artifact-type.challenge-event/v1','selectors':{'subject_identity':'/payload/subject_ref','subject_revision':'/payload/subject_version_ref','contract':'/payload/challenge_contract_ref','response_state':'/payload/response_state','resolution':'/payload/resolution_decision_ref'},'contract_binding':binding(ROOT/'authority/artifact-types/challenge-event/v1/schema.json'),'rules':['Resolve identity AND exact version; version mismatch is unresolved.','Pending challenges are retained separately from admission, confidence, commitment and ontology lifecycle.','A resolved challenge never establishes general truth or new action authority.']},
 'business_system_bridge':{'subject_binding':'Exact business subject revision','implementation_binding':'Exact governed Implementation revision or explicitly labeled source symbol','assertion_binding':'Exact alignment proposition and evidence revision','rule':'Source symbol discovery alone is observed material; missing alignment evidence is unresolved. No method, feature, capability or implementation collapse.'},
 'coverage':{'classification':['mapped','unresolved','excluded'],'partition_rule':'Every selected subject is classified once; each unresolved/excluded row has exact identity, reason and closing task or intentional scope exclusion.','mapped_rule':'Exact revision, namespace, source bytes, type contract, independent posture axes and required joins resolve. Mapped means representation coverage, not verified domain truth.','query_obligations':['lifecycle-slice','authority-explanation','capability-provenance'],'query_result':['complete','partial','blocked'],'limits':{'depth':4,'nodes':100,'edges':200},'truncation':'Partial with omitted frontier and continuation bound to the same source cut.','currentness':'Check all selected source/control/profile/head bindings; changed or unverified claims are excluded from confirmed current paths.'},
 'independent_axes':['carrier_contract','instance_admission','domain_state','ontology_lifecycle','confidence','commitment','challenge_state','runtime_observation','agent_session'],
 'adapter_gaps':[{'id':'O01-RUST-ADAPTER','owner_task':'O02','rule':'Translate rich Node/v2 domain record to Rust typed NodeSemanticState with exact definition selector digests, components, scope, typed properties and forbidden collapses; fail on missing fields. No generic dictionary passthrough.'},{'id':'O01-EVENT-ADMISSION','owner_task':'O03','rule':'Project histories are not ontology events; construct and separately authorize exact ontology semantic/governance events before claiming canonical Ontology Cut.'},{'id':'O01-REPRESENTED-ENDPOINTS','owner_task':'C14','rule':'Project/Product/Method semantic endpoint mappings require exact reviewed contracts and R08 outcomes.'}],
 'claim_ceiling':'Candidate mapping design only. No canonical ontology events, admitted profile, live service or complete repository coverage.'}
put(PACKAGE/'profiles/lab-ontology-profile.json',profile)
base={'ontology_ref':'example:lab-ontology','namespace':'lab.governed-subject','kind':'work','identity_ref':'example:work:inspect','version_ref':'example:work:inspect@1','represented_byte_sha256':hashlib.sha256(b'example exact revision bytes').hexdigest(),'fixture':True,'actual_admission_evidence':None}
examples=[{'case':'current',**base,'instance_admission':'admitted-current','domain_state':'in-progress','ontology_lifecycle':'not-established','classification':'mapped','allowed_path':'current representation only; no completion'}, {'case':'historical',**base,'version_ref':'example:work:inspect@0','instance_admission':'historical','domain_state':'completed','ontology_lifecycle':'not-established','classification':'mapped','allowed_path':'historical inspection only'}, {'case':'withdrawn',**base,'instance_admission':'withdrawn','domain_state':'in-progress','ontology_lifecycle':'not-established','classification':'mapped','allowed_path':'historical diagnostic; no current semantic edge'}, {'case':'challenged',**base,'instance_admission':'admitted-current','challenge_state':'pending','challenge_subject_version':'example:work:inspect@1','classification':'mapped','allowed_path':'retain pending challenge; do not infer rejection or confidence'}, {'case':'version-mismatch',**base,'challenge_subject_version':'example:work:inspect@different','classification':'unresolved','allowed_path':'diagnostic only; no silently aliased challenge path'}, {'case':'private-session-memory',**base,'kind':'session-memory','classification':'excluded','allowed_path':'never durable ontology memory'}, {'case':'missing-implementation-evidence',**base,'kind':'product-capability','classification':'unresolved','allowed_path':'source discovery may display; realization claim remains unresolved'}, {'case':'same-label-other-namespace',**base,'namespace':'lab.local-evidence','classification':'mapped','allowed_path':'distinct representation identity despite equal labels'}]
put(PACKAGE/'design/mapping-examples.json',{'authority_effect':'none','fixture_only':True,'actual_owner_outcome':None,'examples':examples})
text='''# Lab ontology mapping contract

Status: candidate design. Exact profile and mapping examples are adjacent. No ontology event has been appended.

## Selected scope and identity

Use the exact D75 source profile and its independent byte pin. The profile enumerates every registered carrier mapping and a closed set of subject kinds. Represent a subject through ontology namespace, kind, identity, exact version and byte digest. Labels are display fields. Historical revisions remain separately inspectable. Missing revisions are unresolved, never silently resolved to latest.

The ontology represents an artifact or definition; it does not become that artifact. Type contract admission, instance admission, domain completion, ontology lifecycle, confidence, commitment, challenge, runtime and Agent Session state remain independent tracks.

## Connections

A global Edge projects one exact admitted Typed Relation. It preserves relation revision, direction, both endpoint revisions, qualifiers and evidence. Invalid or unresolved connections are diagnostic and cannot support confirmed paths. A local Edge uses one profile-declared ordered signature and exact evidence; it neither creates global semantics nor expands Relation Kind endpoint pairs. Registration creates no instance edge.

The profile expands the frozen runtime's generic subject traceability signatures into explicit subject-kind pairs. New challenge joins are candidate local predicates. Their presence in this design gives no admitted ontology-event writing authority. Each actual qualifier value and claim requires its own exact evidence binding.

## Histories and Rust adapter

Project semantic/governance histories describe Lab state. Ontology semantic/governance histories describe representations. Their four cursors and digests remain distinct. A derived graph is not an Ontology Cut without actual canonical ontology events. Rust governance events join an exact semantic event ID, digest and cursor. Checkpoints and SQLite projections are discardable and cannot replace byte/event/signature verification.

Node/v2 and Rust NodeSemanticState are different contracts. O02 must explicitly translate semantic definition IDs plus selector digests, components, scope, typed properties, obligations and forbidden collapses. Missing evidence is a named gap; no generic record passthrough or fabricated confidence value is permitted.

## Challenges and implementation bridges

Join Challenge Event through both subject identity and exact subject revision, then its exact Challenge Contract and resolution Decision. Pending contest and admission remain independent. A mismatch is visible and excluded from confirmed traversal.

A business/system bridge requires the business subject revision, selected Implementation or source symbol, and evidence for the alignment assertion. A discovered source file is not demonstrated realization, use, effectiveness or live runtime.

## Coverage and queries

Partition every selected subject exactly once as mapped, unresolved or intentionally excluded. Preserve reasons and closure routes. Each query independently reports complete, partial or blocked against its declared scope and obligations. Default bounds are depth 4, 100 nodes and 200 edges; truncation must return a stable frontier at the same source cut. File count is not semantic coverage.

Lifecycle queries preserve content cursor versus admission epoch. Authority explanation describes recorded effects and never authorizes a new action. Capability provenance can establish exact lineage while realization or effectiveness remains unknown. Source changes invalidate affected current claims; historical evidence remains inspectable.

## Examples and closure

mapping-examples.json covers current, historical, withdrawn, challenged, mismatched-revision, private-session-memory, missing-implementation-evidence and equal-label/different-namespace cases. Every example is a design fixture; none claims an observed owner outcome. O02/O03 implement translation and canonical event bindings. C14 and R08 close exact semantic endpoint proposals. The current profile grants no execution or admission.
'''
(PACKAGE/'design/mapping-contract.md').write_text(text)
print(json.dumps({'carriers':len(profile['domain_carrier_mappings']),'subject_kinds':len(kinds),'local_predicates':len(local),'local_pairs':sum(len(v) for v in local.values()),'examples':len(examples),'authority_effect':'none'}))
