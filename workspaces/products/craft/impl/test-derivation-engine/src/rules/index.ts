// Stage C — Deriver: pure total function δ(G, Δ) -> Obligation[].
// SWU-ENG-003. Encodes the rule set Δ as CODE (TEST-PIPELINE.md does not exist as
// a doc; the rule TYPES below are reverse-engineered from the doc structure and the
// categories present in the committed financial-settlement/TEST-SPEC.md).
//
// Rule types encoded (δ = ⋃ δ_i), each a pure G -> Obligation[]:
//
//   δ_validTransition   one obligation per Transition Table row (the happy-path move).
//                       Cardinality = |transitions|.
//   δ_invalidTransition (non-terminal states × events) − valid transitions, in
//                       lexicographic (state, event) order. A state is terminal iff
//                       it never appears as a `from` in any transition (a sink).
//                       Cardinality = Σ |non-terminal states|·|events| − |valid from non-terminal|.
//   δ_invariant         classify the Formal expression and emit EXACT count:
//                         EXISTENCE  exists(...)            -> 2 (present / absent)
//                         PRESENCE   a != null and b ...    -> #conjuncts
//                         RANGE      a <= x <= b            -> 4 (lower, upper, below, above)
//                         COUNT_CAP  count(...) <= k        -> 2 (first ok / duplicate capped)
//                         else (unclassifiable prose)       -> needs_formal (1, surfaced not guessed)
//   δ_ruleValidation    same classifier over operations.md Rules (R1..Rn).
//   δ_calculation       one obligation per Calculation row, UNLESS the formula is
//                       a ternary (RANGE-of-branches) -> 2 (one per branch), or is
//                       prose / a bare function call the sub-grammar cannot evaluate
//                       -> needs_formal (1).
//   δ_postcondition     one obligation per Postcondition row.
//   δ_contract          one obligation per Response row (status × condition).
//   δ_event             one PRODUCER obligation per Event (emitted) PLUS one
//                       CONSUMER obligation per (Event × Consumer) read from the
//                       events.md `### Consumed By` table. Consumer-side obligations
//                       are a distinct class (events CONSUMED, not just produced);
//                       the semantic-id buckets them as `event:<consumer>` so an
//                       oracle's per-consumer rows ("Audit subsystem consumption")
//                       bridge to obligations the engine genuinely emits.
//   δ_errorObligation   one obligation per (Operation × `### Error States` row): the
//                       documented condition->error-code mapping, op-bucketed.
//
// δ is PURE (no I/O, no clock, no Math.random) and TOTAL over any G, and emits in a
// deterministic order. The classifier is best-effort: anything it cannot classify
// becomes a counted, content-addressed needs_formal obligation — never an interpreted guess.

import type {
  ConceptGraph,
  Node,
  Obligation,
  RuleType,
  Value,
} from "../ir/types.js";
import { obligationKey } from "../keys/index.js";
import { parseFormal } from "../formal/ast.js";

/** Δ — the rule set. Versioned identity for the encoded rule functions. */
export interface RuleSet {
  readonly version: string;
}

export const DEFAULT_RULE_SET: RuleSet = { version: "L0-1.0.0" };

// --- Formal-expression classifier ---------------------------------------------

export type FormalClass =
  | "EXISTENCE"
  | "PRESENCE"
  | "RANGE"
  | "COUNT_CAP"
  | "UNCLASSIFIED";

export interface Classification {
  readonly kind: FormalClass;
  /** For PRESENCE: the conjunct count; for others, the canonical case count. */
  readonly count: number;
}

