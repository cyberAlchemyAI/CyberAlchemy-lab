import { OUTCOMES } from "./outcomes.mjs";
import { verifyRecordDigest } from "./canonical-json.mjs";

export const EVALUATOR_ID = "semantic-judgment-evaluator@1";
export const SCHEMA_VERSION = "1.0.0";

function terminal(
  outcome,
  {
    applicabilityStatus,
    applicableRuleIds = [],
    defeatedRuleIds = [],
    conflictRuleIds = [],
    precedenceEdgesUsed = [],
    derivation = [],
    residue = [],
  } = {},
) {
  return {
    outcome,
    applicability_decision: {
      status: applicabilityStatus ?? outcome,
      applicable_rule_ids: [...applicableRuleIds].sort(),
      defeated_rule_ids: [...defeatedRuleIds].sort(),
      conflict_rule_ids: [...conflictRuleIds].sort(),
      precedence_edges_used: [...precedenceEdgesUsed].sort((left, right) =>
        `${left.from}:${left.to}`.localeCompare(`${right.from}:${right.to}`),
      ),
      residue: [...residue],
    },
    derivation: [...derivation],
    residue: [...residue],
  };
}

function invalid(reason, derivation = []) {
  return terminal(OUTCOMES.INVALID_INPUT, {
    applicabilityStatus: "invalid-input",
    derivation: [...derivation, `invalid:${reason}`],
    residue: [reason],
  });
}

function isValidTimestamp(value) {
  return (
    typeof value === "string" &&
    value.length > 0 &&
    Number.isFinite(Date.parse(value))
  );
}

function recordCheck(record, name) {
  if (!record || typeof record !== "object") {
    return `${name}:missing`;
  }
  if (record.schema_version !== SCHEMA_VERSION) {
    return `${name}:unknown-schema-version`;
  }
  if (!verifyRecordDigest(record)) {
    return `${name}:digest-mismatch`;
  }
  return null;
}

function contextEnvelopeBindingCheck(request) {
  const binding = request.context_envelope_binding;
  if (binding === undefined) return null;
  const recordFailure = recordCheck(binding, "context-envelope-binding");
  if (recordFailure) return recordFailure;
  const frame = request.frame;
  const entryGate = request.entry_gate;
  const itemDigestsEqual = Array.isArray(binding.context_item_digests)
    && Array.isArray(frame.context_item_digests)
    && JSON.stringify(binding.context_item_digests) === JSON.stringify(frame.context_item_digests);
  if (
    binding.record_type !== "ContextEnvelopeBinding" ||
    binding.authority_effect !== "none" ||
    binding.bound_frame_digest !== frame.digest ||
    binding.context_epoch_id !== frame.context_epoch_id ||
    binding.context_envelope_digest !== frame.context_envelope_digest ||
    binding.freshness_state !== frame.context_freshness_state ||
    binding.claim_ceiling !== frame.context_claim_ceiling ||
    !itemDigestsEqual ||
    entryGate.subject_digest !== frame.digest ||
    entryGate.context_envelope_binding_digest !== binding.digest ||
    entryGate.authority_snapshot_digest !== request.authority_snapshot.digest
  ) {
    return "context-envelope-binding:mismatch";
  }
  return null;
}

function hasCycle(edges) {
  const graph = new Map();
  for (const edge of edges ?? []) {
    if (
      typeof edge?.from !== "string" ||
      typeof edge?.to !== "string" ||
      !edge.from ||
      !edge.to
    ) {
      return true;
    }
    if (!graph.has(edge.from)) graph.set(edge.from, []);
    graph.get(edge.from).push(edge.to);
  }
  const visiting = new Set();
  const visited = new Set();
  const visit = (node) => {
    if (visiting.has(node)) return true;
    if (visited.has(node)) return false;
    visiting.add(node);
    for (const next of graph.get(node) ?? []) {
      if (visit(next)) return true;
    }
    visiting.delete(node);
    visited.add(node);
    return false;
  };
  return [...graph.keys()].some(visit);
}

