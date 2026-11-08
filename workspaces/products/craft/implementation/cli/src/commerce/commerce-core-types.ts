/** Explicit Core source type environment for pure semantic reconstruction.
 * Retains source refinement minima/literals rather than erasing them to String.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreFreeze,coreSourceFail as fail,coreSourceChildren,coreSourceTokens,type CoreSourceRange} from './commerce-core-syntax.js';
import type {CoreCommerceType,CoreCommerceDeclaration,CoreCommerceModule,CoreCommerceReconstruction} from './commerce-core-reconstruction.js';
export type CoreValueType=
 {readonly kind:'UInt64'}|{readonly kind:'Bool'}|{readonly kind:'String';readonly max_bytes:number;readonly max_scalars:number}|
 {readonly kind:'literal';readonly value:string}|{readonly kind:'record'|'enum'|'refinement';readonly name:string}|
 {readonly kind:'variant';readonly name:string;readonly variant:string}|
 {readonly kind:'optional';readonly value:CoreValueType}|{readonly kind:'List';readonly value:CoreValueType;readonly maximum:number}|
 {readonly kind:'outcome';readonly state:CoreValueType;readonly intent:CoreValueType;readonly maximum:number};
export interface CoreRefinement {readonly name:string;readonly min_bytes:number;readonly max_bytes:number;readonly min_scalars:number;readonly max_scalars:number;readonly pattern:string|null}
export interface CoreValueTypes {
 readonly modules:ReadonlyMap<string,CoreCommerceModule>;readonly declarations:ReadonlyMap<string,CoreCommerceDeclaration>;
 resolve(module:string,name:string,where:CoreSourceRange):CoreCommerceDeclaration;
 type(module:string,value:CoreCommerceType,where:CoreSourceRange):CoreValueType;
 fields(type:CoreValueType,where:CoreSourceRange):readonly {readonly name:string;readonly type:CoreValueType}[];
 readonly refinements:ReadonlyMap<string,CoreRefinement>;
}
export const CORE_UINT64:CoreValueType=Object.freeze({kind:'UInt64'}),CORE_BOOL:CoreValueType=Object.freeze({kind:'Bool'});
export function sameCoreValueType(a:CoreValueType,b:CoreValueType):boolean {return JSON.stringify(a)===JSON.stringify(b);}
export function acceptsCoreValueType(expected:CoreValueType,actual:CoreValueType):boolean {
 if(sameCoreValueType(expected,actual))return true;
 if(expected.kind==='List'&&actual.kind==='List')return actual.maximum<=expected.maximum&&acceptsCoreValueType(expected.value,actual.value);
 if(expected.kind==='optional'&&actual.kind==='optional')return acceptsCoreValueType(expected.value,actual.value);
 if(expected.kind==='enum'&&actual.kind==='variant')return expected.name===actual.name;
 return false;
}
/** No code executes from a refinement. Its registered finite regular-language
 * subset has only anchored ASCII literals/classes and finite repetitions. */
export function checkCoreRefinementPattern(pattern:string,where:CoreSourceRange):void {
 if(pattern.length>4096||pattern[0]!=='^'||pattern.at(-1)!=='$')fail('UnsupportedCapability',where,'refinement pattern needs finite anchored subset');
 let at=1;while(at<pattern.length-1){const c=pattern[at]!;
  if(c==='['){const end=pattern.indexOf(']',at+1);if(end<0||end===at+1||/[^A-Za-z0-9_ -]/.test(pattern.slice(at+1,end)))fail('UnsupportedCapability',where,'finite ASCII character class required');at=end+1;}
  else if(/[A-Za-z0-9_ -]/.test(c))at++;
  else fail('UnsupportedCapability',where,'unregistered refinement regex operator');
  if(pattern[at]==='{'){const quantifier=/^\{([0-9]+)(?:,([0-9]+))?\}/.exec(pattern.slice(at));if(!quantifier)fail('UnsupportedCapability',where,'finite regex repetition required');const low=BigInt(quantifier[1]!),high=BigInt(quantifier[2]??quantifier[1]!);if(low>high||high>1048576n)fail('ResourceLimit',where,'pattern repetition bound');at+=quantifier[0].length;}
 }
 try{new RegExp(pattern,'u');}catch{fail('InvalidContract',where,'invalid finite regular expression');}
}
/** Finite membership, with an explicit work ceiling. Even bounded overlapping
 * repetitions must not acquire the host regex engine's backtracking behavior. */
