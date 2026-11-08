import assert from "node:assert/strict";
import test from "node:test";
import { CompilationRejected, compileCarrier } from "../src/index.js";
import { unseenCarrier } from "./compiler.test.js";

function rejects(code: string, mutate: (carrier: any) => void): void {
  const carrier: any = unseenCarrier(); mutate(carrier);
  assert.throws(() => compileCarrier(carrier), (error: unknown) => error instanceof CompilationRejected && error.issues.some((issue) => issue.code === code));
}

test("unknown operators fail closed", () => rejects("UNKNOWN_OPERATOR", (carrier) => { carrier.rules[0].condition.operator = "approximately"; }));
test("dangling references fail closed", () => rejects("UNRESOLVED_REFERENCE", (carrier) => { carrier.actions[0].input_facts = ["missing-fact"]; }));
test("type mismatches fail closed", () => rejects("TYPE_MISMATCH", (carrier) => { carrier.rules[0].condition.operands[1].value_type = "string"; }));
test("missing owners fail closed", () => rejects("MISSING_OWNER", (carrier) => { carrier.owners = []; }));
test("missing authority boundaries fail closed", () => rejects("MISSING_AUTHORITY_BOUNDARY", (carrier) => { carrier.actions[0].authority_boundary_ref = "ambient-authority"; }));
test("unsupported constructs fail closed", () => rejects("UNSUPPORTED_SEMANTIC_CONSTRUCT", (carrier) => { carrier.schema_version = "future/99"; }));
test("multi-entity carriers require explicit fact subjects", () => rejects("AMBIGUOUS_FACT_SUBJECT", (carrier) => { carrier.terms.push({ term_id: "renewal", kind: "entity", meaning: "A loan renewal." }); }));
test("fact subjects must resolve to declared entities", () => rejects("UNRESOLVED_REFERENCE", (carrier) => { carrier.facts[0].subject_ref = "missing-entity"; }));
