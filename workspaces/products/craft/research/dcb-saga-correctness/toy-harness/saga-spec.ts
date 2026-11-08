import { createHash } from "node:crypto";

export type DomainSpecEdgeName =
  | "orchestrates"
  | "triggers-cross"
  | "produces-for"
  | "enforces-cross"
  | "produces"
  | "transitions"
  | "applies"
  | "exposes"
  | "maps";

export type MetaType =
  | "Saga"
  | "Workflow"
  | "Operation"
  | "Rule"
  | "Policy"
  | "Event"
  | "State Machine"
  | "Entity"
  | "Interface"
  | "Mapping"
  | "Query";

export type FactMechanism = "hash" | "rerun" | "dcb";

export type Participant = {
  id: string;
  context: string;
};

export type SagaStep = {
  id: string;
  participant: string;
  forwardOperation: string;
  successEvent: string;
  compensationOperation?: string;
  terminalFailurePolicy?: string;
};

export type DomainSpecEdge = {
  from: string;
  fromType: MetaType;
  edge: DomainSpecEdgeName;
  to: string;
  toType: MetaType;
  note: string;
};

export type PolicyRef = {
  id: string;
  appliesTo: string[];
};

export type StateMachineRef = {
  id: string;
  owner: string;
  states: string[];
};

export type SagaSpec = {
  id: string;
  treatsSagaAsWorkflowSpecialization: boolean;
  participants: Participant[];
  steps: SagaStep[];
  edges: DomainSpecEdge[];
  policies: PolicyRef[];
  stateMachines: StateMachineRef[];
};

export type GraphValidation = {
  status: "pass" | "flag" | "fail";
  errors: string[];
  flags: string[];
  residue: string[];
};

export type TraceEvent = {
  kind: "forward" | "waiver" | "compensation" | "terminal";
  operation: string;
  participant?: string;
  outcome: "success" | "timeout" | "failed" | "waived" | "compensated" | "terminal-failure";
  evidence?: string[];
};

export type BoundedRun = {
  scenario: string;
  trace: TraceEvent[];
  completedSteps: string[];
  failedStep: string;
  terminalState: "success" | "compensatedFailure" | "terminalFailure";
  acceptedSuccess: boolean;
  compensationsRun: string[];
};

export type BehavioralWitness = {
  status: "pass" | "fail";
  assertions: Array<{
    id: string;
    status: "pass" | "fail";
    detail: string;
  }>;
  run: BoundedRun;
  negativeWitness: {
    detectedMissingCompensation: boolean;
    violations: string[];
  };
};

export type Fact = {
  id: string;
  type: string;
  key: string;
  mechanism: FactMechanism;
  content: unknown;
};

export type ReadSetEntry = {
  id: string;
  key: string;
  mechanism: FactMechanism;
  marker: string;
};

export type FreshnessClaim = {
  command: "AcceptSagaProofFreshnessClaim";
  claimId: string;
  readSet: ReadSetEntry[];
  readMarker: Record<string, string>;
};

export type FreshnessResult = {
  status: "accepted" | "rejected";
  claimId: string;
  staleFact?: string;
  currentFact?: string;
  reason: string;
};

export type ToyRunResult = {
  scenario: string;
  witness_kind: "bounded";
  recommendation: "borrow-carefully";
  graph_witness: GraphValidation["status"];
  graph_residue: string[];
  behavioral_witness: BehavioralWitness["status"];
  freshness_claim: FreshnessResult["status"];
  stale_fact: string | null;
  current_fact: string | null;
  deterministic_fact_mechanism: "per-dependency-hash";
  non_rerunnable_fact: string;
  command: FreshnessClaim["command"];
  trace: TraceEvent[];
  graph: GraphValidation;
  behavior: BehavioralWitness;
  freshness: {
    claim: FreshnessClaim;
    result: FreshnessResult;
  };
  notes: string[];
};

const EDGE_SIGNATURES: Record<
  DomainSpecEdgeName,
  Array<{ from: MetaType; to: MetaType }>
> = {
  orchestrates: [{ from: "Workflow", to: "Operation" }],
  "triggers-cross": [{ from: "Event", to: "Operation" }],
  "produces-for": [{ from: "Operation", to: "Entity" }],
  "enforces-cross": [{ from: "Rule", to: "Operation" }],
  produces: [{ from: "Operation", to: "Event" }],
  transitions: [{ from: "Event", to: "State Machine" }],
  applies: [{ from: "Policy", to: "Operation" }],
  exposes: [
    { from: "Interface", to: "Operation" },
    { from: "Interface", to: "Query" },
  ],
  maps: [
    { from: "Mapping", to: "Entity" },
    { from: "Mapping", to: "Interface" },
  ],
};

