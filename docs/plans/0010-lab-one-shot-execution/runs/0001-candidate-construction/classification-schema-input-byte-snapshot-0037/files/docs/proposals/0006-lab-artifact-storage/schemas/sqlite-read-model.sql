-- Proposed disposable read model. These tables do not authorize artifact writes.
-- Draft minimum: SQLite 3.37 for STRICT tables; deployed compatibility remains a selection gate.
-- Enable foreign_keys on every writer connection. Build a complete immutable generation
-- inside one database transaction. Trust its source only after independent verification.
PRAGMA foreign_keys = ON;

CREATE TABLE projection_generation (
  generation_ref TEXT PRIMARY KEY,
  source_cut_sha256 TEXT NOT NULL CHECK(length(source_cut_sha256)=64),
  source_profile_sha256 TEXT NOT NULL CHECK(length(source_profile_sha256)=64),
  projector_sha256 TEXT NOT NULL CHECK(length(projector_sha256)=64),
  contract_catalog_sha256 TEXT NOT NULL CHECK(length(contract_catalog_sha256)=64),
  derived_rows_sha256 TEXT NOT NULL CHECK(length(derived_rows_sha256)=64),
  posture TEXT NOT NULL CHECK(posture IN ('building','ready','stale','invalidated')),
  canonical_replay_source INTEGER NOT NULL DEFAULT 0 CHECK(canonical_replay_source=0),
  authority_effect TEXT NOT NULL DEFAULT 'none' CHECK(authority_effect='none')
) STRICT;

CREATE TABLE stream_watermark (
  generation_ref TEXT NOT NULL REFERENCES projection_generation(generation_ref),
  stream_ref TEXT NOT NULL,
  cursor INTEGER NOT NULL CHECK(cursor>=0),
  head_sha256 TEXT NOT NULL CHECK(length(head_sha256)=64),
  PRIMARY KEY(generation_ref,stream_ref)
) STRICT;

-- An optional exact-byte cache; deletion loses no committed content.
-- Application verifies byte_sha256 against canonical content before indexing/use.
CREATE TABLE content_cache (
  byte_sha256 TEXT PRIMARY KEY CHECK(length(byte_sha256)=64),
  media_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),
  content BLOB NOT NULL,
  CHECK(length(content)=size_bytes)
) STRICT;

CREATE TABLE artifact_revision (
  generation_ref TEXT NOT NULL REFERENCES projection_generation(generation_ref),
  scope_key TEXT NOT NULL,
  version_ref TEXT NOT NULL,
  identity_ref TEXT NOT NULL,
  carrier_ref TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('definition','artifact-type','relation-kind','typed-relation','artifact-instance')),
  semantic_kind TEXT NOT NULL,
  byte_sha256 TEXT NOT NULL CHECK(length(byte_sha256)=64),
  semantic_sha256 TEXT CHECK(semantic_sha256 IS NULL OR length(semantic_sha256)=64),
  semantic_digest_algorithm_ref TEXT,
  source_package_ref TEXT NOT NULL,
  source_entry_ref TEXT NOT NULL,
  admission_posture TEXT NOT NULL,
  domain_posture TEXT,
  implementation_posture TEXT,
  runtime_observation_posture TEXT,
  outcome_posture TEXT,
  PRIMARY KEY(generation_ref,scope_key,version_ref),
  UNIQUE(generation_ref,scope_key,identity_ref,version_ref),
  CHECK((semantic_sha256 IS NULL)=(semantic_digest_algorithm_ref IS NULL))
) STRICT;
CREATE INDEX artifact_by_identity ON artifact_revision(generation_ref,scope_key,identity_ref);
CREATE INDEX artifact_by_type ON artifact_revision(generation_ref,carrier_ref,admission_posture);

CREATE TABLE artifact_head (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  identity_ref TEXT NOT NULL,
  current_version_ref TEXT NOT NULL,
  PRIMARY KEY(generation_ref,scope_key,identity_ref),
  FOREIGN KEY(generation_ref,scope_key,identity_ref,current_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,identity_ref,version_ref)
) STRICT;

