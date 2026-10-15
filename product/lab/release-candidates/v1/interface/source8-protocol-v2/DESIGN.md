# Versioned Source8 protocol closure

This candidate package gives the exact Source8 carrier/catalog extension its own
schema resource identities. The predecessor common/v1 and domain resources stay
available with their original meanings. No original URI is overwritten.

The operator profile v4 selects this closed resource set by exact byte hash. The
existing wire call/reply v2 shape is retained; its required independent contract
profile binding identifies the revised eligibility rules. Internal requests to
validate a predecessor protocol name are explicitly translated through the
selected profile map. This does not change the original resource in the registry.

## Exact extension

- Add only `cal.artifact-type.typed-relation/v4` to the eleven existing carrier
  enum surfaces that previously contained Typed Relation/v3.
- Add one domain-artifact branch bound to the exact frozen Typed Relation/v4
  schema. Original carrier branches and all closed qualifier rules remain.
- Add one catalog representation for the exact signed local v4 declaration.
  Its body, original bytes, metacarrier, instance schema, source snapshot and
  transaction are bound independently. It is catalog metadata, not a domain
  instance or canonical admission.
- Rebind retained baseline catalog envelopes to the actual current host's
  unchanged catalog map. The predecessor copied schema used api-v23's locator
  while later hosts emitted their own locator; that exact metadata mismatch is
  corrected in this candidate.

## Example

A query can return the original signed Goal-to-Project Typed Relation/v4 header.
Inspecting its body must validate against the exact v4 schema and return its
original byte hash. Inspecting `cal.artifact-type.typed-relation/v4` instead
returns the signed contract declaration as catalog metadata. Neither response
grants authority, admits the candidate carrier globally, or activates a consumer.

## Verification scope

Original resource validation must continue to reject a v4 header. The new
resource must accept its exact shape and reject unknown carriers and malformed
headers. Actual current source query/inspection, original-body parity, closed
domain validation and source/guard preservation require separate qualification.
All 323 inherited API method ASTs are retained; their full execution and all
remaining 34-operation/46-task plan obligations still apply.

Revision 2 additionally selects the signed original catalog locator when building
the complete SQLite generation, and binds baseline catalog metadata to API93.
