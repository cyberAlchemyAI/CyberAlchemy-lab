# W02 bounded authority and Tool context

Candidate execution evidence; 24 exact sources, all seven task obligations covered. W01/C13 are complete and current. Native domain mapping and general APIs remain separate.

## Decisions

- Use a narrow in-process trusted host adapter and an owned isolated local counter Tool; no generic shell or network adapter.
- The host receives explicit local development permission separately from schema-valid/admitted records. Public request fields cannot construct host authentication or grant objects. Positive authorization cases use labeled isolated candidate selections; old admitted assignment is a negative real-source case.
- Treat free-form assignment/delegation periods as exact keys in an independently supplied host period registry. Unknown keys deny; do not infer current authority from arbitrary text.
- Use a separate original-byte local-action fingerprint and durable file ledger for the narrow W02 interface. The proposed general API JCS codec and all 34 handlers remain R03 obligations.
- Persist pending before effect and block all later effects while pending. Recovery observes the Tool state under exclusive lock, never reruns the action to discover an outcome.

## Obligations

- resolve exact current Principal, role, delegation, assignment, ephemeral instance/session and Tool from trusted host inputs
- recheck scope/action/period/revocation/redelegation/gates immediately before effect
- deny unknown, malformed, expired, revoked or stale authority and client-supplied permission
- execute a closed local adapter with original-byte input/output contracts and strict budgets
- retain durable pending/indeterminate operational metadata and reconcile before any new non-idempotent dispatch
- bind Agent Action and receipt to actual inputs, outputs and residue; expire Session memory
- validate allowed and all denied cases, process restart and actual current Agent context; preserve frozen predecessors

## Boundaries

W02 isolated bounded authority/Tool candidate only. No canonical admission, live store/service effects, production authentication, full API or power-loss durability.

- `docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/W02.md` — ordered rules and SWUs
- `docs/plans/0010-lab-one-shot-execution/work-pack/tasks/W02.md` — candidate acceptance and scope
- `docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json` — isolated candidate implementation and verification
- `implementation/lab-workflows/candidates/v1/receipts/W01-0001.json` — exact workflow transition predecessor
- `implementation/lab-workflows/candidates/v1/design/transition-contracts.json` — actor and action transition obligations
- `implementation/lab-continuity/candidates/v1/receipts/C13/0002.json` — complete current continuity predecessor
- `implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json` — fresh committed-source Agent context
- `authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/MODEL.md` — ephemeral Agent and attributable Action boundaries
- `docs/proposals/0008-lab-api-contracts/POLICIES.md` — current authority and durable uncertainty; local interface is not full API
- `docs/proposals/0008-lab-api-contracts/operations/action.dispatch.json` — recheck before actual bounded effect
- `docs/proposals/0008-lab-api-contracts/operations/action.reconcile.json` — observe uncertainty without replay
- `authority/artifact-types/principal/v1/schema.json` — exact principal carrier; structural validity grants no permission
- `authority/artifact-types/role/v1/schema.json` — exact role carrier; structural validity grants no permission
- `authority/artifact-types/role-assignment/v1/schema.json` — exact role-assignment carrier; structural validity grants no permission
- `authority/artifact-types/delegation/v1/schema.json` — exact delegation carrier; structural validity grants no permission
- `authority/artifact-types/agent-assignment/v1/schema.json` — exact agent-assignment carrier; structural validity grants no permission
- `authority/artifact-types/agent-instance/v1/schema.json` — exact agent-instance carrier; structural validity grants no permission
- `authority/artifact-types/agent-session/v1/schema.json` — exact agent-session carrier; structural validity grants no permission
- `authority/artifact-types/agent-profile/v1/schema.json` — exact agent-profile carrier; structural validity grants no permission
- `authority/artifact-types/tool/v1/schema.json` — exact tool carrier; structural validity grants no permission
- `authority/artifact-types/agent-action/v1/schema.json` — exact agent-action carrier; structural validity grants no permission
- `docs/proposals/0007-lab-integrated-schema-package/schemas/action-receipt.schema.json` — completion, uncertainty and residue postures
- `implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/session.py` — live context expiry and memory erasure
- `authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/agent-assignment.json` — old exact assignment eligibility must reject a new ephemeral Agent
