import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {interfaceTypeScriptV1Provider} from "../../../../factory/registry/providers/interface-typescript-v1.js";
import {interfacePythonV1Provider} from "../../../../factory/registry/providers/interface-python-v1.js";
import {interfaceRustV1Provider} from "../../../../factory/registry/providers/interface-rust-v1.js";
import {makeSettlementInterfaceCase} from "../../../../targets/typescript/interface-v1.js";

const parityReceiptPath="projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-IFACE-006.json";
const parityReceiptSha256="a1ffa95e8424dbd715fa01ce8b2b8285df70f97c182ccdc0148a8130496e4e25";
const canonical=(value:unknown):unknown=>Array.isArray(value)?value.map(canonical):value&&typeof value==="object"
  ?Object.fromEntries(Object.entries(value).sort(([left],[right])=>left.localeCompare(right)).map(([key,item])=>[key,canonical(item)])):value;

export const runInterfaceParity=async()=>{
  const parityBytes=readFileSync(parityReceiptPath);
  const observedParityHash=createHash("sha256").update(parityBytes).digest("hex");
  if(observedParityHash!==parityReceiptSha256) throw new Error("RMT_IFACE_REPLAY_PARITY_RECEIPT_STALE");
  const parityReceipt=JSON.parse(parityBytes.toString("utf8"));
  if(parityReceipt.result!=="pass"||parityReceipt.authority_effect!=="none") throw new Error("RMT_IFACE_REPLAY_PARITY_RECEIPT_INVALID");
  const input={raw_inputs:{interface_case:JSON.stringify(makeSettlementInterfaceCase())}} as never;
  const results=[];
  for(const provider of [interfaceTypeScriptV1Provider,interfacePythonV1Provider,interfaceRustV1Provider]) results.push(await provider.execute(input));
  const outputs=results.map((result:any)=>result.semantic_output);
  const portable=outputs.map(({portable}:any)=>JSON.stringify(canonical(portable)));
  if(results.some(({result})=>result!=="pass")||portable[1]!==portable[0]||portable[2]!==portable[0]) throw new Error("RMT_IFACE_REPLAY_PARITY_DRIFT");
  return Object.freeze({
    schema_version:"domainspec.interface-semantic-replay-receipt/v1",result:"pass",work_pack_id:"WP-RMT-002",swu_id:"RMT-IFACE-007",
    parity_receipt:Object.freeze({path:parityReceiptPath,sha256:observedParityHash,size_bytes:parityBytes.length}),
    provider_ids:Object.freeze(results.map(({provider_id})=>provider_id)),portable:outputs[0].portable,
    native_evidence:Object.freeze(outputs.map(({native_evidence}:any)=>native_evidence)),
    fresh_process_count_declared:2,native_hash_byte_comparison:false,authority_effect:"none",
  });
};

if(process.argv[1]?.endsWith("run-interface-parity.ts")){
  const mode=process.argv[2]??"--emit";
  if(mode==="--fail"){
    process.stderr.write("RMT_IFACE_REPLAY_PROBE_FAILURE\n");
    process.exitCode=23;
  }else if(mode==="--malformed-output"){
    process.stdout.write("{}\n{}\n");
  }else if(mode==="--emit"){
    try{process.stdout.write(`${JSON.stringify(await runInterfaceParity())}\n`);}
    catch(error){process.stderr.write(`${error instanceof Error?error.message:String(error)}\n`);process.exitCode=1;}
  }else{
    process.stderr.write("RMT_IFACE_REPLAY_MODE_INVALID\n");process.exitCode=24;
  }
}
