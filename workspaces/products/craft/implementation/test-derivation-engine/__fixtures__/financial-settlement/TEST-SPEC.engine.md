# Test Spec (engine-derived): financial-settlement

<!-- ENGINE-PROVENANCE
format_version: 1
feature: financial-settlement
engine_commit: 53d8f08
inputs:
  domain.md: sha256:2a309a573646db82307cbe66fec3729bdde4be0e8caa06487a7b626c88a6c8b0
  events.md: sha256:c8bca48654b2d5ec82c39c93e449895eb3ed548e1ec1ab96f9d91311fe39796e
  interfaces.md: sha256:543f0e8e467aa8d6f0fe0ed960a4e9919851a39f606e4699a7ea78a97e2679cf
  mappings.md: sha256:51397c55845dcbed8c58c07e6cf6e77bfb78466f1d7b4918d33c1331ffb01060
  operations.md: sha256:af758df82c1fbe1dc502d1311e455325db41669791423bf7612a7d0ffd897de6
  queries.md: sha256:f8941479819137ab5d3739ffbb058a10e504bff7cfba264ea4c4282885549417
  states.md: sha256:68d3341678352eabeb34c40116317d8f27cb4a3115514556067e0804139abcb5
  workflows.md: sha256:b310c983704dd615bd185ad999c4b6bdd9e0ed0dda9a2b9be365bb504bf0f7c2
note: the ENGINE-REGION below is deterministic δ output, replaced wholesale on
      re-derive. Do not hand-edit it. Run `check` to detect drift.
-->

<!-- ENGINE-REGION-START — deterministic δ output; overwritten on re-derive, do not hand-edit -->

## Source Completeness Gate

| Doc | Status |
| --- | --- |
| states.md | present |
| operations.md | present |
| interfaces.md | present |
| events.md | present |
| workflows.md | present |
| queries.md | present |
| mappings.md | present |
| domain.md | present |
| rules.md | absent |

## Coverage Summary

Total obligations: 79
Spec-formalization metric (pure / (pure + needs_formal)): 96.0%

| Tier | Count |
| --- | --- |
| derivable-needs-harness | 54 |
| derivable-pure | 24 |
| needs-formal | 1 |

| Rule class | Count |
| --- | --- |
| calculation | 5 |
| contract | 10 |
| domain-enum | 1 |
| domain-field | 11 |
| error-obligation | 3 |
| event-obligation | 4 |
| invalid-transition | 9 |
| invariant | 2 |
| mapping-row | 2 |
| needs-formal | 1 |
| postcondition | 4 |
| query-behavior | 1 |
| rule-validation | 13 |
| valid-transition | 4 |
| workflow-step | 9 |

## Suite Partition

- Unit (derivable-pure): 24
- Integration (derivable-needs-harness): 54
- Unresolved (needs-formal): 1

## Obligations

