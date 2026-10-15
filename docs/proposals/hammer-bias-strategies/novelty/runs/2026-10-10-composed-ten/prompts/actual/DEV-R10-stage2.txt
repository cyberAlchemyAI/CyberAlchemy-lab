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
JOB_ID=DEV-R10-stage2
CASE_ID=DEV
CONDITION_ID=R10
OUTPUT_PATH=/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-composed-ten/raw/DEV-R10-stage2.json
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
    "condition_id": "R10",
    "instructions": "Compose interface ablation with protected anomaly. State rival parent-only and interaction accounts of the exact anomalous observation. Fresh builder interrupts ONLY the existing connection while preserving both parent functions and measures an observation that attributes the anomaly to the connection under opposing predictions. Disabling a parent or a measurement equally explained by it defeats the recipe.",
    "name": "Anomaly identifies interaction",
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
        "id": "core-observation",
        "source_refs": [
          "C1",
          "O2",
          "O5",
          "O6",
          "P1",
          "P2"
        ],
        "text": "Protect the exact anomaly: B9 initially contains nine brackets despite its ten-bracket packing mark. P1 output is nine source carriers unloaded; P2 output is twelve correct sealed releases by minute 13. Transport throughput and packing marks cannot substitute for correct releases."
      },
      {
        "id": "core-ablation-limit",
        "source_refs": [
          "C3",
          "C4",
          "C6",
          "O3",
          "O5",
          "O6",
          "R7",
          "R8"
        ],
        "text": "No admissible connection-only separating probe is identified. Inspection eligibility requires rack arrival; removing that connection prevents inspection of demanded source carriers. Changing trolley to hand carrier preserves the connection, while withholding transfer changes P1 output. Thirteen required inspection minutes leave no inspection-idling margin. The present connection generating B9 missing contents conflicts with the stipulated initial discrepancy. Disabling either parent or measuring its ordinary output alone defeats this recipe."
      },
      {
        "id": "core-action",
        "source_refs": [
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O4",
          "R1",
          "R2",
          "R3",
          "R5",
          "R6",
          "M1",
          "M2",
          "M3",
          "M4"
        ],
        "text": "Concrete lawful benchmark: start trolley B4-B7 at 0, unload at 3; start trolley B8-B11 at 3, unload at 6; hand-carry B12 from 6 to 7. Start every next inspection immediately; B9 occupies 8-10 and B12 completes at 13. Calculated rack occupancies after these unloads are four, five, five. Closest rival: hand-carry B4-B12 consecutively from 0 to 9, with the same continuous inspection. Ledger comparison predicts nine source unloads, twelve correct releases, and thirteen inspection minutes for both; transfer occupation is seven versus nine minutes without blocked unloading. This feasible comparison checks timing and actor burden, but cannot attribute B9 mismatch to the connection."
      }
    ],
    "job_id": "DEV-R10-stage1",
    "policy": "R10",
    "residue": [
      {
        "id": "residue-protected",
        "source_refs": [
          "C6",
          "O5",
          "O6",
          "R4",
          "M2"
        ],
        "text": "Retain B9 discrepancy under either vehicle schedule. Count nine, add the supplied spare, recount ten, and seal over two minutes. Its completed correct release occurs at 10 in the calculated benchmarks; a matching packing mark is insufficient."
      },
      {
        "id": "residue-unknowns",
        "source_refs": [
          "O8",
          "U1",
          "U2",
          "U3"
        ],
        "text": "Packing-discrepancy cause remains unknown. Later request adaptation is unobserved and changes no present demand. These are finite-model calculations, not observed trials or evidence of future performance. A lawful intervention preserving both parent functions while severing only their connection remains unavailable; therefore the required causal attribution is not established."
      }
    ],
    "tension": {
      "account_a": "Parent-only account: B9 contents already differ from its mark before present transfer; inspection exposes and corrects the discrepancy independently of the rack connection.",
      "account_b": "Interaction hypothesis: the present transfer-to-inspection connection generates B9 packing-mark discrepancy. This conflicts with its stipulated initial contents.",
      "prediction_a": "If a connection-only ablation preserving both outputs were possible, B9 would still count nine before correction.",
      "prediction_b": "Such an ablation would eliminate B9 mismatch while preserving both outputs. No permitted separating trial realizes this prediction; vehicle substitution cannot distinguish these accounts."
    }
  }
}
