# Game mechanics and effects inventory

Date: 8 November 2026. Status: design inventory for the one-character revision; no game implementation or playtest. This inventory separates the original game's selected rules from its wider research portfolio. A proposal in the portfolio is not automatically part of the revised game.

The first [gameplay system model](system-model/README.md) adds a classification scheme and separate combat, build and run contracts. It treats single-target and AoE as delivery, target leap as attack propagation, and cooldown reduction as a modifier.

Sources: [original game design](../2026-10-11/GAME-DESIGN.md), [original frame](../2026-10-11/FRAME.md), [24 proposed mechanics](../2026-10-11/WILD-MECHANICS.md), [four mechanic constructions](../2026-10-11/MECHANIC-GENERATION-EXAMPLES.md), and [six composition-study representatives](../2026-10-11/composition-study-001/REPORT.md).

## 1. Existing systems and effects

| System / effect | What the original design specifies | Revised disposition |
| --- | --- | --- |
| Health, damage, death | Direct hostile hits, damage over time, terrain damage and death have separate attribution. Death ends the original run. | Keep attribution. Hardcore resets the character; lite retries the current level from its entry state. |
| Physical mitigation | Damage reduction and guard can reduce a qualifying hit; a blocked touch differs from direct HP loss. | Keep as upgrade axes. Define armor and percentage reduction separately before balancing them. Guard must trigger automatically if retained. |
| Magic and resistance | Magic is a separate damage channel with explicit resistance and visible source attribution. | Keep. Magic defense is an explicit tradeoff axis. |
| Temporary shields | Shields absorb after mitigation; a commitment payoff may create a capped shield. | Keep, with a finite cap and expiry/spend rule. |
| Stamina, recovery and commitment | Guard, casts, placement and movement actions have costs or recovery windows. | Keep costs for automatic actions. Decide whether movement consumes stamina; the player has no manual guard or cast button. |
| Dodge and invulnerability | Manual dodge and accepted-hit rules distinguish a visual overlap from a true hit. | Rework or defer. A movement-only control scheme cannot rely on an extra dodge command. If a build grants an automatic dodge, its trigger and cost must be visible. |
| Poison | Capped damage over time with named stack/refresh and tick rules; it does not finance direct-hit retaliation. | Keep. Include resistance, duration and cleansing as possible build axes. |
| Slow | Bounded movement impairment, never an unexplained permanent stop. | Keep for enemies and hero; movement cost is especially important with movement-only control. |
| Knockback | Directional displacement with resistance and collision rules; bosses may resist magnitude. | Keep. Movement, walls and hazards make it a strong positioning mechanic. |
| Reflection / retaliation | Qualifying hostile direct contact can produce a capped response; reflected damage never recursively reflects. | Keep as a build family. Preserve the distinction between blocked contact and actual HP loss. |
| Walls and routing | Temporary walls have count, lifetime, placement recovery and deterministic path updates. Preview the hero's exit. | Keep as an automatic or movement-triggered build family only after its trigger can be understood without a placement button. |
| Terrain and lethal hazards | Hazard families and warning zones are public; a newly issued lethal event must leave a reachable escape under current constraints. | Keep. Levels can test different movement and defensive assumptions. |
| Enemy attack facts | Windups, targeting, collision, accepted hits, deadlines and boss objectives are public enough to support response. | Keep. Auto attacks must have equally explicit target and timing rules. |
| Goal-bound commitment (WM01) | Spend a catalyst to empower one highlighted boss attack; earn one bounded payoff if its announced touch, wound or arrival objective fails and the hero survives. | Candidate for a later level. Binding needs a preselected automatic trigger because the player only controls movement during combat. |
| Items and XP | Finite encounters and caches give items/XP; six starting item modifiers cover terrain, contact, walls, cleanse, magic and growth. | Keep the effect families. Every permanent build selection must pair a gain with one of three meaningful drawbacks. Decide when offers pause the level. |
| Enemy counters | Poison/range pressure reflection, flyers or wall breakers pressure mazes, and visible memory can pressure repeated routes. | Keep the principle: pressure an assumption while preserving an affordable adaptation. |
| Singing / audio | A separate optional input slice ties calibrated pitch and rhythm to power, detection, decoys and silence. | Defer. Live singing conflicts with movement-only combat unless treated as a pre-level build choice or a later optional input mode. |

The original six items are Hazard Boots, Contact Mirror, Wall Spool, Antidote Kit, Magic Prism and Study Seal. They remain effect seeds, not approved upgrade cards. Their old costs were equipment slots, charges or exposure; the revised gain-plus-drawback format needs a new cost comparison.

