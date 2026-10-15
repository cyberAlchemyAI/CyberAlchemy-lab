# R06: exact current privacy boundary evidence

Status: **partial candidate proof; R06 remains in progress.** No publication, canonical admission or owner outcome.

## Actual results

The successor inspection passed all **17 checks**, with separately observed exit-zero terminals for both the checks and actual package inspection. Its 1,139-file proof retains the failed predecessor unchanged.

- **87** original code/control members in the selected R02 payload.
- **10** exact package files, including all **eight** selected dependency wheels.
- One exact signed source archive, retained as private provenance and excluded from public payloads. The recorded file mode is **0600**, owned by the current user, with no group/other read permission.
- **140** nonexportable migration items: **138 private** and **two public-scoped references**. Original classifications and dispositions remain separate.
- Two structural occurrences of historical Session memory fields were found inside the private archive. No private values were copied into the findings.

## Example

The distributable code snapshot contains exact implementation bytes and schemas. The signed source snapshot also contains historical artifact bodies, including a Session record. It can support protected replay provenance while its entire body remains excluded from public code packages. A public-scoped source reference can be visible metadata and still prohibit body export under the selected import contract.

The inspector decodes the closed embedded byte formats and verifies their hashes. A nested Session-memory field is detected even when its containing JSON is base64 encoded. A schema property declaration is retained as a declaration.

## Retained failure

The first inspector incorrectly treated every nonexportable migration item as private. Its actual inspection exited one, while its 16 mechanical checks passed. Successor2 preserves the source classification rather than rewriting those two public-scoped references. An added test verifies the actual 138/2 split.

## Remaining original obligations

R06 cannot close on the foundation package. Every final integrated API, workflow, ontology, schema, review and evidence byte still needs a disposition and exact release binding. The current release selection is explicitly partial and permits no final public release. R07/S02 must select its complete successor; R08 remains the sole final owner checkpoint.

The fresh currentness verifier passed **36/46 closed criteria, 38 active receipts, 77 preserved preparation files and 887 original sources**, with no changes. This does not qualify the unfinished Agent/API integration or establish a human pilot.

## Evidence

- [Complete partial proof](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/boundary-review/0002/receipts/proof-0001.json)
- [Exact inventory](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/boundary-review/0002/inventory.json)
- [Partial release selection](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/release-selection.json)
- [Actual source custody](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/boundary-review/0002/custody-observation.json)
- [Preserved failed predecessor](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/R06-boundary-failed-proof-0001.json)
