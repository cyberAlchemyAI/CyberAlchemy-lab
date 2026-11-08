import { lstat, readFile, readdir, realpath } from "node:fs/promises";
import { relative, resolve } from "node:path";

import { canonicalJson, fail, sha256 } from "../shared/canonical.js";

type RunIndex = Readonly<{
  schema_version: "FactoryRunIndex/v1";
  entries: readonly Readonly<{ path: string; sha256: string; byte_length: number }>[];
  authority_effect: "none";
}>;

const walk = async (root: string, current = root): Promise<string[]> => {
  const paths: string[] = [];
  for (const name of await readdir(current)) {
    const path = resolve(current, name);
    const stat = await lstat(path);
    if (stat.isSymbolicLink()) fail("FACTORY_RUN_SYMLINK_FORBIDDEN");
    if (stat.isDirectory()) paths.push(...await walk(root, path));
    else if (stat.isFile()) paths.push(relative(root, path).replaceAll("\\", "/"));
    else fail("FACTORY_RUN_FILE_TYPE_INVALID");
  }
  return paths.sort((left, right) => Buffer.from(left).compare(Buffer.from(right)));
};

export const verifyFactoryRunRoot = async (runPath: string): Promise<Readonly<{
  result: "pass";
  semantic_receipt_sha256: string;
  lock_sha256: string;
  run_id: string;
  authority_effect: "none";
}>> => {
  const root = await realpath(runPath).catch(() => fail("FACTORY_RUN_MISSING"));
  const index = JSON.parse(await readFile(resolve(root, "run-index.json"), "utf8")) as RunIndex;
  if (index.schema_version !== "FactoryRunIndex/v1" || index.authority_effect !== "none") {
    fail("FACTORY_RUN_INDEX_INVALID");
  }
  const expected = ["run-index.json", ...index.entries.map(({ path }) => path)]
    .sort((left, right) => Buffer.from(left).compare(Buffer.from(right)));
  if (JSON.stringify(await walk(root)) !== JSON.stringify(expected)) {
    fail("FACTORY_RUN_UNINDEXED_FILE");
  }
  for (const entry of index.entries) {
    const path = resolve(root, entry.path);
    if (!path.startsWith(`${root}/`)) fail("FACTORY_RUN_INDEX_INVALID");
    const bytes = await readFile(path).catch(() => fail("FACTORY_RUN_BYTES_MISSING", entry.path));
    if (bytes.byteLength !== entry.byte_length || sha256(bytes) !== entry.sha256) {
      fail("FACTORY_RUN_BYTES_TAMPERED", entry.path);
    }
  }
  const terminal = JSON.parse(await readFile(resolve(root, "terminal.json"), "utf8")) as Record<string, unknown>;
  const semantic = JSON.parse(await readFile(resolve(root, "semantic-receipt.json"), "utf8")) as Record<string, unknown>;
  const observedSemantic = sha256(canonicalJson(semantic));
  if (terminal.result !== "pass" || terminal.semantic_receipt_sha256 !== observedSemantic ||
      semantic.result !== "pass" || semantic.authority_effect !== "none") {
    fail("FACTORY_SEMANTIC_RECEIPT_INVALID");
  }
  return Object.freeze({
    result: "pass",
    semantic_receipt_sha256: observedSemantic,
    lock_sha256: String(semantic.lock_sha256),
    run_id: String(semantic.run_id),
    authority_effect: "none",
  });
};