-- Global Typed Relation projection only. Ontology-local edges retain their own contracts.
CREATE TABLE typed_relation_projection (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  relation_version_ref TEXT NOT NULL,
  relation_kind_version_ref TEXT NOT NULL,
  source_scope_key TEXT NOT NULL,
  source_version_ref TEXT NOT NULL,
  target_scope_key TEXT NOT NULL,
  target_version_ref TEXT NOT NULL,
  qualifiers_byte_sha256 TEXT NOT NULL CHECK(length(qualifiers_byte_sha256)=64),
  qualifiers_bytes BLOB NOT NULL,
  PRIMARY KEY(generation_ref,scope_key,relation_version_ref),
  FOREIGN KEY(generation_ref,scope_key,relation_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref),
  FOREIGN KEY(generation_ref,source_scope_key,source_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref),
  FOREIGN KEY(generation_ref,target_scope_key,target_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref)
) STRICT;
CREATE INDEX relations_outgoing ON typed_relation_projection(generation_ref,source_scope_key,source_version_ref,relation_kind_version_ref);
CREATE INDEX relations_incoming ON typed_relation_projection(generation_ref,target_scope_key,target_version_ref,relation_kind_version_ref);

CREATE TABLE contract_binding_projection (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  carrier_version_ref TEXT NOT NULL,
  schema_byte_sha256 TEXT NOT NULL CHECK(length(schema_byte_sha256)=64),
  schema_selector TEXT,
  identity_selector TEXT NOT NULL,
  discriminator_selector TEXT,
  discriminator_value TEXT,
  PRIMARY KEY(generation_ref,scope_key,carrier_version_ref),
  FOREIGN KEY(generation_ref,scope_key,carrier_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref)
) STRICT;

CREATE TABLE reference_resolution (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  source_version_ref TEXT NOT NULL,
  reference_selector TEXT NOT NULL,
  requested_ref TEXT NOT NULL,
  resolved_scope_key TEXT,
  resolved_version_ref TEXT,
  posture TEXT NOT NULL CHECK(posture IN ('resolved','unresolved','excluded','ambiguous','historical')),
  PRIMARY KEY(generation_ref,scope_key,source_version_ref,reference_selector),
  FOREIGN KEY(generation_ref,scope_key,source_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref),
  FOREIGN KEY(generation_ref,resolved_scope_key,resolved_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref),
  CHECK((resolved_scope_key IS NULL)=(resolved_version_ref IS NULL)),
  CHECK(posture NOT IN ('resolved','historical') OR resolved_version_ref IS NOT NULL)
) STRICT;

-- Indexed evidence of existing Decisions, never grants derived from SQL rows.
CREATE TABLE authority_fact_projection (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  subject_version_ref TEXT NOT NULL,
  decision_ref TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  effect_scope_ref TEXT NOT NULL,
  selected_outcome TEXT NOT NULL,
  evidence_byte_sha256 TEXT NOT NULL CHECK(length(evidence_byte_sha256)=64),
  PRIMARY KEY(generation_ref,scope_key,subject_version_ref,decision_ref,effect_scope_ref),
  FOREIGN KEY(generation_ref,scope_key,subject_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref)
) STRICT;

CREATE TABLE ontology_representation_link (
  generation_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  represented_version_ref TEXT NOT NULL,
  ontology_ref TEXT NOT NULL,
  node_version_ref TEXT NOT NULL,
  ontology_semantic_cursor INTEGER NOT NULL CHECK(ontology_semantic_cursor>=0),
  ontology_governance_cursor INTEGER NOT NULL CHECK(ontology_governance_cursor>=0),
  mapping_sha256 TEXT NOT NULL CHECK(length(mapping_sha256)=64),
  PRIMARY KEY(generation_ref,scope_key,represented_version_ref,ontology_ref,node_version_ref),
  FOREIGN KEY(generation_ref,scope_key,represented_version_ref)
    REFERENCES artifact_revision(generation_ref,scope_key,version_ref)
) STRICT;

CREATE TABLE projection_gap (
  generation_ref TEXT NOT NULL REFERENCES projection_generation(generation_ref),
  gap_ref TEXT NOT NULL,
  scope_key TEXT NOT NULL,
  subject_ref TEXT NOT NULL,
  gap_kind TEXT NOT NULL,
  owner_route TEXT NOT NULL,
  blocking_use TEXT NOT NULL,
  PRIMARY KEY(generation_ref,gap_ref)
) STRICT;

-- This pointer publishes a database generation only; it does not advance canonical history.
CREATE TABLE active_generation (
  slot TEXT PRIMARY KEY CHECK(slot='artifact-read-model'),
  generation_ref TEXT NOT NULL REFERENCES projection_generation(generation_ref)
) STRICT;
