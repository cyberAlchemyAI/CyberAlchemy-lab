import {createHash} from "node:crypto";

import {
  canonicalModuleJson,
  digestModuleValue,
} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {createDefineSessionClient} from "../../src/durable-session-runtime.mjs";
import {runOntologyStage} from "../ontology-stage-port/index.mjs";

export const DEFINE_CLIENT_RESULT_SCHEMA = "cav2.define-client-result/v1";

const REQUEST_SCHEMAS = Object.freeze({
  startWork: "cav2.define-client-start/v1",
  resumeWork: "cav2.define-client-resume/v1",
  listStages: "cav2.define-client-list-stages/v1",
  nextQuestion: "cav2.define-client-next-question/v1",
  submitResponse: "cav2.define-client-submit-response/v1",
  inspectReadiness: "cav2.define-client-inspect-readiness/v1",
  confirmArtifact: "cav2.define-client-confirm-artifact/v1",
  exportArtifact: "cav2.define-client-export-artifact/v1",
});

const REQUEST_KEYS = Object.freeze({
  startWork: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "stage_id", "goal", "intent", "context", "consumer", "context_sufficiency_evaluation", "context_candidates", "sources", "evidence", "owners", "authority_envelope", "prerequisite_receipts"],
  resumeWork: ["schema_version", "work_id"],
  listStages: ["schema_version"],
  nextQuestion: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context"],
  submitResponse: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "response_kind", "response", "reason", "evidence"],
  inspectReadiness: ["schema_version", "work_id"],
  confirmArtifact: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "candidate_bytes"],
  exportArtifact: ["schema_version", "work_id", "candidate_bytes"],
});

const REQUIRED_KEYS = Object.freeze({
  startWork: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "stage_id", "goal", "intent", "context", "consumer"],
  resumeWork: ["schema_version", "work_id"],
  listStages: ["schema_version"],
  nextQuestion: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context"],
  submitResponse: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "response_kind"],
  inspectReadiness: ["schema_version", "work_id"],
  confirmArtifact: ["schema_version", "command_id", "work_id", "expected_revision", "actor_access_context", "candidate_bytes"],
  exportArtifact: ["schema_version", "work_id", "candidate_bytes"],
});

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
}

function clone(value) {
  return JSON.parse(canonicalModuleJson(value));
}

function freeze(value) {
  if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
  Object.freeze(value);
  for (const child of Object.values(value)) freeze(child);
  return value;
}

function text(value) {
  return typeof value === "string" ? value.trim() : "";
}

function exactRequest(operation, request) {
  if (!record(request) || request.schema_version !== REQUEST_SCHEMAS[operation]) return false;
  const allowed = new Set(REQUEST_KEYS[operation]);
  const actor = request.actor_access_context;
  const actorValid = actor === undefined || (record(actor)
    && Object.keys(actor).every((key) => ["actor_ref", "allowed_effects"].includes(key))
    && text(actor.actor_ref) && Array.isArray(actor.allowed_effects)
    && actor.allowed_effects.every((item) => text(item))
    && new Set(actor.allowed_effects).size === actor.allowed_effects.length);
  return actorValid && Object.keys(request).every((key) => allowed.has(key))
    && REQUIRED_KEYS[operation].every((key) => Object.hasOwn(request, key));
}

function result(operation, {ok, disposition, workId = null, revision = null, value = null, reasonCodes = []}) {
  const material = clone({
    schema_version: DEFINE_CLIENT_RESULT_SCHEMA,
    operation,
    ok,
    disposition,
    work_id: workId,
    revision,
    value,
    reason_codes: [...new Set(reasonCodes)].sort(),
    authority_effect: "none",
  });
  return freeze({...material, result_digest: digestModuleValue(material)});
}

function invalid(operation, request, reasonCode = "define.client-request-invalid") {
  return result(operation, {
    ok: false,
    disposition: request?.schema_version === REQUEST_SCHEMAS[operation] ? "invalid" : "incompatible-schema",
    workId: text(request?.work_id) || null,
    reasonCodes: [reasonCode],
  });
}

