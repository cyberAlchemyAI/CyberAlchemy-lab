# Local control plane prototype definitions

Status: private candidate specializations; no canonical vocabulary promotion. Canonical owner remains CyberAlchemy-v2 authority/definitions.

## LCP-TENANT: Tenant

Formal prototype meaning: A server-configured principal owning projects; every lookup includes that principal identifier.

Plain language (interpretive): An account whose projects are separate from other accounts.

Alch context (interpretive): The authenticated operator-configured user ID is the SQLite tenant key.

## LCP-PROJECT: Project scope

Formal prototype meaning: A (tenant, project) pair bounding revision and route access, additionally restricted by credential scopes.

Plain language (interpretive): The workspace containing one user’s functions.

Alch context (interpretive): HTTP project paths are resolved with the authenticated tenant, never a caller-supplied tenant.

## LCP-REVISION: Function revision

Formal prototype meaning: An immutable source and compiled artifact set bound by hashes to a compiler binding and one tenant/project.

Plain language (interpretive): A recorded build that cannot be overwritten through the API.

Alch context (interpretive): The registry stores a server-generated revision ID; each revision has separate runtime state.

## LCP-ROUTE: Active route

Formal prototype meaning: A transactional (tenant, project, function) pointer to a verified ready revision.

Plain language (interpretive): The version that receives new calls.

Alch context (interpretive): Activation first starts the bound host, then updates SQLite; older revisions retain their own state and delivery workers while this process lives.

## Open Questions

See [README](README.md#open-questions).
