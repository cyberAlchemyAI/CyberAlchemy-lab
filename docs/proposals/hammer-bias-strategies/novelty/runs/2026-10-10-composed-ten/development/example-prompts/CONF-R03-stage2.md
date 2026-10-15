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
JOB_ID=CONF-R03-stage2
CASE_ID=CONF
CONDITION_ID=R03
OUTPUT_PATH=/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-composed-ten/raw/CONF-R03-stage2.json
ALLOWED_SOURCE_REFS_JSON:
["C1", "C2", "C3", "C4", "C5", "C6", "M1", "M2", "M3", "M4", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "P1", "P2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "U1", "U2", "U3"]
DECLARED_INPUTS_JSON:
{
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
    "case_id": "CONF",
    "job_id": "CONF-guard",
    "limits": [
      {
        "constraint_id": "C1",
        "text": "Eight fixed identities require separate registration and recognition counts. Initially two registrations and one recognition exist; six registrations and seven distinct recognitions remain. Duplicate receipts cannot satisfy this demand (O1, O2, P1, P2)."
      },
      {
        "constraint_id": "C2",
        "text": "Only ticks 0 through 8 supply delivery time. Requests become eligible at the next boundary; requests at tick 8 cannot contribute. Registrations also complete at the next boundary. The empty initial queue supplies no eligible delivery at tick 0 (O1)."
      },
      {
        "constraint_id": "C3",
        "text": "R1 supplies one registration clerk for nine ticks; each remaining record needs one tick and validates successfully (O3). R2 supplies six dispatcher actions, at most one per tick. Roles cannot be exchanged, and neither action count nor request count measures distinct recognition."
      },
      {
        "constraint_id": "C4",
        "text": "R3 and R4 provide the stipulated bulk and individual controls. Both require registered, dashboard-pending identities and consume one dispatcher action. The bulk control adds no registration or delivery capacity. N1 remains displayed pending through boundary 3 despite its prior recognition (O7)."
      },
      {
        "constraint_id": "C5",
        "text": "R5 provides one automatic FIFO server with sufficient queue storage, processing one eligible entry per tick without clerk labor. Duplicates and failures consume delivery slots without adding distinct recognition. N8 is unavailable through tick 5; its availability at ticks 6 through 8 is fixed (O4)."
      },
      {
        "constraint_id": "C6",
        "text": "R7 supplies all signed records and addresses; validation contents, endpoint availability, queue order, dashboard delays and processing duration remain fixed. R6 supplies readable ledgers and clock without extra clerk labor. R8 makes extra actions, servers, configuration access, repair, channels and clerks unavailable. No new demand arrives in this window."
      }
    ],
    "outcome": "Register eight notices and have eight senders recognize their receipts by boundary 9, within six dispatcher actions.",
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
      "O7",
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
      "U1: The origin of N1 exceptional display delay is unknown; its fixed clearing boundary establishes no wider defect.",
      "U2: Later sender adaptation or additional status-query demand has no observational support and does not occur as a present stipulation.",
      "U3: No empirical network distribution, previous trial comparison or globally best schedule proof is supplied; this audit establishes no successful execution."
    ]
  },
  "stage1": {
    "case_id": "CONF",
    "core": [
      {
        "id": "core-attack",
        "source_refs": [
          "P1",
          "P2",
          "C4",
          "C5",
          "O2",
          "O5",
          "O7"
        ],
        "text": "Failed account: every registered dashboard-pending identity needs recognition, so routine bulk faithfully advances P2. N1 already recognized yet remains pending; bulk can spend a delivery on an identity with no remaining recognition demand. Surviving function: registration still establishes eligibility, while bulk can economically enqueue several genuinely unrecognized registered identities."
      },
      {
        "id": "core-conditional-action",
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
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6"
        ],
        "text": "Conditional proposal: when recognition and pending ledgers disagree for N1, select individuals before its clearing boundary and defer bulk. Validate N3,N4,N5,N6,N7,N8 at ticks 0,1,2,3,4,5. Request individual N2,N3,N4 at ticks 0,1,2. At boundary 4, require N1 cleared, prior recognized notices cleared, and an empty queue; then bulk N5,N6. Request individual N7 at tick 5 and N8 at tick 6. Predicted first deliveries: N2,N3,N4 at ticks 1,2,3; N5,N6,N7,N8 at ticks 5,6,7,8. Eight registrations complete by boundary 6; eight recognitions include initial N1. Six actions. This is a model prediction, not execution evidence."
      },
      {
        "id": "core-probe-defeat",
        "source_refs": [
          "C1",
          "C3",
          "C4",
          "C5",
          "M1",
          "M2",
          "M3",
          "M4",
          "O2",
          "O7",
          "R6"
        ],
        "text": "Closest rival is immediate routine bulk. Feasible separating probe: compare N1 registration, first-success ledger and pending identity at boundary 0, then observe clearing at boundary 4. A recognized-but-pending identity selects the guarded request timing. Missing recognition would instead support genuine unmet receipt demand. Immediate bulk predicts a duplicate N1 delivery at tick 1; guarded scheduling predicts none. Defeat: required ledgers or boundary-4 guard contradict the signature, or the proposed trace exceeds six actions or finishes below eight distinct recognitions."
      },
      {
        "id": "core-burden",
        "source_refs": [
          "C3",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R6",
          "R8"
        ],
        "text": "Actor burden: registration clerk performs six validations; dispatcher performs six requests and compares readable ledgers at action boundaries. Ledger access adds no clerk labor. Audit registrations, distinct recognition, actions, duplicate/failure deliveries and display boundaries separately. Extra capacity, configuration changes and endpoint repair are unavailable."
      }
    ],
    "job_id": "CONF-R03-stage1",
    "policy": "R03",
    "residue": [
      {
        "id": "residue-protected-signature",
        "source_refs": [
          "O2",
          "O6",
          "O7",
          "M2",
          "M4"
        ],
        "text": "Protected failure signature: N1 has prior successful recognition but remains dashboard-pending at boundaries 0 through 3 and clears at boundary 4. Preserve this disagreement as a timing sensor; do not erase it by treating pending as receipt demand."
      },
      {
        "id": "residue-unknowns",
        "source_refs": [
          "U1",
          "U2",
          "U3",
          "O8",
          "C6"
        ],
        "text": "Delay origin is unknown. Later sender adaptation and extra status-query demand remain unobserved hypotheses; no new demand occurs here. Synthetic timings supply neither empirical network evidence nor a globally best schedule proof."
      }
    ],
    "tension": {
      "account_a": "Pending can lag recognition; the N1 mismatch identifies an unsafe early bulk window.",
      "account_b": "Pending accurately identifies unmet recognition; N1 belongs in immediate bulk.",
      "prediction_a": "At boundary 0 N1 has recorded recognition despite pending; immediate bulk repeats N1, while the guarded boundary-4 bulk excludes it.",
      "prediction_b": "At boundary 0 N1 lacks recorded recognition; an immediate N1 receipt adds one distinct recognition."
    }
  }
}