export function stableStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function hashFact(value: unknown): string {
  return createHash("sha256").update(stableStringify(value)).digest("hex");
}

export function validateGraph(spec: SagaSpec): GraphValidation {
  const errors: string[] = [];
  const flags: string[] = [];
  const residue: string[] = [];
  const participants = new Set(spec.participants.map((participant) => participant.id));

  for (const step of spec.steps) {
    if (!participants.has(step.participant)) {
      errors.push(`Step ${step.id} references unknown participant ${step.participant}.`);
    }
    if (!step.compensationOperation && !step.terminalFailurePolicy) {
      errors.push(
        `Step ${step.id} has no compensation operation or terminal failure policy.`,
      );
    }
  }

  for (const edge of spec.edges) {
    const signatures = EDGE_SIGNATURES[edge.edge];
    const exactMatch = signatures.some(
      (signature) => signature.from === edge.fromType && signature.to === edge.toType,
    );
    const sagaOrchestratesResidue =
      edge.edge === "orchestrates" &&
      edge.fromType === "Saga" &&
      edge.toType === "Operation" &&
      !spec.treatsSagaAsWorkflowSpecialization;

    if (sagaOrchestratesResidue) {
      const message =
        "orchestrates signature for Saga is residue: RELATIONSHIPS.md types orchestrates as Workflow -> Operation[].";
      flags.push(message);
      residue.push(message);
      continue;
    }

    if (!exactMatch) {
      errors.push(
        `${edge.edge} has invalid signature ${edge.fromType} -> ${edge.toType} for ${edge.from} -> ${edge.to}.`,
      );
    }
  }

  return {
    status: errors.length > 0 ? "fail" : flags.length > 0 ? "flag" : "pass",
    errors,
    flags,
    residue,
  };
}

export function enumerateRuns(spec: SagaSpec): BoundedRun {
  const completedSteps: string[] = [];
  const trace: TraceEvent[] = [];

  const emitForward = (
    operation: string,
    participant: string,
    outcome: TraceEvent["outcome"],
    evidence: string[] = [],
  ) => {
    trace.push({ kind: "forward", operation, participant, outcome, evidence });
  };

  emitForward("CreateOrder", "ordering", "success");
  completedSteps.push("CreateOrder");

  emitForward("AuthorizePayment", "payment", "timeout", [
    "ExternalEvidenceReceiptRecorded:payment-auth-provider-r42",
  ]);
  trace.push({
    kind: "waiver",
    operation: "HumanWaiverApplied:waiver:ship-after-payment-timeout-v1",
    participant: "payment",
    outcome: "waived",
    evidence: ["ExternalEvidenceReceiptRecorded:payment-auth-provider-r42"],
  });
  completedSteps.push("AuthorizePayment");

  emitForward("ReserveInventory", "inventory", "success");
  completedSteps.push("ReserveInventory");

  emitForward("CreateShipment", "shipping", "failed");

  const completedCompensatable = spec.steps
    .filter((step) => completedSteps.includes(step.forwardOperation))
    .filter((step) => step.compensationOperation)
    .reverse();

  for (const step of completedCompensatable) {
    trace.push({
      kind: "compensation",
      operation: step.compensationOperation as string,
      participant: step.participant,
      outcome: "compensated",
    });
  }

  trace.push({
    kind: "terminal",
    operation: "DeadLetterPolicy",
    outcome: "terminal-failure",
    evidence: ["CreateShipment failed after ReserveInventory succeeded"],
  });

  return {
    scenario: spec.id,
    trace,
    completedSteps,
    failedStep: "CreateShipment",
    terminalState: "compensatedFailure",
    acceptedSuccess: false,
    compensationsRun: completedCompensatable.map(
      (step) => step.compensationOperation as string,
    ),
  };
}

