import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";
import { firefox } from "playwright";

const benchmarkRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(benchmarkRoot, "..");
const config = JSON.parse(await readFile(join(benchmarkRoot, "config.json"), "utf8"));
const startedAt = new Date().toISOString();
const runStamp = startedAt.replace(/[:.]/g, "-");
const runId = process.env.ALCHLANG_BENCHMARK_RUN_ID || `alchlang-docs-${runStamp}`;

function findRepositoryRoot(start) {
  let current = start;
  while (true) {
    if (existsSync(join(current, ".git"))) return current;
    const parent = dirname(current);
    if (parent === current) throw new Error("Could not resolve repository root");
    current = parent;
  }
}

const repositoryRoot = findRepositoryRoot(packageRoot);
const outputRoot = process.env.ALCHLANG_BENCHMARK_OUTPUT
  ? resolve(process.env.ALCHLANG_BENCHMARK_OUTPUT)
  : join(repositoryRoot, "output", "playwright", "ux-validator", runId);

const output = {
  accessibility: join(outputRoot, "accessibility"),
  aria: join(outputRoot, "aria"),
  measurements: join(outputRoot, "measurements"),
  screenshots: join(outputRoot, "screenshots"),
  traces: join(outputRoot, "traces"),
};
await Promise.all(Object.values(output).map((directory) => mkdir(directory, { recursive: true })));

const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const writeJson = (path, value) => writeFile(path, `${JSON.stringify(value, null, 2)}\n`);

async function capturePage(page, path, documentHeight) {
  const maximumImageDimension = 32000;
  if (documentHeight <= maximumImageDimension) {
    await page.screenshot({ path, fullPage: true, timeout: 60000 });
    return [path];
  }
  const viewport = page.viewportSize();
  if (!viewport) throw new Error("Screenshot viewport is unavailable");
  const paths = [];
  const tileHeight = Math.min(12000, maximumImageDimension);
  await page.setViewportSize({ width: viewport.width, height: tileHeight });
  for (let y = 0, part = 1; y < documentHeight; y += tileHeight, part += 1) {
    const partPath = path.replace(/\.png$/, `-part-${part}.png`);
    await page.evaluate((offset) => window.scrollTo(0, offset), y);
    await page.screenshot({ path: partPath, timeout: 60000 });
    paths.push(partPath);
  }
  await page.setViewportSize(viewport);
  return paths;
}

async function filesUnder(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await filesUnder(path));
    else files.push(path);
  }
  return files.sort();
}

async function bundleMeasurements() {
  const dist = join(packageRoot, "dist");
  const assets = await filesUnder(dist);
  const records = [];
  for (const path of assets) {
    const bytes = await readFile(path);
    records.push({
      path: relative(dist, path),
      bytes: bytes.length,
      gzip_bytes: gzipSync(bytes).length,
      sha256: sha256(bytes),
    });
  }
  const runtimeRecords = records.filter((item) => !item.path.endsWith(".map"));
  const sum = (suffix, field) => records.filter((item) => item.path.endsWith(suffix)).reduce((total, item) => total + item[field], 0);
  return {
    files: records,
    javascript_bytes: sum(".js", "bytes"),
    css_bytes: sum(".css", "bytes"),
    total_bytes: runtimeRecords.reduce((total, item) => total + item.bytes, 0),
    total_gzip_bytes: runtimeRecords.reduce((total, item) => total + item.gzip_bytes, 0),
    candidate_sha256: sha256(records.map((item) => `${item.path}:${item.sha256}`).join("\n")),
  };
}

async function freePort() {
  return await new Promise((resolvePort, reject) => {
    const socket = createServer();
    socket.unref();
    socket.once("error", reject);
    socket.listen(0, "127.0.0.1", () => {
      const address = socket.address();
      const port = typeof address === "object" && address ? address.port : null;
      socket.close(() => port ? resolvePort(port) : reject(new Error("Could not allocate preview port")));
    });
  });
}

