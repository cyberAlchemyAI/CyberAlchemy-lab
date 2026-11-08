import fs from "node:fs";
import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { loadCompiledProjectGraph, validateCompiledProjectGraphObligations, type CompiledProjectGraph } from "../input/project-model.js";
import { CLI_VERSION } from "../version.js";

export interface CompiledProjectCertificateV1 {
  readonly schema_version: "domainspec.compiled-project-certificate/v1";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly graph_sha256: string;
  readonly node_count: number;
  readonly edge_count: number;
  readonly backend_type_ids: readonly string[];
  readonly backend_relationship_ids: readonly string[];
  readonly obligation_applicability: CompiledProjectGraph["obligation_applicability"];
  readonly obligation_witnesses: CompiledProjectGraph["obligation_witnesses"];
  readonly compiler: Readonly<{ readonly package: "@domainspec-v2/cli"; readonly version: string; readonly node: string }>;
  readonly authority_effect: "none";
  readonly certificate_sha256: string;
}

export class CompilationCertificateError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "CompilationCertificateError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new CompilationCertificateError(code, pointer, message); }

export function createCompiledSemanticGraph(graph: CompiledProjectGraph): Omit<CompiledProjectGraph, "project_root"> {
  return Object.freeze({
    schema_version: graph.schema_version,
    project_id: graph.project_id,
    source_manifest: graph.source_manifest,
    nodes: graph.nodes,
    relationships: graph.relationships,
    obligation_witnesses: graph.obligation_witnesses,
    obligation_applicability: graph.obligation_applicability,
    authority_effect: graph.authority_effect,
  });
}

export function createCompiledProjectCertificate(graph: CompiledProjectGraph): CompiledProjectCertificateV1 {
  validateCompiledProjectGraphObligations(graph);
  const body = {
    schema_version: "domainspec.compiled-project-certificate/v1" as const,
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    graph_sha256: sha256(canonicalJson(createCompiledSemanticGraph(graph))),
    node_count: graph.nodes.length,
    edge_count: graph.relationships.length,
    backend_type_ids: Object.freeze([...new Set(graph.nodes.map(({ meta_type_id }) => meta_type_id))].sort()),
    backend_relationship_ids: Object.freeze([...new Set(graph.relationships.map(({ relationship }) => relationship))].sort()),
    obligation_applicability: graph.obligation_applicability,
    obligation_witnesses: graph.obligation_witnesses,
    compiler: Object.freeze({ package: "@domainspec-v2/cli" as const, version: CLI_VERSION, node: process.version }),
    authority_effect: "none" as const,
  };
  return Object.freeze({ ...body, certificate_sha256: sha256(canonicalJson(body)) });
}

export function compileProject(sourceRoot: string): Readonly<{ readonly graph: CompiledProjectGraph; readonly certificate: CompiledProjectCertificateV1 }> {
  const graph = loadCompiledProjectGraph(sourceRoot);
  return Object.freeze({ graph, certificate: createCompiledProjectCertificate(graph) });
}

export function validateCompiledProjectCertificate(graph: CompiledProjectGraph, certificate: CompiledProjectCertificateV1): CompiledProjectCertificateV1 {
  const expected = createCompiledProjectCertificate(graph);
  if (canonicalJson(expected) !== canonicalJson(certificate)) fail("MTCLI_COMPILED_CERTIFICATE", "/certificate", "compiled-project certificate is stale, omitted, or changed");
  return certificate;
}

export function materializeCompiledProjectCertificate(sourceRoot: string, targetPath: string): CompiledProjectCertificateV1 {
  if (!path.isAbsolute(targetPath) || path.resolve(targetPath) !== targetPath) fail("MTCLI_COMPILED_CERTIFICATE_PATH", "/target", "certificate target must be a normalized absolute path");
  if (fs.existsSync(targetPath)) fail("MTCLI_COMPILED_CERTIFICATE_EXISTS", "/target", "certificate target already exists");
  const certificate = compileProject(sourceRoot).certificate;
  const parent = path.dirname(targetPath);
  let parentStats: fs.Stats;
  try { parentStats = fs.lstatSync(parent); } catch { fail("MTCLI_COMPILED_CERTIFICATE_PARENT", "/target", "certificate target parent does not exist"); }
  if (!parentStats.isDirectory() || parentStats.isSymbolicLink() || fs.realpathSync(parent) !== parent) fail("MTCLI_COMPILED_CERTIFICATE_PARENT", "/target", "certificate target parent must be a real directory");
  const temporary = path.join(parent, `.${path.basename(targetPath)}.${process.pid}.${Date.now()}.tmp`);
  try {
    fs.writeFileSync(temporary, `${canonicalJson(certificate)}\n`, { flag: "wx", mode: 0o644 });
    fs.linkSync(temporary, targetPath);
    fs.unlinkSync(temporary);
  } catch (error) {
    fs.rmSync(temporary, { force: true });
    if ((error as NodeJS.ErrnoException).code === "EEXIST") fail("MTCLI_COMPILED_CERTIFICATE_EXISTS", "/target", "certificate target appeared during publication");
    throw error;
  }
  return certificate;
}
