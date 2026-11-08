import type { Fact, SagaSpec } from "./saga-spec.ts";

export const orderFulfillmentSaga: SagaSpec = {
  id: "OrderFulfillmentSaga",
  treatsSagaAsWorkflowSpecialization: false,
  participants: [
    { id: "ordering", context: "Ordering bounded context" },
    { id: "payment", context: "Payment bounded context" },
    { id: "inventory", context: "Inventory bounded context" },
    { id: "shipping", context: "Shipping bounded context" },
  ],
  steps: [
    {
      id: "step-create-order",
      participant: "ordering",
      forwardOperation: "CreateOrder",
      successEvent: "OrderCreated",
      compensationOperation: "CancelOrder",
    },
    {
      id: "step-authorize-payment",
      participant: "payment",
      forwardOperation: "AuthorizePayment",
      successEvent: "PaymentAuthorized",
      compensationOperation: "VoidPayment",
    },
    {
      id: "step-reserve-inventory",
      participant: "inventory",
      forwardOperation: "ReserveInventory",
      successEvent: "InventoryReserved",
      compensationOperation: "ReleaseInventory",
    },
    {
      id: "step-create-shipment",
      participant: "shipping",
      forwardOperation: "CreateShipment",
      successEvent: "ShipmentCreated",
      compensationOperation: "CancelShipment",
      terminalFailurePolicy: "DeadLetterPolicy",
    },
  ],
  policies: [
    {
      id: "RetryPolicy",
      appliesTo: ["AuthorizePayment", "CreateShipment"],
    },
    {
      id: "TimeoutPolicy",
      appliesTo: ["AuthorizePayment"],
    },
    {
      id: "DeadLetterPolicy",
      appliesTo: ["CreateShipment"],
    },
    {
      id: "CompensationOrderPolicy",
      appliesTo: ["ReleaseInventory", "VoidPayment", "CancelOrder"],
    },
  ],
  stateMachines: [
    {
      id: "OrderFulfillmentSagaState",
      owner: "OrderFulfillmentSaga",
      states: ["Started", "PaymentTimedOut", "InventoryReserved", "CompensatedFailure"],
    },
    {
      id: "PaymentAuthorizationState",
      owner: "payment",
      states: ["Requested", "TimedOut", "Waived", "Voided"],
    },
  ],
  edges: [
    {
      from: "OrderFulfillmentSaga",
      fromType: "Saga",
      edge: "orchestrates",
      to: "CreateOrder",
      toType: "Operation",
      note: "Kept as residue because RELATIONSHIPS.md currently types orchestrates as Workflow -> Operation[].",
    },
    {
      from: "OrderCreated",
      fromType: "Event",
      edge: "triggers-cross",
      to: "AuthorizePayment",
      toType: "Operation",
      note: "Ordering completion activates payment authorization.",
    },
    {
      from: "PaymentAuthorized",
      fromType: "Event",
      edge: "triggers-cross",
      to: "ReserveInventory",
      toType: "Operation",
      note: "Payment completion activates inventory reservation.",
    },
    {
      from: "InventoryReserved",
      fromType: "Event",
      edge: "triggers-cross",
      to: "CreateShipment",
      toType: "Operation",
      note: "Inventory reservation activates shipment creation.",
    },
    {
      from: "ReserveInventory",
      fromType: "Operation",
      edge: "produces-for",
      to: "InventoryReservation",
      toType: "Entity",
      note: "Inventory operation writes participant-owned reservation state.",
    },
    {
      from: "ShipmentAllowedAfterTimeoutRule",
      fromType: "Rule",
      edge: "enforces-cross",
      to: "CreateShipment",
      toType: "Operation",
      note: "Shipping is constrained by a cross-context payment timeout waiver rule.",
    },
    {
      from: "CreateShipment",
      fromType: "Operation",
      edge: "produces",
      to: "ShipmentCreationFailed",
      toType: "Event",
      note: "Shipment failure triggers compensation flow.",
    },
    {
      from: "ShipmentCreationFailed",
      fromType: "Event",
      edge: "transitions",
      to: "OrderFulfillmentSagaState",
      toType: "State Machine",
      note: "Saga transitions into compensated failure handling.",
    },
    {
      from: "CompensationOrderPolicy",
      fromType: "Policy",
      edge: "applies",
      to: "ReleaseInventory",
      toType: "Operation",
      note: "Compensation ordering starts with the latest completed participant.",
    },
    {
      from: "PaymentAPI",
      fromType: "Interface",
      edge: "exposes",
      to: "AuthorizePayment",
      toType: "Operation",
      note: "Saga calls payment through participant interface.",
    },
    {
      from: "PaymentAuthorizationMapping",
      fromType: "Mapping",
      edge: "maps",
      to: "PaymentAPI",
      toType: "Interface",
      note: "External payment receipt is mapped at the payment boundary.",
    },
  ],
};

