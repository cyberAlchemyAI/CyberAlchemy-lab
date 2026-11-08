import * as fn0 from "./generated/src/domainspec/typescript/delivery-example/order-to-message.js";
import * as fn1 from "./generated/src/domainspec/typescript/delivery-example/partial-message.js";
import * as fn2 from "./generated/src/domainspec/typescript/delivery-example/choose-delivery-fee.js";
function implementation(module:Record<string,unknown>):Function {const exported=Object.values(module).filter((value):value is Function=>typeof value==="function");if(exported.length!==1)throw new Error("ALCH_GENERATED_EXPORT_CONTRACT");return exported[0];}
const implementations: Record<string, Function> = {"OrderToMessage":implementation(fn0),"PartialMessage":implementation(fn1),"ChooseDeliveryFee":implementation(fn2)};
const mappings: any = {"OrderToMessage":{"fields":[{"id":"orderId","target":"order_id","type":"identifier"},{"id":"urgent","target":"urgent","type":"boolean"},{"id":"priority","target":"priority","type":"boolean"}],"outputs":[{"id":"messageId","target":"message_id"},{"id":"currency","target":"currency"}]},"PartialMessage":{"fields":[{"id":"orderId","target":"order_id","type":"identifier"},{"id":"urgent","target":"urgent","type":"boolean"},{"id":"priority","target":"priority","type":"boolean"}],"outputs":[{"id":"messageId","target":"message_id"}]}};
const policies: any = {"ChooseDeliveryFee":{"fields":[{"id":"urgent","target":"urgent","type":"boolean"},{"id":"priority","target":"priority","type":"boolean"}],"targets":{"delivery-example:express-fee":"ExpressFee","delivery-example:priority-fee":"PriorityFee","delivery-example:standard-fee":"StandardFee"}}};
function input(value: unknown, fields: any[], required: boolean): Record<string,unknown> {
 if(!value || typeof value!=="object" || Array.isArray(value) || ![Object.prototype,null].includes(Object.getPrototypeOf(value)))throw new Error("ALCH_INPUT_RECORD");
 const out:Record<string,unknown>=Object.create(null);
 for(const f of fields){const desc=Object.getOwnPropertyDescriptor(value,f.id);if(!desc){if(required)throw new Error("ALCH_MISSING_INPUT:"+f.id);continue;}if(!("value" in desc) || typeof desc.value!==(f.type==="boolean"?"boolean":"string"))throw new Error("ALCH_INPUT_TYPE:"+f.id);out[f.target]=desc.value;}
 return out;
}
export function evaluateMapping(id:string, value:unknown): Readonly<Record<string,unknown>> {
 if(!Object.hasOwn(mappings,id))throw new Error("ALCH_UNKNOWN_MAPPING:"+id);const m=mappings[id];const result=implementations[id](input(value,m.fields,false));const out:Record<string,unknown>={};for(const f of m.outputs)if(Object.hasOwn(result,f.target))Object.defineProperty(out,f.id,{value:result[f.target],enumerable:true});return Object.freeze(out);
}
export function selectPolicy(id:string,value:unknown):string {
 if(!Object.hasOwn(policies,id))throw new Error("ALCH_UNKNOWN_POLICY:"+id);const p=policies[id];const result=implementations[id](input(value,p.fields,true));if(!Object.hasOwn(p.targets,result))throw new Error("ALCH_UNKNOWN_TARGET");return p.targets[result];
}
