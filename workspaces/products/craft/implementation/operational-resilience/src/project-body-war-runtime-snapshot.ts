import { createHash } from "node:crypto";
import { BODY_WAR_RUNTIME_EVIDENCE_LANE, BODY_WAR_RUNTIME_SOURCE_MODE, decodeBodyWarRuntimeSnapshot, type BodyWarRuntimeProjectionFinding, type BodyWarRuntimeProjectionResult } from "../contracts/body-war-runtime-snapshot.js";

const sha256 = (bytes: Uint8Array): string => createHash("sha256").update(bytes).digest("hex");
const freeze = <T>(value: T): T => { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; };

export function projectBodyWarRuntimeSnapshot(snapshotValue: unknown, rawEvidencePack: Uint8Array, projectedAt: string): BodyWarRuntimeProjectionResult {
  const decoded = decodeBodyWarRuntimeSnapshot(snapshotValue);
  const snapshot = decoded.verdict === "pass" ? decoded.value : null;
  const findings: BodyWarRuntimeProjectionFinding[] = decoded.findings.map((finding) => ({...finding}));
  const rawDigest = sha256(rawEvidencePack);
  if (snapshot !== null && rawDigest !== snapshot.raw_evidence_pack_sha256) findings.push({code:"BODY_WAR_RUNTIME_RAW_PACK_SUBSTITUTED",path:"/raw_evidence_pack_sha256",detail:"supplied raw evidence pack does not match the snapshot binding"});
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(projectedAt) || !Number.isFinite(Date.parse(projectedAt))) findings.push({code:"BODY_WAR_RUNTIME_PROJECTED_AT_INVALID",path:"/projected_at",detail:"expected RFC3339 UTC timestamp"});
  const snapshotId = snapshot?.snapshot_id ?? "invalid-snapshot";
  const boundDigest = snapshot?.raw_evidence_pack_sha256 ?? rawDigest;
  const identity = sha256(Buffer.from(`${snapshotId}\0${boundDigest}`, "utf8"));
  const base = {schema_version:"domainspec.orodi.body-war-runtime-projection-result/v1" as const,projector_id:"domainspec.orodi.body-war-runtime-projector" as const,projector_version:"1.0.0-candidate-local" as const,evidence_lane:BODY_WAR_RUNTIME_EVIDENCE_LANE,projection_id:`bw-runtime-projection-${identity.slice(0,16)}`,snapshot_id:snapshotId,raw_evidence_pack_sha256:boundDigest,source_mode:BODY_WAR_RUNTIME_SOURCE_MODE,projected_at:projectedAt,observation_plane:"product" as const,observation_mode:"simulation" as const,runtime_admitted_observation_ids:[] as const,eligible_control_ids:[] as const,eligibility_decision:"replay-only" as const,runtime_admission:"denied" as const,authority_effect:"none" as const};
  if (findings.length > 0) return freeze({...base,verdict:"rejected" as const,observation_id:null,findings:findings.sort((a,b)=>a.path.localeCompare(b.path)||a.code.localeCompare(b.code))});
  return freeze({...base,verdict:"projected" as const,observation_id:`bw-runtime-observation-${identity.slice(0,16)}`,findings:[] as const});
}
