import { createHash } from "node:crypto";
import { lstat, readFile, readdir } from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../..");
const receiptRoot = resolve(repositoryRoot,
  "projects/domainspec-v2/development/meta-type-realization-factory/receipts");
const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const canonical = (value) => JSON.stringify(
  Array.isArray(value) ? value.map((item) => JSON.parse(canonical(item))) :
    value !== null && typeof value === "object"
      ? Object.fromEntries(Object.entries(value).sort(([left], [right]) =>
          Buffer.from(left).compare(Buffer.from(right))).map(([key, child]) =>
          [key, JSON.parse(canonical(child))]))
      : value,
);
const expectedRed = new Set([1, 9, 17]);
const requestedCount = Number(process.argv.find((item) =>
  item.startsWith("--expected-count="))?.split("=")[1] ?? "29");
const fail = (code) => { throw new Error(code); };

const walk = async (root, current = root) => {
  const files = [];
  for (const name of await readdir(current)) {
    const path = resolve(current, name);
    const stat = await lstat(path);
    if (stat.isDirectory()) files.push(...await walk(root, path));
    else if (stat.isFile()) files.push(relative(root, path).replaceAll("\\", "/"));
  }
  return files.sort();
};

const validateRawRun = async (path) => {
  const indexPath = resolve(repositoryRoot, path);
  const runPath = dirname(indexPath);
  const index = JSON.parse(await readFile(indexPath, "utf8"));
  const expected = new Set(["raw-index.json"]);
  for (const entry of index.entries ?? []) {
    expected.add(entry.path);
    const bytes = await readFile(resolve(runPath, entry.path));
    if (bytes.byteLength !== entry.byte_length || sha256(bytes) !== entry.sha256) {
      fail("FACTORY_FINAL_RAW_INDEX_TAMPERED");
    }
  }
  const observed = await walk(runPath);
  if (JSON.stringify(observed) !== JSON.stringify([...expected].sort())) {
    fail("FACTORY_FINAL_RAW_INDEX_UNREACHABLE");
  }
};

const validateReproducibleRun = async (runPath) => {
  const index = JSON.parse(await readFile(resolve(runPath, "run-index.json"), "utf8"));
  const expected = new Set(["run-index.json"]);
  for (const entry of index.entries ?? []) {
    expected.add(entry.path);
    const bytes = await readFile(resolve(runPath, entry.path));
    if (bytes.byteLength !== entry.byte_length || sha256(bytes) !== entry.sha256) {
      fail("FACTORY_REPRODUCTION_RUN_TAMPERED");
    }
  }
  if (JSON.stringify(await walk(runPath)) !== JSON.stringify([...expected].sort())) {
    fail("FACTORY_REPRODUCTION_RUN_UNINDEXED");
  }
  const [semantic, terminal, lock] = await Promise.all([
    readFile(resolve(runPath, "semantic-receipt.json"), "utf8").then(JSON.parse),
    readFile(resolve(runPath, "terminal.json"), "utf8").then(JSON.parse),
    readFile(resolve(runPath, "lock.json"), "utf8").then(JSON.parse),
  ]);
  const semanticSha256 = sha256(canonical(semantic));
  const lockBody = Object.fromEntries(Object.entries(lock).filter(([key]) =>
    key !== "lock_sha256"));
  if (terminal.result !== "pass" || terminal.semantic_receipt_sha256 !== semanticSha256 ||
      semantic.lock_sha256 !== lock.lock_sha256 ||
      sha256(canonical(lockBody)) !== lock.lock_sha256) {
    fail("FACTORY_REPRODUCTION_RUN_RECEIPT_INVALID");
  }
  return { semanticSha256, lock };
};

const loadReproductionBridge = async () => {
  const finalRoot = resolve(repositoryRoot,
    "projects/domainspec-v2/development/meta-type-factory-reproducibility/runs/final");
  const receipt = JSON.parse(await readFile(resolve(finalRoot,
    "reproduction-receipt.json"), "utf8"));
  if (receipt.result !== "pass" || receipt.authority_effect !== "none" ||
      !Array.isArray(receipt.runs) || receipt.runs.length !== 2) {
    fail("FACTORY_REPRODUCTION_RECEIPT_INVALID");
  }
  const runs = await Promise.all(receipt.runs.map(({ path }) =>
    validateReproducibleRun(resolve(finalRoot, path))));
  if (runs[0].semanticSha256 !== runs[1].semanticSha256 ||
      runs[0].semanticSha256 !== receipt.semantic_receipt_sha256 ||
      runs[0].lock.lock_sha256 !== runs[1].lock.lock_sha256) {
    fail("FACTORY_REPRODUCTION_SEMANTIC_DIGEST_MISMATCH");
  }
  const currentComponents = new Map();
  for (const node of runs[0].lock.nodes ?? []) {
    for (const component of node.components ?? []) {
      currentComponents.set(component.path, component.sha256);
    }
  }
  return { receipt, currentComponents };
};

