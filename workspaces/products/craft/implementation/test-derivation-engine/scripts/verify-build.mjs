import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const emitted = join(packageRoot, "dist");
const engine = await import(pathToFileURL(join(emitted, "test-derivation-engine/src/index.js")).href);
if (typeof engine.derive !== "function") throw new Error("emitted TDE entry is not loadable");

const minted = await import(pathToFileURL(join(emitted, "tools/minted-project/views.js")).href);
const result = minted.verifyMintedProjectBuild(packageRoot, {
  graphBytes: "{}", sourceManifestBytes: "{}", markdownViewBytes: "{}", buildReceiptBytes: "null",
});
if (result.status !== "fail" || !result.codes.includes("GRAPH_INVALID") ||
    !result.codes.includes("SOURCE_MANIFEST_INVALID") ||
    !result.codes.includes("MARKDOWN_VIEW_INVALID") ||
    !result.codes.includes("BUILD_RECEIPT_INVALID"))
  throw new Error("emitted minted verifier did not validate canonical local schemas");
