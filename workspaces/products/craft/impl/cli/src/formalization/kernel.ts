import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { sha256 } from "./refinement.js";

export const FORMALIZATION_LEAN_MODULE_FILENAMES = Object.freeze([
  "DomainSpecMetaTypeKernel.lean",
  "DomainSpecMetaTypeCompilerRefinement.lean",
  "DomainSpecMetaTypeTypeScriptProjectionRefinement.lean",
] as const);

export type FormalizationLeanModuleFilename = typeof FORMALIZATION_LEAN_MODULE_FILENAMES[number];

export type FormalizationLeanModuleSources = Readonly<Record<FormalizationLeanModuleFilename, string>>;

export interface FormalizationLeanModuleEntry {
  readonly filename: FormalizationLeanModuleFilename;
  readonly source: string;
  readonly sha256: string;
}

export interface FormalizationLeanModuleSet {
  readonly schema_version: "domainspec.formalization-lean-module-set/v1-candidate";
  readonly sha256: string;
  readonly modules: readonly FormalizationLeanModuleEntry[];
}

const leanRoot = fileURLToPath(new URL("../../lean/", import.meta.url));

export function formalizationLeanModuleSources(): FormalizationLeanModuleSources {
  return Object.freeze(Object.fromEntries(
    FORMALIZATION_LEAN_MODULE_FILENAMES.map((filename) => [filename, fs.readFileSync(path.join(leanRoot, filename), "utf8")]),
  ) as Record<FormalizationLeanModuleFilename, string>);
}

export function createFormalizationLeanModuleSet(sources: FormalizationLeanModuleSources): FormalizationLeanModuleSet {
  const modules = Object.freeze(FORMALIZATION_LEAN_MODULE_FILENAMES.map((filename) => Object.freeze({
    filename,
    source: sources[filename],
    sha256: sha256(sources[filename]),
  })));
  return Object.freeze({
    schema_version: "domainspec.formalization-lean-module-set/v1-candidate",
    sha256: sha256(JSON.stringify(modules.map(({ filename, source }) => ({ filename, source })))),
    modules,
  });
}

export function formalizationLeanModuleSet(): FormalizationLeanModuleSet {
  return createFormalizationLeanModuleSet(formalizationLeanModuleSources());
}
