import { describe, expect, it } from "vitest";
import { artifactRoles, backendTypeAnchor, backendTypes, commonDiagnostics, constructionSteps, declarationClauses, declarationGrammar, diagnosticAnchor, docsSearchEntries, docsViewForHash, domainSpecTarget, fileGrammar, grammarNotation, implementationCoverage, integratedJourney, lexicalRules, metaTypeExtensionSteps, navGroups, overviewHero, packageRoles, quickstart, sections, sfolGrammar, supportingDeclarationAnchor, supportingDeclarations, systemLayers, typeDecisionGuide, validationBoundary } from "./content";
import { defaultWorkspaceSource } from "./workspace";

describe("documentation navigation", () => {
  it("states the landing-page product outcome without internal catalog language", () => {
    const copy = `${overviewHero.lead} ${overviewHero.emphasis} ${overviewHero.descriptionBeforeFile}.alch${overviewHero.descriptionAfterFile}`;
    expect(copy).toContain("people and agents");
    expect(copy).not.toContain("SFOL rules");
    expect(copy).toContain(".alch files");
    expect(copy).toContain("deterministic application code");
    expect(overviewHero.value).toContain("Precise for agents");
    expect(copy).not.toContain("backend types");
  });

  it("uses unique section identifiers", () => {
    const ids = sections.map((section) => section.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("places every section in the navigation", () => {
    const navigationIds = navGroups.flatMap((group) => group.items.map((item) => item.id));
    expect(navigationIds).toEqual(sections.map((section) => section.id));
  });

  it("keeps every searchable section complete", () => {
    for (const section of sections) {
      expect(section.eyebrow.length).toBeGreaterThan(0);
      expect(section.title.length).toBeGreaterThan(0);
      expect(section.summary.length).toBeGreaterThan(30);
    }
  });

  it("opens on the explanatory overview", () => {
    expect(docsViewForHash("")).toBe("overview");
    expect(docsViewForHash("#overview")).toBe("overview");
    expect(docsViewForHash("#unknown")).toBe("overview");
  });

  it("routes tutorial and section links into the guide", () => {
    expect(docsViewForHash("#tutorial")).toBe("tutorial");
    for (const section of sections) {
      expect(docsViewForHash(`#${section.id}`)).toBe("tutorial");
    }
  });

  it("constructs the example cumulatively", () => {
    expect(constructionSteps).toHaveLength(5);
    for (let index = 1; index < constructionSteps.length; index += 1) {
      expect(constructionSteps[index].source.startsWith(constructionSteps[index - 1].source)).toBe(true);
    }
  });

  it("finishes with the exact workspace source", () => {
    expect(constructionSteps.at(-1)?.source).toBe(defaultWorkspaceSource);
  });

  it("maps every implemented capability to a documented section", () => {
    const sectionIds = new Set(sections.map((section) => section.id));
    expect(implementationCoverage).toHaveLength(18);
    for (const item of implementationCoverage) {
      expect(sectionIds.has(item.section)).toBe(true);
      expect(item.evidence.length).toBeGreaterThan(5);
    }
  });

  it("covers the current compiler, registry, durable runtime, and integrations", () => {
    expect(implementationCoverage.map((item) => item.capability)).toEqual(expect.arrayContaining([
      "validate-lower-render-write",
      "domainspec-exact-uint64-lowering",
      "integrated-alch-domainspec-journey",
      "operation-pattern-registry",
      "sqlite-outbox-generator",
      "durable-transactional-outbox",
      "confirmed-http-transport",
      "idempotent-inbox",
      "value-object-and-enum-contracts",
      "full-operation-contract",
      "workflow-interface-and-state-machine-contracts",
    ]));
  });

  it("keeps internal open-question language out of the user-facing product", async () => {
    const appSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./App.tsx", import.meta.url), "utf8"));
    const contentSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./content.ts", import.meta.url), "utf8"));
    expect(`${appSource}\n${contentSource}`).not.toMatch(/open questions?/i);
  });

  it("uses the Exchange orb without exposing build versions in the overview header", async () => {
    const appSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./App.tsx", import.meta.url), "utf8"));
    expect(appSource).toContain("cyberalchemy-orb-frozen.webp");
    expect(appSource).not.toContain("Alch v0.4 · Craft 1.0");
  });

  it("uses one product lockup and the canonical Lab identity across both pages", async () => {
    const appSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./App.tsx", import.meta.url), "utf8"));
    const styleSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./styles.css", import.meta.url), "utf8"));
    expect(appSource).toContain("function ProductLogo");
    expect(appSource).toContain("./assets/alchlang-mark.svg");
    expect(appSource).toContain("./assets/craft-mark.svg");
    expect(appSource).not.toContain("function BrandMark");
    expect(appSource).toContain("cyberalchemy-lab-logo-light-v2.svg");
    expect(appSource.match(/<ProductFooter/g)).toHaveLength(2);
    expect(appSource).toContain("ALCHLANG + CRAFT");
    expect(appSource).not.toContain("ALCHLANG + DOMAINSPEC");
    expect(styleSource).not.toMatch(/\.overview-brand[^{}]*(?:strong|em)[^{]*\{[^}]*display:\s*none/);
    expect(styleSource).toContain("@media (max-width: 900px)");
    expect(styleSource).toContain("@media (min-width: 521px) and (max-width: 900px)");
    expect(styleSource).toContain("@media (max-width: 520px)");
    expect(styleSource).toContain("@media (max-height: 700px) and (min-width: 901px)");
    expect(styleSource).not.toContain("min-height: min(calc(100svh - 56px), 700px)");
  });

  it("keeps the responsive walkthrough inset and expands it in document flow", async () => {
    const appSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./App.tsx", import.meta.url), "utf8"));
    const styleSource = await import("node:fs/promises").then((fs) => fs.readFile(new URL("./styles.css", import.meta.url), "utf8"));
    expect(appSource).not.toContain('document.body.style.overflow = "hidden"');
    expect(appSource).not.toContain("builder-backdrop");
    expect(styleSource).toContain("width: min(760px, calc(100% - 48px))");
    expect(styleSource).toContain("width: calc(100% - 20px)");
    expect(styleSource).toMatch(/\.overview-builder\.is-maximized\s*\{[^}]*position:\s*relative/);
    expect(styleSource).toMatch(/\.overview-builder\.is-maximized\s*>\s*pre\s*\{[^}]*overflow-y:\s*visible/);
  });

  it("explains the complete AlchLang to Craft handoff", () => {
    expect(sections.some((section) => section.id === "integration")).toBe(true);
    expect(sections.some((section) => section.id === "domainspec-target")).toBe(true);
    expect(systemLayers.map((layer) => layer.product)).toEqual(["AlchLang", "Craft", "Your application"]);
    expect(integratedJourney.map((item) => item.owner)).toEqual(["AlchLang", "AlchLang", "Craft", "Craft", "Application", "Evidence"]);
    expect(packageRoles).toHaveLength(4);
    expect(artifactRoles).toHaveLength(6);
  });

  it("keeps first-use commands package-first and application-facing", () => {
    expect(quickstart).toContain("npm install ../cyberalchemy-alchlang-0.4.0-candidate.0.tgz");
    expect(quickstart).toContain("npx alchlang build workspace.alch");
    expect(quickstart).not.toContain("node dist/cli.js");
    expect(domainSpecTarget.install).toContain("domainspec-v2-cli-1.0.0.tgz");
    expect(domainSpecTarget.commands).toContain("npx alchlang");
    expect(domainSpecTarget.usage).toContain("selectPolicy");
  });

  it("presents the complete non-contiguous Craft backend profile", () => {
    expect(backendTypes).toHaveLength(13);
    expect(backendTypes.map((type) => type.id)).toEqual([
      "DS-D1.1", "DS-D1.2", "DS-D1.3", "DS-D1.4", "DS-D1.5", "DS-D1.6", "DS-D1.7",
      "DS-D1.8", "DS-D1.9", "DS-D1.11", "DS-D1.12", "DS-D1.13", "DS-D1.14",
    ]);
    expect(backendTypes.map((type) => String(type.name))).not.toContain("Saga");
  });

  it("provides a complete reference record for every backend type", () => {
    for (const type of backendTypes) {
      expect(type.meaning.length).toBeGreaterThan(40);
      expect(type.useWhen.length).toBeGreaterThan(50);
      expect(type.form).toContain(`${type.syntax} `);
      expect(type.requirements.length).toBeGreaterThanOrEqual(3);
      expect(type.compilesTo.length).toBeGreaterThan(40);
    }
  });

  it("separates selection, lexical, declaration, and grammar references", () => {
    expect(sections.map((section) => section.id)).toEqual(expect.arrayContaining([
      "type-selection", "lexical-reference", "declaration-reference", "formal-grammar",
    ]));
    expect(supportingDeclarations.map((item) => item.syntax)).toEqual([
      "actor", "boundary", "permission", "action", "effect", "example",
    ]);
    expect(typeDecisionGuide.length).toBeGreaterThanOrEqual(8);
    expect(lexicalRules.map((item) => item.subject)).toEqual(expect.arrayContaining(["Canonical file", "Identifier", "String literal"]));
    expect(grammarNotation).toHaveLength(7);
    expect(fileGrammar).toContain("[A-Za-z_][A-Za-z0-9_.-]*");
    expect(declarationGrammar).toContain("value-object");
    expect(declarationGrammar).toContain("state-machine");
    expect(sfolGrammar).toContain("comparison");
    expect(sfolGrammar).toContain("divide(a,b)");
    expect(validationBoundary.map((item) => item.layer)).toEqual(["Lexing and parsing", "Semantic validation", "Compilation"]);
    expect(metaTypeExtensionSteps).toHaveLength(6);
  });

  it("indexes sections, declarations, lexical rules, and diagnostics", () => {
    const searchable = docsSearchEntries.map((item) => `${item.title} ${item.summary} ${item.terms.join(" ")}`).join(" ");
    expect(searchable).toContain("Operation");
    expect(searchable).toContain("permission");
    expect(searchable).toContain("[A-Za-z_][A-Za-z0-9_.-]*");
    for (const diagnostic of commonDiagnostics) expect(searchable).toContain(diagnostic);
  });

  it("provides clause records for every accepted declaration", () => {
    const syntaxes = [...backendTypes, ...supportingDeclarations].map((item) => item.syntax);
    expect(Object.keys(declarationClauses).sort()).toEqual([...syntaxes].sort());
    for (const syntax of syntaxes) {
      const clauses = declarationClauses[syntax];
      expect(clauses).toBeDefined();
      for (const clause of clauses) {
        expect(clause.clause.length).toBeGreaterThan(2);
        expect(clause.value.length).toBeGreaterThan(2);
        expect(clause.meaning.length).toBeGreaterThan(20);
        expect(["0", "0..1", "0..n", "1", "1..n", "2..n"]).toContain(clause.cardinality);
      }
    }
  });

  it("routes every reference result to a stable unique anchor", () => {
    const anchors = [
      ...backendTypes.map((item) => backendTypeAnchor(item.syntax)),
      ...supportingDeclarations.map((item) => supportingDeclarationAnchor(item.syntax)),
      ...commonDiagnostics.map(diagnosticAnchor),
    ];
    expect(new Set(anchors).size).toBe(anchors.length);
    for (const anchor of anchors) {
      expect(docsSearchEntries.some((entry) => entry.id === anchor)).toBe(true);
      expect(docsViewForHash(`#${anchor}`)).toBe("tutorial");
    }
  });
});