function transitivePrecedence(edges, from, to) {
  const graph = new Map();
  for (const edge of edges ?? []) {
    if (!graph.has(edge.from)) graph.set(edge.from, []);
    graph.get(edge.from).push(edge.to);
  }
  const seen = new Set();
  const pending = [from];
  while (pending.length) {
    const current = pending.pop();
    if (current === to) return true;
    if (seen.has(current)) continue;
    seen.add(current);
    pending.push(...(graph.get(current) ?? []));
  }
  return false;
}

function compare(actual, condition) {
  switch (condition.op) {
    case "equals":
      return actual === condition.value;
    case "not_equals":
      return actual !== condition.value;
    case "less_than":
      return typeof actual === "number" && actual < condition.value;
    case "less_than_or_equal":
      return typeof actual === "number" && actual <= condition.value;
    case "greater_than":
      return typeof actual === "number" && actual > condition.value;
    case "greater_than_or_equal":
      return typeof actual === "number" && actual >= condition.value;
    case "in":
      return Array.isArray(condition.value) && condition.value.includes(actual);
    default:
      return false;
  }
}

function observationMap(observations) {
  const map = new Map();
  for (const observation of observations) {
    if (observation.posture === "admitted") {
      map.set(observation.field, observation.value);
    }
  }
  return map;
}

function matchingConditions(conditions, facts) {
  return (conditions ?? []).every(
    (condition) =>
      facts.has(condition.field) &&
      compare(facts.get(condition.field), condition),
  );
}

function missingConditions(conditions, facts) {
  return (conditions ?? [])
    .filter((condition) => !facts.has(condition.field))
    .map((condition) => condition.field)
    .sort();
}

function validateChallenge(challengeClosure, asOf) {
  for (const lane of challengeClosure.required_lanes ?? []) {
    if (
      !isValidTimestamp(lane.deadline_at) ||
      !Number.isInteger(lane.attempt_limit) ||
      lane.attempt_limit <= 0 ||
      !Number.isInteger(lane.attempt_count) ||
      lane.attempt_count < 0
    ) {
      return { outcome: OUTCOMES.INVALID_INPUT, reason: `invalid-lane:${lane.lane_id}` };
    }
    if (lane.status === "failed") {
      return { outcome: OUTCOMES.INSUFFICIENT, reason: `required-lane-failed:${lane.lane_id}` };
    }
    if (lane.status !== "closed") {
      if (
        Date.parse(asOf) >= Date.parse(lane.deadline_at) ||
        lane.attempt_count >= lane.attempt_limit
      ) {
        return { outcome: OUTCOMES.INSUFFICIENT, reason: `required-lane-timeout:${lane.lane_id}` };
      }
      return { outcome: OUTCOMES.INSUFFICIENT, reason: `required-lane-open:${lane.lane_id}` };
    }
  }
  if (
    (challengeClosure.material_disputes ?? []).some(
      (dispute) => dispute.status !== "resolved",
    )
  ) {
    return { outcome: OUTCOMES.ESCALATE_OWNER, reason: "material-dispute-unresolved" };
  }
  if ((challengeClosure.admitted_defeaters ?? []).length > 0) {
    return { outcome: OUTCOMES.DEFEATED, reason: "admitted-material-defeater" };
  }
  return null;
}

function temporalOutcome(mode) {
  return mode === "current-revalidation"
    ? OUTCOMES.INVALIDATED
    : OUTCOMES.UNAUTHORIZED_CATALOG;
}

