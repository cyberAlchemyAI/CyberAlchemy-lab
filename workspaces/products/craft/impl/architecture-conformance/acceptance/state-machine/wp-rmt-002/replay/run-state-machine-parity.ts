import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {stateMachineTypeScriptV1Provider} from "../../../../factory/registry/providers/state-machine-typescript-v1.js";
import {stateMachinePythonV1Provider} from "../../../../factory/registry/providers/state-machine-python-v1.js";
import {stateMachineRustV1Provider} from "../../../../factory/registry/providers/state-machine-rust-v1.js";
import {makeSettlementStateMachineCase} from "../../../../targets/typescript/state-machine-v1.js";
const parityReceiptPath="projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-SM-006.json",parityReceiptSha256="f3b250f79e0001a9a762dc3261ff47563bfe8bb4d932dd90b2f298afeb060368";
const canonical=(value:unknown):unknown=>Array.isArray(value)?value.map(canonical):value&&typeof value==="object"?Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b)).map(([key,item])=>[key,canonical(item)])):value;
export const runStateMachineParity=async()=>{
  const bytes=readFileSync(parityReceiptPath),observedHash=createHash("sha256").update(bytes).digest("hex");if(observedHash!==parityReceiptSha256)throw new Error("RMT_SM_REPLAY_PARITY_RECEIPT_STALE");
  const parity=JSON.parse(bytes.toString("utf8"));if(parity.result!=="pass"||parity.authority_effect!=="none"||parity.semantic_plan_epoch_id!=="WP-RMT-002/S1/2026-08-16"||parity.proof?.effect_execution_authority!==false)throw new Error("RMT_SM_REPLAY_PARITY_RECEIPT_INVALID");
  const providers=[stateMachineTypeScriptV1Provider,stateMachinePythonV1Provider,stateMachineRustV1Provider],input={raw_inputs:{state_machine_case:JSON.stringify(makeSettlementStateMachineCase())}} as never,results=[];
  for(const provider of providers)results.push(await provider.execute(input));
  const outputs=results.map((result:any)=>result.semantic_output),portable=outputs.map(({portable}:any)=>JSON.stringify(canonical(portable)));
  if(results.some(({result})=>result!=="pass")||portable[1]!==portable[0]||portable[2]!==portable[0])throw new Error("RMT_SM_REPLAY_PARITY_DRIFT");
  const semanticReceipt=(outputs[0] as any).portable;
  if(semanticReceipt.effects_performed_inline!==false||semanticReceipt.transition_results.length!==3||semanticReceipt.transition_results[2].accepted!==false)throw new Error("RMT_SM_REPLAY_EFFECT_AUTHORITY_DRIFT");
  return Object.freeze({schema_version:"domainspec.state-machine-semantic-replay-receipt/v1",result:"pass",work_pack_id:"WP-RMT-002",swu_id:"RMT-SM-007",semantic_plan_epoch_id:"WP-RMT-002/S1/2026-08-16",semantic_contract_digest:"75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7",parity_receipt:Object.freeze({path:parityReceiptPath,sha256:observedHash,size_bytes:bytes.length}),provider_ids:Object.freeze(results.map(({provider_id})=>provider_id)),semantic_receipt:semanticReceipt,native_evidence:Object.freeze(outputs.map(({native_evidence}:any)=>native_evidence)),fresh_process_count_declared:2,meaningful_case_count:3,provider_transition_case_count:9,effect_execution_authority:false,native_hash_byte_comparison:false,authority_effect:"none"});
};
if(process.argv[1]?.endsWith("run-state-machine-parity.ts")){
  const mode=process.argv[2]??"--emit";
  if(mode==="--nonzero-valid-looking"){process.stdout.write(JSON.stringify({schema_version:"domainspec.state-machine-semantic-replay-receipt/v1",result:"pass"})+"\n");process.stderr.write("RMT_SM_REPLAY_PROBE_FAILURE\n");process.exitCode=23;}
  else if(mode==="--malformed-output")process.stdout.write("{}\n{}\n");
  else if(mode==="--extra-member")process.stdout.write(JSON.stringify({schema_version:"domainspec.state-machine-semantic-replay-receipt/v1",unexpected:true})+"\n");
  else if(mode==="--emit"){try{process.stdout.write(JSON.stringify(await runStateMachineParity())+"\n");}catch(error){process.stderr.write((error instanceof Error?error.message:String(error))+"\n");process.exitCode=1;}}
  else{process.stderr.write("RMT_SM_REPLAY_MODE_INVALID\n");process.exitCode=24;}
}
