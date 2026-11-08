PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS auth_authentication_evidence (
    evidence_row_id INTEGER PRIMARY KEY,
    evidence_ref TEXT NOT NULL CHECK (length(evidence_ref) > 0),
    session_id TEXT NOT NULL CHECK (length(session_id) > 0),
    trusted INTEGER NOT NULL CHECK (trusted IN (0, 1)),
    revoked INTEGER NOT NULL CHECK (revoked IN (0, 1)),
    expires_at INTEGER NOT NULL CHECK (expires_at >= 0),
    evidence_revision INTEGER NOT NULL CHECK (evidence_revision >= 0),
    authenticated_subject_id TEXT NOT NULL CHECK (length(authenticated_subject_id) > 0)
);

CREATE INDEX IF NOT EXISTS auth_authentication_evidence_by_ref
    ON auth_authentication_evidence (evidence_ref, evidence_row_id);

CREATE TABLE IF NOT EXISTS auth_route_authorization_bindings (
    binding_row_id INTEGER PRIMARY KEY,
    route_id TEXT NOT NULL CHECK (length(route_id) > 0),
    resource TEXT NOT NULL CHECK (length(resource) > 0),
    action TEXT NOT NULL CHECK (length(action) > 0),
    scope TEXT NOT NULL CHECK (length(scope) > 0),
    scope_evidence_ref TEXT NOT NULL CHECK (length(scope_evidence_ref) > 0),
    complete INTEGER NOT NULL CHECK (complete IN (0, 1)),
    enabled INTEGER NOT NULL CHECK (enabled IN (0, 1)),
    binding_revision INTEGER NOT NULL CHECK (binding_revision >= 0)
);

CREATE INDEX IF NOT EXISTS auth_route_bindings_by_route
    ON auth_route_authorization_bindings (route_id, binding_row_id);

CREATE TABLE IF NOT EXISTS auth_sessions (
    session_row_id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL CHECK (length(session_id) > 0),
    user_id TEXT NOT NULL CHECK (length(user_id) > 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'revoked')),
    authorization_revision INTEGER NOT NULL CHECK (authorization_revision >= 0),
    expires_at INTEGER NOT NULL CHECK (expires_at >= 0)
);

CREATE INDEX IF NOT EXISTS auth_sessions_by_session_id
    ON auth_sessions (session_id);

CREATE TABLE IF NOT EXISTS auth_roles (
    role_id TEXT PRIMARY KEY CHECK (length(role_id) > 0)
);

CREATE TABLE IF NOT EXISTS auth_session_active_roles (
    session_row_id INTEGER NOT NULL REFERENCES auth_sessions(session_row_id) ON DELETE CASCADE,
    role_id TEXT NOT NULL REFERENCES auth_roles(role_id),
    authorization_revision INTEGER NOT NULL CHECK (authorization_revision >= 0),
    PRIMARY KEY (session_row_id, role_id)
);

CREATE TABLE IF NOT EXISTS auth_role_permissions (
    role_id TEXT NOT NULL REFERENCES auth_roles(role_id) ON DELETE CASCADE,
    resource TEXT NOT NULL CHECK (length(resource) > 0),
    action TEXT NOT NULL CHECK (length(action) > 0),
    scope TEXT NOT NULL CHECK (length(scope) > 0),
    authorization_revision INTEGER NOT NULL CHECK (authorization_revision >= 0),
    PRIMARY KEY (role_id, resource, action, scope)
);

CREATE TABLE IF NOT EXISTS auth_authorization_revisions (
    session_id TEXT PRIMARY KEY CHECK (length(session_id) > 0),
    revision INTEGER NOT NULL CHECK (revision >= 0)
);

CREATE TABLE IF NOT EXISTS auth_scope_evidence (
    evidence_ref TEXT PRIMARY KEY CHECK (length(evidence_ref) > 0),
    resource TEXT NOT NULL CHECK (length(resource) > 0),
    action TEXT NOT NULL CHECK (length(action) > 0),
    scope TEXT NOT NULL CHECK (length(scope) > 0),
    trusted INTEGER NOT NULL CHECK (trusted IN (0, 1))
);

PRAGMA user_version = 2;