export function matchesCoreRefinementPattern(pattern:string,value:string,where:CoreSourceRange):boolean {
 checkCoreRefinementPattern(pattern,where);const atoms:{chars:ReadonlySet<string>;min:number;max:number}[]=[];let at=1;
 while(at<pattern.length-1){const chars=new Set<string>();if(pattern[at]==='['){const end=pattern.indexOf(']',at+1),body=pattern.slice(at+1,end);for(let i=0;i<body.length;i++){if(body[i+1]==='-'&&i+2<body.length){for(let n=body.charCodeAt(i);n<=body.charCodeAt(i+2);n++)chars.add(String.fromCharCode(n));i+=2;}else chars.add(body[i]!);}at=end+1;}else chars.add(pattern[at++]!);
  let min=1,max=1;if(pattern[at]==='{'){const q=/^\{([0-9]+)(?:,([0-9]+))?\}/.exec(pattern.slice(at))!;min=Number(q[1]);max=Number(q[2]??q[1]);at+=q[0].length;}atoms.push({chars,min,max});
 }
 const scalars=[...value];let positions=new Set([0]),work=0;
 for(const atom of atoms){const next=new Set<number>();for(const start of positions){if(atom.min===0)next.add(start);let n=0;while(n<atom.max&&start+n<scalars.length){if(++work>1000000)fail('ResourceLimit',where,'finite refinement membership work limit');if(!atom.chars.has(scalars[start+n]!))break;n++;if(n>=atom.min)next.add(start+n);}}positions=next;if(!positions.size)return false;}
 return positions.has(scalars.length);
}
export function createCoreValueTypes(reconstruction:CoreCommerceReconstruction):CoreValueTypes {
 const modules=new Map(reconstruction.modules.map(m=>[m.module,m])),declarations=new Map(reconstruction.modules.flatMap(m=>m.declarations.map(d=>[d.id,d]as const))),refinements=new Map<string,CoreRefinement>();
 const resolve=(module:string,name:string,where:CoreSourceRange)=>{
  const m=modules.get(module);if(!m)fail('UnknownReference',where,'source module absent');const id=declarations.has(module+'.'+name)?module+'.'+name:m.imports.find(i=>i.alias===name)?.target??name;
  const result=declarations.get(id);if(!result)fail('UnknownReference',where,'exact source type/declaration absent '+name);return result;
 };
 for(const d of declarations.values())if(d.refinement){
  const singleton=new Map<string,readonly string[]>();
  for(const clause of coreSourceChildren(d.syntax,'record-clause')){const ts=coreSourceTokens(clause).filter(t=>!t.layout).map(t=>t.token);singleton.set(ts[0]!,ts);}
  const bound=(key:string,required:boolean):[number,number]|null=>{const ts=singleton.get(key);if(!ts){if(required)fail('MissingMapping',d.syntax,'refinement requires explicit '+key);return null;}const lo=ts[1]!,hi=ts[3]!;if(!/^(0|[1-9][0-9]*)$/.test(lo)||!/^(0|[1-9][0-9]*)$/.test(hi)||BigInt(lo)>BigInt(hi)||BigInt(hi)>1048576n)fail('InvalidContract',d.syntax,'refinement finite min/max bounds');return [Number(lo),Number(hi)];};
  const bytes=bound('utf8-bytes',true)!,scalars=bound('unicode-scalars',false)??[0,bytes[1]],pattern=singleton.get('pattern');
  if(scalars[0]>bytes[1]||bytes[0]>4*scalars[1])fail('InvalidContract',d.syntax,'refinement domain has incompatible byte/scalar bounds');
  const expression=pattern?JSON.parse(pattern[1]!)as string:null;if(expression!==null)checkCoreRefinementPattern(expression,d.syntax);
  refinements.set(d.id,coreFreeze({name:d.id,min_bytes:bytes[0],max_bytes:bytes[1],min_scalars:scalars[0],max_scalars:scalars[1],pattern:expression}));
 }
 const type=(module:string,value:CoreCommerceType,where:CoreSourceRange):CoreValueType=>{
  switch(value.kind){case'UInt64':return CORE_UINT64;case'Bool':return CORE_BOOL;case'String':return reconstruction.capture_mode==='event-handoff-entry'?{kind:'String',max_bytes:256,max_scalars:256}:fail('MissingMapping',where,'unbounded String requires a declared bounded expected context');case'literal':return {kind:'literal',value:value.value};
   case'named':{const d=resolve(module,value.name,where);if(d.refinement)return {kind:'refinement',name:d.id};if(d.surface==='Enum')return {kind:'enum',name:d.id};if(['Entity','ValueObject','Event'].includes(d.surface))return {kind:'record',name:d.id};return fail('TypeMismatch',where,'private owner/callable cannot become a pure serializable value');}
   case'optional':return {kind:'optional',value:type(module,value.value,where)};
   case'List':return {kind:'List',value:type(module,value.value,where),maximum:value.maximum};
   case'outcome':return {kind:'outcome',state:type(module,value.state,where),intent:type(module,value.intent,where),maximum:value.maximum};
  }
 };
 const fields=(t:CoreValueType,where:CoreSourceRange):readonly {name:string;type:CoreValueType}[]=>{
  if(t.kind==='record'||t.kind==='variant'){const d=declarations.get(t.name);if(!d)fail('UnknownReference',where,'record/enum source declaration absent');const variant=t.kind==='variant'?t.variant:null,fs=variant===null?d.fields:d.variants.find(v=>v.name===variant)?.fields;if(!fs)fail('UnknownReference',where,'variant absent');return fs.map(f=>({name:f.name,type:type(d.module,f.type,f.span)}));}
  if(t.kind==='outcome')return [{name:'tag',type:{kind:'String',max_bytes:10,max_scalars:10}},{name:'state',type:t.state},{name:'intents',type:{kind:'List',value:t.intent,maximum:t.maximum}},{name:'machine',type:{kind:'String',max_bytes:256,max_scalars:256}},{name:'branch',type:{kind:'String',max_bytes:256,max_scalars:256}},{name:'reason',type:{kind:'String',max_bytes:256,max_scalars:256}}];
  return fail('TypeMismatch',where,t.kind==='optional'?'optional value must be narrowed or explicitly unwrapped before field access':'field access requires a declared record/variant/outcome');
 };
 return Object.freeze({modules,declarations,refinements,resolve,type,fields});
}
export function coreStringDomain(type:CoreValueType,types:CoreValueTypes):CoreRefinement|null {
 if(type.kind==='refinement')return types.refinements.get(type.name)??null;
 if(type.kind==='literal')return {name:'literal',min_bytes:Buffer.byteLength(type.value),max_bytes:Buffer.byteLength(type.value),min_scalars:[...type.value].length,max_scalars:[...type.value].length,pattern:null};
 if(type.kind==='String')return {name:'String',min_bytes:0,max_bytes:type.max_bytes,min_scalars:0,max_scalars:type.max_scalars,pattern:null};return null;
}

