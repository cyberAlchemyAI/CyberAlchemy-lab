# Proposer R1 — complete-run tactics and causal rhetoric

Status: design hypothesis; round 1 of exactly 3, Deep, two tracks. No gameplay experiment, implementation, literature search, playability result, or worldwide-novelty claim is implied.

## Evidence and constraints lane

Confirmed frame: choose one hero from a roster of three; that hero survives three stages, each ending with a boss. Find items during stages; gain XP and choose skills. Manual or autoplay must obey the same world rules. Manual execution should matter inside the chosen strategy; auto should reward authored preparation. Preserve damage reduction, magic, poison, slow, knockback, movement patterns, harmful random map events, and potentially lethal hazards. Preserve reflect-contact and maze-funnel builds and later encounters that expose their assumptions. Singing quality changing damage is a legitimate optional branch.

Unconfirmed: viewpoint, platform, movement precision, persistence across runs, run duration, acceptable authoring language, and sound sensing. For this proposal assume a compact arena with continuous movement, visible attacks, no permanent progression, and a readable rule editor. These assumptions permit design closure; they establish no usability knowledge.

Claims: C1, a complete three-stage run is the minimum unit carrying adaptation. C2, one shared simulation with different command sources can retain both authored preparation and manual skill. C3, rhetoric can change causal dependencies rather than rename buffs. All are hypotheses. Novelty means a different decision or dependency against a simpler candidate here; originality against all games is unknown.

## Generative construction lane: shared contract

Every command consumes the same resources and passes the same checks: move, dodge, guard, strike, cast, place, and use item. Recovery, stamina, geometry, damage categories, status buildup, and telegraphs are shared. Auto emits these commands through ordered conditions plus a fallback; manual emits them directly and can benefit from an authored movement guide. Auto has no hidden dodge, resource refund, privileged prediction, or stronger damage. Both see the same warning information.

Authoring is a bounded program: up to six ordered rules, explicit distance/health/telegraph predicates, action, and fallback. Examples: “avoid hazard polygon; hold ground when melee contact approaches; guard if stamina exceeds reserve” and “place barrier at choke; retreat along marked loop; knock back only inside choke.” A route is a sequence of waypoints with named exceptions, not pixel-perfect coordinates. Manual players decide timings and local deviations; their build still constrains successful execution. Auto players can revise rules at item/XP pauses and stage transitions.

Random events select a visible location and warning, then activate: poison rain, sweeping magic, collapsing floor. A possible instant-kill collapse has a committed timer, an unmistakable zone, and reachable exits when announced. Generation must reject unavoidable placements given the hero's current movement capacity. Randomness chooses the problem; warnings permit a response. Enemy body contact remains separately classified from hazards.

## Three heroes: strengths with costs

| Hero | Concrete advantage | Cost and counterpressure |
| --- | --- | --- |
| Bastion, the hospitable martyr | Guard converts capped monster-contact damage into stored retaliation; high reduction; short-range knockback | Contact spends stamina, storage expires, hazards bypass this mechanism; repeated heavy blows break guard. Ranged enemies force approach; manual timing can preserve stamina. |
| Mason, the malicious host | Three temporary barriers, poison on routed crossings, slow and knockback; can create a maze | Low durability, placement recovery, finite wall lifetime. Walls must retain an exit route; burrowers and visibly destructible walls require a second route rather than invalidating the whole build. |
| Veil, the unreliable cantor | Magic, movement feints, quick dodge, delayed poison mark; can attack while repositioning | Low health, cast recovery, weak sustained damage. Repeated identical escapes become predictable; attack-channel diversity costs resources. Sound later can add expressiveness without replacing baseline commands. |

XP offers one of two branches per hero: Bastion sustains contact or releases burst retaliation; Mason strengthens routing or converts walls to delayed magic; Veil deepens poison or diversifies magic. Mid-stage items allow local revision: hazard boots, contact mirror, temporary-wall spool, antidote, and a rhetoric catalyst. These are a small test vocabulary; effects alone are not the proposed invention.

## Track A — authored tactics plus demanding execution

Layer map: **purpose** survival through adaptive strategy → **capability** compose and execute a build → **workflow** three-stage run → **rule/interface** conditions, commands, encounters → **artifact** run specification. Candidate smallest coherent unit A: three heroes, one deployed, both modes, three encounters and bosses, items and XP pauses, two contrasting build routes.

