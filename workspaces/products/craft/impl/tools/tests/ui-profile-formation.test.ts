import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { loadActiveMetaTypes, parseUiProfile, validateUiProfile } from "../validate-ui-profile";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const uiSchemaRoot = resolve(implRoot, "spec/meta-types/ui");
const profilePath = resolve(implRoot, "spec/ui-profile/profile.yml");
const designPath = resolve(
  implRoot,
  "../development/ui-profile-implementation/UI-PROFILE-DESIGN.json",
);
const metaTypesPath = resolve(implRoot, "../definitions/meta-types/meta-types.yml");

const expectedNodes = [
  "Page",
  "Layout",
  "Component",
  "View Model",
  "Hook",
  "Form",
  "Action",
  "Guard",
  "Binding",
];
const neighbors = new Map([
  ["Page", "Component"],
  ["Layout", "Page"],
  ["Component", "Form"],
  ["View Model", "Value Object"],
  ["Hook", "Binding"],
  ["Form", "Component"],
  ["Action", "event handler"],
  ["Guard", "Rule"],
  ["Binding", "DS-D8 relation"],
]);

function run(tool: string, args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", tool, ...args], {
    cwd: implRoot,
    encoding: "utf8",
  });
}

function combined(result: ReturnType<typeof run>): string {
  return result.stdout + result.stderr;
}

function firstAttributeLine(body: string): string {
  return body.split("\n").find((line) => /^  [a-z_]+: /.test(line)) ?? "";
}

function mutateFirstAttribute(body: string, replacement?: string): string {
  const line = firstAttributeLine(body);
  assert.notEqual(line, "", body);
  return replacement === undefined
    ? body.replace(`${line}\n`, "")
    : body.replace(line, `${line.slice(0, line.indexOf(":") + 1)} ${replacement}`);
}

test("profile node declarations resolve to exactly nine implementation twins", () => {
  const profile = parseUiProfile(readFileSync(profilePath, "utf8"));
  const validated = validateUiProfile(profile, {
    activeMetaTypes: loadActiveMetaTypes(metaTypesPath),
    design: JSON.parse(readFileSync(designPath, "utf8")),
  });
  const nodes = validated.profile.concepts
    .filter((concept) => concept.representation === "node")
    .map((concept) => concept.term);
  assert.deepEqual(nodes, expectedNodes);

  for (const concept of validated.profile.concepts.filter(
    (entry) => entry.representation === "node",
  )) {
    assert.ok(concept.formation_contract);
    const schema = resolve(implRoot, concept.formation_contract!);
    const card = schema.replace(/\.schema\.yml$/, ".md");
    assert.equal(existsSync(schema), true, schema);
    assert.equal(existsSync(card), true, card);
    assert.match(readFileSync(card, "utf8"), new RegExp(`^# ${concept.term}$`, "m"));
  }
});

test("ported schemas use nonempty semantics and retain a closed nine-type census", () => {
  const schemas = readdirSync(uiSchemaRoot)
    .filter((name) => name.endsWith(".schema.yml"))
    .sort();
  const cards = readdirSync(uiSchemaRoot).filter((name) => name.endsWith(".md")).sort();
  assert.equal(schemas.length, 9);
  assert.equal(cards.length, 9);

  const raw = schemas.map((name) => readFileSync(join(uiSchemaRoot, name), "utf8")).join("\n");
  assert.equal((raw.match(/rule: attribute-nonempty\/v1/g) ?? []).length, 43);
  assert.equal((raw.match(/rule: attribute-present/g) ?? []).length, 0);
  assert.equal((raw.match(/authority_boundary: implementation-owned development profile only/g) ?? []).length, 9);
});

test("all nine generated instances round-trip through the existing instance tool", () => {
  const out = mkdtempSync(join(tmpdir(), "domainspec-ui-instances-"));
  try {
    const generate = run("tools/instances.ts", [
      "generate",
      "--schema-dir",
      "spec/meta-types/ui",
      "--out-dir",
      out,
    ]);
    assert.equal(generate.status, 0, combined(generate));
    assert.match(generate.stdout, /generated 9 example instance/);
    const validate = run("tools/instances.ts", [
      "validate",
      "--schema-dir",
      "spec/meta-types/ui",
      "--dir",
      out,
    ]);
    assert.equal(validate.status, 0, combined(validate));
    assert.match(validate.stdout, /PASS \(9 instance\(s\) validated; schemas=9\)/);
  } finally {
    rmSync(out, { recursive: true, force: true });
  }
});

