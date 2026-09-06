#!/usr/bin/env tsx
/**
 * instances.ts — DomainSpec v2 machine-generated instance tooling (MT-INST).
 *
 * Two modes over the per-meta-type schemas in spec/meta-types/:
 *   generate  — for each <type>.schema.yml, emit a canonical example instance <type>.example.instance.yml
 *               (DEF-D3 source B) that CONFORMS to the schema. Shape is normalized from the schema's
 *               required_structure + criterion — it is NOT derived (no src/rules, no δ-algorithm), so this
 *               stays the PUBLIC structural authoring aid (validators-as-moat asset #1).
 *   validate  — validate machine-generated instances against their schema's criterion (the same rules
 *               validate-content applies to markdown, applied here to structured YAML instance data).
 *
 * Usage:
 *   tsx tools/instances.ts generate [--schema-dir spec/meta-types] [--out-dir spec/__generated__/instances]
 *   tsx tools/instances.ts validate [--schema-dir spec/meta-types] [--dir <d> | --file <f>] [--mode strict|warn]
 */

import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { join, relative, resolve } from "node:path";

import {
  type Criterion,
  type CriterionSubject,
  evaluateCriteria,
  loadMetaTypeSchemas,
  type MetaTypeSchema,
  parseMetaTypeYaml,
} from "./lib/meta-type-criteria";
import {
  uiRepairViolation,
} from "./lib/ui-repair-rule-contract";

type Schema = MetaTypeSchema;

const argv = process.argv.slice(2);
const mode = argv[0];
const validateMode = getArg("--mode") || "strict";
const schemaDir = resolve(process.cwd(), getArg("--schema-dir") || "spec/meta-types");
const outDir = resolve(process.cwd(), getArg("--out-dir") || "spec/__generated__/instances");

const loadedSchemas = loadMetaTypeSchemas<Schema>(schemaDir);
const schemas = loadedSchemas.map((entry) => entry.schema);
if (schemas.length === 0) {
  console.error(`instances: no .schema.yml found under ${toRel(schemaDir)}`);
  process.exit(1);
}

if (mode === "generate") {
  runGenerate();
} else if (mode === "validate") {
  runValidate();
} else {
  console.error("instances: first arg must be 'generate' or 'validate'");
  process.exit(1);
}

// ---------------------------------------------------------------------------
// generate: schema -> canonical example instance (conforms by construction)
// ---------------------------------------------------------------------------

function runGenerate(): void {
  mkdirSync(outDir, { recursive: true });
  let count = 0;
  for (const schema of schemas) {
    const slug = schema.meta_type.trim().toLowerCase().replace(/\s+/g, "-");
    const yaml = emitInstance(buildInstance(schema));
    writeFileSync(join(outDir, `${slug}.example.instance.yml`), yaml, "utf-8");
    count += 1;
  }
  console.log(`instances: generated ${count} example instance(s) -> ${toRel(outDir)}`);
}

function buildInstance(schema: Schema): Record<string, unknown> {
  const rs = schema.required_structure || {};
  const crit = schema.criterion || {};
  const slug = schema.meta_type.trim().replace(/\s+/g, "");
  const inst: Record<string, unknown> = {
    meta_type: schema.meta_type,
    concept: `Example${slug}`,
  };

  if (rs.fields_table_columns) {
    const names = ["sample"];
    const types = ["String"];
    const identity = ["no"];
    let needIdentity = false;
    for (const c of Object.values(crit)) {
      if (c.rule === "at-least-one" && (c.column || "").toLowerCase() === "identity") {
        needIdentity = true;
      }
    }
    if (needIdentity) {
      names.unshift("id");
      types.unshift("Uuid");
      identity.unshift("yes");
    }
    // Keys are field_<column-lowercased> so the validator's `field_${column}` lookup resolves.
    inst.field_name = names;
    inst.field_type = types;
    inst.field_identity = identity;
    // section-contains criteria: emit a scalar carrying the required pattern
    for (const [name, c] of Object.entries(crit)) {
      if (c.rule === "section-contains") {
        inst[name] = `example ${inst.concept} are ${c.pattern} by fields`;
      }
    }
  } else if (rs.value_table_columns) {
    inst.values = ["ALPHA", "BETA", "GAMMA"];
  } else if (rs.attributes_table_columns) {
    const attrs: Record<string, string> = {};
    for (const [name, c] of Object.entries(crit)) {
      if (c.rule === "attribute-equals" && c.key) {
        attrs[c.key] = String(c.value ?? "");
      } else if (c.rule === "attribute-present" && c.key) {
        attrs[c.key] = `example-${c.key}`;
      } else if (c.rule === "attribute-nonempty/v1") {
        const key = (c.key || "").trim();
        if (!key) {
          throw new Error(
            uiRepairViolation(
              "ATTRIBUTE-MISSING",
              `instances: criterion '${name}': attribute-nonempty/v1 requires a non-empty 'key'`,
            ),
          );
        }
        attrs[key] = `example-${key}`;
      } else if (c.rule === "attribute-one-of") {
        const key = (c.key || "").trim();
        if (!key) {
          throw new Error(
            `instances: criterion '${name}': attribute-one-of requires a non-empty 'key'`,
          );
        }
        if (
          !Array.isArray(c.values) ||
          c.values.length === 0 ||
          c.values.some((value) => typeof value !== "string" || value.trim() === "")
        ) {
          throw new Error(
            `instances: criterion '${name}': attribute-one-of requires a non-empty 'values' string array`,
          );
        }
        attrs[key] = c.values[0]!.trim();
      }
    }
    inst.attributes = attrs;
  }
  return inst;
}

