import { readFile, readdir } from "node:fs/promises";
import { writeFileSync } from "node:fs";
import { dirname, posix, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import ts from "typescript";

const here = dirname(fileURLToPath(import.meta.url));
const defaultRepositoryRoot = resolve(here, "../../../../../..");
const sourceExtensions = [".ts", ".tsx", ".mts", ".cts"];

const walk = async (root) => {
  const files = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) files.push(...await walk(path));
    else if (entry.isFile() && sourceExtensions.some((extension) =>
      entry.name.endsWith(extension))) files.push(path);
  }
  return files;
};

const scriptKindFor = (path) => path.endsWith(".tsx")
  ? ts.ScriptKind.TSX
  : path.endsWith(".mts")
    ? ts.ScriptKind.TS
    : path.endsWith(".cts")
      ? ts.ScriptKind.TS
      : ts.ScriptKind.TS;

const isLiteralModuleSpecifier = (node) =>
  ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node);

const hasRuntimeImportBindings = (clause) => {
  if (clause === undefined) return true;
  if (clause.isTypeOnly) return false;
  if (clause.name !== undefined) return true;
  if (clause.namedBindings === undefined ||
      ts.isNamespaceImport(clause.namedBindings)) return true;
  return clause.namedBindings.elements.some((element) => !element.isTypeOnly);
};

const hasRuntimeExportBindings = (declaration) => {
  if (declaration.isTypeOnly) return false;
  if (declaration.exportClause === undefined ||
      ts.isNamespaceExport(declaration.exportClause)) return true;
  return declaration.exportClause.elements.some((element) => !element.isTypeOnly);
};

const extractRuntimeModuleSpecifiers = (source, path) => {
  const sourceFile = ts.createSourceFile(
    path,
    source,
    ts.ScriptTarget.Latest,
    true,
    scriptKindFor(path),
  );
  const specifiers = [];
  const visit = (node) => {
    if (ts.isImportDeclaration(node) &&
        isLiteralModuleSpecifier(node.moduleSpecifier) &&
        hasRuntimeImportBindings(node.importClause)) {
      specifiers.push(node.moduleSpecifier.text);
    } else if (ts.isExportDeclaration(node) &&
        node.moduleSpecifier !== undefined &&
        isLiteralModuleSpecifier(node.moduleSpecifier) &&
        hasRuntimeExportBindings(node)) {
      specifiers.push(node.moduleSpecifier.text);
    } else if (ts.isImportEqualsDeclaration(node) &&
        !node.isTypeOnly &&
        ts.isExternalModuleReference(node.moduleReference) &&
        node.moduleReference.expression !== undefined &&
        isLiteralModuleSpecifier(node.moduleReference.expression)) {
      specifiers.push(node.moduleReference.expression.text);
    } else if (ts.isCallExpression(node) && node.arguments.length === 1 &&
        isLiteralModuleSpecifier(node.arguments[0]) &&
        (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
          (ts.isIdentifier(node.expression) && node.expression.text === "require"))) {
      specifiers.push(node.arguments[0].text);
    }
    ts.forEachChild(node, visit);
  };
  visit(sourceFile);
  return specifiers;
};

const normalizedImportPath = (specifier, sourcePath) => {
  const normalizedSpecifier = specifier.replaceAll("\\", "/");
  if (!normalizedSpecifier.startsWith(".")) {
    return posix.normalize(normalizedSpecifier);
  }
  return posix.normalize(posix.join(posix.dirname(
    sourcePath.replaceAll("\\", "/"),
  ), normalizedSpecifier));
};

const pathSegments = (value) => value.split("/").filter((part) =>
  part !== "" && part !== "." && part !== "..");

const hasSegment = (segments, segment) => segments.includes(segment);

const isProviderRegistryPath = (segments) => hasSegment(segments, "registry");

const isExpectedFixturePath = (segments) =>
  hasSegment(segments, "fixtures") ||
  segments.some((segment) => /^(?:expected(?:-results?)?|obligations?|mutants?)$/u
    .test(segment.replace(/\.[^.]+$/u, "")));

