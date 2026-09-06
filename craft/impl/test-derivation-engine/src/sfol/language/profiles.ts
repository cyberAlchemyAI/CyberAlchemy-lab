import {
  DS_SFOL_LANGUAGE_VERSION,
  NODE_LOGIC_SCHEMA_VERSION,
  type LogicClauseKind,
  type LogicDeclarationTag,
  type LogicTermTag,
  type SfolLanguageVersion,
} from "./ast.js";
import {
  contractFailure,
  contractSuccess,
  type SfolContractResult,
} from "./contracts.js";

export interface SfolLanguageProfile {
  readonly profile_id: "domainspec-sfol";
  readonly language_version: SfolLanguageVersion;
  readonly node_schema_version: typeof NODE_LOGIC_SCHEMA_VERSION;
  readonly term_tags: readonly LogicTermTag[];
  readonly declaration_tags: readonly LogicDeclarationTag[];
  readonly clause_kinds: readonly LogicClauseKind[];
  readonly exact_numeric_sorts: readonly ["integer", "rational"];
  readonly quantifier_domain: "declared-finite-fixture-universe";
  readonly unsupported_policy: "reject";
}

export const DS_SFOL_V1_PROFILE: SfolLanguageProfile = deepFreeze({
  profile_id: "domainspec-sfol",
  language_version: DS_SFOL_LANGUAGE_VERSION,
  node_schema_version: NODE_LOGIC_SCHEMA_VERSION,
  term_tags: [
    "literal",
    "variable",
    "field",
    "record",
    "list",
    "set",
    "enum",
    "arithmetic",
    "negate",
    "comparison",
    "boolean",
    "not",
    "conditional",
    "fold",
    "quantifier",
    "call",
  ],
  declaration_tags: [
    "enum",
    "record",
    "function",
    "predicate",
    "fixture-universe",
  ],
  clause_kinds: [
    "function",
    "predicate",
    "invariant",
    "precondition",
    "postcondition",
    "transition",
    "effect-relation",
  ],
  exact_numeric_sorts: ["integer", "rational"],
  quantifier_domain: "declared-finite-fixture-universe",
  unsupported_policy: "reject",
});

export const DS_SFOL_PROFILE_REGISTRY: Readonly<
  Record<SfolLanguageVersion, SfolLanguageProfile>
> = Object.freeze({
  [DS_SFOL_LANGUAGE_VERSION]: DS_SFOL_V1_PROFILE,
});

export function resolveSfolLanguageProfile(
  version: string,
): SfolContractResult<SfolLanguageProfile> {
  if (version === DS_SFOL_LANGUAGE_VERSION) {
    return contractSuccess(DS_SFOL_PROFILE_REGISTRY[version]);
  }
  return contractFailure({
    code: "SFOL_LANGUAGE_UNKNOWN_VERSION",
    stage: "contract",
    path: "$.language_version",
    detail: `unsupported DS-SFOL language version ${version}`,
  });
}

function deepFreeze<T>(value: T): T {
  if (typeof value !== "object" || value === null || Object.isFrozen(value)) {
    return value;
  }
  for (const child of Object.values(value)) {
    deepFreeze(child);
  }
  return Object.freeze(value);
}