const RANGE_RE = /[<>]=?.*?[<>]=?/; // two comparison operators -> a <= x <= b shape
const COUNT_CAP_RE = /count\s*\(.*\)\s*<=?\s*\d+/i;
const EXISTENCE_RE = /(^|\b)(not\s+)?exists?\s*\(/i;
const PRESENCE_RE = /!=\s*null/i;

/** Classify a Formal/Formula cell into an exact-cardinality class. Pure, deterministic. */
export function classifyFormal(formal: string): Classification {
  const f = formal.trim();
  if (f === "") return { kind: "UNCLASSIFIED", count: 1 };

  // COUNT_CAP must be checked before RANGE (it also contains a `<=`).
  if (COUNT_CAP_RE.test(f)) return { kind: "COUNT_CAP", count: 2 };

  if (PRESENCE_RE.test(f)) {
    // Count `!= null` conjuncts; PRESENCE -> one "missing" obligation per field.
    const conjuncts = (f.match(/!=\s*null/gi) ?? []).length;
    return { kind: "PRESENCE", count: Math.max(conjuncts, 1) };
  }

  if (EXISTENCE_RE.test(f)) return { kind: "EXISTENCE", count: 2 };

  // RANGE: a chained comparison like `a <= x <= b`. Require two comparison ops and
  // no boolean connectors / arrows that would make it an implication or compound rule.
  const cmpCount = (f.match(/[<>]=?/g) ?? []).length;
  const hasConnective = /->|=>|\band\b|\bor\b/i.test(f);
  if (cmpCount >= 2 && !hasConnective && RANGE_RE.test(f)) {
    return { kind: "RANGE", count: 4 };
  }

  return { kind: "UNCLASSIFIED", count: 1 };
}

// --- Obligation construction helper -------------------------------------------

function mk(
  ruleType: RuleType,
  sourceAnchor: string,
  canonicalParams: Record<string, Value>,
  description: string,
): Obligation {
  return {
    obligation_key: obligationKey(sourceAnchor, ruleType, canonicalParams),
    rule_type: ruleType,
    source_anchor: sourceAnchor,
    canonical_params: canonicalParams,
    description,
  };
}

function byType(graph: ConceptGraph, type: Node["type"]): Node[] {
  return graph.nodes.filter((n) => n.type === type);
}

function s(v: Value | undefined): string {
  return v == null ? "" : String(v);
}

// --- δ rule functions ----------------------------------------------------------

/** δ_validTransition: one obligation per transition row. */
function deriveValidTransitions(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const t of byType(graph, "Transition")) {
    const from = s(t.fields.from);
    const event = s(t.fields.event);
    const to = s(t.fields.to);
    out.push(
      mk(
        "valid-transition",
        t.source_anchor,
        { from, event, to },
        `Transition ${from} --${event}--> ${to} succeeds when guarded`,
      ),
    );
  }
  return out;
}

/**
 * δ_invalidTransition: (non-terminal states × events) − valid transitions,
 * lexicographically ordered. EXACT cardinality, no "at least N".
 */
function deriveInvalidTransitions(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  const transitions = byType(graph, "Transition");

  // Group transitions by entity.
  const byEntity = new Map<string, Node[]>();
  for (const t of transitions) {
    const e = s(t.fields.entity);
    (byEntity.get(e) ?? byEntity.set(e, []).get(e)!).push(t);
  }

  for (const [entity, ts] of [...byEntity.entries()].sort((a, b) =>
    a[0] < b[0] ? -1 : 1,
  )) {
    // Sources that appear as `from`; targets that appear as `to`.
    const fromStates = new Set<string>();
    const allStates = new Set<string>();
    const events = new Set<string>();
    const valid = new Set<string>(); // `${from}\u0000${event}`
    for (const t of ts) {
      const from = s(t.fields.from);
      const to = s(t.fields.to);
      const ev = s(t.fields.event);
      fromStates.add(from);
      allStates.add(from);
      allStates.add(to);
      events.add(ev);
      valid.add(`${from}\u0000${ev}`);
    }
    // Every real state (terminal sinks INCLUDED) x every event, minus the valid
    // moves, is an invalid transition. Terminal states reject ALL events — the oracle
    // catalogues "TERMINAL + AnyEvent -> rejected", so excluding terminal sinks would
    // under-cover those documented obligations. The `[new]` pseudo-start is not a real
    // state and is excluded as a `from`. EXACT cardinality, no "at least N".
    const candidateStates = [...allStates]
      .filter((st) => st !== "[new]" && st !== "")
      .sort();
    const sortedEvents = [...events].sort();
    const entityAnchor = `${entity}`;
    for (const state of candidateStates) {
      for (const ev of sortedEvents) {
        if (valid.has(`${state}\u0000${ev}`)) continue;
        out.push(
          mk(
            "invalid-transition",
            `states.md#${entityAnchor}:invalid:${state}:${ev}`,
            { entity, from: state, event: ev },
            `Event ${ev} in state ${state} is rejected (no valid transition)`,
          ),
        );
      }
    }
  }
  return out;
}

