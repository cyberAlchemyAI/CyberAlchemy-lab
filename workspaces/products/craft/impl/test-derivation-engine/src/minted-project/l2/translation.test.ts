import { describe, expect, it } from "vitest";

import { extractFacts } from "./extract.js";
import { fixtureGraph, fixtureProperty } from "./extract.test.js";
import { translateAlloy } from "./translate-alloy.js";
import { translateDatalog } from "./translate-datalog.js";

describe("EVF L2 provider translations", () => {
  it("emits complete deterministic Souffle facts", () => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    const translation = translateDatalog(projection, fixtureProperty());
    expect(translation.files["Node.facts"].trim().split("\n")).toHaveLength(5);
    expect(translation.files["Edge.facts"].trim().split("\n")).toHaveLength(4);
    expect(translation.files["RequiredSource.facts"].trim().split("\n")).toHaveLength(2);
    expect(translation.files["Target.facts"]).toBe("financial-settlement.PayoutCreatedEvent\n");
    expect(translation.selected_tuples).toEqual(projection.selected_edges);
  });

  it("emits one fixed Alloy atom per node and only exact selected tuples", () => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    const translation = translateAlloy(projection, fixtureProperty());
    expect(translation.exact_scope).toEqual({ Node: 5 });
    expect(translation.selected_tuples).toEqual(projection.selected_edges);
    expect(translation.model).toContain("one sig N0, N1, N2, N3, N4 extends Node {}");
    expect(translation.model).toContain("assert NoViolation");
    expect(translation.model).toContain("check NoViolation for exactly 5 Node");
    expect(translation.model).not.toContain("calculates");
  });

  it("is byte-stable on replay", () => {
    const projection = extractFacts(fixtureGraph(), fixtureProperty());
    expect(translateDatalog(projection, fixtureProperty()))
      .toEqual(translateDatalog(projection, fixtureProperty()));
    expect(translateAlloy(projection, fixtureProperty()))
      .toEqual(translateAlloy(projection, fixtureProperty()));
  });
});
