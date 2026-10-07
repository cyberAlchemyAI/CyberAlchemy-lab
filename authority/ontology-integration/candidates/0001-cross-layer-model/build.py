#!/usr/bin/env python3
"""Build the Step 7 cross-layer ontology integration model and gap audit."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
DEF_REG=LAB/"authority/definitions/registry.json"
REL_MODEL=LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
BUSINESS=LAB/"ontology-lifecycle/business-ontology.json"
DOMAIN_REL=LAB/"ontology-lifecycle/domainspec/relationship-registry.json"
ARCH_DEC=LAB/"docs/decisions/0005-governed-ontology-node-architecture/decision.json"
LIFE_DEC=LAB/"docs/decisions/0007-ontology-lifecycle-state-vocabulary/decision.json"
ADOPT_DEC=LAB/"docs/decisions/0048-ontology-event-runtime-adoption/decision.json"
ACT_DEC=LAB/"docs/decisions/0049-ontology-event-runtime-activation/decision.json"
ACT_EXEC=LAB/"docs/decisions/0049-ontology-event-runtime-activation/receipts/execution.json"
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")

ONTOLOGY_DEFS=["ontology","ontology-node","ontology-edge","ontology-manifest","ontology-cut","ontology-view","semantic-event-history","governance-event-history","typed-relation","relation-kind"]

def current_definition(reg:dict,name:str)->dict:
 did=f"cal.definition.{name}";ref=reg["current_lookup"][did]
 row=next(x for x in reg["entries"] if x["definition_id"]==did and f"{did}@{x['version']}"==ref)
 return {"definition_ref":ref,"path":row["path"],"sha256":row["sha256"],"admission_decision_ref":row["admission_decision_ref"],"lifecycle_state":row["lifecycle_state"]}

def main()->None:
 reg=load(DEF_REG); rel=load(REL_MODEL); biz=load(BUSINESS); domain=load(DOMAIN_REL)
 definitions={name:current_definition(reg,name) for name in ONTOLOGY_DEFS}
 global_names={x["relation_kind_id"].removeprefix("relation.") for x in rel["entries"]}
 business_names={x["type"] for x in biz["relationships"]}
 domain_names={x["id"] for x in domain["signatures"]}
 token_collisions=sorted(global_names & (business_names|domain_names))
 model={
  "schema_version":"cyberalchemy-lab-ontology-cross-layer-model/v1",
  "model_id":"CAL-ONTOLOGY-INTEGRATION-CROSS-LAYER-MODEL-0001",
  "status":"candidate-owner-review-open","authority_effect":"none",
  "objective":"Integrate admitted Lab semantics, Artifact Type carriers, global Typed Relations, ontology-local subjects, event histories, projections, contexts, and the adopted bounded runtime without collapsing their identities, lifecycles, authority, or source direction.",
  "selected_foundations":{
   "architecture":{"decision_id":load(ARCH_DEC)["decision_id"],"status":load(ARCH_DEC)["status"],"path":str(ARCH_DEC.relative_to(LAB)),"sha256":sha(ARCH_DEC),"effect":"immutable-successor-planning-baseline"},
   "lifecycle":{"decision_id":load(LIFE_DEC)["decision_id"],"status":load(LIFE_DEC)["status"],"path":str(LIFE_DEC.relative_to(LAB)),"sha256":sha(LIFE_DEC),"values":["active","retired","removed"]},
   "definitions":definitions,
   "relation_model":{"path":str(REL_MODEL.relative_to(LAB)),"sha256":sha(REL_MODEL),"relation_kinds":23,"exact_endpoint_pairs":147,"status":rel["status"]},
  },
  "layers":[
   {"layer":1,"name":"Definition authority","canonical_objects":["Definition"],"effect":"Supplies admitted meaning only."},
   {"layer":2,"name":"Carrier contracts","canonical_objects":["Artifact Type","Schema"],"effect":"Permits closed shapes for future instances; creates no instance or connection."},
   {"layer":3,"name":"Global connection vocabulary","canonical_objects":["Relation Kind"],"effect":"Permits one semantic axis, exact ordered endpoint pairs, and closed qualifiers; creates no connection."},
   {"layer":4,"name":"Global connection instances","canonical_objects":["Typed Relation"],"effect":"Records one independently admitted global connection between exact artifact revisions."},
   {"layer":5,"name":"Ontology subjects","canonical_objects":["Ontology Node","Ontology Edge"],"effect":"Represents exact subjects and ontology-scoped connections inside one Ontology with separate local identities and lifecycles."},
   {"layer":6,"name":"Canonical ontology histories","canonical_objects":["Semantic Event History","Governance Event History"],"effect":"Events calculate semantic and governance state; histories remain separate and append-only."},
   {"layer":7,"name":"Calculated state and views","canonical_objects":["Ontology Cut","Ontology View","Context View"],"effect":"Rebuildable projections expose one consistent cut or bounded consumer view and are never replay sources."},
   {"layer":8,"name":"Runtime execution","canonical_objects":["adopted Rust library","authorized local CLI instance"],"effect":"Replays exact events and calculates projections inside its authorized envelope; it cannot create semantic or governance authority."},
  ],
  "cross_layer_mappings":[
   {"mapping_id":"MAP-SUBJECT-NODE","from":"artifact-instance@exact-revision","to":"ontology-node","cardinality":"0..n","required_binding":["subject_kind","subject_ref","subject_version_ref","subject_digest","ontology_ref","node_id"],"rule":"An Ontology Node represents an exact subject revision in one Ontology; it never becomes or replaces the represented artifact."},
   {"mapping_id":"MAP-GLOBAL-RELATION-EDGE","from":"typed-relation@exact-revision","to":"ontology-edge","cardinality":"0..n","required_binding":["typed_relation_ref","typed_relation_version_ref","typed_relation_digest","source_node_ref","target_node_ref"],"rule":"A projected Ontology Edge preserves the exact global connection and cannot amend it."},
   {"mapping_id":"MAP-LOCAL-EDGE","from":"ontology-local-interpretation","to":"ontology-edge","cardinality":"1..1","required_binding":["ontology_ref","relation_type_ref","source_node_ref","target_node_ref","local_scope","owner_ref","evidence_refs"],"rule":"A local Ontology Edge is canonical only inside its Ontology and cannot be used as a global Typed Relation."},
   {"mapping_id":"MAP-RELATION-KIND","from":"relation-kind","to":"typed-relation-or-projected-ontology-edge","cardinality":"1..n","required_binding":["relation_kind_ref","exact_endpoint_pair","closed_qualifiers"],"rule":"Global connections use admitted Relation Kinds. A projected edge retains that reference. A local-only edge uses a separately governed ontology-local relation type and does not silently enter the global namespace."},
   {"mapping_id":"MAP-SEMANTIC-HISTORY","from":"ontology-node-or-edge","to":"semantic-event-history","cardinality":"1..1","required_binding":["subject_identity","event_id","event_digest","graph_cursor","complete_resulting_state"],"rule":"The latest node or edge state is calculated from canonical semantic events; mutable records and projections are not replay inputs."},
   {"mapping_id":"MAP-GOVERNANCE-HISTORY","from":"exact-semantic-event","to":"governance-event-history","cardinality":"1..1","required_binding":["semantic_event_id","semantic_event_digest","semantic_cursor","governance_event_refs"],"rule":"Governance state joins only through an exact semantic event tuple and cannot patch semantic state."},
   {"mapping_id":"MAP-CUT-VIEW","from":"ontology-cut","to":"ontology-view","cardinality":"1..n","required_binding":["ontology_ref","semantic_cursor","governance_cursor_or_join_policy","source_event_set_digest","selector_ref","consumer_ref"],"rule":"A View filters one consistent Cut for a purpose and consumer; neither becomes canonical event history."},
  ],
  "identity_and_lifecycle_invariants":[
   "Artifact instance identity, Ontology Node identity, and the represented subject binding are three separate values.",
   "Typed Relation identity and Ontology Edge identity remain separate even for a projected edge.",
   "One global Typed Relation may be projected into several Ontologies; each edge has its own ontology-local lifecycle.",
   "Retiring a projected Ontology Edge does not retire its global Typed Relation; retiring a global Typed Relation does not erase historical ontology events.",
   "An ontology-local edge never becomes global through export, projection, schema validity, shared labels, or repeated use.",
   "Ontology lifecycle active, retired, removed remains independent of admission, maturity, promotion, confidence, projection freshness, and runtime activation.",
   "Semantic events change meaning-bearing state; governance events record governance posture for an exact semantic epoch and cannot rewrite it.",
   "A calculated Cut, View, snapshot, index, graph, or Markdown rendering is never accepted as canonical replay input.",
  ],
  "admission_and_effect_laws":[
   "Definition admission supplies meaning only.","Artifact Type admission supplies a carrier contract only.","Relation Kind admission permits exact pair and qualifier contracts only.","Typed Relation admission establishes one global connection only.","Appending an ontology semantic event changes one ontology-local subject state only.","Appending a governance event records governance state for one exact semantic epoch only.","Projecting a global Typed Relation into an Ontology creates no new global connection.","Calculating a Cut or View creates no semantic, governance, admission, or runtime authority.","Runtime adoption or activation executes only its exact admitted binding and cannot admit Definitions, Artifact Types, Relation Kinds, Typed Relations, nodes, or edges.",
  ],
  "relation_namespaces":[
   {"namespace":"lab-global","count":len(global_names),"authority":"Step 6 Relation Kind model","purpose":"Governed cross-artifact semantic connections","names":sorted(global_names)},
   {"namespace":"ontology-business-model","count":len(business_names),"entry_count":len(biz["relationships"]),"authority":"Ontology Lifecycle business ontology candidate/admitted epoch","purpose":"Local conceptual model structure","names":sorted(business_names)},
   {"namespace":"domainspec-development","count":len(domain_names),"entry_count":len(domain["signatures"]),"authority":"DomainSpec development profile","purpose":"Model-language signatures between DDD symbols","names":sorted(domain_names)},
  ],
  "relation_token_collisions":{"tokens":token_collisions,"rule":"Equal text across namespaces does not establish identity, equivalence, inheritance, admission, or automatic mapping. Every bridge requires an explicit mapping artifact and evidence on both sides."},
  "non_collapse_cases":[
   {"left":"Artifact Type","right":"artifact instance","reason":"Contract versus governed occurrence."},
   {"left":"artifact instance","right":"Ontology Node","reason":"Represented subject versus ontology-scoped representation."},
   {"left":"Typed Relation","right":"Ontology Edge","reason":"Global connection versus ontology-scoped projected or local connection."},
   {"left":"Relation Kind","right":"DomainSpec relationship signature","reason":"Global semantic connection contract versus modeling-language structural signature."},
   {"left":"Ontology","right":"Ontology Manifest","reason":"Governed meaning layer versus stable configuration and identity record."},
   {"left":"Ontology Node","right":"Governed Ontology Node View","reason":"Ontology subject versus calculated consumer read model."},
   {"left":"Ontology Cut","right":"Ontology View","reason":"Complete consistent state at a cursor versus purpose-bounded selection for a consumer."},
   {"left":"Ontology View","right":"Context View","reason":"Ontology-specific projection versus broader task-ready context projection that may cite several sources."},
   {"left":"Semantic Event History","right":"Governance Event History","reason":"Meaning-bearing history versus governance observation history joined to exact semantic epochs."},
   {"left":"ontology lifecycle","right":"governance status","reason":"Subject availability versus independent admission, maturity, confidence, challenge, or authority posture."},
   {"left":"canonical event history","right":"projection","reason":"Replay authority versus discardable calculated output."},
   {"left":"local relation type","right":"global Relation Kind","reason":"Ontology or modeling namespace meaning versus globally admitted connection vocabulary."},
  ],
  "runtime_state":{
   "adoption":{"decision_id":load(ADOPT_DEC)["decision_id"],"status":load(ADOPT_DEC)["status"],"authority_effect":load(ADOPT_DEC)["authority_effect"],"path":str(ADOPT_DEC.relative_to(LAB)),"sha256":sha(ADOPT_DEC)},
   "activation":{"decision_id":load(ACT_DEC)["decision_id"],"status":load(ACT_DEC)["status"],"authority_effect":load(ACT_DEC)["authority_effect"],"path":str(ACT_DEC.relative_to(LAB)),"sha256":sha(ACT_DEC),"execution_receipt_path":str(ACT_EXEC.relative_to(LAB)),"execution_receipt_sha256":sha(ACT_EXEC),"execution_result":load(ACT_EXEC)["result"]},
   "effective_boundary":"Exact adopted Rust library plus one authorized and successfully materialized local CLI instance. No daemon, persistent active service, repository enforcement, general legacy migration, cutover, publication, deployment, or external effect is established.",
  },
  "gaps":[
   {"gap_id":"ONT-GAP-001","severity":"admission-blocker","subject":"Ontology Node/v1","finding":"The candidate carrier lacks represented subject kind/ref/version/digest, closed semantic and governance facet separation, event epoch bindings, branch/profile, use obligations, and forbidden-collapse fields required by its admitted Definition and selected architecture.","recommendation":"Materialize Ontology Node/v2 and supersede v1 before Artifact Type admission."},
   {"gap_id":"ONT-GAP-002","severity":"carrier-missing","subject":"Ontology Edge","finding":"The Definition is admitted but no Artifact Type carrier exists.","recommendation":"Materialize Ontology Edge/v1 with projected-global and ontology-local modes, exact endpoints, independent identity/lifecycle, and no authority transfer."},
   {"gap_id":"ONT-GAP-003","severity":"carrier-missing","subject":"Ontology Manifest","finding":"The Definition is admitted but no Artifact Type carrier exists; Ontology/v1 is the meaning-layer aggregate and cannot substitute for its stable configuration record.","recommendation":"Materialize Ontology Manifest/v1."},
   {"gap_id":"ONT-GAP-004","severity":"carrier-missing","subject":"Ontology Cut","finding":"The Definition is admitted but no Artifact Type carrier exists.","recommendation":"Materialize Ontology Cut/v1 as a rebuildable exact-cursor calculated record that is forbidden as replay input."},
   {"gap_id":"ONT-GAP-005","severity":"carrier-missing","subject":"Ontology View","finding":"The Definition is admitted but no Artifact Type carrier exists.","recommendation":"Materialize Ontology View/v1 with consumer, selector, exact cut, event-set digest, freshness, expiry, exclusions, and claim ceiling."},
   {"gap_id":"ONT-GAP-006","severity":"carrier-missing","subject":"Semantic Event History","finding":"The Definition is admitted but no Artifact Type carrier exists.","recommendation":"Materialize Semantic Event History/v1 as an append-only subject-history manifest bound to exact event records and cursors."},
   {"gap_id":"ONT-GAP-007","severity":"carrier-missing","subject":"Governance Event History","finding":"The Definition is admitted but no Artifact Type carrier exists.","recommendation":"Materialize Governance Event History/v1 with exact semantic epoch joins and upstream Governance evidence bindings."},
   {"gap_id":"ONT-GAP-008","severity":"mapping-missing","subject":"relation namespaces","finding":"The 23 global Relation Kinds, 24 business-ontology relationships, and 28 DomainSpec signatures have no explicit namespace and bridge registry; `derives-from` collides textually.","recommendation":"Create an explicit relation namespace and bridge registry; preserve unmapped local terms."},
   {"gap_id":"ONT-GAP-009","severity":"projection-drift","subject":"selected architecture posture","finding":"Immutable proposal bytes and several consumers still say unselected or draft although CAL-GONA-0005 selected the exact digest.","recommendation":"Create a current effective-state overlay/index; do not rewrite historical proposal bytes."},
   {"gap_id":"ONT-GAP-010","severity":"semantic-reconciliation","subject":"local governed-node definition pack","finding":"The selected local pack uses OntologyRelation while the admitted integrated model uses Ontology Edge for the same scoped first-class concept.","recommendation":"Declare OntologyRelation as the Ontology Lifecycle bounded-context term mapped to global Ontology Edge; preserve local aliases and source definitions without duplicate global identity."},
  ],
  "recommended_artifact_type_actions":[
   {"action":"supersede-before-admission","artifact_type_ref":"cal.artifact-type.ontology-node/v2","definition_ref":definitions["ontology-node"]["definition_ref"],"predecessor_ref":"cal.artifact-type.ontology-node/v1"},
   *[{"action":"materialize-new","artifact_type_ref":f"cal.artifact-type.{name}/v1","definition_ref":definitions[name]["definition_ref"]} for name in ["ontology-edge","ontology-manifest","ontology-cut","ontology-view","semantic-event-history","governance-event-history"]],
  ],
  "counts":{"layers":8,"cross_layer_mappings":7,"identity_and_lifecycle_invariants":8,"admission_and_effect_laws":9,"relation_namespaces":3,"global_relation_kinds":len(global_names),"business_relationship_terms":len(business_names),"business_relationship_entries":len(biz["relationships"]),"domainspec_relationship_terms":len(domain_names),"domainspec_relationship_signatures":len(domain["signatures"]),"relation_token_collisions":len(token_collisions),"non_collapse_cases":12,"gaps":10,"artifact_type_actions":7},
  "claim_ceiling":"This candidate maps selected and admitted evidence, identifies integration gaps, and proposes seven Artifact Type actions. It does not amend a selected convention, rewrite historical bytes, admit a carrier or instance, add a relation endpoint pair, migrate an ontology, or activate a runtime.",
 }
 dump(ROOT/"integration-model.json",model)
 lines=["<!-- GENERATED FILE: canonical data is integration-model.json. -->","","# Step 7 — Ontology cross-layer integration model","",f"- Layers: `{model['counts']['layers']}`",f"- Cross-layer mappings: `{model['counts']['cross_layer_mappings']}`",f"- Non-collapse cases: `{model['counts']['non_collapse_cases']}`",f"- Gaps: `{model['counts']['gaps']}`",f"- Proposed Artifact Type actions: `{model['counts']['artifact_type_actions']}`","- Authority effect: `none`","","## Integrated flow","","```text","admitted Definition","  -> admitted Artifact Type carrier","  -> admitted artifact instance","  -> optional Ontology Node representation","","admitted Relation Kind","  -> admitted global Typed Relation","  -> optional digest-bound Ontology Edge projection","","Ontology Node / Ontology Edge semantic events","  + exact governance-event joins","  -> consistent Ontology Cut","  -> purpose-bounded Ontology View","  -> optional Context View for an Agent Session","```","","## Non-collapse rules",""]
 for x in model["non_collapse_cases"]:lines.append(f"- **{x['left']} / {x['right']}** — {x['reason']}")
 lines += ["","## Carrier actions",""]
 for x in model["recommended_artifact_type_actions"]:lines.append(f"- `{x['action']}` `{x['artifact_type_ref']}` bound to `{x['definition_ref']}`")
 lines += ["","## Gaps",""]
 for x in model["gaps"]:lines += [f"### {x['gap_id']} — {x['subject']}","",x["finding"],"",f"Recommendation: {x['recommendation']}",""]
 lines += ["## Runtime boundary","",model["runtime_state"]["effective_boundary"],"","## Claim ceiling","",model["claim_ceiling"],""]
 (ROOT/"INTEGRATION-MODEL.md").write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":main()
