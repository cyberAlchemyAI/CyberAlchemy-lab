#!/usr/bin/env python3
"""Dependency-free, deterministic, check-only validator for the Define business ontology."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent.parent
REPO=PACKAGE.parents[2]
checks=[]
def add(i,o,d): checks.append({"check_id":i,"outcome":o,"detail":d})
def readj(n): return json.loads((PACKAGE/n).read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(v): return len(v)==len(set(v))
def authority_none(v):
 if isinstance(v,dict): return all((k!="authority_effect" or x=="none") and authority_none(x) for k,x in v.items())
 if isinstance(v,list): return all(authority_none(x) for x in v)
 return True
profile=readj("PROFILE.json"); sources=readj("SOURCES.json"); nodes=readj("NODES.json"); relations=readj("RELATIONS.json"); views=readj("VIEWS.json"); bindings=readj("SCHEMA-BINDINGS.json"); selection=readj("TYPE-SELECTION.json"); decision=readj("MATERIALIZATION-DECISION.json")
residue=[json.loads(x) for x in (PACKAGE/"RESIDUE.jsonl").read_text().splitlines() if x]
core=set(profile["inventory_contract"]["core_files"]); actual={str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob("*") if p.is_file() and "receipts" not in p.relative_to(PACKAGE).parts}
add("closed-package-inventory","PASS" if core==actual else "BLOCK",f"{len(actual)} material files")
add("profile-identity","PASS" if profile.get("ontology_id")=="cav2.define.business-domain.v1" and profile.get("ontology_type")=="business-domain" and profile.get("branch")=="business" and profile.get("root_node_id")=="B-DEFINE-PRODUCT-CAPABILITY" and profile.get("owner_route")=="CyberAlchemy v2 product owner" and profile.get("visibility")=="private" else "BLOCK","stable private business-domain identity")
add("materialization-decision","PASS" if decision.get("classification")=="package-required" and decision.get("package_root")=="cyberAlchemy-v2/define/business-ontology" else "BLOCK","durable package boundary")
add("type-selection","PASS" if selection.get("selected_type")=="business-domain" and selection.get("branch")=="business" else "BLOCK","explicit business-domain selection")
source_ids=[x["source_id"] for x in sources["sources"]]; add("source-id-uniqueness","PASS" if unique(source_ids) else "BLOCK",f"{len(source_ids)} exact sources")
source_ok=True
for row in sources["sources"]:
 p=(REPO/row["path"]).resolve(); source_ok &= p.is_file() and REPO in p.parents and sha(p)==row["sha256"] and p.stat().st_size==row["size_bytes"]
 if p.is_file():
  text=p.read_text(encoding="utf-8"); source_ok &= all(s in text for s in row["selectors"])
add("source-currency-and-selectors","PASS" if source_ok else "BLOCK","all exact sources and selectors are current")
node_ids=[x["id"] for x in nodes["nodes"]]; expected_nodes={"B-DEFINE-PRODUCT-CAPABILITY","B-SHARED-MEANING","B-DEFINITION-PACK","B-LANGUAGE-CONTEXT-VIEW","B-HANDLED-DEFINITION-REGISTRY","B-CONCEPT-COVERAGE","B-HUMAN-CONTROL","B-WORK-CONTINUITY","B-CONTEXT-SUFFICIENCY","B-LANGUAGE-APPLICATION","B-BOUNDED-AUTHORITY","B-PROPORTIONATE-GOVERNANCE","B-DOMAINSPEC-CONSTRUCTION-READINESS"}
node_ok=set(node_ids)==expected_nodes and unique(node_ids) and all(x["branch"]=="business" and x["role"] in profile["allowed_node_roles"] and x["status"]=="candidate" and x["authority_effect"]=="none" and all(r["source_id"] in source_ids for r in x["source_refs"]) for x in nodes["nodes"])
add("business-node-closure","PASS" if node_ok else "BLOCK",f"{len(node_ids)} extracted business nodes")
definition_pack=next((x for x in nodes["nodes"] if x["id"]=="B-DEFINITION-PACK"),{}); definition_pack_claim=str(definition_pack.get("claim","")); definition_pack_ok=all(x in definition_pack_claim for x in ("Language Context View identity","digest","source epoch","applied binding references"))
add("definition-pack-language-binding","PASS" if definition_pack_ok else "BLOCK","Definition Pack preserves the consulted view and applied bindings")
relation_ids=[x["id"] for x in relations["relations"]]; relation_ok=len(relations["relations"])==12 and unique(relation_ids) and all(x["branch"]=="business" and x["type"] in profile["allowed_relation_types"] and x["source"] in node_ids and x["target"] in node_ids and x["source"]!=x["target"] and x["authority_effect"]=="none" and all(r["source_id"] in source_ids for r in x["source_refs"]) for x in relations["relations"])
add("business-relation-closure","PASS" if relation_ok else "BLOCK",f"{len(relation_ids)} extracted typed relations")
language_edges={(x["type"],x["source"],x["target"]) for x in relations["relations"]}; required_language_edges={("consumed_by","B-LANGUAGE-CONTEXT-VIEW","B-DEFINE-PRODUCT-CAPABILITY"),("constrains","B-LANGUAGE-APPLICATION","B-DEFINE-PRODUCT-CAPABILITY")}
add("bounded-language-consultation","PASS" if required_language_edges<=language_edges and {"SRC-CAV2-GOVERNANCE-LANGUAGE","SRC-CAV2-LANGUAGE-MEANING-BINDINGS","SRC-CAV2-LANGUAGE-REALIZATION-BINDINGS","SRC-CAV2-LANGUAGE-EDGE-VOCABULARY","SRC-CAV2-LANGUAGE-AUTHORITY-BINDINGS"}<=set(source_ids) else "BLOCK","view consumption, application rule, and exact language sources")
construction_edge=("constrains","B-DOMAINSPEC-CONSTRUCTION-READINESS","B-DEFINE-PRODUCT-CAPABILITY")
construction_node=next((x for x in nodes["nodes"] if x["id"]=="B-DOMAINSPEC-CONSTRUCTION-READINESS"),{})
construction_source_selectors={row["source_id"]:set(row["selectors"]) for row in sources["sources"]}
construction_selectors_ok="## CAV2-D65: DomainSpec-Governed Construction Invariant" in construction_source_selectors.get("SRC-CAV2-DEFINITIONS",set()) and "CA2-RULE-DOMAINSPEC-GOVERNED-CONSTRUCTION" in construction_source_selectors.get("SRC-CAV2-PRODUCT-NODES",set())
construction_ok=construction_edge in language_edges and construction_selectors_ok and all(token in str(construction_node.get("claim","")) for token in ("canonical definitions","product-ontology records","capability business-ontology records","digests","owner routes","validation outcomes","residue","challenge routes")) and "DomainSpec compilation" in str(construction_node.get("forbidden_collapse",""))
add("domainspec-construction-readiness","PASS" if construction_ok else "BLOCK","Define preserves the exact D65 handoff and does not own compilation")
view=views["views"][0] if len(views.get("views",[]))==1 else {}; view_ok=view.get("branch")=="business" and set(view.get("node_ids",[]))==set(node_ids) and set(view.get("relation_ids",[]))==set(relation_ids)
add("business-view-total-coverage","PASS" if view_ok else "BLOCK","one business view covers every owned record")
residue_ok=unique([x["residue_id"] for x in residue]) and all(set(x["subject_refs"])<=set(node_ids) and set(x["source_refs"])<=set(source_ids) and x["authority_effect"]=="none" for x in residue)
add("residue-reference-closure","PASS" if residue_ok else "BLOCK",f"{len(residue)} explicit gaps")
schema=readj("schemas/ontology-package.schema.json"); schema_ok=schema.get("$schema")=="https://json-schema.org/draft/2020-12/schema" and set(schema.get("$defs",{}))>={"profile","sources","nodes","relations","views","residue"} and bindings.get("owned_schema")=="schemas/ontology-package.schema.json"
add("owned-schema-bindings","PASS" if schema_ok else "BLOCK","owned schema and record bindings")
add("authority-effect-none","PASS" if all(authority_none(x) for x in [profile,sources,nodes,relations,views,residue,bindings,selection,decision]) else "BLOCK","all package records preserve no-authority posture")
h=hashlib.sha256()
for rel in sorted(core): h.update(rel.encode()); h.update(b"\0"); h.update((PACKAGE/rel).read_bytes()); h.update(b"\0")
material=h.hexdigest(); current=[]
for p in sorted((PACKAGE/"receipts").glob("validation-*.json")) if (PACKAGE/"receipts").is_dir() else []:
 try: r=json.loads(p.read_text())
 except Exception: continue
 if r.get("material_digest")==material and r.get("overall")=="PASS" and r.get("authority_effect")=="none" and p.name==f"validation-{material[:16]}.json" and re.fullmatch(r"[0-9a-f]{64}",r.get("validation_output_sha256","")): current.append(r)
add("append-only-current-receipt","PASS" if len(current)==1 else "BLOCK",f"{len(current)} current receipt")
blocked=sum(x["outcome"]=="BLOCK" for x in checks); out={"schema_version":"cav2.define.business-ontology.validation/v1","ontology_id":profile.get("ontology_id"),"overall":"PASS" if not blocked else "BLOCK","material_digest":material,"summary":{"checks":len(checks),"passed":sum(x["outcome"]=="PASS" for x in checks),"blocked":blocked,"nodes":len(node_ids),"relations":len(relation_ids),"sources":len(source_ids),"views":len(views.get("views",[])),"residue_entries":len(residue)},"checks":checks,"claim_ceiling":"Private source-current business ontology candidate only; no measured outcome, implementation, conformance, admission, promotion, execution, publication, release, deployment, or external effect.","authority_effect":"none"}
print(json.dumps(out,indent=2,sort_keys=True)); raise SystemExit(0 if not blocked else 1)
