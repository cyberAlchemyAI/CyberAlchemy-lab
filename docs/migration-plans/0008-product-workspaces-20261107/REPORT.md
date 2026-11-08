# Product workspace migration

Status: applied and verified, 7 November 2026. Filesystem organization only; existing native admission and candidate standing are unchanged.

## Current homes

| Product | Canonical home |
| --- | --- |
| CyberAlchemy Lab | Repository root |
| Craft | workspaces/products/craft/ |
| Define | workspaces/products/define/ |
| Ontology, including Lifecycle | workspaces/products/ontology/ |
| People and Teams | workspaces/products/people-and-teams/ |
| Lab website | workspaces/products/lab-website/ |
| Trusted Dataset Materialization | workspaces/products/trusted-dataset-materialization/ |
| Agent Reasoning Engine | Existing upstream implementation, referenced without a local copy |

Each physical Product workspace has product/, project/, work/, authority/, ontology/, architecture/, implementation/ and docs/. Product, Project and Work identities remain distinct records within one Product home. There are no standalone Project workspaces currently selected.

Craft source, its older Product representation and its coordination history now share Craft's home. Define source is under implementation/source/, and its development/proposals are under work/. Ontology's Product package and Lifecycle engine are separate implementation packages inside one home. Website source is under implementation/site/. Definition Formal Assurance records now live in root project/definition-formal-assurance/, with related plans under root work/plans/.

People and Teams and Trusted Dataset reference their exact imported source artifacts. Their import archives and previous receipts remain historical evidence; no executable runtime was unpacked to populate these homes. Frozen ontology integration plans and native Project carriers retain their exact evidence locations and are referenced rather than copied.

## Shared operations and compatibility

Shared operations remain in root implementation/, including Lab runtime/context/work/workflows/review/continuity/ontology/integration/provisioning and Define connectors. Product-owned code remains in its Product home.

No shared runtime or dependency installation was copied. The existing website Python environment was renamed into .local/shared-environments/lab-website/venv on the same filesystem. Shared Node and seven shared Lab directories retain their original inodes. Product dependencies remain links to the existing selected installations.

Fourteen directory moves used same-device os.rename. Old source locations are relative compatibility symlinks to the moved directories, not additional Product homes. This preserves existing source references, native source pins and retained evidence. Fifty dependency links were retargeted without copying their targets.

TROQAR/Body War, Engineer Assessment and Agentic Research Network remain external. Definition NFT and Lab migration remain removed from active planning; exact historical admission/evidence records remain retained.

## Verification

- All 33,827 inventoried existing files retain their original inode and original content, except the explicitly journaled path/configuration/provenance edits. No missing files or unexpected content changes.
- All 21,026 tracked paths already deleted before this task remain absent. Pre-existing user changes were not reset, restored or staged.
- Both Lab runtime verifiers pass with byte-identical baseline output and the same source snapshot digests: v1 3b7c0aa920c195d82b5c1dcc3652b28cd67554b5289f40cf546aa85a7ce3648e; v2 655e1309e167e0735730e7320cd0ff10463982bc420672d9b7527e3e322d3fe3.
- Craft builds using existing shared tools. Three application relocation tests and seven Ontology reader/integrity tests pass.
- Website: six tests pass.
- Ontology Product package: eight tests pass. Lifecycle: twenty-three tests pass.
- Define standalone doctor passes with the same baseline output. Current Lab connector doctor verifies all 56 selected files, through canonical and compatibility entry points.
- Workspace catalog validation passes: eight Product scope entries, six nested physical Product homes, no standalone Projects, three external scopes, 110 exact source pins.

The older default Define v1 doctor was already failing before migration because legacy craft/impl/cli/dist artifacts were absent. It still exits 3 with a byte-identical baseline diagnostic; both captures are retained. The current define-lab and standalone routes pass. Missing legacy artifacts were not restored.

Relocation changed selected launchers, TypeScript ancestry and the Craft reader/test fixture paths. Their narrowly selected integrity/provenance hashes were updated only after matching the original hashes to saved preimages. Every old/new hash and the reason is in JOURNAL.json. No bulk semantic repinning, frozen Define Pack mutation, native identity creation, native typed-profile adoption, transaction replay or runtime deployment was performed. The older Project-only native workspace profile still requires its separate successor; these component checks do not establish full platform qualification.

## Evidence and review

- [Prepared file inventory and move plan](PLAN.json)
- [Applied moves and exact edit preimages](JOURNAL.json)
- [Final preservation/check receipt](VERIFICATION.json)
- [Repeatable read-only verifier](verify.py)
- [Baseline and current command captures](checks/)
- [Current folder structure](../../../architecture/workspace-model-mapping/FOLDER-STRUCTURE.md)
- [Current workspace map](../../../architecture/workspace-model-mapping/WORKSPACES.md)

No Git staging, commit, external repository writes or publication was performed.

To recheck from the Lab root: python3 -B docs/migration-plans/0008-product-workspaces-20261107/verify.py
