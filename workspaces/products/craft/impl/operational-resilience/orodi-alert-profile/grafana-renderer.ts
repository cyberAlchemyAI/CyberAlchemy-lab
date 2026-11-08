import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

export type JsonObject = Record<string, any>;

const STATES = ["normal", "pending", "firing", "no_data", "error"];
const FORBIDDEN_QUERY = ["vector(0)", "/control/action", "authorization", "http://", "https://"];
const FORBIDDEN_LABELS = ["request_id", "timestamp", "token", "secret", "authorization", "user"];

export const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");

export function validateProfile(profile: JsonObject): string[] {
  const errors: string[] = [];
  if (profile.schema_version !== "cav2.orodi.alert-profile-instance/v1-candidate") errors.push("schema-version");
  if (profile.authority_effect !== "none") errors.push("authority-effect");
  if (JSON.stringify(profile.state_model?.states) !== JSON.stringify(STATES)) errors.push("state-model");
  if (profile.state_model?.no_data_policy?.evidence_state !== "no_data" || profile.state_model?.no_data_policy?.attention !== "fail-closed") errors.push("no-data-policy");
  if (profile.state_model?.error_policy?.evidence_state !== "error" || profile.state_model?.error_policy?.attention !== "fail-closed") errors.push("error-policy");
  const separation = new Set(profile.state_model?.separation_invariants ?? []);
  for (const invariant of ["no_data is not normal", "error is not normal", "no_data is not error", "firing is not proof of causation", "shared attention policy does not collapse evidence meaning"]) {
    if (!separation.has(invariant)) errors.push(`state-separation:${invariant}`);
  }
  if (profile.notification_delivery?.state !== "absent" || profile.notification_delivery?.destinations?.length !== 0 || profile.notification_delivery?.credential_refs?.length !== 0 || profile.notification_delivery?.separate_binding_required !== true) errors.push("notification-delivery");

  const sources = new Set<string>();
  for (const source of profile.source_contracts ?? []) {
    if (!source.source_id || sources.has(source.source_id)) errors.push(`source-id:${source.source_id}`);
    sources.add(source.source_id);
    if (source.query_language !== "promql") errors.push(`query-language:${source.source_id}`);
    if (!(source.conservation_obligations ?? []).includes("missing telemetry remains missing")) errors.push(`source-conservation:${source.source_id}`);
  }
  const allowedKeys = new Set<string>((profile.label_contract?.allowed_keys ?? []).map(String));
  if (allowedKeys.size === 0) errors.push("label-contract-empty");
  for (const key of allowedKeys) if (FORBIDDEN_LABELS.some((token) => key.toLowerCase().includes(token))) errors.push(`label-key:${key}`);

  const rules = profile.rule_set?.rules ?? [];
  const ruleIds = new Set<string>();
  if (rules.length === 0) errors.push("rule-set-empty");
  for (const rule of rules) {
    if (!rule.rule_id || ruleIds.has(rule.rule_id)) errors.push(`rule-id:${rule.rule_id}`);
    ruleIds.add(rule.rule_id);
    if (!sources.has(rule.source_id)) errors.push(`rule-source:${rule.rule_id}`);
    if (rule.authority_effect !== "none") errors.push(`rule-authority:${rule.rule_id}`);
    if (!['lt', 'gt'].includes(rule.predicate?.operator) || typeof rule.predicate?.threshold !== "number") errors.push(`predicate:${rule.rule_id}`);
    const expression = String(rule.expression ?? "").toLowerCase().replaceAll(" ", "");
    for (const token of FORBIDDEN_QUERY) if (expression.includes(token.replaceAll(" ", ""))) errors.push(`query-forbidden:${rule.rule_id}:${token}`);
    const labels = rule.fixed_labels ?? {};
    if (Object.keys(labels).some((key) => !allowedKeys.has(key))) errors.push(`rule-label-key:${rule.rule_id}`);
    for (const [key, value] of Object.entries(labels)) {
      if (!(profile.label_contract?.allowed_values?.[key] ?? []).includes(value)) errors.push(`rule-label-value:${rule.rule_id}:${key}`);
    }
    if (!/^\d+s$/.test(rule.evaluation_interval ?? "") || !/^\d+s$/.test(rule.persistence_duration ?? "")) errors.push(`rule-duration:${rule.rule_id}`);
  }
  return [...new Set(errors)].sort();
}

