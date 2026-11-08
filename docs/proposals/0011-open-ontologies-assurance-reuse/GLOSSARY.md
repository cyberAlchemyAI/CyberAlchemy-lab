# Words used in the design

| Term | Meaning here |
| --- | --- |
| Definition | The Lab's governed source meaning, not just a formula emitted by a tool. |
| Interpretation | A selected formal reading of a source, with explicit scope, assumptions and omitted meanings. |
| Obligation | The exact statement that must be established, independently selected before accepting result files. |
| Model witness | A concrete structure showing that selected formulas can hold together. |
| Countermodel | A model of the selected premises in which a named claim fails. |
| Backend check | The imported executable evaluated particular evidence; its result is scoped to its input format and trust boundary. |
| Kernel replay | Fresh Lean validation of actual proof terms/declarations, with exact statements, imports and axioms inspected. |
| Semantic bridge | A theorem connecting the selected Lab formal meaning to the backend meaning, not merely matching hashes. |
| Source fidelity | Whether the selected formal reading preserves the intended source definition; a separate review question. |
| Ontology cut | A view calculated at a particular meaning-history position. Review references/view digest also matter for a fully fixed input. |
| Profile | A versioned supported language, operation, runtime and evidence contract. |
| Unchanged copy | Source bytes and relative layout match the pinned upstream; patches and new adapters are tracked separately. |

This glossary explains existing terms for this candidate design. It creates no
new canonical definition or admission. It preserves the existing distinction
between model evidence, universal proof, source fidelity, currentness and
authority. No same-label term is used to merge their identities.
