# Research map: mushroom simulation, coding agents, and RL control

Status: candidate evidence supporting [the project intake](README.md).
Authority effect: none. Checked 2026-09-18 (America/Sao_Paulo).
This is a targeted literature scan, not an exhaustive or systematic review.
Recommendations below are research hypotheses, not selected architecture or an
implementation plan. Open questions are owned by [README.md](README.md#open-questions).

## Most useful research

| Source | Evidence and relevance | Limit on reuse |
| --- | --- | --- |
| **Wachowicz and Woroncow, 2010: Comprehensive Model of Processes Proceeding at a Mushroom-Growing Cellar** — [primary paper](https://uwm.edu.pl/wnt/technicalsc/tech_13/B04.PDF) | Models heat, moisture, CO₂, substrate, ventilation, and conditioning equipment; compares simulation with measurements from a mushroom cellar. A concrete starting point for physical room dynamics. | Full-text narrative inspected; equations require separate transcription and dimensional checks before reuse. It does not establish a universal crop-growth model. |
| **Jung and Son, 2021: Carbon Dioxide Emission Modeling of King Oyster Mushroom before and after Thinning Processes According to Temperature and Growth Stage** — [primary paper](https://www.ksbec.org/articles/pdf/MYDd/phpf-2021-030-02-0.pdf) | Models respiration across temperature, growth stage, and thinning for P. eryngii; reports measured-versus-estimated emission R² = 0.71. Connects crop development to room CO₂ loading. | One cultivation context; transfer to other strains, substrates, or species needs new calibration. The paper's five-second gas measurements do not establish a five-second control interval. |
| **Responses of the Mushroom Pleurotus ostreatus under Different CO₂ Concentration by Comparative Proteomic Analyses, 2022** — [primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9321156/) | Experimental evidence connects CO₂ conditions with fruiting-body development and proteomic changes. Useful for asking what biological effects a climate-only simulator omits. | Does not supply a universal causal growth simulator or universal CO₂ setpoint. |
| **Energy-Saving Control Method for Factory Mushroom Room Air Conditioning Based on MPC, 2023** — [publisher](https://www.mdpi.com/1996-1073/16/22/7623) | Direct mushroom-domain precedent combining data-driven model predictive control (MPC) with PID. High-priority baseline literature. | Publisher search excerpt verified; full page returned maintenance. No numerical performance claim adopted. |
| **DigiFungi: An education software for button mushrooms, SoftwareX 29, 2025** — [paper](https://doi.org/10.1016/j.softx.2024.101993), [authors' repository](https://github.com/SCT-lab/DigiFungi) | Educational cultivation simulation covering preparation, inoculation, growth, and quality feedback; useful for domain walkthroughs and visualization. Repository README inspected. | An educational game is not evidence of calibrated action-to-growth dynamics. Paper access was restricted; numerical fidelity and reuse permissions remain to be checked. |
| **Mallick et al., 2024/2025: Reinforcement Learning-based Model Predictive Control for Greenhouse Climate Control** — [paper](https://arxiv.org/abs/2409.12789) | RL adjusts a parameterized MPC scheme in the presence of prediction uncertainty; reports simulation improvements in constraint handling and crop performance. A strong method to investigate alongside direct learned policies. | Greenhouse simulation evidence, not a mushroom-farm deployment. Photosynthesis and plant CO₂ assumptions must not be imported into fungal biology. |
| **Hafner et al.: DreamerV3** — [research preprint](https://arxiv.org/abs/2301.04104), [2025 Nature publication](https://doi.org/10.1038/s41586-025-08744-2) | Learns a world model and improves policies using imagined trajectories across many benchmark tasks. Relevant to latent crop-state modeling and long-horizon decisions. | No mushroom validation. Learned imagination can amplify errors when the model is wrong; biological calibration remains necessary. |
| **Ma et al., ICLR 2024: Eureka** — [paper](https://arxiv.org/abs/2310.12931) | Uses LLM-written reward code, RL evaluation, and iterative improvement. Closest direct precedent for a coding agent producing artifacts that improve RL training. | Demonstrated in robotic benchmark environments, not farms. It generates reward code; it does not establish that arbitrary generated controllers are optimal or safe. |
| **Rusu et al., 2015/2016: Policy Distillation** — [paper](https://arxiv.org/abs/1511.06295) | Transfers teacher policy behavior into smaller networks and combines task-specific teachers. Relevant to turning expensive discovery into cheaper control inference. | Atari evidence. The project must measure the student's loss of performance and robustness on farm tasks. |
| **Ross et al., 2011: DAgger** — [paper](https://proceedings.mlr.press/v15/ross11a.html) | Addresses the distribution shift caused when an imitation learner visits states outside the demonstrations. Useful for generating corrective teacher examples in simulation. | Teacher availability and quality are assumptions. Hardware exploration does not follow from a successful simulation procedure. |
| **Kumar et al., 2020: Conservative Q-Learning** — [paper](https://arxiv.org/abs/2006.04779) | Offline RL addresses overestimated values for actions poorly represented in logged data. Relevant once farm behavior logs exist. | Cannot create evidence for actions missing from the dataset or guarantee farm safety. |
| **Yu et al., NeurIPS 2020: MOPO** — [paper](https://arxiv.org/abs/2005.13239) | Model-based offline RL penalizes uncertain model predictions during policy optimization. Relevant to limiting exploitation of unreliable simulated outcomes. | Uncertainty quality is itself an empirical question; the farm setting remains an extrapolation. |
| **Tobin et al., 2017: Domain Randomization** — [paper](https://arxiv.org/abs/1703.06907) | Varies simulated visual conditions to improve transfer to real-world perception. Supports testing diverse synthetic appearances. | The original evidence is visual robotics. Randomizing biological/actuator dynamics is a proposed extension here, not a result established by that paper. |
| **Heemels, Johansson, Tabuada, 2012: An introduction to event-triggered and self-triggered control** — [authors' institutional copy](https://kth.diva-portal.org/smash/get/diva2%3A586391/FULLTEXT02) | Framework for asking when new measurements/control updates are necessary rather than assuming a universal fixed rate. | Does not provide mushroom-specific timing values; control assumptions and stability conditions require their own analysis. |

The most direct reading sequence is the mushroom-cellar model, the king oyster
respiration study, mushroom MPC, RL–MPC, Eureka, then policy distillation.
Dreamer is valuable as a comparison candidate once the biological evaluation is
credible; it is not a prerequisite for the first useful simulator.

## What the world model would need to mean

Proposed conceptual decomposition:

| Component | Candidate state or behavior | Evidence needed |
| --- | --- | --- |
| Room and equipment | Air/substrate temperature, water vapor, condensation, CO₂, ventilation, heat transfer, actuator delays and saturation | Synchronized sensor readings, commands, actual actuator response, room geometry and calibration |
| Crop and substrate | Species/strain, substrate identity, available water/nutrients, colonization, respiration, fruit-body development, harvest flushes | Repeated crop cycles, growth observations, mass/quality/harvest labels and interventions |
| Observation | Sensor bias/noise/dropout, camera geometry, occlusion, missing values and timestamp delays | Calibration, independent references, spatial measurements and fault logs |
| Disturbances | Outdoor weather, door openings, loading, operator interventions and failures | Event logs and held-out disturbances |

A useful research candidate is a **hybrid model**: physical balances for the
room, species/stage-specific biological models, and learned residual dynamics
where data supports them. This is our synthesis of the sources, not a validated
integrated system. A digital twin additionally needs a declared real counterpart
and calibration/synchronization; a purely hypothetical simulator should not be
called a validated farm twin.

For “everything,” retain separate profiles for species, strain, substrate,
lifecycle stage, equipment, and site. Button, oyster, and king oyster provide
initial literature anchors. Broader species coverage needs separate primary
evidence; merely adding a species label cannot establish transfer. Whole-farm
coverage could include substrate preparation, incubation, fruiting, harvest,
cleaning, and storage, but each adds different dynamics and interventions.

## Fast control and slower code discovery

The timing objective contains five separate quantities:

1. **Simulation integration step:** numerical resolution needed for stable,
   sufficiently accurate dynamics.
2. **Sensor sampling interval:** measurement cadence justified by the actual
   sensor response and information content.
3. **Control interval:** when the deployed controller may change an action.
4. **Decision latency:** elapsed time from an available observation to a valid
   action, including computation and communication.
5. **Discovery time:** time/compute spent generating, testing, and selecting code.

Our candidate framing separates an expensive research loop from a bounded
execution loop. A coding agent could propose reward functions, estimators,
controller parameters, or controller code, then test them before inclusion.
A selected controller or distilled policy can execute repeatedly without
regenerating code at every sample.

Research should compare a range of control intervals and event-triggered
updates, keeping the simulated physical horizon, reward units, and discount
horizon comparable. Otherwise, changing the timestep changes the optimization
problem and can manufacture an apparent gain. Timing sweeps must respect
actuator response and cycling limits. No millisecond, second, or minute value is
endorsed here without hardware and system-identification evidence.

## Turning the agent's work into learning material

There are distinct outputs with distinct uses:

| Agent output | Possible learning use | Necessary qualification |
| --- | --- | --- |
| Executable controller | Teacher demonstrations or teacher action/value targets | Independently evaluated behavior |
| Reward code | RL training objective | Frozen external outcome measures prevent reward gaming |
| Simulator/model code | Synthetic trajectories and model-based learning | Calibration and held-out prediction checks |
| Experiment trajectories | Imitation learning, offline RL, world-model learning | Versioned observations, actions, timestamps, outcomes and provenance |
| Hypotheses and explanations | Experiment selection and a source-linked knowledge library | Distinguish tested claims, counterevidence, and untested suggestions |

A candidate experience record includes observation history or estimated state,
action, elapsed physical time, next observation, reward components, terminal
status, constraint violations, species/stage/substrate/site identifiers,
controller and simulator versions, seed, uncertainty, and whether data is real
or synthetic. If teachers access hidden simulator state, record that privilege
and prevent accidental leakage into deployment inputs.

Code and text can train a separate language/code model if that becomes a later
objective. For the farm RL policy, the central bridge is the **behavior and
measured consequences** generated by that code, not a folder of prose.

ARE's local CLI currently exposes route, context, effect, and continuation
decisions and explicitly does not execute proposals or invoke a model; see the
[local integration contract](../../../agent-routing/capabilities/are-cli/README.md).
Its proposed scientific role is traceability and experiment/context management.
Whether it improves discovery speed, controller quality, or reproducibility is
an experimental question. Compare the same coding model, tools, budget, and
task set with and without ARE; count ARE overhead in the cost and latency.

## Data that can help now

| Resource | Verified scope | Appropriate use and gap |
| --- | --- | --- |
| [M18K paper](https://arxiv.org/abs/2407.11275) and [authors' repository](https://github.com/abdollahzakeri/m18k) | Over 18,000 annotated mushroom instances in 423 RGB-D image pairs in the described release | Detection/segmentation research. It is not verified here as a synchronized action-to-harvest dataset. |
| [Pleurotus Mushroom Dataset](https://zenodo.org/records/15467287), v1.0.0, 2025 | Harvest categories plus growth photographs of 33 bags over seven days; collected in Greece in 2022 | Growth/harvest perception. Do not infer environmental or actuator trajectories from photographs alone. |
| [High-humidity psychrometer dataset](https://data.mendeley.com/datasets/3x2vvv8vrz/1), v1, 14 September 2026 | Metadata describes HTU21D calibration, psychrometer validation, and cultivation measurements; CC BY 4.0 listed | Candidate sensor-calibration evidence. Files and field completeness were not inspected, so control/RL suitability is unverified. |

Dataset metadata was checked; files were not downloaded or quality-audited.
The scan did not verify a complete, open, multi-species dataset joining commands,
actual actuator response, environment, growth, and harvest outcomes. This is a
search result limitation, not a claim that none exists.

The proposed farm-data requirement is repeated complete crop cycles with
calibrated measurements and logged interventions. Split by crop cycle, farm,
season, and where appropriate species; random adjacent-frame splits would
overstate independent generalization. Observational fit alone does not identify
the effect of changing a control action.

## Other signals: an optional scientific branch

[Detection of electrical signals in fungal mycelia in response to external
stimuli (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12483595/) reports
electrode-based experiments with stimulus and non-inoculated controls. It is
relevant if “other signals” includes fungal electrophysiology. Primary indexed
text was available; direct full-page access encountered a browser challenge.

Treat electrical signals as experimental measurements, not decoded fungal
language or established farm-state labels. A useful question is whether they
add predictive value beyond temperature, humidity, CO₂, images, and mass after
accounting for electrode drift, substrate moisture, and actuator interference.
The source does not establish mushroom-farm control benefit.

## Falsifiable research hypotheses

These frame later study selection; they are not an admitted execution schedule.

| Hypothesis | Comparison and possible falsifier |
| --- | --- |
| A hybrid world model predicts useful action consequences | Compare with persistence, a simple fitted model, and purely learned dynamics on held-out cycles and interventions. Reject added complexity if it fails to improve relevant predictive accuracy/calibration. |
| An ARE-equipped agent improves controller discovery | Compare fixed-budget coding-agent runs with/without ARE, fixed search/evaluation rules, multiple seeds, and unseen cases. No gain after overhead is evidence against the claim. |
| Agent-generated artifacts improve RL | Compare RL with human-designed rewards, agent-written rewards, and teacher demonstrations under the same budget. Evaluate harvest/resource outcomes independently of training reward. |
| A smaller student preserves teacher value | Compare quality, constraints, worst-case behavior, and measured tail latency on target hardware. Fast but materially worse control fails the proposition. |
| Finer time granularity is useful | Sweep control intervals with comparable physical objectives; report outcome gains against compute, communication, and actuator cycling. No meaningful gain falsifies “faster is better” in that range. |
| Behavior transfers beyond the training environment | Evaluate held-out parameters, equipment, cycles, and eventual real measurements. Simulator-only success cannot answer this claim. |

Candidate performance measures include marketable yield, quality grade, time to
harvest, energy and water per marketable mass, constraint-violation duration,
loss events, actuator cycling, prediction uncertainty, p95/p99 inference latency,
and cost/time to discover a passing candidate. Exact weights, limits, sample
sizes, and acceptance thresholds remain owner decisions.

A credible evaluation would retain scheduled/rule-based control, PID and MPC
as baselines. Protect the evaluator, held-out cases, and outcome definitions
from modification by the agent proposing code. Distinguish code correctness,
simulator validity, improved simulated control, and eventual farm transfer.
The proposed real-world sequence is observational comparison, hardware timing
checks, then a separately scoped supervised trial with an independent fallback
controller. No such trial or actuator access is authorized by this intake.

## Open Questions

See [the intake's question list](README.md#open-questions). In addition, source
follow-up should establish available mushroom MPC code/data, species-specific
growth parameters, simulator identifiability, dataset reuse terms, and whether
any verified action-conditioned crop-cycle dataset can reduce new data needs.
