# Finite inference semantics, candidate profile v1

This profile defines positive, function-free, range-restricted Horn rules over a
captured finite active domain. It preserves F0 and the captured registry. It
does not interpret the remaining unsupported natural-language relation effects.
I01 establishes a contract and tested projection; I02–I06 must supply its proofs
and integration evidence before a rule-changing extension is ready.

Each value has a sort: reference, effect, scope, epoch or text. A reference is
the exact pair `(artifact ID, version)`; epochs are natural numbers. Predicate
identities bind their declared ID, version, signature, role and content hash.
Rules bind ID, version, complete source syntax and resolved predicate identities.
An omitted predicate version resolves only against the unique explicitly
captured declaration. No runtime registry lookup supplies an implicit version.

A ground atom consists of a captured predicate identity and a correctly sorted
argument tuple from the finite domain. A pattern term is either an indexed
variable or a captured constant. A substitution assigns every variable exactly
one domain value of its declared sort. Instantiation replaces each variable in
the head and all positive body premises. Every variable occurs in a body
premise. Rules can introduce tuples but cannot introduce fresh values,
identities, function terms, external facts or independently checked roots.
Ground rules with an empty body and only captured constants are allowed.

Let `T` be the typed captured rule theory and `F` its validated initial facts.
Define `Derivable(T,F,a)` independently by two inductive constructors:

1. Any `a` in `F` is derivable.
2. For any rule in `T` and any valid ground substitution, if every instantiated
   body premise is derivable, the instantiated head is derivable.

The finite Herbrand universe is the set of correctly sorted ground atoms over
the declared predicates and active domain. A model `M` contains `F` and contains
each ground rule head whenever it contains every corresponding premise.
The least closure is the intersection of such models, equivalently the least
fixed point of the immediate-consequence operator beginning with `F`.
Certificate soundness must imply the independent inductive derivability
predicate. Closure certification must prove base inclusion, saturation for
*every* valid ground substitution, and derivability of every included atom.
Soundness alone is insufficient for a negative derivability claim.

The protected tuple is exactly
`(targetVersion, effect, scope, capturedAuthorityEpoch)`.
`Admitted` and any `root-carrier` predicate have this signature. `CheckedRoot`
has the same signature and may only originate from independent supplied
existing-admission evidence. It cannot be a rule head. Matching is literal,
including the artifact version and all three other coordinates; there are no
wildcards, scope inheritance or epoch conversion.

Independent root assessment files bind receipt ID, version and SHA-256, use the
`existing-admission` evidence role, have `accepted: true`, and match the tuple
and captured epoch. Their declared truth is an external assumption. Hash
matching and role validation do not authenticate an issuer, perform an actual
admission, validate signatures or prove the real-world assessment true. The
candidate accepts no authority transition and reports `authority_effect: none`.
Every protected or carrier initial fact requires such an exact independent
root. Root observations never automatically add an `Admitted` fact.

Logical rule validity and protected justification are separate obligations.
The frontend allows a well-typed positive rule producing `Admitted` for analysis
and reports that protected policy review remains required. I04 must check every
producer of `Admitted` or a root carrier: a matching checked root or already
justified carrier must occur in its body. Its generic induction must establish
that every derived protected tuple has an independent matching root, including
through intermediate rules. A logically valid leaking rule is a policy failure,
not an accepted authority bridge. An ordinary intermediate predicate cannot
launder the missing justification.

Conformance alone is not root evidence. The profile imposes no negative axiom
`Conforms(x) -> not Admitted(x,...)`. Conformance and independently justified
existing admission may coexist. A model satisfying the exact theory with
conformance true and admission false proves non-entailment of that implication.
Absence from a checked complete closure establishes non-derivability for the
captured finite profile; an unsuccessful or interrupted search establishes
neither claim. I05 must check witnesses against all model obligations.

Excluded constructs include negation, disjunction, generated terms, arithmetic
constraints, unbounded temporal reasoning and fresh identity creation. Adding
them requires another profile and its own soundness and termination arguments.
The JSON parser, canonical hashing, host projection and supplied evidence truth
remain explicit trust boundaries; later Lean audits do not erase them.