export type CoreGenericAdmissionMode='technical-profile'|'bounded-values'|'state-proposals'|'keyed-query-entry'|'atomic-state-entry'|'external-read-entry'|'external-write-entry'|'event-handoff-entry';
export function coreGenericAdmissionMode(value:unknown='bounded-values'):CoreGenericAdmissionMode {
 if(value!=='technical-profile'&&value!=='bounded-values'&&value!=='state-proposals'&&value!=='keyed-query-entry'&&value!=='atomic-state-entry'&&value!=='external-read-entry'&&value!=='external-write-entry'&&value!=='event-handoff-entry')fail('InvalidContract',{path:'generic-admission',start:0,end:0},'exact registered generic admission mode required');return value;
}
export function assertCoreGenericNullaryControl(types:CoreValueTypes,type:CoreValueType,where:CoreSourceRange):void {
 if(type.kind!=='enum')fail('TypeMismatch',where,'StateMachine control requires a declared enum');
 const declaration=types.declarations.get(type.name);if(!declaration||declaration.surface!=='Enum')fail('TypeMismatch',where,'StateMachine control requires an actual enum declaration');
 if(declaration.variants.some(v=>v.fields.length))fail('UnsupportedCapability',where,'StateMachine controls require nullary enums');
}
/** The same check covers declaration/import types and local expression binders. */
export function assertCoreGenericValueType(types:CoreValueTypes,type:CoreValueType,where:CoreSourceRange,mode:CoreGenericAdmissionMode='bounded-values'):void {
 coreGenericAdmissionMode(mode);
 const inspect=(type:CoreValueType,where:CoreSourceRange,depth=0):void=>{
  if(depth>64)fail('ResourceLimit',where,'generic value nesting bound');
  if(type.kind==='optional'){if(type.value.kind==='optional')fail('TypeMismatch',where,'adjacent Optional is not a generic wire type');inspect(type.value,where,depth+1);}
  else if(type.kind==='List'){if(type.maximum>100)fail('ResourceLimit',where,'generic List maximum is 100');inspect(type.value,where,depth+1);}
  else if(type.kind==='outcome'){
   if(mode==='bounded-values'||mode==='technical-profile')fail('UnsupportedCapability',where,'StateMachine outcome is outside this generic phase');
   assertCoreGenericNullaryControl(types,type.state,where);
   if(type.intent.kind!=='Bool'||type.maximum!==0)fail('UnsupportedCapability',where,'generic StateMachine outcome requires Bool and zero intents');
  }
 };
 inspect(type,where);
}
/** Resolve actual source/imported declarations before enforcing generic shapes. */
export function assertCoreGenericValueTypes(types:CoreValueTypes,mode:CoreGenericAdmissionMode='bounded-values'):void {
 coreGenericAdmissionMode(mode);const inspect=(type:CoreValueType,where:CoreSourceRange)=>assertCoreGenericValueType(types,type,where,mode);
 for(const d of types.declarations.values()){
  if(d.surface==='StateMachine'&&(mode==='bounded-values'||mode==='technical-profile'))fail('UnsupportedCapability',d.syntax,'StateMachine requires explicit state-proposals admission');
  if(d.surface==='StateMachine')for(const p of d.parameters)assertCoreGenericNullaryControl(types,types.type(d.module,p.type,p.span),p.span);
  for(const f of [...d.fields,...d.variants.flatMap(v=>v.fields),...d.parameters])inspect(types.type(d.module,f.type,f.span),f.span);
  if(d.result)inspect(types.type(d.module,d.result,d.syntax),d.syntax);
 }
}