const execute = async () => {
  if (!Number.isInteger(requestedCount) || requestedCount < 1 || requestedCount > 29) {
    fail("FACTORY_FINAL_RECEIPT_COUNT_INVALID");
  }
  const receipts = [];
  for (let number = 1; number <= requestedCount; number += 1) {
    const id = `MTF-${String(number).padStart(3, "0")}`;
    const name = `${id}${expectedRed.has(number) ? ".expected-red" : ""}.json`;
    const value = JSON.parse(await readFile(resolve(receiptRoot, name), "utf8"));
    if (value.swu_id !== id || value.authority_effect !== "none" ||
        !String(value.state).includes("complete")) {
      fail("FACTORY_FINAL_RECEIPT_INVALID");
    }
    for (const dependency of value.dependencies ?? []) {
      const dependencyNumber = Number(String(dependency).split("-")[1]);
      if (!Number.isInteger(dependencyNumber) || dependencyNumber >= number) {
        fail("FACTORY_FINAL_DEPENDENCY_INVALID");
      }
    }
    receipts.push({ number, value, historical: expectedRed.has(number) });
  }
  const lastClaims = new Map();
  for (const receipt of receipts) {
    for (const entry of [...(receipt.value.inputs ?? []), ...(receipt.value.outputs ?? [])]) {
      if (typeof entry.path === "string" && typeof entry.sha256 === "string") {
        lastClaims.set(entry.path, { ...entry, historical: receipt.historical });
      }
    }
  }
  let currentPaths = 0;
  let historicalOnly = 0;
  let supersededCurrentClaims = 0;
  const reproduction = await loadReproductionBridge();
  for (const [path, claim] of lastClaims) {
    let bytes;
    try {
      bytes = await readFile(resolve(repositoryRoot, path));
    } catch {
      if (claim.historical) { historicalOnly += 1; continue; }
      fail("FACTORY_FINAL_REFERENCED_OUTPUT_MISSING");
    }
    if (sha256(bytes) !== claim.sha256) {
      if (claim.historical) { historicalOnly += 1; continue; }
      if (reproduction.currentComponents.get(path) === sha256(bytes)) {
        supersededCurrentClaims += 1;
        continue;
      }
      fail("FACTORY_FINAL_REFERENCED_OUTPUT_STALE");
    }
    currentPaths += 1;
  }
  await validateRawRun(
    "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-021/typescript-rule-v1/raw-index.json",
  );
  await validateRawRun(
    "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-027/rule-operation-composition-v1/raw-index.json",
  );
  const matrix = JSON.parse(await readFile(resolve(repositoryRoot,
    "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-029/readiness-matrix.json"), "utf8"));
  if (matrix.meta_types?.length !== 25 || new Set(matrix.meta_types.map(
    ({ meta_type_id: id }) => id)).size !== 25 || matrix.counts?.total !== 25 ||
      matrix.authority_effect !== "none" || matrix.status !== "non-authorizing-read-model") {
    fail("FACTORY_FINAL_READINESS_ACCOUNTING_INVALID");
  }
  return Object.freeze({
    schema_version: "MetaTypeFactoryReceiptValidation/v1",
    result: "pass",
    receipts_joined: receipts.length,
    current_output_claims_verified: currentPaths,
    historical_expected_red_claims_not_live: historicalOnly,
    superseded_current_claims_verified_by_reproduction: supersededCurrentClaims,
    reproduction_semantic_receipt_sha256: reproduction.receipt.semantic_receipt_sha256,
    reproduction_runs_verified: 2,
    raw_runs_verified: 2,
    meta_type_ids_accounted: 25,
    authority_effect: "none",
  });
};

execute().then((result) => process.stdout.write(`${JSON.stringify(result)}\n`))
  .catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