const sourceFamily = (sourcePath) => {
  const segments = pathSegments(sourcePath.replaceAll("\\", "/"));
  const familyIndex = segments.indexOf("families");
  return familyIndex === -1 ? undefined : segments[familyIndex + 1];
};

const importsAnotherFamily = (segments, sourcePath) => {
  const familyIndex = segments.indexOf("families");
  if (familyIndex === -1) return false;
  const importedFamily = segments[familyIndex + 1];
  const currentFamily = sourceFamily(sourcePath);
  return currentFamily === undefined || importedFamily === undefined ||
    currentFamily !== importedFamily;
};

const isLegacyFiniteVocabularyBridge = (sourcePath, segments) =>
  sourcePath.replaceAll("\\", "/") === "families/finite-vocabulary/index.ts" &&
  hasSegment(segments, "realization") &&
  (hasSegment(segments, "evaluator") || hasSegment(segments, "enum"));

const isEvaluatorContractImport = (sourcePath, importedPath) =>
  sourcePath.replaceAll("\\", "/").startsWith("realization/evaluator/") &&
  importedPath.startsWith("realization/contracts/");

const codesForImport = (lane, specifier, sourcePath) => {
  const importedPath = normalizedImportPath(specifier, sourcePath);
  const segments = pathSegments(importedPath);
  const codes = [];
  if (lane === "kernel") {
    if (hasSegment(segments, "families")) codes.push("KERNEL_IMPORTS_FAMILY");
    if (hasSegment(segments, "targets")) codes.push("KERNEL_IMPORTS_TARGET");
    if (hasSegment(segments, "realization") ||
        hasSegment(segments, "realizations")) {
      codes.push("KERNEL_IMPORTS_REALIZATION");
    }
    if (hasSegment(segments, "acceptance")) {
      codes.push("KERNEL_IMPORTS_ACCEPTANCE");
    }
    if (isProviderRegistryPath(segments) && !importedPath.startsWith("kernel/")) {
      codes.push("KERNEL_IMPORTS_PROVIDER_REGISTRY");
    }
  } else if (lane === "family") {
    if (hasSegment(segments, "targets") ||
        (hasSegment(segments, "typescript") &&
          segments.some((segment) => /^(?:adapter|adapter-tests|compiler|generator)$/u
            .test(segment)))) {
      codes.push("FAMILY_IMPORTS_TARGET_IMPLEMENTATION");
    }
    if ((hasSegment(segments, "realization") ||
         hasSegment(segments, "realizations")) &&
        !isLegacyFiniteVocabularyBridge(sourcePath, segments) &&
        !isEvaluatorContractImport(sourcePath, importedPath)) {
      codes.push("FAMILY_IMPORTS_REALIZATION");
    }
    if (hasSegment(segments, "acceptance")) {
      codes.push("FAMILY_IMPORTS_ACCEPTANCE");
    }
    if (isProviderRegistryPath(segments)) {
      codes.push("FAMILY_IMPORTS_PROVIDER_REGISTRY");
    }
    if (importsAnotherFamily(segments, sourcePath)) {
      codes.push("FAMILY_IMPORTS_ANOTHER_FAMILY");
    }
    if (isExpectedFixturePath(segments)) {
      codes.push("FAMILY_IMPORTS_PRODUCER_OR_EXPECTATION");
    }
  } else if (lane === "target") {
    if (hasSegment(segments, "families")) codes.push("TARGET_IMPORTS_FAMILY");
    if (hasSegment(segments, "realization") ||
        hasSegment(segments, "realizations")) {
      codes.push("TARGET_IMPORTS_REALIZATION");
    }
    if (hasSegment(segments, "acceptance")) {
      codes.push("TARGET_IMPORTS_ACCEPTANCE");
    }
    if (isExpectedFixturePath(segments)) {
      codes.push("TARGET_IMPORTS_EXPECTED_SEMANTICS");
    }
  } else if (lane === "registry") {
    const allowed = importedPath.startsWith("factory/registry/providers/") ||
      importedPath.startsWith("factory/contracts/") ||
      importedPath.startsWith("factory/shared/");
    if (!allowed) codes.push("REGISTRY_IMPORTS_NON_PROVIDER");
  }
  return codes;
};

