import {createHash} from "node:crypto";
import {closeSync, existsSync, mkdirSync, openSync, readFileSync, renameSync, rmSync, writeFileSync, fsyncSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {canonicalJson, canonicalizeJson, sha256HexText} from "../../intent-route-resolver/index.mjs";

function digest(value) {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex");
}

export function createServingVersionStore({path} = {}) {
  if (!path) throw new TypeError("Serving-version store path is required");
  const storePath = resolve(path);
  const lockPath = `${storePath}.lock`;
  mkdirSync(dirname(storePath), {recursive: true});

  function read() {
    if (!existsSync(storePath)) return null;
    const value = JSON.parse(readFileSync(storePath, "utf8"));
    if (value.schema_version !== "are.serving-version-pointer/v1" || value.pointer_digest !== digest({schema_version: value.schema_version, version_ref: value.version_ref, predecessor_ref: value.predecessor_ref, decision_ref: value.decision_ref})) throw new Error("Serving-version pointer is malformed or corrupt");
    return Object.freeze(value);
  }

  function write({version_ref, predecessor_ref = null, decision_ref = null}) {
    let lock;
    try { lock = openSync(lockPath, "wx", 0o600); } catch (error) {
      if (error?.code === "EEXIST") return {ok: false, disposition: "busy", reason_codes: ["evolution.serving-version-writer-active"], authority_effect: "none"};
      throw error;
    }
    const material = {schema_version: "are.serving-version-pointer/v1", version_ref, predecessor_ref, decision_ref};
    const pointer = {...material, pointer_digest: digest(material)};
    const temporary = `${storePath}.tmp-${process.pid}`;
    try {
      const descriptor = openSync(temporary, "wx", 0o600);
      writeFileSync(descriptor, `${JSON.stringify(pointer)}\n`, "utf8");
      fsyncSync(descriptor);
      closeSync(descriptor);
      renameSync(temporary, storePath);
      return {ok: true, disposition: "written", value: Object.freeze(pointer), authority_effect: "none"};
    } finally {
      rmSync(temporary, {force: true});
      closeSync(lock);
      rmSync(lockPath, {force: true});
    }
  }

  return Object.freeze({read, write, path: storePath});
}

export async function applyUpgradeDecision({decision, store, canary} = {}) {
  if (!decision || decision.schema_version !== "are.upgrade-decision/v1" || decision.authority_effect !== "none") throw new TypeError("A non-authorizing upgrade decision is required");
  const {record_id: _recordId, record_digest: _recordDigest, ...decisionMaterial} = decision;
  const expectedDecisionDigest = sha256HexText(canonicalJson(canonicalizeJson(decisionMaterial)));
  if (decision.record_digest !== expectedDecisionDigest || decision.record_id !== `upgrade-decision:${expectedDecisionDigest}`) throw new TypeError("Upgrade decision digest is invalid");
  if (!store || typeof store.read !== "function" || typeof store.write !== "function") throw new TypeError("A serving-version store is required");
  if (decision.disposition !== "activate-candidate") return Object.freeze({ok: true, disposition: "no-change", version_ref: store.read()?.version_ref ?? null, canary_calls: 0, authority_effect: "none"});
  if (typeof canary !== "function") return Object.freeze({ok: false, disposition: "blocked", reason_codes: ["evolution.activation-canary-required"], canary_calls: 0, authority_effect: "none"});
  const current = store.read();
  if (!current || current.version_ref !== decision.predecessor_ref) return Object.freeze({ok: false, disposition: "blocked", reason_codes: ["evolution.serving-predecessor-mismatch"], canary_calls: 0, authority_effect: "none"});
  const activated = store.write({version_ref: decision.candidate_version_ref, predecessor_ref: current.version_ref, decision_ref: decision.record_id});
  if (!activated.ok) return activated;
  let canaryResult;
  try { canaryResult = await canary({candidate_version_ref: decision.candidate_version_ref, predecessor_ref: current.version_ref}); }
  catch (error) { canaryResult = {ok: false, reason: error.message}; }
  if (canaryResult?.ok === true) return Object.freeze({ok: true, disposition: "activated", version_ref: decision.candidate_version_ref, canary_calls: 1, authority_effect: "none"});
  const rollback = store.write({version_ref: current.version_ref, predecessor_ref: decision.candidate_version_ref, decision_ref: decision.record_id});
  return Object.freeze({ok: false, disposition: rollback.ok ? "rolled-back" : "rollback-failed", version_ref: rollback.ok ? current.version_ref : decision.candidate_version_ref, reason_codes: ["evolution.activation-canary-failed"], canary_calls: 1, authority_effect: "none"});
}
