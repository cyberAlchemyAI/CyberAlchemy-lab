/**
 * meta-type-noncollapse.ts — pure core of the node non-collapse checker.
 *
 * Implements DESIGN-SPEC-v2 (node-side mirror of the D3 edge gate, seated as D6's third challenge).
 * No I/O here: the CLI (tools/validate-meta-types-noncollapse.ts) loads schemas + the relationship
 * authority and calls summarize(); tests import these functions directly with synthetic inputs.
 */

// The TOTAL rule->class map over the supported keywords (closes findings c2).
export const STRUCTURE_READING = new Set([
  "at-least-one",
  "all-nonempty",
  "none",
  "section-contains",
  "table-has-column",
]);
export const ATTESTATION = new Set([
  "attribute-equals",
  "attribute-one-of",
  "attribute-present",
  "attribute-nonempty/v1",
]);

// The owner-enumerated exception allow-list (closes a3): the formal_return_type sort. Owner-authored,
// never self-claimed. Passed into deriveFacts so tests can vary it; the CLI defaults to this.
export const DEFAULT_EXCEPTION_ALLOWLIST = new Set(["rule", "policy", "calculation"]);

export type Criterion = {
  rule: string;
  column?: string;
  pattern?: string;
  key?: string;
  value?: string;
  values?: string[];
};
export type Schema = {
  meta_type: string;
  criterion?: Record<string, Criterion>;
  edge_participation?: { source_of?: string[]; target_of?: string[] };
  [key: string]: unknown;
};
export type EdgeMaps = { sourceEdges: Map<string, Set<string>>; targetEdges: Map<string, Set<string>> };

export type TypeFacts = {
  name: string; // normalized
  display: string;
  structKeys: Set<string>;
  attestationOnly: boolean;
  sourceE: Set<string>;
  targetE: Set<string>;
  onAllowlist: boolean;
};
export type Via = "exception-lane" | "W-struct" | "W-edge" | "W-struct+W-edge" | "no witness";
export type PairVerdict = { a: string; b: string; verdict: "distinct" | "collapse"; via: Via };
export type Summary = {
  facts: TypeFacts[];
  pairs: PairVerdict[];
  collapses: PairVerdict[];
  exceptionLane: string[];
  attestationOnlyNotExempt: string[];
  unclassified: string[];
};

export function normalize(s: string): string {
  return s.trim().toLowerCase().replace(/\[[^\]]*\]/g, "").replace(/[^a-z0-9]+/g, "");
}

/** Guard for the total-classification invariant (c2): any rule keyword outside the supported map. */
export function findUnclassifiedRules(schemas: Schema[]): string[] {
  const out: string[] = [];
  for (const s of schemas) {
    for (const [name, crit] of Object.entries(s.criterion || {})) {
      if (!STRUCTURE_READING.has(crit.rule) && !ATTESTATION.has(crit.rule)) {
        out.push(`${s.meta_type}.${name} uses unclassified rule '${crit.rule}'`);
      }
    }
  }
  return out;
}

export function deriveFacts(schemas: Schema[], edges: EdgeMaps, allowlist: Set<string>): TypeFacts[] {
  return schemas.map((s) => {
    const name = normalize(s.meta_type);
    const structKeys = new Set<string>();
    let hasStruct = false;
    for (const crit of Object.values(s.criterion || {})) {
      if (STRUCTURE_READING.has(crit.rule)) {
        hasStruct = true;
        // canonical clause key: rule + the column/pattern it reads. Attestation values are NEVER read
        // here — that is what makes witnesses invariant under attestation permutation (closes d1).
        structKeys.add(`${crit.rule}::${(crit.column || crit.pattern || "").toLowerCase()}`);
      }
    }
    return {
      name,
      display: s.meta_type,
      structKeys,
      attestationOnly: !hasStruct,
      sourceE: edges.sourceEdges.get(name) || new Set(),
      targetE: edges.targetEdges.get(name) || new Set(),
      onAllowlist: allowlist.has(name),
    };
  });
}

/** Structural separating witness (closes a2): a structure-reading clause present in exactly one of
 * A/B, or contradictory on the same column. A byte-identical shared clause separates nothing and is
 * in neither symmetric difference, so it is never credited. */
export function wStruct(a: TypeFacts, b: TypeFacts): boolean {
  for (const k of a.structKeys) if (!b.structKeys.has(k)) return true;
  for (const k of b.structKeys) if (!a.structKeys.has(k)) return true;
  return false;
}

/** Edge-participation separating witness (closes a1): participation resolved through the DS-D8
 * authority differs. The caller builds the edge maps from the authority, never from raw schema slices. */
export function wEdge(a: TypeFacts, b: TypeFacts): boolean {
  return !setEq(a.sourceE, b.sourceE) || !setEq(a.targetE, b.targetE);
}

export function evaluatePairs(facts: TypeFacts[]): PairVerdict[] {
  const pairs: PairVerdict[] = [];
  for (let i = 0; i < facts.length; i++) {
    for (let j = i + 1; j < facts.length; j++) {
      const a = facts[i]!;
      const b = facts[j]!;
      if (a.onAllowlist || b.onAllowlist) {
        pairs.push({ a: a.display, b: b.display, verdict: "distinct", via: "exception-lane" });
        continue;
      }
      const s = wStruct(a, b);
      const e = wEdge(a, b);
      if (s || e) {
        pairs.push({
          a: a.display,
          b: b.display,
          verdict: "distinct",
          via: s && e ? "W-struct+W-edge" : s ? "W-struct" : "W-edge",
        });
      } else {
        pairs.push({ a: a.display, b: b.display, verdict: "collapse", via: "no witness" });
      }
    }
  }
  return pairs;
}

export function summarize(schemas: Schema[], edges: EdgeMaps, allowlist: Set<string>): Summary {
  const facts = deriveFacts(schemas, edges, allowlist);
  const pairs = evaluatePairs(facts);
  return {
    facts,
    pairs,
    collapses: pairs.filter((p) => p.verdict === "collapse"),
    exceptionLane: facts.filter((f) => f.onAllowlist).map((f) => f.display).sort(),
    attestationOnlyNotExempt: facts.filter((f) => f.attestationOnly && !f.onAllowlist).map((f) => f.display).sort(),
    unclassified: findUnclassifiedRules(schemas),
  };
}

function setEq(a: Set<string>, b: Set<string>): boolean {
  if (a.size !== b.size) return false;
  for (const x of a) if (!b.has(x)) return false;
  return true;
}
