import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const forbidden = [
  "/typescript/generator/",
  "/typescript/compiler/",
  "/typescript/adapter/",
  "/development/architecture-realization-compiler/catalogues/",
  "/development/architecture-realization-compiler/fixtures/",
];

export const assertEvaluatorImportBoundary = async (entryPath: string): Promise<readonly string[]> => {
  const visited = new Set<string>();
  const visit = async (path: string): Promise<void> => {
    const absolute = resolve(path);
    if (visited.has(absolute)) return;
    if (forbidden.some((part) => absolute.includes(part))) {
      throw new Error(`ARCH_EVALUATOR_FORBIDDEN_IMPORT:${absolute}`);
    }
    visited.add(absolute);
    const source = await readFile(absolute, "utf8");
    const imports = [...source.matchAll(/\b(?:import|export)\s+(?:type\s+)?(?:[^"']*?\s+from\s+)?["']([^"']+)["']/gu)]
      .map((match) => match[1] as string)
      .filter((specifier) => specifier.startsWith("."));
    for (const specifier of imports) {
      const target = resolve(dirname(absolute), specifier.replace(/\.js$/u, ".ts"));
      await visit(target);
    }
  };
  await visit(entryPath);
  return Object.freeze([...visited].sort());
};
