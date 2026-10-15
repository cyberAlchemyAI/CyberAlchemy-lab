[Documentation home](../../README.md)

<a id="runtime-paperclip"></a>

Lab runtime · proposed documentation

# Use Paperclip as a bounded Lab reader

Configure the pinned process adapter without confusing orchestration with Lab authority.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-paperclip-what-has-actually-been-observed"></a>

<a id="runtime-paperclip-what-has-actually-been-observed-title"></a>

## What has actually been observed

The pinned published Paperclip version is 2026.1005.0. A local process-reader episode was observed on 13 October 2026 through the independently selected wrapper/runner configuration. Its [public closure](../../assets/e116c0c1e80f-closure.json) records process success, zero Lab mutations and zero Lab Sessions. It read a historical genuine-W09 engineering source.

The earlier [runner README](../../assets/c3d6821bfb42-README.md) says Paperclip was not installed when that package was authored. The later receipt records setup; neither statement establishes current server health. The recorded local endpoint was 127.0.0.1:3100, the old reader grant expired, and the human pilot/usefulness outcome remains unobserved.

<a id="runtime-paperclip-keep-the-two-authority-boundaries"></a>

<a id="runtime-paperclip-keep-the-two-authority-boundaries-title"></a>

## Keep the two authority boundaries

Paperclip company/agent/task IDs and its API token provide orchestration and correlation. Lab access comes from an independently provisioned current Lab policy, reader key, source/profile/plan pins and signed nonce proof. Do not put real private credentials or policy bodies into Paperclip task text, repository files or stdout.

The recorded agent could not create agents/skills or assign tasks, and used manual/on-demand scheduling. A process-adapter success is not a Work completion, an engineering tool effect, a research conclusion or repository admission. A future autonomous Work integration needs its actual workflow/tool/output/authority evidence.

<a id="runtime-paperclip-configure-only-the-inspected-adapter-contract"></a>

<a id="runtime-paperclip-configure-only-the-inspected-adapter-contract-title"></a>

## Configure only the inspected adapter contract

The [published adapter probe](../../assets/2dd8089d5421-Paperclip-process-adapter-probe-0140.json) selects an executable command with separate args, cwd and timeout, using direct process spawning. Do not paste a newer upstream shell-command example into this pinned version. A version upgrade needs its own compatibility review.

| Selected runner argument | Requirement |
| --- | --- |
| --api-root | Exact qualified API directory, not the currently changed/ineligible API17 |
| --source-sha256 / --profile-sha256 | Independently verified selected source and protocol profile |
| --policy / --policy-sha256 | Fresh isolated reader policy and exact digest |
| --reader-key / --reader-key-sha256 | Matching protected credential selected outside task text |
| --plan / --plan-sha256 | Exact bounded read plan |
| --timeout-seconds | Whole-episode bound, at most 900 seconds |

These are real runner flags, not a fabricated working configuration. The historic plan was limited to Lab status/catalog reads; the runner code supports additional bounded artifact reads only when its selected plan/policy permits them.

<a id="runtime-paperclip-follow-a-fresh-operator-setup"></a>

<a id="runtime-paperclip-follow-a-fresh-operator-setup-title"></a>

## Follow a fresh operator setup

First choose a qualified Lab reader and obtain a fresh scope/key/nonce channel. Run its exact approved command directly; preserve public observations and cleanup. Then configure Paperclip's process agent to run that same executable/argument selection from the selected repository cwd and compare results. Start a local server only under the accepted installation/service scope.

The current preparation provides no new credential, runnable server config or qualified integrated API. Old public config hashes and receipts cannot regenerate an expired grant. Keep persistent server/company state separate from temporary Lab credential roots; health, setup and Lab authentication need separate current checks.

<a id="runtime-paperclip-assess-usefulness-with-the-pilot-owner"></a>

<a id="runtime-paperclip-assess-usefulness-with-the-pilot-owner-title"></a>

## Assess usefulness with the pilot owner

The owner's question is how to use Paperclip to run the Lab; the agreed research question asks which evidence verifies that ability and what remains unproven. After a fresh technical setup, show the actual read output and ask the owner whether it answered those questions. Record time/failures and their own assessment without claiming improvement against an unattempted baseline.

Do not convert read-only process execution into autonomous engineering/research success. [Work and evidence](../explanation/work-evidence-learning.md) explains the missing output/assessment boundaries; [status](../status.md) retains the dated pilot limits.

<a id="runtime-paperclip-sources"></a>

## Selected public evidence

- [docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/Paperclip-process-adapter-probe-0140.json](../../assets/2dd8089d5421-Paperclip-process-adapter-probe-0140.json). SHA-256 2dd8089d5421613b24aa5ad6394f3bc267799fa59f655ed87d15fe5022f28bad; 2040 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/paperclip-runner-v3/README.md](../../assets/c3d6821bfb42-README.md). SHA-256 c3d6821bfb42142c3d8cd9b53233c16092c9c0e79cada0387b68257fe3d25c18; 3602 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/paperclip-local-pilot-0270/closure.json](../../assets/e116c0c1e80f-closure.json). SHA-256 e116c0c1e80f1837fc76740b532ff5851ab2137692970e2388d211be5a0fc671; 4458 bytes. Public technical snapshot; no authority transfer.
