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
{"archive_pairs": [{"archive_id": "exact archive ID", "card_id": "opaque card ID", "reason": "text", "relation": "equivalent|distinct|unknown"}], "candidate_pairs": [{"left": "opaque card ID", "reason": "text", "relation": "equivalent|distinct|unknown", "right": "opaque card ID"}], "cards": [{"anchor_fit": "boolean|null", "card_id": "opaque card ID", "defeat_clear": "boolean|null", "reason": "text", "resource_fit": "boolean|null", "separating": "boolean|null", "source_support": "boolean|null", "unit_id": "opaque unit ID"}], "case_id": "text", "job_id": "text", "units": [{"reason": "text", "status": "valid|invalid|gated", "unit_id": "opaque unit ID"}]}
Whole-case independent review. Method labels and the private permutation map are withheld; substantive content can suggest a method, so full semantic blinding is not claimed. Preserve supplied structural unit status. Judge all five axes true/false/null and explicitly reject indispensable unavailable resources. Pair relations are equivalent/distinct/unknown without transitivity.
Cover exactly all units, every declared raw card including malformed declarations in failure wrappers, every card/archive pair and every unordered card/card pair once. Valid zero-opening units have no card rows. Complete coverage takes priority over the 16000 normalized JSON word soft cap. Nominal geometry is 315 rows with 21 cards and three archives; anomalous extra cards are never discarded.
JOB_ID=DEV-review1
CASE_ID=DEV
CONDITION_ID=NONE
OUTPUT_PATH=/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-composed-ten/raw/DEV-review1.json
ALLOWED_SOURCE_REFS_JSON:
["C1", "C2", "C3", "C4", "C5", "C6", "M1", "M2", "M3", "M4", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "P1", "P2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "U1", "U2", "U3"]
DECLARED_INPUTS_JSON:
{
  "archive": [
    {
      "id": "A1",
      "limits": "Whole-load unloading, two charge allowances, and source order apply.",
      "operation": "Use full powered-trolley loads where remaining source quantity permits, then hand carry the remainder.",
      "probe": "Record unloads, correct releases, occupied transfer minutes, and rack waits.",
      "relation": "P1 feeds the rack and P2 frees space during the window."
    },
    {
      "id": "A2",
      "limits": "One carrier per one-minute trip, rack capacity, and B9 correction time apply.",
      "operation": "Hand carry source carriers consecutively while inspection follows its normal sequence.",
      "probe": "Record both output counts and clerk occupied intervals.",
      "relation": "Single-carrier arrivals supply the existing P1-to-P2 connection."
    },
    {
      "id": "A3",
      "limits": "The checklist creates no parts, removes no transport waits, and proves no future behavior.",
      "operation": "Apply the counting and sealing checklist to every arriving carrier.",
      "probe": "Compare physical counts with packing marks; record completed correct seals.",
      "relation": "P2 establishes whether supplied carriers satisfy release demand."
    }
  ],
  "cards": [
    {
      "card_id": "DEV-U01-C01",
      "declared_card": {
        "anchor": "Whole-load rack fit and charge limits coexist with nine source unloads, twelve releases, and B9 correction; batch capacity alone does not establish lower labor.",
        "burden": "Transfer clerk works seven minutes and uses both trolley allowances; inspection clerk works thirteen minutes. The clerk must switch vehicles at boundary 1 and maintain the specified load order.",
        "construction": "Hand carry B4 during 0-1; trolley B5-B8 during 1-4; trolley B9-B12 during 4-7. Inspect B1-B8 consecutively during 0-8, correct and seal B9 during 8-10, then inspect B10-B12 during 10-13. Completion before unloading leaves zero rack carriers at 4 and one at 7, so both four-carrier loads fit.",
        "defeat": "Reject if the boundary ledger shows any blocked unload, transfer occupation above seven minutes, or fewer than twelve physically correct completed seals by 13. Equal final performance supplies no evidence of superiority over the rival.",
        "mutation": "Move the single hand-carried remainder to the first trip, making the second trolley load contain B9 through B12.",
        "prediction_candidate": "Finite-model prediction: one source carrier unloaded by 1, five by 4, nine by 7; twelve correct releases by 13, including corrected B9, with seven occupied transfer minutes and no blocked unloading.",
        "prediction_rival": "Finite-model prediction: zero source unloads by 1, four by 3, eight by 6, nine by 7; the same twelve correct releases and seven occupied transfer minutes.",
        "probe": "Replay both schedules against the stated boundary rules; ledger carrier identities, whole-load fit, charge use, occupied intervals, physical bracket counts and completed seals. Boundary-1 source unload counts distinguish the schedules; final counts test feasibility and the predicted tie.",
        "residue_refs": [
          "DEV-U01-C01-SUP1",
          "DEV-U01-C01-SUP2",
          "DEV-U01-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Full-load-first archive operation: trolley B4-B7 during 0-3, trolley B8-B11 during 3-6, then hand carry B12 during 6-7, with continuous ordered inspection.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "O8",
          "P1",
          "P2",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause remains unknown.",
          "Later request adaptation remains unobserved and does not change this window.",
          "These are calculated schedules, not trial outcomes, empirical distributions or a global optimality proof."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U01"
    },
    {
      "card_id": "DEV-U02-C01",
      "declared_card": {
        "anchor": "P1 supplies P2; immediate inspection returns rack space. B9 requires correction despite its packing mark. Two trolley allowances permit a hypothesized boundary where adding a singleton powered trip increases occupied transfer minutes without improving correct releases.",
        "burden": "Transfer clerk changes vehicle and follows fixed departures; inspection clerk counts, corrects B9 and seals in arrival order. Exit occupies transfer for a predicted nine minutes, one more than normal. Ledger captures both clerks separately.",
        "construction": "Normal: trolley B4-B7 at 0-3, then hand B8-B12 consecutively at 3-8. Higher dose: identical first trolley, singleton trolley B8 at 3-6, then hand B9-B12 consecutively at 6-10. Inspect each eligible next carrier immediately. If triggered, exit uses only consecutive hand trips B4-B12 at 0-9 with immediate inspection, preserving all identifiers, inspection and correction. Physical activation is unqualified pending independent reset resources.",
        "defeat": "Either completed higher-dose trial ties or beats its normal control, or hand exit fails twelve correct releases by 13, defeats the proposed harmful-boundary exit. Missing trials establish no trigger.",
        "mutation": "Predeclare a switch away from powered-trolley dependency only when BOTH independently reset matched higher-dose trials worsen the exact present metric versus their normal-dose controls; otherwise hold normal.",
        "prediction_candidate": "Finite-model prediction: both schedules complete twelve correct releases by 13; normal occupies transfer for eight minutes, higher for ten. Each matched pair therefore worsens the metric. Dependency-free hand exit predicts twelve correct releases by 13 and nine occupied transfer minutes.",
        "prediction_rival": "At least one completed higher-dose trial uses no more occupied transfer minutes than its completed normal control; the two-pair trigger fails.",
        "probe": "Fix two independently reset normal/higher trial pairs with identical O1 demand before observation. Exact metric: twelve correct sealed releases by minute 13 outranks failure; among successes fewer occupied transfer-clerk minutes wins; failures against failures are unordered. Record unload identities, correct releases, occupied intervals, rack occupancy, waits and charge with clock and ledger. No post-result cutoff.",
        "residue_refs": [
          "DEV-U02-C01-SUP1",
          "DEV-U02-C01-SUP2",
          "DEV-U02-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Additional powered service preserves present success without increasing transfer occupation relative to the fixed normal schedule.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
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
          "Untestable assumption: four independently reset physical trials are obtainable. Reset facilities, replacement consumed seals and restored trolley charge are not supplied; declared resources cannot establish this physical trigger.",
          "B9 discrepancy cause and any later downstream adaptation remain unknown; neither changes fixed demand.",
          "No trials, measured threshold, observed benefit or global optimality proof are supplied."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U02"
    },
    {
      "card_id": "DEV-U04-C01",
      "declared_card": {
        "anchor": "P1 supplies rack carriers to P2. The initial three-carrier buffer can sustain inspection while replenishment travels; B9 still requires correction despite its packing mark.",
        "burden": "Candidate hypothesis: transfer clerk occupies minutes 0-7, seven total; inspection clerk occupies 0-13, thirteen total. Rival hypothesis: transfer occupies 0-9, nine total; inspection also thirteen. Record blocked unloading as occupied labor.",
        "construction": "Future A hypothesizes twelve correct releases by 13 through initial-buffer and bulk-replenishment dependencies. Inspect continuously from 0; trolley B4-B7 at 0-3, trolley B8-B11 at 3-6, hand B12 at 6-7. After releases at boundaries 3 and 6, batches produce rack occupancies four and five; B12 fits at 7. B9 correction uses the available spare.",
        "defeat": "Reject the candidate success hypothesis if any whole load cannot unload as scheduled, continuous inspection breaks, or fewer than twelve correct releases finish by 13. Reject its burden advantage if occupied transfer time reaches nine or more minutes. A packing mark cannot satisfy release evidence.",
        "mutation": "Backcast the two futures to their first causal divergence at boundary 0: commit the transfer clerk to a four-carrier trolley trip versus a one-carrier hand trip. Select A for the present probe because its hypothesized complete success uses fewer transfer minutes.",
        "prediction_candidate": "At boundaries 1,2,3 cumulative source unloads are 0,0,4. Two trolley allowances are consumed by boundary 3. Correct completions B1-B8 occur at 1-8, B9 at 10, and B10-B12 at 11-13; nine source carriers unload by 7, without blocked unloading.",
        "prediction_rival": "At boundaries 1,2,3 cumulative source unloads are 1,2,3, with both trolley allowances retained. Nine source carriers unload by 9, without blocking; the same twelve correct completion times are hypothesized.",
        "probe": "Execute A once using only available controls. Inspect B1 at 0; record identities, cumulative unloads, rack occupancy, waits, charge and both clerks occupied intervals at boundaries 0-3, then through 13. Count actual brackets and completed correct seals. Compare observations with the finite-model rival predictions; B remains an unobserved counterfactual.",
        "residue_refs": [
          "DEV-U04-C01-SUP1",
          "DEV-U04-C01-SUP2",
          "DEV-U04-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Future B hypothesizes twelve correct releases by 13 through regular single-carrier arrivals: hand-carry B4-B12 with starts 0-8 and unloads 1-9, while inspecting continuously from 0.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "O8",
          "P1",
          "P2",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause remains unknown.",
          "Later downstream request adaptation is unobserved and does not change fixed demand.",
          "No empirical comparison, distribution or supplied global optimality proof; both futures and predictions are hypotheses within the stipulated model."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U04"
    },
    {
      "card_id": "DEV-U06-C01",
      "declared_card": {
        "anchor": "P1 must deliver nine source carriers while P2 releases all twelve correctly by boundary 13. The preferred trolley R2 is forbidden in candidate P1.",
        "burden": "Predicted candidate transfer occupation: nine minutes; inspection: thirteen uninterrupted minutes, including B9 correction. Same two clerks retain their roles. The unrestricted rival predicts seven transfer minutes, so deprivation demonstrates feasibility rather than winning the secondary objective.",
        "construction": "Using R3, start consecutive one-carrier hand trips at boundaries 0 through 8, delivering B4 through B12 at boundaries 1 through 9. Inspect B1-B8 consecutively during 0-8, B9 during 8-10, then B10-B12 during 10-13. Count B9, add the spare, recount, and seal; count every other carrier and seal upon inspection completion.",
        "defeat": "Reject for fewer than twelve correct completed releases at 13, incorrect counts or seals, candidate trolley use, overlapping trips, broken ordering, rack overflow, floor storage, or interrupted inspection. A legal successful rival with fewer transfer minutes defeats any candidate superiority claim.",
        "mutation": "Replace bulk powered transport with a one-carrier arrival stream, preserving the existing rack-to-inspection connection and source order. Retain the B9 discrepancy, whole-load unloading, boundary precedence, and inspection occupancy from residue.",
        "prediction_candidate": "Finite-model prediction: nine source unloads by 9, no blocking or inspection starvation, peak rack occupancy four, and twelve correct releases at 13. Candidate consumes zero trolley allowances.",
        "prediction_rival": "Unrestricted bulk rival predicts the same twelve releases at 13 with seven occupied transfer minutes and two allowances consumed. The necessity hypothesis instead predicts that trolley deprivation starves inspection and misses twelve; successful candidate replay would refute that hypothesis in this window.",
        "probe": "Replay candidate and unrestricted rival in the stipulated model using R6; record identities, rack occupancy at boundaries, waiting intervals, allowances, separate clerk occupation, bracket counts, and completed seals. Compare the candidate metrics with summary-only deprivation and residue construction without deprivation under identical demand and rules. Their outputs are unavailable; leave those comparisons unresolved rather than inventing schedules or results.",
        "residue_refs": [
          "DEV-U06-C01-SUP1",
          "DEV-U06-C01-SUP2",
          "DEV-U06-C01-SUP3",
          "DEV-U06-C01-SUP4",
          "DEV-U06-C01-SUP5",
          "DEV-U06-C01-SUP6",
          "DEV-U06-C01-SUP7"
        ],
        "resources": [
          "R1",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Closest unrestricted rival: R2 carries B4-B7 during 0-3 and B8-B11 during 3-6; R3 carries B12 during 6-7. Inspection completion precedes unloading, so these full loads fit. This is a comparison arm only; R2 cannot enter candidate construction.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "No comparator-arm outcomes or empirical trials are supplied.",
          "B9 discrepancy cause remains unknown.",
          "Later request adaptation is an unobserved hypothesis and changes no present demand.",
          "These legal schedule calculations establish no global optimality."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U06"
    },
    {
      "card_id": "DEV-U07-C01",
      "declared_card": {
        "anchor": "Hold B1-B12 fixed: twelve correct seals by boundary 13. B9 requires its observed missing-bracket correction; its packing mark cannot establish a correct release.",
        "burden": "Calculated present transfer occupation is seven minutes versus nine for consecutive hand trips; inspection occupies thirteen minutes. Future disclosure and request logging impose equal-contact burdens that must be measured separately; no duration is supplied.",
        "construction": "Trolley B4-B7 at 0-3, trolley B8-B11 at 3-6, hand carry B12 at 6-7. Inspect continuously in arrival order, including B9 at 8-10 and B12 at 12-13. Boundary ordering permits both whole trolley loads within the five-place rack.",
        "defeat": "Reject the proposed perception mechanism if disclosure demonstrably raises perceived effort yet later frequency and request size remain unchanged. Unequal physical service confounds the comparison; failure to change perception makes a null result inconclusive. Any missed correct seal defeats the present action.",
        "mutation": "Invert the hypothesized return link by associating apparently inexpensive trolley deliveries with their occupied transfer minutes, while preserving initial demand and physical service. This is a proposed later communication intervention, not an observed effect or an extra present operation control.",
        "prediction_candidate": "Tool-induced later-demand hypothesis: conditional on higher perceived service cost, effort disclosure produces fewer later requests and larger quantities per request than the sham, at equal total later requirements.",
        "prediction_rival": "Exogenous later-demand hypothesis: later requirements determine requests independently of perceived trolley cost, so effort disclosure and sham produce unchanged frequency and size.",
        "probe": "Prospective extension only: after identical successful service, randomly assign effort-associated ledger delivery records or an equal-contact sham showing carrier identities alone. Check the perception manipulation and compare subsequent request frequency and quantity per request, accounting for total later requirements. Record present unloads, releases, occupancy and clerk intervals first. No later requests or intervention outcomes occur in the supplied window; future execution access is unresolved.",
        "residue_refs": [
          "DEV-U07-C01-SUP1",
          "DEV-U07-C01-SUP2",
          "DEV-U07-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Closest present rival: consecutive hand trips 0-9 also permit twelve correct seals by 13 but use nine transfer minutes. The causal rival attributes later requests to exogenous requirements rather than inexpensive-looking trolley service.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause is unknown.",
          "Later behavioral adaptation and disclosure effectiveness are unobserved.",
          "Future participants, permission and execution access are not supplied; this protocol is not presently executable.",
          "No empirical comparison or global optimality proof is supplied."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U07"
    },
    {
      "card_id": "DEV-U08-C01",
      "declared_card": {
        "anchor": "B9 has a ten-bracket packing mark but nine brackets. Preserve its two-minute count, spare-bracket correction, recount and seal. Its rack retention suggests a possible coupling with whole-load unloading; that penalty remains a hypothesis.",
        "burden": "One clerk performs all transfers; the other inspects continuously for thirteen minutes. Both variants use two trolley allowances, twelve seals and one spare bracket. Logging adds no modeled labor.",
        "construction": "Inspect continuously from boundary 0. Trolley B4-B7 runs 0-3; trolley B8-B11 runs 3-6; hand B12 runs 6-7. Check actual counts and complete B9 correction before release.",
        "defeat": "Defeat the candidate advantage if the four-carrier second load waits, any correct release misses boundary 13, or its transfer occupation is not below the three-carrier variant. The supplied finite-model calculation instead defeats the hypothesized blocking rival for this schedule.",
        "mutation": "Make second trolley load size the control knob: four carriers versus three, keeping first trip and continuous inspection fixed; hand carry the resulting remainder in source order.",
        "prediction_candidate": "Calculated model prediction: both variants unload nine source carriers and correctly release twelve by 13, with no unloading waits. Four-carrier loading occupies transfer for seven minutes versus eight for three; inspection occupies thirteen in both. B9 still takes two minutes.",
        "prediction_rival": "Hypothesized rack-retention account predicts the four-carrier variant blocks unloading or adds enough occupied transfer time to erase its advantage; reducing the second load to three avoids that penalty.",
        "probe": "Run the two finite schedules. Comparator: trolley B4-B7 at 0, B8-B10 at 3, hand B11 at 6 and B12 at 7. Record boundary unloads, identities, rack headroom, waits, charge, correct-release times and separate occupied intervals. At boundary 6, after B6 release, one rack carrier remains: four free places permit either trolley load.",
        "residue_refs": [
          "DEV-U08-C01-SUP1",
          "DEV-U08-C01-SUP2",
          "DEV-U08-C01-SUP3",
          "DEV-U08-C01-SUP4"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Reduce the second trolley load to three and hand carry two carriers, on the hypothesis that preserving headroom prevents a B9-related transfer penalty.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "O8",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3",
          "P1",
          "P2"
        ],
        "unknowns": [
          "B9 discrepancy cause is unknown; no further discrepancy follows.",
          "No empirical trial distribution or global optimality proof is supplied.",
          "Later request adaptation is unobserved and does not change this window."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U08"
    },
    {
      "card_id": "DEV-U10-C01",
      "declared_card": {
        "anchor": "P1 supplies the five-place rack for ordered P2 inspection; the existing trolley routine fits nine source carriers and two charged trips.",
        "burden": "Transfer clerk occupies seven minutes; inspection clerk occupies thirteen, including B9 correction. Both trolley allowances are consumed. The rival occupies nine transfer minutes.",
        "construction": "Start trolley B4-B7 at 0, unloading at 3; trolley B8-B11 at 3, unloading at 6; hand carry B12 at 6, unloading at 7. Inspect continuously: B1-B8 finish at 1-8, B9 runs 8-10 with the spare bracket, and B10-B12 finish at 11-13. Seal only after correct counting.",
        "defeat": "Reject the proposed benefit if the legal candidate trace requires unloading waits or an inspection gap, fails any correct release by 13, or occupies at least nine transfer minutes. Apply the transfer preference only after complete success.",
        "mutation": "Consolidate the ordinary full-load routine into two four-carrier trolley trips followed immediately by one permitted hand trip.",
        "prediction_candidate": "Finite-model calculation predicts nine source unloads, twelve correct releases and 120 released brackets by 13, zero unloading waits, seven transfer minutes and thirteen inspection minutes; maximum rack occupancy is five. Execution is unobserved.",
        "prediction_rival": "Consecutive hand trips predict the same nine unloads, twelve releases and 120 brackets by 13, with nine transfer minutes and thirteen inspection minutes. The competing blocking account instead predicts a trolley wait or inspection gap and deadline failure.",
        "probe": "Compare legal boundary-by-boundary event traces of both schedules using carrier identities, counts at completed releases, clerk occupied intervals, rack occupancy, waiting loads and charge use. Independently check P1 unloads and P2 releases; packing marks alone do not count.",
        "residue_refs": [
          "DEV-U10-C01-SUP1",
          "DEV-U10-C01-SUP2",
          "DEV-U10-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Hand carry B4-B12 consecutively from 0 to 9 while inspection follows arrival order and corrects B9.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause is unknown.",
          "Later request-frequency adaptation is unobserved and does not change this window.",
          "No empirical trial, performance distribution or global optimality proof is supplied."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U10"
    },
    {
      "card_id": "DEV-U11-C01",
      "declared_card": {
        "anchor": "P1 must unload nine ordered source carriers; P2 must release all twelve correctly sealed carriers by minute 13, including the initially supplied three and corrected B9.",
        "burden": "Calculated transfer-clerk occupation is nine minutes with zero unloading waits; inspection-clerk occupation is thirteen minutes. The schedule establishes feasibility, not superiority on the secondary transfer-labor preference or global optimality.",
        "construction": "Hand-carry B4 through B12 consecutively: start at boundaries 0 through 8, unload at 1 through 9. Inspect B1 through B8 continuously from 0 through 8; count, correct with the spare bracket, recount, and seal B9 during 8 through 10; complete B10, B11, and B12 at 11, 12, and 13. Apply inspection-completion-before-unloading at every boundary. Calculated rack maximum is four.",
        "defeat": "Reject this counterexample for any deadline miss, incorrect bracket count or seal, source or inspection ordering violation, interrupted operation, rack overflow, forbidden storage, blocked unloading, or powered-trolley use.",
        "mutation": "Remove powered-trolley service entirely from the candidate route. Preserve demand, both parent functions, B9 correction, staffing, rack capacity, ordering, and deadline; replace each source movement with the available one-carrier hand operation.",
        "prediction_candidate": "Within the stipulated model, nine source carriers unload by boundary 9; twelve correct sealed releases totaling 120 brackets complete by boundary 13. Rack occupancy never exceeds four, unloading never waits, and both trolley allowances remain unused.",
        "prediction_rival": "The trolley-necessity hypothesis predicts that the hand-only schedule starves P2 and yields fewer than twelve correct releases by boundary 13. This prediction is a hypothesis, not an observed failure.",
        "probe": "Execute the specified hand-only trace with the clock and event ledger. Independently record P1 unload identities, P2 completion times and counts, bracket totals, both clerks occupied intervals, rack occupancy, waiting loads, and remaining trolley allowances. Judge necessity using completed correct releases; nine deliveries alone are insufficient.",
        "residue_refs": [
          "DEV-U11-C01-SUP1",
          "DEV-U11-C01-SUP2",
          "DEV-U11-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Closest dependency explanation: the current multi-carrier powered-trolley routine is necessary to sustain P2 supply; sequential hand deliveries would cause starvation before the deadline.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "The cause of B9 discrepancy remains unknown.",
          "Later downstream request adaptation is unobserved and cannot change this fixed window.",
          "No empirical trial distribution or global optimum is supplied; these are finite-model predictions."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U11"
    },
    {
      "card_id": "DEV-U13-C01",
      "declared_card": {
        "anchor": "The surviving all-manual migration predicts twelve releases but nine transfer minutes; its supplied seven-minute rival defeats that labor ranking. Preserve the hand carrier as a selective bridge.",
        "burden": "Predicted ledger: transfer clerk one manual minute plus six trolley minutes, zero waiting; inspection clerk thirteen busy minutes including B9 correction. Two charge allowances and twelve seals consumed; rack peak five. Dispatch and counting remain actor obligations. R6 adds no modeled maintenance labor; no broader maintenance claim follows.",
        "construction": "Hand carry B4 at 0-1. Trolley B5-B8 at 1-4, then B9-B12 at 4-7. Inspect continuously from 0: B4 at 3-4, B5-B8 at 4-8, B9 at 8-10, B10-B12 at 10-13. At 7 the completed inspection leaves B8, allowing the entire four-carrier unload.",
        "defeat": "Reject any replay showing fewer than twelve correct releases, unloading waits, capacity violation, or more than seven transfer minutes. A one-boundary deferral of the initial manual trip predicts an inspection gap at 4-5 and only eleven releases by 13. Equal baseline labor gives no preference over the rival.",
        "mutation": "Migrate the first source replenishment into the available hand carrier, retaining powered batches for the other eight. Original carrier migration already includes a second attack. The added operation here is a comparative burden ledger for this changed dispatch order, followed by a dependency-specific delayed-start replay.",
        "prediction_candidate": "Finite-model hypothesis: source unload counts at boundaries 1, 3, 4, 6, 7 are 1, 1, 5, 5, 9; twelve correct releases at 13, B9 corrected at 10, seven occupied transfer minutes.",
        "prediction_rival": "Finite-model hypothesis: source unload counts at those boundaries are 0, 4, 4, 8, 9; also twelve correct releases at 13 and seven occupied transfer minutes. It therefore matches the candidate on the stated ranking.",
        "probe": "Replay both schedules using R6 and M1-M4, recording identities, boundary unload counts, correct seals and bracket counts, occupied intervals, occupancy, waits and charge. Separately replay the candidate with its hand trip at 1-2 and successive trolleys at 2-5 and 5-8; this tests timely bridge dispatch without asserting delay occurrence.",
        "residue_refs": [
          "DEV-U13-C01-SUP1",
          "DEV-U13-C01-SUP2"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Trolley B4-B7 at 0-3, trolley B8-B11 at 3-6, hand B12 at 6-7, with continuous inspection.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "P1",
          "P2",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "Whether dispatch delay would occur.",
          "B9 discrepancy cause and future request adaptation remain unknown.",
          "No empirical comparison or global optimality proof is supplied; timing and burden results are finite-model predictions."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U13"
    },
    {
      "card_id": "DEV-U14-C01",
      "declared_card": {
        "anchor": "O6: B9 bears a ten-bracket packing mark but contains nine; the mark cannot establish a correct release.",
        "burden": "The transfer clerk makes two trolley trips and one hand trip, predicted seven occupied minutes. The inspection clerk spends thirteen occupied minutes, including two for B9; ledger recording adds no modeled labor.",
        "construction": "Trolley B4-B7 during 0-3 and B8-B11 during 3-6; hand carry B12 during 6-7. Inspect continuously: B1-B8 complete at 1-8, B9 at 10 after counting nine, adding the spare, recounting ten and sealing; B10-B12 complete at 11-13. Completion-first boundaries predict sufficient rack space for every whole-load unload.",
        "defeat": "Any missed correct release by 13, capacity blockage invalidating this sequence, transfer occupation above seven, or failure to count nine then correct B9 defeats the proposed execution. Equal or lower rival occupation defeats its burden advantage.",
        "mutation": "Combine permitted batch transfer with the protected B9 exception. Retain incompatible accounts explicitly: physical count predicts nine before correction; the rejected mark-as-count account predicts ten. Do not shorten B9 inspection to reconcile them.",
        "prediction_candidate": "Calculated: B9 first count nine, corrected recount ten; nine source unloads, twelve correct sealed releases by 13, seven transfer minutes, thirteen inspection minutes and zero blocked unloading.",
        "prediction_rival": "Calculated hand-only rival: B9 first count nine and corrected recount ten; nine source unloads, twelve correct releases by 13, nine transfer minutes and thirteen inspection minutes. The separate rejected mark-as-count account predicts ten before correction, contrary to O6.",
        "probe": "Replay both finite schedules using clock and ledger; record source identities and unloads, rack occupancy, remaining charge, both occupied intervals and completed correct releases. At B9 record its packing mark and first physical count before adding the spare, then record recount and completed seal. Compare initial nine versus ten predictions and seven versus nine transfer-minute predictions.",
        "residue_refs": [
          "DEV-U14-C01-SUP1",
          "DEV-U14-C01-SUP2",
          "DEV-U14-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6"
        ],
        "rival": "Consecutive hand trips B4-B12 during 0-9 with the same complete inspection and B9 correction sequence.",
        "source_refs": [
          "O6",
          "C6",
          "O5",
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "O1",
          "O2",
          "O3",
          "O4",
          "O8",
          "P1",
          "P2",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause remains unknown.",
          "Later request adaptation is unobserved and does not alter this fixed demand.",
          "These are finite-model calculations, not observed comparative runs; global optimality is unproved."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U14"
    },
    {
      "card_id": "DEV-U15-C01",
      "declared_card": {
        "anchor": "Present deadline regime: at boundary 10, B12 alone remains at source and earlier inspections follow the declared schedule. Predeclare latest admissible B12 unloading at boundary 12; later unloading cannot permit its one-minute correct release by 13.",
        "burden": "Predicted transfer-clerk occupancy is nine minutes for hand carrying versus eleven for the powered final leg, without unloading waits. Inspection occupies thirteen versus twelve minutes; the latter leaves one demanded release incomplete. Both clerks follow boundary controls and record events.",
        "construction": "Hand carry B4 through B11 on eight consecutive trips starting at boundaries 0 through 7. Idle transfer from 8 to 10. Hand carry B12 from 10 to 11. Inspect B1 through B8 continuously from 0 to 8, correct and seal B9 from 8 to 10, then inspect B10, B11, B12 on 10-11, 11-12, 12-13.",
        "defeat": "Defeat this inversion if replacing the final leg with the powered trip legally yields twelve correct releases by boundary 13 under the identical prefix, durations, ordering and controls. A prefix violation invalidates the comparison.",
        "mutation": "Increase preferred intervention only on the final singleton: replace hand carrying B12 at 10 with a powered-trolley trip starting at 10, leaving every earlier operation identical.",
        "prediction_candidate": "Deadline coupling predicts hand B12 unloading at 11 and twelve correct releases at 13. Powered B12 unloads at 13, triggering the predeclared detector and leaving eleven correct releases. Both alternatives unload all nine source carriers by 13; rack occupancy never exceeds three.",
        "prediction_rival": "The transfer-output sufficiency account predicts twelve correct releases in both alternatives because all nine source carriers reach the rack by 13, regardless of the final vehicle.",
        "probe": "Replay both declared schedules in the finite model. Predeclared detector: B12 has not unloaded by boundary 12. Record its unloading boundary, inspection eligibility at 12, correct releases at 13, rack occupancy, charge use and both clerks occupied intervals; distinguish P1 unloading from P2 release.",
        "residue_refs": [
          "DEV-U15-C01-SUP1",
          "DEV-U15-C01-SUP2",
          "DEV-U15-C01-SUP3"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Closest operational rival uses the same eight-hand-trip prefix and powered B12 at 10; its competing account treats complete transfer output by the deadline as sufficient for complete release.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "O7",
          "O8",
          "M1",
          "M2",
          "M3",
          "M4",
          "P1",
          "P2",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 packing discrepancy cause remains unknown.",
          "Later demand adaptation is unobserved and supplies no present harm boundary.",
          "These are finite-model predictions; no empirical trials, performance distribution or global optimality proof is supplied."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U15"
    },
    {
      "card_id": "DEV-U16-C01",
      "declared_card": {
        "anchor": "Attack the powered-trolley supply dependency by imposing no trolley starts. This counterfactual failure tests the proposed necessity account; no trolley breakdown or operator belief was observed.",
        "burden": "Displace transport onto the same transfer clerk: nine uninterrupted hand trips occupy nine minutes. Inspection occupies thirteen minutes, including B9 correction. Restored powered service uses seven transfer minutes, so survival carries two additional transfer minutes.",
        "construction": "Hand carry B4 through B12 consecutively during intervals 0-1 through 8-9. Inspect B1 through B8 during 0-8; correct and seal B9 during 8-10; inspect B10 during 10-11, B11 during 11-12, B12 during 12-13. Complete inspections before unloading at each boundary. Rack occupancy after unloading remains three through boundary 8, reaches four at 9, then decreases. Use the supplied spare bracket and twelve seals.",
        "defeat": "An inspection gap, blocked unloading, capacity breach, wrong order, missing correction, or fewer than twelve correct releases defeats this survivor. Valid hand-only completion defeats the necessity account. Seven transfer minutes for the restored routine defeat any claim of hand-only labor superiority.",
        "mutation": "Retain timely P1 supply and P2 correct release while withholding every powered trip; construct supply from existing permitted hand trips.",
        "prediction_candidate": "Finite-model prediction: nine source unloads by 9, twelve correct sealed releases and 120 brackets by 13, no inspection gaps or transfer waits, nine transfer minutes and thirteen inspection minutes.",
        "prediction_rival": "The necessity account predicts a gap and fewer than twelve correct releases under withheld trolley starts. With service restored, the concrete closest routine predicts twelve releases by 13 using seven transfer minutes.",
        "probe": "Replay hand-only and restored-service schedules with clock and ledger. Restored routine: trolley B4-B7 during 0-3, trolley B8-B11 during 3-6, hand B12 during 6-7; retain the same inspection sequence. Check unload identities, correct releases, bracket counts, boundary occupancy, waits, allowances, and both occupied intervals.",
        "residue_refs": [
          "DEV-U16-C01-SUP1",
          "DEV-U16-C01-SUP2",
          "DEV-U16-C01-SUP3",
          "DEV-U16-C01-SUP4"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Closest operational rival restores the routine powered supply with two four-carrier trips and one hand remainder. Its associated necessity account claims timely release cannot survive withholding powered service; survival and labor preference are separate tests.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause remains unknown.",
          "Later request adaptation is unobserved and does not change fixed demand.",
          "These are finite-model predictions; no empirical distribution or global optimum proof is supplied."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U16"
    },
    {
      "card_id": "DEV-U17-C01",
      "declared_card": {
        "anchor": "Twelve correct releases require uninterrupted thirteen-minute inspection. The initial three carriers bridge the first arrival deadline at boundary 3; B9 needs its stipulated correction despite its packing mark.",
        "burden": "Both paths require thirteen inspection-clerk minutes, twelve seals, and one spare bracket. Candidate predicts seven occupied transfer-clerk minutes and two charge allowances; rival predicts nine transfer minutes and zero charge. Record occupied waiting intervals as labor.",
        "construction": "At boundary 0 start trolley B4-B7 for 0-3 while inspecting B1-B3. Start trolley B8-B11 at 3 for unloading at 6, then hand-carry B12 during 6-7. Completion-first boundaries leave room for both whole trolley loads and B12. Inspect arrivals continuously; B9 occupies 8-10 and B12 finishes at 13.",
        "defeat": "Reject this candidate if its ledger shows blocked unloading, inspection idle time, fewer than twelve correct releases or 120 released brackets at 13, or transfer occupation exceeding the predicted seven minutes. A packing mark cannot rescue a missing correction. No global minimum is claimed.",
        "mutation": "Backcast both successful futures to their boundary-0 fork. Make the first four-carrier trolley departure a checkable present choice while retaining the charge-free hand path through the final comparison.",
        "prediction_candidate": "Derived prediction: zero source unloads at 1, four at 3, nine by 7; twelve correct releases at 13, seven occupied transfer minutes, and no trolley allowances remaining.",
        "prediction_rival": "Derived prediction: one source unload at 1, three at 3, nine by 9; twelve correct releases at 13, nine occupied transfer minutes, and both trolley allowances remaining.",
        "probe": "Execute the candidate boundary-0 departure. At boundaries 1 and 3 inspect source-unload identities and counts against the opposing predictions. Continue its schedule through 13, recording rack occupancy, waits, allowances, correct releases, bracket counts and both clerks busy intervals. Compare the completed trace with the retained finite-model rival schedule; never interrupt or switch an active trip.",
        "residue_refs": [
          "DEV-U17-C01-SUP1",
          "DEV-U17-C01-SUP2",
          "DEV-U17-C01-SUP3",
          "DEV-U17-C01-SUP4"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Start hand-carrying B4 at 0 and continue B4-B12 in nine consecutive one-minute trips, unloading at 1-9. Inspect continuously from the initial rack buffer. This successful future depends on single arrivals and no trolley charge.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause is unknown (U1).",
          "Later request adaptation is unobserved and cannot alter this fixed window (U2).",
          "Both futures are derived from synthetic facts; no empirical comparison, performance distribution or global-optimality proof is supplied (U3)."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U17"
    },
    {
      "card_id": "DEV-U18-C01",
      "declared_card": {
        "anchor": "Nine source unloads feed twelve inspections; B9 requires correction despite its ten-bracket mark. Twelve correct releases by 13 remain mandatory before comparing transfer labor.",
        "burden": "The transfer clerk selects two full loads, switches to hand carrying and records occupied intervals. The inspection clerk counts, corrects B9 using the spare and seals continuously when eligible; predicted inspection occupation is thirteen minutes. Ledger checking adds unmodeled review effort.",
        "construction": "Choose the boundary-ledger dry run before selecting either account. Inspect whenever eligible. Start trolley B4-B7 at 0, then trolley B8-B11 at 3 after unloading, then hand B12 at 6 after unloading. Apply completion-before-unload, entire-load capacity and arrival order at every boundary. Retain A and B through trace checking; their predictions are hypotheses, not received results.",
        "defeat": "Defeat A if batching misses twelve correct releases by 13 or fails to beat a successful hand rival on occupied transfer minutes. Defeat B if the checked batch trace yields nine unloads by 7, twelve releases by 13 and seven occupied transfer minutes while the successful hand rival takes nine. A packing mark never establishes a correct release.",
        "mutation": "Replace routine batch preference with a preselected separating action that tests batch continuity against whole-load blocking while holding inspection rules and demand fixed.",
        "prediction_candidate": "Account A: full trolley loads preserve inspection continuity without blocked unloading. Predicted unload boundaries are 3, 6 and 7; all nine source carriers arrive by 7, all twelve correct releases finish by 13, and transfer occupation is seven minutes versus nine for the successful hand rival.",
        "prediction_rival": "Incompatible account B: whole-load blocking erases batching advantage. It predicts this batch sequence misses twelve releases by 13 or occupies at least nine transfer minutes, allowing successful consecutive hand carrying to win or tie.",
        "probe": "Check both finite schedules in the same boundary ledger through 13. Record carrier identities, rack occupancy including active inspection, waiting loads, both trip allowances, B9 correction, source unloads, completed correct releases and separate clerk intervals. Verify rack space at boundaries 3, 6 and 7, where batch unloading could separate A from B.",
        "residue_refs": [
          "DEV-U18-C01-SUP1",
          "DEV-U18-C01-SUP2",
          "DEV-U18-C01-SUP3",
          "DEV-U18-C01-SUP4"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Consecutive hand trips B4-B12 start at boundaries 0 through 8; use the same continuously eligible inspections, correction, capacity and boundary rules.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
          "O1",
          "O2",
          "O3",
          "O4",
          "O5",
          "O6",
          "O8",
          "P1",
          "P2",
          "M1",
          "M2",
          "M3",
          "M4",
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause is unknown; no additional discrepancy follows.",
          "Later request adaptation remains unobserved and does not change this demand.",
          "No empirical trial distribution or supplied global-optimality proof establishes either account."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U18"
    },
    {
      "card_id": "DEV-U20-C01",
      "declared_card": {
        "anchor": "P1 supplies P2 through the rack. The trolley-favoring routine can migrate this supply function to the available hand carrier, using B1-B3 as an initial buffer.",
        "burden": "The transfer clerk occupies nine minutes under migration, versus seven for the closest rival; neither clerk substitutes roles. Inspection requires thirteen occupied minutes including B9 correction. Clock and ledger maintenance add no modeled labor.",
        "construction": "Start hand trips at boundaries 0-8, unloading B4-B12 at 1-9. Inspect continuously from boundary 0, count and correct B9 during 8-10, and complete B12 at 13. Use the supplied spare bracket and seals.",
        "defeat": "Any inspection gap, blocking unload, incorrect seal, or fewer than twelve correct releases defeats migration completion. The successful seven-minute rival defeats choosing migration under the labor preference. Twelve releases under the delayed-feed attack would defeat the proposed timing-dependency account.",
        "mutation": "Move source-to-rack supply into the hand carrier plus initial rack stock; attack its dependency on timely individual arrivals by withholding the first trip until boundary 3.",
        "prediction_candidate": "Finite-model prediction: immediate migration unloads nine source carriers and releases twelve correctly at 13 using nine transfer minutes. Delayed migration unloads nine by 12 but leaves inspection idle during 3-4 and completes only eleven correct releases by 13.",
        "prediction_rival": "The hybrid rival predicts twelve correct releases at 13 with seven transfer minutes, no unload waits, and peak rack occupancy five. An opposing timing-independent account predicts twelve releases even after delaying hand supply until boundary 3.",
        "probe": "Replay immediate migration, delayed migration, and the hybrid rival in the finite event ledger. Compare carrier identities, unload boundaries, completed correct seals and bracket counts, rack occupancy, charge allowances, and both clerks occupied intervals. The attack separates eleven from twelve releases; the baseline comparison separates nine from seven transfer minutes.",
        "residue_refs": [
          "DEV-U20-C01-SUP1",
          "DEV-U20-C01-SUP2",
          "DEV-U20-C01-SUP3",
          "DEV-U20-C01-SUP4"
        ],
        "resources": [
          "R1",
          "R2",
          "R3",
          "R4",
          "R5",
          "R6",
          "R7"
        ],
        "rival": "Trolley B4-B7 during 0-3, trolley B8-B11 during 3-6, then hand carry B12 during 6-7; inspection remains continuous.",
        "source_refs": [
          "C1",
          "C2",
          "C3",
          "C4",
          "C5",
          "C6",
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
          "M1",
          "M2",
          "M3",
          "M4",
          "U1",
          "U2",
          "U3"
        ],
        "unknowns": [
          "B9 discrepancy cause remains unknown.",
          "Later request-size or frequency adaptation is unobserved and does not alter this window.",
          "No empirical comparison or global optimality proof is supplied; these predictions concern the stipulated finite model."
        ]
      },
      "failure_reason": null,
      "structurally_valid_unit": true,
      "unit_id": "DEV-U20"
    }
  ],
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
    "ordinary_archive": [
      {
        "id": "A1",
        "limits": "Whole-load unloading, two charge allowances, and source order apply.",
        "operation": "Use full powered-trolley loads where remaining source quantity permits, then hand carry the remainder.",
        "probe": "Record unloads, correct releases, occupied transfer minutes, and rack waits.",
        "relation": "P1 feeds the rack and P2 frees space during the window."
      },
      {
        "id": "A2",
        "limits": "One carrier per one-minute trip, rack capacity, and B9 correction time apply.",
        "operation": "Hand carry source carriers consecutively while inspection follows its normal sequence.",
        "probe": "Record both output counts and clerk occupied intervals.",
        "relation": "Single-carrier arrivals supply the existing P1-to-P2 connection."
      },
      {
        "id": "A3",
        "limits": "The checklist creates no parts, removes no transport waits, and proves no future behavior.",
        "operation": "Apply the counting and sealing checklist to every arriving carrier.",
        "probe": "Compare physical counts with packing marks; record completed correct seals.",
        "relation": "P2 establishes whether supplied carriers satisfy release demand."
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
  "case_id": "DEV",
  "job_id": "DEV-review1",
  "required_row_count": 186,
  "rubric": {
    "axes": [
      "anchor_fit",
      "resource_fit",
      "separating",
      "defeat_clear",
      "source_support"
    ],
    "composition_addition": "all four relevant chains and both review locks valid; qualified recipe card distinct by both reviewers against every raw card in O and both parents",
    "coverage_priority": "every declared raw card and all pairs, including anomalous extra declarations",
    "nominal_rows": 315,
    "pair_policy": "either equivalent excludes addition; both distinct proves separation; all remaining pairs unknown and conservative null",
    "qualified": "valid full chain; available resources; both reviewers true on all five axes and distinct against every ordinary archive",
    "review_soft_word_cap": 16000
  },
  "units": [
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U01"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U02"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U03"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U04"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U05"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U06"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U07"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U08"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U09"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U10"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U11"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U12"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U13"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U14"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U15"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U16"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U17"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U18"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U19"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U20"
    },
    {
      "reason": "valid",
      "status": "valid",
      "unit_id": "DEV-U21"
    }
  ]
}