/** δ_invariant: classify Formal; exact count by class. */
function deriveInvariants(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const inv of byType(graph, "Invariant")) {
    const id = s(inv.fields.id);
    const formal = s(inv.fields.formal);
    emitClassified(
      out,
      "invariant",
      inv.source_anchor,
      { id, formal },
      formal,
      `Invariant ${id}`,
    );
  }
  return out;
}

/** δ_ruleValidation: classify each operations.md Rule's Formal; exact count by class. */
function deriveRuleValidations(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const r of byType(graph, "Rule")) {
    const id = s(r.fields.id);
    const formal = s(r.fields.formal);
    emitClassified(
      out,
      "rule-validation",
      r.source_anchor,
      { id, formal },
      formal,
      `Rule ${id}`,
    );
  }
  return out;
}

/**
 * Shared classifier-driven emitter. Emits EXACT count obligations by FormalClass,
 * each a distinct case so keys differ; UNCLASSIFIED -> one needs_formal obligation.
 */
function emitClassified(
  out: Obligation[],
  ruleType: RuleType,
  anchor: string,
  baseParams: Record<string, Value>,
  formal: string,
  label: string,
): void {
  const cls = classifyFormal(formal);
  switch (cls.kind) {
    case "EXISTENCE": {
      for (const c of ["present", "absent"]) {
        out.push(
          mk(
            ruleType,
            anchor,
            { ...baseParams, case: c },
            `${label}: ${c} (existence)`,
          ),
        );
      }
      break;
    }
    case "PRESENCE": {
      for (let i = 0; i < cls.count; i += 1) {
        out.push(
          mk(
            ruleType,
            anchor,
            { ...baseParams, case: `missing-${i}` },
            `${label}: conjunct ${i} missing`,
          ),
        );
      }
      break;
    }
    case "RANGE": {
      for (const c of [
        "lower-inclusive",
        "upper-inclusive",
        "below",
        "above",
      ]) {
        out.push(
          mk(
            ruleType,
            anchor,
            { ...baseParams, case: c },
            `${label}: ${c} (range)`,
          ),
        );
      }
      break;
    }
    case "COUNT_CAP": {
      for (const c of ["first-allowed", "duplicate-capped"]) {
        out.push(
          mk(
            ruleType,
            anchor,
            { ...baseParams, case: c },
            `${label}: ${c} (count cap)`,
          ),
        );
      }
      break;
    }
    default: {
      out.push(
        mk(
          "needs-formal",
          anchor,
          { ...baseParams, base_rule_type: ruleType },
          `${label}: needs_formal (prose Formal)`,
        ),
      );
    }
  }
}

