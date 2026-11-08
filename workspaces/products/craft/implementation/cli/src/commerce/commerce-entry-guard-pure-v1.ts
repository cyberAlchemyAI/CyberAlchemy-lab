/** Execute Bool pure calls in a checked Entry resource condition from the
 * captured Core source. A caller supplies only already-evaluated arguments;
 * the callee, parameter ABI and limits come from the original source/domain.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {pinCoreImplementation} from './commerce-core-physical.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import {evaluateCommerceComputation} from './commerce-computation-evaluate.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,
 type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {EntryContractV1,FlowExprV1} from './commerce-data-v1.js';

export class CommerceEntryGuardPureErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceEntryGuardPureErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceEntryGuardPureErrorV1(code);};
const pin=pinCoreImplementation(import.meta.url,[]);

export interface CommerceEntryGuardPureOwnerV1 {
 evaluate(path:string,args:readonly unknown[]):boolean;
 assertCurrent():void;
 dispose():void;
}
interface GuardCodecs {
 schemaForCallableArguments(id:string):unknown;
 encodeComputationParameters(schema:unknown,value:unknown):{ok:true;value:Uint8Array}|{ok:false};
}

/** Retain exact expression paths so a caller cannot choose an unrelated pure
 * declaration and use its result as a worker authorization predicate. */
export function createCommerceEntryGuardPureOwnerV1(
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 entry:EntryContractV1,codecs:GuardCodecs,
):CommerceEntryGuardPureOwnerV1 {
 assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);pin.assertCurrent();
 const staged=stage.inspect(source),base=domain.inspect(baseline);
 if(base.source_capture_sha256!==staged.source_sha256)bad('ForeignSource');
 const original=stage.moduleContracts(source).flatMap(module=>module.entries).find(row=>row.id===entry.id);
 const condition=entry.access.resource_condition;
 if(original!==entry||!condition)bad('ForeignEntry');
 const calls=new Map<string,{declaration:string;count:number}>();
 let nodes=0;
 const walk=(node:FlowExprV1,path:string):void=>{
  if(++nodes>65536)bad('GuardBound');
  if(node.op==='call')calls.set(path,{declaration:node.declaration,count:node.arguments.length});
  for(const [key,value] of Object.entries(node)){
   if(!value||typeof value!=='object')continue;
   if(Array.isArray(value))value.forEach((item,index)=>{
    if(item&&typeof item==='object'&&'op'in item)walk(item as FlowExprV1,path+'.'+key+'['+index+']');
   });
   else if('op'in value)walk(value as FlowExprV1,path+'.'+key);
  }
 };
 walk(condition!.expression,'$.access.resource_condition.expression');
 const texts=staged.modules.map(module=>({path:module.identity.artifact.path,text:module.text}));
 const handles=new Map<string,CommerceComputationDomainHandle>();
 let disposed=false;
 const current=()=>{
  if(disposed)bad('DisposedOwner');pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);
  for(const handle of handles.values())domain.assertCurrent(handle);
 };
 const owner:CommerceEntryGuardPureOwnerV1=Object.freeze({
  evaluate(path:string,args:readonly unknown[]){
   current();const call=calls.get(path);
   if(!call)bad('ForeignCall');
   if(!Array.isArray(args)||args.length!==call!.count)bad('ForeignCall');
   let handle=handles.get(call!.declaration);
   if(!handle){
    handle=domain.check(createCoreCommerceComputationContract(texts,call!.declaration,base.contract.limits));
    const contract=domain.inspect(handle).contract;
    if(contract.result.kind!=='scalar'||contract.result.name!=='Bool'||contract.inputs.length!==call!.count){
     domain.dispose(handle);bad('UnsupportedGuardCall');
    }
    handles.set(call!.declaration,handle);
   }
   const contract=domain.inspect(handle).contract,input:Record<string,unknown>=Object.create(null);
   for(let i=0;i<contract.inputs.length;i++)input[contract.inputs[i]!.name]=args[i];
   let encoded:{ok:true;value:Uint8Array}|{ok:false};
   try{encoded=codecs.encodeComputationParameters(codecs.schemaForCallableArguments(call!.declaration),input);}
   catch{return bad('InvalidGuardArguments');}
   if(!encoded.ok)return bad('InvalidGuardArguments');
   const result=evaluateCommerceComputation(domain,handle,encoded.value);
   if(!result.ok)return bad('GuardEvaluationFailed:'+result.error.code+':'+result.error.expression_path);
   let value:unknown;
   try{value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result.wire));}
   catch{return bad('InvalidGuardResult');}
   if(typeof value!=='boolean')return bad('InvalidGuardResult');
   current();return value as boolean;
  },
  assertCurrent:current,
  dispose(){if(disposed)return;disposed=true;for(const handle of handles.values())domain.dispose(handle);handles.clear();},
 });
 current();return owner;
}
