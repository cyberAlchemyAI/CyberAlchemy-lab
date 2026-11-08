import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {beforeAll, describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {typeScriptEntityV1Provider} from
  "../../../../factory/registry/providers/typescript-entity-v1.js";
import {buildTypeScriptEntityProof, TYPESCRIPT_ENTITY_RAW_PATHS,
  type TypeScriptEntityRawInputs} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../../../../../../..");
let raw: TypeScriptEntityRawInputs;

beforeAll(async () => {
  const entries = await Promise.all(Object.entries(
    TYPESCRIPT_ENTITY_RAW_PATHS).map(async ([role, path]) =>
    [role, await readFile(resolve(root, path), "utf8")] as const));
  raw = Object.freeze(Object.fromEntries(entries)) as TypeScriptEntityRawInputs;
});

describe("TypeScript Entity realization and candidate provider", () => {
  it("executes exact source twice and keeps evidence classes separate", async () => {
    const proof = await buildTypeScriptEntityProof(raw);
    expect(proof.family_evaluation.verdict).toBe("pass");
    expect(proof.accounting).toEqual({
      positives: {declared: 5, passed: 5},
      construction_routes: {declared: 4, observed: 4},
      source_controls: {declared: 10, rejected: 10},
      predecessor_family_controls: {declared: 7, killed: 7},
    });
    expect(proof.process_evidence).toMatchObject({executions: 2, distinct_pids: 2,
      input_materialization: "json-inert-owner-cases",
      process_ids_excluded_from_semantic_digest: true});
  });

  it("direct-calls the provider but leaves registry lookup unknown", async () => {
    const result = await typeScriptEntityV1Provider.execute({raw_inputs: raw,
      upstream: Object.freeze({})});
    expect(result.accounting).toEqual({positives_declared: 5,
      positives_passed: 5, mutants_declared: 17, mutants_killed: 17});
    expect(listFactoryNodeProvidersV1().some(({provider_id}) =>
      provider_id === "typescript-entity-v1")).toBe(false);
  });

  it("snapshots callers and rejects stale proof-producing roles", async () => {
    const staleRoles = Object.keys(TYPESCRIPT_ENTITY_RAW_PATHS).filter(
      (candidate) => candidate !== "binding") as readonly Exclude<
        keyof TypeScriptEntityRawInputs, "binding">[];
    expect(staleRoles).toHaveLength(13);
    for (const role of staleRoles) {
      await expect(buildTypeScriptEntityProof({...raw,
        [role]: `${raw[role]}\n`})).rejects.toThrow("TS_ENTITY_BINDING_INPUT_STALE");
    }
    const stale = JSON.parse(raw.binding) as Record<string, unknown>;
    stale.binding_sha256 = "0".repeat(64);
    await expect(buildTypeScriptEntityProof({...raw,
      binding: JSON.stringify(stale)}))
      .rejects.toThrow("TS_ENTITY_BINDING_DIGEST_STALE");
    const callerOwned = {...raw};
    const pending = buildTypeScriptEntityProof(callerOwned);
    callerOwned.source = "caller-mutated-after-invocation";
    await expect(pending).resolves.toMatchObject({result: "pass"});
  });
});
