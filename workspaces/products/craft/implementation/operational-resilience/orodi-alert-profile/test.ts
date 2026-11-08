import assert from "node:assert/strict";
import { resolve } from "node:path";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

import { readJson, renderGrafana, validateGrafanaBinding, validateProfile } from "./grafana-renderer";

const here = dirname(fileURLToPath(import.meta.url));
const original = readJson(resolve(here, "body-war-canary.alert-profile.json"));
const originalBinding = readJson(resolve(here, "body-war-canary.grafana-binding.json"));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value));
assert.deepEqual(validateProfile(original), []);
assert.deepEqual(validateGrafanaBinding(originalBinding), []);
const first = renderGrafana(original, originalBinding);
const second = renderGrafana(original, originalBinding);
assert.equal(first, second);
assert.equal(first, readFileSync(resolve(here, "../body-war-canary.grafana-alerts.yml"), "utf8"));

const hostile: Array<[string, (profile: any, binding: any) => void]> = [
  ["duplicate-rule", (p) => { p.rule_set.rules[1].rule_id = p.rule_set.rules[0].rule_id; }],
  ["no-data-healthy", (p) => { p.state_model.no_data_policy.attention = "healthy"; }],
  ["error-normal", (p) => { p.state_model.error_policy.evidence_state = "normal"; }],
  ["query-side-zero", (p) => { p.rule_set.rules[0].expression = "up or vector(0)"; }],
  ["control-action", (p) => { p.rule_set.rules[0].expression = "http://gateway/control/action"; }],
  ["unbounded-label", (p) => { p.rule_set.rules[0].fixed_labels.request_id = "dynamic"; }],
  ["notification-destination", (p) => { p.notification_delivery.state = "enabled"; p.notification_delivery.destinations = ["https://example.invalid"]; }],
  ["unknown-source", (p) => { p.rule_set.rules[0].source_id = "missing"; }],
  ["rule-authority", (p) => { p.rule_set.rules[0].authority_effect = "rollback"; }],
  ["external-renderer-sink", (_p, b) => { b.notification_suppression.sink = "https://example.invalid/hook"; }],
];
for (const [name, mutate] of hostile) {
  const profile = clone(original);
  const binding = clone(originalBinding);
  mutate(profile, binding);
  const errors = [...validateProfile(profile), ...validateGrafanaBinding(binding)];
  assert.ok(errors.length > 0, `hostile mutation must fail: ${name}`);
}

process.stdout.write(`${JSON.stringify({result:"pass",valid_profile_rules:original.rule_set.rules.length,deterministic_runs:2,reference_bytes_equal:true,hostile_mutations:hostile.length,notification_delivery:"absent",authority_effect:"none"}, null, 2)}\n`);
