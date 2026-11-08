import { lstat, readFile, realpath } from "node:fs/promises";
import { dirname, extname, relative, resolve } from "node:path";

import ts from "typescript";

import { fail, safeRelativePath } from "../shared/canonical.js";

const EXECUTABLE_EXTENSIONS = new Set([
  ".ts",
  ".tsx",
  ".mts",
  ".cts",
  ".js",
  ".jsx",
  ".mjs",
  ".cjs",
]);

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const within = (root: string, target: string): boolean =>
  target.startsWith(`${root}/`);

const scriptKind = (path: string): ts.ScriptKind => {
  switch (extname(path)) {
    case ".ts": return ts.ScriptKind.TS;
    case ".tsx": return ts.ScriptKind.TSX;
    case ".jsx": return ts.ScriptKind.JSX;
    case ".js":
    case ".mjs":
    case ".cjs": return ts.ScriptKind.JS;
    case ".mts": return ts.ScriptKind.TS;
    case ".cts": return ts.ScriptKind.TS;
    default: return ts.ScriptKind.Unknown;
  }
};

const literalText = (value: ts.Expression): string | undefined =>
  ts.isStringLiteral(value) || ts.isNoSubstitutionTemplateLiteral(value)
    ? value.text
    : undefined;

const hasIdentifier = (node: ts.Node, name: string): boolean => {
  let found = false;
  const visit = (child: ts.Node): void => {
    if (found) return;
    if (ts.isIdentifier(child) && child.text === name) {
      found = true;
      return;
    }
    ts.forEachChild(child, visit);
  };
  visit(node);
  return found;
};

const explicitNonRepositoryDynamicLoad = (value: ts.Expression): boolean => {
  if (ts.isTemplateExpression(value) && value.head.text.startsWith("data:")) return true;
  const literal = literalText(value);
  if (literal?.startsWith("data:") === true) return true;
  return hasIdentifier(value, "pathToFileURL");
};

const runtimeImport = (node: ts.ImportDeclaration): boolean => {
  const clause = node.importClause;
  if (clause === undefined) return true;
  if (clause.isTypeOnly) return false;
  if (clause.name !== undefined) return true;
  const bindings = clause.namedBindings;
  if (bindings === undefined || ts.isNamespaceImport(bindings)) return true;
  return bindings.elements.some((element) => !element.isTypeOnly);
};

const runtimeExport = (node: ts.ExportDeclaration): boolean => {
  if (node.isTypeOnly) return false;
  if (node.exportClause === undefined || ts.isNamespaceExport(node.exportClause)) return true;
  return node.exportClause.elements.some((element) => !element.isTypeOnly);
};

const relativeSpecifier = (value: string): boolean =>
  value.startsWith("./") || value.startsWith("../");

const extractRuntimeSpecifiers = (
  path: string,
  source: string,
): readonly string[] => {
  const file = ts.createSourceFile(
    path,
    source,
    ts.ScriptTarget.ESNext,
    true,
    scriptKind(path),
  );
  const specifiers: string[] = [];
  const includeLiteral = (value: ts.Expression): void => {
    const literal = literalText(value);
    if (literal !== undefined) {
      if (relativeSpecifier(literal)) specifiers.push(literal);
      else if (literal.startsWith("/") || literal.startsWith("file:")) {
        fail("FACTORY_COMPONENT_PATH_ESCAPE", `${path}->${literal}`);
      }
      return;
    }
    if (!explicitNonRepositoryDynamicLoad(value)) {
      fail("FACTORY_COMPONENT_DYNAMIC_IMPORT_UNSUPPORTED", path);
    }
  };
  const visit = (node: ts.Node): void => {
    if (ts.isImportDeclaration(node) && runtimeImport(node) &&
        ts.isStringLiteral(node.moduleSpecifier)) {
      includeLiteral(node.moduleSpecifier);
    } else if (ts.isExportDeclaration(node) && runtimeExport(node) &&
        node.moduleSpecifier !== undefined && ts.isStringLiteral(node.moduleSpecifier)) {
      includeLiteral(node.moduleSpecifier);
    } else if (ts.isImportEqualsDeclaration(node) && !node.isTypeOnly &&
        ts.isExternalModuleReference(node.moduleReference) &&
        node.moduleReference.expression !== undefined) {
      includeLiteral(node.moduleReference.expression);
    } else if (ts.isCallExpression(node) && node.arguments.length === 1 &&
        (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
          (ts.isIdentifier(node.expression) && node.expression.text === "require"))) {
      includeLiteral(node.arguments[0]!);
    }
    ts.forEachChild(node, visit);
  };
  visit(file);
  return Object.freeze([...new Set(specifiers)].sort(compareUtf8));
};

