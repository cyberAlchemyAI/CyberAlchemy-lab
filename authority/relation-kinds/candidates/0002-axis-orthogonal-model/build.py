#!/usr/bin/env python3
"""Build the axis-orthogonal successor to the initial complete relation catalog."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
PREDECESSOR = ROOT.parent / "0001-complete-relation-model"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
EXTENSION_DEFINITION = LAB / "authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/definition.json"
EXTENSION_DEFINITION_VALIDATION = LAB / "authority/definitions/candidates/0012-typed-connection-extension-rule/receipts/validation.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


AXES = [
    {"id": "relation.member-of", "group": "structure", "question": "Which governed container or scope is this member part of?", "effect": "Records scoped membership or composition in member-to-container direction without transferring identity or authority.", "sources": ["*"], "targets": ["product", "project", "team", "ontology", "role", "*"], "qualifiers": ["membership_role"], "forbids": ["contribution", "assignment", "authority", "identity-equivalence"]},
    {"id": "relation.contributes-to", "group": "purpose", "question": "Which Product or Goal is this activity intended to advance?", "effect": "Records intended contribution without proving success, realization, or value.", "sources": ["project", "research-inquiry", "research-run", "experiment-design", "experiment-run"], "targets": ["product", "goal"], "qualifiers": ["contribution_role", "contribution_scope"], "forbids": ["membership", "realization", "evaluation-result", "product-value"]},
    {"id": "relation.uses-method", "group": "dependency", "question": "Which Method does this subject depend on or employ?", "effect": "Records Method dependency without implying conformance, realization, or success.", "sources": ["research-run", "experiment-run", "measurement-result", "observation", "project", "product"], "targets": ["method"], "qualifiers": ["usage_role"], "forbids": ["conformance", "realization", "validation", "achievement"]},
    {"id": "relation.evaluates", "group": "evaluation", "question": "Which subject or proposition is being assessed?", "effect": "Records evaluation scope without deciding evidence polarity, adoption, realization, or value.", "sources": ["evaluation", "experiment-design", "experiment-run"], "targets": ["*"], "qualifiers": ["evaluation_role", "evaluation_purpose"], "forbids": ["support", "contradiction", "adoption", "realization", "product-value"]},
    {"id": "relation.realizes", "group": "realization", "question": "Which declared design or capability is concretely instantiated by this subject?", "effect": "Records realization or execution without implying conformance, effectiveness, adoption, or evidence acceptance.", "sources": ["implementation", "experiment-run"], "targets": ["product-capability", "experiment-design"], "qualifiers": ["realization_role", "exact_target_version_ref"], "forbids": ["conformance", "effectiveness", "adoption", "support"]},
    {"id": "relation.engages-inquiry", "group": "research", "question": "How does this research carrier engage a Research Inquiry?", "effect": "Records whether an activity addresses or a Finding answers an Inquiry without converting either into the other.", "sources": ["research-run", "experiment-design", "experiment-run", "finding"], "targets": ["research-inquiry"], "qualifiers": ["inquiry_role"], "forbids": ["finding-acceptance", "evidence-support", "inquiry-completion"]},
    {"id": "relation.originates-from", "group": "lineage", "question": "From which source did this identity or content originate?", "effect": "Records origin lineage without asserting transformation, succession, or authority transfer.", "sources": ["*"], "targets": ["source"], "qualifiers": ["origin_role"], "forbids": ["derivation", "successor", "authority-transfer"]},
    {"id": "relation.derives-from", "group": "lineage", "question": "From which material or governed source was this artifact derived?", "effect": "Records derivation, compilation, or projection while preserving source and derived identities.", "sources": ["*"], "targets": ["*"], "qualifiers": ["derivation_role"], "forbids": ["identity-equality", "source-authority-transfer", "admission"]},
    {"id": "relation.evidence-bears-on", "group": "evidence", "question": "What evidential polarity does this evidence have toward this claim?", "effect": "Records supporting or contradicting evidence without accepting, rejecting, or deciding the claim.", "sources": ["evidence-set", "observation", "measurement-result"], "targets": ["finding", "identity-claim", "authority-claim", "hypothesis"], "qualifiers": ["polarity"], "forbids": ["claim-acceptance", "decision", "admission", "truth"]},
    {"id": "relation.governed-by", "group": "governance", "question": "Which Policy or Constitution governs this subject?", "effect": "Records applicable governance without proving compliance or authorization.", "sources": ["*"], "targets": ["policy", "constitution"], "qualifiers": ["governance_role"], "forbids": ["conformance", "authorization", "admission"]},
    {"id": "relation.declares-effect-on", "group": "governance", "question": "Which exact governance effect does this Decision declare?", "effect": "Records admission, adoption, or authorization as separate effect values and executes none of them.", "sources": ["decision"], "targets": ["*"], "qualifiers": ["effect_kind", "exact_target_version_ref"], "forbids": ["effect-execution", "cross-effect-inference", "runtime-success"]},
    {"id": "relation.instance-of", "group": "classification", "question": "Under which exact parent model is this subject classified?", "effect": "Records classification without implying conformance, ownership transfer, or realization.", "sources": ["implementation", "product-capability", "capability-instance"], "targets": ["product-capability", "product", "governed-model"], "qualifiers": ["parent_version_ref", "binding_ref"], "forbids": ["conformance", "realization", "ownership-transfer"]},
    {"id": "relation.binds-implementation", "group": "implementation", "question": "Which Ontology or Schema does this implementation bind?", "effect": "Records an implementation-model binding without proving conformance or runtime behavior.", "sources": ["implementation"], "targets": ["ontology", "schema"], "qualifiers": ["binding_role"], "forbids": ["conformance", "runtime-effectiveness", "admission"]},
    {"id": "relation.conforms-to", "group": "conformance", "question": "Which exact contract does this subject demonstrably conform to, and under which evidence?", "effect": "Records scoped conformance only; it does not imply admission, implementation conformance outside scope, or runtime conformance.", "sources": ["context", "capability-instance"], "targets": ["context-profile", "governed-model", "contract"], "qualifiers": ["conformance_scope", "exact_version_ref", "conformance_evidence_refs"], "forbids": ["admission", "runtime-conformance", "effectiveness", "authority"]},
    {"id": "relation.inherits-contract", "group": "contract", "question": "Which exact contract obligations are inherited by this instance?", "effect": "Records inherited obligations without transferring parent ownership or proving conformance.", "sources": ["capability-instance"], "targets": ["contract"], "qualifiers": ["binding_ref", "contract_version_ref"], "forbids": ["ownership-transfer", "conformance", "adoption"]},
    {"id": "relation.frames", "group": "context", "question": "Which subject does this Context frame for relevance and interpretation?", "effect": "Records Context framing, including Bounded Context reference, without making the framed subject authoritative or current.", "sources": ["context"], "targets": ["*"], "qualifiers": ["framing_role"], "forbids": ["source-authority", "currentness", "truth"]},
    {"id": "relation.requests-resolution-of", "group": "context", "question": "Which exact Context version does this Context Request ask to resolve?", "effect": "Records a resolution request without performing resolution or mutating Context.", "sources": ["context-request"], "targets": ["context"], "qualifiers": ["context_version_ref"], "forbids": ["resolution", "context-mutation", "source-authority"]},
    {"id": "relation.fulfills-request", "group": "context", "question": "Which request is this immutable output intended to fulfill?", "effect": "Records request fulfillment without implying that included sources or Context remain current.", "sources": ["context-view"], "targets": ["context-request"], "qualifiers": ["fulfillment_role"], "forbids": ["currentness", "source-authority", "context-mutation"]},
    {"id": "relation.successor-of", "group": "lifecycle", "question": "Which predecessor does this successor continue or replace?", "effect": "Records succession; replacement occurs only when succession_effect is supersedes.", "sources": ["*"], "targets": ["*"], "qualifiers": ["succession_effect"], "forbids": ["automatic-supersession", "identity-equality", "authority-transfer"]},
    {"id": "relation.assigned-to", "group": "people-and-teams", "question": "Which Role or Responsibility is explicitly assigned to this assignee?", "effect": "Records an assignment through its lifecycle-bearing record without implying Team membership or authority.", "sources": ["person-reference", "team"], "targets": ["role", "responsibility"], "qualifiers": ["assignment_kind", "relation_record_ref"], "forbids": ["team-membership", "authority", "permission", "identity"]},
    {"id": "relation.asserts-identity-of", "group": "identity", "question": "What bounded identity correspondence is being asserted between these endpoints?", "effect": "Records representation, identity linking, or identifier claims without merging identities or authority.", "sources": ["person-reference", "identity-claim"], "targets": ["person", "person-reference"], "qualifiers": ["assertion_kind", "claim_scope"], "forbids": ["identity-merge", "authority-transfer", "private-attribute-inference"]},
    {"id": "relation.scopes-authority-over", "group": "authority", "question": "What object or assignment is bounded by this explicit Authority Claim?", "effect": "Records claimed or bounding authority without granting permission or authenticating the claim.", "sources": ["authority-claim"], "targets": ["*", "role-assignment"], "qualifiers": ["authority_role", "scope_ref"], "forbids": ["permission-grant", "claim-authentication", "effect-execution"]},
    {"id": "relation.carries-definition", "group": "semantic-governance", "question": "Which exact Definition version supplies this Artifact Type's governed meaning?", "effect": "Records the semantic contract without admitting either endpoint or transferring Definition authority.", "sources": ["artifact-type"], "targets": ["definition"], "qualifiers": ["definition_version_ref", "definition_sha256"], "forbids": ["admission", "authority-transfer", "endpoint-identity-collapse"]},
]


AXIS_IDS = {
    "relation.member-of": "axis.membership",
    "relation.contributes-to": "axis.contribution",
    "relation.uses-method": "axis.method-dependency",
    "relation.evaluates": "axis.evaluation",
    "relation.realizes": "axis.realization",
    "relation.engages-inquiry": "axis.inquiry-engagement",
    "relation.originates-from": "axis.origin-lineage",
    "relation.derives-from": "axis.derivation",
    "relation.evidence-bears-on": "axis.evidence-polarity",
    "relation.governed-by": "axis.governance-applicability",
    "relation.declares-effect-on": "axis.decision-effect",
    "relation.instance-of": "axis.classification",
    "relation.binds-implementation": "axis.implementation-binding",
    "relation.conforms-to": "axis.conformance",
    "relation.inherits-contract": "axis.contract-inheritance",
    "relation.frames": "axis.context-framing",
    "relation.requests-resolution-of": "axis.context-resolution-request",
    "relation.fulfills-request": "axis.request-fulfillment",
    "relation.successor-of": "axis.lifecycle-succession",
    "relation.assigned-to": "axis.assignment",
    "relation.asserts-identity-of": "axis.identity-assertion",
    "relation.scopes-authority-over": "axis.authority-scope",
    "relation.carries-definition": "axis.semantic-contract",
}


def pairs(*values: tuple[str, str]) -> list[dict[str, str]]:
    return [{"source_kind": source, "target_kind": target} for source, target in values]


# This is the closed coupling surface. A source/target connection is valid only
# when its exact ordered pair appears here. Adding an endpoint kind to the
# inventory does not connect it; a new pair must be reviewed and declared.
CLOSED_PAIR_CONTRACTS = {
    "relation.member-of": pairs(
        ("product-capability", "product"), ("product-thesis", "product"), ("context", "product"),
        ("research-inquiry", "project"), ("research-run", "project"), ("experiment-design", "project"),
        ("experiment-run", "project"), ("goal", "project"), ("work", "project"),
        ("evidence-set", "project"), ("capability-realization-binding", "project"), ("context", "project"),
        ("ontology-node", "ontology"), ("typed-relation", "ontology"), ("product", "product"),
        ("responsibility", "role"), ("person-reference", "team"),
    ),
    "relation.contributes-to": pairs(
        ("project", "product"), ("project", "goal"), ("research-inquiry", "goal"),
        ("research-run", "goal"), ("experiment-design", "goal"), ("experiment-run", "goal"),
    ),
    "relation.uses-method": pairs(
        ("research-run", "method"), ("experiment-run", "method"), ("measurement-result", "method"),
        ("observation", "method"), ("project", "method"), ("product", "method"),
    ),
    "relation.evaluates": pairs(
        ("evaluation", "product-thesis"), ("evaluation", "product-capability"),
        ("evaluation", "capability-realization-binding"), ("experiment-design", "product"),
        ("experiment-design", "product-capability"), ("experiment-design", "capability-realization-binding"),
        ("experiment-design", "product-thesis"), ("experiment-run", "product"),
        ("experiment-run", "product-capability"), ("experiment-run", "capability-realization-binding"),
        ("experiment-run", "product-thesis"),
    ),
    "relation.realizes": pairs(("implementation", "product-capability"), ("experiment-run", "experiment-design")),
    "relation.engages-inquiry": pairs(
        ("research-run", "research-inquiry"), ("experiment-design", "research-inquiry"),
        ("experiment-run", "research-inquiry"), ("finding", "research-inquiry"),
    ),
    "relation.originates-from": pairs(
        ("definition", "source"), ("artifact-type", "source"), ("relation-kind", "source"), ("finding", "source"),
    ),
    "relation.derives-from": pairs(
        ("observation", "experiment-run"), ("observation", "research-run"),
        ("measurement-result", "experiment-run"), ("measurement-result", "research-run"),
        ("evidence-set", "experiment-run"), ("evidence-set", "research-run"),
        ("finding", "research-run"), ("finding", "evidence-set"), ("context-view", "context"),
        ("product-capability", "product-thesis"), ("generated-output", "source"),
    ),
    "relation.evidence-bears-on": pairs(*tuple(
        (source, target)
        for source in ("evidence-set", "observation", "measurement-result")
        for target in ("finding", "identity-claim", "authority-claim", "hypothesis")
    )),
    "relation.governed-by": pairs(
        ("context", "policy"), ("ontology", "policy"), ("artifact-type", "constitution"),
        ("definition", "constitution"), ("relation-kind", "constitution"),
    ),
    "relation.declares-effect-on": pairs(
        ("decision", "definition"), ("decision", "artifact-type"), ("decision", "relation-kind"),
        ("decision", "product-capability"), ("decision", "capability-realization-binding"),
        ("decision", "governed-model"), ("decision", "effect"),
    ),
    "relation.instance-of": pairs(
        ("implementation", "product-capability"), ("implementation", "governed-model"),
        ("product-capability", "product"), ("capability-instance", "product-capability"),
        ("capability-instance", "governed-model"),
    ),
    "relation.binds-implementation": pairs(("implementation", "ontology"), ("implementation", "schema")),
    "relation.conforms-to": pairs(
        ("context", "context-profile"), ("capability-instance", "governed-model"),
        ("capability-instance", "contract"),
    ),
    "relation.inherits-contract": pairs(("capability-instance", "contract")),
    "relation.frames": pairs(
        ("context", "bounded-context"), ("context", "product"), ("context", "project"),
        ("context", "goal"), ("context", "review"),
    ),
    "relation.requests-resolution-of": pairs(("context-request", "context")),
    "relation.fulfills-request": pairs(("context-view", "context-request")),
    "relation.successor-of": pairs(*tuple(
        (kind, kind) for kind in (
            "definition", "artifact-type", "relation-kind", "bounded-context", "context", "context-profile",
            "context-request", "context-view", "product", "product-thesis", "product-capability",
            "capability-realization-binding", "project", "research-inquiry", "research-run", "experiment-design",
            "experiment-run", "observation", "measurement-result", "finding", "ontology", "person-reference",
            "identity-claim", "team", "role", "role-assignment", "capability-instance", "governed-model",
            "contract", "schema", "policy", "constitution", "method", "goal",
        )
    )),
    "relation.assigned-to": pairs(
        ("person-reference", "role"), ("person-reference", "responsibility"),
        ("team", "role"), ("team", "responsibility"),
    ),
    "relation.asserts-identity-of": pairs(
        ("person-reference", "person"), ("person-reference", "person-reference"),
        ("identity-claim", "person-reference"),
    ),
    "relation.scopes-authority-over": pairs(
        ("authority-claim", "role-assignment"), ("authority-claim", "decision-scope"),
    ),
    "relation.carries-definition": pairs(("artifact-type", "definition")),
}


MAP = {
    "relation.belongs-to-product": ("relation.member-of", {"membership_role": "product-anchor"}),
    "relation.belongs-to-project": ("relation.member-of", {"membership_role": "project-scope"}),
    "relation.contains": ("relation.member-of", {"membership_role": "composition", "direction_normalized": "member-to-container"}),
    "relation.member-of": ("relation.member-of", {"membership_role": "team-membership"}),
    "relation.defines-responsibility": ("relation.member-of", {"membership_role": "role-contract", "direction_normalized": "responsibility-to-role"}),
    "relation.advances-goal": ("relation.contributes-to", {"contribution_role": "advance-goal"}),
    "relation.contributes-to-product": ("relation.contributes-to", {"contribution_role": "advance-product"}),
    "relation.uses-method": ("relation.uses-method", {}),
    "relation.evaluates": ("relation.evaluates", {"evaluation_role": "assess-subject"}),
    "relation.tests-thesis-proposition": ("relation.evaluates", {"evaluation_role": "test-thesis-proposition"}),
    "relation.realizes": ("relation.realizes", {"realization_role": "capability-realization"}),
    "relation.executes-design": ("relation.realizes", {"realization_role": "design-execution"}),
    "relation.addresses-inquiry": ("relation.engages-inquiry", {"inquiry_role": "addresses"}),
    "relation.answers-inquiry": ("relation.engages-inquiry", {"inquiry_role": "answers"}),
    "relation.originates-from": ("relation.originates-from", {}),
    "relation.derives-from": ("relation.derives-from", {"derivation_role": "derived-artifact"}),
    "relation.compiles-to": ("relation.derives-from", {"derivation_role": "compiled-output", "direction_normalized": "output-to-source"}),
    "relation.projects-context": ("relation.derives-from", {"derivation_role": "context-projection"}),
    "relation.supports": ("relation.evidence-bears-on", {"polarity": "supports"}),
    "relation.contradicts": ("relation.evidence-bears-on", {"polarity": "contradicts"}),
    "relation.governed-by": ("relation.governed-by", {}),
    "relation.authorizes": ("relation.declares-effect-on", {"effect_kind": "authorizes"}),
    "relation.adopts": ("relation.declares-effect-on", {"effect_kind": "adopts"}),
    "relation.admits": ("relation.declares-effect-on", {"effect_kind": "admits"}),
    "relation.instance-of": ("relation.instance-of", {}),
    "relation.binds-implementation": ("relation.binds-implementation", {}),
    "relation.conforms-to": ("relation.conforms-to", {}),
    "relation.inherits-contract": ("relation.inherits-contract", {}),
    "relation.frames": ("relation.frames", {"framing_role": "subject-framing"}),
    "relation.references-bounded-context": ("relation.frames", {"framing_role": "bounded-context-reference"}),
    "relation.requests-resolution-of": ("relation.requests-resolution-of", {}),
    "relation.fulfills-request": ("relation.fulfills-request", {}),
    "relation.successor-of": ("relation.successor-of", {"succession_effect": "continues"}),
    "relation.supersedes": ("relation.successor-of", {"succession_effect": "supersedes"}),
    "relation.assigned-role": ("relation.assigned-to", {"assignment_kind": "role"}),
    "relation.assigned-responsibility": ("relation.assigned-to", {"assignment_kind": "responsibility"}),
    "relation.represents-person": ("relation.asserts-identity-of", {"assertion_kind": "represents-person"}),
    "relation.identity-link": ("relation.asserts-identity-of", {"assertion_kind": "identity-link"}),
    "relation.claims-identifier-for": ("relation.asserts-identity-of", {"assertion_kind": "claims-identifier"}),
    "relation.claims-authority-over": ("relation.scopes-authority-over", {"authority_role": "claims-over"}),
    "relation.bounded-by-authority-claim": ("relation.scopes-authority-over", {"authority_role": "bounds-assignment", "direction_normalized": "authority-claim-to-assignment"}),
    "relation.carries-definition": ("relation.carries-definition", {}),
}


EXAMPLES = {
    "relation.member-of": ("experiment-run:definition-normalization-residue:2026-10-05", "project:lab-semantic-governance", {"membership_role": "project-scope"}),
    "relation.contributes-to": ("project:lab-semantic-governance", "CA2-PRODUCT-CRAFT", {"contribution_role": "advance-product", "contribution_scope": "Governed semantic foundations"}),
    "relation.uses-method": ("measurement-result:definition-normalization-residue-entropy:2026-10-05", "measurement-method:definition-normalization-residue-entropy", {"usage_role": "measurement"}),
    "relation.evaluates": ("experiment-design:definition-normalization-residue", "product-thesis:craft#outcome-authoritative-state", {"evaluation_role": "test-thesis-proposition", "evaluation_purpose": "Test one bounded outcome proposition"}),
    "relation.realizes": ("experiment-run:definition-normalization-residue:2026-10-05", "experiment-design:definition-normalization-residue", {"realization_role": "design-execution", "exact_target_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1"}),
    "relation.engages-inquiry": ("finding:normalization-residue-lowered", "research-inquiry:definition-normalization-residue", {"inquiry_role": "answers"}),
    "relation.originates-from": ("finding:research-inquiry-v1-contract-gap", "source:cyberalchemy-v2-definitions", {"origin_role": "content-source"}),
    "relation.derives-from": ("context-view:remaining-18-review:2026-10-05", "context:lab-artifact-type-admission", {"derivation_role": "context-projection"}),
    "relation.evidence-bears-on": ("evidence-set:definition-normalization-residue-run-2026-10-05", "finding:normalization-residue-lowered", {"polarity": "supports"}),
    "relation.governed-by": ("context:lab-artifact-type-admission", "policy:admitted-authority-first", {"governance_role": "source-selection"}),
    "relation.declares-effect-on": ("decision:artifact-type-batch-admission", "cal.artifact-type.experiment-run/v1", {"effect_kind": "admits", "exact_target_version_ref": "cal.artifact-type.experiment-run/v1@1.0.0-candidate.2"}),
    "relation.instance-of": ("capability-instance:lab-artifact-type-reviewer", "product-capability:governed-definition-admission", {"parent_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1", "binding_ref": "model-instance-binding:artifact-type-reviewer"}),
    "relation.binds-implementation": ("implementation:definition-validator", "ontology:artifact-governance", {"binding_role": "implements-ontology"}),
    "relation.conforms-to": ("context:lab-artifact-type-admission", "context-profile:governed-review", {"conformance_scope": "context-contract", "exact_version_ref": "context-profile:governed-review@1.0.0-candidate.2", "conformance_evidence_refs": ["receipt:remaining-18-model-validation"]}),
    "relation.inherits-contract": ("capability-instance:lab-artifact-type-reviewer", "contract:definition-admission-boundaries/v1", {"binding_ref": "model-instance-binding:artifact-type-reviewer", "contract_version_ref": "contract:definition-admission-boundaries/v1"}),
    "relation.frames": ("context:lab-artifact-type-admission", "bounded-context:semantic-governance", {"framing_role": "bounded-context-reference"}),
    "relation.requests-resolution-of": ("context-request:remaining-18-review", "context:lab-artifact-type-admission", {"context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2"}),
    "relation.fulfills-request": ("context-view:remaining-18-review:2026-10-05", "context-request:remaining-18-review", {"fulfillment_role": "immutable-view"}),
    "relation.successor-of": ("artifact-type:product-identity@2", "artifact-type:product-identity@1", {"succession_effect": "supersedes"}),
    "relation.assigned-to": ("person-reference:repository-reviewer", "role:artifact-type-reviewer", {"assignment_kind": "role", "relation_record_ref": "role-assignment:reviewer:artifact-type-reviewer"}),
    "relation.asserts-identity-of": ("identity-claim:repository-reviewer:workspace-handle", "person-reference:repository-reviewer", {"assertion_kind": "claims-identifier", "claim_scope": "CyberAlchemy Lab review attribution"}),
    "relation.scopes-authority-over": ("authority-claim:may-recommend-artifact-type-admission", "role-assignment:reviewer:artifact-type-reviewer", {"authority_role": "bounds-assignment", "scope_ref": "scope:artifact-type-admission-recommendation"}),
    "relation.carries-definition": ("cal.artifact-type.experiment-run/v1", "cal.definition.experiment@1.0.0-candidate.1", {"definition_version_ref": "cal.definition.experiment@1.0.0-candidate.1", "definition_sha256": "digest-bound-at-instance-time"}),
}


DEFINITION_IDS = [
    "cal.definition.classification-axis", "cal.definition.classification-orthogonality-invariant",
    "cal.definition.typed-coupling-invariant", "cal.definition.root-axis-independence-invariant",
    "cal.definition.governance-axis-independence-invariant", "cal.definition.identity-relation",
]


ENDPOINT_CARRIERS = {
    "artifact-type": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.artifact-type/v2", "path": "authority/artifact-types/artifact-type/v2/artifact.json", "admission_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"},
    "capability-instance": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.capability-instance/v1", "path": "authority/artifact-types/capability-instance/v1/artifact.json", "admission_ref": "CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"},
    "definition": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.definition/v1", "path": "authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json", "admission_ref": "CAL-DECISION-0015-DEFINITION-V1-ADMISSION", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"},
    "goal": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.goal/v1", "path": "authority/artifact-types/goal/v1/artifact.json", "admission_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"},
    "method": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.method-binding/v1", "path": "authority/artifact-types/method-binding/v1/artifact.json", "admission_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json", "note": "The admitted carrier is Method Binding; the relation endpoint uses the normalized semantic kind method."},
    "product": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.product-identity/v2", "path": "authority/artifact-types/product-identity/v2/artifact.json", "admission_ref": "CAL-DECISION-0057-PRODUCT-IDENTITY-V2-SUCCESSOR-ADMISSION", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/product-identity.json", "note": "Product Identity/v2 is the current Product identity carrier."},
    "product-capability": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.product-capability/v1", "path": "authority/artifact-types/product-capability/v1/artifact.json", "admission_ref": "CAL-DECISION-0059-PRODUCT-CAPABILITY-V1-ADMISSION", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/product-capability.json"},
    "project": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.project-identity/v1", "path": "authority/artifact-types/project-identity/v1/artifact.json", "admission_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json", "note": "Project Identity/v1 is the current Project identity carrier."},
    "research-inquiry": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.research-inquiry/v1", "path": "authority/artifact-types/research-inquiry/v1/artifact.json", "admission_ref": "CAL-DECISION-0062-RESEARCH-INQUIRY-V1-ADMISSION", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/research-inquiry.json"},
    "research-run": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.research-run/v1", "path": "authority/artifact-types/research-run/v1/artifact.json", "admission_ref": "CAL-DECISION-0063-RESEARCH-RUN-V1-ADMISSION", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/research-run.json"},
    "bounded-context": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.bounded-context/v2", "path": "authority/artifact-types/bounded-context/v2/artifact.json", "lifecycle_evidence_path": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"},
    "product-thesis": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.product-thesis/v1", "path": "authority/artifact-types/product-thesis/v1/artifact.json", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/product-thesis.json"},
    "capability-realization-binding": {"lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.capability-realization-binding/v1", "path": "authority/artifact-types/capability-realization-binding/v1/artifact.json", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/capability-realization-binding.json"},
    "context": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.context/v1", "path": "authority/artifact-types/context/v1/artifact.json"},
    "context-profile": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.context-profile/v1", "path": "authority/artifact-types/context-profile/v1/artifact.json"},
    "context-request": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.context-request/v1", "path": "authority/artifact-types/context-request/v1/artifact.json"},
    "context-view": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.context-view/v1", "path": "authority/artifact-types/context-view/v1/artifact.json"},
    "experiment-design": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.experiment-design/v1", "path": "authority/artifact-types/experiment-design/v1/artifact.json"},
    "experiment-run": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.experiment-run/v1", "path": "authority/artifact-types/experiment-run/v1/artifact.json"},
    "finding": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.finding/v1", "path": "authority/artifact-types/finding/v1/artifact.json"},
    "identity-claim": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.identity-claim/v1", "path": "authority/artifact-types/identity-claim/v1/artifact.json"},
    "measurement-result": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.measurement-result/v1", "path": "authority/artifact-types/measurement-result/v1/artifact.json"},
    "observation": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.observation/v1", "path": "authority/artifact-types/observation/v1/artifact.json"},
    "ontology": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.ontology/v1", "path": "authority/artifact-types/ontology/v1/artifact.json"},
    "person-reference": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.person-reference/v1", "path": "authority/artifact-types/person-reference/v1/artifact.json"},
    "role": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.role/v1", "path": "authority/artifact-types/role/v1/artifact.json"},
    "role-assignment": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.role-assignment/v1", "path": "authority/artifact-types/role-assignment/v1/artifact.json"},
    "team": {"lifecycle_state": "candidate-materialized", "carrier_ref": "cal.artifact-type.team/v1", "path": "authority/artifact-types/team/v1/artifact.json"},
    "authority-claim": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "constitution": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "contract": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "decision": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "Decision documents exist, but no canonical root Decision Artifact Type package exists."},
    "evaluation": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "evidence-set": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "governed-model": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "hypothesis": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "Product Thesis can carry hypothesis propositions, but Hypothesis is not a standalone Artifact Type."},
    "implementation": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "person": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "policy": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "responsibility": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "schema": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "Schemas exist as governed files, but no canonical root Schema Artifact Type package exists."},
    "source": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "Source records exist in governance surfaces, but no canonical root Source Artifact Type package exists."},
    "decision-scope": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "effect": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "generated-output": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "ontology-node": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "relation-kind": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "The Relation Kind catalog is candidate-only and no Relation Kind Artifact Type carrier exists."},
    "review": {"lifecycle_state": "referenced-no-canonical-carrier"},
    "typed-relation": {"lifecycle_state": "referenced-no-canonical-carrier", "note": "Typed relation instances are modeled by this candidate, but no standalone Typed Relation Artifact Type exists."},
    "work": {"lifecycle_state": "referenced-no-canonical-carrier"},
}


UNCONNECTED_ADMITTED_CARRIERS = [
    {"endpoint_kind": "intent", "lifecycle_state": "admitted-current", "carrier_ref": "cal.artifact-type.intent/v1", "path": "authority/artifact-types/intent/v1/artifact.json", "lifecycle_evidence_path": "authority/artifact-types/admissions/migration-26/v1/intent.json", "used_by": []},
]


HOSTILES = [
    {"id": "membership-is-not-contribution", "asserted": "relation.member-of", "forbidden": ["relation.contributes-to"]},
    {"id": "contribution-is-not-realization", "asserted": "relation.contributes-to", "forbidden": ["relation.realizes", "relation.evaluates"]},
    {"id": "method-use-is-not-conformance", "asserted": "relation.uses-method", "forbidden": ["relation.conforms-to", "relation.realizes"]},
    {"id": "evaluation-is-not-evidence-verdict", "asserted": "relation.evaluates", "forbidden": ["relation.evidence-bears-on", "relation.declares-effect-on"]},
    {"id": "realization-is-not-conformance", "asserted": "relation.realizes", "forbidden": ["relation.conforms-to", "relation.declares-effect-on"]},
    {"id": "conformance-is-not-admission", "asserted": "relation.conforms-to", "forbidden": ["relation.declares-effect-on"]},
    {"id": "assignment-is-not-authority", "asserted": "relation.assigned-to", "forbidden": ["relation.scopes-authority-over"]},
    {"id": "identity-assertion-is-not-identity-merge", "asserted": "relation.asserts-identity-of", "forbidden": ["endpoint-equality", "authority-transfer"]},
    {"id": "succession-is-not-automatic-supersession", "asserted": "relation.successor-of", "qualifier": {"succession_effect": "continues"}, "forbidden": ["supersedes"]},
    {"id": "decision-effects-do-not-cross-infer", "asserted": "relation.declares-effect-on", "qualifier": {"effect_kind": "admits"}, "forbidden": ["adopts", "authorizes", "effect-executed"]},
]


def build() -> dict[str, Any]:
    prior = load(PREDECESSOR / "model.json")
    registry = load(DEFINITION_REGISTRY)
    extension_definition = load(EXTENSION_DEFINITION)
    extension_validation = load(EXTENSION_DEFINITION_VALIDATION)
    admitted = {item["definition_id"]: item for item in registry["entries"] if item["lifecycle_state"] == "admitted"}
    definition_bindings = [{"definition_ref": f"{definition_id}@{admitted[definition_id]['version']}", "path": admitted[definition_id]["path"], "sha256": admitted[definition_id]["sha256"]} for definition_id in DEFINITION_IDS]
    absorbed = {axis["id"]: [] for axis in AXES}
    normalizations = []
    for old in sorted(MAP):
        new, qualifiers = MAP[old]
        absorbed[new].append(old)
        normalizations.append({"previous_relation_kind": old, "axis_relation_kind": new, "fixed_qualifiers": qualifiers})
    entries = []
    for axis in AXES:
        endpoint_pairs = CLOSED_PAIR_CONTRACTS[axis["id"]]
        entries.append({
            "relation_kind_id": axis["id"], "axis_id": AXIS_IDS[axis["id"]], "group": axis["group"], "unique_question": axis["question"],
            "operational_effect": axis["effect"],
            "source_kinds": sorted({pair["source_kind"] for pair in endpoint_pairs}),
            "target_kinds": sorted({pair["target_kind"] for pair in endpoint_pairs}),
            "allowed_endpoint_pairs": endpoint_pairs,
            "required_qualifier_axes": axis["qualifiers"], "forbidden_inferences": axis["forbids"],
            "absorbed_relation_kinds": absorbed[axis["id"]], "authority_effect": "none", "status": "candidate-axis-orthogonal",
        })
    examples = {axis: {"relation_id": f"example:{axis}", "relation_kind_ref": axis, "source_ref": source, "target_ref": target, "qualifiers": qualifiers, "owner_ref": "role:relation-owner", "evidence_refs": [f"evidence:{axis.removeprefix('relation.')}"], "lifecycle_state": "candidate", "authority_effect": "none"} for axis, (source, target, qualifiers) in EXAMPLES.items()}
    model = {
        "schema_version": "cyberalchemy-lab-axis-orthogonal-relation-model/v1", "model_id": "CAL-AXIS-ORTHOGONAL-RELATION-MODEL-0002",
        "status": "candidate-complete-awaiting-owner-review", "authority_effect": "none",
        "predecessor": {"path": rel(PREDECESSOR / "model.json"), "sha256": sha(PREDECESSOR / "model.json"), "relation_kinds": prior["counts"]["relation_kinds"]},
        "definition_bindings": definition_bindings,
        "candidate_definition_bindings": [{
            "definition_ref": f"{extension_definition['definition_id']}@{extension_definition['version']}",
            "path": rel(EXTENSION_DEFINITION),
            "sha256": sha(EXTENSION_DEFINITION),
            "validation_path": rel(EXTENSION_DEFINITION_VALIDATION),
            "validation_sha256": sha(EXTENSION_DEFINITION_VALIDATION),
            "validation_result": extension_validation["result"],
            "admission_posture": "candidate-unadmitted",
            "required_before_relation_kind_admission": True,
        }],
        "axis_contract": {
            "vector": ["relation_identity", "semantic_axis", "source_endpoint", "target_endpoint", "direction", "qualifier_axes", "owner", "evidence", "lifecycle", "authority_effect"],
            "rule": "A change on one axis does not imply a change on another axis unless an explicit typed coupling, schema rule, gate, validator, or owner decision declares that bridge.",
            "endpoint_closure_rule": "Only exact ordered source_kind -> target_kind pairs declared by a Relation Kind are permitted. Wildcards and inference from separate source/target lists are forbidden. Every new connection requires an explicit candidate pair, owner review, evidence, and validation before admission.",
            "endpoint_extension_definition_ref": f"{extension_definition['definition_id']}@{extension_definition['version']}",
        },
        "counts": {"predecessor_relation_kinds": 42, "axis_relation_kinds": len(entries), "collapsed_duplicate_kinds": 42 - len(entries), "normalized_previous_relation_names": len(normalizations), "declared_endpoint_pairs": sum(len(item["allowed_endpoint_pairs"]) for item in entries), "hostile_no_collapse_cases": len(HOSTILES)},
        "entries": entries, "normalizations": normalizations, "hostile_no_collapse_cases": HOSTILES,
        "claim_ceiling": "This candidate compresses the previous 42 relation names into independently valued typed coupling axes, preserves their semantic distinctions as qualifier values, and closes use to explicitly declared ordered endpoint pairs. It does not admit Relation Kinds, permit undeclared endpoint connections, merge endpoints, grant authority, accept evidence, execute decisions, or establish runtime conformance.",
    }
    endpoint_inventory = build_endpoint_inventory(model)
    dump(ROOT / "model.json", model)
    dump(ROOT / "examples.json", examples)
    dump(ROOT / "endpoint-inventory.json", endpoint_inventory)
    (ROOT / "RELATIONS.md").write_text(render(model, examples), encoding="utf-8")
    (ROOT / "ENDPOINTS.md").write_text(render_endpoints(model, endpoint_inventory), encoding="utf-8")
    paths = [ROOT / "build.py", ROOT / "validate.py", ROOT / "model.json", ROOT / "examples.json", ROOT / "endpoint-inventory.json", ROOT / "RELATIONS.md", ROOT / "ENDPOINTS.md"]
    endpoint_input_paths = sorted({item["path"] for item in endpoint_inventory["entries"] if item.get("path")} | {item["lifecycle_evidence_path"] for item in endpoint_inventory["entries"] if item.get("lifecycle_evidence_path")} | {item["path"] for item in UNCONNECTED_ADMITTED_CARRIERS} | {item["lifecycle_evidence_path"] for item in UNCONNECTED_ADMITTED_CARRIERS})
    endpoint_inputs = [{"path": path, "sha256": sha(LAB / path)} for path in endpoint_input_paths]
    candidate_definition_inputs = [{"path": rel(EXTENSION_DEFINITION), "sha256": sha(EXTENSION_DEFINITION)}, {"path": rel(EXTENSION_DEFINITION_VALIDATION), "sha256": sha(EXTENSION_DEFINITION_VALIDATION)}]
    dump(ROOT / "manifest.json", {"schema_version": "cyberalchemy-lab-exact-file-manifest/v1", "subject": model["model_id"], "files": [{"path": rel(path), "sha256": sha(path)} for path in paths], "inputs": [{"path": rel(PREDECESSOR / "model.json"), "sha256": sha(PREDECESSOR / "model.json")}, {"path": rel(DEFINITION_REGISTRY), "sha256": sha(DEFINITION_REGISTRY)}] + definition_bindings + candidate_definition_inputs + endpoint_inputs, "excluded_from_self_hash": [rel(ROOT / "manifest.json"), rel(ROOT / "receipts/validation.json"), rel(ROOT / "receipts/no-collapse.json")]})
    return model


def build_endpoint_inventory(model: dict[str, Any]) -> dict[str, Any]:
    source_for = {kind: [] for kind in ENDPOINT_CARRIERS}
    target_for = {kind: [] for kind in ENDPOINT_CARRIERS}
    for relation in model["entries"]:
        for kind in relation["source_kinds"]:
            if kind != "*":
                source_for[kind].append(relation["relation_kind_id"])
        for kind in relation["target_kinds"]:
            if kind != "*":
                target_for[kind].append(relation["relation_kind_id"])
    entries = []
    for kind in sorted(ENDPOINT_CARRIERS):
        carrier = ENDPOINT_CARRIERS[kind]
        entries.append({"endpoint_kind": kind, **carrier, "source_for": sorted(source_for[kind]), "target_for": sorted(target_for[kind])})
    counts = {state: sum(item["lifecycle_state"] == state for item in entries) for state in ["admitted-current", "candidate-materialized", "referenced-no-canonical-carrier"]}
    return {
        "schema_version": "cyberalchemy-lab-relation-endpoint-inventory/v1",
        "subject": model["model_id"],
        "status": "candidate-inventory",
        "authority_effect": "none",
        "counts": {"named_endpoint_kinds": len(entries), "declared_endpoint_pairs": sum(len(item["allowed_endpoint_pairs"]) for item in model["entries"]), "wildcard_tokens": 0, **counts},
        "closed_world": True,
        "extension_definition_ref": model["axis_contract"]["endpoint_extension_definition_ref"],
        "extension_definition_admission_posture": "candidate-unadmitted",
        "extension_rule": "A new connection requires an explicit ordered source_kind -> target_kind pair in the owning Relation Kind plus owner review, evidence, and validation. Registering a new endpoint kind alone creates no connection.",
        "entries": entries,
        "admitted_carriers_without_declared_connections": UNCONNECTED_ADMITTED_CARRIERS,
        "claim_ceiling": "This inventory reports carrier availability and the closed endpoint universe named by the candidate relation model. It does not admit missing carriers, admit Relation Kinds, validate instances, or authorize undeclared connections.",
    }


def endpoint_label(kind: str, inventory_by_kind: dict[str, dict[str, Any]]) -> str:
    states = {"admitted-current": "A", "candidate-materialized": "C", "referenced-no-canonical-carrier": "R"}
    return f"`{kind}` [{states[inventory_by_kind[kind]['lifecycle_state']]}]"


def render_endpoints(model: dict[str, Any], inventory: dict[str, Any]) -> str:
    by_kind = {item["endpoint_kind"]: item for item in inventory["entries"]}
    lines = [
        "<!-- GENERATED FILE: canonical data is model.json and endpoint-inventory.json. -->", "", "# Relation endpoint inventory", "",
        "This surface separates relation grammar from Artifact Type lifecycle. `A` means an admitted-current carrier exists, `C` means a materialized candidate carrier exists, and `R` means the relation model references the concept but no canonical root Artifact Type carrier exists.", "",
        f"**Closed endpoint model:** {inventory['counts']['named_endpoint_kinds']} named endpoint kinds and {inventory['counts']['declared_endpoint_pairs']} exact ordered pairs = {inventory['counts']['admitted-current']} admitted-current + {inventory['counts']['candidate-materialized']} candidate-materialized + {inventory['counts']['referenced-no-canonical-carrier']} referenced without a canonical carrier. Wildcards: 0.", "",
        "## Complete declared connection matrix", "", "| # | Semantic axis | Directed relation | Declared ordered endpoint pairs |", "| ---: | --- | --- | --- |"
    ]
    for index, relation in enumerate(model["entries"], 1):
        declared_pairs = "<br>".join(f"{endpoint_label(pair['source_kind'], by_kind)} → {endpoint_label(pair['target_kind'], by_kind)}" for pair in relation["allowed_endpoint_pairs"])
        lines.append(f"| {index} | `{relation['axis_id']}` | `{relation['relation_kind_id']}` | {declared_pairs} |")
    lines += ["", "## Named endpoint carriers", "", "| Endpoint kind | State | Canonical carrier | Source in relations | Target in relations | Note |", "| --- | --- | --- | --- | --- | --- |"]
    for item in inventory["entries"]:
        carrier = f"`{item['carrier_ref']}`<br>`{item['path']}`" if item.get("carrier_ref") else "None yet"
        sources = ", ".join(f"`{value}`" for value in item["source_for"]) or "—"
        targets = ", ".join(f"`{value}`" for value in item["target_for"]) or "—"
        lines.append(f"| `{item['endpoint_kind']}` | `{item['lifecycle_state']}` | {carrier} | {sources} | {targets} | {item.get('note', '')} |")
    lines += ["", "## Admitted carriers without a declared connection", "", "| Endpoint kind | Carrier | Connection status |", "| --- | --- | --- |"]
    for item in inventory["admitted_carriers_without_declared_connections"]:
        lines.append(f"| `{item['endpoint_kind']}` | `{item['carrier_ref']}` | No connection. Adding one requires an explicit pair declaration. |")
    lines += ["", "## Extension rule", "", f"Definition dependency: `{inventory['extension_definition_ref']}` (`{inventory['extension_definition_admission_posture']}`).", "", inventory["extension_rule"], "", "## Claim ceiling", "", inventory["claim_ceiling"], ""]
    return "\n".join(lines)


def render(model: dict[str, Any], examples: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is model.json and examples.json. -->", "", "# Axis-orthogonal Relation Kind model", "", "The initial 42-kind candidate failed semantic compression review. This successor normalizes all 42 prior relation names into 23 independently valued relation axes plus explicit qualifier axes.", "", f"**Resulting model:** {model['counts']['axis_relation_kinds']} relation axes; {model['counts']['collapsed_duplicate_kinds']} duplicate kinds collapsed; {model['counts']['normalized_previous_relation_names']} prior names normalized; {model['counts']['declared_endpoint_pairs']} exact endpoint pairs; zero wildcards.", "", "## Axis rule", "", model["axis_contract"]["rule"], "", "## Endpoint closure rule", "", model["axis_contract"]["endpoint_closure_rule"], "", f"Definition dependency: `{model['axis_contract']['endpoint_extension_definition_ref']}` (`candidate-unadmitted`; required before Relation Kind admission).", "", "The noun names the independent semantic axis, while the Relation Kind is a directed predicate. For example, `axis.membership` is represented by `relation.member-of`.", "", "## All relation axes", "", "| # | Semantic axis | Directed Relation Kind | Unique question | Required qualifier axes | Absorbed previous kinds | Forbidden inference examples |", "| ---: | --- | --- | --- | --- | --- | --- |"]
    for i, item in enumerate(model["entries"], 1):
        lines.append(f"| {i} | `{item['axis_id']}` | `{item['relation_kind_id']}` | {item['unique_question']} | {', '.join(f'`{x}`' for x in item['required_qualifier_axes'])} | {', '.join(f'`{x}`' for x in item['absorbed_relation_kinds'])} | {', '.join(f'`{x}`' for x in item['forbidden_inferences'])} |")
    lines += ["", "## Exact 42-to-23 normalization", "", "| Previous relation kind | Axis relation kind | Fixed qualifier values |", "| --- | --- | --- |"]
    for item in model["normalizations"]:
        lines.append(f"| `{item['previous_relation_kind']}` | `{item['axis_relation_kind']}` | `{json.dumps(item['fixed_qualifiers'], sort_keys=True)}` |")
    lines += ["", "## Realistic examples", ""]
    for i, item in enumerate(model["entries"], 1):
        ex = examples[item["relation_kind_id"]]
        lines += [f"### {i}. `{item['relation_kind_id']}`", "", item["operational_effect"], "", "```json", json.dumps(ex, indent=2, sort_keys=True), "```", ""]
    lines += ["## Claim ceiling", "", model["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> int:
    build()
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
