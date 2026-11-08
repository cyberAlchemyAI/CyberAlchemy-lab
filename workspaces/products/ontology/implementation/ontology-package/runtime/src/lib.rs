use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::error::Error;
use std::fmt::{self, Display};
use std::fs;
use std::path::Path;

pub const SOURCE_SCHEMA: &str = "cyberalchemy-lab-ontology-source/v1";
pub const PACKAGE_SCHEMA: &str = "cyberalchemy-lab-ontology-package/v1";
pub const PRODUCT_REF: &str = "CA2-PRODUCT-ONTOLOGY/v1";
pub const PRODUCT_OUTPUT_REF: &str = "CA2-OUTPUT-ONTOLOGY-PACKAGE";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProductError {
    pub code: &'static str,
    pub message: String,
}

impl ProductError {
    fn new(code: &'static str, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
        }
    }
}

impl Display for ProductError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.message)
    }
}

impl Error for ProductError {}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceReference {
    pub source_id: String,
    pub selector: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ForbiddenCollapse {
    pub left_ref: String,
    pub right_ref: String,
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyNode {
    pub node_id: String,
    pub type_ref: String,
    pub label: String,
    pub definition_or_claim: String,
    pub scope: String,
    pub source_refs: Vec<SourceReference>,
    pub use_obligations: Vec<String>,
    pub forbidden_collapse: Vec<ForbiddenCollapse>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyRelation {
    pub relation_id: String,
    pub type_ref: String,
    pub source_node_id: String,
    pub target_node_id: String,
    pub source_refs: Vec<SourceReference>,
    pub forbidden_collapse: Vec<ForbiddenCollapse>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TypedResidue {
    pub residue_id: String,
    pub statement: String,
    pub owner_route: String,
    pub treatment: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologySource {
    pub schema_version: String,
    pub source_id: String,
    pub package_id: String,
    pub package_version: String,
    pub domain: String,
    pub owner_route: String,
    pub product_ref: String,
    pub product_output_ref: String,
    pub authority_effect: String,
    pub nodes: Vec<OntologyNode>,
    pub relations: Vec<OntologyRelation>,
    pub residue: Vec<TypedResidue>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceBinding {
    pub source_id: String,
    pub owner_route: String,
    pub sha256: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct QueryContract {
    pub allowed_operations: Vec<String>,
    pub identity_field: String,
    pub unknown_identity_behavior: String,
    pub filesystem_reach: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceDirection {
    pub canonical: String,
    pub human_projection: String,
    pub projection_policy: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyPackage {
    pub schema_version: String,
    pub package_id: String,
    pub version: String,
    pub status: String,
    pub authority_effect: String,
    pub domain: String,
    pub product_ref: String,
    pub product_output_ref: String,
    pub source_binding: SourceBinding,
    pub nodes: Vec<OntologyNode>,
    pub relations: Vec<OntologyRelation>,
    pub residue: Vec<TypedResidue>,
    pub query_contract: QueryContract,
    pub source_direction: SourceDirection,
    pub claim_ceiling: String,
}

pub fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn canonical_json<T: Serialize>(value: &T) -> Result<Vec<u8>, ProductError> {
    let mut bytes = serde_json::to_vec_pretty(value)
        .map_err(|error| ProductError::new("SERIALIZE_FAILED", error.to_string()))?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn require_text(field: &str, value: &str) -> Result<(), ProductError> {
    if value.trim().is_empty() {
        return Err(ProductError::new(
            "REQUIRED_TEXT_MISSING",
            format!("{field} must not be empty"),
        ));
    }
    Ok(())
}

fn validate_graph(
    nodes: &[OntologyNode],
    relations: &[OntologyRelation],
) -> Result<(), ProductError> {
    if nodes.is_empty() {
        return Err(ProductError::new(
            "NODE_SET_EMPTY",
            "at least one ontology node is required",
        ));
    }
    let mut node_ids = BTreeSet::new();
    for node in nodes {
        require_text("node_id", &node.node_id)?;
        require_text("node.type_ref", &node.type_ref)?;
        require_text("node.label", &node.label)?;
        require_text("node.definition_or_claim", &node.definition_or_claim)?;
        require_text("node.scope", &node.scope)?;
        if node.source_refs.is_empty() {
            return Err(ProductError::new(
                "SOURCE_REFERENCE_MISSING",
                format!("node {} has no source reference", node.node_id),
            ));
        }
        if !node_ids.insert(node.node_id.clone()) {
            return Err(ProductError::new("NODE_ID_DUPLICATE", node.node_id.clone()));
        }
    }
    let mut relation_ids = BTreeSet::new();
    for relation in relations {
        require_text("relation_id", &relation.relation_id)?;
        require_text("relation.type_ref", &relation.type_ref)?;
        if !relation_ids.insert(relation.relation_id.clone()) {
            return Err(ProductError::new(
                "RELATION_ID_DUPLICATE",
                relation.relation_id.clone(),
            ));
        }
        if !node_ids.contains(&relation.source_node_id) {
            return Err(ProductError::new(
                "RELATION_SOURCE_MISSING",
                format!("{} -> {}", relation.relation_id, relation.source_node_id),
            ));
        }
        if !node_ids.contains(&relation.target_node_id) {
            return Err(ProductError::new(
                "RELATION_TARGET_MISSING",
                format!("{} -> {}", relation.relation_id, relation.target_node_id),
            ));
        }
        if relation.source_refs.is_empty() {
            return Err(ProductError::new(
                "SOURCE_REFERENCE_MISSING",
                format!("relation {} has no source reference", relation.relation_id),
            ));
        }
    }
    Ok(())
}

pub fn validate_source(source: &OntologySource) -> Result<(), ProductError> {
    if source.schema_version != SOURCE_SCHEMA {
        return Err(ProductError::new(
            "SOURCE_SCHEMA_UNSUPPORTED",
            &source.schema_version,
        ));
    }
    for (field, value) in [
        ("source_id", source.source_id.as_str()),
        ("package_id", source.package_id.as_str()),
        ("package_version", source.package_version.as_str()),
        ("domain", source.domain.as_str()),
        ("owner_route", source.owner_route.as_str()),
    ] {
        require_text(field, value)?;
    }
    if source.authority_effect != "none" {
        return Err(ProductError::new(
            "AUTHORITY_EFFECT_FORBIDDEN",
            &source.authority_effect,
        ));
    }
    if source.product_ref != PRODUCT_REF {
        return Err(ProductError::new(
            "PRODUCT_REF_MISMATCH",
            &source.product_ref,
        ));
    }
    if source.product_output_ref != PRODUCT_OUTPUT_REF {
        return Err(ProductError::new(
            "PRODUCT_OUTPUT_REF_MISMATCH",
            &source.product_output_ref,
        ));
    }
    if source.package_id == source.product_ref || source.package_id == source.product_output_ref {
        return Err(ProductError::new(
            "IDENTITY_COLLAPSE",
            "package identity must remain distinct from Product and Product output kind",
        ));
    }
    validate_graph(&source.nodes, &source.relations)
}

pub fn build_package(source_bytes: &[u8]) -> Result<OntologyPackage, ProductError> {
    let source: OntologySource = serde_json::from_slice(source_bytes)
        .map_err(|error| ProductError::new("SOURCE_JSON_INVALID", error.to_string()))?;
    validate_source(&source)?;
    let mut nodes = source.nodes;
    let mut relations = source.relations;
    let mut residue = source.residue;
    nodes.sort_by(|left, right| left.node_id.cmp(&right.node_id));
    relations.sort_by(|left, right| left.relation_id.cmp(&right.relation_id));
    residue.sort_by(|left, right| left.residue_id.cmp(&right.residue_id));
    let package = OntologyPackage {
        schema_version: PACKAGE_SCHEMA.to_owned(),
        package_id: source.package_id,
        version: source.package_version,
        status: "test-candidate".to_owned(),
        authority_effect: "none".to_owned(),
        domain: source.domain,
        product_ref: source.product_ref,
        product_output_ref: source.product_output_ref,
        source_binding: SourceBinding {
            source_id: source.source_id,
            owner_route: source.owner_route,
            sha256: sha256(source_bytes),
        },
        nodes,
        relations,
        residue,
        query_contract: QueryContract {
            allowed_operations: vec!["list".to_owned(), "get".to_owned()],
            identity_field: "node_id".to_owned(),
            unknown_identity_behavior: "fail-closed".to_owned(),
            filesystem_reach: "package-file-only".to_owned(),
        },
        source_direction: SourceDirection {
            canonical: "ontology-package.json".to_owned(),
            human_projection: "ONTOLOGY-PACKAGE.md".to_owned(),
            projection_policy: "generated-only".to_owned(),
        },
        claim_ceiling: "This governed ontology package is a private test-candidate output. Validation and retrieval do not admit source meaning, create authority, prove Product value, or authorize publication or deployment.".to_owned(),
    };
    validate_package(&package)?;
    Ok(package)
}

pub fn validate_package(package: &OntologyPackage) -> Result<(), ProductError> {
    if package.schema_version != PACKAGE_SCHEMA {
        return Err(ProductError::new(
            "PACKAGE_SCHEMA_UNSUPPORTED",
            &package.schema_version,
        ));
    }
    if package.status != "test-candidate" || package.authority_effect != "none" {
        return Err(ProductError::new(
            "PACKAGE_POSTURE_INVALID",
            format!("{} / {}", package.status, package.authority_effect),
        ));
    }
    if package.product_ref != PRODUCT_REF || package.product_output_ref != PRODUCT_OUTPUT_REF {
        return Err(ProductError::new(
            "PACKAGE_PRODUCT_BINDING_INVALID",
            format!("{} / {}", package.product_ref, package.product_output_ref),
        ));
    }
    if package.package_id == package.product_ref
        || package.package_id == package.product_output_ref
        || package.source_binding.sha256.len() != 64
        || !package
            .source_binding
            .sha256
            .chars()
            .all(|character| character.is_ascii_hexdigit() && !character.is_ascii_uppercase())
    {
        return Err(ProductError::new(
            "PACKAGE_IDENTITY_OR_SOURCE_BINDING_INVALID",
            &package.package_id,
        ));
    }
    if package.query_contract.allowed_operations != ["list", "get"]
        || package.query_contract.identity_field != "node_id"
        || package.query_contract.unknown_identity_behavior != "fail-closed"
        || package.query_contract.filesystem_reach != "package-file-only"
    {
        return Err(ProductError::new(
            "QUERY_CONTRACT_INVALID",
            "only package-local list/get retrieval is permitted",
        ));
    }
    if package.source_direction.projection_policy != "generated-only" {
        return Err(ProductError::new(
            "PROJECTION_POLICY_INVALID",
            &package.source_direction.projection_policy,
        ));
    }
    validate_graph(&package.nodes, &package.relations)
}

pub fn load_package(path: impl AsRef<Path>) -> Result<OntologyPackage, ProductError> {
    let bytes = fs::read(path.as_ref())
        .map_err(|error| ProductError::new("PACKAGE_READ_FAILED", error.to_string()))?;
    let package: OntologyPackage = serde_json::from_slice(&bytes)
        .map_err(|error| ProductError::new("PACKAGE_JSON_INVALID", error.to_string()))?;
    validate_package(&package)?;
    Ok(package)
}

pub fn list_nodes(package: &OntologyPackage) -> Vec<&OntologyNode> {
    package.nodes.iter().collect()
}

pub fn get_node<'a>(
    package: &'a OntologyPackage,
    node_id: &str,
) -> Result<&'a OntologyNode, ProductError> {
    package
        .nodes
        .iter()
        .find(|node| node.node_id == node_id)
        .ok_or_else(|| ProductError::new("NODE_NOT_FOUND", node_id))
}

fn escape_cell(value: &str) -> String {
    value.replace('|', "\\|").replace('\n', " ")
}

pub fn human_projection(package: &OntologyPackage) -> String {
    let mut lines = vec![
        "<!-- Generated by cal-ontology-product from ontology-package.json. Do not edit. -->"
            .to_owned(),
        String::new(),
        format!("# Ontology package `{}`", package.package_id),
        String::new(),
        format!("- Version: `{}`", package.version),
        format!("- Domain: `{}`", package.domain),
        format!("- Status: `{}`", package.status),
        format!("- Authority effect: `{}`", package.authority_effect),
        format!("- Product: `{}`", package.product_ref),
        format!("- Product output: `{}`", package.product_output_ref),
        format!("- Source: `{}`", package.source_binding.source_id),
        format!("- Source digest: `{}`", package.source_binding.sha256),
        String::new(),
        "## Nodes".to_owned(),
        String::new(),
        "| ID | Type | Label | Scope |".to_owned(),
        "| --- | --- | --- | --- |".to_owned(),
    ];
    for node in &package.nodes {
        lines.push(format!(
            "| `{}` | `{}` | {} | {} |",
            escape_cell(&node.node_id),
            escape_cell(&node.type_ref),
            escape_cell(&node.label),
            escape_cell(&node.scope)
        ));
    }
    lines.extend([
        String::new(),
        "## Relations".to_owned(),
        String::new(),
        "| ID | Type | Source | Target |".to_owned(),
        "| --- | --- | --- | --- |".to_owned(),
    ]);
    for relation in &package.relations {
        lines.push(format!(
            "| `{}` | `{}` | `{}` | `{}` |",
            escape_cell(&relation.relation_id),
            escape_cell(&relation.type_ref),
            escape_cell(&relation.source_node_id),
            escape_cell(&relation.target_node_id)
        ));
    }
    lines.extend([String::new(), "## Residue".to_owned(), String::new()]);
    if package.residue.is_empty() {
        lines.push("- None.".to_owned());
    } else {
        for residue in &package.residue {
            lines.push(format!(
                "- `{}` — {} Owner: `{}`; treatment: `{}`.",
                residue.residue_id, residue.statement, residue.owner_route, residue.treatment
            ));
        }
    }
    lines.extend([
        String::new(),
        "## Query contract".to_owned(),
        String::new(),
        format!(
            "- Allowed operations: `{}`",
            package.query_contract.allowed_operations.join("`, `")
        ),
        format!(
            "- Unknown identity: `{}`",
            package.query_contract.unknown_identity_behavior
        ),
        format!(
            "- Filesystem reach: `{}`",
            package.query_contract.filesystem_reach
        ),
        String::new(),
        "## Claim ceiling".to_owned(),
        String::new(),
        package.claim_ceiling.clone(),
        String::new(),
    ]);
    lines.join("\n")
}
