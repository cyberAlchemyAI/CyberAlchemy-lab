# Game design revision: one hero, twenty levels, costly evolution

Date: 8 November 2026. Status: design proposal based on the user's new direction; no implementation or gameplay evidence. This document advances the [11 October game design](../2026-10-11/GAME-DESIGN.md) without rewriting that dated research record. Read the [mechanics and effects inventory](MECHANICS-INVENTORY.md) first.

The [first gameplay system model](system-model/README.md) defines system ownership and formalizes attack delivery, target-leap propagation, effects, modifiers, upgrades and run-mode state.

## 1. New design center

The player controls **one customizable character** through **20 levels**. During combat, the player controls **movement only**. The character attacks automatically according to visible, deterministic rules and the chosen build. Every permanent build selection grants an improvement and requires the player to choose **one of three different drawbacks**. The game should make a stronger character interesting by changing what that character is vulnerable to, what position it wants and how it handles the next level's challenge.

The old three-hero roster, three-stage run and manual-attack/full-autoplay split are superseded by these user decisions. The Foundry, Marsh and Court can remain as thematic arcs and boss sources within 20 levels; their exact placement below is a proposal. Poison, slow, knockback, reflection, magic, temporary geometry, warned hazards and boss objectives remain useful mechanic seeds. None is proven fun or balanced.

## 2. Run and mode rules

The two mode choices are independent. A player selects one death rule and one build rule when starting a character.

| Mode axis | Rule | Proposed death/retry or build consequence |
| --- | --- | --- |
| Hardcore | Character death resets the character and level progress to level 1. | No permanent combat power survives death; records and cosmetic or informational unlocks may persist only if explicitly designed later. |
| Lite | Character death retries the current level. | Restore the character, build, resources and level challenge to the level-entry snapshot. Failed attempts grant no XP, upgrades or farmable resources. |
| Rebuild | At the start of each level, reallocate all earned build selections and their paired drawbacks from the available pool. | The earned budget is conserved; rebuilding does not create additional upgrade picks or erase the cost of a selected improvement. |
| Locked build | Add newly earned selections between levels, but do not respec earlier selections or their drawbacks. | Permanent choices create a long-term adaptation problem. Level design must leave viable responses for different legal builds. |

These definitions give four combinations: hardcore/rebuild, hardcore/locked, lite/rebuild and lite/locked. Mode selection is fixed for a character's run. Whether a player can change it after a completed 20-level run remains open.

### Level loop

1. Inspect the next level's disclosed challenge: enemy families, damage channels, terrain hazards and special objective. Exact spawn positions may remain uncertain.
2. In rebuild mode, reallocate the earned build budget. In locked mode, retain past choices and spend only new selections. Every selection includes its chosen drawback.
3. Enter the level. Move to position, route enemies, avoid warnings and shape which automatic attacks or passive effects can occur.
4. On success, earn a bounded upgrade choice and advance. On death, apply the selected death rule.

For the first design pass, permanent selections happen at level boundaries. Existing mid-stage caches can return as temporary resources or as a paused, explicitly priced build offer after the basic loop works. This avoids hiding a permanent drawback inside a rushed combat pickup.

## 3. Movement-only combat contract

The player has no attack, guard, cast, dodge, wall-placement or binding button during a level. The initial automatic attack rule should be simple enough to predict: at a declared interval, choose a reachable eligible target by a displayed priority (for example, closest enemy, then stable ID), face/aim under known limits, commit for a visible windup, resolve collision and damage, then recover. Movement can change range, line of sight, facing opportunity, target priority and exposure. It cannot cancel a committed attack unless a declared build effect permits that tradeoff.

Automatic abilities are build effects with public triggers, costs, cooldowns and target rules. Examples: retaliate after a qualifying direct hit, apply poison on a successful attack, generate a shield after crossing a warned zone, or create a short wall after a declared movement event. The game must show **why** an effect fired or did not fire. If several effects trigger together, fix their order and prevent recursive loops.

An attack can hit one target, affect an area, or leap from one target to the next like chain lightning. These are separate delivery and propagation rules. Cooldown reduction changes a named reuse timer, not the basic attack interval by default. The [combat model](system-model/COMBAT.md) closes the initial distinctions; numeric limits remain for balance work.

The old six-rule authored autoplay editor is not part of the starting control scheme. A later version could let players customize targeting or passive trigger priorities **before** a level without adding combat buttons or automatic movement. That would need its own usability test; high customization should begin with understandable build choices, not an opaque rules program.

## 4. Upgrade and drawback structure

Each upgrade card has one gain and three mutually exclusive drawback choices. Selecting a drawback attaches it to that gain as a single build record. A rebuild may replace the entire record; locked mode cannot. Numerical values below are deliberately absent until the combat model and level budgets are fixed.

| Gain example | Drawback A | Drawback B | Drawback C | Decision it should create |
| --- | --- | --- | --- | --- |
| Higher physical armor | Lower magic defense | Lower movement speed | Shorter auto-attack range | Choose the exposure the armor build can manage. |
| Stronger magic attacks | Lower physical mitigation | Longer attack commitment | Lower maximum health | Pursue burst while accepting a different survival problem. |
| Faster automatic attacks | Lower damage per hit | Higher resource or heat cost | Shorter targeting range | Trade output pattern, resource endurance or positioning. |
| More potent poison | Weaker direct attacks | Slower poison application cadence | Less defense against poison | Decide between burst, sustained exposure and mirror vulnerability. |
| Larger retaliation payoff | Lower mobility | Lower ranged damage | Smaller shield capacity | Accept contact deliberately without making exposure free. |
| More durable temporary geometry | Slower movement near own walls | Lower wall-trigger frequency | Weaker direct damage | Buy routing control at a cost that remains visible. |