export const findProviderFirewallViolations = (lane, source, path = "probe.ts") => {
  const codes = new Set();
  for (const specifier of extractRuntimeModuleSpecifiers(source, path)) {
    for (const code of codesForImport(lane, specifier, path)) codes.add(code);
  }
  if (lane === "kernel" && /\bEnum\b|DS-D1\.3|status\.paid/u.test(source)) {
    codes.add("KERNEL_CONTAINS_ENUM_SEMANTICS");
  }
  return [...codes].map((code) => ({ code, path }));
};

const validateFirewallFixtures = async (fixtureRoot) => {
  const manifestPath = resolve(fixtureRoot, "manifest.json");
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const violations = [];
  for (const fixture of manifest.fixtures) {
    const fixturePath = resolve(fixtureRoot, fixture.source);
    const source = await readFile(fixturePath, "utf8");
    const actual = findProviderFirewallViolations(
      fixture.lane,
      source,
      fixture.path,
    ).map(({ code }) => code).sort();
    const expected = [...fixture.expected_codes].sort();
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      violations.push({
        code: "PROVIDER_FIREWALL_FIXTURE_MISMATCH",
        path: fixturePath,
      });
    }
  }
  return violations;
};

export const validateProviderFirewalls = async (
  repositoryRoot = defaultRepositoryRoot,
) => {
  const architectureRoot = resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance",
  );
  const lanes = [
    ["kernel", resolve(architectureRoot, "kernel")],
    ["family", resolve(architectureRoot, "families")],
    ["family", resolve(architectureRoot, "realization/evaluator")],
    ["target", resolve(architectureRoot, "targets")],
  ];
  const violations = [];
  for (const [lane, root] of lanes) {
    for (const path of await walk(root)) {
      const relative = path.slice(architectureRoot.length + 1);
      if (relative.endsWith(".test.ts") ||
          relative.endsWith("/forbidden-imports.ts") ||
          relative.includes("/fixtures/") ||
          relative.includes("/testing/")) continue;
      violations.push(...findProviderFirewallViolations(
        lane,
        await readFile(path, "utf8"),
        relative,
      ));
    }
  }
  const registryPath = resolve(
    architectureRoot,
    "factory/registry/factory-node-registry-v1.ts",
  );
  violations.push(...findProviderFirewallViolations(
    "registry",
    await readFile(registryPath, "utf8"),
    "factory/registry/factory-node-registry-v1.ts",
  ));
  violations.push(...await validateFirewallFixtures(resolve(
    architectureRoot,
    "kernel/testing/fixtures/provider-firewalls",
  )));
  const expectationPath = resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/test-derivation-engine/src/bte/self-authored-expectations.ts",
  );
  const expectationSource = await readFile(expectationPath, "utf8");
  if (/buildCatalogues|deriveDevelopmentCatalogues/u.test(expectationSource)) {
    violations.push({
      code: "BTE_EXPECTATION_IMPORTS_GENERATED_CATALOGUE",
      path: expectationPath,
    });
  }
  return {
    schema_version: "ProviderFirewallValidation/v1",
    result: violations.length === 0 ? "pass" : "fail",
    violations,
    authority_effect: "none",
  };
};

const [mode, lane, source] = process.argv.slice(2);
const result = mode === "--probe"
  ? {
      schema_version: "ProviderFirewallProbe/v1",
      result: findProviderFirewallViolations(lane, source).length === 0
        ? "pass"
        : "fail",
      violations: findProviderFirewallViolations(lane, source),
      authority_effect: "none",
    }
  : await validateProviderFirewalls(mode || defaultRepositoryRoot);
writeFileSync(process.stdout.fd, `${JSON.stringify(result)}\n`);
if (result.result !== "pass") process.exitCode = 1;
