# Automatic attack, delivery and effect model · draft v0.1

Status: candidate game rules. No resolver, balance simulation or playtest exists. This document follows the [system map](README.md), [classification scheme](CLASSIFICATION.md) and original [effect rules](../../2026-10-11/GAME-DESIGN.md#effect-rules).

## 1. The four separate questions in an attack

1. **Activation:** What automatic condition makes the attack eligible? The player only controls movement during combat.
2. **Acquisition:** Which initial target or location does the attack choose, using public state and deterministic tie-breaking?
3. **Delivery:** Which component tests a single entity or a spatial area, and when is its hit resolved?
4. **Propagation:** After a qualifying hit, does the attack stop or **leap to another target**? Attack leap here means chain-lightning-style propagation. Source-actor movement is separate.

AoE and single-target describe a **delivery component**, not damage type. Cooldown reduction describes a **modifier**, not a delivery or effect. An attack can combine a single-target initial hit, target-leap propagation and an AoE component at each landing if the definition pays for and bounds all three.

## 2. Definitions and required fields

| Object | Required fields before it enters a playable pool |
| --- | --- |
| Attack definition | Stable ID/version; activation and target rule; eligibility/range; windup; delivery components; propagation rule; resource cost; cooldown or basic interval; recovery; interruption/retarget rule; feedback. |
| Delivery component | Anchor rule; `single-entity`, radius, cone or line application; geometry and line-of-sight checks; hit cap; timing; effect references; whether a subject can be hit again by this attack instance. |
| Attack instance | Run-local ID; definition version; source; commit time; selected initial target; committed modifier snapshot; visited leap anchors; effect recipients; remaining hops; current phase. |
| Gameplay effect | State domain and exact target; magnitude or operation; source attribution; channel if damage; duration/tick timing if relevant; stacking/cap; dispel or expiry; recursion eligibility. |
| Modifier | Exact parameter path; operation; scope; stacking order; cap/floor; lifetime and source upgrade. |

**Hit attempt** means a delivery component tested an eligible subject. **Accepted hit** means collision, invulnerability, avoidance and any other admission rules allowed the hit event. **HP loss** means a damage effect or separate tick actually reduced health after mitigation and shield handling. An accepted hit may deplete a shield while causing zero HP loss. A blocked touch can also be an accepted hit with zero direct HP loss, preserving the old [touch/wound distinction](../../2026-10-11/GAME-DESIGN.md#7-one-unusual-core-bind-the-enemys-stated-objective).

## 3. Resolution sequence

The following order is the starting contract, subject to prototype revision:

1. When an automatic trigger occurs, check readiness, target eligibility, range and resource sufficiency. If any check fails, record why; do not spend or start a cooldown.
2. Acquire the initial target or location by the definition's declared rule. The default for entity targeting is nearest eligible target, then stable entity ID. No hidden optimizer changes the player's build strategy.
3. Commit one attack instance, snapshot applicable modifiers and spend its declared resource. Start its cooldown at commitment. If a target leaves during windup, do not silently retarget; the definition must say whether the committed hit misses or follows a marked target.
4. Resolve windup and movement restrictions. Ordinary player movement continues unless the attack explicitly imposes a movement cost or lock.
5. At each delivery point, form the candidate set from the component's footprint. Resolve hit admission, then damage/status/displacement/geometry effects in a declared order. For damage, apply channel-specific mitigation, then shields, then direct HP loss. Preserve separate attribution for poison ticks, terrain, reflection and direct contact.
6. If propagation is `target-leap` and its qualifying hit condition was met, choose the next distinct anchor under the leap rule. Repeat bounded delivery until the target limit is reached or no eligible anchor exists.
7. Close the attack instance and explain its results. The next use requires both cooldown completion and any recovery condition; cooldown reduction alone cannot erase recovery.

An attack definition may require different ordering for a specific effect, but must state the difference before use. Rejected hit attempts, failed target checks and stopped chains remain visible events rather than silent omissions.

## 4. Single-target and area delivery

| Delivery | Candidate set at resolution | Required boundary |
| --- | --- | --- |
| `single-entity` | The one selected eligible entity. | At most one accepted hit for that component. |
| `radius-area` | Eligible entities whose collision shapes intersect a radius around the declared anchor. | Radius, center-lock rule, line-of-sight policy and max recipients. |
| `cone-area` | Eligible entities in an oriented cone from its anchor. | Facing snapshot or tracking rule, angle, reach and max recipients. |
| `line-area` | Eligible entities intersecting a declared line segment or swept path. | Width, endpoints, obstruction/piercing rule and max recipients. |

Area delivery does not promise that multiple targets are present. If more eligible subjects are inside than the cap permits, select recipients by declared priority (default distance from anchor, then stable entity ID). A selected-entity attack may also produce a radius component centered on that entity's locked or impact position; the attack definition must choose which. A composite attack lists components in resolution order and prevents accidental duplicate damage from overlapping footprints.

## 5. Target-leap propagation (chain lightning)

`target-leap` is an attack-level propagation rule. It requires `max_targets` (counting the initial anchor), `leap_range`, a qualifying-hit condition, a candidate-selection rule, hop timing, any falloff, and line-of-sight policy. A chain has a finite visited-anchor set. The default candidate rule is the nearest eligible enemy within `leap_range` of the previous anchor at hop time, then stable entity ID; already visited anchors are excluded.

The default qualifying condition is an **accepted hit** on the current anchor, even if a shield prevents HP loss. An invulnerable target with no accepted hit stops the chain. A poison tick, reflected hit or AoE recipient does not create an extra leap: only the current primary anchor can advance this attack instance. By default, one subject can receive the attack's direct damage at most once per instance, even if later AoE footprints overlap. A specific variant may change that rule only with an explicit cap and explanation.

Illustrative attack: `Chain Lightning` acquires one enemy, applies one single-entity magic hit, then can leap to up to two more distinct eligible enemies. The source hero remains in place apart from the player's movement. The second and third hops may have a defined damage falloff. The target count is an example, not a balance result.

If a later attack makes the **hero** jump or lunge, model that separately as `attack.actor-motion = forced-displacement`, with a path, collision, vulnerability and landing rule. It does not redefine target leap.

## 6. Cooldowns and cooldown reduction

**Cooldown** is the interval from an attack's committed use until that named attack can be eligible again. **Basic attack interval** is the cadence of the default automatic attack. **Windup** is time before delivery; **recovery** is the post-commit action constraint. They are separate parameters.

**Cooldown reduction (CDR)** is a modifier to explicitly named cooldowns. The provisional resolver takes a snapshot at commitment: apply eligible reductions to the base cooldown, apply eligible cooldown increases from drawbacks, then enforce that attack's minimum cooldown and reduction cap. Numeric caps belong to each attack/family definition and need balance testing. Changing a build later does not rewrite an already running cooldown. CDR does not alter the basic attack interval, windup, recovery, poison ticks or level timers unless a separate modifier expressly names those parameters.

Example: an upgrade that says “reduce cooldowns of chain attacks” can shorten `Chain Lightning` if it carries the `chain` scope tag. It does not make ordinary basic attacks faster. An upgrade that says “increase attack speed” changes the basic interval under its own cap and does not shorten `Chain Lightning`'s cooldown by implication.

## 7. Effect safety and feedback invariants

- Each attack instance has a finite component count, recipient cap and leap count. Secondary effects cannot recursively create unbounded attacks or leaps.
- Reflection from reflected damage and poison ticks does not recursively finance itself, preserving the original rule.
- Every effect records its direct source and originating attack/upgrade; labels like “AoE” or “magic” alone do not explain damage attribution.
- Movement-only play must show target choice, upcoming attack commitment, active cooldown and chain path clearly enough for the player to reposition intentionally.
- A new lethal hazard must leave a reachable warned escape under the current movement state, including slows, walls and attack-imposed movement locks, as required by the original design.

Open balance questions: leap range and timing, per-hop falloff, AoE recipient caps, simultaneous-event order, attack animation/collision detail and CDR caps. These are parameter decisions, not reasons to merge the categories above.
