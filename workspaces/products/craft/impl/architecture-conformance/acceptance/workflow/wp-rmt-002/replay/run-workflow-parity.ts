import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {workflowTypeScriptV1Provider} from "../../../../factory/registry/providers/workflow-typescript-v1.js";
import {workflowPythonV1Provider} from "../../../../factory/registry/providers/workflow-python-v1.js";
import {workflowRustV1Provider} from "../../../../factory/registry/providers/workflow-rust-v1.js";
import {makeSettlementWorkflowCase} from "../../../../targets/typescript/workflow-v1.js";
const parityReceiptPath="projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-WF-006.json",parityReceiptFile=resolve(dirname(fileURLToPath(import.meta.url)),"../../../../../../development/remaining-meta-types/receipts/RMT-WF-006.json"),parityReceiptSha256="1884651c3493e9fc3eb9b9c3301788c76eb4f8514cc564c5d0d161356f286bd5";
const canonical=(value:unknown):unknown=>Array.isArray(value)?value.map(canonical):value&&typeof value==="object"?Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b)).map(([key,item])=>[key,canonical(item)])):value;
export const runWorkflowParity=async()=>{
  const bytes=readFileSync(parityReceiptFile),observedHash=createHash("sha256").update(bytes).digest("hex");if(observedHash!==parityReceiptSha256)throw new Error("RMT_WF_REPLAY_PARITY_RECEIPT_STALE");
  const parity=JSON.parse(bytes.toString("utf8"));if(parity.result!=="pass"||parity.authority_effect!=="none"||parity.semantic_plan_epoch_id!=="WP-RMT-002/S1/2026-08-16"||parity.proof?.base_stale_binding_rejected_by_all_providers!==true||parity.proof?.s1_stale_binding_rejected_by_all_providers!==true||parity.proof?.compensation_execution_authority!==false||parity.proof?.direct_effect_execution_authority!==false)throw new Error("RMT_WF_REPLAY_PARITY_RECEIPT_INVALID");
  const providers=[workflowTypeScriptV1Provider,workflowPythonV1Provider,workflowRustV1Provider],input={raw_inputs:{workflow_case:JSON.stringify(makeSettlementWorkflowCase())}} as never,results=[];
  for(const provider of providers)results.push(await provider.execute(input));
  const outputs=results.map((result:any)=>result.semantic_output),portable=outputs.map(({portable}:any)=>JSON.stringify(canonical(portable)));
  if(results.some(({result})=>result!=="pass")||portable[1]!==portable[0]||portable[2]!==portable[0])throw new Error("RMT_WF_REPLAY_PARITY_DRIFT");
  const semanticReceipt=(outputs[0] as any).portable,failure=semanticReceipt.scenarios?.[1];
  if(semanticReceipt.authority_separation!==true||semanticReceipt.scenarios?.length!==2||failure?.compensation_execution!==false||failure?.durable_fact_preservation!=="preserve-durable-facts"||failure?.recovery_intents?.[0]!=="forward-recover-settlement"||failure?.direct_effects_executed?.length!==0)throw new Error("RMT_WF_REPLAY_AUTHORITY_DRIFT");
  return Object.freeze({schema_version:"domainspec.workflow-semantic-replay-receipt/v1",result:"pass",work_pack_id:"WP-RMT-002",swu_id:"RMT-WF-007",semantic_plan_epoch_id:"WP-RMT-002/S1/2026-08-16",semantic_contract_digest:"75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7",parity_receipt:Object.freeze({path:parityReceiptPath,sha256:observedHash,size_bytes:bytes.length}),provider_ids:Object.freeze(results.map(({provider_id})=>provider_id)),semantic_receipt:semanticReceipt,native_evidence:Object.freeze(outputs.map(({native_evidence}:any)=>native_evidence)),fresh_process_count_declared:2,meaningful_case_count:2,provider_scenario_count:6,compensation_execution_authority:false,direct_effect_execution_authority:false,native_hash_byte_comparison:false,exactly_once_claim:false,authority_effect:"none"});
};
if(process.argv[1]?.endsWith("run-workflow-parity.ts")){
  const mode=process.argv[2]??"--emit";
  if(mode==="--nonzero-valid-looking"){process.stdout.write(JSON.stringify({schema_version:"domainspec.workflow-semantic-replay-receipt/v1",result:"pass"})+"\n");process.stderr.write("RMT_WF_REPLAY_PROBE_FAILURE\n");process.exitCode=23;}
  else if(mode==="--malformed-output")process.stdout.write("{}\n{}\n");
  else if(mode==="--extra-member")process.stdout.write(JSON.stringify({schema_version:"domainspec.workflow-semantic-replay-receipt/v1",unexpected:true})+"\n");
  else if(mode==="--emit"){try{process.stdout.write(JSON.stringify(await runWorkflowParity())+"\n");}catch(error){process.stderr.write((error instanceof Error?error.message:String(error))+"\n");process.exitCode=1;}}
  else{process.stderr.write("RMT_WF_REPLAY_MODE_INVALID\n");process.exitCode=24;}
}
