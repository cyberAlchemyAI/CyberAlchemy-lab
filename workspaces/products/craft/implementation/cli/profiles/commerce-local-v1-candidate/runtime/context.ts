/** Internal source-bound identity data primitives. Not a private context owner.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import {createHash} from 'node:crypto';
import {types as host} from 'node:util';
import {commerceIdentityModel as model} from './commerce-identity-model.js';
import {createCommerceValueCodecs} from './values-and-codecs.js';
const nativeNow=Date.now,encoder=new TextEncoder(),MAX_TUPLE=524288,MAX=18446744073709551615n;
class IdentityFault extends Error {readonly code:string;constructor(code:string){super(code);this.code=code;}}
const reject=():never=>{throw new IdentityFault('ProducerValueRejected');};
const closed=(input:any,keys:string[]):any=>{
 if(!input||typeof input!=='object'||host.isProxy(input)||Array.isArray(input))return reject();const proto=Object.getPrototypeOf(input);if(proto!==Object.prototype&&proto!==null)return reject();const names=Reflect.ownKeys(input);if(names.length!==keys.length||names.some(k=>typeof k!=='string'||!keys.includes(k)))return reject();
 const out=Object.create(null);for(const k of keys){const d=Object.getOwnPropertyDescriptor(input,k);if(!d||!d.enumerable||!Object.hasOwn(d,'value'))return reject();out[k]=d.value;}return out;
};
const argumentsCopy=(input:any,count:number):any[]=>{
 if(host.isProxy(input)||!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype)return reject();const n=Object.getOwnPropertyDescriptor(input,'length')!.value;if(n!==count||count>16||Reflect.ownKeys(input).length!==count+1)return reject();const out:any[]=[];
 for(let i=0;i<count;i++){const d=Object.getOwnPropertyDescriptor(input,String(i));if(!d||!d.enumerable||!Object.hasOwn(d,'value'))return reject();out.push(d.value);}return out;
};
const quote=(s:string)=>'"'+s.replace(/["\\\u0000-\u001f]/g,c=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"';
const canonical=(v:any):string=>v===null?'null':typeof v==='bigint'?quote(String(v)):typeof v==='string'?quote(v):typeof v==='boolean'?String(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>quote(k)+':'+canonical(v[k])).join(',')+'}';
function tuple(domain:string,fields:readonly string[]):Uint8Array {
 let total=0;const encoded:Uint8Array[]=[];for(const text of [domain,...fields]){const b=encoder.encode(text);if(b.length>MAX_TUPLE||total+4+b.length>MAX_TUPLE)reject();total+=4+b.length;encoded.push(b);}const out=new Uint8Array(total),view=new DataView(out.buffer);let offset=0;for(const b of encoded){view.setUint32(offset,b.length,false);offset+=4;out.set(b,offset);offset+=b.length;}return out;
}
export function createCommerceIdentityPrimitives(){
 if(arguments.length)throw new IdentityFault('ContextCustodyRejected');
 const codecs=createCommerceValueCodecs(),schemas=new Map<string,any>(),bindings=new Map<string,any>(model.bindings.map((b:any)=>[b.key,b]));
 const schema=(t:any)=>{const key=JSON.stringify(t);let h=schemas.get(key);if(!h){const r=codecs.checkCommerceSchema({...model.source_schema,root:t});if(!r.ok)throw new IdentityFault('NativeImplementationUnavailable');h=r.value;schemas.set(key,h);}return h;};
 const copy=(t:any,value:any):any=>{
  if(t.kind==='optional'){const v=closed(value,value&&typeof value==='object'&&!host.isProxy(value)&&Object.getOwnPropertyDescriptor(value,'kind')?.value==='none'?['kind']:['kind','value']);if(v.kind==='none')return Object.freeze({kind:'none'});if(v.kind!=='some')return reject();return Object.freeze({kind:'some',value:copy(t.element,v.value)});}
  if(t.kind==='string'||t.kind==='literal'){const r=codecs.copyCommerceValue(codecs.schemaForType('Shop.Values.Identifier'),value);if(!r.ok)return reject();if(t.kind==='literal'&&r.value!==t.value||t.kind==='string'&&(encoder.encode(r.value as string).length>t.max_bytes||[...(r.value as string)].length>t.max_scalars))return reject();return r.value;}
  const r=codecs.copyCommerceValue(schema(t),value);if(!r.ok)return reject();return r.value;
 };
 return Object.freeze({evaluateNativeIdentityData(bindingKey:string,parameters:readonly unknown[]){
  const b=typeof bindingKey==='string'?bindings.get(bindingKey):undefined;if(!b)return {ok:false,error:{code:'ContextCustodyRejected'}};
  try{
   const raw=argumentsCopy(parameters,b.parameters.length),a=b.parameters.map((p:any,i:number)=>{const value=copy(p.type,raw[i]);if(p.finite&&!p.finite.includes(value))return reject();if(p.literal){const expected=p.literal.type.kind==='scalar'&&p.literal.type.name==='UInt64'?BigInt(p.literal.value):p.literal.value;if(value!==expected)return reject();}return value;});
   let fields:string[]=[],prefix='',value:any,tuple_bytes=0;const method=b.observation.method,domain=b.signature.domain;
   switch(method){
    case'checkoutFingerprint':fields=a;break;
    case'newOrderId':fields=a;prefix='ord_';break;
    case'commandId':fields=a;prefix='cmd_';break;
    case'eventMetadata':if(a[0]!==b.service||!b.event_targets.length)return reject();fields=[a[0],a[1],String(a[2]),String(a[3])];prefix='evt_';break;
    case'stockLinesFingerprint':fields=[canonical(a[0])];break;
    case'stockCommandFingerprint':if(a[0]==='reserve'?a[3].kind!=='none':!['allocate','release'].includes(a[0])||a[3].kind!=='some')return reject();fields=[a[0],a[1],canonical(a[2]),a[3].kind==='none'?'none':'some:'+String(a[3].value)];break;
    case'captureFingerprint':fields=[a[0],a[1],String(a[2]),a[3]];break;
    case'taggedCommandIdentity':{
     const type=b.parameters[1].type,groups=b.signature.slot_groups,variant=a[1].kind;
     if(type.kind!=='enum'||typeof variant!=='string'||!groups||typeof groups!=='object')return reject();
     const selected=Object.entries(groups).find(([,members])=>Array.isArray(members)&&members.includes(variant));
     if(!selected)return reject();
     const encoded=codecs.encodeCommerceValue(schema(type),a[1]);if(!encoded.ok)return reject();
     const content=new TextDecoder('utf-8',{fatal:true}).decode(encoded.value);
     const slotBytes=tuple(domain+'/slot',[a[0],type.name,selected[0]]),contentBytes=tuple(domain+'/content',[a[0],type.name,content]);
     tuple_bytes=slotBytes.length+contentBytes.length;
     value=Object.freeze({commandId:'cmd_'+createHash('sha256').update(slotBytes).digest('hex'),
      requestFingerprint:createHash('sha256').update(contentBytes).digest('hex')});
     break;
    }
    case'eventFingerprint':{if(!b.event_schema)return reject();const encoded=codecs.encodeCommerceValue(schema(b.parameters[0].type),a[0]);if(!encoded.ok)return reject();fields=[b.event_schema.name,String(b.event_schema.version),new TextDecoder().decode(encoded.value)];break;}
    case'confirmedOrderFingerprint':fields=[canonical(Object.fromEntries(b.parameters.map((p:any,i:number)=>[p.name,a[i]])))];break;
    case'orderActionFingerprint':if(a[0]==='confirm'?a[2].kind!=='none':a[0]!=='cancel'||a[2].kind!=='some'||!['StockUnavailable','PaymentDeclined'].includes(a[2].value))return reject();fields=[a[0],a[1],a[2].kind==='none'?'none':'some:'+a[2].value];break;
    case'clockEpochMs':{const observed=nativeNow();if(typeof observed!=='number'||!Number.isSafeInteger(observed)||observed<0)return reject();value=BigInt(observed);if(value>MAX)return reject();break;}
    default:throw new IdentityFault('NativeImplementationUnavailable');
   }
   if(method!=='clockEpochMs'&&method!=='taggedCommandIdentity'){const bytes=tuple(domain,fields);tuple_bytes=bytes.length;const digest=createHash('sha256').update(bytes).digest('hex'),id=prefix+digest;value=method==='eventMetadata'?Object.freeze({eventId:id,producer:a[0],aggregateId:a[1],aggregateVersion:a[2],ordinal:a[3],correlationId:a[4],commandId:a[5]}):id;}
   value=copy(b.observation.result,value);return {ok:true,value,tuple_bytes,qualification:'identity-data-primitive-only;no-private-invocation-commit-delivery-or-auth-context'};
  }catch(error){if(error instanceof IdentityFault)return {ok:false,error:{code:error.code}};throw error;}
 }});
}
