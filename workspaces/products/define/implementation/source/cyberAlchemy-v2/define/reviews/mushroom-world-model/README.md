# Mushroom World Model and Learning Control

Status: candidate research-project intake, pending scope confirmation.
Authority effect: none. Working title proposed by the assistant.
Research checked: 2026-09-18 (America/Sao_Paulo).

## Intent and desired outcome

Investigate whether a simulator of mushroom growth and farm signals can support
an ARE-equipped coding agent that develops and evaluates control code, and
whether the resulting tested behavior and knowledge can train reinforcement
learning policies for eventual mushroom-farm control.

The user explicitly clarified that “RLM” means **reinforcement-learning models**.
Use **RL** in this project to avoid confusion with recursive language models.
The user's answer about species, data, and equipment was “everything.” Broad
research coverage is the working interpretation; access to any particular
farm, species, dataset, or device has not been established.

This intake supports research discussion. It is not a completed Definition Pack:
no saved Define Session, formal sufficiency evaluator receipt, scope acceptance,
or construction handoff is claimed. See [intake.json](intake.json) for provenance
and [RESEARCH.md](RESEARCH.md) for the literature and research hypotheses.

## Candidate research question

Can an ARE-equipped agent produce tested controllers and useful training
experience that improve mushroom cultivation outcomes under a bounded compute
and response-time budget, relative to conventional control and the same agent
without ARE?

“Always produce the best code” is an aspiration, not a supported guarantee.
The proposed measurable meaning is **best observed eligible candidate on a
declared benchmark**, with independent tests, comparable compute budgets,
uncertainty, and explicit quality/resource tradeoffs. Benchmark success cannot
establish global optimality or transfer to all farms.

## Candidate domain language

These terms are local research proposals, not changes to canonical vocabulary.
The requesting user is the scope decision-maker; scientific and farm-operation
owners still need to be named.

| Concept | Disposition | Candidate meaning and boundary |
| --- | --- | --- |
| Mushroom world model | propose | An action-conditioned model predicting distributions over future crop and farm states for declared species, stages, equipment, and conditions. Predicting the next photograph alone is insufficient for control. |
| Farm state and observation | propose | State includes latent crop/substrate conditions; observations are timestamped, noisy measurements. A deployable policy receives available observations/history or estimated state, not hidden simulator truth. |
| ARE-equipped research agent | propose | A coding agent using ARE to manage selected context, decisions, evidence, and effect boundaries while proposing experiments. ARE is neither the biological simulator nor evidence that its code is optimal. |
| Control code | propose | A versioned executable mapping observations or state estimates to permitted actions or setpoints, with measurable resource use and response latency. Code generation is distinct from each control execution. |
| Knowledge produced | propose | Source-linked hypotheses, tested code, parameters, failures, counterexamples, and experiment records. Untested prose remains a hypothesis. |
| RL model | propose | A policy/value/world-model learning component improved using rewards and experience; user confirmed this intended family. Code and narrative are not, by themselves, a farm-control experience dataset. |
| Best code | open | Which outcomes, constraints, cost weights, and comparison budget define “best”? The user owns this decision before any winner is declared. |
| Minimum time granularity | open | Which quantity should be minimized: sensor interval, simulation step, action interval, decision latency, or controller-development time? Keep all five distinct until confirmed. |
| Everything | open | Research breadth is recorded; species coverage, lifecycle coverage, equipment inventory, data access, and practical exclusions need explicit bounds before implementation. |

Proposed relationships: actions change the farm; observations inform state
estimation; the world model predicts action consequences; controllers select
actions; experiments evaluate controller code; recorded trajectories support RL;
ARE evidence links support reproducibility and comparison.

## Consumers and scope

The immediate consumer is the requesting user choosing the research direction.
Later proposed consumers are simulation/control researchers, mushroom-domain
specialists, dataset maintainers, and farm operators; these roles are not yet
appointments or approvals.

The research scope covers biology, environmental dynamics, sensing, actuation,
code generation, control, RL training, transfer, and evaluation. Its evidence
currently concentrates on button, oyster, and king oyster mushrooms. Shiitake,
enoki, lion's mane, straw mushrooms, other cultivated species, and other signals
remain expansion targets, not supported coverage claims.

## Current result and checks

The literature supplies useful components, but this investigation does not
establish an integrated, validated, all-species farm world model. The main
evidence gap is synchronized action/environment/growth/harvest data across
independent crop cycles and farms.

Sources are linked rather than copied. Primary paper text, abstracts, repository
documentation, and dataset metadata were checked; access limitations are stated
in the research map. No paper results were reproduced, datasets downloaded,
simulator built, policy trained, or farm-control benefit measured.

Local checks cover JSON syntax, local links, required intake fields, and the
three-file write scope only. This does not clear the parent Define package's
documented validation blockers or constitute formal pack acceptance.

## Open Questions

1. Does the user accept the proposed research question and candidate terms?
2. Which species/strain, stage, and chamber will supply the first measured case,
   while preserving broad research coverage?
3. What real farms, historical records, sensor streams, and actuators are
   accessible? Who owns them and their interpretation?
4. Does “minimum time” prioritize inference latency, control frequency, or time
   to discover an improved controller?
5. How should yield, quality, time to harvest, energy, water, crop loss, and
   hardware wear be traded off? Which bounds are hard constraints?
6. What compute budget and target edge hardware should comparisons respect?
7. Are biological electrical signals specifically desired, or merely an
   optional research extension?

The user owns scope clarification; scientific and operational owners are open.
Unanswered questions do not block this literature intake. They do block claims
of complete scope, optimal control, or readiness for a real farm. Continue by
confirming/correcting this intake; any later Plan or Implement objective needs
its own repository route and applicable authorization.
