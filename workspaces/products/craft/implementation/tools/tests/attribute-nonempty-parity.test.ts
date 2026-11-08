import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../");
const vectors = JSON.parse(
  readFileSync(
    resolve(implRoot, "../development/ui-meta-type-repair/fixtures/contracts/attribute-nonempty-v1-vectors.json"),
    "utf8",
  ),
) as {
  vectors: Array<{
    id: string;
    markdown_row: string | null;
    instance_line: string | null;
    code: string | null;
    markdown_representable: boolean;
  }>;
};

const SCHEMA = [
  "meta_type: Nonempty Probe",
  "required_structure:",
  "  attributes_table_columns: [Attribute, Value]",
  "criterion:",
  "  label_text:",
  "    rule: attribute-nonempty/v1",
  "    key: label",
  "",
].join("\n");

function run(tool: string, args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", tool, ...args], {
    cwd: implRoot,
    encoding: "utf8",
  });
}

function markdown(row: string): string {
  return [
    "# fixture",
    "",
    "## Concept Registry",
    "| Concept | Type |",
    "| --- | --- |",
    "| Probe | Nonempty Probe |",
    "",
    "## Probe",
    "| Attribute | Value |",
    "| --- | --- |",
    row,
    "",
  ].join("\n");
}

function instance(attributeLine?: string): string {
  return [
    "meta_type: Nonempty Probe",
    "concept: Probe",
    ...(attributeLine === undefined ? [] : ["attributes:", `  ${attributeLine}`]),
    "",
  ].join("\n");
}

function combined(result: ReturnType<typeof run>): string {
  return result.stdout + result.stderr;
}

test("attribute-nonempty/v1 generation is deterministic and round-trips", () => {
  const schemaDir = mkdtempSync(join(tmpdir(), "uir-nonempty-schema-"));
  const outDir = mkdtempSync(join(tmpdir(), "uir-nonempty-out-"));
  try {
    writeFileSync(join(schemaDir, "nonempty.schema.yml"), SCHEMA, "utf8");
    const first = run("tools/instances.ts", ["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(first.status, 0, combined(first));
    const generated = join(outDir, "nonempty-probe.example.instance.yml");
    const body = readFileSync(generated, "utf8");
    assert.match(body, /label: example-label/);
    const second = run("tools/instances.ts", ["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(second.status, 0, combined(second));
    assert.equal(readFileSync(generated, "utf8"), body);
    const validated = run("tools/instances.ts", ["validate", "--schema-dir", schemaDir, "--file", generated]);
    assert.equal(validated.status, 0, combined(validated));
  } finally {
    rmSync(schemaDir, { recursive: true, force: true });
    rmSync(outDir, { recursive: true, force: true });
  }
});

for (const vector of vectors.vectors.filter((entry) => entry.markdown_representable)) {
  test(`attribute-nonempty/v1 outcome/code parity: ${vector.id}`, () => {
    const dir = mkdtempSync(join(tmpdir(), "uir-nonempty-parity-"));
    try {
      const schema = join(dir, "nonempty.schema.yml");
      const aspect = join(dir, "aspect.md");
      const instanceFile = join(dir, "probe.instance.yml");
      writeFileSync(schema, SCHEMA, "utf8");
      writeFileSync(aspect, markdown(vector.markdown_row!), "utf8");
      writeFileSync(instanceFile, instance(vector.instance_line ?? undefined), "utf8");

      const markdownResult = run("tools/validate-content.ts", ["--schema-dir", dir, "--file", aspect]);
      const instanceResult = run("tools/instances.ts", ["validate", "--schema-dir", dir, "--file", instanceFile]);
      assert.equal(markdownResult.status, instanceResult.status, combined(markdownResult) + combined(instanceResult));
      if (vector.code === null) {
        assert.equal(markdownResult.status, 0, combined(markdownResult));
      } else {
        assert.equal(markdownResult.status, 1, combined(markdownResult));
        assert.match(combined(markdownResult), new RegExp(`ui-repair-violations/v1:${vector.code}`));
        assert.match(combined(instanceResult), new RegExp(`ui-repair-violations/v1:${vector.code}`));
      }
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}

test("attribute-nonempty/v1 rejects non-string instance values", () => {
  const dir = mkdtempSync(join(tmpdir(), "uir-nonempty-nonstring-"));
  try {
    const schema = join(dir, "nonempty.schema.yml");
    const file = join(dir, "probe.instance.yml");
    writeFileSync(schema, SCHEMA, "utf8");
    const vector = vectors.vectors.find((entry) => entry.id === "non-string")!;
    assert.equal(vector.markdown_representable, false);
    writeFileSync(file, instance(vector.instance_line ?? undefined), "utf8");
    const result = run("tools/instances.ts", ["validate", "--schema-dir", dir, "--file", file]);
    assert.equal(result.status, 1, combined(result));
    assert.match(combined(result), new RegExp(`ui-repair-violations/v1:${vector.code}`));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("unknown attribute-nonempty version fails both paths before execution", () => {
  const dir = mkdtempSync(join(tmpdir(), "uir-nonempty-version-"));
  try {
    const schema = join(dir, "nonempty.schema.yml");
    const aspect = join(dir, "aspect.md");
    const instanceFile = join(dir, "probe.instance.yml");
    writeFileSync(schema, SCHEMA.replace("attribute-nonempty/v1", "attribute-nonempty/v2"), "utf8");
    writeFileSync(aspect, markdown("| label | hello |"), "utf8");
    writeFileSync(instanceFile, instance("label: hello"), "utf8");
    for (const result of [
      run("tools/validate-content.ts", ["--schema-dir", dir, "--file", aspect]),
      run("tools/instances.ts", ["validate", "--schema-dir", dir, "--file", instanceFile]),
    ]) {
      assert.equal(result.status, 1, combined(result));
      assert.match(combined(result), /ui-repair-violations\/v1:UNKNOWN-RULE/);
      assert.match(combined(result), /attribute-nonempty\/v2/);
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
