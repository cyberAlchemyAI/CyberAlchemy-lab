CREATE SCHEMA IF NOT EXISTS kep_hosted;

-- statement
CREATE TABLE IF NOT EXISTS kep_hosted.application_state (
  state_id SMALLINT PRIMARY KEY CHECK (state_id = 1),
  state_json JSONB NOT NULL,
  revision BIGINT NOT NULL CHECK (revision > 0),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- statement
CREATE TABLE IF NOT EXISTS kep_hosted.event_journal (
  event_id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  event_json JSONB NOT NULL,
  previous_event_digest BYTEA NOT NULL CHECK (octet_length(previous_event_digest) = 32),
  event_digest BYTEA UNIQUE NOT NULL CHECK (octet_length(event_digest) = 32),
  created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- statement
CREATE TABLE IF NOT EXISTS kep_hosted.encrypted_archive (
  object_digest BYTEA PRIMARY KEY CHECK (octet_length(object_digest) = 32),
  encrypted_bytes BYTEA NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- statement
CREATE TABLE IF NOT EXISTS kep_hosted.client_error_journal (
  event_id BIGSERIAL PRIMARY KEY,
  attempt_id TEXT UNIQUE NOT NULL,
  operation_kind TEXT NOT NULL,
  stage TEXT NOT NULL,
  error_code TEXT NOT NULL,
  effect_status TEXT NOT NULL,
  network TEXT NOT NULL CHECK (network = 'solana-devnet'),
  safe_message TEXT NOT NULL,
  diagnostic_digest BYTEA NOT NULL CHECK (octet_length(diagnostic_digest) = 32),
  rpc_request_id TEXT,
  transaction_signature TEXT,
  event_digest BYTEA UNIQUE NOT NULL CHECK (octet_length(event_digest) = 32),
  created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- statement
CREATE OR REPLACE FUNCTION kep_hosted.reject_immutable_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'KEP hosted recovery records are append-only or immutable';
END
$$;

-- statement
DROP TRIGGER IF EXISTS kep_hosted_journal_immutable ON kep_hosted.event_journal;

-- statement
CREATE TRIGGER kep_hosted_journal_immutable BEFORE UPDATE OR DELETE ON kep_hosted.event_journal FOR EACH ROW EXECUTE FUNCTION kep_hosted.reject_immutable_mutation();

-- statement
DROP TRIGGER IF EXISTS kep_hosted_archive_immutable ON kep_hosted.encrypted_archive;

-- statement
CREATE TRIGGER kep_hosted_archive_immutable BEFORE UPDATE OR DELETE ON kep_hosted.encrypted_archive FOR EACH ROW EXECUTE FUNCTION kep_hosted.reject_immutable_mutation();

-- statement
DROP TRIGGER IF EXISTS kep_hosted_client_error_immutable ON kep_hosted.client_error_journal;

-- statement
CREATE TRIGGER kep_hosted_client_error_immutable BEFORE UPDATE OR DELETE ON kep_hosted.client_error_journal FOR EACH ROW EXECUTE FUNCTION kep_hosted.reject_immutable_mutation();
