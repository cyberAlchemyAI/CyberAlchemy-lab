import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync, realpathSync } from "node:fs";
import path from "node:path";
import { CompilationRejected } from "./model.js";
import { resolveExactFormalSource, validateExactFormalSourceRef } from "./formal-claim-lowering.js";

const fail = (message: string): never => {
  throw new CompilationRejected([{ code: "APPLICATION_EVIDENCE_FILE", path: "$evidence", message }]);
};

/** Read only explicitly selected exact evidence. No discovery, writes or acceptance. */
export function loadApplicationEvidenceFiles(rootDirectory: string, references: readonly unknown[]): ReadonlyMap<string, Buffer> {
  // Validate the entire selection before opening any selected file.
  const refs = references.map((ref, i) => validateExactFormalSourceRef(ref, `$evidence/${i}`));
  const selected = new Map<string, typeof refs[number]>();
  for (const ref of refs) {
    const previous = selected.get(ref.path);
    if (previous && (previous.sha256 !== ref.sha256 || previous.size_bytes !== ref.size_bytes)) fail(`conflicting reference: ${ref.path}`);
    selected.set(ref.path, ref);
  }
  const root = realpathSync(rootDirectory);
  if (!lstatSync(root).isDirectory()) fail("application root must be a directory");
  const sources = new Map<string, Buffer>();
  for (const ref of selected.values()) {
    let target = root;
    const segments = ref.path.split("/");
    for (let i = 0; i < segments.length; i++) {
      target = path.join(target, segments[i]!);
      const stat = lstatSync(target);
      if (stat.isSymbolicLink()) fail(`symlink: ${ref.path}`);
      if (i < segments.length - 1 ? !stat.isDirectory() : !stat.isFile()) fail(`not a regular evidence path: ${ref.path}`);
    }
    if (realpathSync(target) !== target) fail(`changed evidence path: ${ref.path}`);
    const fd = openSync(target, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
    try {
      const before = fstatSync(fd);
      if (!before.isFile() || before.size !== ref.size_bytes) fail(`evidence size/type changed: ${ref.path}`);
      const bytes = readFileSync(fd);
      const after = fstatSync(fd);
      if (before.size !== after.size || before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs) fail(`evidence changed while reading: ${ref.path}`);
      resolveExactFormalSource(ref, new Map([[ref.path, bytes]]), `$evidence/${ref.path}`);
      sources.set(ref.path, bytes);
    } finally { closeSync(fd); }
  }
  return sources;
}
