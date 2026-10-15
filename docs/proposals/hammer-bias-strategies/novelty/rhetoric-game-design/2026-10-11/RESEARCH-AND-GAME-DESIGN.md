# Rhetoric, contradiction and creative strategy: principles and game design

**Date:** 11 October 2026.  
**Status:** Primary-source research and proposed design; game implementation and gameplay studies have not been performed.  
**Research scope:** General principles of irony/sarcasm, creative reasoning and applicability across domains; strategies for generating game mechanics and for enabling players to construct strategies.  
**Confirmed frame:** Choose one character from a roster of three; survive three stages with a boss in each; acquire items during stages; use manual control or authored autoplay.  
**New research direction:** Irony, sarcasm, surprise, contradictions and indirection.  
**Package:** Eighteen academic references, seventeen game precedents, fourteen RT strategies, ten PR strategies, sixteen MG mechanic-generation strategies, a concrete game specification, twenty-four WM proposals and four further MC worked constructions. Goat Simulator investigates novelty in premise and experience; the principles module extends the inquiry beyond games.

## Reading path

For the general research question, start with [PRINCIPLES-AND-APPLICABILITY.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/PRINCIPLES-AND-APPLICABILITY.md). It distinguishes theories of ironic meaning, experimental creativity findings and proposed transfer, with eight principles and a domain applicability map. [PRINCIPLE-STRATEGIES.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/PRINCIPLE-STRATEGIES.md) provides ten general strategies and matched comparisons. These additions follow the completed game-design dialogue.

Start with the argument and evidence below, then read [GAME-DESIGN.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GAME-DESIGN.md) for the run and control contracts. [WILD-MECHANICS.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/WILD-MECHANICS.md) preserves the broader creative portfolio. [RHETORICAL-STRATEGIES.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/RHETORICAL-STRATEGIES.md) turns the directions into repeatable investigations. [GAME-PRECEDENTS.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GAME-PRECEDENTS.md) gives the comparison map; [SOURCES.json](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/SOURCES.json) records source scope and access depth. [DISTILL-RESULT.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/DISTILL-RESULT.md) records the actual bounded design conversation and reconciliation.

The [Goat Simulator case](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GOAT-SIMULATOR-CASE.md) adds a contrasting research direction: unexpected premise, ironic expectations and a different criterion for a valuable experience.

For generating mechanics, use [MECHANIC-GENERATION-STRATEGIES.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-STRATEGIES.md). Its sixteen generators produce rule proposals through reversal, failure residue, actor changes, contradictory effects, expressive inputs, grammar mutation and other transformations. [MECHANIC-GENERATION-EXAMPLES.md](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-EXAMPLES.md) works through four combinations into playable-rule sketches and comparison plans.

The previous [research report](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/RESEARCH-REPORT.md) remains the record of earlier experiments. This extension adds research and design; it contributes no new scored gameplay findings to those studies.

## 1. The proposed creative move

The game can make weaknesses into materials for strategy. A player can accept monster contact to finance retaliation while avoiding terrain hazards, build a corridor that also threatens their own escape, or let an enemy commit to a goal that can be redirected. The useful question is which causal relationship changes and what decision that makes possible.

That question concerns strategic novelty. The Goat Simulator addition supplies a second axis: whose expectation changes, and what experience becomes interesting or valuable? Familiar rules can support an unexpected purpose or tone. The two axes require separate comparisons; an unchanged optimal strategy does not settle an experience claim.

A promising identity is **build the circumstances in which an enemy's strength becomes useful to you**. This preserves the user's desire for careful planning, meaningful direct execution and unusual mechanics. It does not require every familiar effect to be new.

Some possible lines for that identity are:

- “Pick the flaw you want the monsters to pay for.”
- “Build a plan. Survive its consequences.”
- “Your weakness is the opening move.”
- “Make the monster finish your strategy.”

These are framing candidates. The mechanisms and player decisions below must carry their meaning; wording does not establish invention.

## 2. Academic grounding and its limits

