#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[3]
GEN=LAB/"tooling/generators/artifact_surface.py"
def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")

spec=importlib.util.spec_from_file_location("g",GEN); g=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(g)

ROOT_V1="authority/artifact-types/artifact-type/v1/artifact.json"; ROOT_V2="authority/artifact-types/artifact-type/v2/artifact.json"; FOUNDATION_SCHEMA="authority/foundation/v1/schema.json"
specs=[
 ("cal.artifact-type.artifact-type/v1","artifact-type",ROOT_V1,"authority/artifact-types/artifact-type/v1/schema.json",None,"cyberalchemy-lab-artifact-type/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-historical",[]),
 ("cal.artifact-type.lifecycle-profile/v1","lifecycle-profile",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/lifecycleProfile","cyberalchemy-lab-lifecycle-profile/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.evaluation-profile/v1","evaluation-profile",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/evaluationProfile","cyberalchemy-lab-evaluation-profile/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.owner-registry/v1","owner-registry",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/ownerRegistry","cyberalchemy-lab-owner-registry/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.source-admission/v1","source-admission",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/sourceAdmissions","cyberalchemy-lab-source-admission-candidates/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.definition-registry/v1","definition-registry",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/definitionRegistry","cyberalchemy-lab-definition-registry/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.drift-audit/v1","drift-audit",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/driftAudit","cyberalchemy-lab-definition-drift-audit/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.foundation-manifest/v1","foundation-manifest",ROOT_V1,FOUNDATION_SCHEMA,"#/$defs/manifest","cyberalchemy-lab-foundation-manifest/v1","CAL-DECISION-0013-FOUNDATION-01-ADMISSION","admitted-current",[]),
 ("cal.artifact-type.definition/v1","definition","authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json","authority/artifact-types/definition/v1/schema.json",None,"cyberalchemy-lab-definition/v1","CAL-DECISION-0015-DEFINITION-V1-ADMISSION","admitted-current",["cal.definition.definition@1.0.0-candidate.1"]),
 ("cal.artifact-type.bounded-context/v1","bounded-context","authority/artifact-types/bounded-context/v1/artifact.json","authority/artifact-types/bounded-context/v1/schema.json",None,"cyberalchemy-lab-bounded-context/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-historical",["cal.definition.bounded-context@1.0.0-candidate.1"]),
 ("cal.artifact-type.ubiquitous-language/v1","ubiquitous-language","authority/artifact-types/ubiquitous-language/v1/artifact.json","authority/artifact-types/ubiquitous-language/v1/schema.json",None,"cyberalchemy-lab-ubiquitous-language/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.ubiquitous-language@1.0.0-candidate.1"]),
 ("cal.artifact-type.capability-instance/v1","capability-instance","authority/artifact-types/capability-instance/v1/artifact.json","authority/artifact-types/capability-instance/v1/schema.json",None,"cyberalchemy-lab-capability-instance/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.capability-instance@1.0.0-candidate.1"]),
 ("cal.artifact-type.coordination-context/v1","coordination-context","authority/artifact-types/coordination-context/v1/artifact.json","authority/artifact-types/coordination-context/v1/schema.json",None,"cyberalchemy-lab-coordination-context/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.coordination-context@1.0.0-candidate.1"]),
 ("cal.artifact-type.context-map/v1","context-map","authority/artifact-types/context-map/v1/artifact.json","authority/artifact-types/context-map/v1/schema.json",None,"cyberalchemy-lab-context-map/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-historical",["cal.definition.context-map@1.0.0-candidate.1"]),
 ("cal.artifact-type.context-migration-manifest/v1","context-migration-manifest","authority/artifact-types/context-migration-manifest/v1/artifact.json","authority/artifact-types/context-migration-manifest/v1/schema.json",None,"cyberalchemy-lab-context-migration-manifest/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.context-migration-manifest@1.0.0-candidate.1"]),
 ("cal.artifact-type.context-lineage-record/v1","context-lineage-record","authority/artifact-types/context-lineage-record/v1/artifact.json","authority/artifact-types/context-lineage-record/v1/schema.json",None,"cyberalchemy-lab-context-lineage-record/v1","CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.context-lineage-record@1.0.0-candidate.1"]),
 ("cal.artifact-type.bounded-context/v2","bounded-context","authority/artifact-types/bounded-context/v2/artifact.json","authority/artifact-types/bounded-context/v2/schema.json",None,"cyberalchemy-lab-bounded-context/v2","CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.bounded-context@2.0.0-candidate.1"]),
 ("cal.artifact-type.context-map/v2","context-map","authority/artifact-types/context-map/v2/artifact.json","authority/artifact-types/context-map/v2/schema.json",None,"cyberalchemy-lab-context-map/v2","CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION","admitted-current",["cal.definition.context-map@2.0.0-candidate.1"]),
 ("cal.artifact-type.artifact-type/v2","artifact-type",ROOT_V2,"authority/artifact-types/artifact-type/v2/schema.json",None,"cyberalchemy-lab-artifact-type/v2","CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1","admitted-current",["cal.definition.artifact-type@1.0.0-candidate.1"]),
 ("cal.artifact-type.product-identity/v1","product-identity","authority/artifact-types/product-identity/v1/artifact.json","authority/artifact-types/product-identity/v1/schema.json",None,"cyberalchemy-lab-product-identity/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["cal.definition.product@1.0.0-candidate.1","cal.definition.identity-carrier@1.0.0-candidate.1"]),
 ("cal.artifact-type.project-identity/v1","project-identity","authority/artifact-types/project-identity/v1/artifact.json","authority/artifact-types/project-identity/v1/schema.json",None,"cyberalchemy-lab-project-identity/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["CAV2-D60@1.0.0-candidate.1","cal.definition.identity-carrier@1.0.0-candidate.1"]),
 ("cal.artifact-type.method-binding/v1","method-binding","authority/artifact-types/method-binding/v1/artifact.json","authority/artifact-types/method-binding/v1/schema.json",None,"cyberalchemy-lab-method-binding/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["CAV2-D20@1.0.0-candidate.1","cal.definition.identity-relation@1.0.0-candidate.1"]),
 ("cal.artifact-type.goal/v1","goal","authority/artifact-types/goal/v1/artifact.json","authority/artifact-types/goal/v1/schema.json",None,"cyberalchemy-lab-goal/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["CAV2-D59@1.0.0-candidate.1","cal.definition.identity-carrier@1.0.0-candidate.1"]),
 ("cal.artifact-type.identity-graph/v1","identity-graph","authority/artifact-types/identity-graph/v1/artifact.json","authority/artifact-types/identity-graph/v1/schema.json",None,"cyberalchemy-lab-identity-graph/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["cal.definition.identity-relation@1.0.0-candidate.1"]),
 ("cal.artifact-type.identity-lineage/v1","identity-lineage","authority/artifact-types/identity-lineage/v1/artifact.json","authority/artifact-types/identity-lineage/v1/schema.json",None,"cyberalchemy-lab-identity-lineage/v1","CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1","admitted-current",["cal.definition.identity-lineage@1.0.0-candidate.1"]),
]

def build_registry():
 entries=[]
 for ref,kind,ap,sp,selector,disc,decision,state,defs in specs:
  entries.append({"artifact_type_ref":ref,"lifecycle_state":state,"semantic_kind":kind,"artifact_path":ap,"artifact_sha256":sha(LAB/ap),"schema_path":sp,"schema_selector":selector,"schema_sha256":sha(LAB/sp),"instance_discriminator":{"path":"/schema_version","value":disc},"semantic_definition_refs":defs,"admission_decision_ref":decision})
 return {"schema_version":"cyberalchemy-lab-artifact-type-registry/v1","registry_id":"cal.registry.artifact-types/v1-candidate.1","version":"1.0.0-test-candidate.1","status":"candidate-postimage","authority_effect":"none","owner_ref":"role:artifact-type-owner","entries":entries,"source_direction":{"canonical":"registry.json","human_projection":"REGISTRY.md","projection_policy":"generated-only","generator_ref":"cal.generator.artifact-surface/v1"},"claim_ceiling":"Candidate postimage reconstructing 25 exact decision-admitted Artifact Type versions. It is not the live registry and cannot change lifecycle state."}

def build_audit():
 findings=[
  {"finding_id":"ASF-AUDIT-001","classification":"resolved-by-admitted-type","path":"contexts/","statement":"The 17 principal Context carriers inspected have explicit admitted Artifact Type references.","treatment":"Preserve; package-home manifests remain later work."},
  {"finding_id":"ASF-AUDIT-002","classification":"resolvable-by-registry-discriminator","path":"coordination/goals/craft-product-foundation/v1/goal.json","statement":"Goal resolves through schema_version to admitted Goal/v1 without directory inference.","treatment":"Preserve; later declare its package home."},
  {"finding_id":"ASF-AUDIT-003","classification":"resolvable-by-registry-discriminator","path":"coordination/projects/craft/v1/project.json","statement":"Project resolves through schema_version to admitted Project Identity/v1.","treatment":"Preserve; later declare its package home."},
  {"finding_id":"ASF-AUDIT-004","classification":"resolvable-by-registry-discriminator","path":"product/products/ontology/v1/product.json","statement":"Ontology Product resolves through schema_version to admitted Product Identity/v1.","treatment":"Preserve; do not infer Product ownership for sibling files."},
  {"finding_id":"ASF-AUDIT-005","classification":"unresolved-first-class-candidate","path":"product/products/ontology/v1/source-closure.json","statement":"Source Closure has no admitted Artifact Type mapping.","treatment":"Owner must choose declared component or Artifact Type Request; no automatic type creation."},
  {"finding_id":"ASF-AUDIT-006","classification":"unresolved-first-class-candidate","path":"product/products/ontology/v1/product-ontology/ontology.json","statement":"Product Ontology has no admitted Artifact Type mapping.","treatment":"Route through exact semantic/type analysis before canonical use."},
  {"finding_id":"ASF-AUDIT-007","classification":"unresolved-first-class-candidate","path":"implementation/bindings/ontology-product-lifecycle/v1/binding.json","statement":"Runtime Binding has no admitted Artifact Type mapping.","treatment":"Likely Artifact Type Request; owner must confirm distinct validation purpose."},
  {"finding_id":"ASF-AUDIT-008","classification":"candidate-type-not-admitted","path":"authority/artifact-types/ontology-package/v1/artifact.json","statement":"Ontology Package/v1 exists physically but is absent from the admitted registry postimage.","treatment":"Keep candidate-only; do not consume as an admitted type."},
  {"finding_id":"ASF-AUDIT-009","classification":"nested-package-decision-open","path":"product/products/ontology/v1/product-ontology/source-package/","statement":"The nested source package has migration, generator, validator, imported sources, and evidence but no explicit lifecycle-owner/unit-of-change declaration.","treatment":"Do not infer independence; decide during package-manifest authoring."}
 ]
 return {"schema_version":"cyberalchemy-lab-artifact-surface-audit/v1","audit_id":"CAL-ARTIFACT-SURFACE-AUDIT-0001","title":"Selected current-tree Artifact Surface audit","status":"candidate-diagnostic","result":"complete-with-visible-residue","authority_effect":"none","scope":["authority","contexts","coordination","product/products/ontology/v1","implementation/bindings/ontology-product-lifecycle/v1"],"findings":findings,"claim_ceiling":"Selected-surface diagnostic only. It does not establish repository-wide conformance, decide whether unresolved files are components or Artifact instances, or authorize migration."}

def render_candidate(c):
 lines=["<!-- GENERATED FILE: canonical data is candidate.json. -->","",f"# {c['candidate_id']}","",f"- Version: `{c['version']}`",f"- Status: `{c['status']}`",f"- Authority effect: `{c['authority_effect']}`","","## Product-construction frontier","",c['construction']['product_frontier'],"","## Runnable product work",""]
 lines += [f"- {x}" for x in c['construction']['runnable_product_work']]; lines += ["","## Operational support",""]
 lines += [f"- `{x['owner_ref']}` — {x['task']} Stage: {x['affected_stage']}; blocks frontier: `{str(x['blocks_current_frontier']).lower()}`." for x in c['construction']['operational_support']]
 lines += ["","## Causal blockers",""]+[f"- {x}" for x in c['construction']['causal_blockers']]+["","## Claim ceiling","",c['claim_ceiling']]
 return "\n".join(lines).rstrip()+"\n"

def build_manifest():
 paths=[]
 definition_root=LAB/"authority/definitions/candidates/0009-artifact-surface-foundation"
 for p in definition_root.rglob("*"):
  if p.is_file() and "receipts" not in p.parts and "__pycache__" not in p.parts: paths.append(p)
 for name in ["artifact-type-registry","artifact-type-request","canonical-package-manifest"]:
  base=LAB/f"authority/artifact-types/{name}/v1"
  for p in base.rglob("*"):
   if p.is_file() and "receipts" not in p.parts and "__pycache__" not in p.parts: paths.append(p)
 paths += [LAB/"tooling/generators/artifact_surface.py",LAB/"tooling/validators/artifact_surface.py",LAB/"tests/conformance/artifact-surface-foundation/suite.json"]
 for name in ["candidate.json","CANDIDATE.md","build.py","validate.py","registry.json","REGISTRY.md","audit.json","AUDIT.md"]: paths.append(ROOT/name)
 unique=sorted(set(paths),key=lambda p:str(p.relative_to(LAB)))
 return {"schema_version":"cyberalchemy-lab-candidate-byte-manifest/v1","manifest_id":"CAL-ARTIFACT-SURFACE-FOUNDATION-MANIFEST-0001","candidate_id":"CAL-ARTIFACT-SURFACE-FOUNDATION-0001","status":"candidate-digest-closure","authority_effect":"none","materials":[{"path":str(p.relative_to(LAB)),"sha256":sha(p)} for p in unique],"source_direction":{"canonical":"manifest.json","human_projection":"MANIFEST.md","projection_policy":"generated-only","generator":"build.py"},"claim_ceiling":"Digest closure for candidate review only. It does not approve, admit, activate, migrate, commit, push, publish, release, or deploy any material."}

def render_manifest(m):
 lines=["<!-- GENERATED FILE: canonical data is manifest.json. -->","","# Artifact Surface Foundation candidate manifest","",f"- Manifest: `{m['manifest_id']}`",f"- Candidate: `{m['candidate_id']}`",f"- Materials: `{len(m['materials'])}`","","| Path | SHA-256 |","| --- | --- |"]
 lines += [f"| `{x['path']}` | `{x['sha256']}` |" for x in m["materials"]]
 lines += ["","## Claim ceiling","",m["claim_ceiling"]]
 return "\n".join(lines).rstrip()+"\n"

if __name__=="__main__":
 reg=build_registry(); dump(ROOT/"registry.json",reg); (ROOT/"REGISTRY.md").write_text(g.render_registry(reg))
 audit=build_audit(); dump(ROOT/"audit.json",audit); (ROOT/"AUDIT.md").write_text(g.render_audit(audit))
 c=load(ROOT/"candidate.json"); (ROOT/"CANDIDATE.md").write_text(render_candidate(c))
 manifest=build_manifest(); dump(ROOT/"manifest.json",manifest); (ROOT/"MANIFEST.md").write_text(render_manifest(manifest))
