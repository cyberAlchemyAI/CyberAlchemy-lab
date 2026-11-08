# Commerce-compatible construction plan

Status: implementation and local product tests complete. Owner-directed local product construction;
no admission, product approval, publication or deployment is implied.

## Definition and ontology prototypes

Antecedent: ../domainspec-application-trial-v1/NEXT-PROFILE.md.
Selected ontology dependencies: all nodes and relations in ALCH-CD-PRODUCT-VIEW
and ALCH-CD-BUSINESS-VIEW under definitions/compiler-domain-separation/v1.

Numeric Representation Contract: exact UInt64 calculation inputs, integer
arithmetic, rounding and failure semantics. Calculation results are bigint.
Query Evaluation Contract: supplied rows only; filtering, stable sorting,
limit and projection with missing-field errors and no mutation.
Target Compatibility Gap: source-bound reason a declaration cannot be lowered.

Prototype relations: Compiler Binding selects Numeric Representation Contract;
Query Declaration conforms to Query Evaluation Contract; Domain Declaration may
expose Target Compatibility Gap. These scaffolds are unregistered, non-authoritative.
Product outcome: unchanged commerce source produces equivalent values and errors.
Business limit: support claims cannot hide rejected declarations or narrow UInt64.

## Product construction

Frontier: tested exact-profile candidate; product review remains unrecorded.
Completed construction sequence:
1. DomainSpec opt-in TypeScript realization and profile-bound build/verify receipts.
2. AlchLang explicit profile, complete commerce lowering and checked entry.
3. Parity, boundaries, failures, determinism and existing-profile regression tests.
4. Current usage documentation and one source-hashed candidate with test evidence.

The existing typed-contract schemas can represent full UInt64 constants through
exact base-2^32 decomposition using safe literal leaves. Trace records must identify
this derivation. No unsafe JSON Number or new implicit compiler behavior is needed.
Integer record inputs accept bigint or nonnegative safe integer Numbers. Calculation
inputs additionally accept canonical unsigned decimal strings. Mapping and query
outputs preserve supplied representation; predicates retain source equality and
ordering semantics. Unsafe Numbers reject rather than being rounded.

The first exact profile limits queries to one sort key (the target schema's
current contract). Other unsupported constructs remain explicit rejections.

## Operational support

Owner: repository maintainer. Rebuilding the local bound CLI affects the compiler
binding stage and is part of local verification. Packaging, registry publication,
release and deployment are deferred with no construction stage affected here.
No operational queue blocks runnable prototype work. No public subsystem changes.

## Open questions

Product approval of the exact tested candidate remains an owner decision. Additional
sort keys, decimal arithmetic and other backend kinds are outside this increment.
