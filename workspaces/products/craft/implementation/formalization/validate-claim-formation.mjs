#!/usr/bin/env node
// Opt-in v4 source-shape and proposition-formation check. Never admission.
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { assertSupportedSchema, validateSchemaInstance } from "./schema-instance.mjs";

const packageRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(packageRoot, "../../../..");
const schemaPath = resolve(packageRoot, "schemas/formal-claim-source-v4-candidate.schema.json");
const checkerPath = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/core-cli.js");
const ceiling = "V4 JSON shape and selected proposition formation only; no BusinessMeaning acceptance, definition closure, interpretation, admission, TDE, F5, EVF, or runtime guarantee.";
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const result = (status, code, extra = {}) => ({ schema_version: "domainspec-v2.formal-claim-formation-result/v1-candidate", status,
  authority_effect: "none", claim_ceiling: ceiling, ...(code ? { code } : {}), ...extra });

function exactFile(root, ref) {
  if (!object(ref) || Object.keys(ref).sort().join("|") !== "current|path|sha256|size_bytes"
    || ref.current !== true || typeof ref.path !== "string" || !ref.path || isAbsolute(ref.path)
    || typeof ref.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(ref.sha256)
    || !Number.isSafeInteger(ref.size_bytes) || ref.size_bytes < 1) throw new Error("CLAIM_REF_SHAPE");
  const absolute = resolve(root, ref.path);
  const relativePath = relative(root, absolute);
  if (!relativePath || relativePath.startsWith("..") || isAbsolute(relativePath)) throw new Error("CLAIM_REF_PATH");
  if (realpathSync(absolute) !== absolute || !statSync(absolute).isFile()) throw new Error("CLAIM_REF_PATH");
  const bytes = readFileSync(absolute);
  if (bytes.length !== ref.size_bytes || sha(bytes) !== ref.sha256) throw new Error("CLAIM_REF_STALE");
  return bytes;
}

export function checkClaimFormation(request) {
  if (!object(request) || Object.keys(request).sort().join("|") !== "claim_ref|root_directory|schema_version|selected_profile"
    || request.schema_version !== "domainspec-v2.formal-claim-formation-request/v1-candidate"
    || typeof request.root_directory !== "string" || !isAbsolute(request.root_directory)
    || typeof request.selected_profile !== "string") return result("rejected", "REQUEST_SHAPE");
  let claimBytes;
  try { claimBytes = exactFile(request.root_directory, request.claim_ref); }
  catch (error) { return result("rejected", error.message.startsWith("CLAIM_REF_") ? error.message : "CLAIM_SOURCE_IO"); }
  const claimSource = { path: request.claim_ref.path, sha256: sha(claimBytes), size_bytes: claimBytes.length };
  let claim;
  try { claim = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(claimBytes)); }
  catch { return result("rejected", "CLAIM_SOURCE_JSON", { claim_source: claimSource }); }
  let schemaBytes, schema;
  try {
    schemaBytes = readFileSync(schemaPath);
    schema = JSON.parse(schemaBytes);
    assertSupportedSchema(schema);
  } catch { return result("rejected", "SCHEMA_UNAVAILABLE", { claim_source: claimSource }); }
  const schemaRef = { path: relative(repositoryRoot, schemaPath), sha256: sha(schemaBytes), size_bytes: schemaBytes.length };
  let errors;
  try { errors = validateSchemaInstance(claim, schema); }
  catch { return result("rejected", "SCHEMA_EVALUATION", { claim_source: claimSource, schema_ref: schemaRef }); }
  if (errors.length) return result("rejected", "CLAIM_SCHEMA", { claim_source: claimSource, schema_ref: schemaRef, schema_errors: errors.slice(0, 12) });
  let checkerBytes;
  try { checkerBytes = readFileSync(checkerPath); }
  catch { return result("rejected", "CHECKER_UNAVAILABLE", { claim_source: claimSource, schema_ref: schemaRef }); }
  const checkerEntry = { path: relative(repositoryRoot, checkerPath), sha256: sha(checkerBytes), size_bytes: checkerBytes.length };
  const input = { schema_version: "alchlang.formal-claim-formation-request/v1", root_directory: request.root_directory,
    claim_ref: request.claim_ref, selected_profile: request.selected_profile };
  const run = spawnSync(process.execPath, [checkerPath, "check-formal-claim"], {
    input: JSON.stringify(input), encoding: "utf8", timeout: 20000, maxBuffer: 1048576,
  });
  if (run.error || run.signal) return result("rejected", "CHECKER_EXECUTION", { claim_source: claimSource, schema_ref: schemaRef, checker_entry: checkerEntry });
  let checked;
  try { checked = JSON.parse(run.stdout); }
  catch { return result("rejected", "CHECKER_PROTOCOL", { claim_source: claimSource, schema_ref: schemaRef, checker_entry: checkerEntry }); }
  const expectedExit = { checked: 0, rejected: 2, unsupported: 3 }[checked?.status];
  if (!object(checked) || checked.schema_version !== "alchlang.formal-claim-formation-result/v1"
    || checked.authority_effect !== "none" || expectedExit === undefined || run.status !== expectedExit
    || checked.claim_source?.sha256 !== claimSource.sha256 || checked.claim_source?.size_bytes !== claimSource.size_bytes
    || checked.claim_source?.path !== claimSource.path)
    return result("rejected", "CHECKER_PROTOCOL", { claim_source: claimSource, schema_ref: schemaRef, checker_entry: checkerEntry });
  return result(checked.status, checked.status === "rejected" ? checked.code ?? "CHECKER_REJECTED" : undefined,
    { claim_source: claimSource, schema_ref: schemaRef, checker_entry: checkerEntry, formation: checked });
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const chunks = [];
  let size = 0;
  for await (const chunk of process.stdin) {
    size += chunk.length;
    if (size > 1048576) { console.log(JSON.stringify(result("rejected", "REQUEST_SIZE"))); process.exitCode = 2; break; }
    chunks.push(chunk);
  }
  if (!process.exitCode) {
    let request;
    try { request = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(Buffer.concat(chunks))); }
    catch { request = null; }
    const output = process.argv.length === 2 ? checkClaimFormation(request) : result("rejected", "REQUEST_ARGUMENT");
    console.log(JSON.stringify(output));
    process.exitCode = { checked: 0, rejected: 2, unsupported: 3 }[output.status];
  }
}
