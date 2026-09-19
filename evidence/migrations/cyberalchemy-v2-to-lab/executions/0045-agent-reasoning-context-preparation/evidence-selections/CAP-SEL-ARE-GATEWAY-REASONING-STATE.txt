import {createHash} from "node:crypto";
import {resolve} from "node:path";

import {freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";

function consumerFileStem(consumerId) {
  const readable = consumerId.toLowerCase().replace(/[^a-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || "consumer";
  const identity = createHash("sha256").update(consumerId, "utf8").digest("hex").slice(0, 16);
  return `${readable}-${identity}`;
}

export function deriveGatewayReasoningStateProfile(loadedProfile, consumerId, directoryOverride = null) {
  if (!isRecord(loadedProfile) || !isRecord(loadedProfile.reasoning_state) || !isRecord(loadedProfile.gateway?.reasoning_state)) {
    throw new TypeError("A loaded profile with gateway reasoning-state configuration is required.");
  }
  if (!nonEmptyString(consumerId)) throw new TypeError("A non-empty gateway consumer identity is required.");
  const gatewayState = loadedProfile.gateway.reasoning_state;
  if (gatewayState.mode === "process-memory") return freezeResult({...loadedProfile.reasoning_state, storage_mode: "process-memory", log_path: null, single_writer: false});
  const directory = nonEmptyString(directoryOverride) ? resolve(directoryOverride) : gatewayState.directory;
  if (!nonEmptyString(directory)) throw new TypeError("A file-backed gateway reasoning-state directory is required.");
  const stem = consumerFileStem(consumerId.trim());
  return freezeResult({
    ...loadedProfile.reasoning_state,
    ledger_id: `${loadedProfile.reasoning_state.ledger_id}:${stem}`,
    storage_mode: "append-only-file-fsync",
    log_path: resolve(directory, `${stem}.jsonl`),
    single_writer: true,
  });
}
