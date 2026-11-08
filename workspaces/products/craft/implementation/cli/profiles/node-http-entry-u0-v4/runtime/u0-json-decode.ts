import {types} from 'node:util';

/** Finite flat-wire tokenizer, not UInt64 formation or a general JSON parser.
 * Open Questions: U06b/U06c/U07 and J01 actual registered realization. */
export interface U0DecodedWireRecord {readonly id:string;readonly verified:boolean}
export type U0JsonDecodeCode='U0_DECODE_ARGUMENT'|'U0_DECODE_LIMIT'|'U0_DECODE_BYTES'|'U0_DECODE_BOM'|'U0_DECODE_UTF8'|'U0_DECODE_JSON'|'U0_DECODE_ESCAPE'|'U0_DECODE_DUPLICATE'|'U0_DECODE_FIELD'|'U0_DECODE_MISSING';
export class U0JsonDecodeError extends SyntaxError {
 constructor(readonly code:U0JsonDecodeCode,readonly offset:number){super(code+' at '+offset);this.name='U0JsonDecodeError';}
}
export interface U0JsonDecodeInspection {
 readonly value:U0DecodedWireRecord;
 readonly work:Readonly<{input_bytes:number;source_code_units:number;cursor_advances:number;code_unit_reads:number;decoded_string_units:number}>;
}
const typedArrayPrototype=Object.getPrototypeOf(Uint8Array.prototype) as object;
const nativeByteLength=Object.getOwnPropertyDescriptor(typedArrayPrototype,'byteLength')!.get!;
const nativeBuffer=Object.getOwnPropertyDescriptor(typedArrayPrototype,'buffer')!.get!;
const fail=(code:U0JsonDecodeCode,offset=0):never=>{throw new U0JsonDecodeError(code,offset);};
function ownedBytes(input:Uint8Array,maximumBytes:number):Uint8Array {
 if(!Number.isSafeInteger(maximumBytes)||maximumBytes<1||maximumBytes>2147483647)fail('U0_DECODE_LIMIT');
 if(!types.isUint8Array(input))fail('U0_DECODE_ARGUMENT');
 // Native getters avoid caller overrides. Native set copies typed-array storage
 // without iterators/species or per-index JavaScript callbacks.
 const length=Reflect.apply(nativeByteLength,input,[]) as number;
 if(length>maximumBytes)fail('U0_DECODE_BYTES');
 if(types.isSharedArrayBuffer(Reflect.apply(nativeBuffer,input,[])))fail('U0_DECODE_ARGUMENT');
 try{const value=new Uint8Array(length);Uint8Array.prototype.set.call(value,input);return value;}catch{return fail('U0_DECODE_ARGUMENT');}
}
/** Inspection is pure fixed telemetry, with no callback or observer dependency. */
export function inspectU0JsonDecode(input:Uint8Array,maximumBytes:number):U0JsonDecodeInspection {
 const bytes=ownedBytes(input,maximumBytes);
 if(bytes[0]===0xef&&bytes[1]===0xbb&&bytes[2]===0xbf)fail('U0_DECODE_BOM');
 let text:string;
 try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);}catch{return fail('U0_DECODE_UTF8');}
 let cursor=0,reads=0,advances=0,stringUnits=0;
 const peek=():number=>{reads++;return cursor<text.length?text.charCodeAt(cursor):-1;};
 const take=():number=>{const code=peek();if(code<0)fail('U0_DECODE_JSON',cursor);cursor++;advances++;return code;};
 const expect=(expected:number):void=>{if(take()!==expected)fail('U0_DECODE_JSON',cursor-1);};
 const whitespace=():void=>{for(;;){const code=peek();if(code!==0x20&&code!==0x09&&code!==0x0a&&code!==0x0d)return;take();}};
 const hex=():number=>{
  let value=0;
  for(let i=0;i<4;i++){
   const code=take(),digit=code>=48&&code<=57?code-48:code>=65&&code<=70?code-55:code>=97&&code<=102?code-87:-1;
   if(digit<0)fail('U0_DECODE_ESCAPE',cursor-1);value=value*16+digit;
  }return value;
 };
 const string=():string=>{
  expect(0x22);const parts:string[]=[];
  for(;;){
   const code=take();
   if(code===0x22){const value=parts.join('');stringUnits+=value.length;return value;}
   if(code<0x20)fail('U0_DECODE_ESCAPE',cursor-1);
   if(code===0x5c){
    const escape=take();
    switch(escape){
     case 0x22:parts.push('"');break;case 0x5c:parts.push('\\');break;case 0x2f:parts.push('/');break;
     case 0x62:parts.push('\b');break;case 0x66:parts.push('\f');break;case 0x6e:parts.push('\n');break;case 0x72:parts.push('\r');break;case 0x74:parts.push('\t');break;
     case 0x75:{
      const first=hex();
      if(first>=0xd800&&first<=0xdbff){
       if(take()!==0x5c||take()!==0x75)fail('U0_DECODE_ESCAPE',cursor-1);
       const second=hex();if(second<0xdc00||second>0xdfff)fail('U0_DECODE_ESCAPE',cursor-4);parts.push(String.fromCharCode(first,second));
      }else if(first>=0xdc00&&first<=0xdfff)fail('U0_DECODE_ESCAPE',cursor-4);
      else parts.push(String.fromCharCode(first));break;
     }
     default:fail('U0_DECODE_ESCAPE',cursor-1);
    }
   }else if(code>=0xd800&&code<=0xdbff){
    const second=take();if(second<0xdc00||second>0xdfff)fail('U0_DECODE_ESCAPE',cursor-1);parts.push(String.fromCharCode(code,second));
   }else if(code>=0xdc00&&code<=0xdfff)fail('U0_DECODE_ESCAPE',cursor-1);
   else parts.push(String.fromCharCode(code));
  }
 };
 const literal=(value:'true'|'false'):boolean=>{for(let i=0;i<value.length;i++)expect(value.charCodeAt(i));return value==='true';};
 whitespace();expect(0x7b);whitespace();
 let id:string|undefined,verified:boolean|undefined;const keys=new Set<string>();
 if(peek()!==0x7d){
  for(;;){
   const key=string();
   if(key!=='id'&&key!=='verified')fail('U0_DECODE_FIELD',cursor);
   if(keys.has(key))fail('U0_DECODE_DUPLICATE',cursor);keys.add(key);
   whitespace();expect(0x3a);whitespace();
   if(key==='id')id=string();
   else {const code=peek();if(code===0x74)verified=literal('true');else if(code===0x66)verified=literal('false');else fail('U0_DECODE_FIELD',cursor);}
   whitespace();if(peek()===0x7d)break;expect(0x2c);whitespace();
  }
 }
 expect(0x7d);whitespace();if(cursor!==text.length)fail('U0_DECODE_JSON',cursor);
 if(!keys.has('id')||!keys.has('verified'))fail('U0_DECODE_MISSING',cursor);
 const value=Object.freeze({id:id!,verified:verified!});
 return Object.freeze({value,work:Object.freeze({input_bytes:bytes.byteLength,source_code_units:text.length,cursor_advances:advances,code_unit_reads:reads,decoded_string_units:stringUnits})});
}
export function decodeU0Json(input:Uint8Array,maximumBytes:number):U0DecodedWireRecord {
 return inspectU0JsonDecode(input,maximumBytes).value;
}
