[Documentation home](../../README.md)

<a id="runtime-provision"></a>

Lab runtime · proposed documentation

# Provision a branch and review its authority

Separate environment selection, store creation, key custody and approval.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-provision-choose-the-kind-of-provisioning"></a>

<a id="runtime-provision-choose-the-kind-of-provisioning-title"></a>

## Choose the kind of provisioning

Local v1 init creates a new operational branch. Candidate provisioning constructs a separately scoped branch from pinned runtime/configuration/baseline/HEAD. Composite operator preparation additionally selects three independent branch workspaces, policies and authentication proofs. These actions are not interchangeable.

Read [CandidateScope and CandidateBranch](../../assets/fdfe260336ac-provision.py) for controlled branch construction, [bootstrap composition](../../assets/22103d4007e1-bootstrap.py) for seed packaging, and [v1 admission](../../assets/79c23e82b5de-ADMISSION.md) for its local scope. A package, key, store and admitted implementation each answer a different question.

<a id="runtime-provision-check-the-environment-before-the-branch"></a>

<a id="runtime-provision-check-the-environment-before-the-branch-title"></a>

## Check the environment before the branch

Select the exact executable, parser, profile, dependency closure and supported filesystem assumptions. T07's [1010-file selected dependency declaration](../../assets/2345d4d3a59c-dependency-selection-0002.json) identifies installation0004; its existence is not a new-install witness or a blanket compatibility result for every package.

Confirm the source cut and current byte checks before selecting a new store. A historical profile may be useful for inspection while lacking current records. Installing Python/native dependencies does not initialize a branch, provision authority or activate a service. The [CLI/environment reference](../reference/cli-and-environment.md) keeps those interfaces separate.

<a id="runtime-provision-keep-credential-custody-explicit"></a>

<a id="runtime-provision-keep-credential-custody-explicit-title"></a>

## Keep credential custody explicit

A local approver key remains outside Git and outside public artifacts. A reader policy selects a bounded Principal, source, scope, operations, budgets, expiry and nonce channel. Private signing bytes, credential paths with real secrets and live private policy bodies do not belong in task text, replies, exports or tutorial logs.

For the composite candidate, Base, Action and Governance need independent current branch selectors and three proofs. The [operator contract](../../assets/c034636b312a-README.md) explicitly selects the outer policy custody root separately from Base's actual nested Vault and its original workspace/workspace.json. Copying an outer manifest cannot stand in for the real Vault.

<a id="runtime-provision-review-before-authorizing"></a>

<a id="runtime-provision-review-before-authorizing-title"></a>

## Review before authorizing

| Stage | What it establishes |
| --- | --- |
| Environment/source inspection | The selected inputs are available and match declared bytes |
| Branch initialization | A new scoped store/configuration exists |
| Candidate review | Consequences, contracts, source cut and unresolved obligations are visible |
| Exact signed authorization | This local approver approved these bytes within this boundary |
| Application and cold replay | The observed scoped effect and its committed chain |
| Repository admission or service activation | Separate governing and operational evidence |

Review failures stay attached to their exact input version. A technical provisioning receipt cannot become Action/Governance or genuine owner authority merely by being passed to another component.

<a id="runtime-provision-when-provisioning-refuses"></a>

<a id="runtime-provision-when-provisioning-refuses-title"></a>

## When provisioning refuses

An existing path, changed baseline/HEAD, unsafe root, missing public key, expired/revoked policy or unknown execution origin should refuse. Preserve the actual error and owned partial state. Choose a separately authorized new branch or correct a new candidate version; do not silently overwrite, restore old Session RAM or extend a historical period.

Fresh setup and full three-branch operation remain pending for the changed API17 composition. Follow [status](../status.md) and [recovery](recover-and-retry.md) before interpreting a refusal as a reason to rerun.

<a id="runtime-provision-sources"></a>

## Selected public evidence

- [implementation/lab-runtime/ADMISSION.md](../../assets/79c23e82b5de-ADMISSION.md). SHA-256 79c23e82b5dedb74b19580f845c333554e8cd5d73a5bd4e617d6879ebc341283; 1632 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-bootstrap/candidates/v1/bootstrap.py](../../assets/22103d4007e1-bootstrap.py). SHA-256 22103d4007e15c9156a4641f64b61404d680475ed8c99e60c4ab4474bb5d4b1b; 41190 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json](../../assets/2345d4d3a59c-dependency-selection-0002.json). SHA-256 2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835; 317618 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-provisioning/candidates/v1/provision.py](../../assets/fdfe260336ac-provision.py). SHA-256 fdfe260336ac5e2ed3063d3d57044a3ab841074ec5ab26f6966ff02c563cfa4b; 7886 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/README.md](../../assets/c034636b312a-README.md). SHA-256 c034636b312ac42c3ecd25b6c8e5ec0586cbf606459a9ab1cd37343a3b541a1e; 11032 bytes. Public technical snapshot; no authority transfer.
