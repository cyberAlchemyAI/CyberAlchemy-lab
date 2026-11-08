# Independent review of current-family authentication source names

Reviewed the closed JSON Schema successor emitted by auth_schema_current_names.py and independently reran all six Draft 2020-12 cases in normal and optimized Python. Both passed, including exactly one matching metadata policy variant, renewed family name, retained old names, unrelated-name/extra-field refusal, dedicated Lesson variant non-overlap and unchanged integrated/history branches.

The schema change admits only the lexical current-Legacy/current-participation names needed by the installed provider. Other fields, required properties, oneOf structure, budget and scope constraints remain. Accepting a lexical name is not Source selection: the actual Reader validates exact independently installed family, actual producer/module origin, period, principal separation, nonce, policy hash, UID, purposes and operation-specific controls. A request cannot retarget those private installed inputs.

No blocking finding in this schema correction. It makes the existing current-family authority checks reachable rather than bypassing them. Actual full-policy authentication and final integrated API tests remain required.

Reviewed helper SHA: 0389d021b1a4b86870e931dade8a1abd243965ee7aac9b93c08aed9e84dfcb77
Reviewed composed authentication.schema.json SHA: 78ef67e39516c8264c257edaeca90576ae3a804f50ff8546f4b45ca7e0bfb980
