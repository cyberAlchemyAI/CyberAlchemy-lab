Complete payload body provider — formalization before implementation

The original K02 payload catalog contains bodies for Intent, Agent Assignment,
Goal, Product, Product Capability, Project and Research Inquiry. A String body
fixture does not realize their source formats. Preserve each whole body and the
exact current repository artifact/schema contract; do not impose a common header.
Goal's identity field is goal_id; the other six use node_id. Several bare body
schemas have neither schema_version nor a common payload field. The schema_ref
from artifact.json is authoritative for profile identification: three v1 artifact
directories currently refer to v2 review schemas. A directory name is not a
schema revision.

For a frozen profile P and submitted original bytes B, the independent target is:

    CandidateBody(P, B, identity, body) iff
      P selects an exact supported artifact/schema definition AND
      B is a supported complete strict UTF-8 JSON object with unique members AND
      body is the complete decoded object, with no dropped or invented fields AND
      body satisfies every assertion in the complete pinned schema AND
      identity is exactly body[P.identity_field].

The byte parser must preserve original B for later digest and source joins.
Reject duplicate names at every object level, malformed UTF-8/JSON, unsupported
scalar surrogates and non-JSON numeric constants. Explicit byte/depth/numeric
limits precede excessive parser work. These local limits do not replace the
full parent-plus-nested budget already formalized in the original entrypoint.

OwnedBody adds independent source issuance, exact schema ownership/admission,
typed identity interpretation, owner/scope authority, frame and freshness
premises. CandidateBody does not imply OwnedBody. A role string in an artifact
definition is not an actual assigned owner. Candidate-unadmitted source types
remain candidate-unadmitted after successful decoding. Body validity does not
imply that an Intent is satisfied, a Goal achieved, a Project complete or an
Assignment authorized. No arbitrary approval Boolean is accepted.

Implementation order: capture and audit the seven exact original schema/profile
bindings; implement complete byte-to-body validation; exercise actual repository
positive and negative fixtures plus field/constraint counterexamples; expose the
remaining formal correspondence and authority gaps explicitly. The installed
Draft202012Validator is an implementation dependency, not a Lean proof oracle.
Its behavior and Python regular-expression interpretation need correspondence
analysis before a general JSON Schema refinement theorem can be claimed.

The next integration step must construct a proved Decoder for heterogeneous full
bodies and join its selected profile to the captured source kind, exact schema
revision and owned identity policy. This prototype must not replace the registered
Lean decoder, mark approved kind-specific decoders realized, or discharge any of
the eighteen remaining policy slots or 263 inherited obligations.

Controls must include every required top-level field, all seven complete positive
bodies, available original hostile witnesses, nested fields, unknown properties,
array uniqueness/bounds, constants/enums, conditional Intent satisfaction and
succession, Goal's local references, Research Inquiry timestamps, digest/profile
substitution and malformed/duplicate/surrogate input. Passing fixtures establish
only the exercised behavior; general refinement and authenticity remain pending.
