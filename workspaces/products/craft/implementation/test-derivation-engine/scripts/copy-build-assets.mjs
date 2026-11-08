import { cpSync, mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceRoot = join(packageRoot, "src");
const emittedRoot = join(packageRoot, "dist", "test-derivation-engine", "src");

function copyJsonAssets(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const source = join(directory, entry.name);
    if (entry.isDirectory()) {
      copyJsonAssets(source);
      continue;
    }
    if (!entry.isFile() || !entry.name.endsWith(".json")) continue;
    const target = join(emittedRoot, source.slice(sourceRoot.length + 1));
    mkdirSync(dirname(target), { recursive: true });
    cpSync(source, target);
  }
}

copyJsonAssets(sourceRoot);
writeFileSync(join(packageRoot, "dist", ".tde-build-owned"), "tde-owned-emitted-build/v1\n", { flag: "wx" });
