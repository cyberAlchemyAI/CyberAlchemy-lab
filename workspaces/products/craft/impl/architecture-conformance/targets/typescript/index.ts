import {
  compileGeneratedEnum,
  getTypeScriptCompileExpectation,
} from "../../typescript/compiler/enum/compile-generated-enum.js";

export const typescriptTargetProvider = Object.freeze({
  schema_version: "TargetProvider/v2" as const,
  provider_id: "target.typescript",
  provider_version: "1.0.0",
  compile: compileGeneratedEnum,
  compileExpectation: getTypeScriptCompileExpectation,
  authority_effect: "none" as const,
});
