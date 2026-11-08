/** Candidate D45 outbound composition. Semantics/Open Questions: ../../OUTBOUND-COMPOSITION.md. */
export const OUTBOUND_COMPOSITION_PROFILE = 'domainspec.outbound-composition/v1-candidate';
export const OUTBOUND_COMPOSITION_PROFILE_V2 = 'domainspec.outbound-composition/v2-candidate';
export type Shape = {type: string | Record<string, Shape>; items?: string | Record<string, Shape>; optional?: boolean; nullable?: boolean; [key: string]: unknown};
export interface LocalInterface {input: Shape; output: Shape}
export interface OutboundComposition {
 schema_version: typeof OUTBOUND_COMPOSITION_PROFILE | typeof OUTBOUND_COMPOSITION_PROFILE_V2;
 input: Shape;
 modules: Record<string, LocalInterface>;
 limits: {deadline_ms:number; max_bytes:number; max_concurrent:number; max_attempts:1};
 steps: Array<Record<string, any>>;
 output: string;
}
const fail=(message:string):never=>{throw Error('DS_OUTBOUND: '+message);};
const safe=(s:unknown):s is string=>typeof s==='string'&&/^[A-Za-z][A-Za-z0-9_]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);
const record=(v:any):v is Record<string,any>=>!!v&&typeof v==='object'&&!Array.isArray(v);
function keys(v:any,required:string[],optional:string[]=[]){if(!record(v)||required.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>![...required,...optional].includes(k)))fail('unknown or missing field');}
function shape(s:any,depth=0):void{
 if(depth>32)fail('shape depth');keys(s,['type'],['items','optional','nullable','min','max','pattern','const']);
 for(const k of ['optional','nullable'])if(k in s&&typeof s[k]!=='boolean')fail('shape qualifier');
 if(record(s.type)){for(const [k,v]of Object.entries(s.type)){if(!safe(k))fail('shape field');shape(v,depth+1);}}
 else if(!['string','identifier','integer','boolean','list'].includes(s.type))fail('shape type');
 if(s.type==='list'){if(!s.items)fail('list items');shape({type:s.items},depth+1);}else if('items'in s)fail('unexpected items');
 for(const k of ['min','max'])if(k in s&&(!Number.isSafeInteger(s[k])||s[k]<0))fail('shape bound');
 if('pattern'in s){if(typeof s.pattern!=='string'||s.pattern.length>1024)fail('shape pattern');try{new RegExp(s.pattern);}catch{fail('shape pattern');}}
}
function accepts(target:Shape,source:Shape):boolean{
 if(source.optional&&!target.optional||source.nullable&&!target.nullable)return false;
 if(record(target.type)){if(!record(source.type))return false;const t=target.type as Record<string,Shape>,s=source.type as Record<string,Shape>;return Object.entries(t).every(([k,v])=>s[k]?accepts(v,s[k]):v.optional)&&Object.keys(s).every(k=>Object.hasOwn(t,k));}
 if(target.type!==source.type&&!(target.type==='string'&&source.type==='identifier'))return false;
 if(target.type==='list'&&!accepts({type:target.items!},{type:source.items!}))return false;
 if(target.min!==undefined&&(source.min===undefined||Number(source.min)<Number(target.min)))return false;
 if(target.max!==undefined&&(source.max===undefined||Number(source.max)>Number(target.max)))return false;
 if(target.pattern!==undefined&&target.pattern!==source.pattern)return false;
 if(Object.hasOwn(target,'const')&&target.const!==source.const)return false;
 return true;
}
export function compileOutboundComposition(value:unknown){
 const c=JSON.parse(JSON.stringify(value)) as OutboundComposition;
 keys(c,['schema_version','input','modules','limits','steps','output']);if(c.schema_version!==OUTBOUND_COMPOSITION_PROFILE&&c.schema_version!==OUTBOUND_COMPOSITION_PROFILE_V2)fail('profile');shape(c.input);
 keys(c.limits,['deadline_ms','max_bytes','max_concurrent','max_attempts']);
 for(const [k,max]of Object.entries({deadline_ms:c.schema_version===OUTBOUND_COMPOSITION_PROFILE_V2?300000:5000,max_bytes:65536,max_concurrent:128,max_attempts:1}))if(!Number.isSafeInteger((c.limits as any)[k])||(c.limits as any)[k]<1||(c.limits as any)[k]>max)fail('limit '+k);
 if(!record(c.modules)||Object.keys(c.modules).length>32)fail('module bound');
 for(const [name,m]of Object.entries(c.modules)){if(!safe(name))fail('module name');keys(m,['input','output']);shape(m.input);shape(m.output);}
 if(!Array.isArray(c.steps)||c.steps.length<1||c.steps.length>32)fail('step bound');
 const first=c.steps[0]!;if(first.kind!=='local'||first.args!=='input'||!c.modules[first.module]||!accepts(c.input,c.modules[first.module]!.input)||!accepts(c.modules[first.module]!.input,c.input))fail('first step must validate complete input');
 const scope:Record<string,Shape>={input:c.input};let http=0;const bindings=new Set<string>(),used=new Set<string>();
 const ref=(p:any):Shape=>{if(typeof p!=='string'||p.split('.').some(k=>!safe(k)))return fail('reference');const parts=p.split('.');let s:Shape=scope[parts.shift()!]??fail('forward or missing reference '+p);for(const k of parts){if(s.optional||s.nullable||!record(s.type)||!Object.hasOwn(s.type,k))return fail('unsafe reference '+p);s=(s.type as Record<string,Shape>)[k]??fail('missing field');}return s;};
 const args=(a:any):Shape=>{if(typeof a==='string')return ref(a);if(!record(a))return fail('arguments');return {type:Object.fromEntries(Object.entries(a).map(([k,p])=>{if(!safe(k))fail('argument name');return [k,ref(p)];}))};};
 const code=(s:any)=>{if(typeof s!=='string'||!/^[A-Z][A-Z0-9_]{0,127}$/.test(s))fail('error code');};
 for(const s of c.steps){if(!safe(s.id)||Object.hasOwn(scope,s.id))fail('duplicate/unsafe step');
  if(s.kind==='local'){
   keys(s,['id','kind','module','args','error'],['accept','reject']);code(s.error);
   const m=c.modules[s.module]??fail('missing module');used.add(s.module);if(!accepts(m.input,args(s.args)))fail('incompatible local input '+s.id);
   if(s.accept!==undefined){if(typeof s.accept!=='string'||!record(m.output.type)||!['string','identifier'].includes(String((m.output.type as any).status?.type)))fail('status guard');code(s.reject);}else if(s.reject!==undefined)fail('reject without guard');scope[s.id]=m.output;
  }else if(s.kind==='binding'){
   keys(s,['id','kind','binding_id','version','model','policy']);
   for(const k of ['binding_id','version','model','policy'])if(!['string','identifier'].includes(String(ref(s[k]).type)))fail('binding identity type');
   const id:Shape={type:'identifier',max:128};scope[s.id]={type:{id,version:id,model:id,remote_model:id}};bindings.add(s.id);
  }else if(s.kind==='http'){
   keys(s,['id','kind','binding','body','omit','output','stream','identity']);
   if(++http>1||!bindings.has(s.binding))fail('one fixed-bound attempt required');
   const b=ref(s.body);if(!record(b.type)||b.optional||b.nullable)fail('request object');if(!Array.isArray(s.omit)||new Set(s.omit).size!==s.omit.length||s.omit.some((k:any)=>!safe(k)||!Object.hasOwn(b.type as Record<string,Shape>,k)))fail('omit field');
   const stream=ref(s.stream);if(stream.type!=='boolean'||stream.optional||stream.nullable)fail('stream flag');
   keys(s.identity,['request_id','model']);for(const p of Object.values(s.identity))if(!['string','identifier'].includes(String(ref(p).type)))fail('stream identity');
   const out=/^([A-Za-z][A-Za-z0-9_]*)\.input$/.exec(s.output);if(!out||!c.modules[out[1]!])fail('raw response interface');scope[s.id]=c.modules[out![1]!]!.input;const next=c.steps[c.steps.indexOf(s)+1];if(!next||next.kind!=='local'||next.module!==out![1]||next.args!==s.id)fail('raw response must be decoded by the next local step');
  }else fail('unsupported step kind');
 }
 if(http!==1)fail('one attempt required');if(Object.keys(c.modules).some(k=>!used.has(k)))fail('unused module');const output=ref(c.output);if(output.optional||output.nullable)fail('required output');
 return {contract:c,output,trace:{schema_version:'domainspec.outbound-composition-trace/v1-candidate',steps:c.steps.map((s,index)=>({index,id:s.id,kind:s.kind,output:scope[s.id]})),authority_effect:'none' as const}};
}

export const validateCompositionShape=shape;
