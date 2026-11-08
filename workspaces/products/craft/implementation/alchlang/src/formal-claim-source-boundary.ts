import { createHash } from "node:crypto";
import { loadApplicationEvidenceFiles } from "./application-evidence-files.js";
import { checkFormalClaimSourceProposition } from "./formal-claim-source-check.js";
import { validateExactFormalSourceRef } from "./formal-claim-lowering.js";
import { CompilationRejected } from "./model.js";

type RecordValue = Record<string, unknown>;
type FormationResult =
  | { status: "checked"; checker: "alchlang-fol/1"; selected_profile: string; profile_ref_digest: string; representation_digest: string; ast_digest: string }
  | { status: "unsupported"; reason: "profile-or-media-type" }
  | { status: "rejected"; code: string };

const isRecord = (value: unknown): value is RecordValue => !!value && typeof value === "object" && !Array.isArray(value);
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");

/**
 * Candidate formation preflight for a caller-selected v4 source and profile.
 * This does not validate BusinessMeaning acceptance, definition closure,
 * interpretation, claim admission, or runtime behavior.
 */
export function checkFormalClaimSourceBoundary(rootDirectory: string, claim: unknown, selectedProfile: string): FormationResult {
  if (!isRecord(claim) || !isRecord(claim.formal_language_profile_ref))
    return { status: "rejected", code: "PROFILE_REF_SHAPE" };
  if (typeof selectedProfile !== "string" || !/^[A-Za-z][A-Za-z0-9-]*\/[A-Za-z0-9-]+$/.test(selectedProfile))
    return { status: "rejected", code: "PROFILE_SELECTION" };

  let ref: ReturnType<typeof validateExactFormalSourceRef>;
  try {
    ref = validateExactFormalSourceRef(claim.formal_language_profile_ref, "$claim/formal_language_profile_ref");
    const files = loadApplicationEvidenceFiles(rootDirectory, [ref]);
    const bytes = files.get(ref.path);
    if (!bytes) return { status: "rejected", code: "PROFILE_SOURCE_MISSING" };
    let registry: unknown;
    try { registry = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)); }
    catch { return { status: "rejected", code: "PROFILE_SOURCE_JSON" }; }
    if (!isRecord(registry) || !Array.isArray(registry.profiles))
      return { status: "rejected", code: "PROFILE_REGISTRY_SHAPE" };
    const matches = registry.profiles.filter((item: unknown) => isRecord(item)
      && `${item.profile_id}/${item.version}` === selectedProfile);
    if (matches.length !== 1) return { status: "rejected", code: "PROFILE_SELECTION_CARDINALITY" };
    const checked = checkFormalClaimSourceProposition(claim, matches[0]);
    if (checked.status === "unsupported") return checked;
    return { ...checked, selected_profile: selectedProfile, profile_ref_digest: sha(bytes) };
  } catch (error) {
    if (error instanceof CompilationRejected)
      return { status: "rejected", code: error.issues[0]?.code ?? "COMPILATION_REJECTED" };
    if (error instanceof Error && "code" in error && typeof error.code === "string")
      return { status: "rejected", code: "PROFILE_SOURCE_IO" };
    throw error;
  }
}
