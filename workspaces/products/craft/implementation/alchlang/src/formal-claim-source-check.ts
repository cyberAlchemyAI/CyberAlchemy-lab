import { createHash } from "node:crypto";
import { parseFormalProposition, type FormalSignature } from "./formal-claim.js";
import { FOL_CORE_PROFILE_SHA256 } from "./formal-claim-lowering.js";
import { CompilationRejected } from "./model.js";

type RecordValue = Record<string, unknown>;
const sha = (value: string) => createHash("sha256").update(value).digest("hex");
const canonical = (value: unknown): string => Array.isArray(value)
  ? `[${value.map(canonical).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as RecordValue)[key])}`).join(",")}}`
    : JSON.stringify(value);
const isRecord = (value: unknown): value is RecordValue => !!value && typeof value === "object" && !Array.isArray(value);
const reject = (code: string, message: string): never => { throw new CompilationRejected([{ code, path: "$claim/canonical_proposition", message }]); };

/** Formation only. Unsupported representations are never treated as valid formulae. */
export function checkFormalClaimSourceProposition(claim: unknown, selectedProfile: unknown):
  | { status: "checked"; checker: "alchlang-fol/1"; representation_digest: string; ast_digest: string }
  | { status: "unsupported"; reason: "profile-or-media-type" } {
  if (!isRecord(claim) || claim.schema_version !== "domainspec-v2.formal-claim-source/v4-candidate"
    || !isRecord(claim.canonical_proposition) || !isRecord(claim.formal_signature))
    reject("FOL_SOURCE_SHAPE", "expected a FormalClaimSource/v4 proposition and signature");
  const checkedClaim = claim as RecordValue;
  const proposition = checkedClaim.canonical_proposition as RecordValue;
  if (typeof proposition.representation !== "string" || !proposition.representation.trim()
    || typeof proposition.representation_media_type !== "string" || !proposition.representation_media_type.trim()
    || typeof proposition.representation_digest !== "string"
    || typeof proposition.semantic_identity !== "string"
    || typeof proposition.semantic_identity_digest !== "string")
    reject("FOL_SOURCE_SHAPE", "missing source or identity bytes");
  const source = proposition.representation as string;
  if (sha(source) !== proposition.representation_digest)
    reject("FOL_SOURCE_STALE", "proposition source digest differs");
  if (sha(proposition.semantic_identity as string) !== proposition.semantic_identity_digest)
    reject("FOL_SOURCE_IDENTITY", "semantic identity digest differs");
  const signature = checkedClaim.formal_signature as RecordValue;
  if (!Array.isArray(signature.sorts) || !Array.isArray(signature.functions)
    || !Array.isArray(signature.predicates) || !Array.isArray(signature.constants)
    || !signature.sorts.every(item => isRecord(item) && typeof item.name === "string")
    || ![...signature.functions, ...signature.predicates].every(item => isRecord(item)
      && typeof item.name === "string" && Array.isArray(item.parameter_sorts)
      && item.parameter_sorts.every((sort: unknown) => typeof sort === "string"))
    || !signature.functions.every(item => typeof item.result_sort === "string")
    || !signature.constants.every(item => isRecord(item) && typeof item.name === "string" && typeof item.sort === "string"))
    reject("FOL_SOURCE_SHAPE", "invalid formal signature");
  if (!isRecord(selectedProfile) || `${selectedProfile.profile_id}/${selectedProfile.version}` !== "fol-core/1-candidate"
    || sha(canonical(selectedProfile)) !== FOL_CORE_PROFILE_SHA256
    || proposition.representation_media_type !== "text/x-alchlang-fol")
    return { status: "unsupported", reason: "profile-or-media-type" };
  const ast = parseFormalProposition(source, signature as unknown as FormalSignature);
  const astIdentity = canonical(ast);
  if (astIdentity !== proposition.semantic_identity || sha(astIdentity) !== proposition.semantic_identity_digest)
    reject("FOL_SOURCE_IDENTITY", "semantic identity does not match the checked syntax tree");
  return { status: "checked", checker: "alchlang-fol/1", representation_digest: sha(source), ast_digest: sha(astIdentity) };
}
