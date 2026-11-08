import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  PROVIDER_CAPABILITIES,
  ProviderPackSelectionError,
  providerPackSelectionSha256,
  validateProviderPackSelectionV1,
  compileProviderRuntimeProfileV1,
  resolveProviderRuntimeProfileV1,
  REFERENCE_PROVIDER_RUNTIME,
} from "../../src/system-integration/provider-pack-v1.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");

function source(language: "typescript" | "python" | "rust"): any {
  return JSON.parse(fs.readFileSync(path.join(example, `providers/${language}.json`), "utf8"));
}

test("L2 provider selections close the exact three-language provider matrix", () => {
  const selections = (["typescript", "python", "rust"] as const).map(language => validateProviderPackSelectionV1(source(language), language));
  assert.deepEqual(selections.map(selection => selection.language), ["typescript", "python", "rust"]);
  assert.deepEqual(selections.map(selection => selection.capabilities), [PROVIDER_CAPABILITIES, PROVIDER_CAPABILITIES, PROVIDER_CAPABILITIES]);
  assert.equal(selections.every(selection => Object.isFrozen(selection) && Object.isFrozen(selection.providers)), true);
  assert.equal(new Set(selections.map(providerPackSelectionSha256)).size, 3);
  assert.equal(selections.every(selection => selection.authority_effect === "none"), true);
});

test("runtime profile assertions preserve existing selections and reject unsupported requirements", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const input = source(language);
    const result = compileProviderRuntimeProfileV1(input, REFERENCE_PROVIDER_RUNTIME[language]);
    assert.deepEqual(result.selection, input);
    assert.equal(result.selection_sha256, providerPackSelectionSha256(validateProviderPackSelectionV1(input)));
    assert.equal(result.runtime_guarantees_observed, false);
    assert.equal(Object.isFrozen(result.requirements), true);
    const request = { ...input, schema_version: "domainspec.provider-profile-request/v1-candidate",
      providers: Object.fromEntries(Object.entries(input.providers).map(([role, item]) => [role, (item as any).provider_id])) };
    assert.deepEqual(resolveProviderRuntimeProfileV1(request, REFERENCE_PROVIDER_RUNTIME[language]), result);
    assert.throws(() => resolveProviderRuntimeProfileV1({ ...request, pack_id: "unknown/pack" }, REFERENCE_PROVIDER_RUNTIME[language]), /DS_PROVIDER_SELECTION_SCHEMA/);
    assert.throws(() => resolveProviderRuntimeProfileV1({ ...request, providers: { ...request.providers, persistence: "postgresql:17" } }, REFERENCE_PROVIDER_RUNTIME[language]), /DS_PROVIDER_SELECTION_REALIZATION/);
    assert.throws(() => resolveProviderRuntimeProfileV1({ ...request, providers: {} }, REFERENCE_PROVIDER_RUNTIME[language]), /DS_PROVIDER_SELECTION_SCHEMA/);
    assert.throws(() => compileProviderRuntimeProfileV1(input, {}), /DS_PROVIDER_SELECTION_SCHEMA/);
    assert.throws(() => compileProviderRuntimeProfileV1(input, { ...REFERENCE_PROVIDER_RUNTIME[language], secret: "not-a-reference" }), /DS_PROVIDER_SELECTION_SCHEMA/);
    const requirement = Object.keys(REFERENCE_PROVIDER_RUNTIME[language])[0]!;
    assert.throws(() => compileProviderRuntimeProfileV1(input, { [requirement]: "unsupported" }), /DS_PROVIDER_RUNTIME_REQUIREMENTS/);
  }
});

test("L2 provider selection rejects fallback, version drift, language mismatch, and credential values", () => {
  const cases: readonly [string, (value: any) => void, string][] = [
    ["unknown provider", value => { value.providers.persistence.library = "fallback-pg"; }, "DS_PROVIDER_SELECTION_REALIZATION"],
    ["version drift", value => { value.providers.messaging.version = "latest"; }, "DS_PROVIDER_SELECTION_REALIZATION"],
    ["capability collapse", value => { value.capabilities.pop(); }, "DS_PROVIDER_SELECTION_CAPABILITY"],
    ["credential value", value => { value.configuration.password = "secret"; }, "DS_PROVIDER_SELECTION_SCHEMA"],
    ["case drift", value => { value.providers.persistence.provider_id = "PostgreSQL:16"; }, "DS_PROVIDER_SELECTION_REALIZATION"],
  ];
  for (const [name, mutate, code] of cases) {
    const value = source("typescript");
    mutate(value);
    assert.throws(
      () => validateProviderPackSelectionV1(value, "typescript"),
      (error: unknown) => error instanceof ProviderPackSelectionError && error.code === code,
      name,
    );
  }
  assert.throws(
    () => validateProviderPackSelectionV1(source("typescript"), "python"),
    (error: unknown) => error instanceof ProviderPackSelectionError && error.code === "DS_PROVIDER_SELECTION_LANGUAGE",
  );
});
