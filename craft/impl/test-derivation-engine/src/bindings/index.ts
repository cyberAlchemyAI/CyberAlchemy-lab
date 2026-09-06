// P4 — Binding sidecar loader. A per-feature `bindings/<feature>.json` declares,
// per obligation (matched by rule_type + canonical_params), WHICH pure domain
// function + arg shape the test targets — and NOTHING about the expected answer.
// Expected values come from the Formal AST at emit time, so generation stays pure
// (the sidecar is read once, upstream, exactly like the spec docs). The binding is
// data, not an oracle: it says which function, never what value.

import { readFileSync } from "node:fs";
import type { Obligation } from "../ir/types.js";

export type BindingStrategy = "ast-eval" | "property" | "closed-form";

/**
 * A fixture env for a closed-form binding. `vars`/`collections` feed the pure
 * evaluator (the engine derives EXPECTED from the SPEC Formal over THIS env, it
 * never reads the impl). `call_arg` is the literal JS argument object passed to
 * the bound fn at runtime — its fields MUST mirror the env so the spec-evaluated
 * EXPECTED and the impl-under-test see the same inputs. This is fixture INPUT,
 * never the expected OUTPUT (no oracle in the data — generation stays pure).
 */
export interface ClosedFormFixture {
  readonly vars?: Readonly<Record<string, number | string>>;
  readonly collections?: Readonly<
    Record<string, readonly Readonly<Record<string, number>>[]>
  >;
  /** Literal argument object (JSON) the emitted test passes to `symbol(...)`. */
  readonly call_arg: unknown;
}

export interface Binding {
  readonly match: Readonly<Record<string, string>>;
  readonly module: string;
  readonly symbol: string;
  readonly strategy: BindingStrategy;
  readonly kind: string;
  readonly result_field?: string;
  readonly decision_field?: string;
  readonly tx_type?: string;
  readonly args?: readonly string[];
  /** For `closed-form` bindings: the fixture env + the literal call argument. */
  readonly fixture?: ClosedFormFixture;
}

export interface BindingSet {
  readonly feature: string;
  readonly emit_dir: string;
  readonly test_file: string;
  readonly bindings: readonly Binding[];
}

/** Read a binding sidecar from disk. The only I/O; happens once, upstream of emit. */
export function loadBindings(path: string): BindingSet {
  const raw = JSON.parse(readFileSync(path, "utf8")) as Partial<BindingSet>;
  return {
    feature: raw.feature ?? "",
    emit_dir: raw.emit_dir ?? "",
    test_file: raw.test_file ?? "derived.test.ts",
    bindings: raw.bindings ?? [],
  };
}

/**
 * Resolve the binding for an obligation: the first binding whose `match` is a
 * subset of (rule_type + canonical_params). Pure. Returns null when no pure
 * target is declared (-> the emitter renders a coverage_gap skip).
 */
export function bindingFor(
  obligation: Obligation,
  set: BindingSet,
): Binding | null {
  const haystack: Record<string, string> = {
    rule_type: obligation.rule_type,
  };
  for (const [k, v] of Object.entries(obligation.canonical_params)) {
    haystack[k] = v == null ? "" : String(v);
  }
  for (const b of set.bindings) {
    const hit = Object.entries(b.match).every(([k, v]) => haystack[k] === v);
    if (hit) return b;
  }
  return null;
}

export type ExactBindingFailureCode =
  | "BINDING_MISSING"
  | "BINDING_DUPLICATE"
  | "BINDING_AMBIGUOUS";

export class ExactBindingResolutionError extends Error {
  readonly code: ExactBindingFailureCode;

  constructor(code: ExactBindingFailureCode, message: string) {
    super(message);
    this.name = "ExactBindingResolutionError";
    this.code = code;
  }
}

/**
 * Resolve an EVF typed binding by obligation identity with exact-one semantics.
 * This is deliberately separate from the legacy first-match resolver above.
 */
export function resolveExactBinding<
  T extends { readonly obligation_id: string; readonly binding_id: string },
>(
  obligationId: string,
  bindings: readonly T[],
  expectedBindingId?: string,
): T {
  const matches = bindings.filter((binding) => binding.obligation_id === obligationId);
  if (matches.length === 0) {
    throw new ExactBindingResolutionError(
      "BINDING_MISSING",
      `no binding for obligation ${obligationId}`,
    );
  }
  if (matches.length > 1) {
    const identities = new Set(matches.map((binding) => binding.binding_id));
    throw new ExactBindingResolutionError(
      identities.size === 1 ? "BINDING_DUPLICATE" : "BINDING_AMBIGUOUS",
      `${matches.length} bindings for obligation ${obligationId}`,
    );
  }
  const selected = matches[0]!;
  if (expectedBindingId !== undefined && selected.binding_id !== expectedBindingId) {
    throw new ExactBindingResolutionError(
      "BINDING_AMBIGUOUS",
      `binding ${selected.binding_id} does not match ${expectedBindingId}`,
    );
  }
  return selected;
}
