import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { projectTypeScriptEnum } from "../../adapter/enum/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const shared = {
  repositoryRoot,
  exportName: "OrderStatus",
  subjectRef: "enum.order.status",
  conceptId: "domain.order.Status",
  expectedValues: ["draft", "active", "closed"],
  profilePath:
    "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
  providerPath:
    "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
  profileActivationReceiptPath:
    "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/SWU-APE-ENUM-TS-001A.json",
} as const;

describe("TypeScript Enum observation adapter", () => {
  it("projects the admitted provider-bound const object with exact provenance", async () => {
    const projection = await projectTypeScriptEnum({
      ...shared,
      sourcePath:
        "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter-tests/enum/fixtures/order-status.ts",
    });

    expect(projection.authority_effect).toBe("none");
    expect(projection.diagnostics).toEqual([]);
    expect(projection.tool.version).toMatch(/^5\./);
    expect(projection.raw_evidence_refs).toHaveLength(3);
    expect(
      projection.facts.find(({ predicate_ref }) => predicate_ref === "enum.implemented_values")?.value,
    ).toEqual(["active", "closed", "draft"]);
    expect(
      projection.facts.find(({ predicate_ref }) => predicate_ref === "representation.protocol_id")?.value,
    ).toBe("typescript.owned-const-object-enum/v1");
    expect(
      projection.facts.every(({ provenance }) =>
        ["observed", "owner-resolved"].includes(String((provenance as { kind: string }).kind))
      ),
    ).toBe(true);
  });

  it("types a native enum as unsupported without inventing absent facts", async () => {
    const projection = await projectTypeScriptEnum({
      ...shared,
      sourcePath:
        "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter-tests/enum/fixtures/native-status.ts",
      exportName: "NativeStatus",
    });

    expect(projection.facts).toHaveLength(1);
    expect(projection.facts[0]?.value).toBeNull();
    expect((projection.facts[0]?.provenance as { kind: string }).kind).toBe("unsupported");
    expect(projection.diagnostics[0]?.code).toBe("TS_ENUM_PROVIDER_BINDING_UNSUPPORTED");
  });

  it("blocks a stale provider digest before parsing source", async () => {
    await expect(
      projectTypeScriptEnum({
        ...shared,
        providerPath:
          "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter-tests/enum/fixtures/native-status.ts",
        sourcePath:
          "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter-tests/enum/fixtures/order-status.ts",
      }),
    ).rejects.toMatchObject({
      code: "ADAPTER_PROVIDER_PATH_MISMATCH",
    });
  });

  it("blocks the former 001A versus 001B activation-binding mismatch", async () => {
    await expect(projectTypeScriptEnum({
      ...shared,
      sourcePath:
        "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter-tests/enum/fixtures/order-status.ts",
      profileActivationReceiptPath:
        "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/SWU-APE-ENUM-TS-001B.json",
    })).rejects.toMatchObject({ code: "ADAPTER_ACTIVATION_BINDING_MISMATCH" });
  });
});