const candidatePaths = (base: string, specifier: string): readonly string[] => {
  const extension = extname(specifier);
  if (extension === ".js") {
    return Object.freeze([base, `${base.slice(0, -3)}.ts`, `${base.slice(0, -3)}.tsx`]);
  }
  if (extension === ".jsx") {
    return Object.freeze([base, `${base.slice(0, -4)}.tsx`]);
  }
  if (extension === ".mjs") {
    return Object.freeze([base, `${base.slice(0, -4)}.mts`]);
  }
  if (extension === ".cjs") {
    return Object.freeze([base, `${base.slice(0, -4)}.cts`]);
  }
  if (extension.length > 0) return Object.freeze([base]);
  const extensions = [".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".json"];
  return Object.freeze([
    base,
    ...extensions.map((suffix) => `${base}${suffix}`),
    ...extensions.map((suffix) => resolve(base, `index${suffix}`)),
  ]);
};

const ownedFile = async (
  root: string,
  candidate: string,
): Promise<string | undefined> => {
  if (!within(root, candidate)) fail("FACTORY_COMPONENT_PATH_ESCAPE", candidate);
  const stat = await lstat(candidate).catch((error: unknown) => {
    if ((error as { code?: string }).code === "ENOENT") return undefined;
    throw error;
  });
  if (stat === undefined) return undefined;
  if (stat.isSymbolicLink()) fail("FACTORY_COMPONENT_SYMLINK", candidate);
  if (!stat.isFile()) return undefined;
  const owned = await realpath(candidate);
  if (!within(root, owned)) fail("FACTORY_COMPONENT_PATH_ESCAPE", candidate);
  if (owned !== candidate) fail("FACTORY_COMPONENT_SYMLINK", candidate);
  return owned;
};

const resolveImport = async (input: Readonly<{
  root: string;
  importer: string;
  specifier: string;
}>): Promise<string> => {
  const base = resolve(dirname(input.importer), input.specifier);
  if (!within(input.root, base)) {
    return fail("FACTORY_COMPONENT_PATH_ESCAPE", `${input.importer}->${input.specifier}`);
  }
  const candidates = candidatePaths(base, input.specifier);
  const exact = await ownedFile(input.root, candidates[0]!);
  if (exact !== undefined) return exact;
  const resolved = (await Promise.all(candidates.slice(1).map((candidate) =>
    ownedFile(input.root, candidate)))).filter((path): path is string => path !== undefined);
  const distinct = [...new Set(resolved)];
  if (distinct.length === 0) {
    return fail("FACTORY_COMPONENT_IMPORT_UNRESOLVED", `${input.importer}->${input.specifier}`);
  }
  if (distinct.length > 1) {
    return fail("FACTORY_COMPONENT_IMPORT_AMBIGUOUS", `${input.importer}->${input.specifier}`);
  }
  return distinct[0]!;
};

const resolveRoot = async (root: string, path: string): Promise<string> => {
  if (!safeRelativePath(path)) return fail("FACTORY_COMPONENT_ROOT_INVALID", path);
  const target = resolve(root, path);
  const owned = await ownedFile(root, target);
  return owned ?? fail("FACTORY_COMPONENT_ROOT_INVALID", path);
};

export const resolveFactoryComponentClosure = async (input: Readonly<{
  repositoryRoot: string;
  rootPaths: readonly string[];
}>): Promise<readonly string[]> => {
  const root = await realpath(input.repositoryRoot);
  if (input.rootPaths.length === 0 || new Set(input.rootPaths).size !== input.rootPaths.length) {
    return fail("FACTORY_COMPONENT_ROOT_INVALID", "root-set");
  }
  const pending = await Promise.all([...input.rootPaths].sort(compareUtf8)
    .map((path) => resolveRoot(root, path)));
  const visited = new Set<string>();
  while (pending.length > 0) {
    const current = pending.shift()!;
    if (visited.has(current)) continue;
    visited.add(current);
    if (!EXECUTABLE_EXTENSIONS.has(extname(current))) continue;
    const source = await readFile(current, "utf8");
    const specifiers = extractRuntimeSpecifiers(current, source);
    for (const specifier of specifiers) {
      const dependency = await resolveImport({ root, importer: current, specifier });
      if (!visited.has(dependency)) pending.push(dependency);
    }
    pending.sort(compareUtf8);
  }
  return Object.freeze([...visited]
    .map((path) => relative(root, path))
    .sort(compareUtf8));
};
