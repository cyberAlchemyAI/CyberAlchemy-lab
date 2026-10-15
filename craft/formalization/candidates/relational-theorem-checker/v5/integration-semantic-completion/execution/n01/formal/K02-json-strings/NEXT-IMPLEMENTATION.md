# Next implementation, starting with independent meanings

1. Formalize prefix boundaries for JSON literals and numbers using the existing
   document and decimal grammar. Specify exact original lexeme and suffix;
   refuse incomplete fractions/exponents and leading-zero continuations at
   whole-document qualification. Prove each prefix decoder sound and complete.
2. Formalize whitespace-prefixed value/array/object scanner meanings and a
   well-founded recursion measure. Specify comma/colon placement, empty
   containers, no trailing comma, nesting, ordered decoded key/value entries
   and whole input consumption. Implement only after these meanings are fixed.
3. Prove the complete document decoder exact against `DocumentMeaning`, then
   compose it with the proved UTF-8 decoder against `ByteDocumentMeaning`.
4. Formalize and implement explicit UTF-16-unit to scalar-string AST conversion.
   Prove scalar range, surrogate pairing, unchanged member order and exact number
   lexemes. Represent unsupported raw units explicitly; do not silently narrow
   the independent JSON grammar or replace data.
5. Join complete bytes → raw JSON → supported AST → existing binding-record
   decoder → retained catalog stage. Prove the actual source-capture bridge,
   digest/profile/schema/review providers and all nineteen source policies.
6. Complete original relation semantics, effect/forbidden-claim coverage and
   mandatory independent closure. Audit all exact inherited IDs and preserve
   original discharge scope, then run all seven integration extensions and the
   final actual new use assessment in the existing 20-task DAG.

The candidate APIs and proofs are N01 preparation. They do not freeze N03,
accept the parser profile or discharge the 263 inherited obligations. The
actual sequential K04 review remains pending; no other relation or global
policy receives implied acceptance.