These are **test cards**, not a final item list. A drawback must affect the level being played or a credible future challenge; an irrelevant penalty is a free upgrade. Avoid strict dominance among the three penalties. Cap stacking and establish minimum viable movement, health and attack output so legal builds do not become irrecoverably unable to finish a level. Conversely, do not guarantee that every build has equal success: the point is to make tradeoffs consequential.

The old six items can become upgrade seeds: Hazard Boots for terrain recovery, Contact Mirror for direct-hit retaliation, Wall Spool for geometry, Antidote Kit for cleansing, Magic Prism for magic behavior and Study Seal for growth. Their original slot, charge and exposure costs should not silently stack with a new penalty; each needs an explicit total price.

## 5. A provisional twenty-level challenge ladder

Each row names a different **primary question**, not a complete encounter or a proven difficulty curve. The old three regions and bosses are reused as three arcs. Levels 6, 13 and 20 are proposed boss milestones. Other levels may contain elite encounters, but should not repeat the same primary decision with larger HP numbers.

| Level | Theme | Primary challenge for movement and build | Mechanics to exercise |
| --- | --- | --- | --- |
| 1 | Foundry | Learn auto-target range and safe repositioning. | Basic attack, movement, direct hit. |
| 2 | Foundry | Choose whether to cross a warned melee contact zone. | Physical mitigation, retaliation. |
| 3 | Foundry | Reach a target through a ranged firing lane. | Line of sight, speed, magic/physical defense. |
| 4 | Foundry | Route two enemy types without losing an exit. | Slow, knockback, geometry. |
| 5 | Foundry | Spend a finite shield or preserve it for a timed wave. | Shield, recovery, resource reserve. |
| 6 | Foundry boss | Survive the Bellows Keeper's guardable hit and floor sweep. | Contact versus terrain, warning readability. |
| 7 | Marsh | Cross poison while deciding whether to fight or move on. | Poison, cleansing, duration. |
| 8 | Marsh | Manage a flanker while the auto-target rule prefers another enemy. | Target priority, positioning. |
| 9 | Marsh | Make a temporary wall useful without trapping the hero. | Geometry, pathing, exit preview. |
| 10 | Marsh | Handle a slow field under a timed hazard. | Slow, escape feasibility. |
| 11 | Marsh | Choose between a safe detour and an exposed reward route. | Bounded XP/acquisition, speed, health. |
| 12 | Marsh | Respond when a warned enemy breaks the preferred funnel. | Wall counter, alternate route. |
| 13 | Marsh boss | Beat the Dredger's poison, range and wall-breaking pressure. | Multi-source defense, build adaptation. |
| 14 | Court | Vary a repeated escape route against visible finite memory. | Movement pattern, enemy prediction. |
| 15 | Court | Decide whether protection's attraction cost is useful. | Shield beacon candidate, aggro. |
| 16 | Court | Pass a timed gate without losing the return route. | Timing, geometry, movement speed. |
| 17 | Court | Survive a strong attack while a borrowed defense expires. | Shield debt candidate, timing. |
| 18 | Court | Escape a lethal sweep through a disclosed, reachable route. | Hazard fairness, knockback. |
| 19 | Court | Practice changing the outcome of a public boss objective. | Touch/wound/arrival distinction. |
| 20 | Court boss | Face the Examiner's changing objective and movement pressure. | Goal-bound commitment candidate, full build tradeoff. |

Levels 15–17 and 19–20 use candidate mechanics from the wider portfolio. They need a simpler-equivalent comparison and a movement-only trigger contract before inclusion. If one candidate fails, replace the level's question rather than forcing an unworkable effect into the game. Hardcore's 20-level restart cost also requires short level durations, clear failure explanations and measured total run length.

## 6. What to specify and test next

1. **Close the automatic attack model.** Define target selection, attack timing, interruption, damage channels and feedback. Check whether moving alone produces enough interesting decisions in a small arena.
2. **Close the upgrade economy.** Define starting stats, upgrade budget per level, stacking limits, six to ten concrete cards and three drawbacks per card. Make every selected cost visible in the build summary.
3. **Prototype one challenge and one counter.** Use physical armor versus magic defense or speed, one auto attack, one warned hazard and two enemy types. Test a few contrasting builds before producing 20 levels.
4. **Test the four mode combinations.** Snapshot/retry/reset behavior, permanent choice records, rebuild budget conservation and no death farming need explicit checks. In locked mode, test whether several legal early builds can still answer later levels through movement and new upgrades.
5. **Build a five-level vertical slice.** Include a boss, distinct challenge questions and the first upgrade set. Use observations from real play to revise costs, then expand the 20-level ladder.
6. **Revisit unusual mechanics one at a time.** Reflection and geometry are good early candidates. Test goal-bound commitment only after the movement-only interaction makes its outcome legible. Defer audio until the core loop works.

The principal design risk is that automatic attacks make movement feel passive while an enormous upgrade menu makes planning exhausting. The first prototype should show a small number of visible, consequential tradeoffs and explain every automatic action. If that is not engaging, adding more effects or levels will not repair the core loop.
