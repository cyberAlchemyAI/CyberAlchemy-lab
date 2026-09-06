#!/usr/bin/env node
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

import { readJson, renderGrafana, sha256, validateGrafanaBinding, validateProfile } from "./grafana-renderer";

const here = dirname(fileURLToPath(import.meta.url));
const profilePath = resolve(here, "body-war-canary.alert-profile.json");
const bindingPath = resolve(here, "body-war-canary.grafana-binding.json");
const outputPath = resolve(here, "generated/body-war-canary.grafana-alerts.yml");
const referencePath = resolve(here, "../body-war-canary.grafana-alerts.yml");
const command = process.argv[2] ?? "check";
const profile = readJson(profilePath);
const binding = readJson(bindingPath);
const errors = [...validateProfile(profile), ...validateGrafanaBinding(binding)];
if (errors.length > 0) {
  process.stderr.write(`${JSON.stringify({result:"fail",errors}, null, 2)}\n`);
  process.exit(1);
}
const rendered = renderGrafana(profile, binding);
if (command === "render") writeFileSync(outputPath, rendered, "utf8");
else if (command !== "validate" && command !== "check") throw new Error(`UNKNOWN_COMMAND:${command}`);
const reference = command === "check" ? await import("node:fs").then(({readFileSync}) => readFileSync(referencePath, "utf8")) : null;
if (reference !== null && reference !== rendered) {
  process.stderr.write(`${JSON.stringify({result:"fail",error:"REFERENCE_BYTES_DIFFER",rendered_sha256:sha256(rendered),reference_sha256:sha256(reference)}, null, 2)}\n`);
  process.exit(1);
}
process.stdout.write(`${JSON.stringify({result:"pass",command,profile_id:profile.profile_id,rules:profile.rule_set.rules.length,rendered_sha256:sha256(rendered),reference_equal:reference === null ? null : true,notification_delivery:"absent",authority_effect:"none"}, null, 2)}\n`);
