import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {beforeAll, describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {typeScriptValueObjectV1Provider} from
  "../../../../factory/registry/providers/typescript-value-object-v1.js";
import {buildTypeScriptValueObjectProof, TYPESCRIPT_VALUE_OBJECT_RAW_PATHS,
  type TypeScriptValueObjectRawInputs} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../../../../../../..");
let raw: TypeScriptValueObjectRawInputs;

beforeAll(async () => {
  const entries = await Promise.all(Object.entries(
    TYPESCRIPT_VALUE_OBJECT_RAW_PATHS).map(async ([role, path]) =>
    [role, await readFile(resolve(root, path), "utf8")] as const));
  raw = Object.freeze(Object.fromEntries(entries)) as TypeScriptValueObjectRawInputs;
});

describe("TypeScript Value Object realization and registered provider", () => {
  it("executes the exact target twice and passes all portable decisions", async () => {
    const proof = await buildTypeScriptValueObjectProof(raw);
    expect(proof.family_evaluation.verdict).toBe("pass");
    expect(proof.accounting).toEqual({positives: {declared: 7, passed: 7},
      static_binding_controls: {declared: 8, rejected: 8},
      predecessor_family_controls: {declared: 12, killed: 12}});
    expect(proof.process_evidence).toMatchObject({executions: 2, distinct_pids: 2,
      input_materialization: "json-inert-owner-cases",
      process_ids_excluded_from_semantic_digest: true});
  });

  it("direct-calls the provider and resolves its RMT-VO-006 registration", async () => {
    const result = await typeScriptValueObjectV1Provider.execute({raw_inputs: raw,
      upstream: Object.freeze({})});
    expect(result.accounting).toEqual({positives_declared: 7, positives_passed: 7,
      mutants_declared: 12, mutants_killed: 12});
    expect(listFactoryNodeProvidersV1().some(({provider_id}) =>
      provider_id === "typescript-value-object-v1")).toBe(true);
  });

  it("snapshots and rejects every stale proof-producing input", async () => {
    for (const role of Object.keys(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS).filter(
      (candidate) => candidate !== "binding") as readonly Exclude<
        keyof TypeScriptValueObjectRawInputs, "binding">[]) {
      await expect(buildTypeScriptValueObjectProof({...raw,
        [role]: `${raw[role]}\n`})).rejects.toThrow("TS_VALUE_OBJECT_BINDING_INPUT_STALE");
    }
    const staleBinding = JSON.parse(raw.binding) as Record<string, unknown>;
    staleBinding.binding_sha256 = "0".repeat(64);
    await expect(buildTypeScriptValueObjectProof({...raw,
      binding: JSON.stringify(staleBinding)}))
      .rejects.toThrow("TS_VALUE_OBJECT_BINDING_DIGEST_STALE");

    const callerOwned = {...raw};
    const pending = buildTypeScriptValueObjectProof(callerOwned);
    callerOwned.source = "caller-mutated-after-invocation";
    await expect(pending).resolves.toMatchObject({result: "pass"});
  });
});
