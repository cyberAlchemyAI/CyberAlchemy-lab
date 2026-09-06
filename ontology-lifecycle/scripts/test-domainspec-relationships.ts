#!/usr/bin/env -S node --import tsx
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  compileMintedProject,
  MintedProjectCompilerError,
  type MintedProjectCompilerErrorCode,
} from "../../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/compiler.ts";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(scriptDir, "..");
const projectRoot = resolve(packageRoot, "domainspec");
const profilePath = resolve(projectRoot, "development-profile.json");
const options = {
  developmentProfileRegistry: {
    path: profilePath,
    handle: "ontology-lifecycle-development-explicit-v0.1",
  },
};
const reconstructorPath = "specs/ontology-lifecycle/nodes/reconstruct-governed-ontology-state.json";

function readJson(path: string): Record<string, any> {
  return JSON.parse(readFileSync(path, "utf8")) as Record<string, any>;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function expectCode(
  label: string,
  expected: MintedProjectCompilerErrorCode,
  mutate: (root: string) => void,
): { label: string; result: "PASS"; observed_code: MintedProjectCompilerErrorCode } {
  const parent = mkdtempSync(join(tmpdir(), "cal-domainspec-negative-"));
  const project = join(parent, "project");
  cpSync(projectRoot, project, { recursive: true });
  try {
    mutate(project);
    try {
      compileMintedProject(project, options);
    } catch (error) {
      if (error instanceof MintedProjectCompilerError && error.code === expected) {
        return { label, result: "PASS", observed_code: error.code };
      }
      throw error;
    }
    throw new Error(`${label}: compiler unexpectedly accepted the negative fixture`);
  } finally {
    rmSync(parent, { recursive: true, force: true });
  }
}

const positive = compileMintedProject(projectRoot, options);
const results = [
  expectCode("reconstructs-from rejects an Event target", "EDGE_ENDPOINT_KIND_MISMATCH", (root) => {
    const path = join(root, reconstructorPath);
    const node = readJson(path);
    node.connections[0].to = "ontology-lifecycle.SemanticEvent";
    writeJson(path, node);
  }),
  expectCode("unknown relationship fails closed", "EDGE_TYPE_UNKNOWN", (root) => {
    const path = join(root, reconstructorPath);
    const node = readJson(path);
    node.connections[0].type = "reconstructs-from-unknown";
    writeJson(path, node);
  }),
];

process.stdout.write(`${JSON.stringify({
  status: "PASS",
  positive: { nodes: positive.graph.nodes.length, edges: positive.graph.edges.length },
  negative: results,
  authority_effect: "none",
}, null, 2)}\n`);