export function validateGrafanaBinding(binding: JsonObject): string[] {
  const errors: string[] = [];
  if (binding.schema_version !== "cav2.orodi.alert-profile.grafana-binding/v1-candidate") errors.push("binding-schema");
  if (binding.platform !== "grafana-file-provisioning") errors.push("binding-platform");
  if (binding.external_delivery !== "disabled" || binding.authority_effect !== "none") errors.push("binding-authority");
  const suppression = binding.notification_suppression ?? {};
  if (suppression.mode !== "always-muted-container-loopback") errors.push("binding-suppression");
  if (suppression.sink !== "http://127.0.0.1:9/orodi-disabled") errors.push("binding-sink");
  return errors.sort();
}

const yamlSingle = (value: string): string => `'${value.replaceAll("'", "''")}'`;

export function renderGrafana(profile: JsonObject, binding: JsonObject): string {
  assert.deepEqual(validateProfile(profile), []);
  assert.deepEqual(validateGrafanaBinding(binding), []);
  const lines: string[] = [
    "apiVersion: 1",
    "groups:",
    `  - orgId: ${binding.org_id}`,
    `    name: ${binding.group_name}`,
    `    folder: ${binding.folder}`,
    `    interval: ${binding.evaluation_interval}`,
    "    rules:",
  ];
  for (const rule of profile.rule_set.rules) {
    lines.push(
      `      - uid: ${rule.rule_id}`,
      `        title: ${rule.title}`,
      "        condition: C",
      "        data:",
      "          - refId: A",
      `            relativeTimeRange: {from: ${rule.relative_from_seconds}, to: 0}`,
      `            datasourceUid: ${binding.datasource_uid}`,
      "            model:",
      "              editorMode: code",
      `              expr: ${yamlSingle(rule.expression)}`,
      "              instant: true",
      `              intervalMs: ${binding.query_interval_ms}`,
      `              maxDataPoints: ${binding.max_data_points}`,
      "              range: false",
      "              refId: A",
      "          - refId: C",
      "            datasourceUid: __expr__",
      "            model:",
      "              conditions:",
      `                - evaluator: {params: [${rule.predicate.threshold}], type: ${rule.predicate.operator}}`,
      "                  operator: {type: and}",
      "                  query: {params: [C]}",
      "                  reducer: {params: [], type: last}",
      "                  type: query",
      "              datasource: {type: __expr__, uid: __expr__}",
      "              expression: A",
      `              intervalMs: ${binding.query_interval_ms}`,
      `              maxDataPoints: ${binding.max_data_points}`,
      "              refId: C",
      "              type: threshold",
      "        noDataState: Alerting",
      "        execErrState: Alerting",
      `        for: ${rule.persistence_duration}`,
      "        annotations:",
      `          summary: ${rule.annotations.summary}`,
      `          evidence_boundary: ${rule.annotations.evidence_boundary}`,
      `        labels: {authority: ${rule.fixed_labels.authority}, severity: ${rule.fixed_labels.severity}, scope: ${rule.fixed_labels.scope}}`,
      "        notification_settings:",
      `          receiver: ${binding.notification_suppression.receiver}`,
      "          group_by: ['...']",
      `          mute_time_intervals: [${binding.notification_suppression.mute_interval}]`,
      "        isPaused: false",
    );
  }
  lines.push(
    "muteTimes:",
    `  - orgId: ${binding.org_id}`,
    `    name: ${binding.notification_suppression.mute_interval}`,
    "    time_intervals:",
    "      - times:",
    "          - start_time: '00:00'",
    "            end_time: '24:00'",
    "        weekdays: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']",
    "contactPoints:",
    `  - orgId: ${binding.org_id}`,
    `    name: ${binding.notification_suppression.receiver}`,
    "    receivers:",
    `      - uid: ${binding.notification_suppression.receiver_uid}`,
    "        type: webhook",
    "        disableResolveMessage: true",
    "        settings:",
    `          url: ${binding.notification_suppression.sink}`,
  );
  return `${lines.join("\n")}\n`;
}

export const readJson = (path: string): JsonObject => JSON.parse(readFileSync(path, "utf8"));
