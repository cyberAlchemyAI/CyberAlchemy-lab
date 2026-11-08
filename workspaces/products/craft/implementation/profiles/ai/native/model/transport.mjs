import {createOpenAIInferenceTransport} from '@cyberalchemy/are-model-transports/native-provider-transports';
import {capture,canonical,freeze,assert,count,text,copyBytes} from '../shared.mjs';

/** Exact strict-schema projection, never dropping business constraints. Scalar
 * roots are wrapped because Responses requires an object root. Length bounds
 * become a Unicode-scalar pattern intersection; the original pattern remains.
 * The original generated decoder remains the final business type owner.
 * Open Questions: README.md. */
export function projectStrictSchema(input) {
 const schema=capture(input);let nodes=0;
 const scalar='(?:[^\\uD800-\\uDFFF]|[\\uD800-\\uDBFF][\\uDC00-\\uDFFF])';
 const project=(s,depth=0)=>{
  assert(++nodes<=4096&&depth<=16&&s&&typeof s==='object'&&!Array.isArray(s),'UnsupportedCapability','finite strict schema');
  const allowed=new Set(['type','properties','required','additionalProperties','items','minItems','maxItems','minLength','maxLength','pattern','enum','anyOf','minimum','maximum','description']);
  assert(Object.keys(s).every(k=>allowed.has(k)),'UnsupportedCapability','unsupported strict schema keyword');
  if(s.anyOf){assert(Object.keys(s).every(k=>['anyOf','description'].includes(k))&&Array.isArray(s.anyOf)&&s.anyOf.length>0&&s.anyOf.length<=16,'UnsupportedCapability','finite anyOf');return {anyOf:s.anyOf.map(x=>project(x,depth+1))};}
  assert(['object','array','string','boolean','null','number','integer'].includes(s.type),'UnsupportedCapability','closed strict type');const out=JSON.parse(canonical(s));
  if(s.type==='object'){
   assert(s.additionalProperties===false&&s.properties&&typeof s.properties==='object'&&!Array.isArray(s.properties)&&Array.isArray(s.required)&&Object.keys(s.properties).length<=128,'UnsupportedCapability','closed required object');
   assert(canonical([...s.required].sort())===canonical(Object.keys(s.properties).sort()),'UnsupportedCapability','all object fields must be required');
   out.properties=Object.fromEntries(Object.entries(s.properties).map(([k,v])=>[k,project(v,depth+1)]));
  }
  if(s.type==='array'){assert(s.items,'UnsupportedCapability','array items');out.items=project(s.items,depth+1);for(const k of ['minItems','maxItems'])if(s[k]!==undefined)count(s[k],k,65536);if(s.minItems!==undefined&&s.maxItems!==undefined)assert(s.minItems<=s.maxItems,'UnsupportedCapability','array interval');}
  if(s.type==='string'){
   if(s.pattern!==undefined){text(s.pattern,'pattern',65536);try{new RegExp(s.pattern,'u');}catch{assert(false,'UnsupportedCapability','invalid strict pattern');}}
   if(s.minLength!==undefined||s.maxLength!==undefined){const min=s.minLength??0,max=s.maxLength??1048576;count(min,'minLength',1048576);count(max,'maxLength',1048576);assert(min<=max&&(!s.pattern||s.pattern.startsWith('^')),'UnsupportedCapability','exact generated anchored string interval');
    out.pattern=`^(?=${scalar}{${min},${max}}(?![\\s\\S]))(?:${s.pattern??'[\\s\\S]*'})`;delete out.minLength;delete out.maxLength;}
  }
  if(s.enum!==undefined)assert(Array.isArray(s.enum)&&s.enum.length>0&&s.enum.length<=1000&&s.enum.every(v=>typeof v==='string'||typeof v==='boolean'||v===null||typeof v==='number'&&Number.isFinite(v)),'UnsupportedCapability','finite scalar enum');
  for(const k of ['minimum','maximum'])if(s[k]!==undefined)assert(typeof s[k]==='number'&&Number.isFinite(s[k]),'UnsupportedCapability','finite numeric bound');
  return out;
 };
 const projected=project(schema),wrapped=projected.type!=='object';
 return freeze({schema:wrapped?{type:'object',properties:{value:projected},required:['value'],additionalProperties:false}:projected,wrapped});
}

export function createSelectedOpenAITransport(options) {
 const reused=createOpenAIInferenceTransport(options);
 return Object.freeze({identity:freeze({abi:'inference-port/v1',transport_abi:reused.abi,kind:'direct-inference',provider:'openai',model:reused.model,embedding_model:reused.embedding_model,dimensions:reused.dimensions,controls:reused.controls}),
  async invoke(request){const input=copyBytes(request.input);let prompt;try{prompt=new TextDecoder('utf-8',{fatal:true}).decode(input);}catch{assert(false,'InvalidContract','UTF8 model input');}
   const projection=request.operation==='text.structured'?projectStrictSchema(request.result_schema):null;
   const response=await reused.invoke({operation:request.operation,prompt,...(projection?{result_schema:projection.schema}:{}),signal:request.signal,max_output_tokens:request.max_output_tokens,tools:request.tools??[],store:request.store??false,stream:false});
   if(request.signal.aborted)return freeze({kind:'unknown',reason:'cancelled',usage:response.usage,response_id:response.response_id});
   if(response.kind!=='candidate')return response;
   if(request.operation==='vector.embed')return freeze({...response,wire:Array.from(new TextEncoder().encode(JSON.stringify(response.vector)))});
   let final=response.final_bytes;
   if(request.operation==='text.generate'){assert(request.result_schema?.type==='string','UnsupportedCapability','text generation requires original string result');final=JSON.stringify(final);}
   if(projection?.wrapped){try{const parsed=JSON.parse(final);assert(parsed&&typeof parsed==='object'&&!Array.isArray(parsed)&&Object.keys(parsed).length===1&&Object.hasOwn(parsed,'value'),'InvalidContract','wrapped exact scalar result');final=canonical(parsed.value);}catch{return freeze({kind:'invalid',reason:'scalar-wrapper',usage:response.usage,response_id:response.response_id});}}
   return freeze({...response,wire:Array.from(new TextEncoder().encode(final))});
  }
 });
}
