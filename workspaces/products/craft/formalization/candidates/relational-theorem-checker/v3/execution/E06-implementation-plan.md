# E06 implementation plan

Research primary Lean/kernel/export sources and independent proof-checking documentation. Specify a genuinely independent bounded sample checker with explicit supported constructors, universes, primitive signatures, complete instantiated dependency closure and translation trust. The accepted core continues to use its pinned Lean replay.

Select an actual accepted theorem fitting the fragment, export its exact AST statement/proof/definition closure and universe instances from Lean, then check that export using a separately implemented typed evaluator which does not call Lean or trust its acceptance flag. Check a positive sample and reject altered statement/definition, missing universes, unsupported primitives/axioms and forged accepted flags. Document unsupported constructs and wider implementation cost; sample success is never described as independent checking of the whole relational core.

This is a feasibility unit, not deployment or replacement of the mandatory checker. Evidence must include actual independent checking, complete closure accounting and exact claim scope. No core delivery depends on unproved broader translation or checking. Review feasibility and trust boundaries after actual sample controls.
