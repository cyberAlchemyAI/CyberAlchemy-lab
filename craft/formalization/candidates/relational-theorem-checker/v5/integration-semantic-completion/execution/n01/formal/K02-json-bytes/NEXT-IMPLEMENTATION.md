Next: implement the full document parser against the independent meaning

1. Implement exact string-unit prefix decoding first: raw scalar, the eight simple
   escapes and exactly four hex digits. Prove soundness/completeness against
   StringUnitMeaning with the original encoded prefix and suffix retained. Include
   all lowercase/uppercase hex forms and unpaired surrogate units without replacement.
2. Implement quoted-string scanning and prove full StringMeaning equivalence,
   preservation of decoded units and exact consumed input. Check escaped versus
   literal equivalent member names before duplicate qualification.
3. Compose complete number-prefix, literal, array and object parsing with the proved
   UTF-8 decoder and existing full number grammar. Prove complete document parsing
   against DocumentMeaning/ByteDocumentMeaning, including trailing-input refusal,
   exact whitespace, ordered arrays and retained duplicate object members.
4. Formalize and implement conversion to the existing scalar-string AST or its
   approved representation extension. Define explicit outcomes for unpaired units,
   BOM policy and profile/resource restrictions. Prove the accepted conversion and
   its duplicate-key/numeric/byte preservation; do not silently narrow the syntax
   meaning or infer a new profile-owner assessment.
5. Bind actual source/capture bytes to that AST, then realize pinned digest,
   authentic profile/root/review and Schema providers. Obtain the expected digest
   profile from authentic snapshot context. Feed authenticated retained catalogs
   into the K02 qualifier/source/metadata/Selection pipeline and realize all nineteen
   whole source policies.
6. Complete all original inherited qualifier/effect/theory and independent-checking
   obligations; run all seven extension integration and diagnostics/resource work,
   exact 263-plus-90 audit and actual new final use assessment in dependency order.

The full plan is unchanged. K04's actual meaning review and D01-D08 global reviews
remain pending. No prototype Unicode behavior, UTF-8 theorem or grammar constructor
is an inherited semantic discharge, N01 acceptance or N03 admitted API/schema freeze.