export function assertBehavioralObligations(
  spec: SagaSpec,
  run: BoundedRun,
): BehavioralWitness {
  const expectedCompensations = spec.steps
    .filter((step) => run.completedSteps.includes(step.forwardOperation))
    .filter((step) => step.compensationOperation)
    .map((step) => step.compensationOperation as string)
    .reverse();

  const noFalseSuccess = !run.acceptedSuccess && run.terminalState !== "success";
  const completedStepsCompensated = expectedCompensations.every((operation) =>
    run.compensationsRun.includes(operation),
  );

  const brokenSpec: SagaSpec = {
    ...spec,
    steps: spec.steps.map((step) =>
      step.forwardOperation === "ReserveInventory"
        ? { ...step, compensationOperation: undefined, terminalFailurePolicy: undefined }
        : step,
    ),
  };
  const brokenGraph = validateGraph(brokenSpec);

  const assertions = [
    {
      id: "success-not-accepted-after-shipment-failure",
      status: noFalseSuccess ? "pass" : "fail",
      detail:
        "CreateShipment failed; the bounded run must not accept saga success.",
    },
    {
      id: "completed-compensatable-steps-compensated",
      status: completedStepsCompensated ? "pass" : "fail",
      detail: `Expected compensations: ${expectedCompensations.join(", ")}.`,
    },
    {
      id: "missing-compensation-detected",
      status: brokenGraph.errors.length > 0 ? "pass" : "fail",
      detail:
        "Removing ReleaseInventory from ReserveInventory must produce a graph violation.",
    },
  ] as const;

  return {
    status: assertions.every((assertion) => assertion.status === "pass")
      ? "pass"
      : "fail",
    assertions: assertions.map((assertion) => ({ ...assertion })),
    run,
    negativeWitness: {
      detectedMissingCompensation: brokenGraph.errors.length > 0,
      violations: brokenGraph.errors,
    },
  };
}

export function buildReadSet(facts: Fact[]): ReadSetEntry[] {
  return facts.map((fact) => ({
    id: fact.id,
    key: fact.key,
    mechanism: fact.mechanism,
    marker: hashFact(fact),
  }));
}

export function buildFreshnessClaim(
  claimId: string,
  readSet: ReadSetEntry[],
): FreshnessClaim {
  return {
    command: "AcceptSagaProofFreshnessClaim",
    claimId,
    readSet,
    readMarker: Object.fromEntries(
      readSet.map((entry) => [entry.key, entry.marker]),
    ),
  };
}

export function acceptSagaProofFreshnessClaim(
  claim: FreshnessClaim,
  currentFacts: Fact[],
): FreshnessResult {
  const currentByKey = new Map(
    currentFacts.map((fact) => [
      fact.key,
      {
        fact,
        marker: hashFact(fact),
      },
    ]),
  );

  for (const entry of claim.readSet) {
    const current = currentByKey.get(entry.key);
    if (!current) {
      return {
        status: "rejected",
        claimId: claim.claimId,
        staleFact: entry.id,
        reason: `Missing current fact for read-set key ${entry.key}.`,
      };
    }
    if (current.marker !== entry.marker) {
      const deterministic = entry.mechanism === "hash" || entry.mechanism === "rerun";
      return {
        status: "rejected",
        claimId: claim.claimId,
        staleFact: entry.id,
        currentFact: current.fact.id,
        reason: deterministic
          ? `Deterministic fact ${entry.key} changed; rerun/hash refresh required before acceptance.`
          : `Non-rerunnable fact ${entry.key} changed after the read marker; DCB freshness rejects acceptance.`,
      };
    }
  }

  return {
    status: "accepted",
    claimId: claim.claimId,
    reason: "All read-set markers match current facts.",
  };
}

export function buildToyRunResult(input: {
  spec: SagaSpec;
  graph: GraphValidation;
  behavior: BehavioralWitness;
  claim: FreshnessClaim;
  freshnessResult: FreshnessResult;
}): ToyRunResult {
  return {
    scenario: input.spec.id,
    witness_kind: "bounded",
    recommendation: "borrow-carefully",
    graph_witness: input.graph.status,
    graph_residue: input.graph.residue,
    behavioral_witness: input.behavior.status,
    freshness_claim: input.freshnessResult.status,
    stale_fact: input.freshnessResult.staleFact ?? null,
    current_fact: input.freshnessResult.currentFact ?? null,
    deterministic_fact_mechanism: "per-dependency-hash",
    non_rerunnable_fact: "HumanWaiverApplied:waiver:ship-after-payment-timeout-v1",
    command: input.claim.command,
    trace: input.behavior.run.trace,
    graph: input.graph,
    behavior: input.behavior,
    freshness: {
      claim: input.claim,
      result: input.freshnessResult,
    },
    notes: [
      "This is a TypeScript bounded witness, not a formal proof.",
      "DCB guards acceptance freshness; it does not prove saga behavior.",
      "Saga orchestrates relationship signature is preserved as residue instead of mutating RELATIONSHIPS.md.",
    ],
  };
}
