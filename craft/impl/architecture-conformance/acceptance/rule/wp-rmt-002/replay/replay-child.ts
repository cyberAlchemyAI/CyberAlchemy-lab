import {evaluateWpRmt002RuleParity} from
  "../parity/evaluate-rule-parity.js";

const probe = process.env.DOMAINSPEC_RULE_REPLAY_PROBE;
const root = process.env.DOMAINSPEC_RULE_REPLAY_REPOSITORY_ROOT;

if (probe === "malformed-output") {
  process.stdout.write("{not-json}\n");
} else {
  const receipt = await evaluateWpRmt002RuleParity(root);
  process.stdout.write(`${JSON.stringify(receipt)}\n`);
  if (probe === "nonzero-with-valid-output") process.exitCode = 17;
}
