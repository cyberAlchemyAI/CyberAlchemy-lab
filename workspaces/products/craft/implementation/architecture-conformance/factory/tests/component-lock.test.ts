import { mkdir, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import { getFactoryNodeProviderV1 } from "../registry/factory-node-registry-v1.js";
import { runLockedChild } from "../replay/run-locked-child.js";
import { resolveFactoryComponentClosure } from
  "../resolution/resolve-component-closure.js";

const fixtureRoot =
  "projects/domainspec-v2/impl/architecture-conformance/kernel/testing/fixtures/provider-firewalls/component-closure";
const temporaryRoots: string[] = [];

afterEach(async () => Promise.all(temporaryRoots.splice(0)
  .map((root) => rm(root, { recursive: true, force: true }))));

const fixture = (path: string): string => `${fixtureRoot}/${path}`;

describe("factory component closure", () => {
  it("follows runtime imports, re-exports, side effects, literal dynamic edges, and cycles", async () => {
    const positive = await resolveFactoryComponentClosure({
      repositoryRoot,
      rootPaths: [fixture("positive/root.ts")],
    });
    expect(positive).toEqual(expect.arrayContaining([
      fixture("positive/root.ts"),
      fixture("positive/second.ts"),
      fixture("positive/barrel.ts"),
      fixture("positive/side-effect.ts"),
      fixture("positive/dynamic-literal.ts"),
    ]));
    expect(positive).not.toContain(fixture("positive/type-only.ts"));
    expect(positive).toEqual([...positive].sort((left, right) =>
      Buffer.from(left).compare(Buffer.from(right))));

    const cycle = await resolveFactoryComponentClosure({
      repositoryRoot,
      rootPaths: [fixture("cycle/a.ts")],
    });
    expect(cycle).toEqual([
      fixture("cycle/a.ts"),
      fixture("cycle/b.ts"),
    ]);
  });

  it.each([
    ["hostile/unresolved.ts", "FACTORY_COMPONENT_IMPORT_UNRESOLVED"],
    ["hostile/ambiguous.ts", "FACTORY_COMPONENT_IMPORT_AMBIGUOUS"],
    ["hostile/dynamic-relative.ts", "FACTORY_COMPONENT_DYNAMIC_IMPORT_UNSUPPORTED"],
  ])("blocks %s with %s", async (path, code) => {
    await expect(resolveFactoryComponentClosure({
      repositoryRoot,
      rootPaths: [fixture(path)],
    })).rejects.toMatchObject({ code });
  });

  it("blocks path escape, symlink traversal, and duplicate roots", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "domainspec-component-closure-"));
    temporaryRoots.push(root);
    await mkdir(resolve(root, "src"));
    await writeFile(resolve(root, "src/escape.ts"),
      'import "../../outside.js";\n', "utf8");
    await expect(resolveFactoryComponentClosure({
      repositoryRoot: root,
      rootPaths: ["src/escape.ts"],
    })).rejects.toMatchObject({ code: "FACTORY_COMPONENT_PATH_ESCAPE" });

    await writeFile(resolve(root, "src/target.ts"), "export const value = 1;\n", "utf8");
    await symlink("target.ts", resolve(root, "src/link.js"));
    await writeFile(resolve(root, "src/symlink.ts"), 'import "./link.js";\n', "utf8");
    await expect(resolveFactoryComponentClosure({
      repositoryRoot: root,
      rootPaths: ["src/symlink.ts"],
    })).rejects.toMatchObject({ code: "FACTORY_COMPONENT_SYMLINK" });

    await expect(resolveFactoryComponentClosure({
      repositoryRoot,
      rootPaths: [fixture("positive/root.ts"), fixture("positive/root.ts")],
    })).rejects.toMatchObject({ code: "FACTORY_COMPONENT_ROOT_INVALID" });
  });

  it("makes the production planner lock the exact transitive set", async () => {
    const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
    ), "utf8")));
    const plan = await planFactoryRun({ repositoryRoot, request });
    const locked = plan.lock.nodes[0]!;
    const provider = getFactoryNodeProviderV1(locked.provider_id);
    const expected = await resolveFactoryComponentClosure({
      repositoryRoot,
      rootPaths: provider.component_paths,
    });
    const observed = locked.components.map(({ path }) => path);
    expect(observed).toEqual(expected);
    expect(observed).toContain(
      "projects/domainspec-v2/impl/architecture-conformance/kernel/contracts/validated-handle.ts",
    );
    expect(observed.length).toBeGreaterThan(provider.component_paths.length);
  }, 70_000);

  it("makes replay reject a lock with one transitive component omitted", async () => {
    const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
    ), "utf8")));
    const plan = await planFactoryRun({ repositoryRoot, request });
    const locked = plan.lock.nodes[0]!;
    const omittedPath =
      "projects/domainspec-v2/impl/architecture-conformance/kernel/contracts/validated-handle.ts";
    expect(locked.components.some(({ path }) => path === omittedPath)).toBe(true);
    const omittedNode = Object.freeze({
      ...locked,
      components: Object.freeze(locked.components.filter(({ path }) => path !== omittedPath)),
    });
    const omittedLock = Object.freeze({
      ...plan.lock,
      nodes: Object.freeze([omittedNode]),
    });
    const rawInputs = Object.fromEntries(await Promise.all(locked.inputs.map(async ({ role, path }) =>
      [role, await readFile(resolve(repositoryRoot, path), "utf8")])));
    const scratchRoot = await mkdtemp(resolve(tmpdir(), "domainspec-component-replay-"));
    temporaryRoots.push(scratchRoot);
    await expect(runLockedChild({
      scratchRoot,
      nodeId: locked.node_id,
      providerId: locked.provider_id,
      rawInputs,
      upstream: Object.freeze({}),
      lock: omittedLock,
    })).rejects.toMatchObject({
      code: "FACTORY_REPLAY_CHILD_FAILED",
      detail: expect.stringContaining("FACTORY_REPLAY_PROVIDER_IDENTITY_MISMATCH"),
    });
  }, 70_000);
});
