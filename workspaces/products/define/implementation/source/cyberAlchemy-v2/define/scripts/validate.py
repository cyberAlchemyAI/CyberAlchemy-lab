#!/usr/bin/env python3
"""Deterministic, check-only validator for the private Define bridge package."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any
PACKAGE=Path(__file__).resolve().parents[1]
REPO=PACKAGE.parents[1]
MATERIAL_FILES=("ALCHLANG-KEP-AGENT-DEFINITION-PACK.v1-candidate.json","AUTH-FOUNDATION-DEFINITION-PACK.v1-candidate.json","README.md","construction-handoffs.json","definitions.json","docs/AUTHORITY.md","docs/DEFINE.md","docs/DEFINITION-PACK.md","docs/INTERACTION.md","docs/LIFECYCLE.md","docs/PRODUCT.md","handled-definitions.json","documents.json","migration/runtime-rebinding-v1.json","migration/definition-registry-v2.json","migration/construction-handoff-v3.json","module.json","nodes.json","profile.json","relations.json","residue.jsonl","schemas/define-package.schema.json","scripts/validate.py","sources.json","views.json")
checks=[]
def add(i,o,d): checks.append({"check_id":i,"outcome":o,"detail":d})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def readj(rel): return json.loads((PACKAGE/rel).read_text(encoding="utf-8"))
def unique(v): return len(v)==len(set(v))
def authority_none(v):
 if isinstance(v,dict): return all((k!="authority_effect" or x=="none") and authority_none(x) for k,x in v.items())
 if isinstance(v,list): return all(authority_none(x) for x in v)
 return True
def child_nodes(child_id):
 if child_id=="business": return {x["id"] for x in readj("business-ontology/NODES.json")["nodes"]}
 return {x["node_id"] for x in readj("system-ontology/NODES.json")["nodes"]}
def run_child(row):
 path=PACKAGE/row["validator_path"]
 one=subprocess.run([sys.executable,str(path)],cwd=REPO,capture_output=True)
 two=subprocess.run([sys.executable,str(path)],cwd=REPO,capture_output=True)
 deterministic=one.returncode==two.returncode and one.stdout==two.stdout and one.stderr==two.stderr
 try: output=json.loads(one.stdout)
 except Exception: output={}
 expected=(0,"PASS") if row["child_id"]=="business" else (2,"FLAG")
 outcome_ok=one.returncode==expected[0] and output.get("overall")==expected[1]
 output_hash=hashlib.sha256(one.stdout).hexdigest(); material=output.get("material_digest")
 current=[]
 for rp in sorted(PACKAGE.glob(row["receipt_glob"])):
  try:r=json.loads(rp.read_text())
  except Exception:continue
  if r.get("ontology_id")==row["ontology_id"] and r.get("material_digest")==material and r.get("validation_output_sha256")==output_hash and r.get("authority_effect")=="none":current.append(r)
 return deterministic and outcome_ok and len(current)==1, one.returncode, output, output_hash, len(current)
profile=readj("profile.json"); module=readj("module.json"); sources_doc=readj("sources.json"); definitions=readj("definitions.json"); handled_definitions=readj("handled-definitions.json"); auth_definition_pack=readj("AUTH-FOUNDATION-DEFINITION-PACK.v1-candidate.json"); construction_handoffs=readj("construction-handoffs.json"); definition_registry_amendment=readj("migration/definition-registry-v2.json"); construction_handoff_amendment=readj("migration/construction-handoff-v3.json"); documents=readj("documents.json"); nodes_doc=readj("nodes.json"); relations_doc=readj("relations.json"); views_doc=readj("views.json"); migration=readj("migration/runtime-rebinding-v1.json"); schema=readj("schemas/define-package.schema.json")
residue=[json.loads(x) for x in (PACKAGE/"residue.jsonl").read_text().splitlines() if x]
# Parent inventory excludes declared nested packages, review evidence, append-only receipts, and package-local collaboration evidence.
actual=[]
for path in PACKAGE.rglob("*"):
 if not path.is_file():continue
 rel=path.relative_to(PACKAGE); top=rel.parts[0]
 if top=="receipts" or top in profile.get("nested_package_roots",[]) or top in profile.get("evidence_roots",[]) or str(rel) in profile.get("collaboration_files",[]):continue
 actual.append(str(rel))
inventory_ok=sorted(actual)==sorted(MATERIAL_FILES) and profile.get("material_files")==list(MATERIAL_FILES) and profile.get("nested_package_roots")==["business-ontology","system-ontology","capabilities"] and profile.get("evidence_roots")==["reviews","candidates"] and profile.get("collaboration_files")==[".craft/ledger.yml","CRAFT.md"]
add("closed-parent-inventory-and-nested-boundaries","PASS" if inventory_ok else "BLOCK",f"{len(actual)} parent material files; 3 excluded nested package roots; 2 excluded evidence roots")
profile_ok=profile.get("package_id")=="cav2.define" and profile.get("package_version")=="0.6.0-candidate" and profile.get("schema_version")=="cav2-define-profile/v3" and profile.get("ontology_type")=="business-system-bridge" and profile.get("current_lifecycle_state")=="candidate-authored" and profile.get("visibility")=="private" and profile.get("authority_effect")=="none" and "construction handoff or binding admission" in profile.get("blocked_effects",[]) and profile.get("registries",{}).get("handled_definitions")=="handled-definitions.json" and profile.get("registries",{}).get("construction_handoffs")=="construction-handoffs.json" and profile.get("registries",{}).get("definition_registry_amendment")=="migration/definition-registry-v2.json" and profile.get("registries",{}).get("construction_handoff_amendment")=="migration/construction-handoff-v3.json"
add("bridge-profile-identity","PASS" if profile_ok else "BLOCK","parent owns only the business-system bridge")
host=module.get("host_context",{}); source_map={x.get("id"):x for x in sources_doc.get("sources",[])}
try: product_profile=json.loads((REPO/host.get("product_ontology_profile_path","")).read_text(encoding="utf-8"))
except Exception: product_profile={}
module_ontologies=module.get("owned_ontologies",[])
module_ok=module.get("module_id")=="define" and module.get("package_root")=="cyberAlchemy-v2/define" and module.get("module_owner")==profile.get("package_owner") and module.get("visibility")=="private" and module.get("candidate_status")=="candidate" and module.get("authority_effect")=="none" and module.get("implementation_effect")=="none" and host.get("host_id")=="cyberalchemy-v2" and host.get("relationship")=="module_of" and host.get("target_path")=="cyberAlchemy-v2" and source_map.get(host.get("product_thesis_source_id"),{}).get("path")==host.get("product_thesis_path") and product_profile.get("ontology_id")==host.get("product_ontology_id")=="cav2.product-thesis" and {(x.get("id"),x.get("ontology_type"),x.get("branch")) for x in module_ontologies}=={("cav2.define.business-domain.v1","business-domain","business"),("cav2.define.system-runtime.v1","system-runtime","system"),("cav2.define","business-system-bridge","bridge")} and all(x.get("required") is True for x in module_ontologies)
add("define-module-and-cyberalchemy-product-binding","PASS" if module_ok else "BLOCK","Define specializes the bound CyberAlchemy product thesis and ontology without redefining them")
children=profile.get("child_packages",[]); child_map={x.get("child_id"):x for x in children}; child_shape=set(child_map)=={"business","system"} and all(x.get("branch")==x.get("child_id") and x.get("visibility")=="private" and x.get("authority_effect")=="none" for x in children)
add("child-package-declarations","PASS" if child_shape else "BLOCK","business and system children have explicit identity, owner, validator, and receipt bindings")
branches=profile.get("branches",[]); branch_ok={x.get("branch_id") for x in branches}=={"business","system","bridge"} and all(x.get("ownership")==("parent-package" if x.get("branch_id")=="bridge" else "child-package") for x in branches)
add("branch-ownership-separation","PASS" if branch_ok else "BLOCK","business and system are child-owned; bridge is parent-owned")
required_defs={"sourceRef","branch","childPackage","profile","source","sourceRegistry","canonicalBinding","definitionProposal","definitionRegistry","handledDefinitionReusePayload","handledDefinitionSpecializePayload","handledDefinitionProposalPayload","handledDefinitionOpenPayload","handledDefinitionRecord","handledDefinitionRegistry","definitionRegistrySchemaAmendment","constructionExactRef","constructionHandoff","constructionHandoffRegistry","constructionHandoffSchemaAmendment","moduleOntology","moduleManifest","documentAdmission","document","documentRegistry","node","nodeRegistry","relation","relationRegistry","view","viewRegistry","residueEntry","migrationSurface","migrationPhase","migration","validationReceipt"}
add("schema-definition-surface","PASS" if schema.get("$schema")=="https://json-schema.org/draft/2020-12/schema" and set(schema.get("$defs",{}))>=required_defs else "BLOCK","owned schema includes child-package and bridge bindings")
source_ids=[x["id"] for x in sources_doc.get("sources",[])]; add("source-id-uniqueness","PASS" if unique(source_ids) else "BLOCK",f"{len(source_ids)} parent evidence sources")
drift=[]; selector_fail=[]
for row in sources_doc.get("sources",[]):
 p=(REPO/row["path"]).resolve(); current=p.is_file() and REPO in p.parents and sha(p)==row["sha256"] and p.stat().st_size==row["size"]
 if not current:drift.append(row["id"]);continue
 try:text=p.read_text(encoding="utf-8")
 except Exception:text=""
 if not all(x in text for x in row["selectors"]):selector_fail.append(row["id"])
add("source-digest-and-size-currency","PASS" if not drift else "BLOCK","current" if not drift else "drift: "+", ".join(drift))
add("source-selector-resolution","PASS" if not selector_fail else "BLOCK","all selectors resolve" if not selector_fail else "missing selectors: "+", ".join(selector_fail))
# Retain the existing definition/document/migration contracts without granting promotion.
bindings=definitions.get("canonical_bindings",[]); proposals=definitions.get("proposals",[]); proposal_by_id={x.get("candidate_id"):x for x in proposals}; definition_ok=definitions.get("registry_role")=="package-vocabulary" and len(bindings)==11 and len(proposals)==4 and len(proposal_by_id)==4 and all(x.get("authority_effect")=="none" for x in bindings+proposals)
add("definition-bindings-and-candidates","PASS" if definition_ok else "BLOCK","11 canonical bindings and 4 unpromoted candidates")
registry_records=handled_definitions.get("records",[]); registry_ids=[x.get("record_id") for x in registry_records]; registry_shape=handled_definitions.get("schema_version")=="cav2-define-handled-definition-registry/v1" and handled_definitions.get("registry_id")=="cav2.define.handled-definitions" and handled_definitions.get("registry_kind")=="define-handled-definition-records" and handled_definitions.get("registry_owner_route")=="CyberAlchemy v2 product owner" and handled_definitions.get("schema_owner_route")=="CyberAlchemy v2 definitions-governance owner" and handled_definitions.get("canonical_source_ref")=="cyberAlchemy-v2/authority/definitions/DEFINITIONS.md" and handled_definitions.get("status")==(("candidate-empty") if not registry_records else "candidate") and handled_definitions.get("authority_effect")==handled_definitions.get("implementation_effect")==handled_definitions.get("promotion_effect")=="none"
record_ok=unique(registry_ids); current_keys=[]; payload_names={"reuse","specialize","propose","open"}; binding_ids={x.get("id") for x in bindings}
for row in registry_records:
 disposition=row.get("current_disposition"); present=payload_names&set(row)
 record_ok &= isinstance(row.get("record_id"),str) and bool(row.get("record_id")) and disposition in payload_names and present=={disposition} and row.get("authority_effect")=="none"
 refs=row.get("source_refs",[]); record_ok &= isinstance(refs,list) and bool(refs) and all(isinstance(x,dict) and x.get("source_id") in source_ids and isinstance(x.get("selector"),str) and bool(x.get("selector")) for x in refs)
 record_ok &= isinstance(row.get("consumer_refs"),list) and bool(row.get("consumer_refs")) and unique(row.get("consumer_refs",[])) and isinstance(row.get("decision_owner_route"),str) and bool(row.get("decision_owner_route")) and isinstance(row.get("challenge_or_refresh_route"),str) and bool(row.get("challenge_or_refresh_route"))
 if row.get("current") is True:current_keys.append((row.get("concept_id"),row.get("context_id")))
 if disposition=="reuse":
  payload=row.get("reuse",{}); record_ok &= payload.get("canonical_definition_id") in binding_ids and any(source_map.get(x.get("source_id"),{}).get("sha256")==payload.get("source_digest") for x in refs)
 elif disposition in {"specialize","propose"}:
  payload=row.get(disposition,{}); record_ok &= payload.get("status")=="candidate" and payload.get("canonical_target")=="unassigned" and all(isinstance(payload.get(k),str) and bool(payload.get(k)) for k in ("normative_voice","formal_voice","plain_language_voice","domain_context_voice","boundary","drift_route"))
  if disposition=="specialize":record_ok &= isinstance(payload.get("parent_definition_ref"),str) and bool(payload.get("parent_definition_ref")) and isinstance(payload.get("parent_source_digest"),str) and len(payload.get("parent_source_digest"))==64 and isinstance(payload.get("narrower_context"),str) and bool(payload.get("narrower_context"))
 elif disposition=="open":
  payload=row.get("open",{}); record_ok &= all(isinstance(payload.get(k),str) and bool(payload.get(k)) for k in ("question","reason","affected_use","next_action")) and isinstance(payload.get("stop_required"),bool)
record_ok &= unique(current_keys)
add("handled-definition-registry","PASS" if registry_shape and record_ok else "BLOCK",f"{len(registry_records)} handled records; registry is distinct from package vocabulary and grants no authority")
pack_concepts=auth_definition_pack.get("concepts",[]); pack_required=auth_definition_pack.get("required_concept_ids",[]); pack_ids=[x.get("concept_id") for x in pack_concepts]; pack_record_refs=[x.get("handled_definition_ref") for x in pack_concepts]
pack_relations=auth_definition_pack.get("relationships",[]); pack_relation_ids=[x.get("relation_id") for x in pack_relations]; language_application=auth_definition_pack.get("language_application",{}); pack_sources=auth_definition_pack.get("source_refs",[]); pack_checks=auth_definition_pack.get("checks",[])
pack_requirement={"goal":auth_definition_pack.get("goal"),"limits":auth_definition_pack.get("goal_limits"),"required_concept_ids":pack_required}; pack_candidate={"context_id":auth_definition_pack.get("context",{}).get("context_id"),"source_digest":source_map.get("SRC-AUTH-BUSINESS-MEANING-V2",{}).get("sha256"),"concept_record_ids":pack_record_refs}; packed_digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
pack_ok=auth_definition_pack.get("contract_ref")=="docs/DEFINITION-PACK.md" and auth_definition_pack.get("schema_version")=="cav2-define-definition-pack/v1-candidate" and auth_definition_pack.get("pack_id")=="DEFINE-PACK-AUTH-EXACT-SESSION-ROLE-PERMISSION-001" and auth_definition_pack.get("status")=="candidate" and auth_definition_pack.get("define_session",{}).get("state")=="saved-candidate" and auth_definition_pack.get("context",{}).get("context_id")=="AUTH-FOUNDATION-EXACT-SESSION-ROLE-PERMISSION" and auth_definition_pack.get("context_sufficiency",{}).get("status")=="sufficient-for-candidate-definition"
pack_ok &= auth_definition_pack.get("context_sufficiency",{}).get("requirement_digest")==packed_digest(pack_requirement) and auth_definition_pack.get("context_sufficiency",{}).get("candidate_digest")==packed_digest(pack_candidate)
pack_ok &= len(pack_concepts)==len(pack_required)==len(registry_records)==20 and unique(pack_ids) and set(pack_ids)==set(pack_required) and unique(pack_record_refs) and set(pack_record_refs)==set(registry_ids) and all(x.get("current_disposition")=="propose" for x in pack_concepts)
pack_ok &= unique(pack_relation_ids) and all(x.get("source_concept_id") in set(pack_ids) and x.get("target_concept_id") in set(pack_ids) and x.get("relation")=="depends_on" for x in pack_relations)
pack_ok &= language_application.get("language_project_ref")=="CA2-PROJECT-LANGUAGE" and language_application.get("language_context_view_ref") is None and language_application.get("language_context_view_status")=="missing-for-auth-context" and language_application.get("applied_binding_refs")==[] and isinstance(language_application.get("exposed_gap"),str) and bool(language_application.get("exposed_gap"))
pack_ok &= all(isinstance(x,dict) and x.get("source_id") in source_ids and isinstance(x.get("selector"),str) and bool(x.get("selector")) for x in pack_sources) and {x.get("outcome") for x in pack_checks}=={"PASS","PASS_WITH_EXPOSED_GAP"} and len(auth_definition_pack.get("open_questions_and_conflicts",[]))==3 and all(auth_definition_pack.get(k)=="none" for k in ("authority_effect","implementation_effect","promotion_effect"))
add("auth-definition-pack-candidate","PASS" if pack_ok else "BLOCK",f"{len(pack_concepts)} proposed concepts with exact handled-record coverage; missing Auth Language Context View remains explicit")
amendment_ok=definition_registry_amendment.get("amendment_id")=="CAV2-DEFINE-SCHEMA-AMEND-DEFINITION-REGISTRY-001" and definition_registry_amendment.get("from_package_schema")=="https://cyberalchemy.local/private/schemas/define-package/v1" and definition_registry_amendment.get("to_package_schema")=="https://cyberalchemy.local/private/schemas/define-package/v2" and definition_registry_amendment.get("from_profile_schema")=="cav2-define-profile/v1" and definition_registry_amendment.get("to_profile_schema")=="cav2-define-profile/v2" and definition_registry_amendment.get("from_package_version")=="0.4.0-candidate" and definition_registry_amendment.get("to_package_version")=="0.5.0-candidate" and definition_registry_amendment.get("authority_effect")=="none"
add("definition-registry-schema-amendment","PASS" if amendment_ok else "BLOCK","explicit no-effect v1 to v2 package transition")
handoffs=construction_handoffs.get("handoffs",[])
handoff_ok=construction_handoffs.get("schema_version")=="cav2-define-construction-handoff-registry/v1" and construction_handoffs.get("registry_id")=="cav2.define.construction-handoffs" and construction_handoffs.get("canonical_definition_ref")=="CAV2-D65" and construction_handoffs.get("project_ref")=="CA2-PROJECT-DEFINE" and construction_handoffs.get("source_branch_ref")=="business::B-DOMAINSPEC-CONSTRUCTION-READINESS" and construction_handoffs.get("target_domainspec_project_ref")=="system-ontology/domainspec-project/project.json" and construction_handoffs.get("status")=="candidate-empty-blocked" and construction_handoffs.get("validation_mode")=="review-only" and handoffs==[] and all(construction_handoffs.get(k)=="none" for k in ("authority_effect","enforcement_effect","implementation_effect"))
add("construction-handoff-registry","PASS" if handoff_ok else "BLOCK","empty and blocked; full ConstructionBinding ownership remains with Project")
handoff_amendment_ok=construction_handoff_amendment.get("amendment_id")=="CAV2-DEFINE-SCHEMA-AMEND-CONSTRUCTION-HANDOFF-001" and construction_handoff_amendment.get("from_package_schema")=="https://cyberalchemy.local/private/schemas/define-package/v2" and construction_handoff_amendment.get("to_package_schema")=="https://cyberalchemy.local/private/schemas/define-package/v3" and construction_handoff_amendment.get("from_profile_schema")=="cav2-define-profile/v2" and construction_handoff_amendment.get("to_profile_schema")=="cav2-define-profile/v3" and construction_handoff_amendment.get("from_package_version")=="0.5.0-candidate" and construction_handoff_amendment.get("to_package_version")=="0.6.0-candidate" and construction_handoff_amendment.get("authority_effect")=="none"
add("construction-handoff-schema-amendment","PASS" if handoff_amendment_ok else "BLOCK","explicit no-effect v2 to v3 package transition")
docs=documents.get("documents",[]); docs_ok=len(docs)==6 and documents.get("canonical_admission",{}).get("status")=="blocked"
for row in docs:
 p=PACKAGE/row.get("path",""); text=p.read_text(encoding="utf-8") if p.is_file() else ""; docs_ok &= text.startswith("# "+row.get("title","")+"\n") and all(h in text for h in row.get("required_headings",[])) and row.get("canonical_status")=="not-admitted" and row.get("authority_effect")=="none"
add("perennial-document-closure","PASS" if docs_ok else "BLOCK","six non-admitted perennial candidate documents, including the Define product thesis")
phase_ids=[x.get("id") for x in migration.get("phases",[])]; migration_ok=phase_ids==["define-contract-pinned","alch-runtime-compiled","local-runtime-tests-passed","runtime-package-rebound","behavioral-conformance-assessed","runtime-adopted"] and migration.get("external_change",{}).get("status")=="not-performed" and migration.get("authority_effect")=="none"
add("runtime-rebinding-order-and-authority-ceiling","PASS" if migration_ok else "BLOCK","standalone runtime is rebound; conformance and adoption remain pending")
# Validate child identities before resolving qualified endpoints.
child_profile_ok=True
for cid,row in child_map.items():
 try: cp=readj(row["profile_path"])
 except Exception: child_profile_ok=False;continue
 child_profile_ok &= cp.get("ontology_id")==row["ontology_id"] and cp.get("ontology_type")==row["ontology_type"] and cp.get("branch")==row["branch"] and cp.get("owner_route")==row["owner_route"] and cp.get("visibility")==row["visibility"] and cp.get("authority_effect")=="none"
add("child-profile-identity-bindings","PASS" if child_profile_ok else "BLOCK","declared child identities match exact profiles")
business_ids=child_nodes("business"); system_ids=child_nodes("system"); external={*("business::"+x for x in business_ids),*("system::"+x for x in system_ids)}
local_nodes=nodes_doc.get("nodes",[]); local_ids={x.get("id") for x in local_nodes}; local_ok=len(local_nodes)==2 and local_ids=={"BR-DEFINE-PRODUCT-RUNTIME","BR-DEFINE-DOMAINSPEC-CONSTRUCTION-HANDOFF"} and all(x.get("branch")=="bridge" and x.get("role")=="alignment" and x.get("authority_effect")=="none" for x in local_nodes)
add("parent-bridge-node-ownership","PASS" if local_ok else "BLOCK",f"{len(local_nodes)} parent-owned bridge nodes; no duplicate business/system nodes")
rels=relations_doc.get("relations",[]); rel_ids=[x.get("id") for x in rels]; universe=local_ids|external
rel_ok=len(rels)==13 and unique(rel_ids) and all(x.get("branch")=="bridge" and x.get("source") in universe and x.get("target") in universe and x.get("source")!=x.get("target") and x.get("type") in profile.get("allowed_relation_types",[]) and x.get("authority_effect")=="none" and all(r.get("source_id") in source_ids for r in x.get("source_refs",[])) for x in rels)
add("cross-package-relation-endpoint-closure","PASS" if rel_ok else "BLOCK",f"{len(rels)} bridge relations close over current child records")
construction_edges={
 ("BR-DEFINE-PRODUCT-RUNTIME","BR-DEFINE-DOMAINSPEC-CONSTRUCTION-HANDOFF","aligns"),
 ("business::B-DOMAINSPEC-CONSTRUCTION-READINESS","BR-DEFINE-DOMAINSPEC-CONSTRUCTION-HANDOFF","targets"),
 ("BR-DEFINE-DOMAINSPEC-CONSTRUCTION-HANDOFF","system::define-session-runtime.DefineSessionWorkflow","targets"),
}
observed_construction_edges={(x.get("source"),x.get("target"),x.get("type")) for x in rels if x.get("id") in {"E-BR-ROOT-ALIGNS-CONSTRUCTION-HANDOFF","E-BR-BUSINESS-TARGETS-CONSTRUCTION-HANDOFF","E-BR-CONSTRUCTION-HANDOFF-TARGETS-DOMAINSPEC"}}
add("construction-handoff-bridge-boundary","PASS" if observed_construction_edges==construction_edges else "BLOCK","exact business-to-DomainSpec handoff projection; no compiler or generated-output edge")
views=views_doc.get("views",[]); view=views[0] if len(views)==1 else {}; view_ok=view.get("branch")=="bridge" and set(view.get("relation_ids",[]))==set(rel_ids) and set(view.get("node_ids",[]))=={x for r in rels for x in (r.get("source"),r.get("target"))}
add("bridge-view-total-coverage","PASS" if view_ok else "BLOCK","one parent bridge view covers all edges and endpoints")
subject_universe=universe|local_ids|{x.get("candidate_id") for x in proposals}|{x.get("id") for x in bindings}|{x.get("id") for x in docs}|set(registry_ids)|{"cav2.define",migration.get("migration_id"),handled_definitions.get("registry_id"),construction_handoffs.get("registry_id"),definition_registry_amendment.get("amendment_id"),construction_handoff_amendment.get("amendment_id")}
residue_ok=unique([x.get("id") for x in residue]) and all(set(x.get("subject_refs",[]))<=subject_universe and all(r.get("source_id") in source_ids for r in x.get("source_refs",[])) and x.get("authority_effect")=="none" for x in residue)
add("residue-reference-closure","PASS" if residue_ok else "BLOCK",f"{len(residue)} residue records including 2 unsupported former bridge claims")
child_runs={}
for cid,row in child_map.items():
 ok,code,out,out_hash,current=run_child(row); child_runs[cid]={"exit":code,"overall":out.get("overall"),"output_sha256":out_hash,"current_receipts":current}; add(f"child-validator-and-current-receipt:{cid}","PASS" if ok else "BLOCK",f"exit {code}, {out.get('overall')}, {current} current receipt, deterministic two-run output")
all_docs=[profile,module,sources_doc,definitions,handled_definitions,auth_definition_pack,construction_handoffs,definition_registry_amendment,construction_handoff_amendment,documents,nodes_doc,relations_doc,views_doc,residue,migration]
add("authority-effect-none","PASS" if all(authority_none(x) for x in all_docs) else "BLOCK","no parent, child binding, model, residue, or migration record grants authority")
# Historical parent receipts stay immutable history and need not match the new bridge bytes.
history=[]; history_ok=True
for rp in sorted((PACKAGE/"receipts").glob("validation-*.json")):
 try:r=json.loads(rp.read_text())
 except Exception:history_ok=False;continue
 history.append(rp.name); history_ok &= r.get("package_id")=="cav2.define" and r.get("authority_effect")=="none" and r.get("status")=="pass"
add("historical-receipt-integrity","PASS" if history_ok else "BLOCK",f"{len(history)} immutable historical PASS receipts; none stretched over current bytes")
h=hashlib.sha256()
for rel in sorted(MATERIAL_FILES):h.update(rel.encode());h.update(b"\0");h.update((PACKAGE/rel).read_bytes());h.update(b"\0")
blocked=sum(x["outcome"]=="BLOCK" for x in checks); out={"schema_version":"cav2-define-validation/v3","package_id":"cav2.define","package_version":profile.get("package_version"),"overall":"PASS" if not blocked else "BLOCK","material_digest":h.hexdigest(),"summary":{"checks":len(checks),"passed":sum(x["outcome"]=="PASS" for x in checks),"blocked":blocked,"parent_nodes":len(local_nodes),"bridge_relations":len(rels),"handled_definition_records":len(registry_records),"construction_handoffs":len(handoffs),"views":len(views),"residue":len(residue),"source_drift":len(drift)},"child_runs":child_runs,"checks":checks,"blockers":[{"kind":"source-drift","source_ids":drift}] if drift else [],"authority_effect":"none","claim_ceiling":"Cross-package structure, handled-definition and empty construction-handoff registry shapes, source checks, and bridge traceability only; no ConstructionBinding, compiler output, generated system ontology, definition promotion, registry runtime, child promotion, implementation, conformance, acceptance, execution, publication, release, deployment, migration, or external effect."}
print(json.dumps(out,indent=2,sort_keys=True));raise SystemExit(0 if not blocked else 1)
