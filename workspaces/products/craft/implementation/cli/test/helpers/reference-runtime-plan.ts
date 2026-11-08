import fs from "node:fs";
import path from "node:path";

import { planReferenceRuntimeV1 } from "../../src/generation/reference-runtime-v1.ts";
import { composeProviderApplicationV1 } from "../../src/generation/provider-application-v1.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";
import { canonicalJson } from "../../src/input/source-manifest.ts";

const [example, target] = process.argv.slice(2);
if (!example || !path.isAbsolute(example)) throw new Error("absolute example path required");
if (!target || !path.isAbsolute(target) || fs.existsSync(target)) throw new Error("new absolute target path required");
const read = (relative: string): unknown => JSON.parse(fs.readFileSync(path.join(example, relative), "utf8"));
const whole = planWholeApplicationV1(path.join(example, "source"), read("selections/typescript.json") as never, read("integrations/application.json") as never);
const provider = composeProviderApplicationV1(whole, read("providers/typescript.json"), read("integrations/application.json"));
const plan = planReferenceRuntimeV1(provider);
fs.mkdirSync(target, { recursive: true });
for (const item of plan.artifacts) {
  const destination = path.join(target, item.relative_path);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, item.content);
}
process.stdout.write(`${canonicalJson({ schema_version: plan.schema_version, plan_sha256: plan.plan_sha256, provider_application_plan_sha256: plan.provider_application_plan_sha256, artifacts: plan.artifacts.length })}\n`);
