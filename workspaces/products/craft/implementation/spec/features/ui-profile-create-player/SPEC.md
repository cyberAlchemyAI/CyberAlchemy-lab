# Create Player UI Profile — synchronized validator view

> Synthetic mechanical calibration only. Canonical feature semantics live in
> `feature.json`, `nodes/*.json`, `representations/*.json`, `traceability.json`,
> and `residue.json`. This Markdown file is the current human/legacy-validator
> projection; it does not activate UI candidates or change DS-D8.

## What This Feature Owns

A machine-first Create Player specimen that connects backend and UI concepts
through active DomainSpec relationships while preserving Adapter and State
Indicator normalization residue.

## Concept Registry

| Concept | Type |
| --- | --- |
| Player | Entity |
| CreatePlayer | Operation |
| PlayerCreated | Event |
| CanCreatePlayer | Rule |
| PlayerApi | Interface |
| GetPlayerDefaults | Query |
| PlayerLifecycle | State Machine |
| DashboardLayout | Layout |
| CreatePlayerPage | Page |
| CreatePlayerPanel | Component |
| CreatePlayerViewModel | View Model |
| CreatePlayerHook | Hook |
| CreatePlayerForm | Form |
| CreatePlayerAction | Action |
| CreatePlayerGuard | Guard |
| CreatePlayerBinding | Binding |
| CreatePlayerAdapter | Mapping |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| Player | performs | CreatePlayer |
| CreatePlayer | produces | PlayerCreated |
| CreatePlayer | creates | Player |
| PlayerCreated | transitions | PlayerLifecycle |
| CanCreatePlayer | enforces | CreatePlayer |
| PlayerApi | exposes | CreatePlayer |
| PlayerApi | exposes | GetPlayerDefaults |
| GetPlayerDefaults | reads | Player |
| DashboardLayout | wraps | CreatePlayerPage |
| CreatePlayerPage | renders | CreatePlayerPanel |
| CreatePlayerPanel | consumes | CreatePlayerHook |
| CreatePlayerPanel | displays | CreatePlayerViewModel |
| CreatePlayerViewModel | derives | Player |
| CreatePlayerForm | submits | CreatePlayerAction |
| CreatePlayerForm | contracts | PlayerApi |
| CreatePlayerGuard | protects | CreatePlayerPage |
| CreatePlayerGuard | mirrors | CanCreatePlayer |
| CreatePlayerBinding | fetches | GetPlayerDefaults |
| CreatePlayerBinding | mutates | CreatePlayer |
| CreatePlayerAdapter | maps | PlayerApi |

## Player

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| player_id | string | yes | yes | stable player identity |
| name | string | yes |  | display name |
| email | string | yes |  | contact address |

## CreatePlayer

| Attribute | Value |
| --- | --- |
| state_change | yes |

## PlayerCreated

| Attribute | Value |
| --- | --- |
| temporal | past |

## CanCreatePlayer

| Attribute | Value |
| --- | --- |
| formal_return_type | boolean |

## PlayerApi

| Attribute | Value |
| --- | --- |
| interface_kind | internal |

## GetPlayerDefaults

| Attribute | Value |
| --- | --- |
| state_change | no |

## PlayerLifecycle

| Attribute | Value |
| --- | --- |
| has_transitions | yes |

## DashboardLayout

| Attribute | Value |
| --- | --- |
| slots | global-nav,page-content |
| shared_chrome | header |
| page_specific_content | false |
| wrap_target | Page |

## CreatePlayerPage

| Attribute | Value |
| --- | --- |
| route_path | /players/new |
| terminal | true |
| access_context | authenticated |
| primary_content | create-player |
| layout_ref | DashboardLayout |
| unit_inventory | CreatePlayerPanel |

## CreatePlayerPanel

| Attribute | Value |
| --- | --- |
| typed_inputs | PlayerDraft |
| typed_outputs | PlayerId |
| independent_route | false |
| domain_data_authority | false |
| validation_authority | false |
| access_authority | false |

The machine node also carries the `async-request-indicator` profile role with
idle, submitting, success, and error states.

## CreatePlayerViewModel

| Attribute | Value |
| --- | --- |
| typed_fields | display_name:string,active_label:string |
| source_refs | Player.name,Player.active |
| display_context | create-player |
| display_roles | formatted,computed |
| domain_authority | false |

## CreatePlayerHook

| Attribute | Value |
| --- | --- |
| typed_inputs | PlayerDraft |
| typed_returns | PlayerResource |
| reactive_behavior | mutation-state |
| lifecycle | consumer-scope |
| effects | create-player,cancel-request |

## CreatePlayerForm

| Attribute | Value |
| --- | --- |
| typed_fields | name:string,email:email |
| validation_contract | player-input |
| error_contract | field-errors |
| submission_action | CreatePlayerAction |
| target_interface | PlayerApi |
| error_mapping | api-to-fields |

## CreatePlayerAction

| Attribute | Value |
| --- | --- |
| intent | create-player |
| trigger | form-submit |
| target_kind | Binding |
| effect_boundary | player-write |
| success_outcome | player-created |
| error_outcome | creation-failed |

## CreatePlayerGuard

| Attribute | Value |
| --- | --- |
| protected_surface | /players/new |
| source_rule | CanCreatePlayer |
| conditions | authenticated,coach-role |
| fallback | /forbidden |
| decision_authority | false |
| enforcement_scope | ui-projection |

## CreatePlayerBinding

| Attribute | Value |
| --- | --- |
| mode | mutate |
| target_kind | Operation |
| target_ref | CreatePlayer |
| trigger | form-submit |
| parameter_mapping | form-to-operation |
| result_mapping | Player-to-PlayerViewModel |
| cache_key | players |
| invalidation | player-write |

## CreatePlayerAdapter

CreatePlayerAdapter is authored as the normalized Mapping node. Adapter remains
traceability metadata, not a second node kind.

| Attribute | Value |
| --- | --- |
| direction | outbound |

## Required Vocabulary Representation

| Required concept | Development representation | Machine record |
| --- | --- | --- |
| Adapter | Mapping alias with UI-boundary specialization | `CreatePlayerAdapter` |
| Domain State Indicator | projection of State Machine | `representations/domain-state-indicator.json` |
| Async Request Indicator | role on Component | `representations/async-request-indicator.json` |

No `shapes` or `reflects` edge is authored. Those endpoints and three missing
composition paths remain explicit in `residue.json`.
