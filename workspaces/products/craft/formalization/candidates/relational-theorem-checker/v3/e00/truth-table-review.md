# Truth-table review before runtime

The universal formal module compiled before the Python evaluator was written. This is an author semantic review of the proposed separate profile, not a new human assessment or an external leaf-truth claim.

Strong Kleene conjunction is yes only for yes/yes, no whenever either operand is no, and unknown otherwise. Disjunction is no only for no/no, yes whenever either operand is yes, and unknown otherwise. Negation swaps yes/no and preserves unknown. Thus `unknown or yes` is yes and `unknown and no` is no; these are truth-table results, not skipping validation of other evidence. Every supplied leaf record must first be valid, even in a branch that cannot change the result.

| Left | Right | AND | OR |
| --- | --- | --- | --- |
| yes | yes | yes | yes |
| yes | no | no | yes |
| yes | unknown | unknown | yes |
| no | yes | no | yes |
| no | no | no | no |
| no | unknown | no | unknown |
| unknown | yes | unknown | yes |
| unknown | no | no | unknown |
| unknown | unknown | unknown | unknown |

Independent meaning is two evidence rails. Conjunction intersects positive and unions negative support; disjunction unions positive and intersects negative support; negation swaps support. `evaluation_denotes` proves equality for every expression and total keyed environment by induction, using all truth-table rows. `activation_exact` proves origin membership iff potential origin membership and positive independent meaning. Exact atom-key and missing-unknown theorems preserve all frame/condition fields.

Choice: include bounded negation in this separate expression profile. It does not add negated Horn rules to the core. Contradictory supplied values are rejected before constructing the formal environment; they are not a fourth truth value or an explosion rule. Missing evidence is unknown; stale, extraneous or mismatched supplied keys are invalid. All operator rows and these distinctions are accepted by this author review for candidate implementation.