/** δ_calculation: 1 per calc; ternary -> 2 branches; prose/call -> needs_formal. */
function deriveCalculations(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const c of byType(graph, "Calculation")) {
    const id = s(c.fields.id);
    const formula = s(c.fields.formula).trim();
    const isTernary = /\?[^?]*:/.test(formula);
    // Provenance guard (SWU-COB-005): a CLOSED-FORM Formal (a recognized fold like
    // `sum(records.profit)` or a piecewise/arith like `max(0, debt - profit ...)`)
    // is derivable -> a `calculation` obligation. An OPAQUE bare call the AST
    // cannot parse (e.g. `applyMakeupPolicy(...)` before a formula is authored)
    // stays `needs_formal` — the parser is the single arbiter of "closed form",
    // so a bare call is never promotable until the author writes the formula.
    const ast = parseFormal(formula);
    const isClosedForm =
      ast.kind === "fold" ||
      ast.kind === "arith" ||
      ast.kind === "num" ||
      ast.kind === "var" ||
      ast.kind === "piecewise";
    const isBareCall = /^[A-Za-z_][\w]*\s*\(.*\)$/.test(formula); // applyMakeupPolicy(...)
    const isSimpleExpr = formula !== "" && (isClosedForm || !isBareCall);
    if (isTernary) {
      for (const branch of ["true-branch", "false-branch"]) {
        out.push(
          mk(
            "calculation",
            c.source_anchor,
            { id, branch },
            `Calculation ${id}: ${branch}`,
          ),
        );
      }
    } else if (isSimpleExpr) {
      out.push(
        mk(
          "calculation",
          c.source_anchor,
          { id },
          `Calculation ${id}: ${formula}`,
        ),
      );
    } else {
      // Bare call or prose formula -> cannot evaluate deterministically.
      out.push(
        mk(
          "needs-formal",
          c.source_anchor,
          { id, base_rule_type: "calculation" },
          `Calculation ${id}: needs_formal`,
        ),
      );
    }
  }
  return out;
}

/** δ_postcondition: one obligation per postcondition row. */
function derivePostconditions(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const p of byType(graph, "Postcondition")) {
    const id = s(p.fields.id);
    out.push(
      mk(
        "postcondition",
        p.source_anchor,
        { id },
        `Postcondition ${id}: ${s(p.fields.guarantee)}`,
      ),
    );
  }
  return out;
}

/**
 * δ_contract: one obligation per (response × status code). A Status cell that
 * enumerates multiple codes (`401/403`) is split into one obligation per code —
 * each code is a distinct documented contract outcome, read verbatim from the cell
 * (not inferred). A cell with no parseable 3-digit code yields one obligation with
 * the raw status.
 */
function deriveContracts(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const r of byType(graph, "Response")) {
    const endpoint = s(r.fields.endpoint);
    const statusRaw = s(r.fields.status);
    const condition = s(r.fields.condition);
    const codes = statusRaw.match(/[1-5]\d{2}/g) ?? [];
    const statuses = codes.length > 0 ? codes : [statusRaw];
    for (const status of statuses) {
      out.push(
        mk(
          "contract",
          r.source_anchor,
          { endpoint, status, condition },
          `${endpoint} -> ${status} (${condition})`,
        ),
      );
    }
  }
  return out;
}

/**
 * δ_event: a PRODUCER obligation per Event (it is emitted with a valid payload) PLUS
 * one CONSUMER obligation per (Event × Consumer) declared in the `### Consumed By`
 * table. Producer and consumer obligations are distinct classes — the consumer side
 * is the "event consumed, not just produced" obligation the oracle catalogues
 * separately. The producer obligation carries `consumer: ""`; consumer obligations
 * carry the consumer name (semantic-id buckets them by consumer downstream).
 */
function deriveEvents(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  const consumersByEvent = new Map<string, Node[]>();
  for (const c of byType(graph, "Consumer")) {
    const ev = s(c.fields.event);
    (consumersByEvent.get(ev) ?? consumersByEvent.set(ev, []).get(ev)!).push(c);
  }
  for (const ev of byType(graph, "Event")) {
    const name = s(ev.fields.name);
    // Producer obligation — the event is emitted with a valid payload.
    out.push(
      mk(
        "event-obligation",
        ev.source_anchor,
        { event: name, consumer: "" },
        `Event ${name} is emitted with valid payload`,
      ),
    );
    // Consumer obligations — one per declared consumer (events consumed).
    for (const c of consumersByEvent.get(name) ?? []) {
      const consumer = s(c.fields.consumer);
      out.push(
        mk(
          "event-obligation",
          c.source_anchor,
          { event: name, consumer },
          `Event ${name} consumed by ${consumer}`,
        ),
      );
    }
  }
  return out;
}

