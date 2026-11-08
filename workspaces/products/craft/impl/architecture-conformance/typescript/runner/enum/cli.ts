import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import {
  TRUST_ARTIFACT_PATHS,
  buildTrustArtifacts,
  loadStoredTrustArtifacts,
  renderTrustArtifact,
  verifyTrustArtifacts,
} from "./index.js";

const [mode = "verify", rootArgument = "."] = process.argv.slice(2);
const root = resolve(rootArgument);

if (mode === "materialize") {
  const artifacts = await buildTrustArtifacts(root);
  const diagnostics = verifyTrustArtifacts(artifacts);
  if (diagnostics.length > 0) throw new Error(diagnostics.join(","));
  for (const [key, path] of Object.entries(TRUST_ARTIFACT_PATHS)) {
    const target = resolve(root, path);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, renderTrustArtifact(artifacts[key as keyof typeof artifacts]), "utf8");
  }
  process.stdout.write(`${JSON.stringify({ result: "pass", materialized: Object.keys(TRUST_ARTIFACT_PATHS).length })}\n`);
} else if (mode === "verify") {
  const [first, second, stored] = await Promise.all([
    buildTrustArtifacts(root),
    buildTrustArtifacts(root),
    loadStoredTrustArtifacts(root),
  ]);
  const diagnostics = [
    ...verifyTrustArtifacts(first),
    ...verifyTrustArtifacts(stored),
  ];
  for (const key of Object.keys(TRUST_ARTIFACT_PATHS) as Array<keyof typeof first>) {
    if (renderTrustArtifact(first[key]) !== renderTrustArtifact(second[key])) diagnostics.push(`APE_TS_REPLAY_NONDETERMINISTIC:${key}`);
    if (renderTrustArtifact(first[key]) !== renderTrustArtifact(stored[key])) diagnostics.push(`APE_TS_STORED_ARTIFACT_DRIFT:${key}`);
  }
  if (diagnostics.length > 0) throw new Error([...new Set(diagnostics)].sort().join(","));
  process.stdout.write(`${JSON.stringify({ result: "pass", artifacts: Object.keys(TRUST_ARTIFACT_PATHS).length, replay: "byte-identical", authority_effect: "none" })}\n`);
} else {
  throw new Error(`unsupported mode: ${mode}`);
}
