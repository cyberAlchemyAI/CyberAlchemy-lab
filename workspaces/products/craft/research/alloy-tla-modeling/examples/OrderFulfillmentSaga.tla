---- MODULE OrderFulfillmentSaga ----
EXTENDS Naturals, FiniteSets, TLC

\* Illustrative TLA+ sketch for DomainSpec v2 temporal saga research.
\* Status: not parsed by SANY and not checked by TLC.
\* Purpose: show the first state-machine shape for saga execution, failure
\* safety, compensation, and stale freshness rejection.

VARIABLES step, completed, compensated, status, waiverRead, waiverCurrent

Vars == <<step, completed, compensated, status, waiverRead, waiverCurrent>>

Ops == {
  "CreateOrder",
  "AuthorizePayment",
  "ReserveInventory",
  "CreateShipment"
}

Compensations == {
  "CancelOrder",
  "VoidPayment",
  "ReleaseInventory",
  "CancelShipment"
}

Init ==
  /\ step = "Start"
  /\ completed = {}
  /\ compensated = {}
  /\ status = "Running"
  /\ waiverRead = "ship-after-payment-timeout-v1"
  /\ waiverCurrent = "ship-after-payment-timeout-v1"

CreateOrder ==
  /\ step = "Start"
  /\ step' = "Payment"
  /\ completed' = completed \cup {"CreateOrder"}
  /\ UNCHANGED <<compensated, status, waiverRead, waiverCurrent>>

AuthorizePaymentTimeout ==
  /\ step = "Payment"
  /\ step' = "Inventory"
  /\ completed' = completed \cup {"AuthorizePayment"}
  /\ UNCHANGED <<compensated, status, waiverRead, waiverCurrent>>

ReserveInventory ==
  /\ step = "Inventory"
  /\ step' = "Shipment"
  /\ completed' = completed \cup {"ReserveInventory"}
  /\ UNCHANGED <<compensated, status, waiverRead, waiverCurrent>>

CreateShipmentFails ==
  /\ step = "Shipment"
  /\ step' = "Compensating"
  /\ status' = "Failed"
  /\ UNCHANGED <<completed, compensated, waiverRead, waiverCurrent>>

CompensateInventory ==
  /\ step = "Compensating"
  /\ "ReserveInventory" \in completed
  /\ "ReleaseInventory" \notin compensated
  /\ compensated' = compensated \cup {"ReleaseInventory"}
  /\ UNCHANGED <<step, completed, status, waiverRead, waiverCurrent>>

CompensatePayment ==
  /\ step = "Compensating"
  /\ "AuthorizePayment" \in completed
  /\ "VoidPayment" \notin compensated
  /\ "ReleaseInventory" \in compensated
  /\ compensated' = compensated \cup {"VoidPayment"}
  /\ UNCHANGED <<step, completed, status, waiverRead, waiverCurrent>>

CompensateOrder ==
  /\ step = "Compensating"
  /\ "CreateOrder" \in completed
  /\ "CancelOrder" \notin compensated
  /\ "VoidPayment" \in compensated
  /\ compensated' = compensated \cup {"CancelOrder"}
  /\ UNCHANGED <<step, completed, status, waiverRead, waiverCurrent>>

DeadLetter ==
  /\ step = "Compensating"
  /\ {"ReleaseInventory", "VoidPayment", "CancelOrder"} \subseteq compensated
  /\ step' = "Terminal"
  /\ status' = "TerminalFailure"
  /\ UNCHANGED <<completed, compensated, waiverRead, waiverCurrent>>

WaiverChangesAfterRead ==
  /\ waiverRead = "ship-after-payment-timeout-v1"
  /\ waiverCurrent' = "ship-after-payment-timeout-v2"
  /\ UNCHANGED <<step, completed, compensated, status, waiverRead>>

AcceptFreshnessClaim ==
  /\ step = "Terminal"
  /\ waiverRead = waiverCurrent
  /\ status' = "Accepted"
  /\ UNCHANGED <<step, completed, compensated, waiverRead, waiverCurrent>>

RejectFreshnessClaim ==
  /\ step = "Terminal"
  /\ waiverRead # waiverCurrent
  /\ status' = "Rejected"
  /\ UNCHANGED <<step, completed, compensated, waiverRead, waiverCurrent>>

Next ==
  \/ CreateOrder
  \/ AuthorizePaymentTimeout
  \/ ReserveInventory
  \/ CreateShipmentFails
  \/ CompensateInventory
  \/ CompensatePayment
  \/ CompensateOrder
  \/ DeadLetter
  \/ WaiverChangesAfterRead
  \/ AcceptFreshnessClaim
  \/ RejectFreshnessClaim

Spec == Init /\ [][Next]_Vars

SuccessSafety ==
  status = "Accepted" => step = "Terminal"

FailureSafety ==
  status = "TerminalFailure" =>
    {"ReleaseInventory", "VoidPayment", "CancelOrder"} \subseteq compensated

FreshnessSafety ==
  waiverRead # waiverCurrent => status # "Accepted"

====
