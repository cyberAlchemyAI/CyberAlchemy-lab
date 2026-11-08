import { describe, expect, it } from "vitest";

import { assertExactInstanceModel } from "./alloy.js";
import { extractFacts } from "./extract.js";
import { fixtureGraph, fixtureProperty } from "./extract.test.js";
import { translateAlloy } from "./translate-alloy.js";

describe("EVF L2 Alloy exact-instance model", () => {
  it("accepts only the byte-exact fixed universe and selected relation", () => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    const model = translateAlloy(projection, fixtureProperty()).model;
    expect(() => assertExactInstanceModel(model, projection, fixtureProperty())).not.toThrow();
  });

  it.each([
    (model: string) => model.replace("exactly 5 Node", "exactly 6 Node"),
    (model: string) => model.replace("extends Node {}", ", Extra extends Node {}"),
    (model: string) => model.replace("N1->N3", "N1->N3 + N3->N1"),
    (model: string) => model.replace("check NoViolation", "check Other"),
  ])("rejects extra scope, atoms, tuples, or command drift", (mutate) => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    const model = translateAlloy(projection, fixtureProperty()).model;
    const mutated = mutate(model);
    expect(mutated).not.toBe(model);
    expect(() => assertExactInstanceModel(mutated, projection, fixtureProperty()))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_SCOPE_INVALID" }));
  });
});
