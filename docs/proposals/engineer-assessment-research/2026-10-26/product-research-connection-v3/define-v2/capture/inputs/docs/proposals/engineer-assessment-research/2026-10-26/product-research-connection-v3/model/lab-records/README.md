# Candidate Lab records and relation proposals

These are source-controlled **candidate-unadmitted** authoring records. They have no Lab graph standing, owner acceptance, participant collection, observed result or hiring-use effect. [Structural validation](../../tools/validate_lab_carriers.py) checks 34 records against the selected Lab carrier schemas. [Relation validation](../../tools/validate_relation_proposals.py) checks ordered pairs and qualifier contracts; it does not apply a typed relation.

| Family | Candidate records | What remains open |
| --- | --- | --- |
| Project and six Goals | [project](project-identity.json), `goal-01` through `goal-06` | Owner principals, source and admission review |
| Product Thesis and seven Capabilities | [thesis](product-thesis.json), `capability-01` through `capability-07` | Outcome thresholds, owner acceptance, implementation and value evidence |
| Eight Research Inquiries | [central RQ03](research-inquiry.json), `research-inquiry-rq01/02/04/05/06/07/08` | Named role, sources, methods and preregistration |
| Ten Experiment Designs | [E06](experiment-design.json), `experiment-design-e01/02/03/04/05a/05b/05c/07/08` | Protocol inputs, data-purpose approval, recruitment and runs |
| [114 relation proposals](relation-proposals.json) | Exact existing Lab relation kinds, ordered endpoint types and qualifier proposals | Exact endpoint carrier/source review and typed-relation application |

The six untested propositions are in the [Product Thesis](product-thesis.json). The selected Lab Hypothesis v1 schema requires an existing incoming `evidence-bears-on` counterpart in `relation_refs`; no evidence exists. Consequently no standalone Hypothesis carrier is fabricated. A future compatible owner/source route must resolve preregistration of propositions before E05/E06 `tests-hypothesis` instances can be applied.

No Experiment Run, Research Run, Evidence Set, Measurement Result, Finding, Decision or Implementation record exists. The [connection result](../../integration/lab/PRODUCT-RESEARCH-CONNECTION-RESULT.md) records the exact Define preparation and unresolved gates.