function runtimeCommand(request, commandType, payload) {
  return {
    schema_version: "cav2.define-session-command/v1",
    command_id: request.command_id,
    command_type: commandType,
    session_id: request.work_id,
    expected_revision: request.expected_revision,
    actor_access_context: clone(request.actor_access_context),
    payload_schema_version: "v1",
    payload: clone(payload),
  };
}

function runtimeResult(operation, request, write, snapshot) {
  const ok = write.outcome === "confirmed";
  return result(operation, {
    ok,
    disposition: ok ? "confirmed" : write.outcome,
    workId: request.work_id,
    revision: write.resulting_revision,
    value: ok ? {snapshot, event_id: write.event_id, state_digest: write.state_digest} : null,
    reasonCodes: ok ? [] : [write.failure_class ?? `define.client-${write.outcome}`],
  });
}

function exactBytesDigest(value) {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

function stageResponses(snapshot) {
  const answers = snapshot.answers.map((answer) => ({
    question_id: answer.question_id,
    response_kind: answer.response_kind ?? "answer",
    response: answer.answer,
    evidence: clone(answer.evidence ?? {}),
    authority_effect: "none",
  }));
  const answered = new Set(answers.map((item) => item.question_id));
  const unresolved = snapshot.dispositions
    .filter((item) => ["defer", "deferred", "refusal", "refused"].includes(item.response_kind ?? item.disposition) && !answered.has(item.question_id))
    .map((item) => ({
      question_id: item.question_id,
      response_kind: (item.response_kind ?? item.disposition) === "refusal" || item.disposition === "refused" ? "refusal" : "defer",
      response: item.reason,
      evidence: {},
      authority_effect: "none",
    }));
  return [...answers, ...unresolved];
}

function stageInput(snapshot) {
  return {
    stage_id: snapshot.entry_stage_id,
    responses: stageResponses(snapshot),
    prerequisite_receipts: clone(snapshot.prerequisite_receipts ?? []),
  };
}

function latestConfirmation(snapshot) {
  return snapshot.artifact_confirmations.findLast((item) => item.stage_id === snapshot.entry_stage_id) ?? null;
}

export function createDefineClient({runtime, stage_port: stagePort, interface_id: interfaceId}) {
  if (!runtime || typeof runtime.execute !== "function" || typeof runtime.inspect !== "function") {
    throw new TypeError("Define Client requires a durable runtime.");
  }
  if (!stagePort || typeof stagePort.inspect !== "function" || typeof stagePort.invoke !== "function") {
    throw new TypeError("Define Client requires an ontology stage port.");
  }
  if (!text(interfaceId)) throw new TypeError("Define Client requires an interface ID.");
  const session = createDefineSessionClient(runtime, interfaceId);

  function readWork(operation, request) {
    const snapshot = session.resume(request.work_id);
    if (!snapshot) return {failure: result(operation, {ok: false, disposition: "unavailable", workId: request.work_id, reasonCodes: ["define.client-work-unavailable"]})};
    if (snapshot.stage_graph_digest !== stagePort.stage_graph_digest || snapshot.module_set_digest !== stagePort.module_set_digest) {
      return {failure: result(operation, {ok: false, disposition: "blocked", workId: request.work_id, revision: snapshot.revision, reasonCodes: ["define.client-stage-binding-drift"]})};
    }
    return {snapshot};
  }

  function stageRun(snapshot, confirmationCandidateDigest = null) {
    return runOntologyStage({...stageInput(snapshot), stage_port: stagePort, confirmation_candidate_digest: confirmationCandidateDigest});
  }

  function revisionConflict(operation, request, snapshot) {
    if (request.expected_revision === snapshot.revision) return null;
    return result(operation, {ok: false, disposition: "conflict", workId: request.work_id, revision: snapshot.revision, reasonCodes: ["revision-conflict"]});
  }

  return Object.freeze({
    schema_version: "cav2.define-client/v1",
    interface_id: interfaceId,
    authority_effect: "none",

    startWork(request) {
      const operation = "startWork";
      if (!exactRequest(operation, request) || request.expected_revision !== 0 || !text(request.stage_id)) return invalid(operation, request);
      if (!stagePort.descriptor(request.stage_id)) return result(operation, {ok: false, disposition: "unavailable", workId: request.work_id, reasonCodes: ["define.stage-unavailable"]});
      const write = session.execute(runtimeCommand(request, "create-session", {
        goal: request.goal,
        intent: request.intent,
        context: request.context,
        consumer: request.consumer,
        entry_stage_id: request.stage_id,
        stage_graph_digest: stagePort.stage_graph_digest,
        module_set_digest: stagePort.module_set_digest,
        prerequisite_receipts: request.prerequisite_receipts ?? [],
        context_sufficiency_evaluation: request.context_sufficiency_evaluation ?? null,
        context_candidates: request.context_candidates ?? [],
        sources: request.sources ?? [],
        evidence: request.evidence ?? [],
        owners: request.owners ?? [],
        authority_envelope: request.authority_envelope ?? {},
      }));
      return runtimeResult(operation, request, write, write.outcome === "confirmed" ? session.resume(request.work_id) : null);
    },

    resumeWork(request) {
      const operation = "resumeWork";
      if (!exactRequest(operation, request)) return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      return result(operation, {ok: true, disposition: "available", workId: request.work_id, revision: read.snapshot.revision, value: {snapshot: read.snapshot}});
    },

    listStages(request) {
      const operation = "listStages";
      if (!exactRequest(operation, request)) return invalid(operation, request);
      const inspection = stagePort.inspect();
      const stages = inspection.stages.map((descriptor) => {
        const described = stagePort.invoke(descriptor.stage_id, "describe", {stage_id: descriptor.stage_id}, `define-client:list:${descriptor.stage_id}`);
        return {
          stage_id: descriptor.stage_id,
          ontology_type: descriptor.ontology_type,
          prerequisite_stage_ids: descriptor.prerequisite_stage_ids,
          availability: described.ok ? "available" : described.disposition,
          description: described.ok ? described.value : null,
          reason_codes: described.reason_codes,
          authority_effect: "none",
        };
      });
      return result(operation, {ok: true, disposition: "available", value: {stages, stage_graph_digest: inspection.stage_graph_digest, module_set_digest: inspection.module_set_digest}});
    },

    nextQuestion(request) {
      const operation = "nextQuestion";
      if (!exactRequest(operation, request)) return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      const snapshot = read.snapshot;
      const conflict = revisionConflict(operation, request, snapshot);
      if (conflict) return conflict;
      if (snapshot.current_question_id) return result(operation, {ok: false, disposition: "blocked", workId: request.work_id, revision: snapshot.revision, reasonCodes: ["define.client-question-already-open"]});
      const queried = stagePort.invoke(snapshot.entry_stage_id, "next_question", stageInput(snapshot), `define-client:question:${request.work_id}:${snapshot.revision}`);
      if (!queried.ok) return result(operation, {ok: false, disposition: queried.disposition, workId: request.work_id, revision: snapshot.revision, reasonCodes: queried.reason_codes});
      if (queried.value.complete) return result(operation, {ok: true, disposition: "complete", workId: request.work_id, revision: snapshot.revision, value: {question: null}});
      const question = queried.value.question;
      const write = session.execute(runtimeCommand(request, "open-question", {
        question_id: question.question_id,
        term: question.answer_kind,
        question: question.prompt,
        owner_route: question.owner_ref,
      }));
      return runtimeResult(operation, request, write, write.outcome === "confirmed" ? session.resume(request.work_id) : null);
    },

    submitResponse(request) {
      const operation = "submitResponse";
      if (!exactRequest(operation, request) || !["answer", "correction", "refusal", "defer"].includes(request.response_kind)) return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      const conflict = revisionConflict(operation, request, read.snapshot);
      if (conflict) return conflict;
      const questionId = read.snapshot.current_question_id;
      if (!questionId) return result(operation, {ok: false, disposition: "blocked", workId: request.work_id, revision: read.snapshot.revision, reasonCodes: ["define.client-current-question-required"]});
      const isAnswer = ["answer", "correction"].includes(request.response_kind);
      if (isAnswer && !text(request.response)) return invalid(operation, request, "define.client-response-required");
      const write = session.execute(runtimeCommand(request, isAnswer ? "record-answer" : "defer-question", isAnswer ? {
        question_id: questionId,
        answer: request.response,
        response_kind: request.response_kind,
        evidence: request.evidence ?? {},
      } : {
        question_id: questionId,
        response_kind: request.response_kind,
        reason: request.reason ?? request.response,
      }));
      return runtimeResult(operation, request, write, write.outcome === "confirmed" ? session.resume(request.work_id) : null);
    },

    inspectReadiness(request) {
      const operation = "inspectReadiness";
      if (!exactRequest(operation, request)) return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      const run = stageRun(read.snapshot);
      const readyForConfirmation = run.phase === "handoff" && run.candidate !== null;
      const candidateBytes = readyForConfirmation ? canonicalModuleJson(run.candidate) : null;
      return result(operation, {
        ok: true,
        disposition: readyForConfirmation ? "confirmation-required" : run.disposition,
        workId: request.work_id,
        revision: read.snapshot.revision,
        value: {phase: run.phase, candidate: run.candidate, candidate_digest: run.candidate_digest, candidate_bytes: candidateBytes, evidence: run.evidence},
        reasonCodes: run.reason_codes,
      });
    },

    confirmArtifact(request) {
      const operation = "confirmArtifact";
      if (!exactRequest(operation, request) || typeof request.candidate_bytes !== "string") return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      const conflict = revisionConflict(operation, request, read.snapshot);
      if (conflict) return conflict;
      const run = stageRun(read.snapshot);
      if (run.phase !== "handoff" || run.candidate === null) return result(operation, {ok: false, disposition: "blocked", workId: request.work_id, revision: read.snapshot.revision, reasonCodes: run.reason_codes});
      const expectedBytes = canonicalModuleJson(run.candidate);
      if (request.candidate_bytes !== expectedBytes) return result(operation, {ok: false, disposition: "conflict", workId: request.work_id, revision: read.snapshot.revision, reasonCodes: ["define.client-confirmation-candidate-drift"]});
      const write = session.execute(runtimeCommand(request, "confirm-artifact", {
        stage_id: read.snapshot.entry_stage_id,
        artifact_kind: run.candidate.schema_version,
        candidate_digest: run.candidate_digest,
        candidate_bytes_digest: exactBytesDigest(request.candidate_bytes),
      }));
      return runtimeResult(operation, request, write, write.outcome === "confirmed" ? session.resume(request.work_id) : null);
    },

    exportArtifact(request) {
      const operation = "exportArtifact";
      if (!exactRequest(operation, request) || typeof request.candidate_bytes !== "string") return invalid(operation, request);
      const read = readWork(operation, request);
      if (read.failure) return read.failure;
      const confirmation = latestConfirmation(read.snapshot);
      if (!confirmation) return result(operation, {ok: false, disposition: "blocked", workId: request.work_id, revision: read.snapshot.revision, reasonCodes: ["define.client-confirmation-required"]});
      if (confirmation.candidate_bytes_digest !== exactBytesDigest(request.candidate_bytes)) return result(operation, {ok: false, disposition: "conflict", workId: request.work_id, revision: read.snapshot.revision, reasonCodes: ["define.client-confirmation-candidate-drift"]});
      const run = stageRun(read.snapshot, confirmation.candidate_digest);
      if (!run.ok || canonicalModuleJson(run.candidate) !== request.candidate_bytes) return result(operation, {ok: false, disposition: run.disposition === "handoff-ready" ? "conflict" : run.disposition, workId: request.work_id, revision: read.snapshot.revision, reasonCodes: run.reason_codes.length ? run.reason_codes : ["define.client-confirmation-candidate-drift"]});
      return result(operation, {ok: true, disposition: "handoff-ready", workId: request.work_id, revision: read.snapshot.revision, value: {candidate: run.candidate, candidate_bytes: request.candidate_bytes, candidate_digest: run.candidate_digest, confirmation, handoff_receipt: run.handoff_receipt}});
    },
  });
}

export function createDefineCliClient(options) {
  return createDefineClient({...options, interface_id: "cli"});
}

export function createDefineChatClient(options) {
  return createDefineClient({...options, interface_id: "chat"});
}
