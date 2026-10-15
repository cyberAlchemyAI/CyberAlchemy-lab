# Draft API reference preparation

This component prepares the exact contract-reference slice of T21 before the final runtime freeze. It follows proposal 0009 and the repository's maintained documentation convention. The generated [operation reference](reference-0002/README.md) contains all34 declared operations and points to selected candidate implementation files, original schemas and current versioned resource remapping.

Input selection binds182 public contract/schema/code files against the independently selected API17 capture e41772 and profile5c62fe. Generation imports no Lab code, starts no runtime and reads no private operator state. It preserves the historical catalog's authoring standing while clearly distinguishing current implementation and pending final qualification.

Two generation runs produce byte-identical35 Markdown pages. Validation checks311 local links and exact descriptions, deadlines, idempotency, completion conditions, preconditions, postconditions and allowed errors. The first run emitted a harmless Python regex escape warning; the generator's literal was corrected before its frozen closure and the second run completed with warnings treated as errors. No contract or runtime bytes changed.

This is a draft source component. T21 still requires independently reviewed final inputs, maintained website/editorial/navigation/search integration, HTML/Markdown parity, verified copyable startup and recovery procedures in a fresh owned installation, operator/developer explanation and the remaining proposed runtime pages. The original T15/T06/T07 dependencies remain in force. This component does not establish all34 runtime qualification, final privacy, human usefulness, admission or publication.
