# Four worked constructions from mechanic-generation strategies

**Date:** 11 October 2026. **Candidates:** MC01–MC04.  
**Status:** Authored demonstrations of composing generators. No code, simulator, solver, audio input or playtest was used. Numerical values are provisional prototype parameters.  
**Method catalog:** [MG01–MG16](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-STRATEGIES.md).  
**Structured record:** [MECHANIC-GENERATION-TRACE.json](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-TRACE.json).

These candidates add to the research portfolio without rewriting the starting game specification or its twenty-four WM proposals. They illustrate a repeatable construction process; they do not establish that the process generates more original or enjoyable results than ordinary design.

## MC01 — Your song becomes the enemy's next rhythm

**Seed:** The user's idea that singing quality changes damage, plus the existing WM18/WM21 sound candidates.

**Composition:** MG10 expressive input → MG05 coupled liability → MG08 visible opponent expectation.

**Construction:** Instead of changing only damage, make the performed phrase govern a declared part of the next encounter. The enemy repeats its timing, so a powerful phrase also authors a threat the player must survive.

**Rule sketch:** The player chooses one of three reference tempos and performs a three-beat phrase while spending a charge and committing to the cast. Relative pitch/rhythm conformity determines a capped burst within that tempo's damage band. Successful completion commits one upcoming three-hit enemy combo to the chosen tempo's displayed intervals. The fast band offers greater burst power and shorter later intervals; the slow band offers lower burst power and longer intervals. The combo has an ordinary advance warning and expiration; the player cannot rewrite an attack already in progress.

**Observation and cost:** Show the reference, measured conformity, charge expenditure and pending combo intervals. An interrupted phrase spends its charge without changing the enemy pattern. Sensing uncertainty rejects the input at admission before spending; it must not secretly create an arbitrary combo. Each enemy can hold one pending phrase-derived pattern.

**Authored challenge:** A slow first phrase allows a retreat through two openings; a fast phrase may finish an add before the boss closes in. The later combo must still have a feasible warned response. This is an encounter proposal, not a demonstrated solution.

**Manual and auto:** Manual play performs the phrase or equivalent timing controls and executes the ensuing dodge/guard sequence. Full-auto selects tempo, timing, charge reserve and an escape rule; it does not simulate a person's singing errors. Control reliability and tactical authorship need separate tests.

**Counter and repair:** An announced boss variant ignores phrase control on one marked attack category. Keep its eligible categories visible and useful, rather than canceling the entire investment. A second phrase cannot overwrite a pending pattern to farm slowdowns.

**Comparison:** Match burst power against an ordinary rhythm buff; match enemy intervals against a separately selected tempo debuff. Inspect whether the coupling changes a useful plan. Compare the new timing dependence with WM18's damage/detection and WM21's copied hazard path. It may be a familiar combination with a distinct arrangement; prior-art search remains open.

## MC02 — Every barricade opens another passage

**Seed:** Mason's maze and finite temporary walls.

**Composition:** MG02 ironic promise → MG06 spatial contradiction → MG09 topology exchange.

**Construction:** Make “more walls means more safety” fail in a playable, controllable way. Spend passage capacity instead of receiving an isolated obstacle.

**Rule sketch:** A level contains disclosed socket pairs: an initially open cell A and a closed gate B. Activating a pair spends wall capacity, blocks A and opens B for twelve seconds. Only one pair is active in the first prototype. The player chooses which disclosed pair to activate; arbitrary destruction of sealed terrain is not implied.

**State closure:** Admission requires A to be vacant and the new arrangement to preserve currently committed hazard escapes. On expiry, A reopens. B closes when vacant; while occupied, it remains visibly pending-close and the pair's capacity remains occupied. This prevents unexplained displacement and makes holding B a positional commitment. A pending-close pair cannot be reactivated for a free reset.

**Authored challenge:** Closing a short melee route opens a side approach for ranged enemies. The player can choose where the new threat arrives and prepare retaliation or poison there. Remaining near B delays closure while exposing the hero to the enemies using it.

**Manual and auto:** Manual play times activation and movement through the changed geometry. Auto needs public pair states, remaining lifetime and explicit route/fallback commands. A rule such as “activate only while the authored alternate remains available” must be expressible; a hidden route optimizer cannot make that choice for the player.

**Counter and repair:** A disclosed enemy uses the newly opened passage efficiently. Repair through pair selection, timing or item choice; do not invent a secret immunity. New lethal warnings must consider known expiry and occupancy rules when providing their required escape.

