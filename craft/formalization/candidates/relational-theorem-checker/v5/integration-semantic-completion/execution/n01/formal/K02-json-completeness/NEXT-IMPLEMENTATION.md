# Next implementation sequence

1. **Formalize representation conversion first.** Define an independent relation
   between raw UTF-16-unit strings and the existing scalar-string binding AST.
   Cover scalar BMP units, paired supplementary surrogates, empty strings and
   arrays/ordered object entries recursively. Define explicit unsupported results
   for unpaired surrogate units; preserve number lexemes and member order.
   Specify whether different spellings of the same decoded key collide at the
   binding qualification stage. Do not infer that duplicate raw keys are syntax
   errors.
2. Implement the converter and prove soundness, completeness on its stated
   supported domain, exact refusal meaning and field preservation. Compose it
   with `byte_document_parser_exact` without narrowing the raw grammar silently.
3. Formalize and implement actual source-to-binding preparation: exact captured
   bytes, owned parser profiles, digest computation and binding record decoding.
   Prove correspondence with the existing complete field-preserving decoder.
   Keep original fixture parsing and authentication separately evidenced.
4. Formalize Schema/record correspondence and realize the nineteen owned K02
   policies. Missing ownership, evidence or authentication must produce a useful
   refusal; no always-true policy adapters.
5. Define public outcome contracts and measure an explicit supported runtime
   envelope, including deep nesting, long strings/numbers, broad objects and
   malformed inputs. Sufficient abstract recursion fuel is not a measured
   latency, stack or memory bound.
6. Complete K02 relation/effect/forbidden-conclusion obligations and mandatory
   independent closure checking before any inherited ID is discharged.

K04 remains the pending one-at-a-time semantic-owner review. Preparation can
continue within existing authorization; its answer must not be inferred from
K03, parser proofs or earlier bounded-use assessments. The all-41-kind,
550-pair, seven-extension DAG and actual new final bounded-use assessment keep
 their scope. Nothing here authorizes publication or promotion.
