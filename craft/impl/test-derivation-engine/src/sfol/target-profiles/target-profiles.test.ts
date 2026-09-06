import { describe, expect, it } from "vitest";
import { resolveSfolTargetProfile, SFOL_TARGET_PROFILES } from "./index.js";

describe("SFOL target profile registry", () => {
  it("resolves only exact registered profile versions", () => {
    expect(SFOL_TARGET_PROFILES).toHaveLength(2);
    expect(resolveSfolTargetProfile("domainspec.sfol.target.pure-function", "1.0.0")?.effect_authority).toBe("none");
    expect(resolveSfolTargetProfile("domainspec.sfol.target.pure-function", "2.0.0")).toBeNull();
  });
});
