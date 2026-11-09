# Build, progression and run model · draft v0.1

Status: candidate game rules, not implemented or balanced. The [game revision](../GAME-DESIGN-REVISION.md) owns the proposed 20-level challenge ladder. This model defines how upgrade choices, effects and mode settings move through it.

## 1. One character, two independent mode axes

The player creates one character with a starting build budget and takes it through levels 1–20. Combat is movement-only with automatic attacks under the [combat model](COMBAT.md). The run has two independent settings from the [classification scheme](CLASSIFICATION.md):

| Death rule | Build rule | Result |
| --- | --- | --- |
| Hardcore reset | Rebuild | Death returns to a new level-1 character; before each reached level, reallocate the earned budget. |
| Hardcore reset | Locked additive | Death returns to a new level-1 character; previously chosen gain/drawback pairs remain fixed while alive. |
| Lite level retry | Rebuild | Death restores the level-entry snapshot; a new attempt may rebuild from the same earned budget at the level-start screen. |
| Lite level retry | Locked additive | Death restores the level-entry snapshot and its fixed build; only new rewards after successful levels add choices. |

Lite's retry scope remains a **proposed interpretation** of the user's “lite” mode. All four modes use the same attack, damage, enemy and hazard rules. Mode settings change persistence and choices between attempts, not hidden combat bonuses.

## 2. Upgrade choice contract

An upgrade offer contains one gain and exactly three mutually exclusive drawbacks. A selected `UpgradeChoice` stores `offer_id`, gain definition/version, selected drawback definition/version, acquired level, budget cost and source. Gain and drawback are one inseparable build record. An offer is invalid if any advertised drawback has no effect under the legal build or cannot be measured in a credible upcoming challenge.

Gains and drawbacks may install attack components, change propagation, add gameplay effects or apply modifiers. They must name what they touch:

| Example offer | Gain | Three drawback options | Model location |
| --- | --- | --- | --- |
| **Arc Conductor** | A named auto attack gains target-leap propagation with a finite target cap. | Lower direct damage; longer named cooldown; lower magic defense. | Attack propagation plus modifier/effect records. |
| **Wide Surge** | A named attack gains a radius-area delivery component. | Lower single-entity damage; longer basic attack interval if it is a basic attack; lower movement speed during its windup. | Delivery component plus scoped modifiers. |
| **Quick Recast** | Reduce cooldowns of a named attack family. | Lower effect potency; lower maximum health; lower movement speed. | Cooldown modifier plus one selected cost. |
| **Focused Strike** | Increase single-entity hit power. | Smaller existing area radius; longer attack windup; lower physical mitigation. | Damage modifier plus one selected cost. |

These are structural examples, not approved cards or balance values. A drawback referring to a missing area component (such as “smaller radius” on a build with no AoE) is ineligible; the offer needs a meaningful replacement. A drawback is not automatically fair because it has a number. Movement penalties must respect reachable-warning and minimum-speed constraints.

## 3. Build state and derivation

`BuildState` consists of earned budget, acquired offer pool, selected upgrade records, legal starting traits and the resulting effective parameter/effect set. Derived stats are calculated from recorded choices; they are not separately edited. A rebuild replaces the selected records at a level-start boundary while conserving budget and offer eligibility. Locked additive mode preserves earlier records and spends only newly earned budget.

For deterministic resolution, calculate the effective build in a declared order: base character parameters → permanent selected gains/drawbacks → level-scoped temporary effects → caps/floors. A gain and its cost enter together. If a combination exceeds a cap, show the unused portion before the player commits. The exact stacking arithmetic and numeric caps still require card and combat definitions.

Upgrades may have cross-system effects, but each state has one owner: Build owns the selection, Combat owns a modified cooldown or attack resolution, and Encounter owns level hazards. A selected card cannot directly rewrite an already committed attack or a level-entry snapshot.

## 4. Level and run transitions

| Transition | Preconditions and outcome |
| --- | --- |
| Create character | Select death and build rules, set starting budget, build and level 1. |
| Enter level | Validate build; record one level-entry snapshot containing character state, build, resources, challenge version and random-stream positions; publish public encounter facts. |
| Complete level | Resolve objective once, grant bounded reward once, add earned budget/options and advance to the next level-start screen. Level 20 completion ends the run. |
| Die in lite | Discard attempt-only rewards, restore entry snapshot and return to that level's preparation screen. Rebuild may reallocate; locked build cannot. |
| Die in hardcore | Close the character run and its build, then create a new level-1 character under the chosen mode settings if the player retries. |

No failed attempt yields permanent upgrade budget or resources. Level rewards are idempotent: replay, reflection, respawns or duplicate completion events cannot grant them twice. A level seed is part of the snapshot for an exact retry; whether the game later offers alternate seeds is a separate mode rule.

## 5. Challenge contract

A level definition needs an ID/version, distinct primary challenge, enemy and hazard families, public warnings, completion condition, reward budget, and a list of mechanic assumptions it pressures. A stronger enemy with more HP alone does not count as a distinct challenge. The [provisional ladder](../GAME-DESIGN-REVISION.md#5-a-provisional-twenty-level-challenge-ladder) supplies 20 questions but no complete encounter data.

The encounter must preserve at least one legal response to a newly issued compulsory lethal warning under the current build's movement speed, slows, walls and attack movement locks. Locked-build runs require special review: later levels may punish a weakness but cannot silently require a single earlier upgrade or mandatory respec. Rebuild runs may exploit foreknowledge, which is an intended strategic difference; the available information should be declared before preparation.

## 6. Invariants to carry into executable records

- An upgrade gain and exactly one selected drawback are stored, applied and removed together.
- Rebuild conserves earned budget; locked additive mode never rewrites earlier choices.
- Lite retry restores the level-entry state and grants no failed-attempt farming; hardcore death resets the character.
- Classification labels describe a model object; they do not perform an upgrade or change a combat result.
- Every installed attack component, effect and modifier is traceable to a versioned base rule or upgrade choice.
- Each of 20 levels has a stated challenge question and at least one observable way the player's movement and build can respond.

Next: author a few exact attack/effect/upgrade records and simulate level 1 with contrasting builds before treating these contracts as gameplay evidence.
