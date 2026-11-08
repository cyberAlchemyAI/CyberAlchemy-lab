# Craft backend taxonomy and ontology

Generated with the built-in image_gen tool. Backend only.

## Initial prompt

Use case: infographic-diagram.
Create ONE polished, high-resolution SINGLE-PAGE LANDSCAPE educational reference poster, approximately 3840×2560, in English. Topic: Craft backend taxonomy, ontology, semantic contracts and profile implementations. This is a dense but beautifully readable professional architecture map, not a marketing illustration. Crisp typography, precise arrows, flat diagram shapes, generous internal padding, quiet off-white background, dark navy text. Category accents: structural teal; behavioral indigo; connective amber; lifecycle purple. No textures, no 3D, no fantasy imagery, no UI types, no invented types or relationships. Exact spelling matters. All text must be readable when zoomed. Keep every label within page, no cropping.

TITLE: "CRAFT • BACKEND TAXONOMY & ONTOLOGY"
Subtitle: "13 active semantic types · 17 backend relationship signatures · 3 language profiles · 39 admitted realizations"

Small foundation banner below title with three visibly linked boxes:
"Taxonomy" / "Which kinds of concept exist?"
→ "Ontology" / "Typed concepts + directed relationships + meaning"
→ "Realization profile" / "Exact implementation choices that preserve the contract"
Small explanatory caption: "Business meaning is authored. Profiles select technical form. The compiled graph connects them."

MAIN PAGE COMPOSITION: about 56% width on left for a 13-row taxonomy reference table, 44% on right for a carefully organized connected ontology map. Along bottom a substantial profile-implementation strip. Use large section titles and consistent colored category dots, never a giant hairball of crossing arrows.

LEFT heading "WHAT EACH TYPE CARRIES"
Table columns "TYPE" | "SEMANTIC CONTRACT" | "REALIZATION FAMILY"
Group the 13 rows into Structural (3), Behavioral (6), Connective (3), Lifecycle (1). Use exactly these contents, allow deliberate line breaks:

STRUCTURAL
"Entity" | "Stable identity; typed fields; lifecycle. Equality by identity." | "identity-lifecycle-v1"
"Value Object" | "Complete immutable value; no identity. Equality by fields." | "complete-value-v1"
"Enum" | "Closed, finite named variants; reject unknown values." | "finite-vocabulary"

BEHAVIORAL
"Operation" | "State change; declared reads/writes/effects; guard; failure continuation." | "state-changing-v1"
"Query" | "Typed read inputs and result; no state mutation." | "read-model-v1"
"Calculation" | "Pure derived value; inputs; formula; rounding and errors." | "value-computation-v1"
"Rule" | "Typed Boolean predicate; permits or blocks an Operation." | "pure-boolean-v1"
"Policy" | "Strategy choices; conditions; explicit default and ambiguity handling." | "strategy-selection-v1"
"Workflow" | "Ordered Operations; declared scope; explicit recovery semantics." | "ordered-v1"

CONNECTIVE
"Interface" | "Versioned callable boundary; request/response contract." | "versioned-boundary-v1"
"Event" | "Past-tense domain fact; typed payload; source context." | "past-tense-v1"
"Mapping" | "Source/target fields; direction; conversions; total or partial." | "directional-v1"

LIFECYCLE
"State Machine" | "States; initial state; transitions; guards and effects." | "lifecycle-v1"

Under table caption: "Family labels summarize the shared contract. Each backend type has TypeScript, Python and Rust realization bindings."
Tiny separate callout: "Saga is represented by Workflow; it is not a separate active type."

RIGHT heading "HOW THE ONTOLOGY CONNECTS"
Subcaption "Canonical arrow direction · repeated nodes keep the map readable"
Build an elegant set of FIVE small graph panels, with clear actual arrowheads and exact edge labels. Repeated type nodes are intentional. These graph panels together cover ALL 17 canonical backend signatures. Do not reverse an arrow. Where there are multiple target types, branch to the separate named targets; a vertical bar in the specifications below means alternatives, not a new type.

Panel A title "Execution spine":
Entity --performs→ Operation --produces→ Event --transitions→ State Machine.
Rule --enforces→ Operation.
Calculation --calculates→ Operation.
Workflow --orchestrates→ Operation.
Use Operation as central hub within this panel; generous spacing around the three inbound arrows.

Panel B title "Boundaries & decisions":
Interface --exposes→ Operation and Query.
Policy --applies→ Operation and Calculation.
Mapping --maps→ Entity and Value Object and Interface.
Use separate mini-lines with branching arrows instead of crisscrossing.

Panel C title "Data & identity":
Entity --contains→ Value Object.
Query and Operation --reads→ Entity.
Operation --creates→ Entity.
Entity --emits→ Event.
These are four directed mini-lines. In reads line show both source chips pointing through same reads label.

