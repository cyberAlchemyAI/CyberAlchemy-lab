import { lstatSync, readFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const dist = join(packageRoot, "dist");
let stat;
try { stat = lstatSync(dist); }
catch (error) {
  if (error.code === "ENOENT") process.exit(0);
  throw error;
}
if (!stat.isDirectory() || stat.isSymbolicLink() ||
    readFileSync(join(dist, ".tde-build-owned"), "utf8") !== "tde-owned-emitted-build/v1\n")
  throw new Error("refusing to replace an unowned TDE dist directory");
rmSync(dist, { recursive: true });
