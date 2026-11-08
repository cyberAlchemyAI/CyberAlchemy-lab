#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { digest, json } from "../src/domainspec-profile.js";
import { wholeApplicationFixture } from "../test/fixtures/application-whole-fixture.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const targetRoot = path.join(root, "examples/application-v1");
const languages = ["typescript", "python", "rust"] as const;
const profile = {
  typescript: "CommerceRuntime",
  python: "CommerceRuntimePython",
  rust: "CommerceRuntimeRust",
} as const;

function write(rootDirectory: string, relative: string, bytes: string | Buffer) {
  const target = path.join(rootDirectory, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, bytes);
  return {
    path: relative,
    sha256: digest(bytes),
    size_bytes: Buffer.byteLength(bytes),
    current: true,
  };
}

async function materialize(output: string): Promise<void> {
  for (const language of languages) {
    const fixture = await wholeApplicationFixture(`provider-selection:reference-${language}`, false, true, language);
    const languageRoot = path.join(output, language);
    write(languageRoot, "commerce.alch", fixture.source);
    const manifest: Record<string, unknown> = {
      schema_version: "alchlang.application-file/v1-candidate",
      source_sha256: digest(fixture.source),
      bindings: write(languageRoot, "inputs/bindings.json", json(fixture.bindings)),
      interpretation: write(languageRoot, "inputs/interpretation.json", json(fixture.interpretation)),
      execution: write(languageRoot, "inputs/execution.json", json(fixture.execution)),
      evidence: [...fixture.sources].map(([name, bytes]) => write(languageRoot, name, bytes)),
      runtime_profile: profile[language],
      observation: write(languageRoot, "inputs/observation.json", json(fixture.observation)),
    };
    write(languageRoot, "commerce.alch.application.json", json(manifest));
  }
  write(output, "README.md", `# application-v1 installed examples\n\nThese three directories bind the same authored application to explicit TypeScript, Python, and Rust runtime profiles. Use the commands in the package-root \`CLEAN-CONSUMER.md\`. The files are deterministic synthetic construction fixtures; they contain no credentials, production decisions, or authority effects.\n\n## Open Questions\n\nP03 owns freezing an exact candidate from the passing P02 reports.\n`);
}

function inventory(directory: string, prefix = ""): Array<{ path: string; sha256: string }> {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const relative = path.posix.join(prefix, entry.name);
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`APPLICATION_V1_EXAMPLE_SYMLINK:${relative}`);
    return entry.isDirectory() ? inventory(absolute, relative) : [{
      path: relative,
      sha256: crypto.createHash("sha256").update(fs.readFileSync(absolute)).digest("hex"),
    }];
  }).sort((left, right) => left.path.localeCompare(right.path));
}

const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-application-v1-examples-"));
try {
  await materialize(temporary);
  if (process.argv.includes("--write")) {
    if (!fs.existsSync(targetRoot)) {
      fs.cpSync(temporary, targetRoot, { recursive: true, errorOnExist: true, force: false });
    } else {
      const actual = inventory(targetRoot);
      const expected = inventory(temporary);
      if (JSON.stringify(actual.map(item => item.path)) !== JSON.stringify(expected.map(item => item.path))) {
        throw new Error("APPLICATION_V1_EXAMPLE_PATH_DRIFT: review added or missing files before writing");
      }
      for (const [index, item] of expected.entries()) {
        if (actual[index]!.sha256 !== item.sha256) {
          fs.copyFileSync(path.join(temporary, item.path), path.join(targetRoot, item.path));
        }
      }
    }
  } else if (process.argv.includes("--check")) {
    if (!fs.existsSync(targetRoot) || JSON.stringify(inventory(targetRoot)) !== JSON.stringify(inventory(temporary))) {
      throw new Error("APPLICATION_V1_EXAMPLE_DRIFT: run the materializer with --write and review the exact diff");
    }
  } else {
    process.stdout.write(`${JSON.stringify(inventory(temporary), null, 2)}\n`);
  }
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