**Comparison:** Match a normal wall plus an independently controlled gate under the same capacity/time budget. Determine whether coupling the two adds a useful decision or only burdens the interface. Temporary gates and maze manipulation have strong existing overlap; this is a proposed passage-exchange arrangement.

## MC03 — Injuries draw a temporary maze

**Seed:** Damage reflection and movement patterns that deliberately accept enemy contact.

**Composition:** MG03 failure residue → MG09 resource-bearing geometry → MG14 counter/reconstruction.

**Construction:** Give the location of harm a future use, so deliberately accepting a hit can become a construction action. The hero still pays health and exposure.

**Rule sketch:** Eligible direct hostile hits record the hero's position. Two consecutive distinct marks can create a temporary ink segment, up to four map units long, lasting eight seconds. At most three marks and two segments are retained; older ones expire. Segments block disclosed ground-enemy routing while admitting the hero. An eligible segment forms only through vacant cells; an invalid segment produces no substitute damage or refund. Self, terrain, poison-tick and reflected damage do not create marks.

**Player choice:** Accept contact at a chosen location, then move before the next eligible hit to draw a useful segment. Alternatively avoid the health cost and use ordinary movement. A clear command erases the oldest segment without restoring health; it has normal recovery.

**Authored challenge:** One segment can redirect a pursuer toward a poisoned crossing, while a poorly placed segment diverts it away. The player needs at least two viable contact positions and a recovery path for this to be a construction problem.

**Manual and auto:** Manual execution controls spacing and the accepted hit. Auto requires visible mark positions, segment validity, health reserve and a deliberate-contact condition. These are proposed observation/editor additions; their usability in the existing six-rule editor has not been established.

**Counter and repair:** A disclosed flyer ignores ink. The next construction may use the ink to route grounded adds while timing a ranged attack on the flyer. If that leaves no useful operation, keep the failed idea as evidence rather than restoring it through an unexplained power.

**Comparison:** A health-paid placed barrier with identical dimensions, lifetime and routing properties. If choosing hit locations creates no extra viable decision, the mechanic is a different input to ordinary geometry. Compare also with the existing retaliation, wall and poison-path candidates; no absence claim is made.

## MC04 — An item lets you connect a cause to an effect

**Seed:** Mid-stage item selection and skill improvements.

**Composition:** MG15 typed grammar → MG04 action authorship → MG05 opportunity cost.

**Construction:** Give the player a bounded piece of mechanic authorship during a run. Instead of buying only a fixed effect, select a legal connection between an event and an effect.

**Rule sketch:** A paused item offer contains two eligible source events and two compatible effects. Example sources: a successful guard against a direct hostile melee hit, or completion of a named route segment. Example effects: open a selected disclosed gate for a short interval, or deliver a capped magic burst to a valid target. The player chooses one pair and its target binding. The first prototype permits one active coupling and three nonrenewable coupling charges per stage.

**State closure:** A source event spends at most one charge and triggers one effect, subject to a shared cooldown. The event is resolved once; coupling effects cannot create another eligible source event for the same coupling. A false condition, missing target or exhausted charge produces no effect or expenditure. Failed target checks are visible. Automatic gate closure uses explicit occupancy and hazard-escape rules rather than hidden displacement.

**Player choice:** A guard build can spend scarce triggers on escape access instead of damage. A route build may time a segment completion to create a burst window. Choosing one connection gives up the other; adding all connections would remove the item decision.

**Manual and auto:** Both modes choose the pair during the paused offer. Manual timing creates eligible events; auto must author the same guard or route action and reserve conditions. The coupling changes world effects, rather than merely adding a controller rule.

**Counter and repair:** A warned stage lacks the selected gate target or pressures the source action. Offer an affordable rebinding before commitment, or retain another valid target. If every target fails, the item is unavailable before spending. Keep ordinary useful builds available instead of forcing every player to use the grammar.

**Comparison:** Fixed event-linked items, independent upgrades and existing spell-combination precedents such as Noita. Match charges, cooldown and effects. Investigate whether selecting the cause/effect connection adds understandable authorship rather than only more menu work. The broad idea of composable effects has substantial prior art.

## What these examples demonstrate

The written process has produced four inspectable constructions: a phrase-to-enemy-timing relation, a passage exchange, damage-location geometry and an event/effect coupling item. Each has inputs, consequences, player alternatives and an equivalent to inspect.

That is evidence of authored candidate production. It does not measure generator superiority, independent role agreement, implementation feasibility, fun, successful strategy, learning or global novelty. A later comparison should preserve these drafts and prospectively define ordinary/component/composed methods before scoring new outputs.