export function evaluateSemanticJudgment(request, telemetry = {}) {
  telemetry.evaluator_calls = (telemetry.evaluator_calls ?? 0) + 1;
  const derivation = ["input-validation:start"];
  if (request?.schema_version !== SCHEMA_VERSION) {
    return invalid("request:unknown-schema-version", derivation);
  }
  if (!isValidTimestamp(request.as_of)) {
    return invalid("request:invalid-as-of", derivation);
  }
  const namedRecords = [
    ["frame", request.frame],
    ["authority-snapshot", request.authority_snapshot],
    ["catalog", request.catalog],
    ["challenge-closure", request.challenge_closure],
    ["technique-plan", request.technique_plan],
    ["effort-profile", request.effort_profile],
    ["entry-gate", request.entry_gate],
    ["runtime-journal-cut", request.runtime_journal_cut],
  ];
  for (const [name, record] of namedRecords) {
    const failure = recordCheck(record, name);
    if (failure) return invalid(failure, derivation);
  }
  const contextBindingFailure = contextEnvelopeBindingCheck(request);
  if (contextBindingFailure) return invalid(contextBindingFailure, derivation);
  const observationIds = new Set();
  const admittedFields = new Set();
  for (const observation of request.observations ?? []) {
    const failure = recordCheck(observation, "observation");
    if (failure) return invalid(failure, derivation);
    if (observationIds.has(observation.observation_id)) {
      return invalid(`duplicate-observation:${observation.observation_id}`, derivation);
    }
    observationIds.add(observation.observation_id);
    if (!["admitted", "rejected", "unresolved"].includes(observation.posture)) {
      return invalid(`observation-posture:${observation.observation_id}`, derivation);
    }
    if (
      observation.posture === "admitted" &&
      admittedFields.has(observation.field)
    ) {
      return invalid(`duplicate-admitted-fact:${observation.field}`, derivation);
    }
    if (observation.posture === "admitted") {
      admittedFields.add(observation.field);
    }
  }
  derivation.push("input-validation:pass");

  const snapshot = request.authority_snapshot;
  const catalog = request.catalog;
  if (
    catalog.evaluator_id !== EVALUATOR_ID ||
    catalog.status !== "active"
  ) {
    return terminal(temporalOutcome(request.mode), {
      applicabilityStatus: "unauthorized-catalog",
      derivation: [...derivation, "catalog-binding-or-status:reject"],
      residue: ["catalog binding or status is not active"],
    });
  }
  if (
    catalog.revoked_at !== null ||
    (catalog.expires_at !== null &&
      (!isValidTimestamp(catalog.expires_at) ||
        Date.parse(request.as_of) >= Date.parse(catalog.expires_at)))
  ) {
    return terminal(temporalOutcome(request.mode), {
      applicabilityStatus: "unauthorized-catalog",
      derivation: [...derivation, "catalog-temporal-state:reject"],
      residue: ["catalog expired or revoked"],
    });
  }
  if (
    snapshot.status !== "active" ||
    !Array.isArray(snapshot.owners) ||
    !snapshot.owners.includes(catalog.issuer_ref) ||
    catalog.issuer_ref === EVALUATOR_ID ||
    snapshot.owners.includes(EVALUATOR_ID)
  ) {
    return terminal(OUTCOMES.ESCALATE_OWNER, {
      applicabilityStatus: "owner-escalation",
      derivation: [...derivation, "catalog-owner:unresolved-or-self-appointed"],
      residue: ["missing, unresolved, or self-appointed catalog authority"],
    });
  }
  if (
    hasCycle(snapshot.authority_edges ?? []) ||
    hasCycle(catalog.precedence_edges ?? [])
  ) {
    return terminal(OUTCOMES.ESCALATE_OWNER, {
      applicabilityStatus: "owner-escalation",
      derivation: [...derivation, "authority-or-precedence-cycle"],
      residue: ["authority or precedence cycle"],
    });
  }
  derivation.push("catalog-authority-time:pass");

  const rules = (catalog.rules ?? []).filter(
    (rule) => rule.domain === request.frame.conclusion_domain,
  );
  if (
    !(catalog.conclusion_domain ?? []).includes(
      request.frame.conclusion_domain,
    ) ||
    rules.length === 0
  ) {
    return terminal(OUTCOMES.OUT_OF_DOMAIN, {
      applicabilityStatus: "out-of-domain",
      derivation: [...derivation, "domain-match:none"],
      residue: ["no registered conclusion-domain rule"],
    });
  }
  derivation.push("domain-match:pass");

  const challenge = validateChallenge(request.challenge_closure, request.as_of);
  if (challenge) {
    if (challenge.outcome === OUTCOMES.INVALID_INPUT) {
      return invalid(challenge.reason, derivation);
    }
    return terminal(challenge.outcome, {
      applicabilityStatus:
        challenge.outcome === OUTCOMES.DEFEATED
          ? "defeated"
          : challenge.outcome === OUTCOMES.ESCALATE_OWNER
            ? "owner-escalation"
            : "insufficient",
      derivation: [...derivation, `challenge:${challenge.reason}`],
      residue: [challenge.reason],
    });
  }
  derivation.push("challenge-closure:pass");

  const facts = observationMap(request.observations ?? []);
  const candidateRules = [];
  const missing = new Set();
  const excepted = [];
  const defeated = [];
  for (const rule of rules) {
    for (const field of missingConditions(rule.required_facts, facts)) {
      missing.add(field);
    }
    if (
      (rule.selectors ?? []).length > 0 &&
      !matchingConditions(rule.selectors, facts)
    ) {
      continue;
    }
    if (
      (rule.exceptions ?? []).some((condition) =>
        matchingConditions([condition], facts),
      )
    ) {
      excepted.push(rule.rule_id);
      continue;
    }
    if (
      (rule.defeaters ?? []).some((condition) =>
        matchingConditions([condition], facts),
      )
    ) {
      defeated.push(rule.rule_id);
      continue;
    }
    if (missingConditions(rule.required_facts, facts).length === 0) {
      if (matchingConditions(rule.required_facts, facts)) {
        candidateRules.push(rule);
      }
    }
  }
  if (missing.size > 0) {
    return terminal(OUTCOMES.INSUFFICIENT, {
      applicabilityStatus: "insufficient",
      derivation: [...derivation, `required-support:missing:${[...missing].join(",")}`],
      residue: [...missing].map((field) => `missing-required-fact:${field}`),
    });
  }
  if (defeated.length > 0 || excepted.length > 0) {
    return terminal(OUTCOMES.DEFEATED, {
      applicabilityStatus: "defeated",
      defeatedRuleIds: [...defeated, ...excepted],
      derivation: [...derivation, "defeater-or-exception:matched"],
      residue: [
        ...defeated.map((id) => `defeater:${id}`),
        ...excepted.map((id) => `exception:${id}`),
      ],
    });
  }
  if (candidateRules.length === 0) {
    return terminal(OUTCOMES.OUT_OF_DOMAIN, {
      applicabilityStatus: "out-of-domain",
      derivation: [...derivation, "applicability:no-matching-rule"],
      residue: ["no rule selector matched"],
    });
  }

  const conclusions = new Set(candidateRules.map((rule) => rule.conclusion));
  let selectedRules = candidateRules;
  const precedenceEdgesUsed = [];
  if (conclusions.size > 1) {
    const winners = candidateRules.filter((candidate) =>
      candidateRules
        .filter((other) => other.rule_id !== candidate.rule_id)
        .every((other) =>
          transitivePrecedence(
            catalog.precedence_edges ?? [],
            candidate.rule_id,
            other.rule_id,
          ),
        ),
    );
    if (winners.length !== 1) {
      return terminal(OUTCOMES.ESCALATE_OWNER, {
        applicabilityStatus: "owner-escalation",
        conflictRuleIds: candidateRules.map((rule) => rule.rule_id),
        derivation: [...derivation, "applicable-rule-conflict:unresolved"],
        residue: ["unresolved applicable-rule conflict"],
      });
    }
    selectedRules = winners;
    for (const other of candidateRules) {
      if (other.rule_id !== winners[0].rule_id) {
        precedenceEdgesUsed.push({
          from: winners[0].rule_id,
          to: other.rule_id,
        });
      }
    }
  }
  if (selectedRules.some((rule) => rule.conclusion !== "recommend")) {
    return terminal(OUTCOMES.DEFEATED, {
      applicabilityStatus: "defeated",
      defeatedRuleIds: selectedRules.map((rule) => rule.rule_id),
      precedenceEdgesUsed,
      derivation: [...derivation, "selected-rule:deny"],
      residue: ["selected applicable rule denies recommendation"],
    });
  }
  return terminal(OUTCOMES.RECOMMENDED, {
    applicabilityStatus: "applicable",
    applicableRuleIds: selectedRules.map((rule) => rule.rule_id),
    precedenceEdgesUsed,
    derivation: [...derivation, "applicability:pass", "support:complete"],
    residue: [],
  });
}
