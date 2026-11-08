/** Original-source pure call bundle emission; no arbitrary evaluator/module.
 * Open Questions: docs/COMMERCE-COMPUTATION-CALLS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommercePureCallOwner,type CommercePureCallOwner,type CommercePureCallHandle} from './commerce-computation-call-owner.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-computation-call-owner'+ext,'commerce-computation-call-runtime'+ext]);
const hash=(text:string)=>createHash('sha256').update(text).digest('hex');
// Exact typed source correspondence to the owning adapter is a required check.
const ADAPTER_SOURCE=String.raw`function adaptCommercePureCallResult(observation:any,spec:any):any {
 let decision:string,action:any=null;
 if(!observation.result.ok){
  decision=observation.evaluation_phase==='input-validation'?'parameter-validation-error':'evaluation-error';
  if(decision==='evaluation-error')action=spec.on_error;
 }else if(spec.direct_guard){
  const bool=new TextDecoder().decode(observation.result.wire);
  if(bool!=='true'&&bool!=='false')throw new Error('InvalidBooleanComputationResult');
  decision=bool==='true'?'guard-true':'guard-false';if(bool==='false')action=spec.on_false;
 }else decision='value';
 return {observation,decision,source_action:action,action_requirement:action?(spec.requires_rollback?'requires-original-proven-rollback-before-source-action':'requires-original-caller-to-apply-source-action'):'none',qualification:'bound-pure-parameter-evaluation-only;argument-acquisition-and-operation-execution-not-established',authority_effect:'none'};
}
`;
export function compileCommercePureCallBundle(owner:CommercePureCallOwner,handle:CommercePureCallHandle){
 assertCommercePureCallOwner(owner);pin.assertCurrent();owner.assertCurrent(handle);const binding=owner.inspect(handle),pure=owner.compilePure(handle),id=binding.binding_sha256.slice(0,24),purePath='pure-'+id+'.ts',adapterPath='caller-'+id+'.ts';
 const source=`// Generated pure call outcome adapter. Open Questions: docs/COMMERCE-COMPUTATION-CALLS.md#open-questions.\nimport {evaluateObserved} from './${purePath.replace(/\.ts$/,'.js')}';\nconst adaptCommercePureCallResult=${ADAPTER_SOURCE};\nconst spec=JSON.parse(${JSON.stringify(JSON.stringify(binding.adapter))});\nexport function evaluateBoundParameters(input:Uint8Array){return adaptCommercePureCallResult(evaluateObserved(input),spec);}\n`;
 const files=coreFreeze([{path:purePath,text:pure.source},{path:adapterPath,text:source}]),manifest=coreFreeze({kind:'commerce-source-pure-call-bundle/v1-candidate',source_call:binding,pure_manifest:pure.manifest,entrypoint:adapterPath,adapter_template_sha256:hash(ADAPTER_SOURCE),code_epoch_sha256:pin.sha256,members:files.map(f=>({path:f.path,bytes:Buffer.byteLength(f.text),sha256:hash(f.text)})),runtime_dependencies:['node:util'],qualification:'generated-bound-pure-component-and-source-action-proposals-only;not-original-argument-context-or-operation-execution',authority_effect:'none',open_questions_ref:'docs/COMMERCE-COMPUTATION-CALLS.md#open-questions'});
 owner.assertCurrent(handle);pin.assertCurrent();return Object.freeze({files,manifest});
}
