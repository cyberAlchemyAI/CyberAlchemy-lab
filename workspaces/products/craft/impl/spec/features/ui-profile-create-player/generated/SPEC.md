# Ui Profile Create Player Specification

Generated human view. Canonical semantics live in the project-local machine sources.
Graph digest: `73f2199f3d7232add1620f5708a0345bf098450143311a6462a478bbcbb0cefc`.

## Nodes

| Node | Kind | Intent |
| --- | --- | --- |
| `ui-profile-create-player.CanCreatePlayer` | Rule | Allow player creation only for an authorized actor and valid input. |
| `ui-profile-create-player.CreatePlayer` | Operation | Create a player from validated input and persist the new identity. |
| `ui-profile-create-player.CreatePlayerAction` | Action | Own the user intent and observable outcomes of submitting player creation. |
| `ui-profile-create-player.CreatePlayerAdapter` | Mapping | Normalize Adapter vocabulary into the canonical Mapping kind at the UI boundary. |
| `ui-profile-create-player.CreatePlayerBinding` | Binding | Persist the durable query/mutation integration contract for player creation. |
| `ui-profile-create-player.CreatePlayerForm` | Form | Own typed player fields, validation, submission, and error mapping. |
| `ui-profile-create-player.CreatePlayerGuard` | Guard | Project the authoritative create-player Rule into route feedback. |
| `ui-profile-create-player.CreatePlayerHook` | Hook | Expose framework-neutral reactive state for the player-creation interaction. |
| `ui-profile-create-player.CreatePlayerPage` | Page | Own the terminal route and primary content for creating a player. |
| `ui-profile-create-player.CreatePlayerPanel` | Component | Render create-player feedback and consume reactive mutation state. |
| `ui-profile-create-player.CreatePlayerViewModel` | View Model | Project player fields into create-player display and confirmation roles. |
| `ui-profile-create-player.DashboardLayout` | Layout | Provide the shared authenticated shell around create-player pages. |
| `ui-profile-create-player.GetPlayerDefaults` | Query | Read non-mutating defaults used to initialize the create-player form. |
| `ui-profile-create-player.Player` | Entity | Represent the identity-bearing player created by the feature. |
| `ui-profile-create-player.PlayerApi` | Interface | Expose player creation and default-value retrieval to the UI boundary. |
| `ui-profile-create-player.PlayerCreated` | Event | Record the past fact that a player was created. |
| `ui-profile-create-player.PlayerLifecycle` | State Machine | Describe the admitted player lifecycle states projected by the UI. |

## Edges

| Edge | From | Type | To |
| --- | --- | --- | --- |
| `ui-profile-create-player.edge.can-create-player-enforces-create-player` | `ui-profile-create-player.CanCreatePlayer` | `enforces` | `ui-profile-create-player.CreatePlayer` |
| `ui-profile-create-player.edge.create-player-adapter-maps-player-api` | `ui-profile-create-player.CreatePlayerAdapter` | `maps` | `ui-profile-create-player.PlayerApi` |
| `ui-profile-create-player.edge.create-player-binding-fetches-player-defaults` | `ui-profile-create-player.CreatePlayerBinding` | `fetches` | `ui-profile-create-player.GetPlayerDefaults` |
| `ui-profile-create-player.edge.create-player-binding-mutates-create-player` | `ui-profile-create-player.CreatePlayerBinding` | `mutates` | `ui-profile-create-player.CreatePlayer` |
| `ui-profile-create-player.edge.create-player-creates-player` | `ui-profile-create-player.CreatePlayer` | `creates` | `ui-profile-create-player.Player` |
| `ui-profile-create-player.edge.create-player-form-contracts-player-api` | `ui-profile-create-player.CreatePlayerForm` | `contracts` | `ui-profile-create-player.PlayerApi` |
| `ui-profile-create-player.edge.create-player-form-submits-create-player-action` | `ui-profile-create-player.CreatePlayerForm` | `submits` | `ui-profile-create-player.CreatePlayerAction` |
| `ui-profile-create-player.edge.create-player-guard-mirrors-can-create-player` | `ui-profile-create-player.CreatePlayerGuard` | `mirrors` | `ui-profile-create-player.CanCreatePlayer` |
| `ui-profile-create-player.edge.create-player-guard-protects-create-player-page` | `ui-profile-create-player.CreatePlayerGuard` | `protects` | `ui-profile-create-player.CreatePlayerPage` |
| `ui-profile-create-player.edge.create-player-page-renders-create-player-panel` | `ui-profile-create-player.CreatePlayerPage` | `renders` | `ui-profile-create-player.CreatePlayerPanel` |
| `ui-profile-create-player.edge.create-player-panel-consumes-create-player-hook` | `ui-profile-create-player.CreatePlayerPanel` | `consumes` | `ui-profile-create-player.CreatePlayerHook` |
| `ui-profile-create-player.edge.create-player-panel-displays-create-player-view-model` | `ui-profile-create-player.CreatePlayerPanel` | `displays` | `ui-profile-create-player.CreatePlayerViewModel` |
| `ui-profile-create-player.edge.create-player-produces-player-created` | `ui-profile-create-player.CreatePlayer` | `produces` | `ui-profile-create-player.PlayerCreated` |
| `ui-profile-create-player.edge.create-player-view-model-derives-player` | `ui-profile-create-player.CreatePlayerViewModel` | `derives` | `ui-profile-create-player.Player` |
| `ui-profile-create-player.edge.dashboard-layout-wraps-create-player-page` | `ui-profile-create-player.DashboardLayout` | `wraps` | `ui-profile-create-player.CreatePlayerPage` |
| `ui-profile-create-player.edge.get-player-defaults-reads-player` | `ui-profile-create-player.GetPlayerDefaults` | `reads` | `ui-profile-create-player.Player` |
| `ui-profile-create-player.edge.player-api-exposes-create-player` | `ui-profile-create-player.PlayerApi` | `exposes` | `ui-profile-create-player.CreatePlayer` |
| `ui-profile-create-player.edge.player-api-exposes-get-player-defaults` | `ui-profile-create-player.PlayerApi` | `exposes` | `ui-profile-create-player.GetPlayerDefaults` |
| `ui-profile-create-player.edge.player-created-transitions-player-lifecycle` | `ui-profile-create-player.PlayerCreated` | `transitions` | `ui-profile-create-player.PlayerLifecycle` |
| `ui-profile-create-player.edge.player-performs-create-player` | `ui-profile-create-player.Player` | `performs` | `ui-profile-create-player.CreatePlayer` |

This file is generated; edit machine sources and rebuild.
