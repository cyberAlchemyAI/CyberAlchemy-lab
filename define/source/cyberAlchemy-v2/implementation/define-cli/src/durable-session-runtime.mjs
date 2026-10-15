import {mkdirSync, openSync, closeSync, readFileSync, renameSync, rmSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";

import {canonicalJson, canonicalize, digest, stableUniqueStrings} from "./canonical.mjs";

const SESSION_SCHEMA_VERSION = "cav2.define-session/v1";
const COMMAND_SCHEMA_VERSION = "cav2.define-session-command/v1";
const STORE_SCHEMA_VERSION = "cav2.define-session-store/v1";
const OUTCOMES = new Set(["confirmed", "conflict", "denied", "invalid", "incompatible-schema", "storage-failure"]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function text(value) {
  return String(value ?? "").trim();
}

function withoutDigest(snapshot) {
  const copy = clone(snapshot);
  delete copy.state_digest;
  return canonicalize(copy);
}

export function sessionStateDigest(snapshot) {
  return digest(withoutDigest(snapshot));
}

function sealSnapshot(snapshot) {
  const sealed = canonicalize({...withoutDigest(snapshot), state_digest: sessionStateDigest(snapshot)});
  return sealed;
}

function emptyResult(command, outcome, failureClass, observedRevision, extras = {}) {
  const result = {
    schema_version: "cav2.define-session-write-result/v1",
    command_id: text(command?.command_id),
    session_id: text(command?.session_id),
    expected_revision: Number.isInteger(command?.expected_revision) ? command.expected_revision : null,
    observed_revision: observedRevision,
    resulting_revision: observedRevision,
    outcome,
    failure_class: failureClass,
    state_digest: extras.state_digest ?? null,
    event_id: extras.event_id ?? null,
    authority_effect: "none",
  };
  if (!OUTCOMES.has(outcome)) throw new Error(`define-runtime.outcome-invalid:${outcome}`);
  return canonicalize(result);
}

function validateCommand(command) {
  const reasons = [];
  if (command?.schema_version !== COMMAND_SCHEMA_VERSION) reasons.push("command.incompatible-schema");
  for (const key of ["command_id", "command_type", "session_id", "payload_schema_version"] ) {
    if (!text(command?.[key])) reasons.push(`command.${key}-required`);
  }
  if (!Number.isInteger(command?.expected_revision) || command.expected_revision < 0) reasons.push("command.expected_revision-invalid");
  if (!command?.actor_access_context || !text(command.actor_access_context.actor_ref)) reasons.push("command.actor-required");
  if (!command?.payload || typeof command.payload !== "object" || Array.isArray(command.payload)) reasons.push("command.payload-invalid");
  return stableUniqueStrings(reasons);
}

function requiredEffect(commandType) {
  return {
    "create-session": "create-session",
    "open-question": "open-question",
    "record-answer": "record-answer",
    "defer-question": "defer-question",
    "confirm-artifact": "confirm-artifact",
    "set-context-evaluation": "set-context-evaluation",
  }[commandType] ?? null;
}

function authorize(command) {
  const requested = requiredEffect(command.command_type);
  if (!requested) return {decision: "invalid", reason: "command.unsupported-type"};
  const allowed = new Set(command.actor_access_context.allowed_effects ?? []);
  if (!allowed.has(requested)) return {decision: "deny", reason: "authority.effect-not-allowed"};
  return {decision: "allow-routine-record", reason: null};
}

function contextEvaluation(value, {allowDefault = false} = {}) {
  if (value == null && allowDefault) {
    return canonicalize({
      evaluation_id: null,
      status: "indeterminate",
      derivation: "No frozen requirement evaluation was supplied.",
      residue: ["context-sufficiency-evaluation-required"],
      evaluator_receipt_ref: null,
      authority_effect: "none",
    });
  }
  if (!value || !text(value.evaluation_id) || !["sufficient", "insufficient", "indeterminate"].includes(value.status)) {
    throw new Error("domain.context-evaluation-incomplete");
  }
  if (!text(value.derivation) || !Array.isArray(value.residue) || !text(value.evaluator_receipt_ref) || (value.authority_effect ?? "none") !== "none") {
    throw new Error("domain.context-evaluation-incomplete");
  }
  return canonicalize({
    evaluation_id: text(value.evaluation_id),
    status: value.status,
    derivation: text(value.derivation),
    residue: stableUniqueStrings(value.residue),
    evaluator_receipt_ref: text(value.evaluator_receipt_ref),
    authority_effect: "none",
  });
}

function initialSnapshot(command) {
  const payload = command.payload;
  const missing = ["goal", "intent", "context", "consumer"].filter((key) => !text(payload[key]));
  if (missing.length) throw new Error(`domain.scope-incomplete:${missing.join(",")}`);
  const evaluation = contextEvaluation(payload.context_sufficiency_evaluation, {allowDefault: true});
  return sealSnapshot({
    session_id: command.session_id,
    session_schema_version: SESSION_SCHEMA_VERSION,
    revision: 1,
    goal: text(payload.goal),
    intent: text(payload.intent),
    context: text(payload.context),
    consumer: text(payload.consumer),
    entry_stage_id: text(payload.entry_stage_id) || "definition-pack",
    stage_graph_digest: text(payload.stage_graph_digest) || null,
    module_set_digest: text(payload.module_set_digest) || null,
    prerequisite_receipts: clone(payload.prerequisite_receipts ?? []),
    context_candidates: clone(payload.context_candidates ?? []),
    context_sufficiency_evaluation: clone(evaluation),
    current_question_id: null,
    questions: [],
    answers: [],
    artifact_confirmations: [],
    sources: clone(payload.sources ?? []),
    evidence: clone(payload.evidence ?? []),
    dispositions: [],
    owners: clone(payload.owners ?? []),
    gaps: clone(payload.gaps ?? []),
    check_results: [],
    authority_envelope: canonicalize({
      status: "candidate",
      authority_effect: "none",
      allowed_uses: stableUniqueStrings(payload.authority_envelope?.allowed_uses ?? ["review", "meaning-refinement"]),
      blocked_actions: stableUniqueStrings(payload.authority_envelope?.blocked_actions ?? ["canonical-promotion", "external-effect"]),
    }),
    lifecycle_state: evaluation.status === "sufficient" ? "ready" : "awaiting-context",
  });
}

function applyCommand(snapshot, command) {
  const next = clone(snapshot);
  next.revision = snapshot.revision + 1;
  const payload = command.payload;
  if (command.command_type === "set-context-evaluation") {
    next.context_sufficiency_evaluation = contextEvaluation(payload);
    next.lifecycle_state = next.context_sufficiency_evaluation.status === "sufficient" ? "ready" : "awaiting-context";
  } else {
    if (snapshot.context_sufficiency_evaluation?.status !== "sufficient") throw new Error("domain.context-not-sufficient");
    if (command.command_type === "open-question") {
      const questionId = text(payload.question_id);
      if (!questionId || !text(payload.question) || !text(payload.owner_route)) throw new Error("domain.question-incomplete");
      if (snapshot.current_question_id) throw new Error("domain.current-question-already-open");
      if (snapshot.questions.some((item) => item.question_id === questionId)) throw new Error("domain.question-id-duplicate");
      next.questions.push(canonicalize({question_id: questionId, term: text(payload.term), question: text(payload.question), owner_route: text(payload.owner_route), state: "open"}));
      next.current_question_id = questionId;
      next.lifecycle_state = "question-open";
    } else if (command.command_type === "record-answer") {
      const questionId = text(payload.question_id);
      const answer = text(payload.answer);
      const responseKind = text(payload.response_kind) || "answer";
      if (!questionId || !answer || questionId !== snapshot.current_question_id) throw new Error("domain.answer-current-question-required");
      if (!["answer", "correction"].includes(responseKind)) throw new Error("domain.answer-response-kind-invalid");
      const question = next.questions.find((item) => item.question_id === questionId);
      question.state = "answered";
      next.answers.push(canonicalize({
        answer_id: text(payload.answer_id) || `answer:${digest({questionId, answer, responseKind}).slice(0, 20)}`,
        question_id: questionId,
        answer,
        response_kind: responseKind,
        evidence: clone(payload.evidence ?? {}),
        actor_ref: command.actor_access_context.actor_ref,
        authority_effect: "none",
      }));
      next.dispositions.push(canonicalize({question_id: questionId, disposition: responseKind === "correction" ? "corrected" : "answered", response_kind: responseKind, owner_route: question.owner_route}));
      next.current_question_id = null;
      next.lifecycle_state = "ready";
    } else if (command.command_type === "defer-question") {
      const questionId = text(payload.question_id);
      const responseKind = text(payload.response_kind) || "defer";
      if (!questionId || questionId !== snapshot.current_question_id) throw new Error("domain.defer-current-question-required");
      if (!["defer", "refusal"].includes(responseKind)) throw new Error("domain.defer-response-kind-invalid");
      const question = next.questions.find((item) => item.question_id === questionId);
      question.state = responseKind === "refusal" ? "refused" : "deferred";
      next.dispositions.push(canonicalize({question_id: questionId, disposition: responseKind === "refusal" ? "refused" : "deferred", response_kind: responseKind, reason: text(payload.reason) || "Deferred without inferred answer", owner_route: question.owner_route}));
      next.gaps.push(canonicalize({gap_id: `gap:${digest({questionId, revision: next.revision}).slice(0, 20)}`, question_id: questionId, statement: text(payload.reason) || question.question, owner_route: question.owner_route, status: "open"}));
      next.current_question_id = null;
      next.lifecycle_state = "ready-with-open-gaps";
    } else if (command.command_type === "confirm-artifact") {
      const stageId = text(payload.stage_id);
      const candidateDigest = text(payload.candidate_digest);
      const candidateBytesDigest = text(payload.candidate_bytes_digest);
      if (!stageId || !/^[a-f0-9]{64}$/u.test(candidateDigest) || !/^[a-f0-9]{64}$/u.test(candidateBytesDigest)) {
        throw new Error("domain.artifact-confirmation-incomplete");
      }
      if (snapshot.current_question_id) throw new Error("domain.artifact-confirmation-question-open");
      next.artifact_confirmations.push(canonicalize({
        confirmation_id: text(payload.confirmation_id) || `confirmation:${digest({stageId, candidateDigest, candidateBytesDigest, revision: next.revision}).slice(0, 20)}`,
        stage_id: stageId,
        artifact_kind: text(payload.artifact_kind) || "candidate",
        candidate_digest: candidateDigest,
        candidate_bytes_digest: candidateBytesDigest,
        actor_ref: command.actor_access_context.actor_ref,
        confirmed_at_revision: next.revision,
        authority_effect: "none",
      }));
      next.lifecycle_state = "artifact-confirmed";
    }
  }
  return sealSnapshot(next);
}

function eventFor(command, snapshot) {
  const material = {command_id: command.command_id, command_type: command.command_type, session_id: command.session_id, resulting_revision: snapshot.revision, state_digest: snapshot.state_digest};
  return canonicalize({schema_version: "cav2.define-session-event/v1", event_id: `define-event:${digest(material)}`, ...material, authority_effect: "none"});
}

export class InMemorySessionRepository {
  constructor() {
    this.records = new Map();
    this.failNextCommit = false;
  }

  load(sessionId) {
    return this.records.has(sessionId) ? clone(this.records.get(sessionId)) : null;
  }

  injectStorageFailure() {
    this.failNextCommit = true;
  }

  compareAndCommit({command, command_digest, snapshot, event}) {
    if (this.failNextCommit) {
      this.failNextCommit = false;
      return {status: "storage-failure"};
    }
    const record = this.records.get(command.session_id) ?? {snapshot: null, commands: {}, events: []};
    const prior = record.commands[command.command_id];
    if (prior) return prior.command_digest === command_digest ? {status: "replay", result: clone(prior.result)} : {status: "command-conflict"};
    const observed = record.snapshot?.revision ?? 0;
    if (observed !== command.expected_revision) return {status: "revision-conflict", observed_revision: observed, state_digest: record.snapshot?.state_digest ?? null};
    const result = emptyResult(command, "confirmed", null, observed, {state_digest: snapshot.state_digest, event_id: event.event_id});
    result.resulting_revision = snapshot.revision;
    record.snapshot = clone(snapshot);
    record.commands[command.command_id] = {command_digest, result: clone(result)};
    record.events.push(clone(event));
    this.records.set(command.session_id, record);
    return {status: "confirmed", result};
  }
}

export class JsonFileSessionRepository {
  constructor(root) {
    this.root = resolve(root);
    mkdirSync(this.root, {recursive: true, mode: 0o700});
  }

  pathFor(sessionId) {
    return resolve(this.root, `${digest(sessionId)}.json`);
  }

  load(sessionId) {
    try {
      const value = JSON.parse(readFileSync(this.pathFor(sessionId), "utf8"));
      if (value.schema_version !== STORE_SCHEMA_VERSION || value.session_id !== sessionId) throw new Error("define-runtime.store-invalid");
      if (value.snapshot && sessionStateDigest(value.snapshot) !== value.snapshot.state_digest) throw new Error("define-runtime.snapshot-digest-mismatch");
      return clone(value);
    } catch (error) {
      if (error.code === "ENOENT") return null;
      throw error;
    }
  }

  compareAndCommit(input) {
    const target = this.pathFor(input.command.session_id);
    const lock = `${target}.lock`;
    let handle;
    try {
      handle = openSync(lock, "wx", 0o600);
    } catch (error) {
      if (error.code === "EEXIST") return {status: "storage-busy"};
      return {status: "storage-failure"};
    }
    try {
      const record = this.load(input.command.session_id) ?? {schema_version: STORE_SCHEMA_VERSION, session_id: input.command.session_id, snapshot: null, commands: {}, events: []};
      const memory = new InMemorySessionRepository();
      memory.records.set(input.command.session_id, record);
      const outcome = memory.compareAndCommit(input);
      if (outcome.status !== "confirmed") return outcome;
      const updated = memory.records.get(input.command.session_id);
      const temporary = `${target}.${process.pid}.${digest(input.command.command_id).slice(0, 12)}.tmp`;
      writeFileSync(temporary, `${canonicalJson(updated)}\n`, {encoding: "utf8", mode: 0o600});
      renameSync(temporary, target);
      return outcome;
    } catch {
      return {status: "storage-failure"};
    } finally {
      if (handle !== undefined) closeSync(handle);
      rmSync(lock, {force: true});
    }
  }
}

export function createDurableDefineRuntime({repository = new InMemorySessionRepository(), audit = () => {}, clock = () => new Date().toISOString()} = {}) {
  function recordAudit(command, result, interfaceId, startedAt) {
    audit(canonicalize({
      schema_version: "cav2.define-runtime-audit-record/v1",
      command_id: text(command.command_id),
      session_id_hash: digest(text(command.session_id)),
      revision: result.resulting_revision,
      operation: text(command.command_type),
      interface_id: text(interfaceId) || "unspecified",
      outcome: result.outcome,
      failure_class: result.failure_class,
      latency_ms: Math.max(0, Date.now() - startedAt),
      occurred_at: clock(),
      authority_effect: "none",
    }));
  }

  function execute(command, {interface_id = "unspecified"} = {}) {
    const startedAt = Date.now();
    const reasons = validateCommand(command);
    const observed = repository.load(text(command?.session_id))?.snapshot?.revision ?? 0;
    if (reasons.length) {
      const incompatible = reasons.includes("command.incompatible-schema");
      const result = emptyResult(command, incompatible ? "incompatible-schema" : "invalid", reasons.join(";"), observed);
      recordAudit(command ?? {}, result, interface_id, startedAt);
      return result;
    }
    const authority = authorize(command);
    if (authority.decision !== "allow-routine-record") {
      const result = emptyResult(command, authority.decision === "deny" ? "denied" : "invalid", authority.reason, observed);
      recordAudit(command, result, interface_id, startedAt);
      return result;
    }
    const current = repository.load(command.session_id);
    const prior = current?.commands?.[command.command_id];
    if (prior) {
      const result = prior.command_digest === digest(command)
        ? clone(prior.result)
        : emptyResult(command, "conflict", "command-conflict", current.snapshot?.revision ?? 0, {state_digest: current.snapshot?.state_digest ?? null});
      recordAudit(command, result, interface_id, startedAt);
      return result;
    }
    const confirmedRevision = current?.snapshot?.revision ?? 0;
    if (command.expected_revision !== confirmedRevision) {
      const result = emptyResult(command, "conflict", "revision-conflict", confirmedRevision, {state_digest: current?.snapshot?.state_digest ?? null});
      recordAudit(command, result, interface_id, startedAt);
      return result;
    }
    let snapshot;
    try {
      if (command.command_type === "create-session") {
        if (current?.snapshot) {
          const replay = repository.compareAndCommit({command, command_digest: digest(command), snapshot: current.snapshot, event: {event_id: null}});
          if (replay.status === "replay") return replay.result;
          const result = emptyResult(command, "conflict", replay.status, current.snapshot.revision, {state_digest: current.snapshot.state_digest});
          recordAudit(command, result, interface_id, startedAt);
          return result;
        }
        snapshot = initialSnapshot(command);
      } else {
        if (!current?.snapshot) throw new Error("domain.session-not-found");
        snapshot = applyCommand(current.snapshot, command);
      }
    } catch (error) {
      const result = emptyResult(command, "invalid", error.message, observed, {state_digest: current?.snapshot?.state_digest ?? null});
      recordAudit(command, result, interface_id, startedAt);
      return result;
    }
    const event = eventFor(command, snapshot);
    const commit = repository.compareAndCommit({command, command_digest: digest(command), snapshot, event});
    let result;
    if (commit.status === "confirmed" || commit.status === "replay") result = commit.result;
    else if (commit.status === "revision-conflict" || commit.status === "command-conflict") result = emptyResult(command, "conflict", commit.status, commit.observed_revision ?? observed, {state_digest: commit.state_digest ?? current?.snapshot?.state_digest ?? null});
    else result = emptyResult(command, "storage-failure", commit.status, observed, {state_digest: current?.snapshot?.state_digest ?? null});
    recordAudit(command, result, interface_id, startedAt);
    return result;
  }

  function inspect(sessionId) {
    const record = repository.load(sessionId);
    return record?.snapshot ? clone(record.snapshot) : null;
  }

  return Object.freeze({execute, inspect, repository});
}

export function createDefineSessionClient(runtime, interfaceId) {
  return Object.freeze({
    execute: (command) => runtime.execute(command, {interface_id: interfaceId}),
    resume: (sessionId) => runtime.inspect(sessionId),
  });
}
