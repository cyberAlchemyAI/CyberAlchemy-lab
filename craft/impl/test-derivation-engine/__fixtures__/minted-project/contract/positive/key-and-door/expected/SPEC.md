# Key And Door Specification

Generated human view. Canonical semantics live in the project-local machine sources.
Graph digest: `1f0691fac9ed9612605d62d8b390e9b39eca24b6f11a6b0868c7591c6179e7ae`.

## Nodes

| Node | Kind | Intent |
| --- | --- | --- |
| `key-and-door.DoorUnlocked` | Event | Record that the door was successfully unlocked. |
| `key-and-door.HasKeyRule` | Rule | Allow the unlock operation only when the player holds the key. |
| `key-and-door.Player` | Entity | The identity-bearing player that can attempt to unlock the door. |
| `key-and-door.UnlockDoor` | Operation | Unlock the door when the player holds the required key. |

## Edges

| Edge | From | Type | To |
| --- | --- | --- | --- |
| `key-and-door.edge.has-key-rule-enforces-unlock-door` | `key-and-door.HasKeyRule` | `enforces` | `key-and-door.UnlockDoor` |
| `key-and-door.edge.player-performs-unlock-door` | `key-and-door.Player` | `performs` | `key-and-door.UnlockDoor` |
| `key-and-door.edge.unlock-door-produces-door-unlocked` | `key-and-door.UnlockDoor` | `produces` | `key-and-door.DoorUnlocked` |

This file is generated; edit machine sources and rebuild.
