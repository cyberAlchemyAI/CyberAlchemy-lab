# Supported U0 cell and troubleshooting

This preview qualifies one source/profile combination: `alchlang.business-spec/v2-candidate` with `node-http-entry-u0-v4` and `--output code`. It is a bounded foundation for the later application-generation plan.

## Current capability

- One Entity with one exact UInt64 identity and one Boolean field.
- One executable Rule testing that Boolean field.
- One pure Operation with an explicit guard, whole-input result, rejection code and no effects.
- One explicit public entry; permission stays alongside the entry.
- Generated Interface/input/output Mappings, native callable, injected Node Request/Response handler, API contract and checked business/system/bridge views.
- Code generation with zero Definitions and zero FormalClaims. Optional claims are assurance data; code does not require a solver or proof result.
- Exact counted request bounds, duplicate-aware JSON, UInt64 validation and resource cleanup. The selected profile fixes 4096 request bytes, 1024 response bytes and a 2000 ms body-acquisition deadline.
- Fresh output publication with no replacement and original source/review/decision/native currentness checks.

The handler uses Node 26.8.1's built-in Request/Response and the actual packaged codec/value assets. Its body deadline bounds input acquisition. The pure operation runs synchronously; there is no transaction or remote-delivery guarantee in this cell.

## What remains authored

The user supplies business requirements and examples, domain fields, executable conditions, intended operation behavior, permission and failure meaning. They select the supported profile and record a decision for the displayed review/capture scope. Craft generates the supported semantic bindings, technical structure and linked outputs.

The tutorial consumer is a caller of generated code. It does not provide a business evaluator, guard implementation, mapping callback or authorization assertion to generation.

## Scope beyond this cell

Persistence, protected entries/RBAC, external API calls, durable workflows, event delivery and multi-service composition are follow-on implementation work in this plan. A declaration named Interface does not activate a connection to an external API. Those connections require a selected, implemented protocol/native realization and observed wiring.

The thirteen existing meta-types remain available at their separately qualified scopes. This single cell does not establish complete behavior for every meta-type, arbitrary profile extensions, gRPC, event transports or every platform. Source and example syntax from future design documents may still be candidate syntax.

Required `base-model` and `conjecture-problems` exports are unavailable in this selected cell. Optional requests retain explicit unsupported/null results. A code-generation success is not a theorem, solver result, EVF/TDE execution, ontology admission or product approval.

The generated handler is importable and runs through injected Request/Response values. Local hosting, TLS/listener setup, deployment, live identity/provider/database/broker activation, TDE, EVF and publication are deferred. The prepared public repository remains unpublished.

## Troubleshooting

| Observation | Meaning and next action |
|---|---|
| Missing `--profile` or `--output code` | Select the exact supported profile/mode explicitly. |
| Scope/digest mismatch when recording a decision | Use the current displayed `decision_scope_sha256`; review again after changing captured inputs. |
| Decision is declined, stale or for different source/capture | Record an appropriate new decision after inspecting the current review. |
| Destination already exists | Choose a fresh directory; even an empty existing target is preserved. |
| `400 invalid-request` | Check canonical decimal-string UInt64, Boolean type, exact members, duplicate decoded names and valid UTF-8/JSON. |
| `413 request-too-large` | The counted or advertised request exceeds the selected 4096-byte bound. |
| `408 body-timeout` | Body acquisition exceeded the selected deadline. |
| `404` / `405` / `415` | Use `/confirm-delivery`, POST, and `application/json` or the supported UTF-8 charset form. |
| `422 delivery-verification-required` | The authored guard evaluated to false. |
| Missing installed peer/resource/native export | Use the exact prepared Core/Alch/dependency archives; a development checkout does not substitute for a missing installed peer. |
| Unsupported required formal output | Generate code with optional/unrequested formal outputs, or select a separately qualified exporter when one exists. |
| Several minutes spent generating this small example | This is a measured current limitation. Wait for the actual command; no fast-generation claim is qualified. |

After a failed write, keep its private stage as diagnostic evidence and use fresh paths for a new attempt. A failure before finalization cannot be called a complete generated bundle. Local response settlement does not establish delivery to a network peer or rollback of a remote effect.

## Open Questions

The integrated plan retains U0 as its first milestone. It then closes the ecommerce source contracts, calculations, service-owned persistence, protected APIs, inventory/payment/workflow/event joins, complete service composition and fixed installed qualification. Exact additional grammar, profile families and native implementations close in their assigned tasks. Formal claims remain optional; local hosting, TDE, EVF and publication remain deferred.

This guide and its examples are prepared documentation. Their actual command replay, package identity and product-test evidence are maintained in the owning construction records; publication requires a separate decision.
