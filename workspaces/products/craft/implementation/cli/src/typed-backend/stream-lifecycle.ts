import {validateCompositionShape} from './outbound-composition.js';
/** Candidate stream contract. Meanings/Open Questions: ../../STREAM-LIFECYCLE.md. */
export const STREAM_LIFECYCLE_PROFILE='domainspec.stream-lifecycle/v1-candidate';
const fail=(s:string):never=>{throw Error('DS_STREAM: '+s);};
const safe=(s:any)=>typeof s==='string'&&/^[A-Za-z][A-Za-z0-9_]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);
const record=(v:any)=>v&&typeof v==='object'&&!Array.isArray(v);
function keys(v:any,required:string[]){if(!record(v)||required.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>!required.includes(k)))fail('unknown or missing fields');}
const canonical=(v:any):string=>JSON.stringify(v,(_k,x)=>record(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
export function compileStreamLifecycle(value:unknown){
 const c=JSON.parse(JSON.stringify(value)) as any;
 keys(c,['schema_version','initial','open','terminal','transitions','frames','provider_events','errors','limits','modules']);if(c.schema_version!==STREAM_LIFECYCLE_PROFILE)fail('profile');
 keys(c.terminal,['complete','fail','cancel']);const states=[c.initial,c.open,...Object.values(c.terminal)];if(states.some(s=>!safe(s))||new Set(states).size!==5)fail('distinct lifecycle states');
 keys(c.limits,['max_bytes','max_event_bytes','max_frame_bytes']);for(const [k,max]of Object.entries({max_bytes:65536,max_event_bytes:16384,max_frame_bytes:65536}))if(!Number.isSafeInteger(c.limits[k])||c.limits[k]<1||c.limits[k]>max)fail('byte bounds');
 const expected=[{from:c.initial,event:'start',to:c.open},...['fail','cancel'].map(event=>({from:c.initial,event,to:c.terminal[event]})),{from:c.open,event:'delta',to:c.open},...['complete','fail','cancel'].map(event=>({from:c.open,event,to:c.terminal[event]}))];
 if(!Array.isArray(c.transitions)||c.transitions.length!==expected.length)fail('transition coverage');
 for(const t of c.transitions){keys(t,['from','event','to']);if(!expected.some(e=>canonical(e)===canonical(t)))fail('illegal lifecycle transition');}
 if(new Set(c.transitions.map(canonical)).size!==expected.length)fail('duplicate transition');
 keys(c.frames,['start','delta','complete','fail']);keys(c.provider_events,['delta','complete','fail']);if(Object.values(c.provider_events).some(v=>!safe(v))||new Set(Object.values(c.provider_events)).size!==3)fail('provider events');
 keys(c.errors,['eof','unknown','provider','invalid']);for(const v of Object.values(c.errors))if(typeof v!=='string'||!/^[A-Z][A-Z0-9_]{0,127}$/.test(v))fail('error code');
 if(!record(c.modules)||Object.keys(c.modules).length!==4||Object.keys(c.modules).some(k=>!safe(k)))fail('four frame modules');
 const used=new Set<string>(),events=new Set<string>();let identity:any;
 for(const kind of ['start','delta','complete','fail']){
  const f=c.frames[kind];keys(f,['module','event']);if(!safe(f.module)||!safe(f.event)||events.has(f.event))fail('frame binding');events.add(f.event);used.add(f.module);
  const m=c.modules[f.module];keys(m,['input','output']);validateCompositionShape(m.input);validateCompositionShape(m.output);if(m.input.optional||m.input.nullable||m.output.optional||m.output.nullable)fail('required frame interfaces');const fields=m.input?.type,output=m.output?.type?.value;
  if(!record(fields)||!record(fields.identity?.type)||fields.identity.optional||fields.identity.nullable||!record(output?.type)||output.optional||output.nullable)fail('frame interfaces');
  const names=kind==='start'?['identity']:kind==='fail'?['identity','code']:['identity','event'];keys(fields,names);
  if(!identity){identity=fields.identity;const values=Object.values(identity.type) as any[];if(!values.length||values.length>16||values.some(v=>v.optional||v.nullable||!['string','identifier','integer','boolean'].includes(v.type)))fail('bounded scalar identity required');}else if(canonical(identity)!==canonical(fields.identity))fail('identity mismatch');
  if(kind==='fail'&&(fields.code?.type!=='string'||fields.code.optional||fields.code.nullable||fields.code.max!==256))fail('failure code interface');
  if(['delta','complete'].includes(kind)&&(!record(fields.event?.type)||fields.event.optional||fields.event.nullable))fail('provider event interface');
  for(const [key,type]of Object.entries(identity.type))if(canonical(type)!==canonical(output.type[key]))fail('frame identity field');
 }
 if(used.size!==4||Object.keys(c.modules).some(k=>!used.has(k)))fail('unused or repeated frame module');
 return {contract:c,trace:{schema_version:'domainspec.stream-lifecycle-trace/v1-candidate',transitions:c.transitions,frames:c.frames,identity,authority_effect:'none'}};
}
