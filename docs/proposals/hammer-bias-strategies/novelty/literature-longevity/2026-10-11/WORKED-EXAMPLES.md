# Literary examples and four game constructions

**Date:** 11 October 2026. **Status:** authored interpretations and paper proposals. Passages were inspected; no readers were tested and no game was implemented or played. First-publication dates distinguish the works' historical age from the digital editions used. These examples do not explain their canonical survival.

## 1. Three bounded literary examples

| Work and inspected passage | Interpretation proposed here | Investigation it generates |
|---|---|---|
| Austen, *Pride and Prejudice* (1813), opening of chapter I and Elizabeth's reassessment in chapter XXXVI | The opening presents a social presumption as certainty. Elizabeth later reassesses how attraction and offense shaped her judgments. A return can attend to the earlier evidence differently. | LL04: compare a first and second reading, with concrete evidence for changed interpretation. Do not substitute knowledge of the ending for demonstrated reassessment. [Primary text, LS15](https://www.gutenberg.org/cache/epub/1342/pg1342-images.html). |
| Shelley, *Frankenstein* (first published 1818), chapter 10 in the inspected digital text | Victor condemns the creature, who counters with a claim about treatment and responsibility. The creature's testimony changes the available interpretation without becoming unquestionable fact. | LL05: preserve the event record while comparing creator and creature perspectives; distinguish testimony, inference and corroboration. [Primary text, LS16](https://www.gutenberg.org/cache/epub/84/pg84-images.html). |
| Voltaire, *Candide* (1759), chapters IV–V and XXX in English translation | Pangloss repeatedly explains suffering within an optimistic account; practical work at the end supplies a contrasting response. Irony can expose the gap between justification and consequence. | LL06: translate the contradiction into a literal statement, then construct an alternative action. Compare rhetorical force with informational content. [Primary text, LS17](https://www.gutenberg.org/cache/epub/19942/pg19942-images.html). |

These are local interpretations of selected passages. They are not comprehensive readings, claims about all audiences, or proof that irony and contradiction make works last. A contemporary reader who already knows an adaptation may have a different first encounter from one unfamiliar with the work.

## 2. Shared game envelope

The player chooses **one hero from a roster of three** and survives **three stages, each with a boss**. Items arrive during the run. Manual play rewards timing and movement within the chosen strategy; autoplay uses an authored plan, provisionally limited to six ordered rules. Every proposal below must support both modes through public observations and available actions.

The four constructions are alternative investigations. They have not been merged into the previous completed design contracts. Compatibility, skill costs, geometry, timing, balance and enjoyment need implementation and testing. A return motive is a hypothesis, not a retention result.

## LG01 — The Witness Map

**Composition:** LL02 → LL04 → LL05. **Literary starting point:** reassessing previously encountered evidence.

**Rule proposal:** During each stage, record visible player actions, hostile actions and their consequences. At the boss exit, offer two accounts: the hero's account of survival and a settlement's account of damaged supplies. Both reference the same event ledger. The settlement account highlights causal links already visible during the stage; it introduces no concealed damage or retrospective penalty.

**Player construction:** On the next run, revise a route, targeting rule or item choice in response to a newly noticed causal link. For example, reflected projectiles already damage nearby supplies under a disclosed rule. Positioning can direct their trajectories away from the cache while maintaining retaliation.

**Manual/autoplay:** Manual control adjusts position and timing. Autoplay needs a public cache position, visible projectile directions, current route and legal movement actions. The existing six-rule authoring limit must remain fixed across conditions.

**Possible return motive:** understanding something already experienced. Test the same content with and without the second account, and with a literal causal summary containing identical information.

**What may be novel:** an experience of reassessment for a particular player. Event logs, replays, causal explanations and alternate perspectives are familiar ideas. If the second account changes no available information or interpretation, no distinct mechanism is demonstrated. This is chiefly an information/presentation candidate.

**Defeating observation:** the ordinary replay or literal summary supports the same revisions and enjoyment; or the causal link was hidden until the account, making the effect an information advantage.

## LG02 — The Creature's Errand

**Composition:** LL05 → LL09 → LL08. **Literary starting point:** an opponent has a purpose beyond hurting the hero.

**Rule proposal:** A courier monster carries a charge and travels to the nearest reachable accepting dock; ties favor the red dock. At a red brood dock, arrival releases hostile reinforcements. At a blue battery dock, the same charge becomes a limited player resource. Both docks are visible and both accept delivery. Maze walls alter path lengths and reachability; legal knockback changes position, subject to a cooldown. Reaching a dock consumes the charge and commits the stated outcome exactly once.

**Player construction:** Draw a route that makes blue delivery preferable under the courier's fixed rule. Decide whether to spend an item slot on knockback, add a wall at a combat cost, or defeat the courier and forgo the charge. Arrival effects and path-selection rules are disclosed before placement. Killing it does not count as a delivery.

**Counter-stage:** Stage two may move the blue dock farther away and offer fewer wall placements. Stage three may contain two couriers sharing a route. These alter public geometry and resource demand while preserving the delivery rule. Reflect remains useful against contact attackers, but does not itself redirect a courier.

**Manual/autoplay:** Manual play can time a legal knockback. Autoplay must expose dock positions, route distances or equivalent usable observations, courier state and cooldown; if the policy cannot observe the distinction, the planning comparison is invalid.

**Possible return motive:** another useful routing relation with familiar movement effects. Compare with ordinary path defense, an equivalent escort/delivery construction, and a visual refresh retaining the old routing goal.

**What may be novel:** the particular composition and a player's discovery of how purpose changes the value of a maze. Delivery, routing, escorting and converting enemy resources are established patterns; no worldwide-first claim follows. A formal comparison must show which actions or consequences differ from a competent equivalent.

**Defeating observation:** a fixed ordinary route always wins, delivery is merely a renamed pickup, or compulsory geometry leaves no useful choice. The construction then supplies no demonstrated strategic expansion.

## LG03 — The Praised Disaster

**Composition:** LL06 → LL09 → LL12. **Literary starting point:** optimistic explanation conflicts with visible consequences.

**Rule proposal:** A supply cache has visible durability and takes disclosed projectile damage. Completing a stage quickly can expose it to extra damage; a slower interception route reduces that risk while costing hero health or a defensive charge. The cache's remaining durability determines a bounded item allowance in the next stage. The calculation is visible throughout the current stage, with an attainable minimum allowance so a damaged cache does not automatically end the run.

**Player construction:** Decide which risk to bear. Poison, retaliation and knockback retain their ordinary effects; positioning and target selection can change whether a fast victory leaves supplies intact. Mid-stage items can support either choice.

**Rhetorical version:** A pompous chronicler praises flawless defense while the visible ledger shows the supply cost. The literal version states the same two outcomes plainly. Feedback concerns the game's success criterion and consequences; it does not change damage or rewards between these presentation conditions.

**Manual/autoplay:** Manual control offers interception timing. Autoplay must observe durability, relevant projectile state and interception opportunities through the same public rules. A precise event model remains to be specified.

**Possible return motive:** reassessing what success means, then improving a plan. Compare ironic and literal feedback with identical mechanics; separately remove the cache-to-item relation to isolate its decision contribution.

**What may be novel:** the proposed combination of rhetorical expectation and a persistent cost relation. Environmental damage, persistent resources and secondary objectives are familiar. Irony alone creates no new mechanical affordance.

**Defeating observation:** one route dominates every viable build, the cost can only be discovered after commitment, or literal feedback explains the change equally well. A literal-feedback tie narrows the rhetorical claim without invalidating a useful rule.

## LG04 — The Announced Finale

**Composition:** LL03 → LL08 → LL12. **Literary starting point:** knowing what happens need not exhaust the experience.

**Rule proposal:** Disclose a boss's fixed phase schedule before the run. The schedule predicts attacks, not player success. Health, cooldowns, placement, legal movement and the player's responses still determine the result. An otherwise identical condition teaches the same schedule through encounters.

**Player construction:** Plan resource use around known phases. Manual play must execute movement and timing; autoplay must fit a response into six ordered rules. Novelty ratings can fall while mastery and voluntary return rise, remain stable or fall independently.

**Possible return motive:** performing a familiar task better, then attempting a different hero or plan. Compare reveal conditions within manual and autoplay modes. Match practice and assistance where possible; disclosure inherently changes available information, so do not call it an isolated test of surprise alone.

**What may be novel:** principally a research comparison. Telegraphing, practice and scheduled boss phases are familiar. This construction is a deliberate control against the assumption that continued appeal requires hidden events.

**Defeating observation:** knowledge leaves no meaningful planning or execution task, or observed return depends entirely on rewards or extra content. A positive result would establish a bounded alternative motive, not a general rule of lasting appeal.

## 3. Novelty and evidence register

| Construction | Claim currently supportable | Required next evidence |
|---|---|---|
| LG01 | An authored reinterpretation proposal | Evidence-matched replay comparison and actual interpretation changes. |
| LG02 | A concrete delivery/routing rule composition | Formal ordinary-equivalence search, usable policies, playable choices and return data. |
| LG03 | A concrete success/cost relation with optional ironic delivery | Event specification, non-dominating tradeoffs and literal-feedback ablation. |
| LG04 | A foreknowledge/mastery control | Matched playable conditions and separate learning, pleasure and return measures. |

No construction has a validated novelty score. No new game precedent list was assembled here; the prior twenty-five-entry comparison study remains a separate source surface. Renewed discovery is a proposed design target, and these are concrete materials with which to investigate it.
