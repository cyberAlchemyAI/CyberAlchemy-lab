import {readdir, readFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1, listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {operationRustV1Provider} from
  "../../../../factory/registry/providers/operation-rust-v1.js";
import {rustQueryV1Provider} from
  "../../../../factory/registry/providers/rust-query-v1.js";
import {
  canonicalOperationJson,
  sha256OperationBytes,
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {
  inspectRustOperationClosedSubset,
  RUST_OPERATION_SOURCE_CONTROLS,
} from "./closed-subset.js";
import {
  parseRustOperationChildOutput,
  RUST_OPERATION_RAW_PATHS,
  type RustOperationRawInputs,
} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = process.cwd();
const candidateImplRoot = resolve(here, "../../../../..");

const readCandidateOrLive = async (path: string): Promise<string> => {
  if (path.startsWith("projects/domainspec-v2/impl/")) {
    const suffix = path.slice("projects/domainspec-v2/impl/".length);
    try {
      return await readFile(resolve(candidateImplRoot, suffix), "utf8");
    } catch {
      // OP005 staged material intentionally falls back to live OP002 inputs.
    }
  }
  return readFile(resolve(repositoryRoot, path), "utf8");
};

const readRawInputs = async (): Promise<RustOperationRawInputs> =>
  Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(RUST_OPERATION_RAW_PATHS).map(
      async ([role, path]) => [
        role,
        await readCandidateOrLive(path),
      ] as const,
    ),
  ))) as RustOperationRawInputs;

const rebindRole = (
  raw: RustOperationRawInputs,
  role: Exclude<keyof RustOperationRawInputs, "binding">,
  bytes: string,
): RustOperationRawInputs => {
  const binding = JSON.parse(raw.binding) as {
    refs: Record<string, {sha256: string}>;
    binding_sha256: string;
  } & Record<string, unknown>;
  binding.refs[role]!.sha256 = sha256OperationBytes(bytes);
  const {binding_sha256: _digest, ...body} = binding;
  binding.binding_sha256 = sha256OperationBytes(
    canonicalOperationJson(body),
  );
  return Object.freeze({...raw, [role]: bytes,
    binding: JSON.stringify(binding)});
};

const rebindSource = (
  raw: RustOperationRawInputs,
  source: string,
): RustOperationRawInputs => rebindRole(raw, "source", source);

const workspaceNames = async (): Promise<string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-rust-operation-"))
  .sort();

