import { evaluateEnumBijection } from "../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization } from "../../realization/enum/normalize-enum-realization.js";
import { removeEnumMember } from "../../realization/mutation/remove-enum-member.js";
import { observeGeneratedTypeScriptEnum } from "../../typescript/adapter/enum/index.js";
import {
  compileGeneratedEnum,
  getTypeScriptCompileExpectation,
} from "../../typescript/compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum } from "../../typescript/generator/enum/emit-enum.js";

export {
  compileGeneratedEnum,
  emitTypeScriptEnum,
  evaluateEnumBijection,
  getTypeScriptCompileExpectation,
  normalizeEnumRealization,
  observeGeneratedTypeScriptEnum,
  removeEnumMember,
};

export const enumV1CompatibilityFacade = Object.freeze({
  schema_version: "EnumV1CompatibilityFacade/v1" as const,
  normalize: normalizeEnumRealization,
  emit: emitTypeScriptEnum,
  compile: compileGeneratedEnum,
  compileExpectation: getTypeScriptCompileExpectation,
  observe: observeGeneratedTypeScriptEnum,
  evaluate: evaluateEnumBijection,
  mutate: removeEnumMember,
  removal: "separate-migration-required" as const,
  authority_effect: "none" as const,
});
