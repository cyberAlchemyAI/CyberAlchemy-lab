/** Trusted standalone observer. Expected answers are deliberately absent. */
export const COMPOSITION_BEHAVIOR_RUNNER = String.raw`
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {pathToFileURL,fileURLToPath} from 'node:url';
class FixtureError extends Error {}
const fail=s=>{throw new FixtureError('COMPOSITION_RUNNER:'+s);},hash=v=>createHash('sha256').update(v).digest('hex');
function read(file,limit){
 if(fs.realpathSync(file)!==file)fail('symbolic path');
 const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK);
 try{const stat=fs.fstatSync(fd);if(!stat.isFile()||stat.size>limit)fail('file capacity');const value=fs.readFileSync(fd);if(value.length!==stat.size)fail('file changed');return value;}finally{fs.closeSync(fd);}
}
function budget(){let count=0,bytes=0;return {step:d=>{if(++count>20000||d>64)fail('value capacity');},text:s=>{if((bytes+=Buffer.byteLength(s))>8388608)fail('value bytes');}};}
function fields(v,array){
 const proto=Object.getPrototypeOf(v);if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('custom prototype');
 const keys=Reflect.ownKeys(v),length=array?Object.getOwnPropertyDescriptor(v,'length')?.value:0;
 if(keys.some(k=>typeof k!=='string')||(array?length>4096||keys.length!==length+1:keys.length>2048))fail('value shape');
 return (array?Array.from({length},(_,i)=>String(i)):keys).map(k=>{const d=Object.getOwnPropertyDescriptor(v,k);if(!d||!d.enumerable||!Object.hasOwn(d,'value'))fail('data properties');return [k,d.value];});
}
function encode(value){
 const b=budget(),active=new Set();
 const visit=(v,depth)=>{
  b.step(depth);if(v===undefined)return ['undefined'];if(v===null)return ['null'];
  if(typeof v==='boolean')return ['boolean',v];
  if(typeof v==='string'){b.text(v);return ['string',v];}
  if(typeof v==='bigint'){const s=String(v);b.text(s);return ['bigint',s];}
  if(typeof v==='number'){if(!Number.isFinite(v))fail('nonfinite');return ['number',Object.is(v,-0)?'-0':String(v)];}
  if(typeof v!=='object'||active.has(v))fail('inert acyclic value');active.add(v);
  const a=Array.isArray(v),out=fields(v,a).map(([k,x])=>{b.text(k);const next=visit(x,depth+1);return a?next:[k,next];});active.delete(v);return [a?'array':'record',out];
 };return visit(value,0);
}
function decode(value){
 const b=budget(),active=new Set(),array=v=>{if(!Array.isArray(v))fail('wire array');return fields(v,true).map(([,x])=>x);};
 const visit=(v,depth)=>{
  b.step(depth);const tuple=array(v);if(active.has(v))fail('wire cycle');active.add(v);
  const [tag,x]=tuple,done=out=>{active.delete(v);return out;};
  if(tag==='undefined'||tag==='null'){if(tuple.length!==1)fail('wire arity');return done(tag==='null'?null:undefined);}
  if(tuple.length!==2)fail('wire arity');
  if(tag==='boolean'&&typeof x==='boolean')return done(x);
  if(tag==='string'&&typeof x==='string'){b.text(x);return done(x);}
  if(tag==='number'&&typeof x==='string'){b.text(x);const n=Number(x);if(!Number.isFinite(n)||(Object.is(n,-0)?'-0':String(n))!==x)fail('wire number');return done(n);}
  if(tag==='bigint'&&typeof x==='string'){b.text(x);if(!/^(?:0|-?[1-9][0-9]*)$/.test(x))fail('wire bigint');return done(BigInt(x));}
  if(tag==='array')return done(array(x).map(y=>visit(y,depth+1)));
  if(tag==='record'){const out={},rows=array(x),seen=new Set();if(rows.length>2048)fail('wire record capacity');for(const row of rows){const pair=array(row),[key,field]=pair;if(pair.length!==2||typeof key!=='string'||seen.has(key))fail('wire record');seen.add(key);b.text(key);Object.defineProperty(out,key,{value:visit(field,depth+1),enumerable:true,writable:true,configurable:true});}if(JSON.stringify(Object.keys(out))!==JSON.stringify([...seen]))fail('wire field order');return done(out);}
  fail('wire tag');
 };return visit(value,0);
}
const [input,root,scriptHash,inputHash]=process.argv.slice(2),script=fileURLToPath(import.meta.url);
if(!path.isAbsolute(root)||path.resolve(root)!==root||fs.realpathSync(root)!==root)fail('module root');
const inputBytes=read(input,16777216);if(hash(read(script,8388608))!==scriptHash||hash(inputBytes)!==inputHash)fail('runner/input drift');
const selected=JSON.parse(inputBytes);
const keys=(v,names)=>v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).length===names.length&&names.every(n=>Object.hasOwn(v,n));
const digest=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
if(!keys(selected,['schema_version','control_sha256','binding_sha256','behavior_path','adapter_path','modules','cases'])||selected.schema_version!=='domainspec.composition-run-input/v1-candidate'||!digest(selected.control_sha256)||!digest(selected.binding_sha256))fail('input identity');
const safe=p=>typeof p==='string'&&p.length>0&&!p.includes('\0')&&!p.includes('\\')&&!path.posix.isAbsolute(p)&&!p.split('/').some(x=>!x||x==='.'||x==='..');
if(!Array.isArray(selected.modules)||!selected.modules.length||selected.modules.length>2048||selected.modules.some(m=>!keys(m,['relative_path','sha256'])||!safe(m.relative_path)||!digest(m.sha256)||!(/\.(?:js|mjs)$/).test(m.relative_path))||new Set(selected.modules.map(m=>m.relative_path)).size!==selected.modules.length)fail('module inventory');
if(!selected.modules.some(m=>m.relative_path===selected.behavior_path)||!selected.modules.some(m=>m.relative_path===selected.adapter_path))fail('entrypoint');
function current(){let size=0;for(const m of selected.modules){const bytes=read(path.join(root,m.relative_path),8388608);size+=bytes.length;if(size>67108864||hash(bytes)!==m.sha256)fail('native module drift');}if(hash(read(input,16777216))!==inputHash||hash(read(script,8388608))!==scriptHash)fail('runner/input drift');}
if(!Array.isArray(selected.cases)||!selected.cases.length||selected.cases.length>4095||new Set(selected.cases.map(c=>c.id)).size!==selected.cases.length)fail('case inventory');
for(const c of selected.cases){
 if(!keys(c,['id','request','input'])||typeof c.id!=='string'||!c.id.length||!c.request||typeof c.request!=='object'||Array.isArray(c.request)||Object.keys(c.request).some(k=>!['mode','binding','phase'].includes(k))||!['execute','validate-input'].includes(c.request.mode)||Object.hasOwn(c.request,'binding')&&typeof c.request.binding!=='string'||Object.hasOwn(c.request,'phase')&&!['guard','input'].includes(c.request.phase))fail('case shape');
 // Validate the complete input denominator before loading any target module.
 decode(c.input);
}
current();
const behavior=await import(pathToFileURL(path.join(root,selected.behavior_path)).href),api=await import(pathToFileURL(path.join(root,selected.adapter_path)).href);
if(typeof behavior.execute!=='function'||typeof behavior.validateInput!=='function'||typeof api.evaluateCalculation!=='function')fail('native callable');
const errorCode=error=>{
 if(error===null||!['object','function'].includes(typeof error))return 'EVALUATION_FAILED';
 const d=Object.getOwnPropertyDescriptors(error);if(['code','message'].some(k=>d[k]&&!Object.hasOwn(d[k],'value')))fail('error accessor');
 const code=d.code?.value,message=d.message?.value;
 return typeof code==='string'&&/^[A-Z][A-Z0-9_]*$/.test(code)?code:typeof message==='string'?message.match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0]??'EVALUATION_FAILED':'EVALUATION_FAILED';
};
const results=[];let totalBytes=0;
for(const c of selected.cases){
 const roots=decode(c.input),before=JSON.stringify(encode(roots)),observations=[];let outcome,observerFailure;
 const observe=e=>{try{if(observations.length>=20000)fail('observation capacity');observations.push(decode(encode(e)));}catch(error){observerFailure=error;throw error;}};
 try{const value=c.request.mode==='validate-input'?behavior.validateInput(roots,observe):behavior.execute(roots,api,observe,c.request.binding,c.request.phase);outcome={kind:'value',value};}
 catch(error){if(error instanceof FixtureError)throw error;outcome={kind:'error',code:errorCode(error)};}
 if(observerFailure)throw observerFailure;
 if(JSON.stringify(encode(roots))!==before)fail('input mutation');
 const row={id:c.id,observed:encode({outcome,observations}),input_changed:false};totalBytes+=Buffer.byteLength(JSON.stringify(row));if(totalBytes>16777216)fail('complete output capacity');results.push(row);
}
current();
const output=JSON.stringify({schema_version:'domainspec.composition-run-observation/v1-candidate',control_sha256:selected.control_sha256,binding_sha256:selected.binding_sha256,runner_sha256:scriptHash,input_sha256:inputHash,modules:selected.modules,cases:results});
if(Buffer.byteLength(output)>16777216)fail('complete output capacity');process.stdout.write(output);
`;