function emitInstance(inst: Record<string, unknown>): string {
  const lines: string[] = [];
  for (const [key, val] of Object.entries(inst)) {
    if (Array.isArray(val)) {
      lines.push(`${key}: [${val.join(", ")}]`);
    } else if (val && typeof val === "object") {
      lines.push(`${key}:`);
      for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
        lines.push(`  ${k}: ${String(v)}`);
      }
    } else {
      lines.push(`${key}: ${String(val)}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

// ---------------------------------------------------------------------------
// validate: instance data vs its schema criterion (shape only, no moat)
// ---------------------------------------------------------------------------

function runValidate(): void {
  const byType = new Map(
    loadedSchemas.map((entry) => [entry.schema.meta_type.toLowerCase(), entry]),
  );
  const files = resolveInstanceFiles();
  if (files.length === 0) {
    console.log("instances: no instances to validate");
    process.exit(0);
  }

  const violations: string[] = [];
  let checked = 0;
  for (const file of files) {
    const inst = parseMetaTypeYaml(readFileSync(file, "utf-8"), toRel(file));
    const metaType = typeof inst.meta_type === "string" ? inst.meta_type : "";
    const loadedSchema = byType.get(metaType.toLowerCase());
    if (!loadedSchema) {
      violations.push(`${toRel(file)} | declares meta_type '${metaType}' with no schema`);
      continue;
    }
    checked += 1;
    const subject = toCriterionSubject(file, inst);
    for (const failure of evaluateCriteria(
      loadedSchema.path,
      loadedSchema.schema.criterion,
      subject,
    )) {
      violations.push(
        `${toRel(file)} | concept=${String(inst.concept)} | ${failure.message}`,
      );
    }
  }

  if (violations.length === 0) {
    console.log(`instances: PASS (${checked} instance(s) validated; schemas=${schemas.length})`);
    process.exit(0);
  }
  for (const v of violations) {
    console.log(`[instance:${validateMode}] ${v}`);
  }
  console.log(`[instance:${validateMode}] violations=${violations.length}`);
  process.exit(validateMode === "warn" ? 0 : 1);
}

function toCriterionSubject(
  file: string,
  inst: Record<string, unknown>,
): CriterionSubject {
  const attributes = isRecord(inst.attributes)
    ? Object.entries(inst.attributes).map(([key, value]) => ({ key, value }))
    : [];
  const columns = Object.fromEntries(
    Object.entries(inst)
      .filter(([key, value]) => key.startsWith("field_") && Array.isArray(value))
      .map(([key, value]) => [key.slice("field_".length), value as unknown[]]),
  );
  const values = Array.isArray(inst.values) ? inst.values : null;
  return {
    kind: "instance",
    path: toRel(file),
    text: collectScalarText(inst).join("\n"),
    attributes,
    columns,
    table: values
      ? {
          columns: ["Value"],
          rows: values.map((value) => [value]),
        }
      : undefined,
  };
}

function resolveInstanceFiles(): string[] {
  const file = getArg("--file");
  if (file) {
    const p = resolve(process.cwd(), file);
    if (!existsSync(p)) {
      console.error(`instances: --file not found: ${file}`);
      process.exit(1);
    }
    return [p];
  }
  const dir = resolve(process.cwd(), getArg("--dir") || relative(process.cwd(), outDir));
  if (!existsSync(dir)) {
    return [];
  }
  return readdirSync(dir)
    .filter((n) => n.endsWith(".instance.yml"))
    .sort()
    .map((n) => join(dir, n));
}

// ---------------------------------------------------------------------------
// normalized-subject helpers
// ---------------------------------------------------------------------------

function collectScalarText(value: unknown): string[] {
  if (["string", "number", "boolean"].includes(typeof value)) {
    return [String(value)];
  }
  if (Array.isArray(value)) {
    return value.flatMap(collectScalarText);
  }
  if (isRecord(value)) {
    return Object.values(value).flatMap(collectScalarText);
  }
  return [];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function getArg(name: string): string | undefined {
  const idx = argv.indexOf(name);
  return idx < 0 ? undefined : argv[idx + 1];
}

function toRel(abs: string): string {
  return relative(process.cwd(), abs).replace(/\\/g, "/");
}