## 2. New rules that need exact contracts

These are required by the new direction and were not closed by the original document:

| Rule | Minimum contract to define next |
| --- | --- |
| One evolving hero | Starting stats, upgrade slots/budget, legal combinations and how effects are acquired. No class-exclusive baseline abilities. |
| Automatic attacks | Target eligibility and priority, range, facing, attack interval, windup, collision, resource spending, cooldown, interruption and visible feedback. Movement is the only combat input. |
| Single-target and AoE delivery | Define a hit component's candidate set: one entity, radius, cone or line. A targeted attack can also contain an area component. |
| Attack leap / chain propagation | Define a finite jump from one accepted-hit target to another eligible distinct target; the character does not move because of this term. |
| Cooldown reduction | Define a scoped modifier to named cooldowns with stacking, cap and floor; keep basic attack interval, windup and recovery separate. |
| Build choice | One improvement plus exactly one selected drawback from three alternatives. Store both as one irreversible choice in locked-build mode. |
| Physical armor versus damage reduction | Decide whether armor is flat, proportional or threshold-based; prevent double-dipping with reduction and shields. |
| Magic defense | Damage-channel scope and relation to poison, terrain and non-magical statuses. |
| Movement speed | Base speed, slowing, minimum viable speed, collision and escape feasibility under lethal warnings. |
| Twenty levels | Entry/exit, challenge identity, reward budget, boss milestones and level-specific observations. |
| Hardcore versus lite death | What resets on death, what remains unlocked, and whether a failed attempt can grant resources. |
| Rebuild versus locked build | Whether all earned choices can be reallocated at level start, and how newly earned options extend a locked build. |

Do not add an effect to the playable pool until its trigger, state, cost, stacking rule, enemy counter and player-facing explanation are specified. The inventory is a map of design work, not a claim that all listed effects belong in the first prototype.

## 3. Wider candidate portfolio

All WM entries below are **unimplemented research candidates**. WM01 was selected by the old design; it has not yet been adapted to movement-only play. The grouping is for review, not a novelty verdict.

| IDs | Candidate mechanics | First review for this revision |
| --- | --- | --- |
| WM01–WM04 | Invited wound; perfect charge; timed gate; monster-drawn spell | Strong movement/positioning fit, but need automatic triggers and readable warnings. |
| WM05–WM08 | Heal boss into a problem; shield broadcasts position; maze battery; shed armor into cover | Useful gain/cost seeds, especially defense versus exposure or geometry. |
| WM09–WM12 | Poison passage/safe footsteps; refuse knockback; train exit guard; missed-attack echo | Movement tradeoffs and level challenges; the old manual withholding action needs redesign. |
| WM13–WM16 | Targeting promise/decoy; future warning; slower XP route; borrowed future defense | Targeting, information, growth and temporal debt candidates. |
| WM17–WM22 | Singing gate, damage/detection, imperfect-note decoy, silence/decay, copied route, enemy chorus | Audio and phrase family; deferred under movement-only combat. |
| WM23–WM24 | Hostile shove as escape; scout reveals the player's repeated assumption | Strong level-challenge candidates; avoid compulsory damage as the only escape. |

The later [MC01–MC04 constructions](../2026-10-11/MECHANIC-GENERATION-EXAMPLES.md) cover phrase-to-enemy rhythm, passage exchange, injury-drawn maze and a bounded event-to-effect item. MC02–MC04 may fit build customization; MC01 belongs with deferred audio. The [C01–C06 composition representatives](../2026-10-11/composition-study-001/REPORT.md) explore courier custody, cast-origin memory, authored knockback endpoints, a deferred shove, a strengthened boss charge and amended gate law. They remain paper proposals requiring individual feasibility and simpler-equivalent checks. The later [GF01–GF04 family](../../field-opening/2026-10-11/WORKED-FAMILY.md) varies the consequence of a carrier's arrival by destination, time, capacity and authorization; it is another candidate family, not current core content.

## 4. Suggested first playable effect set

Start with health/death, physical and magic damage, physical and magic defenses, movement speed, attack power and interval, a single-target attack, one radius-area attack, poison, slow, knockback, a finite shield, one retaliation effect, warned terrain and one clear auto-target rule. Add a bounded target-leap attack and scoped cooldown reduction as the next combat-model probe. Add walls only after automatic placement or movement-based creation proves legible. Add WM01 only after movement can meaningfully change its touch/wound/arrival outcome. This is a selection proposal for a prototype, not a completed balance decision.