The earlier [academic extension](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/academic-extension/2026-10-10/ACADEMIC-FOUNDATIONS.md) covers creative training, domain knowledge, recombination, incubation, constraints, evaluation and retained learning. This extension adds a narrower evidence map around expectation, rhetoric and game mechanisms.

| ID / reference | Supported contribution | Limit and proposed use |
|---|---|---|
| AR01 Huang, Gino & Galinsky (2015), *The highest form of intelligence*, OBHDP 131, 162–177. [Institution PDF](https://www.hbs.edu/ris/Publication%20Files/Huang%20Gino%20Galinsky%20OBHDP%202015_f4efb1e9-b842-4764-a292-ac4836c29cb2.pdf), DOI 10.1016/j.obhdp.2015.07.001. | Four reported studies connected sarcasm with creative-task performance; abstract thinking and interpersonal conflict were relevant, with trust moderating conflict. | Task-level results are not a universal creativity effect. Test sarcastic critique against equivalent literal critique, followed by the same constructive obligation. |
| AR02 Ritter et al. (2012), *Diversifying experiences enhance cognitive flexibility*, JESP 48(4), 961–964. [Institution PDF](https://pscresearch.faculty.ucdavis.edu/wp-content/uploads/sites/112/2014/09/Simonton-Diversifying-Experiences-Cognitive-Flexibility-2012.pdf), DOI 10.1016/j.jesp.2012.02.009. | Two experiments investigated active unusual experiences and cognitive flexibility. | Flexibility is not sufficient for valuable invention or durable learning. Use benign rule changes that the player can actively investigate. |
| AR03 McGraw & Warren (2010), *Benign Violations: Making Immoral Behavior Funny*. [Author PDF](https://leeds-faculty.colorado.edu/mcgrawp/pdf/mcgraw.warren.inpress.pdf), DOI 10.1177/0956797610376073. | Five experiments investigated humor around moral violations also appraised as benign. | This is a humor account, not a creativity law. Our inference: bend an understood convention while keeping the consequences legible and recoverable. |
| AR04 Grice (1975), *Logic and Conversation*, *Syntax and Semantics 3*, 41–58. [University copy](https://web.stanford.edu/class/psych205/papers/Grice-1975.pdf). | Conceptual context for conversational inference and the relationship between an utterance and its understood meaning. | Scanned chapter text was unavailable; indexed primary excerpts were inspected. No full-review or creativity-intervention claim. |
| AR05 Sperber & Wilson (1981), *Irony and the Use-Mention Distinction*, in *Radical Pragmatics*. [Author copy](https://www.dan.sperber.fr/wp-content/uploads/IronyAndTheUseMentionDistinction.pdf). | Bibliographic predecessor of the echoic interpretation account. | Scanned text was unavailable. Substantive interpretation here uses AR06, rather than claiming a full reading of AR05. |
| AR06 Wilson & Sperber (2012), *Explaining irony*, chapter 6 of *Meaning and Relevance*. [Author chapter](https://www.dan.sperber.fr/wp-content/uploads/WilsonSperber_ExplainingIrony.pdf). | Irony can express a stance toward an echoed expectation; it is not exhausted by asserting the opposite of a sentence. | A pragmatics account. Translating expectation into a game commitment is our design proposal, not the authors' finding. |
| AR07 Gocłowska et al. (2014), *Whether Social Schema Violations Help or Hurt Creativity Depends on Need for Structure*, PSPB 40(8), 959–971. [Publisher](https://journals.sagepub.com/doi/10.1177/0146167214533132), DOI 10.1177/0146167214533132. | In the reported tasks, schema inconsistency helped participants low in need for structure and impeded those high in it. | Primary abstract and institution metadata were inspected; full text was not reliably retrieved. Surprise should be scaffolded and tested, not assumed beneficial. |
| AR08 Hunicke, LeBlanc & Zubek (2004), *MDA: A Formal Approach to Game Design and Game Research*, AAAI WS-04-04. [Author/institution paper](https://www.cs.northwestern.edu/~hunicke/MDA.pdf). | Connects mechanics, resulting dynamics and desired experiences. | A design framework, not proof of fun. Predict the experience of a rule and test the actual consequence. |
| AR09 Sicart (2008), *Defining Game Mechanics*, *Game Studies* 8(2). [Original article](https://www.gamestudies.org/0802/articles/sicart). | Provides a way to analyze mechanics through agents' interactions with game state. | Conceptual vocabulary, not an efficacy trial. Specify verbs, affected states and rule conditions before claiming a new mechanic. |

This is a targeted reading, not a systematic review or replication assessment. Source publication dates are distinct from retrieval date. The ledger includes failed-access notes; access depth varies.

### 2.1 Principles and applicability beyond games

The user's clarification adds seven references, AR10–AR16, around pretense, salience, contextual interpretation, paradoxical frames, observed sarcasm and reading demands. The [principles module](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/PRINCIPLES-AND-APPLICABILITY.md) develops the argument; the source ledger records differing access depths. Nemeth et al., A17 from the earlier academic extension, is reused rather than counted again.

| ID / reference | Contribution to the expanded question | Access and claim boundary |
|---|---|---|
| AR10 Clark & Gerrig (1984), *On the pretense theory of irony*. [Author/institution PDF](https://web.stanford.edu/~clark/1980s/Clark%2C%20H.H.%20_%20Gerrig%2C%20R.J.%20_On%20the%20pretense%20theory%20of%20irony_%201984.pdf). | A competing account of the ironic act and performed speaking position. | Indexed primary abstract; full targeted fetch intermittent. Theory, not a role-method trial. |
| AR11 Giora (1997), *Understanding figurative and literal language: The graded salience hypothesis*. [Author PDF](https://www.tau.ac.il/~giorar/files/Giora1997_Graded_salience_hypothesis.pdf). | Meaning accessibility and familiarity. | Indexed primary abstract/opening; full fetch failed. No creative-training finding. |
| AR12 Pexman (2008), *It's Fascinating Research*. [Original journal](https://journals.sagepub.com/doi/10.1111/j.1467-8721.2008.00591.x). | A model for integrating cues to ironic meaning. | Abstract/opening depth; a review/model rather than a creativity experiment. |
| AR13 Miron-Spektor, Gino & Argote (2011), *Paradoxical frames and creative sparks*. [Original journal](https://www.sciencedirect.com/science/article/pii/S0749597811000471). | Conflicting task demands and creative performance. | Indexed abstract/introduction; no full method appraisal. |
| AR14 Miron-Spektor et al. (2011), *Others' anger makes people work harder not smarter*. [Author abstract](https://pubmed.ncbi.nlm.nih.gov/21574675/). | Observing anger versus sarcastic anger in problem-solving tasks. | Complete primary abstract retrieved through NLM; third-party task findings. |
| AR15 Ivanko & Pexman (2003), *Context Incongruity and Irony Processing*. [Original abstract](https://www.tandfonline.com/doi/abs/10.1207/S15326950DP3503_2). | Context-sensitive ironic/literal comprehension. | Indexed abstract; reading time is not creative benefit. |
| AR16 Zou et al. (2026), *Context and working memory capacity affect the processing of written irony in chinese*. [Original article](https://link.springer.com/article/10.1007/s00426-026-02258-w). | Context and reader-related variation in Chinese reading. | Selected methods/results; capacity groups were not randomly assigned. |

The resulting proposition is conditional: expectation contrast, representation of beliefs, abstraction and scoped integration can be investigated as general reasoning operations. Their benefit should be compared with equally informed literal analysis. Sarcastic delivery is optional; the effects of wording, constructive steps, interpretation and social response must remain distinguishable.

### 2.2 Research on generating mechanics

Two further primary references address mechanic generation directly. They bring this dated register to eighteen; this does not change the separate earlier register of twenty-six.

| ID / reference | Contribution | Access and limit |
|---|---|---|
| AR17 Cook, Colton, Raad & Gow (2013), *Mechanic Miner: Reflection-Driven Game Mechanic Discovery and Level Design*. [Primary paper](https://soundandcomplete.org/papers/EVO2013/MechanicMiner-EvoGames-2013.pdf). | Restricted mechanic search, simulated usefulness and associated level generation. | Selected generation/evaluation/pilot passages; usefulness does not establish fun or originality. |
| AR18 Zook & Riedl, *Automatic Game Design via Mechanic Generation*, inspected 2019 arXiv version. [Primary preprint](https://arxiv.org/abs/1908.01420). | Composable action representations, constrained generation and modeled playability checks. | Abstract and selected formalization/generation passages; no local solver run or player validation. |

The sixteen MG strategies are our prepared authoring adaptations. These papers establish prior approaches, rather than the effectiveness of this catalog.

## 3. What may enable novelty to emerge

The combined research supports a practical hypothesis, rather than a universal list of necessary and sufficient ingredients. Creative work needs enough domain understanding to notice a meaningful deviation; room to vary an assumption; a representation in which the variation can be constructed; and feedback that can distinguish a useful operation from an attractive sentence.

For this game, the proposed ingredients are:

| Ingredient | Concrete provision | Failure signal |
|---|---|---|
| Understandable causal vocabulary | Damage sources, guard, movement, terrain and enemy commitments have stable meanings. | Players cannot explain why a build worked or failed. |
| Productive tension | A safe route loses contact income; a maze also constrains escape; a song attracts listeners. | One choice dominates without a context-dependent cost. |
| Space for construction | Author movement, priorities, resource reserves, item ranks and a recovery plan. | Only designer-prescribed builds can succeed. |
| Bounded disruption | Counter one enabling assumption with advance information and reachable responses. | Surprise feels arbitrary or requires undisclosed information. |
| Consequence feedback | Replay identifies the fired rule, physical event, resource cost and commitment outcome. | The player blames randomness because the causal sequence is unreadable. |
| Revision and practice | Paused acquisition and stage transitions allow informed edits. | Players repeat failure without a meaningful available adjustment. |
| Selection with preserved alternatives | Keep distinct routes until their costs and counters can be inspected. | Early critique collapses every idea to a standard damage build. |
| Transfer assessment | Later unseen encounters test unaided strategy construction. | Improved current-run performance is mistaken for learned creativity. |

These are design inferences to investigate. The academic sources do not establish that this particular game trains creativity. Immediate novel output, enjoyment, win rate and retained learning require separate measures.

## 4. Rhetoric as an operation

**Irony** exposes the gap between an expectation and an outcome. In analysis, preserve whose expectation it was and what failed. In the game, an enemy can visibly commit to touching the hero, wounding the hero or reaching a seal; a player's response can defeat one objective while fulfilling another.

**Sarcasm** can make an assumption conspicuous. The constructive continuation is mandatory: translate the jab into a literal objection, retain useful residue, then build a response. A wall that “protects everyone, including the attackers” prompts the question of whom the wall is actually protecting. Sarcasm directed at people may create conflict; trust and consent in human collaboration matter.

**Surprise** requires a prior expectation. Record a prediction, show a bounded violation, then ask whether a useful new prediction follows. A louder effect or random death supplies surprise without necessarily supplying a new strategy.

**Contradictions** are treated as design tensions with scoped resolutions. A passage can close after the hero crosses; protection can depend on facing; the same block can prevent a wound while still allowing contact. This does not license an invalid logical inference that a proposition and its negation are both true under identical conditions.

**Indirection** changes the route by which a goal is achieved. Influence enemy targeting, movement, attention, topology or timing instead of only increasing damage. The player must be able to observe and act on the intermediary.

The [fourteen strategy cards](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/RHETORICAL-STRATEGIES.md) give triggers, construction steps, controls and defeating observations. They are reusable preparations beyond this single game case; application and benefit remain to be tested in each new context.

The later [ten principle-derived strategies](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/PRINCIPLE-STRATEGIES.md) develop general expectation attribution, interpretation pairs, tone removal, abstraction, contradiction partitioning, metric inspection and constructive handoffs. These are prepared adaptations, with acknowledged overlap with existing methods. They carry no new experimental findings.

## 5. Existing games and the plausible opportunity

The [seventeen-game map](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GAME-PRECEDENTS.md) establishes precedents for most ingredients and adds one contrasting experience case. Maze construction is familiar; authored behavior is familiar; action combined with planning is familiar. Voice input and rhythm-dependent combat power are also familiar. Component novelty cannot be assumed from a new combination.

The proposed opportunity is the relationship among those ingredients: one vulnerable character executes an authored strategy; manual control can exploit its windows; enemy commitments reveal what the plan must defeat; later stages pressure the plan's explicit assumptions. The closest comparisons differ by the decision they give the player, not merely their genre labels.

No mechanic is certified completely new. “The reviewed description does not establish this exact operation” is an open research finding, not proof of worldwide absence. Even a locally distinct mechanism may be less understandable or enjoyable than its familiar equivalent.

### 5.1 Goat Simulator and novelty in the value criterion

The user supplied *Goat Simulator* as an example of unexpected attention. The [case study](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GOAT-SIMULATOR-CASE.md) records official product claims and two attributed developer accounts, then separates that history from our interpretations. It investigates premise inversion, recoverable failure, expressive consequences and social retelling. This is an addition to the research frame; the earlier design dialogue was already complete when this case was added.

The practical transfer is to test what a surprising purpose adds to the same strategic rules, then test whether its appeal survives familiarity. Six case-derived prompts and four proposed comparisons are saved in the case study. They do not change the RT/WM catalog counts or establish six new mechanics. The game still needs legible rules, meaningful planning and warned lethal hazards.

## 6. The proposed game

The selected direction is a strategy survival roguelite with one character per run and two command sources. Choose Bastion for guarded contact and retaliation, Mason for temporary geometry and routing, or Veil for mobile magic and poison. Each has an exposed weakness. Survive a Foundry, a Marsh and a Court, each with its own boss. Items and skill choices arrive during the run and permit bounded plan revision.

Manual execution uses positioning, facing, dodge/guard windows, recovery and resource commitment. Autoplay executes a policy the player authored, including a deliberate risk and a recovery condition. It is not an omniscient optimizer that invents the plan on the player's behalf. Core world and action costs remain shared; equal rules do not promise equal difficulty or outcomes.

The proposed unusual core is a scarce **commitment response**. Bind a stronger enemy attack to an announced goal. Gain a capped payoff only if that particular goal fails while the hero survives the resolution. A blocked touch and a blocked wound differ; intercepting a charge can prevent arrival while still taking a hit. The payoff is contingent and costs a resource upfront.

That contract can be implemented as a conventional conditional reward keyed to the displayed objective. The design therefore claims a possible distinction only against named goal-independent controls and includes a commitment-removal comparison. If player choices and feasible policies are unchanged against those controls, describe it as expressive presentation or a conventional effect combination. No special exemption from ordinary programmed rules is claimed.

The [design specification](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/GAME-DESIGN.md) closes rule ordering, policy authorship, acquisition, lethal warnings, build counters and starting scope. The [twenty-four-mechanic portfolio](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/WILD-MECHANICS.md) keeps singing, silence, enemy memory, timing, topology and risky enemy empowerment available for separate probes.

## 7. Research procedure and proposed experiments

Actual work in this extension consists of source research, two design tracks and a bounded Proposer/Balancer dialogue followed by parent reconciliation. The [Distill result](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/DISTILL-RESULT.md) distinguishes that record from future studies. Canonical Robot Talks was not run; its cross-layer investigation remains a possible route if policy authoring, combat timing and audio sensing later produce unresolved contradictions.

For the analysis strategies, use matched literal analysis, operator-plus-literal-reconstruction and rhetoric-only conditions on frozen cases. Match information and output budget. Assess valid construction, actual operator application, causal difference, preserved obligations and a discriminating probe independently.

For gameplay, prepare these comparisons before implementing balance:

| Question | Matched comparison | Primary observation |
|---|---|---|
| Does authored preparation matter? | Same hero, build and initial seed: authored policy vs fixed behavior. | A changed viable plan and its costs, not just extra automation. |
| Does manual execution matter within strategy? | Same world/build, with human or policy commands; log mode separately. | Timing/positioning changes outcomes without hidden stat bonuses. |
| Is the commitment mechanic causally distinct? | Full goal-bound rule vs matched ordinary proc vs costs/empowerment retained without binding. | A different public objective changes a rational response or viable policy. |
| Are counters fair? | Assumption-specific counter vs blanket immunity or numerical difficulty increase. | Available adaptations, warning comprehension and perceived responsibility. |
| Does voice add expressive strategy? | Calibrated voice vs equivalent timing input vs a plain damage multiplier. | Tactical choice, detection reliability, fatigue and perceived agency. |
| Does surprise support model revision? | Predicted rule change vs equally salient random presentation. | A useful next prediction and transfer to a changed encounter. |
| Does practice teach creative strategy? | Practice plus delayed unaided unseen tasks vs equal-time domain instruction/control. | Retention and transfer; current assisted success is insufficient. |
| Does an unexpected premise change the experience? | Identical strategic rules under sober or absurd framing, with repeated sessions. | Prior expectation, comprehension, enjoyment and sustained interest; decision novelty is measured separately. |

A reused initial seed is only one control: divergence in actions can also change when random draws occur. Use separate encounter/hazard/item random streams and log draws where branch-sensitive comparisons require them. Paired repetitions need held-out seeds and counterbalanced order. No sample size, effect size or power result is claimed; a later pilot must inform an appropriate study.

Track invalid builds, policy expressiveness failures, unreadable warnings and missing observations separately from defeats. Keep no-opening and equivalence outcomes. Measure enjoyment and novelty separately: an original operation can be tedious.

## 8. What is decided and what remains open

Decided by the user: contradictions; three-character roster with one deployed; three stages and three bosses; manual or automatic play; builds, movement, acquisitions, status effects, hazards, counters and room for wild mechanics.

Proposed here: top-down arenas; temporary progression; a small ordered-rule editor; one public bindable commitment at a time; the three hero identities; staged counterpressure; a finite first content slice. These remain revisable design choices.

Prepared and saved: this research map, the additional strategies, game precedents, causal contracts, broader mechanic portfolio, actual design trace and descriptive dispatch route. Unknown: implementation feasibility, input feel, fun, balance, accessible voice sensing, advantage over simpler designs, human learning and worldwide originality.

Two prepared directions can proceed independently: compare the mechanic-generation methods on new design prompts, or prototype a selected mechanic within the three-stage expedition and test its play. Singing and the wider portfolio remain explicit expansion candidates. The selected frame expires if control cadence feels poor, the editor cannot express deliberate risk and recovery, the commitment mechanism proves equivalent, or the user changes deployment or run structure.

## 9. Strategies for generating new game mechanics

The game serves two creative purposes. The designer needs ways to invent rules; the player needs rules that permit constructing strategies. The [sixteen MG generators](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-STRATEGIES.md) make the first purpose explicit. Each starts from a seed, changes a causal relation, constructs a rule with a cost and feedback, and names a comparison that could show ordinary equivalence. Irony, indirection and destructive-to-creative attack become inputs to construction.

The [four worked compositions](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-EXAMPLES.md) demonstrate the process: a phrase governs a future enemy combo; a barricade opens a linked passage; injury locations form temporary geometry; and an item lets the player bind a source event to an effect. Their costs, feedback, manual/auto demands, counters and ordinary equivalents are written out. They add four authored candidates alongside the existing twenty-four WM proposals.

The reusable sequence is **desired decision or experience → seed and obligations → generator variants → composition → rule/cost/feedback → discriminating encounter → comparison and revision**. Keep the method's benefit separate from the mechanic's appeal. A generator can produce coherent ideas without outperforming ordinary ideation; a familiar combination can still create an interesting experience.

The [construction record](/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/rhetoric-game-design/2026-10-11/MECHANIC-GENERATION-TRACE.json) is parent-authored documentation, with no new agents, simulations or playtests. Two lanes, Distill and applicable Robot Talks remain possible future compositions; this addition does not claim their execution.