Stage 1 teaches separations: ordinary contact, one warned hazard, melee boss with a guardable strike and a dodgeable heavy windup. Reflect works; a short maze funnels pursuers. Stage 2 adds a ranged boss that switches between a visible projectile lane and announced wall-breaking charge. Reflect must close distance or diversify; Mason must reroute rather than merely extend a maze. Stage 3 combines a hazard sweep with a boss alternating pursuit and an announced leap. Contact retaliation remains effective during pursuit; walls still redirect adds and influence the landing approach. No blanket immunity cancels the investment.

Decision signature: a Bastion player trades safe hazard avoidance against deliberate contact exposure; a Mason player chooses where geometry buys time and where it traps their own escape; Veil chooses damage windows versus maintaining an unpredictable route. Manual skill improves these timings. Auto success depends on reserve thresholds, escape exceptions, fallback rules, and mid-run revisions.

## Track B — public commitments change consequences

Use Track A's run closure but add one shared, finite **witness rule**. Enemies announce a target, action, and success condition before commitment; a visible token records that expectation. A rhetoric catalyst can bind one response to that token. Each token resolves once, expires with the attack, and cannot bind a second catalyst. No free-text meaning judge is required.

Three proposed operations:

1. **Irony/contradiction:** bind “your blow protects me.” If the announced blow physically hits while guard remains intact, its prevented damage becomes a temporary shield; if it misses, guard breaks, or a hazard hits instead, no shield forms and the catalyst is spent. Bastion can deliberately invite an accurate strike while preserving an exit. It changes the value of getting hit, not just reduction percentage.
2. **Sarcasm:** bind “an impeccable charge.” The enemy receives a real speed increase and commits its lane earlier. If that charge collides with a player-created obstruction, its failed announced arrival releases a capped shockwave into nearby enemies; if it reaches its target, the player faces the stronger attack. Mason chooses whether to empower a foe, where to redirect it, and whether sacrificing a wall is worth the burst. The trigger is observable failure of the particular claim, not generic “sarcasm damage.”
3. **Indirection/surprise:** bind an echo to a visible anchor rather than the enemy. The next attack through that anchor releases its stored magic toward the token's target. The opponent's visible last successful response predicts the echo path; using a different anchor or attack channel defeats that response once. Veil can deliberately teach a pattern and then break it, but repeats receive the same counter again. Anchor travel and arrival time remain visible, so repositioning can foil the echo.

These are world operations any hero may acquire; hero affinities reduce different costs. Bosses use the same witness checks. Their counterplay changes promises, destroys an exposed anchor, telegraphs an obstruction-breaking charge, or delays a blow until a shield window expires. A boss can defeat a setup through a legible action, not semantic exemption.

Sound expansion: pitch accuracy and sustained timing within a displayed phrase could scale an echo's stored magic, with loudness capped out of scoring. A button-timing equivalent supplies the same bounded score to auto and to players using no microphone. This remains a separable input study: the core run does not depend on speech recognition, aesthetic judgments, or singing well. Removing it must not delete rhetoric causality.

## Closure, recomposition, and risks

Inputs: chosen hero, initial build/rules, stage seed, commands, item/XP decisions. Outputs: survival or death, three boss outcomes, acquired build, and visible resolutions explaining consequence. Responsibility: deliver one complete adaptive survival arc. Named coordination: simulation validates commands; encounter schedule emits warnings/tokens; effects resolve once; progression supplies choices; command source selects actions. Splitting down to one boss loses adaptation; a combat sandbox loses the run; an effect list loses strategy. Sound can split cleanly because it supplies one bounded input value.

A reconstructs the upper capability through encounters that pressure authored assumptions. B reconstructs it through the same encounters plus witnessed commitment resolutions. Larger content can add encounter patterns, item combinations, and sound inputs through these named boundaries; defer procedural language interpretation, open-ended programming, multiplayer, permanent progression, and campaign content.

Five premortem risks: (1) auto editor burden overwhelms play—cap predicates and show which rule fired; (2) manual dominates every situation—separate timing skill from strategy quality when later validating; (3) rhetoric is decorative—reject operations whose optimal decisions match ordinary buffs; (4) counterpressure erases builds—require each boss to preserve a useful window for each hero; (5) warnings become impossible after geometry changes—validate current reachable escapes and cancel invalid hazard placements.

Cycle guard: exactly three rounds; retire renamed splits without new dependency or closure evidence. Preserve full-run minimum. A round may refine operations, not accumulate rhetorical labels. Current readiness: **flag**, pending Balancer critique. Frame expires if the user requires party deployment, audio-only play, or a substantially different run structure. Next: critique causal triggers, authoring burden, encounter fairness, and smallest-unit completeness; route the reconciled result to invoke design, with sound research separately deferred.