describe("Rust Operation direct provider", () => {
  it("proves both owner cases, 10 native controls, and 19 family controls", async () => {
    const beforeWorkspaces = await workspaceNames();
    const defaultFiles = await Promise.all([
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.lock",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/lib.rs",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/mod.rs",
    ].map((path) => readFile(resolve(repositoryRoot, path))));
    const result = await operationRustV1Provider.execute({
      raw_inputs: await readRawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "operation-rust-v1",
      accounting: {
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 29,
        mutants_killed: 29,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          schema_version: "RustOperationComposedProof/v1",
          result: "pass",
          target: {
            target_id: "operation.rust.complete-settlement/v1",
            protocol_id: "rust.bound-operation/v1",
            language: "rust",
            symbol_name: "COMPLETE_SETTLEMENT_OPERATION",
          },
          runtime_proof: {
            owner_cases: 2,
            fresh_processes: 4,
            distinct_pid_pairs: 2,
            globally_distinct_pids: 4,
            observer_origin: "independent-injected-port-harness",
          },
          accounting: {
            positives: {declared: 2, passed: 2},
            target_source_controls: {declared: 10, killed: 10},
            family_controls: {declared: 19, killed: 19},
            mutants: {declared: 29, killed: 29},
          },
        },
      },
      authority_effect: "none",
    });
    const proof = (result.semantic_output as {
      proof: {
        source_controls: {control_id: string; source_sha256: string;
          finding_codes: string[]}[];
        family_controls: {hostile_id: string; finding_codes: string[]}[];
        runtime_proof: {process_pairs: {first_pid: number;
          second_pid: number}[]};
      };
    }).proof;
    expect(proof.source_controls.map(({control_id}) => control_id)).toEqual(
      RUST_OPERATION_SOURCE_CONTROLS.map(({control_id}) => control_id),
    );
    expect(new Set(proof.source_controls.map(({source_sha256}) =>
      source_sha256)).size).toBe(10);
    expect(proof.source_controls.every(({finding_codes}) =>
      finding_codes.length >= 1)).toBe(true);
    expect(proof.family_controls).toHaveLength(19);
    expect(proof.family_controls.every(({finding_codes}) =>
      finding_codes.length === 1)).toBe(true);
    expect(new Set(proof.runtime_proof.process_pairs.flatMap(
      ({first_pid: first, second_pid: second}) => [first, second],
    )).size).toBe(4);
    expect(await workspaceNames()).toEqual(beforeWorkspaces);
    const afterDefaultFiles = await Promise.all([
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.lock",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/lib.rs",
      "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/mod.rs",
    ].map((path) => readFile(resolve(repositoryRoot, path))));
    expect(afterDefaultFiles).toEqual(defaultFiles);
    expect(result.claim_ceiling).toContain("not arbitrary Rust");
    expect(result.claim_ceiling).toContain(
      "exactly-once distributed delivery",
    );
  }, 120_000);

  it("rejects an incoherent S1 residue through provider evaluation", async () => {
    const raw = await readRawInputs();
    const role = "hostile_15_before_state_write_failure" as const;
    const fixture = JSON.parse(raw[role]) as {
      mutation: Record<string, unknown>;
    };
    fixture.mutation.transaction_aborted = false;
    await expect(operationRustV1Provider.execute({
      raw_inputs: rebindRole(raw, role, JSON.stringify(fixture)),
      upstream: {},
    })).rejects.toMatchObject({code: "RMT_OP_S1_RESIDUE_INCOHERENT"});
  });

  it("hash-closes all 34 bound roles and the binding body", async () => {
    const baseline = await readRawInputs();
    for (const role of Object.keys(RUST_OPERATION_RAW_PATHS).filter(
      (candidate) => candidate !== "binding",
    )) {
      await expect(operationRustV1Provider.execute({
        raw_inputs: {...baseline, [role]: `${baseline[
          role as keyof RustOperationRawInputs
        ]}\n`},
        upstream: {},
      })).rejects.toThrow(`RUST_OP_BINDING_INPUT_STALE:${role}`);
    }
    const stale = JSON.parse(baseline.binding) as {binding_sha256: string};
    stale.binding_sha256 = "0".repeat(64);
    await expect(operationRustV1Provider.execute({
      raw_inputs: {...baseline, binding: JSON.stringify(stale)},
      upstream: {},
    })).rejects.toThrow("RUST_OP_BINDING_DIGEST_STALE");
  }, 30_000);

  it("rejects nested binding extras and wrong observer identity", async () => {
    const raw = await readRawInputs();
    const nested = JSON.parse(raw.binding) as {
      refs: {source: Record<string, unknown>};
    };
    nested.refs.source.oracle_hint = "forbidden";
    await expect(operationRustV1Provider.execute({
      raw_inputs: {...raw, binding: JSON.stringify(nested)},
      upstream: {},
    })).rejects.toThrow("RUST_OP_BINDING_REF_INVALID");

    const wrongObserver = JSON.parse(raw.binding) as {observer_id: string};
    wrongObserver.observer_id = "observer.untrusted/v1";
    await expect(operationRustV1Provider.execute({
      raw_inputs: {...raw, binding: JSON.stringify(wrongObserver)},
      upstream: {},
    })).rejects.toThrow("RUST_OP_BINDING_POLICY_INVALID");
  });

  it("derives current-version evidence from the target's actual guard input", async () => {
    const raw = await readRawInputs();
    for (const expectedVersion of [-1, 0]) {
      const source = raw.source.replace(
        "    let guard_allowed = ports.guard(GUARD_ID, input);",
        `    let supplied_guard_input = CompleteSettlementInput {
        settlement_id: input.settlement_id,
        expected_state_version: ${expectedVersion},
    };
    let guard_allowed = ports.guard(GUARD_ID, &supplied_guard_input);`,
      );
      expect(source).not.toBe(raw.source);
      await expect(operationRustV1Provider.execute({
        raw_inputs: rebindSource(raw, source),
        upstream: {},
      })).rejects.toThrow(/RUST_OP_TARGET_POSITIVE_BLOCKED:RMT_OP_GUARD_BYPASS/u);
    }
  }, 120_000);

  it("rejects an ignored guard while the input remains immutably borrowed", async () => {
    const raw = await readRawInputs();
    expect(raw.source).toContain("input: &CompleteSettlementInput<'_>");
    expect(raw.source).not.toContain("input: &mut CompleteSettlementInput");
    const source = raw.source.replace(
      "    if !guard_allowed {",
      "    if false && !guard_allowed {",
    );
    await expect(operationRustV1Provider.execute({
      raw_inputs: rebindSource(raw, source),
      upstream: {},
    })).rejects.toThrow(/RUST_OP_TARGET_POSITIVE_BLOCKED:RMT_OP_GUARD_BYPASS/u);
  }, 120_000);

  it("rejects surplus and missing raw input roles", async () => {
    const raw = await readRawInputs();
    await expect(operationRustV1Provider.execute({
      raw_inputs: {...raw, oracle_hint: "forbidden"},
      upstream: {},
    })).rejects.toThrow("RUST_OP_PROVIDER_INPUT_ROLES_INVALID");
    const {source: _source, ...missing} = raw;
    await expect(operationRustV1Provider.execute({
      raw_inputs: missing,
      upstream: {},
    })).rejects.toThrow("RUST_OP_PROVIDER_INPUT_ROLES_INVALID");
  });

  it("snapshots raw inputs before the first asynchronous proof edge", async () => {
    const baseline = await readRawInputs();
    const mutable = {...baseline};
    const pending = operationRustV1Provider.execute({
      raw_inputs: mutable,
      upstream: {},
    });
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({
      result: "pass",
      provider_id: "operation-rust-v1",
    });
  }, 120_000);

  it("remains unregistered without disturbing existing provider identities", () => {
    const ids = listFactoryNodeProvidersV1().map(
      ({provider_id: providerId}) => providerId,
    );
    expect(ids).not.toContain("operation-rust-v1");
    expect(ids).toContain("rust-query-v1");
    expect(() => getFactoryNodeProviderV1(
      "operation-rust-v1",
    )).toThrow("FACTORY_PROVIDER_UNKNOWN:operation-rust-v1");
    expect(getFactoryNodeProviderV1("rust-query-v1"))
      .toBe(rustQueryV1Provider);
  });

  it("rejects ambient Rust surfaces and malformed runner output", async () => {
    const source = (await readRawInputs()).source;
    for (const prefix of [
      "use std::fs;\n",
      "use std::net::TcpStream;\n",
      "static mut FORBIDDEN: i32 = 0;\n",
      "extern crate core;\n",
      "const FORBIDDEN: &str = include_str!(\"forbidden\");\n",
      "const FORBIDDEN: &str = env!(\"HOME\");\n",
    ]) {
      expect(() => inspectRustOperationClosedSubset(
        `${prefix}${source}`,
      )).toThrow("RUST_OP_CLOSED_SUBSET_SOURCE_SHAPE");
    }
    expect(() => parseRustOperationChildOutput(
      "pid\t1\ncase\tcommitted-success\n",
      "",
    )).toThrow("RUST_OP_FRESH_PROCESS_OUTPUT_INVALID");
    expect(() => parseRustOperationChildOutput("", "ambient stderr"))
      .toThrow("RUST_OP_FRESH_PROCESS_STDERR");
  });
});