async function waitForServer(url, child) {
  let lastError;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (child.exitCode !== null) throw new Error(`Vite preview exited with code ${child.exitCode}`);
    try {
      const response = await fetch(url);
      if (response.ok) return;
      lastError = new Error(`Preview returned HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 100));
  }
  throw lastError || new Error("Preview did not become ready");
}

function startPreview(port) {
  const vite = join(packageRoot, "node_modules", "vite", "bin", "vite.js");
  const child = spawn(process.execPath, [vite, "preview", "--host", "127.0.0.1", "--port", String(port), "--strictPort"], {
    cwd: packageRoot,
    env: { ...process.env, NO_COLOR: "1" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  return child;
}

const bundle = await bundleMeasurements();
await writeJson(join(output.measurements, "bundle.json"), bundle);

const port = await freePort();
const baseUrl = `http://127.0.0.1:${port}/`;
const preview = startPreview(port);
let browser;
let browserVersion = "unavailable";
let context;
let benchmarkError;
const runtime = { console: [], page_errors: [], failed_requests: [], http_errors: [], external_requests: [] };
const measurements = [];
const interactionChecks = [];

function recordInteraction(variant, name, passed, detail) {
  interactionChecks.push({ variant, name, passed, detail });
}

try {
  await waitForServer(baseUrl, preview);
  browser = await firefox.launch({ headless: true });
  browserVersion = browser.version();
  context = await browser.newContext({ viewport: config.viewports[0] });
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
  const page = await context.newPage();

  page.on("console", (message) => {
    if (message.type() === "error") runtime.console.push({ type: message.type(), text: message.text() });
  });
  page.on("pageerror", (error) => runtime.page_errors.push({ message: error.message }));
  page.on("requestfailed", (request) => runtime.failed_requests.push({ url: request.url(), error: request.failure()?.errorText || "unknown" }));
  page.on("response", (response) => {
    if (response.status() >= 400) runtime.http_errors.push({ url: response.url(), status: response.status() });
  });
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!["127.0.0.1", "localhost"].includes(url.hostname) && !["data:", "blob:"].includes(url.protocol)) {
      runtime.external_requests.push({ url: request.url(), resource_type: request.resourceType() });
    }
  });

  for (const variant of config.variants) {
    for (const surface of config.surfaces) {
      for (const viewport of config.viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(`${baseUrl}?benchmark=${surface.id}&variant=${variant.id}${surface.hash}`, { waitUntil: "networkidle" });
      await page.addScriptTag({ path: join(packageRoot, "node_modules", "axe-core", "axe.min.js") });

      const layout = await page.evaluate(({ interactiveTargetThreshold, requiredTutorialSections }) => {
        const root = document.documentElement;
        const interactive = [...document.querySelectorAll("a[href], button, input, textarea, select")]
          .filter((element) => {
            const style = getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
          })
          .map((element) => {
            const rect = element.getBoundingClientRect();
            return {
              tag: element.tagName.toLowerCase(),
              label: element.getAttribute("aria-label") || element.textContent?.trim().replace(/\s+/g, " ").slice(0, 80) || "unlabelled",
              width: Number(rect.width.toFixed(2)),
              height: Number(rect.height.toFixed(2)),
            };
          });
        const navigation = performance.getEntriesByType("navigation")[0];
        return {
          title: document.title,
          h1_count: document.querySelectorAll("h1").length,
          main_count: document.querySelectorAll("main").length,
          duplicate_ids: [...document.querySelectorAll("[id]")]
            .map((element) => element.id)
            .filter((id, index, ids) => ids.indexOf(id) !== index),
          document_horizontal_overflow_px: Math.max(0, root.scrollWidth - root.clientWidth),
          document_height_px: root.scrollHeight,
          viewport_pages: Number((root.scrollHeight / innerHeight).toFixed(3)),
          interactive_count: interactive.length,
          heading_count: document.querySelectorAll("h1, h2, h3").length,
          code_block_count: document.querySelectorAll("pre").length,
          table_count: document.querySelectorAll("table, [role=table]").length,
          required_tutorial_sections_missing: requiredTutorialSections.filter((id) => document.querySelectorAll(`#${CSS.escape(id)}`).length !== 1),
          rendered_variant: document.querySelector("[data-experiment-variant]")?.getAttribute("data-experiment-variant") || null,
          targets_below_review_threshold: interactive.filter((item) => item.width < interactiveTargetThreshold || item.height < interactiveTargetThreshold),
          navigation_ms: navigation ? {
            dom_content_loaded: Number(navigation.domContentLoadedEventEnd.toFixed(2)),
            load_event: Number(navigation.loadEventEnd.toFixed(2)),
            response_end: Number(navigation.responseEnd.toFixed(2)),
          } : null,
        };
      }, {
        interactiveTargetThreshold: config.review_thresholds.interactive_target_px,
        requiredTutorialSections: surface.id === "tutorial-workspace" ? config.required_tutorial_sections : [],
      });
      const axe = await page.evaluate(async () => window.axe.run(document, {
        resultTypes: ["violations", "incomplete"],
      }));
      const accessibility = {
        violations: axe.violations,
        incomplete: axe.incomplete,
        violation_count: axe.violations.length,
        impact_counts: axe.violations.reduce((counts, violation) => {
          const impact = violation.impact || "unknown";
          counts[impact] = (counts[impact] || 0) + 1;
          return counts;
        }, {}),
      };
      const record = {
        variant,
        surface,
        viewport,
        ...layout,
        accessibility: {
          ...accessibility.impact_counts,
          total: accessibility.violation_count,
          incomplete: accessibility.incomplete.map((result) => result.id),
        },
      };
      const evidenceId = `${variant.id}-${surface.id}-${viewport.id}`;
      measurements.push(record);
      await writeJson(join(output.measurements, `${evidenceId}.json`), record);
      await writeJson(join(output.accessibility, `axe-${evidenceId}.json`), accessibility);
      await writeFile(join(output.aria, `${evidenceId}.yml`), `${await page.locator("body").ariaSnapshot()}\n`);
      await capturePage(page, join(output.screenshots, `${evidenceId}.png`), layout.document_height_px);
      }
    }
  }

  for (const variant of config.variants) {
    const variantUrl = `${baseUrl}?variant=${variant.id}`;
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(variantUrl, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Next construction step" }).click();
    recordInteraction(variant.id, "walkthrough advances", await page.getByText("Step 2 of 5").isVisible(), "step counter reaches 2 of 5");
    await page.getByRole("button", { name: "Minimize walkthrough" }).click();
    recordInteraction(variant.id, "walkthrough minimizes", await page.getByRole("region", { name: "Build an AlchLang file step by step" }).getAttribute("aria-expanded") === "false", "region reports collapsed state");
    await page.getByRole("button", { name: "Restore walkthrough" }).click();
    await page.getByRole("button", { name: "Maximize walkthrough" }).click();
    recordInteraction(variant.id, "walkthrough maximizes", await page.getByRole("region", { name: "Build an AlchLang file step by step" }).getAttribute("aria-expanded") === "true", "region reports expanded state");
    await page.keyboard.press("Escape");
    recordInteraction(variant.id, "Escape restores walkthrough", await page.getByRole("button", { name: "Maximize walkthrough" }).isVisible(), "maximize control returns after Escape");

    await page.locator("a", { hasText: "Start the tutorial" }).first().click();
    await page.waitForURL(/#quickstart$/);
    recordInteraction(variant.id, "tutorial route opens", await page.getByRole("heading", { name: "Five-minute quickstart" }).isVisible(), "quickstart heading is visible");
    if (variant.id === "progressive-reference") {
      const disclosures = page.locator("details.experiment-disclosure");
      recordInteraction(variant.id, "reference sections start collapsed", await disclosures.evaluateAll((elements) => elements.length === 3 && elements.every((element) => !element.open)), "three long reference sections are initially collapsed");
      await page.goto(`${variantUrl}#lexical-reference`, { waitUntil: "networkidle" });
      recordInteraction(variant.id, "reference deep link opens disclosure", await page.locator("#lexical-reference").getAttribute("open") !== null, "targeted reference section is expanded");
      await page.goto(`${variantUrl}#quickstart`, { waitUntil: "networkidle" });
    }
    await page.getByRole("button", { name: "Search documentation" }).click();
    const search = page.getByRole("dialog", { name: "Search documentation" });
    recordInteraction(variant.id, "search dialog opens", await search.isVisible(), "modal search is visible");
    await search.getByRole("textbox", { name: "Search documentation" }).fill("operation");
    recordInteraction(variant.id, "search returns results", await search.locator(".search-results a").count() > 0, "operation query has at least one result");
    await page.keyboard.press("Shift+Tab");
    recordInteraction(variant.id, "search traps keyboard focus", await search.evaluate((dialog) => dialog.contains(document.activeElement)), "reverse tab remains inside the modal dialog");
    await page.keyboard.press("Escape");
    recordInteraction(variant.id, "Escape closes search", await search.count() === 0, "modal is unmounted");
    recordInteraction(variant.id, "search restores focus", await page.getByRole("button", { name: "Search documentation" }).evaluate((button) => document.activeElement === button), "focus returns to the search trigger");

    await page.goto(`${variantUrl}#workspace`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Check source" }).click();
    await page.locator(".terminal-entry.success").last().waitFor();
    recordInteraction(variant.id, "workspace command executes", await page.locator(".terminal-entry.success").count() > 0, "check source adds a successful terminal entry");
    await capturePage(page, join(output.screenshots, `${variant.id}-workspace-command-desktop.png`), await page.evaluate(() => document.documentElement.scrollHeight));

    await page.setViewportSize({ width: 390, height: 844 });
    await page.reload({ waitUntil: "domcontentloaded", timeout: 60000 });
    await page.getByRole("button", { name: "Open navigation" }).waitFor();
    recordInteraction(variant.id, "closed mobile navigation is inert", await page.locator("#docs-navigation").evaluate((navigation) => getComputedStyle(navigation).visibility === "hidden"), "off-canvas navigation is hidden from keyboard interaction");
    await page.getByRole("button", { name: "Open navigation" }).click();
    recordInteraction(variant.id, "mobile navigation opens", await page.getByRole("complementary", { name: "Documentation navigation" }).getAttribute("class").then((value) => value?.includes("is-open") === true), "sidebar enters open state");
    await page.keyboard.press("Shift+Tab");
    recordInteraction(variant.id, "mobile navigation traps keyboard focus", await page.locator("#docs-navigation").evaluate((navigation) => navigation.contains(document.activeElement)), "reverse tab remains inside the open navigation");
    const navigationBackdrop = await page.getByRole("button", { name: "Close navigation" }).boundingBox();
    if (navigationBackdrop) await page.mouse.click(navigationBackdrop.x + navigationBackdrop.width - 8, navigationBackdrop.y + navigationBackdrop.height / 2);
    recordInteraction(variant.id, "mobile navigation closes", await page.getByRole("button", { name: "Open navigation" }).getAttribute("aria-expanded") === "false", "menu button reports collapsed state");
    recordInteraction(variant.id, "mobile navigation restores focus", await page.getByRole("button", { name: "Open navigation" }).evaluate((button) => document.activeElement === button), "focus returns to the menu trigger");

    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(variantUrl, { waitUntil: "networkidle" });
    const reducedMotion = await page.locator(".overview-builder").evaluate((element) => getComputedStyle(element).transitionDuration);
    recordInteraction(variant.id, "reduced motion is honored", reducedMotion.split(",").every((value) => Number.parseFloat(value) <= 0.001), `transition duration is ${reducedMotion}`);
  }

  await writeJson(join(output.measurements, "interactions.json"), interactionChecks);
} catch (error) {
  benchmarkError = error;
} finally {
  if (context) {
    await context.tracing.stop({ path: join(output.traces, "alchlang-docs.zip") }).catch(() => undefined);
  }
  if (browser) await browser.close().catch(() => undefined);
  preview.kill("SIGTERM");
  await new Promise((resolveWait) => {
    if (preview.exitCode !== null) return resolveWait();
    preview.once("exit", resolveWait);
    setTimeout(() => {
      preview.kill("SIGKILL");
      resolveWait();
    }, 2000).unref();
  });
}

await writeJson(join(outputRoot, "console-network.json"), runtime);

const hardBudgets = config.hard_budgets;
const findings = [];
const hardCheck = (id, title, observed, budget, comparison = "maximum", context = {}) => {
  const passed = comparison === "exact" ? observed === budget : observed <= budget;
  if (!passed) findings.push({ id, class: "hard_gate", severity: "blocking", title, observed, budget, ...context });
};

hardCheck("BENCH-BUNDLE-JS", "JavaScript exceeds its byte budget", bundle.javascript_bytes, hardBudgets.javascript_bytes);
hardCheck("BENCH-BUNDLE-CSS", "CSS exceeds its byte budget", bundle.css_bytes, hardBudgets.css_bytes);
hardCheck("BENCH-BUNDLE-GZIP", "Total compressed output exceeds its byte budget", bundle.total_gzip_bytes, hardBudgets.total_gzip_bytes);
hardCheck("BENCH-CONSOLE", "Browser console errors were observed", runtime.console.length, hardBudgets.console_errors);
hardCheck("BENCH-PAGE-ERROR", "Uncaught page errors were observed", runtime.page_errors.length, hardBudgets.page_errors);
hardCheck("BENCH-REQUEST-FAILED", "Browser requests failed", runtime.failed_requests.length, hardBudgets.failed_requests);
hardCheck("BENCH-HTTP", "HTTP error responses were observed", runtime.http_errors.length, hardBudgets.http_errors);
hardCheck("BENCH-EXTERNAL", "Unexpected external requests were observed", runtime.external_requests.length, hardBudgets.external_requests);

for (const item of measurements) {
  const checkId = `${item.variant.id}-${item.surface.id}-${item.viewport.id}`.toUpperCase();
  const checkLabel = `${item.variant.id} ${item.surface.id} ${item.viewport.id}`;
  const context = { variant: item.variant.id, surface: item.surface.id, viewport: item.viewport.id };
  hardCheck(`BENCH-OVERFLOW-${checkId}`, `${checkLabel} page has horizontal overflow`, item.document_horizontal_overflow_px, hardBudgets.document_horizontal_overflow_px, "maximum", context);
  hardCheck(`BENCH-H1-${checkId}`, `${checkLabel} page must expose one h1`, item.h1_count, 1, "exact", context);
  hardCheck(`BENCH-MAIN-${checkId}`, `${checkLabel} page must expose one main landmark`, item.main_count, 1, "exact", context);
  hardCheck(`BENCH-IDS-${checkId}`, `${checkLabel} page has duplicate IDs`, item.duplicate_ids.length, 0, "maximum", context);
  hardCheck(`BENCH-AXE-${checkId}`, `${checkLabel} page has automated axe violations`, item.accessibility.total, hardBudgets.axe_violations, "maximum", context);
  hardCheck(`BENCH-SECTIONS-${checkId}`, `${checkLabel} page is missing required tutorial sections`, item.required_tutorial_sections_missing.length, 0, "maximum", context);
  hardCheck(`BENCH-VARIANT-${checkId}`, `${checkLabel} did not render the requested treatment`, item.rendered_variant, item.variant.id, "exact", context);
  if (item.accessibility.incomplete.length) {
    findings.push({
      id: `BENCH-AXE-INCOMPLETE-${checkId}`,
      class: "soft_flag",
      severity: "review",
      title: `${checkLabel} has axe checks requiring human review`,
      observed: item.accessibility.incomplete,
      ...context,
    });
  }
  if ((item.navigation_ms?.dom_content_loaded || 0) > config.review_thresholds.dom_content_loaded_ms) {
    findings.push({ id: `BENCH-DCL-${checkId}`, class: "soft_flag", severity: "review", title: `${checkLabel} DOMContentLoaded exceeded the local review threshold`, observed: item.navigation_ms.dom_content_loaded, threshold: config.review_thresholds.dom_content_loaded_ms, ...context });
  }
  if ((item.navigation_ms?.load_event || 0) > config.review_thresholds.load_event_ms) {
    findings.push({ id: `BENCH-LOAD-${checkId}`, class: "soft_flag", severity: "review", title: `${checkLabel} load event exceeded the local review threshold`, observed: item.navigation_ms.load_event, threshold: config.review_thresholds.load_event_ms, ...context });
  }
  if (item.targets_below_review_threshold.length) {
    findings.push({ id: `BENCH-TARGETS-${checkId}`, class: "screenshot_review", severity: "review", title: `${checkLabel} has targets below the review threshold`, observed: item.targets_below_review_threshold.length, threshold_px: config.review_thresholds.interactive_target_px, ...context });
  }
}

for (const check of interactionChecks.filter((item) => !item.passed)) {
  findings.push({ id: `BENCH-INTERACTION-${findings.length + 1}`, class: "hard_gate", severity: "blocking", title: check.name, detail: check.detail, variant: check.variant });
}
if (benchmarkError) findings.push({ id: "BENCH-HARNESS", class: "hard_gate", severity: "blocking", title: "Benchmark harness did not complete", detail: benchmarkError.stack || benchmarkError.message });

const blocking = findings.filter((finding) => finding.class === "hard_gate");
const review = findings.filter((finding) => finding.class !== "hard_gate");
const status = blocking.length ? "block" : review.length ? "flag" : "pass";

await writeJson(join(outputRoot, "findings.json"), {
  schema_version: "alchlang-frontend-benchmark-findings/v1",
  status,
  summary: { blocking: blocking.length, review: review.length, total: findings.length },
  findings,
});

const metadata = {
  schema_version: "alchlang-frontend-benchmark-run/v1",
  run_id: runId,
  started_at: startedAt,
  completed_at: new Date().toISOString(),
  target: baseUrl,
  source: relative(repositoryRoot, packageRoot),
  candidate_sha256: bundle.candidate_sha256,
  browser: { name: "firefox", version: browserVersion },
  variants: config.variants,
  surfaces: config.surfaces,
  viewports: config.viewports,
  status,
  claim_ceiling: "Local production-build browser evidence only; no proof of real-device behavior, complete accessibility conformance, human comprehension, usability, deployment, or production readiness.",
};
await writeJson(join(outputRoot, "run-metadata.json"), metadata);

const summary = `# AlchLang frontend benchmark\n\n- Status: **${status.toUpperCase()}**\n- Candidate: \`${bundle.candidate_sha256}\`\n- Browser: Firefox ${metadata.browser.version}\n- Variants: ${config.variants.map((item) => item.id).join(", ")}\n- Surfaces: ${config.surfaces.map((item) => item.id).join(", ")}\n- Viewports: ${config.viewports.map((item) => `${item.width}x${item.height}`).join(", ")}\n- Variant-surface-viewport scans: ${measurements.length}\n- Interaction checks: ${interactionChecks.length}\n- Hard-gate findings: ${blocking.length}\n- Review findings: ${review.length}\n- Console errors: ${runtime.console.length}\n- Failed requests: ${runtime.failed_requests.length}\n- External requests: ${runtime.external_requests.length}\n- JavaScript: ${bundle.javascript_bytes} bytes\n- CSS: ${bundle.css_bytes} bytes\n- Total gzip: ${bundle.total_gzip_bytes} bytes\n\n## Exercised journeys\n\n- Every experiment variant across overview and complete tutorial/workspace surfaces\n- Required section identity, accessibility, target size, and responsive containment\n- Five-step construction walkthrough, minimize, maximize, and Escape restoration\n- Tutorial navigation and searchable documentation dialog\n- Browser-local workspace validation command\n- Mobile navigation open and close\n- Reduced-motion behavior\n- axe-core automated accessibility scan across every variant, surface, and viewport\n- Console, page-error, HTTP, failed-request, and external-request hygiene\n\n## Claim boundary\n\n${metadata.claim_ceiling}\n`;
await writeFile(join(outputRoot, "summary.md"), summary);
await writeFile(join(outputRoot, "residue-ledger.yml"), `schema_version: alchlang-frontend-benchmark-residue/v1\nresidue:\n  - id: BENCH-RESIDUE-REAL-DEVICES\n    status: open\n    class: human_review\n    statement: Real-device rendering and assistive-technology behavior were not observed.\n  - id: BENCH-RESIDUE-COMPREHENSION\n    status: open\n    class: human_study\n    statement: Automated checks do not establish that readers understand AlchLang or complete tasks successfully.\n  - id: BENCH-RESIDUE-VISUAL\n    status: open\n    class: screenshot_review\n    statement: Screenshots require owner review for typography, hierarchy, clipping, and visual quality.\n`);

console.log(JSON.stringify({ status, output: outputRoot, candidate_sha256: bundle.candidate_sha256, blocking_findings: blocking.length, review_findings: review.length }, null, 2));
if (blocking.length) process.exitCode = 1;