Panel D title "Across features":
Event --triggers-cross→ Operation.
Operation --produces-for→ Entity.
Make a fine dashed vertical feature boundary that arrows cross.

Panel E title "Ownership & membership":
Entity A --owns→ Entity B.
Entity A --belongs-to→ Entity B.
Small text: "owns = lifecycle/custody responsibility; belongs-to = membership or assignment."
"creates is one-to-one within a feature."
Tiny note under map: "Enum types fields and state values through typed references; it has no dedicated DS-D8 backend edge."
Any decorative field-reference line to Enum must be dotted and explicitly labeled "typed reference", never pretend it is one of the 17 verbs.
Another brief note: "Mapping projects shape; it does not construct, persist or invoke."

BOTTOM heading "HOW PROFILES BECOME IMPLEMENTATIONS"
A left-to-right horizontal pipeline with five boxes:
"Authored JSON / AlchLang" → "Checked typed graph" → "Select exact profile + bindings" → "Generate target artifacts" → "Verify artifacts + receipt"
Under pipeline three language mini-cards:
"TypeScript" / "Typed artifacts + exact bindings" / "Enum: owned-const-object-v1"
"Python" / "Typed artifacts + exact bindings" / "Enum: nominal-enum-v1"
"Rust" / "Typed artifacts + exact bindings" / "Enum: unit-variant-enum-v1"
Put a common short caption below them: "13 types × 3 languages = 39 selected realization rows. Each row binds exact source, provider and binding digests."
To the right of these language cards include a small practical profile box:
"Application architecture profiles"
"entry-local: transport owned per entry"
"shared-ports: reusable typed transport"
"api-prefix: route and output placement"
"Profiles supply technical wiring; business semantics stay authored."

BOTTOM FOOTER:
"Implementation baseline: @10 • Semantic maturity, implementation admission and target conformance are separate."
"Generated and statically verified artifacts do not establish provider runtime behavior or production readiness."
"Source: Craft authority definitions, DS-D8 relationships, realization bindings and profile-generation docs • backend only"

Important precision: Do not include frontend/UI candidates. Do not include Page/Layout/Component/Form/etc. Do not imply Enum is a State Machine. Do not show writes as a canonical ontology verb: writes is an Operation contract field. Preserve the exact direction Rule → Operation for enforces, Calculation → Operation for calculates, Event → State Machine for transitions. Do not invent unified all-purpose Port. This is a source-grounded explanatory map, not a runtime qualification claim.

## Cross-feature correction

Edit this infographic surgically. Preserve the full page, all text, every other panel, colors, dimensions, layout and crisp readability. Change ONLY panel D, "Across features", in the right-hand relationship map. It currently has an ambiguous single row. Replace its inner diagram with TWO neatly spaced horizontal rows separated by whitespace. Keep title "D Across features". Place column label "Feature A" at left and "Feature B" at right, with a dashed vertical line between them. ROW 1: one amber Event node entirely to the LEFT of the boundary, arrow labeled "triggers-cross" crossing the boundary left-to-right, pointing to one indigo Operation node entirely to the RIGHT. ROW 2: one indigo Operation node entirely to the LEFT of boundary, arrow labeled "produces-for" crossing boundary left-to-right, pointing to one teal Entity node entirely to the RIGHT. There are exactly four nodes in this panel: Event, Operation, Operation, Entity. Do not connect the two rows. Preserve ALL other image content exactly. No new text outside panel D.

## Caption cleanup

Preserve this entire infographic exactly, including the corrected cross-feature arrows in panel D. Repair ONLY the narrow caption band at the bottom of the right-hand ontology-map container, immediately below panels D and E and above the heading HOW PROFILES BECOME IMPLEMENTATIONS. The Enum note there has duplicated overlapping text. Cleanly typeset that whole narrow caption band on an off-white background. Use only two compact text blocks separated by a thin vertical divider: LEFT block (about 65% of band): 'Enum uses typed field/state references; it has no dedicated DS-D8 backend edge.' RIGHT block (about 35% of band): 'Mapping projects shape; it does not construct, persist or invoke.' Remove the tiny dotted Enum graphic from this caption band to make room. Ensure no text overlaps and every word is readable. Do not change anything outside this narrow caption band. Do not alter any type row, edge, profile, footer, title, or other text.

## Source files consulted

- craft/authority/definitions/meta-types/meta-types.md
- craft/authority/definitions/meta-types/current-implementation.md
- craft/authority/definitions/relationships/relationships.yml (17 backend signatures)
- craft/implementation/spec/TAXONOMY.md
- craft/implementation/architecture-conformance/realizations/
- craft/implementation/cli/COMPILATION-ONTOLOGY.md
- craft/implementation/cli/docs/PROFILE-GENERATION.md
- craft/implementation/cli/docs/PROFILE-PACKAGES.md

This is an explanatory visual sourced from the current repository, not an execution or qualification report.