| ID | Key | Rule | Tier | Source | Obligation |
| --- | --- | --- | --- | --- | --- |
| FS-DOM-001 | 034abae7 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:1 | SettlementResult.periodStart: string (valid date) |
| FS-QRY-001 | 0411cf5a | query-behavior | derivable-needs-harness | queries.md#GetSettlementPreview | Query GetSettlementPreview returns its projected read model without side effects |
| FS-CALC-001 | 05503a8a | calculation | derivable-pure | operations.md#GenerateSettlement:calculation:2 | Calculation C3: false-branch |
| FS-WF-001 | 06cf2453 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:4 | Workflow SettlementWorkflow step 5 (Return response) succeeds |
| FS-DOM-002 | 091b46ec | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:6 | SettlementResult.previousMakeup: integer (non-negative) |
| FS-WF-002 | 0d8d7eb4 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:3 | Workflow SettlementWorkflow step 4 (Persist side-effects) succeeds |
| FS-TR-001 | 0ee36a27 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:SIDE_EFFECTS_PERSISTED:GenerateSettlement | Event GenerateSettlement in state SIDE_EFFECTS_PERSISTED is rejected (no valid transition) |
| FS-DOM-003 | 1954c405 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:2 | SettlementResult.periodEnd: string (valid date) |
| FS-WF-003 | 2b076f26 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:0 | Workflow SettlementWorkflow step 1 (Validate request payload) on failure: return 400 |
| FS-IF-001 | 30a3257c | contract | derivable-needs-harness | interfaces.md#POST /settlements:response:0 | POST /settlements -> 200 (Success) |
| FS-CALC-002 | 35eb1891 | calculation | derivable-pure | operations.md#GenerateSettlement:calculation:2 | Calculation C3: true-branch |
| FS-RULE-001 | 39148629 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:0 | Rule R1: present (existence) |
| FS-TR-002 | 416e9559 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:COMPLETED:GenerateSettlement | Event GenerateSettlement in state COMPLETED is rejected (no valid transition) |
| FS-WF-004 | 480a5040 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:2 | Workflow SettlementWorkflow step 3 (Compute policy result) on failure: return error |
| FS-EVT-001 | 4e5bce9b | event-obligation | derivable-needs-harness | events.md#PayoutCreated | Event PayoutCreated is emitted with valid payload |
| FS-RULE-002 | 5253b0f3 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:2 | Rule R3: above (range) |
| FS-RULE-003 | 53acb8c5 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:3 | Rule R4: first-allowed (count cap) |
| FS-DOM-004 | 55d5be30 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:7 | SettlementResult.newMakeup: integer (non-negative) |
| FS-TR-003 | 564884a1 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:COMPUTED:PayoutCreated or no-payout | Event PayoutCreated or no-payout in state COMPUTED is rejected (no valid transition) |
| FS-POST-001 | 5684ed00 | postcondition | derivable-pure | operations.md#GenerateSettlement:postcondition:3 | Postcondition P4: Creates PAYOUT transaction when payout > 0 and no duplicate exists. |
| FS-IF-002 | 57999404 | contract | derivable-needs-harness | interfaces.md#POST /settlements:response:3 | POST /settlements -> 500 (Unexpected error) |
| FS-ERR-001 | 596d6f2a | error-obligation | derivable-needs-harness | operations.md#GenerateSettlement:errorstate:2 | Error mapping for GenerateSettlement: "Repository failure" -> 500 internal error |
| FS-POST-002 | 5a31788c | postcondition | derivable-pure | operations.md#GenerateSettlement:postcondition:2 | Postcondition P3: Creates MAKEUP_APPLIED transaction when applied amount > 0 and no duplicate exists. |
| FS-TR-004 | 5e464341 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:VALIDATED:PayoutCreated or no-payout | Event PayoutCreated or no-payout in state VALIDATED is rejected (no valid transition) |
| FS-TR-005 | 63739b2f | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:COMPUTED:GenerateSettlement | Event GenerateSettlement in state COMPUTED is rejected (no valid transition) |
| FS-WF-005 | 67121923 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:2 | Workflow SettlementWorkflow step 3 (Compute policy result) succeeds |
| FS-ERR-002 | 6c586013 | error-obligation | derivable-needs-harness | operations.md#GenerateSettlement:errorstate:1 | Error mapping for GenerateSettlement: "Player not found" -> 404 not found error |
| FS-CALC-003 | 6eb2cdb8 | calculation | derivable-pure | operations.md#GenerateSettlement:calculation:0 | Calculation C1: sum(relevantRecords.profit) |
| FS-RULE-004 | 6f952f4d | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:2 | Rule R3: lower-inclusive (range) |
| FS-IF-003 | 72fca8a9 | contract | derivable-needs-harness | interfaces.md#POST /settlements:response:2 | POST /settlements -> 404 (Player not found) |
| FS-TR-006 | 7facbe81 | valid-transition | derivable-needs-harness | states.md#SettlementExecutionState:transition:0 | Transition [new] --GenerateSettlement--> VALIDATED succeeds when guarded |
| FS-DOM-005 | 82028c98 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:3 | SettlementResult.totalProfit: integer (derived sum) |
| FS-ERR-003 | 825f3028 | error-obligation | derivable-needs-harness | operations.md#GenerateSettlement:errorstate:0 | Error mapping for GenerateSettlement: "Missing required fields" -> 400 validation error |
| FS-WF-006 | 853613b7 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:3 | Workflow SettlementWorkflow step 4 (Persist side-effects) on failure: return error |
| FS-DOM-006 | 86c0f750 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:10 | SettlementResult.totalPayout: integer (non-negative) |
| FS-RULE-005 | 8709b665 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:1 | Rule R2: conjunct 0 missing |
| FS-IF-004 | 879db1fd | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:4 | GET /settlements/preview -> 404 (Player not found) |
| FS-MAP-001 | 894ad530 | mapping-row | derivable-needs-harness | mappings.md#SettlementResultToResponse | Mapping SettlementResultToResponse (SettlementResult -> API Response) maps all fields correctly |
| FS-DOM-007 | 8a708347 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:4 | SettlementResult.totalRakeback: integer (derived sum) |
| FS-CALC-004 | 8cb87e0b | calculation | derivable-pure | operations.md#GenerateSettlement:calculation:1 | Calculation C2: sum(relevantRecords.rakeback) |
| FS-RULE-006 | 8d751f3f | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:2 | Rule R3: below (range) |
| FS-EVT-002 | 8d97a003 | event-obligation | derivable-needs-harness | events.md#SettlementGenerated | Event SettlementGenerated is emitted with valid payload |
| FS-RULE-007 | 8f5bc6fe | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:0 | Rule R1: absent (existence) |
| FS-IF-005 | 919def7a | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:3 | GET /settlements/preview -> 403 (Missing permission) |
| FS-NF-001 | 94c269af | needs-formal | needs-formal | states.md#SettlementExecutionState:invariant:0 | Invariant I1: needs_formal (prose Formal) |
| FS-RULE-008 | 96c58733 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:1 | Rule R2: conjunct 1 missing |
| FS-POST-003 | 9ac781e3 | postcondition | derivable-pure | operations.md#GenerateSettlement:postcondition:1 | Postcondition P2: Updates player makeup when `newMakeup != previousMakeup`. |
| FS-RULE-009 | 9c8b1f9f | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:4 | Rule R5: duplicate-capped (count cap) |
| FS-DOM-008 | a0c30fe2 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:0 | SettlementResult.playerId: string (required) |
| FS-EVT-003 | a2206518 | event-obligation | derivable-needs-harness | events.md#SettlementGenerated:consumer:0 | Event SettlementGenerated consumed by finance reporting |
| FS-RULE-010 | a323ca00 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:3 | Rule R4: duplicate-capped (count cap) |
| FS-TR-007 | a4946c90 | valid-transition | derivable-needs-harness | states.md#SettlementExecutionState:transition:1 | Transition VALIDATED --GenerateSettlement--> COMPUTED succeeds when guarded |
| FS-DOM-009 | a7330941 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:5 | SettlementResult.netProfit: integer (informational) |
| FS-IF-006 | a79e77a0 | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:2 | GET /settlements/preview -> 401 (Missing/invalid token) |
| FS-TR-008 | b1d7d600 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:COMPLETED:SettlementGenerated | Event SettlementGenerated in state COMPLETED is rejected (no valid transition) |
| FS-TR-009 | b58f2566 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:SIDE_EFFECTS_PERSISTED:SettlementGenerated | Event SettlementGenerated in state SIDE_EFFECTS_PERSISTED is rejected (no valid transition) |
| FS-INV-001 | b8be9436 | invariant | derivable-pure | states.md#SettlementExecutionState:invariant:1 | Invariant I2: first-allowed (count cap) |
| FS-TR-010 | cc14d5df | valid-transition | derivable-needs-harness | states.md#SettlementExecutionState:transition:2 | Transition COMPUTED --SettlementGenerated--> SIDE_EFFECTS_PERSISTED succeeds when guarded |
| FS-IF-007 | d00a1434 | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:5 | GET /settlements/preview -> 500 (Unexpected error) |
| FS-ENUM-001 | d233f5aa | domain-enum | derivable-needs-harness | domain.md#SettlementTransactionType:enum | SettlementTransactionType vocabulary is exactly {MAKEUP_APPLIED,PAYOUT} |
| FS-IF-008 | d4a3c1f0 | contract | derivable-needs-harness | interfaces.md#POST /settlements:response:1 | POST /settlements -> 400 (Missing required fields) |
| FS-TR-011 | d52c1653 | valid-transition | derivable-needs-harness | states.md#SettlementExecutionState:transition:3 | Transition SIDE_EFFECTS_PERSISTED --PayoutCreated or no-payout--> COMPLETED succeeds when guarded |
| FS-INV-002 | d564ed0a | invariant | derivable-pure | states.md#SettlementExecutionState:invariant:1 | Invariant I2: duplicate-capped (count cap) |
| FS-DOM-010 | d71b606b | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:9 | SettlementResult.playerRakebackShare: integer (non-negative) |
| FS-WF-007 | dc04e66b | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:1 | Workflow SettlementWorkflow step 2 (Load dependencies) on failure: return error |
| FS-TR-012 | de239b75 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:COMPLETED:PayoutCreated or no-payout | Event PayoutCreated or no-payout in state COMPLETED is rejected (no valid transition) |
| FS-DOM-011 | df09b760 | domain-field | derivable-needs-harness | domain.md#SettlementResult:field:8 | SettlementResult.playerProfitShare: integer (non-negative) |
| FS-RULE-011 | e137e691 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:4 | Rule R5: first-allowed (count cap) |
| FS-TR-013 | e42d39f9 | invalid-transition | derivable-needs-harness | states.md#SettlementExecutionState:invalid:VALIDATED:SettlementGenerated | Event SettlementGenerated in state VALIDATED is rejected (no valid transition) |
| FS-EVT-004 | e43d0434 | event-obligation | derivable-needs-harness | events.md#PayoutCreated:consumer:0 | Event PayoutCreated consumed by payout operations |
| FS-MAP-002 | e747ab61 | mapping-row | derivable-needs-harness | mappings.md#SettlementRequestToInput | Mapping SettlementRequestToInput (API Request -> GenerateSettlement input) maps all fields correctly |
| FS-IF-009 | e83e0193 | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:0 | GET /settlements/preview -> 200 (Success) |
| FS-IF-010 | e8b173ec | contract | derivable-needs-harness | interfaces.md#GET /settlements/preview:response:1 | GET /settlements/preview -> 400 (Missing required params) |
| FS-WF-008 | eb6243ab | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:0 | Workflow SettlementWorkflow step 1 (Validate request payload) succeeds |
| FS-CALC-005 | eb6f8f4d | calculation | derivable-pure | operations.md#GenerateSettlement:calculation:3 | Calculation C4: newMakeup = max(0, previousDebt - totalProfit - totalRakeback) |
| FS-POST-004 | ec5e9253 | postcondition | derivable-pure | operations.md#GenerateSettlement:postcondition:0 | Postcondition P1: Returns one [SettlementResult](domain.md#settlementresult). |
| FS-WF-009 | ed9c15e5 | workflow-step | derivable-needs-harness | workflows.md#SettlementWorkflow:step:1 | Workflow SettlementWorkflow step 2 (Load dependencies) succeeds |
| FS-RULE-012 | f36feba9 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:1 | Rule R2: conjunct 2 missing |
| FS-RULE-013 | fbc9d875 | rule-validation | derivable-pure | operations.md#GenerateSettlement:rule:2 | Rule R3: upper-inclusive (range) |

## Unresolved Formal Gaps

needs_formal (un-formalized — no closed checkable expression): 1

- `FS-NF-001` states.md#SettlementExecutionState:invariant:0 — Invariant I1: needs_formal (prose Formal)

needs-harness (derivable, requires a runtime/effect to test): 54

<!-- ENGINE-REGION-END -->
