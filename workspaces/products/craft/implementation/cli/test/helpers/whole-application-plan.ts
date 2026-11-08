import fs from "node:fs";
import path from "node:path";

import { canonicalJson } from "../../src/input/source-manifest.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";

const example = process.argv[2];
if (!example || !path.isAbsolute(example)) throw new Error("absolute example path required");
const selection = JSON.parse(fs.readFileSync(path.join(example, "selections/typescript.json"), "utf8"));
const integration = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));
const plan = planWholeApplicationV1(path.join(example, "source"), selection, integration);
process.stdout.write(`${canonicalJson({ plan_sha256: plan.plan_sha256, artifacts: plan.artifacts.map(item => ({ relative_path: item.relative_path, sha256: item.sha256 })) })}\n`);
