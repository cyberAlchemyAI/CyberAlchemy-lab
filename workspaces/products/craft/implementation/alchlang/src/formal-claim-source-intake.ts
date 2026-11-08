import { loadApplicationEvidenceFiles } from "./application-evidence-files.js";
import { checkFormalClaimSourceBoundary } from "./formal-claim-source-boundary.js";
import { validateExactFormalSourceRef } from "./formal-claim-lowering.js";
import { CompilationRejected } from "./model.js";
import { createHash } from "node:crypto";
import path from "node:path";

type RecordValue = Record<string, unknown>;
const isRecord = (value: unknown): value is RecordValue => !!value && typeof value === "object" && !Array.isArray(value);
const ceiling = "Proposition formation only; no BusinessMeaning acceptance, definition preservation, claim admission, TDE, F5, EVF, or runtime guarantee.";

export type FormalClaimFormationResult = {
  schema_version: "alchlang.formal-claim-formation-result/v1";
  status: "checked" | "unsupported" | "rejected";
  authority_effect: "none";
  claim_ceiling: string;
  claim_source?: { path: string; sha256: string; size_bytes: number };
  selected_profile?: string;
  checker?: "alchlang-fol/1";
  profile_ref_digest?: string;
  representation_digest?: string;
  ast_digest?: string;
  reason?: "profile-or-media-type";
  code?: string;
};

const result = (status: FormalClaimFormationResult["status"], extra: Partial<FormalClaimFormationResult> = {}): FormalClaimFormationResult =>
  ({ schema_version: "alchlang.formal-claim-formation-result/v1", status, authority_effect: "none", claim_ceiling: ceiling, ...extra });
export const rejectFormalClaimFormationRequest = (code: string): FormalClaimFormationResult => result("rejected", { code });

/** Exact-file, opt-in v4 proposition formation. No discovery or authority effect. */
export function checkFormalClaimSourceIntake(request: unknown): FormalClaimFormationResult {
  if (!isRecord(request) || Object.keys(request).sort().join("|") !== "claim_ref|root_directory|schema_version|selected_profile"
    || request.schema_version !== "alchlang.formal-claim-formation-request/v1"
    || typeof request.root_directory !== "string" || !path.isAbsolute(request.root_directory)
    || typeof request.selected_profile !== "string")
    return result("rejected", { code: "FORMATION_REQUEST_SHAPE" });

  let ref: ReturnType<typeof validateExactFormalSourceRef>;
  let bytes: Buffer;
  try {
    ref = validateExactFormalSourceRef(request.claim_ref, "$request/claim_ref");
    const files = loadApplicationEvidenceFiles(request.root_directory, [ref]);
    bytes = files.get(ref.path)!;
  } catch (error) {
    if (error instanceof CompilationRejected)
      return result("rejected", { code: error.issues[0]?.code ?? "COMPILATION_REJECTED" });
    if (error instanceof Error && "code" in error && typeof error.code === "string")
      return result("rejected", { code: "CLAIM_SOURCE_IO" });
    throw error;
  }

  const claimSource = { path: ref.path, sha256: createHash("sha256").update(bytes).digest("hex"), size_bytes: bytes.length };
  let claim: unknown;
  try { claim = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)); }
  catch { return result("rejected", { code: "CLAIM_SOURCE_JSON", claim_source: claimSource }); }
  if (!isRecord(claim) || claim.schema_version !== "domainspec-v2.formal-claim-source/v4-candidate")
    return result("rejected", { code: "CLAIM_SOURCE_SHAPE", claim_source: claimSource });

  const formation = checkFormalClaimSourceBoundary(request.root_directory, claim, request.selected_profile);
  if (formation.status === "checked") return result("checked", { claim_source: claimSource, ...formation });
  if (formation.status === "unsupported") return result("unsupported", { claim_source: claimSource, reason: formation.reason });
  return result("rejected", { claim_source: claimSource, code: formation.code });
}
