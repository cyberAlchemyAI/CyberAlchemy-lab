import fs from "node:fs";
import path from "node:path";

import { composeProviderApplicationV1 } from "../../src/generation/provider-application-v1.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";
import { canonicalJson } from "../../src/input/source-manifest.ts";

const [example, language, target] = process.argv.slice(2);
if (!example || !path.isAbsolute(example)) throw new Error("absolute example path required");
if (language !== "typescript" && language !== "python" && language !== "rust") throw new Error("supported language required");
if (!target || !path.isAbsolute(target) || fs.existsSync(target)) throw new Error("new absolute target path required");

const read = (relative: string): unknown => JSON.parse(fs.readFileSync(path.join(example, relative), "utf8"));
const whole = planWholeApplicationV1(
  path.join(example, "source"),
  read(`selections/${language}.json`) as never,
  read("integrations/application.json") as never,
);
const plan = composeProviderApplicationV1(whole, read(`providers/${language}.json`), read("integrations/application.json"));
fs.mkdirSync(target, { recursive: true });
for (const item of plan.artifacts) {
  const destination = path.join(target, item.relative_path);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, item.content);
}
process.stdout.write(`${canonicalJson({ schema_version: plan.schema_version, language: plan.language, plan_sha256: plan.plan_sha256, artifacts: plan.artifacts.length })}\n`);
