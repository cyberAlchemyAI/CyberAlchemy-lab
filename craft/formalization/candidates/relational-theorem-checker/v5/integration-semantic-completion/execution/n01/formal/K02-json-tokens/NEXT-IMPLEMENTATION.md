# Next: complete JSON container/document parsing

Formalization comes first. Define whitespace/value/member scanner interfaces
against the existing independent `ValueMeaning`, `ItemsMeaning`, `MembersMeaning`
and `DocumentMeaning`; do not substitute a parser-output equality for meaning.
Specify sufficient recursion measure before implementation.

| Step | Concrete result | Required verification |
|---|---|---|
| 1 | Boundary check and primitive value dispatcher using proved string/literal/number scanners | Exact primitive meaning, sufficient fuel, suffix and progress; unknown trailing letters refused at qualification |
| 2 | Array items and array parser | Empty and nonempty arrays; exact whitespace/comma/closing bracket; no trailing comma; nested values and ordered output |
| 3 | Object members and object parser | Quoted key, colon, value, comma and closing brace; ordered entries and duplicate decoded keys retained; no trailing comma |
| 4 | Complete value/document parser | Mutual recursion soundness/completeness against existing meanings; exact root whitespace and complete consumption |
| 5 | Full UTF-8 byte document composition | Exact `ByteDocumentMeaning` for all finite grammar-admissible documents; malformed UTF-8 refused without replacement |
| 6 | Supported scalar-AST conversion | Explicit surrogate pairing or unsupported representation; unchanged member order and number lexemes |
| 7 | Actual source bridge | Captured bytes → raw JSON → supported AST → binding records/catalog; realized digest/profile/schema/authentic providers and nineteen source policies |
| 8 | Original closure and integration | Exact 263 IDs, retained 90 original discharges, whole theory/effect and mandatory independent checking; all seven extensions and final actual new use assessment |

Full JSON completeness must preserve valid numeric spellings and unpaired escaped
UTF-16 units at the raw layer. Profile qualification and resource failures need
separate public outcomes, not a narrower syntax claim. Candidate parser APIs do
not freeze N03 or grant owner acceptance. K04 remains the actual pending review.
