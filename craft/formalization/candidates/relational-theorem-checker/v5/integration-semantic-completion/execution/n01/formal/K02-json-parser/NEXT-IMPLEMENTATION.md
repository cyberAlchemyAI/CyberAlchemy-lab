# Next: prove complete recursive grammar refinement

Formalize each theorem against the existing independent grammar before trying
to prove implementation adequacy. Retain the full raw JSON syntax, including
original numeric spellings, ordered duplicate decoded keys and escaped unpaired
UTF-16 units.

1. Add grammar reconstruction lemmas for leading/trailing whitespace and body
   separators. Prove nonempty and starting-character facts for values, items and
   members, without referring to parser output.
2. Prove the three mutually recursive soundness statements by fuel induction:
   value result implies `BoundedValuePrefixMeaning`; array body implies
   `ArrayBodyMeaning`; object body implies `ObjectBodyMeaning`. For false
   `allowEmpty`, prove nonempty output. Retain exact original suffixes.
3. Prove completeness by independent grammar derivation, with a consumed-word
   length bound sufficient for all modes. Establish `RecursionBudget` adequacy
   rather than merely asserting that structural termination suffices.
4. Derive quantified value and document exactness, uniqueness and complete root
   consumption. Compose with exact UTF-8 decoding to prove `ByteDocumentMeaning`.
5. Formalize and implement scalar-AST conversion with explicit surrogate pairing
   or unsupported representation. Preserve member order, duplicate keys and
   original number lexemes, then perform binding-schema qualification.
6. Prove actual source capture → raw JSON → supported AST → binding records/catalog,
   using realized digest/profile/Schema/authentic-review providers and all nineteen
   K02 policies. Labels or a matching claimed digest are insufficient.
7. Finish original relation/effect/theory closure, exact inherited-ID audit and
   mandatory independent checking. Implement public outcomes and measured resource
   limits, integrate all seven extensions and obtain the actual final new use
   assessment through the existing 20-task DAG.

Candidate evidence does not accept K04 or global policies, freeze N03 or discharge
any inherited semantic ID. The active full-plan scope is unchanged.
