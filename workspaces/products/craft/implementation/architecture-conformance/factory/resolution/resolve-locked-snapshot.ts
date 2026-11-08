import { lstat, mkdir, readFile, realpath, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import type { FactoryRunLockV1, LockedFactoryRefV1 } from "../contracts/factory-run-lock-v1.js";
import { fail, json, sha256 } from "../shared/canonical.js";

const copyLockedRef = async (input: Readonly<{
  repositoryRoot: string;
  stagingRoot: string;
  destination: string;
  ref: LockedFactoryRefV1;
}>): Promise<Readonly<{ path: string; sha256: string; byte_length: number }>> => {
  const root = await realpath(input.repositoryRoot);
  const source = resolve(root, input.ref.path);
  const stat = await lstat(source).catch(() => fail("FACTORY_INPUT_MISSING", input.ref.path));
  if (!stat.isFile() || stat.isSymbolicLink()) fail("FACTORY_INPUT_INVALID", input.ref.path);
  const owned = await realpath(source);
  if (!owned.startsWith(`${root}/`)) fail("FACTORY_REQUEST_INVALID", "symlink-escape");
  const bytes = await readFile(owned);
  if (bytes.byteLength !== input.ref.byte_length || sha256(bytes) !== input.ref.sha256) {
    fail("FACTORY_INPUT_TAMPERED", input.ref.path);
  }
  const target = resolve(input.stagingRoot, input.destination);
  if (!target.startsWith(`${input.stagingRoot}/`)) fail("FACTORY_SNAPSHOT_PATH_ESCAPE");
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes, { flag: "wx" });
  return Object.freeze({
    path: input.destination,
    sha256: input.ref.sha256,
    byte_length: input.ref.byte_length,
  });
};

export const resolveLockedSnapshot = async (input: Readonly<{
  repositoryRoot: string;
  stagingRoot: string;
  lock: FactoryRunLockV1;
}>): Promise<Readonly<{
  raw_inputs_by_node: Readonly<Record<string, Readonly<Record<string, string>>>>;
  snapshot_index_sha256: string;
}>> => {
  const entries: Array<Readonly<{ path: string; sha256: string; byte_length: number }>> = [];
  const rawInputsByNode: Record<string, Readonly<Record<string, string>>> = {};
  const copiedComponents = new Set<string>();
  for (const node of input.lock.nodes) {
    const raw: Record<string, string> = {};
    for (const ref of node.inputs) {
      const destination = `snapshot/nodes/${node.node_id}/inputs/${ref.role}.raw`;
      entries.push(await copyLockedRef({ ...input, destination, ref }));
      raw[ref.role] = await readFile(resolve(input.stagingRoot, destination), "utf8");
    }
    rawInputsByNode[node.node_id] = Object.freeze(raw);
    for (const ref of node.components) {
      if (copiedComponents.has(ref.path)) continue;
      const destination = `snapshot/components/${ref.path}`;
      entries.push(await copyLockedRef({ ...input, destination, ref }));
      copiedComponents.add(ref.path);
    }
  }
  const index = Object.freeze({
    schema_version: "FactorySnapshotIndex/v1",
    lock_sha256: input.lock.lock_sha256,
    entries: Object.freeze(entries.sort((left, right) =>
      Buffer.from(left.path).compare(Buffer.from(right.path)))),
    authority_effect: "none",
  });
  const rendered = json(index);
  await writeFile(resolve(input.stagingRoot, "snapshot/snapshot-index.json"), rendered, {
    encoding: "utf8",
    flag: "wx",
  });
  return Object.freeze({
    raw_inputs_by_node: Object.freeze(rawInputsByNode),
    snapshot_index_sha256: sha256(rendered),
  });
};
