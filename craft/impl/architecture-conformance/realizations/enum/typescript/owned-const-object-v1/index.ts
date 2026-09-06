import { removeEnumMember } from "../../../../realization/mutation/remove-enum-member.js";
import { observeGeneratedTypeScriptEnum } from "../../../../typescript/adapter/enum/index.js";
import { emitTypeScriptEnum } from "../../../../typescript/generator/enum/emit-enum.js";

export const ownedConstObjectRealizationProvider = Object.freeze({
  schema_version: "RealizationProvider/v2" as const,
  provider_id: "realization.enum.typescript.owned-const-object-v1",
  provider_version: "1.0.0",
  modes: Object.freeze(["generate-and-observe" as const]),
  emit: emitTypeScriptEnum,
  observe: observeGeneratedTypeScriptEnum,
  mutate: removeEnumMember,
  authority_effect: "none" as const,
});