export const readSetFacts: Fact[] = [
  {
    id: "SagaDeclared:OrderFulfillmentSaga",
    type: "SagaDeclared",
    key: "SagaDeclared:OrderFulfillmentSaga",
    mechanism: "hash",
    content: {
      sagaId: orderFulfillmentSaga.id,
      participantIds: orderFulfillmentSaga.participants.map((participant) => participant.id),
    },
  },
  {
    id: "SagaStepDeclared:CreateShipment",
    type: "SagaStepDeclared",
    key: "SagaStepDeclared:CreateShipment",
    mechanism: "hash",
    content: orderFulfillmentSaga.steps.find(
      (step) => step.forwardOperation === "CreateShipment",
    ),
  },
  {
    id: "CompensationOperationDeclared:ReleaseInventory",
    type: "CompensationOperationDeclared",
    key: "CompensationOperationDeclared:ReleaseInventory",
    mechanism: "hash",
    content: orderFulfillmentSaga.steps.find(
      (step) => step.compensationOperation === "ReleaseInventory",
    ),
  },
  {
    id: "PolicyObserved:CompensationOrderPolicy",
    type: "PolicyObserved",
    key: "PolicyObserved:CompensationOrderPolicy",
    mechanism: "hash",
    content: orderFulfillmentSaga.policies.find(
      (policy) => policy.id === "CompensationOrderPolicy",
    ),
  },
  {
    id: "PropertyTestRunRecorded:run-ts-bounded-001",
    type: "PropertyTestRunRecorded",
    key: "PropertyTestRunRecorded:run-ts-bounded-001",
    mechanism: "hash",
    content: {
      runner: "tsx",
      harness: "toy-harness/run-toy.ts",
      boundedWitness: true,
    },
  },
  {
    id: "HumanWaiverApplied:waiver:ship-after-payment-timeout-v1",
    type: "HumanWaiverApplied",
    key: "HumanWaiverApplied:ship-after-payment-timeout",
    mechanism: "dcb",
    content: {
      waiverId: "waiver:ship-after-payment-timeout-v1",
      decision: "allow-shipment-after-timeout-with-provider-receipt",
      authorizedBy: "human-review",
      receiptRequired: "ExternalEvidenceReceiptRecorded:payment-auth-provider-r42",
    },
  },
  {
    id: "ExternalEvidenceReceiptRecorded:payment-auth-provider-r42",
    type: "ExternalEvidenceReceiptRecorded",
    key: "ExternalEvidenceReceiptRecorded:payment-auth-provider-r42",
    mechanism: "dcb",
    content: {
      receiptId: "payment-auth-provider-r42",
      provider: "payment-provider",
      status: "authorization-observed-after-timeout",
    },
  },
];

export const currentFactsAfterStaleWaiver: Fact[] = readSetFacts.map((fact) =>
  fact.key === "HumanWaiverApplied:ship-after-payment-timeout"
    ? {
        ...fact,
        id: "HumanWaiverApplied:waiver:ship-after-payment-timeout-v2",
        content: {
          waiverId: "waiver:ship-after-payment-timeout-v2",
          decision: "do-not-allow-shipment-after-timeout-without-reverification",
          authorizedBy: "human-review",
          receiptRequired: "ExternalEvidenceReceiptRecorded:payment-auth-provider-r42",
        },
      }
    : fact,
);
