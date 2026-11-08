import {CROSS_GENERATOR_POLICY_RUNNER} from './reconciled-cross-generator-policy-runner.js';
const replace = (source: string, from: string, to: string) => {
  if (source.split(from).length !== 2) throw Error('STATE_MACHINE_PROBE:observer hook drift');
  return source.replace(from, to);
};
// The shared observer checks frozen reducer outcomes; only initial-state tracing differs.
let runner = replace(CROSS_GENERATOR_POLICY_RUNNER, 'return {[policyCallable]:', 'return {initialState:native.initialState,[policyCallable]:');
runner = replace(runner, 'const observed=await observeRule(row);', "if(row.adapter!=='state-machine'||row.cases[0]?.mode!=='initial-state'||row.cases.slice(1).some(c=>c.mode!=='state-machine'))throw Error('STATE_MACHINE_PROBE_CASES');\n  const observed=await observeRule(row);caseTraces.unshift([]);");
export const CROSS_GENERATOR_STATE_MACHINE_RUNNER = runner;
