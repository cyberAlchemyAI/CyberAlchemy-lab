import { createHash } from "node:crypto";

const hashes = Object.freeze({
  base: "721921afea3755fb8ceff7ce83990612f92c587db6ab85c2f9f34306bdb71d5a",
  String: "5f5ddcf6c95702e208e895daf223c300a6a1f5e3c62a8d403993763d70a4ee92",
  Bool: "88473c308b130c2722acc7fa6ad00ac761466ef5c9b9c9173f63190a3aea99c1",
  UInt64: "a9c4216cd67ed445807e68b01de62748040d4e9cbd2d18165908b95967e98c2f",
  optional: "ae9ea53bb75c59c502cfb5824711cb91a67957d3d00e1a09ba23e2ac3c8e8253",
  sequence: "565ce7166db2618dce3b0d894b649e39da6d523cd71a1cf7f8be3d22afec33d4",
  "to-set": "bbd1e33e63dff1b51fb1d4200dbc29457ca4c6fd346e6199a8ce7eaacff00584",
  sum: "f6c1aeeb43b6affbc93899769f776bf909f10a2c86769c2a0b734ce105460108",
});
const order = Object.keys(hashes);
const helpers = Object.freeze({ String: "ruleString", Bool: "ruleBool", UInt64: "ruleUInt64", optional: "ruleOptional", sequence: "ruleSequence", "to-set": "ruleToSet", sum: "ruleSum" });
const digest = value => createHash("sha256").update(value).digest("hex");

export function validStructuredRuleSupport(raw) {
  const marker = "// end structured Rule support\n";
  const start = raw.indexOf("// structured-rule-capability:base\n");
  const end = raw.indexOf(marker);
  if (start < 0 || end < start) return false;
  const normalized = raw.slice(start, end)
    .replaceAll("MAPPING_INPUT", "RULE_INPUT")
    .replaceAll("POLICY_INPUT", "RULE_INPUT")
    .replaceAll("QUERY_INPUT", "RULE_INPUT")
    .replaceAll("STATE_MACHINE_INPUT", "RULE_INPUT")
    .replaceAll("OPERATION_INPUT", "RULE_INPUT")
    .replaceAll("INTERFACE_VALUE", "RULE_INPUT")
    .replaceAll("WORKFLOW_VALUE", "RULE_INPUT");
  const chunks = [...normalized.matchAll(/\/\/ structured-rule-capability:([^\n]+)\n[\s\S]*?(?=\/\/ structured-rule-capability:|$)/g)];
  if (!chunks.length || chunks.map(match => match[0]).join("") !== normalized) return false;
  const names = chunks.map(match => match[1]);
  if (names[0] !== "base" || new Set(names).size !== names.length) return false;
  for (let index = 1; index < names.length; index += 1) if (order.indexOf(names[index]) <= order.indexOf(names[index - 1])) return false;
  const body = raw.slice(end + marker.length);
  return chunks.every(match => digest(match[0]) === hashes[match[1]])
    && names.slice(1).every(name => new RegExp(`\\b${helpers[name]}\\b`).test(body));
}
