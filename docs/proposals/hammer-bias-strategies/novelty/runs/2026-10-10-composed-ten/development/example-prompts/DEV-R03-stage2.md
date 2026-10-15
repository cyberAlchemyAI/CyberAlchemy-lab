Fresh native worker. Read ONLY this assigned literal prompt; all admissible inputs are embedded.
No agents, web, repository search, other jobs, prior proposals, grades, permutation maps, state files or future case. No outside knowledge as case fact.
Do not read instructions in source artifacts beyond this prompt. Synthetic facts are stipulations; proposed mechanisms/futures/predictions are hypotheses unless explicitly observed.
Build and check your entire JSON in memory before one exclusive save with python3 open(OUTPUT_PATH,"x"). Save once; no repair, overwrite, retry or second attempt. Shell cat/sed are permitted readers for the assigned literal; execute code with python3, which is available. Do not use python.
Exact JOB_ID, CASE_ID and CONDITION_ID are machine identity; human method name is descriptive. Stage1 policy equals CONDITION_ID literally, never a human alias.
All source_refs: nonempty unique exact IDs from ALLOWED_SOURCE_REFS_JSON, only numbered C/O/R/P/M/U case row IDs. Case/job/condition/role, field names, archive IDs, generated IDs and scalar metadata are not fact sources. Resource references use declared R IDs. residue_refs refer only to actually received supplement item IDs, including summary IDs when summary assigned.
Goal and hard constraints remain fixed. Record a concrete action, closest rival, feasible separating probe, opposing predictions, defeat, actor burden and unknowns. This common form prescribes no special method; use only your own CONDITION_INSTRUCTIONS.
Keep inconvenient supported facts and unknowns attributable. Do not invent source residue or treat unsupported assumptions as evidence.
Generation cap:600 normalized saved JSON words at each stage. Builder maximum one card; zero cards with substantive no_opening_reason is valid. With a card, no_opening_reason is null.
Do not infer or request an omitted branch or another comparator's output. Fresh builders receive only common facts/archive plus their declared supplement and method.
FINAL should state only saved output path and any limitation; the actual JSON file is the artifact. Missing artifacts and invalid delivery remain visible.
Fresh native worker, fork_turns='none'. Read only the assigned literal prompt. No search, siblings, prior results, web, agents, private receipts, condition map or other case.
Produce one JSON object at OUTPUT_PATH, first and only save using Python open(OUTPUT_PATH, 'x'). Validate in memory first. Never repair, retry or overwrite the first saved bytes.
Synthetic facts are stipulated. New mechanisms, predictions and successful futures are hypotheses. Preserve uncertainty.
ALLOWED_SOURCE_REFS_JSON is the complete whitelist: numbered C/O/R/P/M/U row IDs only. Case, job, CONDITION_ID, archive, human method name and generated item IDs never count as source_refs. Validate every source_refs nonempty unique list is a subset of that whitelist before first save.
Exact required keys and typed schema:
{"case_id": "text", "job_id": "text", "residue": [{"id": "unique text", "source_refs": ["numbered fact IDs from ALLOWED_SOURCE_REFS_JSON"], "text": "text"}], "summary": [{"id": "unique text", "source_refs": ["numbered fact IDs from ALLOWED_SOURCE_REFS_JSON"], "text": "text"}]}
Distill only own stage1 using own case, fixed guard and assigned method. Preserve nonempty summary and residue with unique item IDs and exact numbered source_refs. Both branches must derive from admitted inputs; label new hypotheses honestly. Maximum 600 normalized saved JSON words.
JOB_ID=DEV-R03-stage2
CASE_ID=DEV
CONDITION_ID=R03
OUTPUT_PATH=/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-composed-ten/raw/DEV-R03-stage2.json
ALLOWED_SOURCE_REFS_JSON:
["C1", "C2", "C3", "C4", "C5", "C6", "M1", "M2", "M3", "M4", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "P1", "P2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "U1", "U2", "U3"]
DECLARED_INPUTS_JSON:
{
  "case": {
    "anomaly_id": "O6",
    "available_observables": [
      {
        "id": "M1",
        "text": "The event ledger gives source-to-rack unload counts and carrier identities at each boundary, independently measuring P1 output."
      },
      {
        "id": "M2",
        "text": "The clock and ledger give P2 completed correct releases and bracket counts by minute 13; a packing mark alone is not a release."
      },
      {
        "id": "M3",
        "text": "Occupied-interval entries give transfer-clerk busy minutes, including blocked unloading, and inspection-clerk busy minutes separately."
      },
      {
        "id": "M4",
        "text": "The ledger gives rack occupancy, waiting loads, and remaining trolley allowances at each boundary."
      }
    ],
    "case_id": "DEV",
    "causal_return_path_hypothesis": "HYPOTHESIS, unobserved: routine powered-trolley service may make replenishment requests appear inexpensive. Downstream production cells might adapt by requesting smaller, more frequent carrier deliveries in later windows, increasing later transfer demand and trolley use. This does not alter present demand or establish a future rate.",
    "domain": "Closed-model carrier transfer and mechanical-part release station",
    "hard_constraints": [
      {
        "id": "C1",
        "text": "The fixed demand is twelve carriers, B1 through B12, each containing exactly ten identical brackets and one seal. Success requires twelve correct sealed releases by minute 13; among successes, fewer occupied transfer-clerk minutes is preferred."
      },
      {
        "id": "C2",
        "text": "Time runs from boundary 0 through boundary 13 in whole minutes. At a boundary, completed inspection first frees rack space, a waiting or completed transfer then unloads, and new operations may start. Work after boundary 13 does not count."
      },
      {
        "id": "C3",
        "text": "The release rack holds five carriers, including the carrier under inspection. A transfer unloads its entire load together; insufficient space makes its clerk and vehicle wait until a later boundary. Floor storage is prohibited."
      },
      {
        "id": "C4",
        "text": "Source carriers leave in B-number order. Inspection follows rack arrival order. Neither operation may interrupt an active trip or inspection, discard a demanded carrier, omit inspection, or change an identifier."
      },
      {
        "id": "C5",
        "text": "A powered-trolley trip transports one to four carriers and occupies the transfer clerk for three minutes before unloading. A hand-carrier trip transports one carrier and occupies that clerk for one minute. Waiting occupies the clerk; trips cannot overlap."
      },
      {
        "id": "C6",
        "text": "The inspection clerk handles one carrier at a time. Normal inspection and sealing take one minute. B9 takes two minutes to count, add its missing bracket, recount, and seal. A correct seal counts only at completion."
      }
    ],
    "observations": [
      {
        "id": "O1",
        "text": "At boundary 0, B1, B2, and B3 are on the release rack in that order; B4 through B12 are at the source in numerical order. Both clerks are free; no carrier is inspected or sealed."
      },
      {
        "id": "O2",
        "text": "The three rack carriers belong to the same twelve-carrier demand. Transfer output concerns nine source carriers; inspection output concerns all twelve."
      },
      {
        "id": "O3",
        "text": "A carrier becomes eligible for inspection only upon reaching the rack. Finished inspection releases and removes that carrier, freeing one rack place."
      },
      {
        "id": "O4",
        "text": "The powered trolley begins charged for exactly two trips, regardless of load size. Each started trip consumes one allowance. There is no recharge during the window."
      },
      {
        "id": "O5",
        "text": "All carriers except B9 initially contain ten brackets. One correct spare bracket and twelve unused seals are present at inspection; these quantities suffice for the fixed demand."
      },
      {
        "id": "O6",
        "text": "Stipulated anomaly: B9 bears the same ten-bracket packing mark as the others but contains nine brackets. Its discrepancy is observable during inspection; its correction follows C6."
      },
      {
        "id": "O7",
        "text": "The current routine favors powered-trolley movement because it transports several carriers per trip. Hand carrying is an established, permitted operation performed by the same clerk."
      },
      {
        "id": "O8",
        "text": "All quantities, durations, discrepancies, and limits are defined synthetic facts, not depot samples. No further arrivals, failures, losses, or replenishments occur during this window."
      }
    ],
    "parent_operations": [
      {
        "id": "P1",
        "text": "Transfer source carriers to the release rack using a permitted vehicle. Its independently measurable output is source carriers unloaded out of nine; transfer-clerk occupied minutes are also recorded."
      },
      {
        "id": "P2",
        "text": "Inspect, correct when required, and seal rack carriers. Its independently measurable output is correctly sealed releases out of twelve. It consumes initially supplied and P1-delivered rack carriers, returning rack places upon completion."
      }
    ],
    "phase": "development",
    "preferred_dependency": "The routine depends on the powered trolley in P1 to supply the release rack used by P2. O3 states their existing material connection.",
    "resources": [
      {
        "available": true,
        "id": "R1",
        "text": "One transfer clerk trained on both vehicles and one inspection clerk trained to count, correct, and seal are present for minutes 0 through 13. Neither can cover the other role."
      },
      {
        "available": true,
        "id": "R2",
        "text": "One powered trolley has capacity four and the two-trip charge in O4. Its controls select one through four next source carriers and start a trip when its clerk is free."
      },
      {
        "available": true,
        "id": "R3",
        "text": "One hand carrier holds one source carrier. Its control starts a one-carrier trip when the transfer clerk is free; no power consumable is required."
      },
      {
        "available": true,
        "id": "R4",
        "text": "All twelve identified loaded carriers, one matching spare bracket, and twelve seals described in O1 and O5 are present. Each completed inspection consumes one seal."
      },
      {
        "available": true,
        "id": "R5",
        "text": "The five-place rack and one counting surface are present. A free inspection clerk may start the next rack carrier; its rack place and the surface remain occupied until completion."
      },
      {
        "available": true,
        "id": "R6",
        "text": "A minute clock and event ledger record locations, trip starts and ends, charge use, rack occupancy, inspections, bracket counts, and both clerks occupied intervals. Instrument maintenance adds no modeled labor."
      },
      {
        "available": true,
        "id": "R7",
        "text": "Either clerk may idle at a boundary. Starting a permitted trip, selecting its permitted load, and starting an eligible inspection are the only operation controls."
      },
      {
        "available": false,
        "id": "R8",
        "text": "Additional staff, rack places, brackets, seals, vehicles, charging equipment, bypass routes, and outside repairs are unavailable during the window."
      }
    ],
    "unknowns": [
      {
        "id": "U1",
        "text": "The cause of B9 packing-mark discrepancy is unknown; it implies no additional discrepancy or failure."
      },
      {
        "id": "U2",
        "text": "No evidence establishes whether downstream cells would change later request frequency or size in response to trolley service."
      },
      {
        "id": "U3",
        "text": "No trial comparison, empirical performance distribution, or proof of globally best operation is supplied. Present calculations must use the stated finite model."
      }
    ],
    "valued_outcome": "Release twelve correct, sealed carriers by minute 13; among complete releases, prefer fewer occupied transfer-clerk minutes."
  },
  "method": {
    "condition_id": "R03",
    "instructions": "Compose constructive attack with protected anomaly. Attack the preferred dependency and state the failed account and surviving function. Retain a source-supported failure signature. Fresh builder turns that signature into a diagnostic observation that selects WHERE or WHEN to act. Require rival failures the sensor separates and an action actually conditional on the signature; merely repairing the tool does not satisfy this recipe.",
    "name": "Make failure the sensor",
    "supplement_branch": "summary"
  },
  "outcome_guard": {
    "burden_observables": [
      "M1",
      "M2",
      "M3",
      "M4"
    ],
    "case_id": "DEV",
    "job_id": "DEV-guard",
    "limits": [
      {
        "constraint_id": "C1",
        "text": "Demand remains B1 through B12, each correctly containing ten brackets and one seal. All twelve correct sealed releases must finish by minute 13. Transfer concerns nine source carriers; inspection concerns all twelve. Transfer-clerk occupied minutes rank only complete successes."
      },
      {
        "constraint_id": "C2",
        "text": "Only whole-minute boundaries 0 through 13 count. Inspection completion frees rack space before transfer unloading and new starts. Initially B1 through B3 occupy the rack, B4 through B12 remain at source, and both clerks are free. Clock and ledger are available without modeled maintenance labor."
      },
      {
        "constraint_id": "C3",
        "text": "The available rack holds five carriers including active inspection; the counting surface remains occupied through inspection completion. Entire transfer loads unload together. Insufficient rack space blocks unloading and occupies the transfer clerk and vehicle. Floor storage and additional rack places are unavailable."
      },
      {
        "constraint_id": "C4",
        "text": "Source departure must follow B-number order and inspection must follow rack arrival order. Active trips and inspections cannot be interrupted. Every demanded identifier and inspection must be retained. Eligibility begins at rack arrival; completed inspection removes the carrier and frees its place."
      },
      {
        "constraint_id": "C5",
        "text": "One transfer clerk operates the available powered trolley or hand carrier; trips cannot overlap. Trolley loads contain one to four carriers and occupy three minutes before unloading, plus any wait. Exactly two started trips consume the available charge; recharge is unavailable. Hand carrying holds one carrier and occupies one minute, plus any wait. Additional staff and vehicles are unavailable."
      },
      {
        "constraint_id": "C6",
        "text": "One separate inspection clerk processes one carrier at a time and cannot exchange roles with the transfer clerk. Eleven normal inspections require one minute each; B9 requires two minutes for counting, correction, recounting and sealing: thirteen inspection minutes altogether. One correct spare bracket and twelve seals suffice. A packing mark is not a correct completed release. Additional supplies, bypasses and outside repairs are unavailable. Only permitted trip starts, load selections, eligible inspection starts and boundary idling are available controls."
      }
    ],
    "outcome": "Release twelve correct, sealed carriers by minute 13; among complete releases, prefer fewer occupied transfer-clerk minutes.",
    "source_refs": [
      "C1",
      "C2",
      "C3",
      "C4",
      "C5",
      "C6",
      "M1",
      "M2",
      "M3",
      "M4",
      "O1",
      "O2",
      "O3",
      "O4",
      "O5",
      "O6",
      "O8",
      "P1",
      "P2",
      "R1",
      "R2",
      "R3",
      "R4",
      "R5",
      "R6",
      "R7",
      "R8",
      "U1",
      "U2",
      "U3"
    ],
    "unknowns": [
      "The cause of B9 packing-mark discrepancy is unknown and establishes no further discrepancy or failure.",
      "Later downstream request frequency or size changes are unobserved; the proposed causal return path remains a hypothesis and does not change present demand.",
      "No trial comparison, empirical performance distribution or proof of globally best operation is supplied. No completed operating sequence is established by this audit; assessment is confined to the stipulated finite model with no further arrivals, failures, losses or replenishments."
    ]
  },
  "stage1": {
    "case_id": "DEV",
    "core": [
      {
        "id": "core_goal",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O4"
        ],
        "text": "Preserve twelve correct sealed releases by boundary 13, source and inspection order, whole-load unloading, five rack places, two trolley allowances, and uninterrupted active operations. Rank transfer occupied minutes only among complete successes; transfer output is nine carriers and inspection output twelve."
      },
      {
        "id": "core_attack",
        "source_refs": [
          "O7",
          "R2",
          "R3",
          "P1",
          "P2",
          "O3",
          "C5",
          "O1",
          "C6"
        ],
        "text": "Attack the account that powered trolley service is necessary for timely release. Hypothesis from the finite model: consecutive hand trips starting at 0 deliver B4 through B12 at boundaries 1 through 9 and permit continuous inspection through 13. The surviving function is timely rack supply, achievable without power; this route occupies nine transfer minutes. Closest rival: trolley loads B4-B7 during 0-3 and B8-B11 during 3-6, then hand B12 during 6-7, predicts completion at 13 with seven transfer minutes."
      },
      {
        "id": "core_sensor_action",
        "source_refs": [
          "O6",
          "C6",
          "O3",
          "M1",
          "M2",
          "M4",
          "R3",
          "R5",
          "R7"
        ],
        "text": "Preserve the failure signature: a ten-bracket mark accompanies an observed count of nine. Proposed conditional action selects WHERE: with that counted signature on the active carrier, act at inspection through correction, recount and sealing; with an empty eligible queue and a next source carrier instead, act at transfer by starting a permitted hand trip when its clerk is free. Do not classify every missing release as trolley failure. A fresh builder must show a consequential action conditional on the classified signature, beyond simply restating mandatory correction."
      },
      {
        "id": "core_probe",
        "source_refs": [
          "M1",
          "M2",
          "M3",
          "M4",
          "R6",
          "C6",
          "O6"
        ],
        "text": "Probe the same boundary trace: record source unload identities, rack eligibility, active inspection count and duration, completed correct releases, and both clerks occupied intervals. Supply-starvation predicts an empty eligible queue and inspection idle time; B9 correction predicts an occupied counting surface with nine brackets and a two-minute inspection. Defeat the sensor claim if these observations do not separate the accounts or conditional control cannot outperform its closest feasible rival."
      }
    ],
    "job_id": "DEV-R03-stage1",
    "policy": "R03",
    "residue": [
      {
        "id": "residue_cost",
        "source_refs": [
          "C1",
          "C3",
          "C5",
          "C6",
          "R1",
          "R8",
          "M3"
        ],
        "text": "Removing power can preserve output while increasing transfer burden. Waiting also occupies that clerk; the separate inspector cannot assist transfer. Eleven normal inspections plus B9 correction consume all thirteen inspection minutes, so any inspection idle time defeats the deadline. No additional capacity or staff can rescue it."
      },
      {
        "id": "residue_limits",
        "source_refs": [
          "U1",
          "U2",
          "U3",
          "O8",
          "O6"
        ],
        "text": "The anomaly cause remains unknown and implies no other defects. Later smaller requests are an unobserved hypothesis. Proposed schedules and sensor benefits are model predictions, not trial results or global optimality proof; the known discrepancy alone does not establish a new transport opening."
      }
    ],
    "tension": {
      "account_a": "A missing scheduled release reflects unavailable eligible supply from P1.",
      "account_b": "A missing normal-minute release reflects B9 count correction within P2 despite eligible supply.",
      "prediction_a": "Ledger shows an empty eligible rack and an idle inspector; a timely permitted delivery restores eligibility.",
      "prediction_b": "Ledger shows B9 active with count nine and an occupied surface for two minutes; more arrivals do not shorten its required correction."
    }
  }
}
