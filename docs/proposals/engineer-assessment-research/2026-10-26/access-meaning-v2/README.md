# Engineer Assessment access meanings and policy model

Status: **candidate exact source cut, 2026-10-26**. Editable sources remain in the separate [Engineer Assessment workspace](../../../../../../engineer-assessment/README.md). This snapshot copies eight source files: local definitions, ontology, software definition coverage, question lifecycle, access model, data model, API contract and experiment operations. The Lab's original registry and exact accepted definition files are captured separately by Define v2. This snapshot is not a new canonical registry version.

The 76 candidate local meanings are split into four [Define v2 requests](define-v2/request-01.json), [part 2](define-v2/request-02.json), [part 3](define-v2/request-03.json) and [part 4](define-v2/request-04.json), with 24, 24, 24 and 4 closed `propose` dispositions. A fifth [request](define-v2/request-lab-access.json) selects exact current Lab meanings for Actor, Principal, Role, Role Assignment, Authority and Policy. All five `capture-snapshot`, `prepare`, `inspect-package` and `reconstruct-local` operations succeeded. `inspect-package` verified 14 members in each local Pack and 13 in the Lab-meaning Pack.

| Pack | SHA-256 |
| --- | --- |
| [local 01](define-v2/package-01/manifest.json) | `180c32ca19846e6d45f163357cbb7363f11d8ed006bfb5db5189ef82ba8ed934` |
| [local 02](define-v2/package-02/manifest.json) | `f06fb93db35b11d05c26878f28f491e1421d6d21587db8bdbd45d2d13478c6e1` |
| [local 03](define-v2/package-03/manifest.json) | `9a08b1a17e489f86fdef1b57c15bc7037c31e88684d63cbc4d67981b993e6158` |
| [local 04](define-v2/package-04/manifest.json) | `c15e91849039929a6de0f429b1108534d5648be46ad6c7ec93ec1413c3f8c591` |
| [Lab access meanings](define-v2/package-lab-access/manifest.json) | `5e9727de781905fb6c27286935992000c606b0225603901ea8a0fb2e249bc8a4` |

All five preparation results are `prepared-with-gaps`: exact inspection is ready; `prepare-owner-review` is blocked by historical capture/current-host obligations, and governing application is blocked by the actual route. `inspect-package` reports `current_use_readiness=not-established`. No concrete product user becomes a Lab Actor merely because the Lab Actor meaning was selected. No named principal, role assignment, active application policy, grant, collection approval, Lab definition admission or employment-use decision exists here.

The [actor, role and permission source](software/ACCESS-MODEL.md) proposes 36 guarded application actions and separation-of-duties rules. A permission entry is an application enforcement candidate, not Lab Authority. The previous [question-meaning cut](../software-meaning-v2/README.md) and [intermediate access cut](../access-meaning-v1/README.md) remain exact historical source cuts, not the selected current candidate model.
