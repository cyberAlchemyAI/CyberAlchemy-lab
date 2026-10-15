Complete heterogeneous typed payload bodies — formalization first

Preserve each complete original schema for Intent, Assignment, Goal, Product,
Capability, Project and Inquiry, including all nested fields and conditionals.
The source body denotation relates a raw ordered JSON AST to a typed record
containing every declared field. Object interpretation is independent of member
order, rejects duplicate/unknown members, and retains the exact source byte
capture outside the typed value. Do not invent a shared node/schema header.

String denotation is the original scalar String meaning, constrained by the exact
minimum character count, constant, enum membership and one of the two pinned
ECMAScript pattern meanings. Null-or-string means either JSON null and None, or
the complete constrained String and Some. Empty strings and null remain distinct.

Array denotation preserves order and cardinality and interprets every occurrence
using the complete element meaning. Bounds constrain the resulting cardinality.
uniqueItems requires pairwise distinct complete typed element values: for each
fixed closed object schema these values contain every field, independent of raw
member order. Do not compare raw object ordering or drop evidence/unused fields
to obtain uniqueness. No admitted body schema allows a numeric leaf, so integer
epoch conversion is not used to interpret or compare source body values.

Closed object denotation requires exactly the schema's declared required fields,
each through its complete component meaning. The seven original active object
schemas make every declared property required; generation must check this fact
rather than assume it for an arbitrary schema. Local Goal $refs are expanded
from the exact captured $defs. Documentation and unused definitions remain bound
in the original schema capture; they are not additional instance assertions.

Intent's two full-record constraints independently require nonempty satisfaction
references in the satisfied posture and nonempty successors in the superseded
posture. This is shape qualification only. Actual satisfaction or succession
requires the remaining semantic policies and evidence.

First prove generic refinement for constrained, mapped, nullable and array
decoders using independent meanings. Generate fixed complete typed records and
decoders from the pinned schema closure, audit every assertion/field/revision,
then check success iff each independent whole-record denotation. Retain the
original source-schema bindings and run the original positive/hostile controls.

Each kind-specific decoder can wrap its complete value in the heterogeneous Body
sum. The catalog-wide dispatcher must subsequently select the exact body kind
and prove complete soundness, completeness and kind/source/profile correspondence;
a caller-selected kind-specific helper alone does not complete that integration.
The Python/Lean/general JSON Schema correspondence still needs proof, beyond
finite fixture agreement. Genuine schema admission, source/identity/owner/scope,
World/selection and all eighteen non-parser policies remain explicit.

No owner assessment is inferred. K04/global review remains pending, all 263
inherited obligations remain open and 90 original discharges retain scope.