/**
 * δ_workflowStep: one obligation per workflow Step Table row. When a row documents an
 * exact `On Failure` outcome (e.g. "return 400"), a second obligation encodes that
 * failure branch — this is read verbatim from the cell, never inferred from prose.
 */
function deriveWorkflowSteps(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const st of byType(graph, "WorkflowStep")) {
    const workflow = s(st.fields.workflow);
    const num = s(st.fields.num);
    const step = s(st.fields.step);
    out.push(
      mk(
        "workflow-step",
        st.source_anchor,
        { workflow, step: num, case: "success" },
        `Workflow ${workflow} step ${num} (${step}) succeeds`,
      ),
    );
    // Encode the failure branch ONLY when the cell names a concrete outcome (status
    // code or "return <x>"); a bare "-" or empty cell yields no failure obligation.
    const onFailure = s(st.fields.on_failure).trim();
    const concreteFailure =
      /\b(return|reject|throw|\d{3})\b/i.test(onFailure) && onFailure !== "-";
    if (concreteFailure) {
      out.push(
        mk(
          "workflow-step",
          st.source_anchor,
          { workflow, step: num, case: "failure", outcome: onFailure },
          `Workflow ${workflow} step ${num} (${step}) on failure: ${onFailure}`,
        ),
      );
    }
  }
  return out;
}

/**
 * δ_errorObligation: one obligation per (operation × Error-States row). Each row of
 * an operation's `### Error States` table is a documented mapping from a failure
 * condition to an error result/code; the engine emits a distinct obligation per row.
 * At the semantic level these case-expand onto `error:<op>` (the oracle catalogues
 * one "X error mapping" row per operation), exactly as postconditions op-bucket —
 * an INV-1-safe case-fold (distinct operations stay distinct keys).
 */
function deriveErrorObligations(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const e of byType(graph, "ErrorState")) {
    const op = s(e.fields.op);
    const condition = s(e.fields.condition);
    const result = s(e.fields.result);
    out.push(
      mk(
        "error-obligation",
        e.source_anchor,
        { op, condition, result },
        `Error mapping for ${op}: "${condition}" -> ${result}`,
      ),
    );
  }
  return out;
}

/** δ_query: one obligation per query (read behavior). */
function deriveQueries(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const q of byType(graph, "Query")) {
    const name = s(q.fields.name);
    out.push(
      mk(
        "query-behavior",
        q.source_anchor,
        { query: name },
        `Query ${name} returns its projected read model without side effects`,
      ),
    );
  }
  return out;
}

/** δ_mapping: one obligation per mapping section. */
function deriveMappings(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const m of byType(graph, "Mapping")) {
    const name = s(m.fields.name);
    out.push(
      mk(
        "mapping-row",
        m.source_anchor,
        { mapping: name },
        `Mapping ${name} (${s(m.fields.from)} -> ${s(m.fields.to)}) maps all fields correctly`,
      ),
    );
  }
  return out;
}

/** δ_domainField: one obligation per domain.md value-object/entity field (L3). */
function deriveDomainFields(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const f of byType(graph, "DomainField")) {
    const entity = s(f.fields.entity);
    const field = s(f.fields.field);
    const ftype = s(f.fields.ftype);
    const constraint = s(f.fields.constraint);
    out.push(
      mk(
        "domain-field",
        f.source_anchor,
        { entity, field, ftype, constraint },
        `${entity}.${field}: ${ftype}${constraint ? ` (${constraint})` : ""}`,
      ),
    );
  }
  return out;
}

/** δ_domainEnum: one obligation per domain.md enum vocabulary (L3). */
function deriveDomainEnums(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const e of byType(graph, "Enum")) {
    const name = s(e.fields.name);
    const values = s(e.fields.values);
    out.push(
      mk(
        "domain-enum",
        e.source_anchor,
        { name, values },
        `${name} vocabulary is exactly {${values}}`,
      ),
    );
  }
  return out;
}

