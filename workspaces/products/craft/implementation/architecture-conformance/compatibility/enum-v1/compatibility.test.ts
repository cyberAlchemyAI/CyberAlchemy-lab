import { describe, expect, it } from "vitest";

import { evaluateEnumBijection as currentEvaluate } from "../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization as currentNormalize } from "../../realization/enum/normalize-enum-realization.js";
import { removeEnumMember as currentMutate } from "../../realization/mutation/remove-enum-member.js";
import { observeGeneratedTypeScriptEnum as currentObserve } from "../../typescript/adapter/enum/index.js";
import { compileGeneratedEnum as currentCompile } from "../../typescript/compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum as currentEmit } from "../../typescript/generator/enum/emit-enum.js";
import {
  enumV1CompatibilityFacade,
  evaluateEnumBijection,
  normalizeEnumRealization,
  removeEnumMember,
  observeGeneratedTypeScriptEnum,
  compileGeneratedEnum,
  emitTypeScriptEnum,
} from "./index.js";

describe("frozen Enum v1 compatibility facade", () => {
  it("preserves every existing implementation function by identity", () => {
    expect(normalizeEnumRealization).toBe(currentNormalize);
    expect(emitTypeScriptEnum).toBe(currentEmit);
    expect(compileGeneratedEnum).toBe(currentCompile);
    expect(observeGeneratedTypeScriptEnum).toBe(currentObserve);
    expect(evaluateEnumBijection).toBe(currentEvaluate);
    expect(removeEnumMember).toBe(currentMutate);
    expect(enumV1CompatibilityFacade).toEqual(expect.objectContaining({
      schema_version: "EnumV1CompatibilityFacade/v1",
      removal: "separate-migration-required",
      authority_effect: "none",
    }));
  });
});
