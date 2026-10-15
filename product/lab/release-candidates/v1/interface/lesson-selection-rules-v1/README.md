# Lesson selection rules

Candidate pure evaluator for the frozen internal lesson routing, applicability and
domain profile contracts. It produces the original Lesson Selection and exact
check bytes. It creates no Application, store write, permission or admission.

## Inputs and authority

The future API host must supply independently selected current facts: a complete
signed lesson inventory, live authenticated Session and Assignment, original
source cut, exact review dispositions, retention and applicability witnesses,
current instruction precedence and assessments of every literal exclusion.
Constructing `ContextFacts`, `LessonFact` or `ReviewFact` authenticates nothing.
The evaluator compares every original witness to those selected facts and checks
all three closed internal schemas and the original canonical Lesson schema.

Routing must cover the complete ordered inventory exactly. Missing witnesses,
changed bytes, unknown current entries or conflicting cuts cannot become an empty
result. Explicit absent review/applicability/retention blocks that lesson. Valid
expiry, exclusions, instructions and contradictory counterevidence omit it.
Unresolved conditions block it. Different influences within one applicable
family block both; excluded or expired lessons cannot introduce conflicts.

The declared domain profile generalizes W06's fixed status, retention and review
assumptions explicitly. Its values grant no review authority. Original W06
implementation and all its tests remain separate immutable predecessors.

## Evidence and lifetime

Returned check bytes retain original evidence and counterevidence bindings and
the selection reason. The host must materialize these bytes only in its owned
evidence workspace and complete live source/permission exit checks before exposure.
It must dispose transient rule state with the real Session. Durable continuity
comes from Project State through Context and Ontology Views.

`checks.py` executes 56 synthetic pure tests and the 53 original W06 tests without
changing them. These prove rule behavior and predecessor retention. They do not
qualify `lesson.select`, actual signed-source transport, assigned Agent permission,
genuine participant use or an owner outcome. Public host integration is pending.
