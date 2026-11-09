# Gameplay classification scheme · draft v0.1

Status: design proposal, not a registered Lab Classification Scheme. The Lab's [Scheme](../../../../../../lab/reference/records/def-cal-definition-classification-scheme.md), [Axis](../../../../../../lab/reference/records/def-cal-definition-classification-axis.md), [Value](../../../../../../lab/reference/records/def-cal-definition-classification-value.md), [Assignment](../../../../../../lab/reference/records/def-cal-definition-classification-assignment.md) and [orthogonality invariant](../../../../../../lab/reference/records/def-cal-definition-classification-orthogonality-invariant.md) supply the modeling discipline: each question has a purpose, allowed answers, applicability and explicit version; labels do not create behavior.

## Assignment rules

1. An assignment names the exact model-object ID/version, this scheme version, one applicable axis, one allowed value and the reason/evidence for it.
2. Each applicable axis has one value for a simple object. When an attack has different hit shapes or payloads, represent them as separate delivery components or effects rather than assigning contradictory values to one component.
3. A changed scheme creates a new version. Earlier assignments retain their original interpretation until deliberately migrated.
4. A classification can aid search and validation, but the attack/effect definition owns its behavior. The words *powerful*, *beneficial* and *novel* are not classification values here because they depend on build, encounter and evidence.

## Model-object axis

| Axis ID | Question | Applies to | Allowed values | Why it matters |
| --- | --- | --- | --- | --- |
| `object.kind` | What kind of model object is this? | Every modeled definition or configuration | `system`, `mechanic`, `attack`, `delivery-component`, `gameplay-effect`, `modifier`, `upgrade`, `resource`, `challenge`, `build`, `run` | Selects the appropriate contract and validation. It does not determine the object's effect. |

## Attack and delivery axes

| Axis ID | Question | Applies to | Allowed values | Why it matters |
| --- | --- | --- | --- | --- |
| `attack.activation` | What starts an automatic attack attempt? | Attack | `ready-with-target`, `event-triggered`, `scheduled` | Determines when eligibility is checked. A cooldown may additionally gate any value. |
| `attack.propagation` | Does a resolved attack select further targets? | Attack | `none`, `target-leap` | Separates chain-lightning-style leaps from the hit shape at each target. |
| `attack.actor-motion` | Does the attack itself move its source actor? | Attack | `none`, `forced-displacement` | Keeps an attack jumping between targets distinct from a hero jumping or lunging. Exact path belongs to the attack rule. |
| `delivery.application` | Which candidate set can this component hit at one resolution point? | Delivery component | `single-entity`, `radius-area`, `cone-area`, `line-area` | Defines single-target versus AoE at component level. Geometry, caps and collision tests belong to the component rule. |
| `delivery.anchor` | What positions the hit footprint? | Delivery component | `selected-entity`, `selected-location`, `source-actor`, `previous-leap-target` | Distinguishes targeting from where an AoE lands. |

An attack can target one enemy and still have an AoE landing component. A target-leap attack can apply one `single-entity` component at each hop, or a radius component at each hop if explicitly defined. No attack-wide `AoE` flag is inferred from the number of targets actually hit.

## Effect and modifier axes

| Axis ID | Question | Applies to | Allowed values | Why it matters |
| --- | --- | --- | --- | --- |
| `effect.state-domain` | Which state does this primitive change? | Gameplay effect | `health`, `shield`, `resource`, `status`, `position`, `geometry`, `information`, `progression` | Determines the resolver and attribution rules. A composite mechanic emits multiple primitive effects. |
| `effect.application-time` | When does this effect apply? | Gameplay effect | `immediate`, `periodic`, `deferred` | Separates a direct hit from poison ticks or a later commitment payoff. Duration and tick schedule remain explicit fields. |
| `modifier.parameter-domain` | What parameter does this modifier change? | Modifier | `damage`, `mitigation`, `movement`, `attack-interval`, `cooldown`, `range`, `status-potency`, `propagation`, `resource-economy` | Makes cooldown reduction distinct from faster basic attacks. Exact parameter path is still required. |
| `modifier.scope` | Which definitions or instances can it alter? | Modifier | `character-stat`, `basic-attack`, `named-attack`, `attack-family`, `effect-family`, `resource-pool` | Prevents a local reduction from silently becoming global. |

Damage channel is an explicit property of each damage effect, initially `physical` or `magic` from the existing design. Poison application is a status effect; a later poison tick is a separately attributed damage event whose channel must be specified. Terrain and hostile contact describe **source**, not automatically a third damage channel.

## Run axes

| Axis ID | Question | Applies to | Allowed values | Why it matters |
| --- | --- | --- | --- | --- |
| `run.death-rule` | What happens when the character dies? | Run | `hardcore-reset`, `lite-level-retry` | Owns reset scope. |
| `run.build-rule` | Can earned choices be reallocated at level start? | Run | `rebuild`, `locked-additive` | Owns respec behavior. |

These two run axes are independent: all four combinations are legal. `lite-level-retry` is the current proposal from the [revision](../GAME-DESIGN-REVISION.md), pending gameplay validation.

## Example assignments

| Subject version | Axis | Value | Basis |
| --- | --- | --- | --- |
| `attack.chain-lightning@0.1` | `attack.propagation` | `target-leap` | Each accepted hop may select another eligible distinct target. |
| `component.chain-lightning-hop@0.1` | `delivery.application` | `single-entity` | Each hop applies to one selected entity. The whole attack can hit several entities. |
| `attack.chain-lightning@0.1` | `attack.actor-motion` | `none` | The attack leaps; the hero stays where movement input places them. |
| `component.blast-radius@0.1` | `delivery.application` | `radius-area` | It tests eligible entities in a declared radius. |
| `modifier.quick-recast@0.1` | `modifier.parameter-domain` | `cooldown` | It changes only named cooldown timers. |
| `run.example@0.1` | `run.death-rule` | `hardcore-reset` | One independent run setting. |
| `run.example@0.1` | `run.build-rule` | `locked-additive` | Another independent run setting. |

These rows illustrate assignments; they are not admitted Lab records or gameplay test results. Exact attack versions and numeric parameters remain to be authored.
