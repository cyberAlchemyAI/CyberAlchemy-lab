import { CompilationRejected } from "./model.js";
import { parseDomainSource } from "./parser.js";
import { selectAlchSourceProfile } from "./profile-architecture.js";
import type { ApplicationFormalSource } from "./formal-claim.js";

export type BehavioralClaim = "closed-state-model" | "executable-runtime";

const reject = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};

/** Source-level closure only. It cannot attest generated or observed runtime behavior. */
export function qualifyBehavioralClaim(source: string, claim: BehavioralClaim) {
  if (claim !== "closed-state-model" && claim !== "executable-runtime") {
    return reject("ALCH_BEHAVIOR_CLAIM", "$claim", `unsupported behavioral claim ${claim}`);
  }
  const selected = selectAlchSourceProfile(source);
  if (selected.profile.id !== "application-v1") {
    return reject("ALCH_BEHAVIOR_PROFILE", "$profile",
      `${claim} requires the canonical application-v1 product profile; ${selected.profile.id} is not sufficient`);
  }
  const parsed = parseDomainSource(source);
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const operations = model.declarations.filter(declaration => declaration.kind === "operation");
  const machines = model.declarations.filter(declaration => declaration.kind === "state-machine");
  if (!operations.length || !machines.length) {
    return reject("ALCH_STATE_MODEL_COVERAGE", "$claim", "closed state model requires declared Operations and State Machines");
  }
  for (const operation of operations) {
    if (!operation.writes.length) reject("ALCH_STATE_MODEL_WRITE", `$operation:${operation.id}`,
      "a closed state model cannot count an Operation without an Entity write");
  }
  for (const machine of machines) {
    if (!machine.subject) reject("ALCH_STATE_MODEL_SUBJECT", `$state-machine:${machine.id}`,
      "closed state model requires an explicit subject Entity");
    for (const transition of machine.transitions) {
      if (!transition.trigger_event) reject("ALCH_STATE_MODEL_TRIGGER", `$state-machine:${machine.id}/${transition.id}`,
        "closed state model requires an explicit trigger Event for every transition");
      const producers = operations.filter(operation => operation.writes.includes(machine.subject!)
        && operation.produces.includes(transition.trigger_event!));
      if (!producers.length) reject("ALCH_STATE_MODEL_PRODUCER", `$state-machine:${machine.id}/${transition.id}`,
        `no Operation both writes ${machine.subject} and produces trigger Event ${transition.trigger_event}`);
    }
  }
  if (claim === "executable-runtime") reject("ALCH_RUNTIME_UNOBSERVED", "$claim",
    "source closure does not observe operation execution, persistence, policy dispatch, or state transitions");
  return {
    schema_version: "alchlang.behavioral-qualification/v1-candidate" as const,
    status: "source-qualified" as const,
    claim,
    profile: "application-v1" as const,
    operations: operations.map(operation => operation.id),
    state_machines: machines.map(machine => machine.id),
    transition_count: machines.reduce((count, machine) => count + machine.transitions.length, 0),
    runtime_guarantees_observed: false as const,
    authority_effect: "none" as const,
  };
}