test("each UI node rejects missing, empty, whitespace, and nearest-neighbor mutations", () => {
  const generated = mkdtempSync(join(tmpdir(), "domainspec-ui-generated-"));
  const mutants = mkdtempSync(join(tmpdir(), "domainspec-ui-mutants-"));
  try {
    const generate = run("tools/instances.ts", [
      "generate",
      "--schema-dir",
      "spec/meta-types/ui",
      "--out-dir",
      generated,
    ]);
    assert.equal(generate.status, 0, combined(generate));

    for (const name of readdirSync(generated).filter((entry) => entry.endsWith(".instance.yml"))) {
      const body = readFileSync(join(generated, name), "utf8");
      const metaType = body.match(/^meta_type: (.+)$/m)?.[1] ?? "";
      assert.ok(expectedNodes.includes(metaType), metaType);
      const cases = [
        ["missing", mutateFirstAttribute(body), "ATTRIBUTE-MISSING"],
        ["empty", mutateFirstAttribute(body, '\"\"'), "ATTRIBUTE-EMPTY"],
        ["whitespace", mutateFirstAttribute(body, '\"   \"'), "ATTRIBUTE-WHITESPACE"],
        [
          "neighbor",
          body.replace(/^meta_type: .+$/m, `meta_type: ${neighbors.get(metaType)}`),
          "criterion|declares meta_type",
        ],
      ] as const;
      for (const [kind, mutant, expected] of cases) {
        const path = join(mutants, `${name}.${kind}.instance.yml`);
        writeFileSync(path, mutant, "utf8");
        const result = run("tools/instances.ts", [
          "validate",
          "--schema-dir",
          "spec/meta-types/ui",
          "--file",
          path,
        ]);
        assert.equal(result.status, 1, `${metaType}/${kind}: ${combined(result)}`);
        assert.match(combined(result), new RegExp(expected), `${metaType}/${kind}`);
      }
    }
  } finally {
    rmSync(generated, { recursive: true, force: true });
    rmSync(mutants, { recursive: true, force: true });
  }
});

test("fixed-value mutation rejects with a distinct code", () => {
  const out = mkdtempSync(join(tmpdir(), "domainspec-ui-fixed-"));
  try {
    assert.equal(
      run("tools/instances.ts", [
        "generate",
        "--schema-dir",
        "spec/meta-types/ui",
        "--out-dir",
        out,
      ]).status,
      0,
    );
    const page = join(out, "page.example.instance.yml");
    const mutant = readFileSync(page, "utf8").replace("terminal: true", "terminal: false");
    writeFileSync(page, mutant, "utf8");
    const result = run("tools/instances.ts", [
      "validate",
      "--schema-dir",
      "spec/meta-types/ui",
      "--file",
      page,
    ]);
    assert.equal(result.status, 1, combined(result));
    assert.match(combined(result), /FIXED-VALUE-MISMATCH/);
  } finally {
    rmSync(out, { recursive: true, force: true });
  }
});

test("Adapter and State Indicator placement contracts match the profile without emitting node schemas", () => {
  const profile = parseUiProfile(readFileSync(profilePath, "utf8"));
  const adapter = JSON.parse(
    readFileSync(resolve(implRoot, "spec/ui-profile/concepts/adapter.yml"), "utf8"),
  ) as any;
  const state = JSON.parse(
    readFileSync(resolve(implRoot, "spec/ui-profile/concepts/state-indicator.yml"), "utf8"),
  ) as any;
  const adapterProfile = profile.concepts.find((concept) => concept.id === "DS-D1.24")!;
  const stateProfile = profile.concepts.find((concept) => concept.id === "DS-D1.25")!;

  assert.equal(adapter.representation, "alias");
  assert.deepEqual(
    { id: adapter.canonical_target.id, term: adapter.canonical_target.term },
    adapterProfile.canonical_target,
  );
  assert.equal(adapter.specialization.canonical_kind_emitted, "Mapping");
  assert.equal(existsSync(resolve(uiSchemaRoot, "adapter.schema.yml")), false);
  assert.equal(state.representation, "split");
  assert.deepEqual(
    state.branches.map((branch: any) => branch.branch_id),
    stateProfile.branches!.map((branch) => branch.branch_id),
  );
  assert.equal(existsSync(resolve(uiSchemaRoot, "state-indicator.schema.yml")), false);
  assert.deepEqual(
    [adapter, state].flatMap((contract) =>
      contract.relationship_residue.map((entry: any) => entry.relationship),
    ),
    ["shapes", "reflects"],
  );
});

test("authority-resolved pairwise non-collapse still passes with UI schemas installed", () => {
  const result = run("tools/validate-meta-types-noncollapse.ts", ["--report"]);
  assert.equal(result.status, 0, combined(result));
  assert.match(result.stdout, /22 meta-types, 231 pairs/);
  assert.match(result.stdout, /collapse-candidate\(s\): none/);
});
