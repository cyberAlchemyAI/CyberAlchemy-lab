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
{"cards": [{"anchor": "text", "burden": "text", "construction": "text", "defeat": "text", "id": "unique text", "mutation": "text", "prediction_candidate": "text", "prediction_rival": "text", "probe": "text", "residue_refs": ["exact received supplement item IDs"], "resources": ["R IDs"], "rival": "text", "source_refs": ["numbered fact IDs from ALLOWED_SOURCE_REFS_JSON"], "unknowns": ["text"]}], "case_id": "text", "job_id": "text", "no_opening_reason": "nonempty text for zero cards, otherwise null"}
Fresh builder: only own case, ordinary archive, assigned method and the supplied supplement branch are admitted. Full stage1, outcome guard and omitted branch are unavailable. Do not infer or request omitted content. residue_refs names only exact IDs received in supplement, including summary IDs where assigned. Maximum ONE card and 600 normalized saved JSON words. Zero cards requires nonempty no_opening_reason; otherwise null. Each card needs anchor, mutation, construction, rival, separating probe, both predictions, defeat, resources, source_refs, residue_refs, burden and unknowns. Required unavailable resources make a card unqualified.
JOB_ID=CONF-R09-builder
CASE_ID=CONF
CONDITION_ID=R09
OUTPUT_PATH=/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-composed-ten/raw/CONF-R09-builder.json
ALLOWED_SOURCE_REFS_JSON:
["C1", "C2", "C3", "C4", "C5", "C6", "M1", "M2", "M3", "M4", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "P1", "P2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "U1", "U2", "U3"]
DECLARED_INPUTS_JSON:
{
  "archive": [
    {
      "id": "A1",
      "limits": "Bulk includes delayed pending displays; six actions and one delivery per tick apply.",
      "operation": "Validate records and use the usual bulk tool on registered pending notices.",
      "probe": "Count registrations, recognitions, actions, and delivery attempts by boundary 9.",
      "relation": "P1 eligibility supplies the identities used by P2."
    },
    {
      "id": "A2",
      "limits": "Each request spends one of six actions; endpoint availability and queue timing apply.",
      "operation": "Validate records and request receipts individually.",
      "probe": "Record recognized IDs and action consumption.",
      "relation": "Each P2 request still requires P1 registration."
    },
    {
      "id": "A3",
      "limits": "Reading changes no display, adds no capacity, and proves no future sender behavior.",
      "operation": "Reconcile the pending display with registration and recognition ledgers.",
      "probe": "Record mismatches, first deliveries, and display clearing boundaries.",
      "relation": "Ledgers distinguish P1 completion from P2 recognition."
    }
  ],
  "case": {
    "anomaly_id": "O7",
    "available_observables": [
      {
        "id": "M1",
        "text": "The registration ledger shows validated IDs and completion boundaries, independently measuring P1 output."
      },
      {
        "id": "M2",
        "text": "The recognition ledger shows first successful deliveries and distinct recognition count by boundary 9, including N1 initial recognition."
      },
      {
        "id": "M3",
        "text": "Request and queue ledgers show actions spent, receipt IDs, eligibility boundaries, delivery order, failures, and duplicates."
      },
      {
        "id": "M4",
        "text": "The clock and dashboard show pending identities at each action boundary for comparison with the recognition ledger."
      }
    ],
    "case_id": "CONF",
    "causal_return_path_hypothesis": "HYPOTHESIS, unobserved: repeated bulk receipts could teach sending institutions that the museum expects frequent status traffic. Senders might adapt by submitting separate status-query notices in later windows rather than waiting for one receipt, increasing later registration and receipt demand. No adaptation or extra demand occurs as a present stipulation.",
    "domain": "Closed-model museum transfer-notice registration and receipt delivery",
    "hard_constraints": [
      {
        "id": "C1",
        "text": "The fixed demand is eight signed transfer notices, N1 through N8. Success requires eight registrations and eight distinct sender-recognized receipts by boundary 9. Repeated receipts for one notice do not increase that count."
      },
      {
        "id": "C2",
        "text": "Nine ticks are numbered 0 through 8. Each boundary exposes prior dashboard updates and completed registrations; clerks choose actions; the server then processes one already eligible entry. Requests at tick k become eligible at boundary k+1. Only deliveries in ticks 0 through 8 count."
      },
      {
        "id": "C3",
        "text": "The registration clerk validates one unregistered notice per tick, completing at the next boundary. The dispatcher may make one request action per tick and six total. Clerks may idle; roles cannot be exchanged."
      },
      {
        "id": "C4",
        "text": "An individual request enqueues one receipt for a selected registered, dashboard-pending notice. The bulk tool enqueues one for every registered, dashboard-pending notice, in N-number order. Either request consumes one dispatcher action."
      },
      {
        "id": "C5",
        "text": "The server processes eligible receipts in enqueue order, one per tick. A duplicate or failed delivery consumes that tick and leaves the queue. First successful delivery establishes sender recognition; subsequent deliveries add no distinct recognition."
      },
      {
        "id": "C6",
        "text": "Notice contents, endpoint availability, delivery rate, dashboard delays, queue order, and validation duration are fixed. Requests require registration. No new notices arrive during the window."
      }
    ],
    "observations": [
      {
        "id": "O1",
        "text": "At boundary 0 all eight notices are present. N1 and N2 are registered; N3 through N8 are unregistered. The queue is empty, both clerks are free, and no dispatcher action is spent."
      },
      {
        "id": "O2",
        "text": "N1 successfully received its receipt at tick -1; its sender recognized it. N2 through N8 have no successful deliveries. Initial independently counted outputs are two registrations and one recognition."
      },
      {
        "id": "O3",
        "text": "All eight signatures and required fields validate successfully in one tick each. No notice requires correction or outside information."
      },
      {
        "id": "O4",
        "text": "N1 through N7 sender endpoints are available at every modeled tick. N8 is unavailable at ticks 0 through 5 and available at ticks 6 through 8. Delivery while unavailable fails under C5."
      },
      {
        "id": "O5",
        "text": "Registration enables dispatcher requests for that notice identity. Registration output can exist independently of any receipt delivery."
      },
      {
        "id": "O6",
        "text": "Normally a successful delivery at tick k removes its notice from the pending dashboard at boundary k+1. Sender recognition occurs at successful delivery, independently of the display."
      },
      {
        "id": "O7",
        "text": "Stipulated anomaly: N1 remains displayed pending at boundaries 0 through 3 despite recognition. Its display clears at boundary 4. This is the only exceptional dashboard delay."
      },
      {
        "id": "O8",
        "text": "The bulk receipt tool is the routine default. All timings, starting states, and endpoint availability are stipulated synthetic facts, not sampled network data. No other failures or deliveries occur."
      }
    ],
    "parent_operations": [
      {
        "id": "P1",
        "text": "Validate and register signed transfer notices. Independently measurable output is distinct registrations out of eight. These identities enable P2 requests."
      },
      {
        "id": "P2",
        "text": "Request and deliver receipts for registered notices. Independently measurable output is distinct sender-recognized receipts out of eight. Requests, failures, and duplicates are separately measured and do not themselves count as recognitions."
      }
    ],
    "phase": "confirmation",
    "preferred_dependency": "The routine depends on the bulk tool in P2 to acknowledge identities registered by P1. O5 states the existing eligibility connection; the two outputs remain separately measurable.",
    "resources": [
      {
        "available": true,
        "id": "R1",
        "text": "One registration clerk trained to validate signed museum notices is present for nine ticks. The control selects any unregistered notice for its one-tick validation."
      },
      {
        "available": true,
        "id": "R2",
        "text": "One trained receipt dispatcher has six action units usable at ticks 0 through 8, at most one per tick. Each individual or bulk request consumes one unit."
      },
      {
        "available": true,
        "id": "R3",
        "text": "The bulk tool has one request control with the exact behavior in C4. It reads registration and pending states; it adds no registration or delivery capacity."
      },
      {
        "available": true,
        "id": "R4",
        "text": "The individual control selects one registered dashboard-pending notice and requests its receipt, following C4."
      },
      {
        "available": true,
        "id": "R5",
        "text": "One automatic FIFO server, its queue, and eight fixed sender endpoints are present. The queue holds every receipt producible by six actions. Processing needs no clerk action."
      },
      {
        "available": true,
        "id": "R6",
        "text": "A tick clock, registration ledger, queue ledger, pending dashboard, and sender-recognition ledger are readable at boundaries. They record actions, eligibility, delivery success, duplicates, and recognized IDs without added clerk labor."
      },
      {
        "available": true,
        "id": "R7",
        "text": "All eight signed records and sender addresses are present. Their fixed contents and identities suffice for validation and requests."
      },
      {
        "available": false,
        "id": "R8",
        "text": "Additional action units, another server, dashboard configuration access, endpoint repair, alternate communication channels, and outside clerks are unavailable."
      }
    ],
    "unknowns": [
      {
        "id": "U1",
        "text": "N1 exceptional delay origin is unknown; its clearing boundary is fixed and establishes no wider defect."
      },
      {
        "id": "U2",
        "text": "No observation establishes later sending adaptation or whether repeated receipts would cause additional status-query notices."
      },
      {
        "id": "U3",
        "text": "No empirical network distribution, previous trial comparison, or globally best schedule proof is supplied. Present claims must follow the finite model."
      }
    ],
    "valued_outcome": "Register eight notices and have eight senders recognize their receipts by boundary 9, within six dispatcher actions."
  },
  "method": {
    "condition_id": "R09",
    "instructions": "Compose causal return-path inversion with rival backcasting. Hold initial demand fixed and propose a break in tool-induced later demand. Backcast from two later worlds: persistent escape vs supplied adaptation recreating dependency. Fresh builder constructs a present probe of the SPECIFIC adaptation link supported in the packet. Do not assert adaptation without supplied basis or vary unrelated inputs.",
    "name": "Attack feedback escape from future",
    "supplement_branch": "summary"
  },
  "supplement": [
    {
      "id": "sum_goal_action",
      "source_refs": [
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "O1",
        "O2",
        "O3",
        "O4",
        "O6",
        "O7",
        "P1",
        "P2",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5"
      ],
      "text": "Fixed guard: eight registrations and eight distinct recognitions by boundary 9 within six dispatcher actions; six registrations and seven recognitions remain. Candidate validates N3,N4,N5,N6,N7,N8 at ticks 0 through 5; individually requests N2,N3,N4,N5,N6 at ticks 0 through 4; bulk requests N7,N8 at tick 6. Predicted deliveries occur at ticks 1 through 5, 7 and 8, giving eight of each including initial N1 without duplicate exposure."
    },
    {
      "id": "sum_future_tension",
      "source_refs": [
        "C5",
        "C6",
        "O8",
        "U2"
      ],
      "text": "Hypothesized return-path break: one receipt exposure per notice prevents repeated bulk traffic from teaching frequent-status expectations. Backcast persistent escape: senders await one receipt and produce no adaptation-driven separate queries. Rival future: the supplied hypothetical learning-to-query adaptation survives suppressed repeats and recreates registration/receipt dependency. Initial demand remains fixed; neither later world is observed."
    },
    {
      "id": "sum_probe_ceiling",
      "source_refs": [
        "C6",
        "M1",
        "M2",
        "M3",
        "M4",
        "R6",
        "U2"
      ],
      "text": "Feasible present probe replays candidate and closest rival against registration, recognition, queue and dashboard ledgers. Opposing predictions: zero versus two duplicate deliveries, eight versus seven recognitions. This tests receipt exposure, the controllable antecedent of the specific proposed learning-to-query link. Both later causal accounts can accept this exposure difference; no new notices may arrive, so present observables cannot separate their later adaptation predictions."
    }
  ]
}
