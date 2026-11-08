# Individual candidate Definition records

The [index](index.json) contains **85 project-scoped, candidate-unadmitted Definition/v1 records**, one for every task-local meaning in [definitions.json](../definitions.json). Each directory contains a machine [definition.json](role-profile/definition.json) and a generated human [DEFINITION.md](role-profile/DEFINITION.md). All records share the selected Lab `cal.artifact-type.definition/v1` carrier. They are distinct from the Product, Experiment Design and other domain records whose meanings they may describe.

The source catalog in `model/definitions.json` remains the **task-local normative source** until an exact owner decision selects a successor. Within each candidate carrier package, `definition.json` is its machine record and `DEFINITION.md` its generated view; source parity keeps its normative statement aligned with the catalog. `tools/build_definition_records.py` copies its statements, scope, boundaries, formal notation and intuition into carrier-shaped review records. The record source refs pin the catalog's bytes and the exact JSON pointer for each term. [Validation](../../tools/validate_definition_records.py) checks source equality, index closure, selected Lab schema and deterministic Markdown projection. Shape and projection checks do not decide semantic quality or grant admission.

## Review split

| Route | Count | Why |
| --- | ---: | --- |
| `lab-reuse-semantic-review` | 36 | Role/outcome, constructs, case/response/score, measurement, study, claims and participant-facing metric meanings cross the product, research and decision boundaries. Review these first for reuse and carrier fit. This route does **not** request or imply Lab-wide admission. |
| `project-local-semantic-review` | 49 | Case generation, application workflow, custody, access and operational records primarily name this product's internal mechanics. Keep them project-scoped unless another Lab consumer and owner justify a broader meaning. |

The [four-part Define preparation](../../integration/lab/DEFINITION-RECORDS-RESULT.md) freezes the earlier 78-definition source cut for inspection. The recovery and integration additions are in a fresh Lab review cut. All 85 need a named semantic owner and term-by-term review before any canonical promotion. The selected Definition/v1 carrier is admitted-current; Definition/v2 is still a candidate successor. A proposed instance using v1 is not admitted just because it conforms to v1.

## Open review work

- Confirm each scientific statement, plain-language explanation, scope, exclusions and boundaries. The generated context voice is intentionally project-scoped; it is an explanation, not a second source of meaning.
- Add term-specific examples and testable conditions where they are needed. The generator leaves these empty rather than inventing domain evidence or formal tests.
- Resolve owner principals, source admission, consumer applicability and exact registry/index postimage before any Lab admission. Source refs currently point to a candidate project file, not an admitted Lab source.
- Review overlap with existing Lab definitions and revise or reuse rather than creating duplicate canonical terms.
- Rebuild and validate after every edit to `model/definitions.json`; earlier Define Packs stay frozen to their historical source cuts.