/** δ_policyDecision: one obligation per rules.md decision-table row (L3). */
function derivePolicyDecisions(graph: ConceptGraph): Obligation[] {
  const out: Obligation[] = [];
  for (const d of byType(graph, "PolicyDecision")) {
    const group = s(d.fields.group);
    const condition = s(d.fields.condition);
    const behavior = s(d.fields.behavior);
    out.push(
      mk(
        "policy-decision",
        d.source_anchor,
        { group, condition, behavior },
        `${group}: when ${condition}, behavior is ${behavior}`,
      ),
    );
  }
  return out;
}

/** One structural conformance obligation per normalized concept declaration. */
function deriveSpecConcepts(graph: ConceptGraph): Obligation[] {
  return byType(graph, "SpecConcept").map((node) => {
    const concept = s(node.fields.concept);
    const metaType = s(node.fields.meta_type);
    return mk(
      "spec-concept",
      node.source_anchor,
      { concept, meta_type: metaType },
      `${concept} is declared with meta-type ${metaType}`,
    );
  });
}

/** One structural conformance obligation per normalized typed relationship. */
function deriveSpecRelationships(graph: ConceptGraph): Obligation[] {
  return byType(graph, "SpecRelationship").map((node) => {
    const from = s(node.fields.from);
    const edge = s(node.fields.edge);
    const to = s(node.fields.to);
    return mk(
      "spec-relationship",
      node.source_anchor,
      { from, edge, to },
      `${from} --${edge}--> ${to} is an admitted typed relationship`,
    );
  });
}

/** One structural conformance obligation per normalized field declaration. */
function deriveSpecFields(graph: ConceptGraph): Obligation[] {
  return byType(graph, "SpecField").map((node) => {
    const concept = s(node.fields.concept);
    const field = s(node.fields.field);
    const valueType = s(node.fields.value_type);
    const required = s(node.fields.required);
    const identity = s(node.fields.identity);
    return mk(
      "spec-field",
      node.source_anchor,
      { concept, field, value_type: valueType, required, identity },
      `${concept}.${field} has type ${valueType} (required=${required}, identity=${identity || "no"})`,
    );
  });
}

/** One structural conformance obligation per normalized concept attribute. */
function deriveSpecAttributes(graph: ConceptGraph): Obligation[] {
  return byType(graph, "SpecAttribute").map((node) => {
    const concept = s(node.fields.concept);
    const attribute = s(node.fields.attribute);
    const value = s(node.fields.value);
    return mk(
      "spec-attribute",
      node.source_anchor,
      { concept, attribute, value },
      `${concept}.${attribute} is ${value}`,
    );
  });
}

/**
 * δ(G, Δ): pure, total, deterministic. Same (G, Δ) -> byte-identical obligations.
 * Obligations are returned sorted by obligation_key so the set is order-free.
 */
export function derive(
  graph: ConceptGraph,
  _rules: RuleSet = DEFAULT_RULE_SET,
): Obligation[] {
  const all: Obligation[] = [
    ...deriveValidTransitions(graph),
    ...deriveInvalidTransitions(graph),
    ...deriveInvariants(graph),
    ...deriveRuleValidations(graph),
    ...deriveCalculations(graph),
    ...derivePostconditions(graph),
    ...deriveContracts(graph),
    ...deriveEvents(graph),
    ...deriveWorkflowSteps(graph),
    ...deriveQueries(graph),
    ...deriveMappings(graph),
    ...deriveErrorObligations(graph),
    ...deriveDomainFields(graph),
    ...deriveDomainEnums(graph),
    ...derivePolicyDecisions(graph),
    ...deriveSpecConcepts(graph),
    ...deriveSpecRelationships(graph),
    ...deriveSpecFields(graph),
    ...deriveSpecAttributes(graph),
  ];
  all.sort((a, b) =>
    a.obligation_key < b.obligation_key
      ? -1
      : a.obligation_key > b.obligation_key
        ? 1
        : 0,
  );
  return all;
}
