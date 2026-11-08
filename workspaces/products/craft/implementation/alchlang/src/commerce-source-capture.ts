/** Original Alch source-file capture/currentness only. No Core graph/profile,
 * native handle or business decision is adopted here. Open Questions: EC06/CONTEXT.md. */
import {constants,openSync,closeSync,readSync,fstatSync,lstatSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {TextDecoder} from 'node:util';
import {commerceRelativePath,COMMERCE_SOURCE_LIMITS} from './commerce-source-lexer.js';
import {parseCommerceModuleSource} from './commerce-source-parser.js';
import {linkCommerceSourceModules,type CommerceLinkedSource} from './commerce-source-link.js';
import {sourceFail,commerceSyntaxDescendants as descendants,commerceSyntaxTokens as tokens,commerceSyntaxChildren as children,commerceSyntaxChild as child,commerceSyntaxText as text,
 type CommerceParsedModule,type CommerceSourceSpan} from './commerce-source-model.js';
export interface CommerceCapturedSource {readonly kind:'original-alch-commerce-source';readonly source_sha256:string}
export interface CommerceCapturedFile {readonly path:string;readonly sha256:string;readonly bytes:number;readonly kind:'module'|'contract'|'assurance'}
export interface CommerceCapturedInspection {readonly source_sha256:string;readonly application:string;readonly files:readonly CommerceCapturedFile[];readonly linked:CommerceLinkedSource;readonly authority_effect:'none'}
interface FileState {readonly relative:string;readonly physical:string;readonly device:bigint;readonly inode:bigint;readonly modified:bigint;readonly size:bigint;readonly text:string;readonly sha256:string;kind:CommerceCapturedFile['kind']}
interface CaptureState {readonly root:string;readonly supplied_root:string;readonly root_device:bigint;readonly root_inode:bigint;readonly files:ReadonlyMap<string,FileState>;readonly inspection:CommerceCapturedInspection;disposed:boolean}
const registry=new WeakMap<object,CaptureState>();
const sha=(bytes:string|Uint8Array)=>createHash('sha256').update(bytes).digest('hex');
const point=(name:string):CommerceSourceSpan=>({path:name,start:0,end:0});
function inside(root:string,file:string){const relative=path.relative(root,file);return relative!== '..'&&!relative.startsWith('..'+path.sep)&&!path.isAbsolute(relative);}
function readOriginal(root:string,relative:string,kind:FileState['kind']):FileState {
 commerceRelativePath(relative);const supplied=path.resolve(root,relative);let physical:string;
 try{physical=realpathSync(supplied);}catch{return sourceFail('UnknownReference',point(relative),'declared source/contract file is missing');}
 if(!inside(root,physical))sourceFail('InvalidContract',point(relative),'declared file escapes captured root');
 let fd:number;try{fd=openSync(physical,constants.O_RDONLY|constants.O_NOFOLLOW);}catch{return sourceFail('InvalidContract',point(relative),'declared file cannot be opened as an original regular file');}
 try{
  const before=fstatSync(fd,{bigint:true});if(!before.isFile())sourceFail('InvalidContract',point(relative),'regular source file required');
  if(before.size>BigInt(COMMERCE_SOURCE_LIMITS.source_bytes))sourceFail('ResourceLimit',point(relative),'declared file exceeds1MiB');
  const chunks:Buffer[]=[];let total=0;
  for(;;){const buffer=Buffer.alloc(Math.min(65536,COMMERCE_SOURCE_LIMITS.source_bytes+1-total)),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;total+=count;if(total>COMMERCE_SOURCE_LIMITS.source_bytes)sourceFail('ResourceLimit',point(relative),'declared file grew beyond byte cap');chunks.push(buffer.subarray(0,count));}
  const after=fstatSync(fd,{bigint:true}),current=realpathSync(supplied),named=lstatSync(current,{bigint:true});
  if(current!==physical||!inside(root,current)||before.dev!==after.dev||before.ino!==after.ino||before.size!==after.size||before.mtimeNs!==after.mtimeNs||named.ino!==after.ino||named.dev!==after.dev||BigInt(total)!==after.size)sourceFail('StaleOwner',point(relative),'source changed during capture');
  const bytes=Buffer.concat(chunks);let source:string;try{source=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);}catch{return sourceFail('Syntax',point(relative),'strict UTF8source required');}
  return {relative,physical,device:after.dev,inode:after.ino,modified:after.mtimeNs,size:after.size,text:source,sha256:sha(bytes),kind};
 }finally{closeSync(fd);}
}
export function parseCommerceContractJson(source:string,relative:string):unknown {
 let at=0,depth=0;const fail=(message:string):never=>sourceFail('Syntax',{path:relative,start:Buffer.byteLength(source.slice(0,at)),end:Buffer.byteLength(source.slice(0,at))},message);
 const skip=()=>{while(/[\x20\t\r\n]/.test(source[at]??'')&&at<source.length)at++;};
 const string=():string=>{const start=at++;while(at<source.length){if(source[at]==='\\')at+=2;else if(source[at++]==='"'){try{const value:unknown=JSON.parse(source.slice(start,at));if(typeof value!=='string'||Buffer.from(value).toString('utf8')!==value)return fail('invalid JSON Unicode scalar');return value;}catch{return fail('invalid JSON string');}}}return fail('unterminated JSON string');};
 const scan=():void=>{skip();if(++depth>32)sourceFail('ResourceLimit',point(relative),'contract JSON depth exceeds32');
  if(source[at]==='{'){at++;skip();const seen=new Set<string>();if(source[at]!=='}')for(;;){skip();if(source[at]!=='"')fail('expected JSON key');const key=string();if(seen.has(key))fail('duplicate contract JSON key');seen.add(key);skip();if(source[at++]!==':')fail('expected JSON colon');scan();skip();if(source[at]!==',')break;at++;}if(source[at++]!=='}')fail('expected JSON object close');}
  else if(source[at]==='['){at++;skip();if(source[at]!==']')for(;;){scan();skip();if(source[at]!==',')break;at++;}if(source[at++]!==']')fail('expected JSON array close');}
  else if(source[at]==='"')string();
  else {const m=/^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(source.slice(at));if(!m)fail('invalid JSON value');at+=m![0].length;if(/^-?\d/.test(m![0])&&!Number.isSafeInteger(Number(m![0])))sourceFail('InvalidContract',point(relative),'contract numbers must be safe integers;business UInt64uses string wire');}
  depth--;
 };
 if(Buffer.byteLength(source)>COMMERCE_SOURCE_LIMITS.source_bytes)sourceFail('ResourceLimit',point(relative),'contract exceeds byte bound');scan();skip();if(at!==source.length)fail('trailing contract JSON');try{return JSON.parse(source) as unknown;}catch{return fail('invalid contract JSON');}
}
function pointer(value:unknown,fragment:string,span:CommerceSourceSpan):unknown {if(!fragment)return value;if(!fragment.startsWith('/'))sourceFail('UnknownReference',span,'JSONpointer must start with /');let current=value;for(const part of fragment.slice(1).split('/')){if(/~(?![01])/.test(part))sourceFail('UnknownReference',span,'malformed JSONpointer escape');const key=part.replace(/~1/g,'/').replace(/~0/g,'~');if(!current||typeof current!=='object'||!Object.hasOwn(current,key))sourceFail('UnknownReference',span,'contract JSONpointer is missing');current=(current as Record<string,unknown>)[key];}return current;}
const object=(value:unknown,at:CommerceSourceSpan):Record<string,unknown>=>{if(!value||typeof value!=='object'||Array.isArray(value))return sourceFail('InvalidContract',at,'contract object required');return value as Record<string,unknown>;};
export function captureCommerceSource(rootPath:string,applicationPath='application.alch'):CommerceCapturedSource {
 commerceRelativePath(applicationPath);const supplied_root=path.resolve(rootPath);let root:string;try{root=realpathSync(supplied_root);if(!lstatSync(root).isDirectory())throw Error('directory');}catch{return sourceFail('InvalidContract',point(applicationPath),'existing application root directory required');}
 const root_stat=lstatSync(root,{bigint:true});
 const files=new Map<string,FileState>(),parsed=new Map<string,CommerceParsedModule>(),contracts=new Map<string,unknown>();let total=0;
 const read=(relative:string,kind:FileState['kind'])=>{const prior=files.get(relative);if(prior){if(prior.kind!==kind)sourceFail('InvalidContract',point(relative),'file has conflicting capture roles');return prior;}if(files.size>=128)sourceFail('ResourceLimit',point(relative),'captured file count exceeds128');const file=readOriginal(root,relative,kind);total+=Number(file.size);if(total>COMMERCE_SOURCE_LIMITS.total_bytes)sourceFail('ResourceLimit',point(relative),'source/asset closure exceeds4MiB');files.set(relative,file);return file;};
 const module=(relative:string)=>{if(parsed.has(relative))sourceFail('DuplicateSymbol',point(relative),'duplicate declared source path');if(parsed.size>=32)sourceFail('ResourceLimit',point(relative),'too many modules');if(!relative.endsWith('.alch'))sourceFail('InvalidContract',point(relative),'module path must end in .alch');const value=parseCommerceModuleSource(read(relative,'module').text,relative);parsed.set(relative,value);return value;};
 const initial=module(applicationPath),applications=initial.declarations.filter(d=>d.kind==='Interface'&&d.interface_kind==='application-composition');if(applications.length!==1)sourceFail('InvalidContract',initial.syntax,'application root needs one composition Interface');const application=applications[0]!;
 const appClauses=descendants(application.syntax,'application-clause');
 for(const clause of appClauses)if(tokens(clause)[0]?.text==='source')module(text(child(clause,'reference')));
 const loadContract=(reference:string,from:string,at:CommerceSourceSpan)=>{
  const [name,fragment='']=reference.split('#');if(reference.split('#').length>2)sourceFail('InvalidContract',at,'multiple reference fragments');
  // Slash-containing paths are application-root relative. A bare contract
  // basename is relative to its declaring module (context.json in contracts).
  const relative=commerceRelativePath(name!.includes('/')?name!:path.posix.join(path.posix.dirname(from),name!));if(!relative.endsWith('.json'))sourceFail('InvalidContract',at,'registered contract reference must name JSON');
  let value=contracts.get(relative);if(value===undefined){value=parseCommerceContractJson(read(relative,'contract').text,relative);contracts.set(relative,value);}pointer(value,fragment,at);return {relative,value};
 };
 let identities:unknown;
 for(const m of parsed.values())for(const d of m.declarations){
  if(d.kind==='FormalClaim'){const [name,fragment]=d.reference.split('#');if(fragment!==undefined)sourceFail('InvalidContract',d.span,'formal model source cannot be a JSONpointer');const relative=commerceRelativePath(name!.includes('/')?name!:path.posix.join(path.posix.dirname(m.path),name!));read(relative,'assurance');continue;}
  if(d.kind!=='Interface')continue;
  for(const clause of descendants(d.syntax,'interface-clause')){
   const head=tokens(clause)[0]?.text,refs=descendants(clause,'reference');if(!refs.length)continue;
   const applicationReference=descendants(clause,'application-reference').length>0;
   if(!applicationReference&&!['binding','family-contract','obligations','signatures','fields','methods','variants'].includes(head??''))continue;
   for(const ref of refs){const result=loadContract(text(ref),m.path,ref);if(head==='source-identities')identities=result.value;}
  }
 }
 if(identities!==undefined){
  const data=object(identities,initial.syntax);if(data.schema_version!=='craft.commerce-source-contract-identities/v1-candidate')sourceFail('UnsupportedCapability',initial.syntax,'unknown source identity contract version');
  if(!Array.isArray(data.modules)||!Array.isArray(data.contract_assets))sourceFail('InvalidContract',initial.syntax,'identity contract requires module/asset arrays');
  const expectedModules=new Set<string>();
  for(const raw of data.modules){const item=object(raw,initial.syntax),artifact=object(item.artifact,initial.syntax),relative=commerceRelativePath(String(artifact.path)),actual=parsed.get(relative);if(expectedModules.has(relative))sourceFail('DuplicateSymbol',initial.syntax,'duplicate identity module');expectedModules.add(relative);if(!actual||actual.module!==item.module||item.version!==1||actual.sha256!==artifact.sha256||actual.bytes!==artifact.bytes)sourceFail('StaleOwner',point(relative),'source identity contract differs from actual captured module');}
  if(expectedModules.size!==parsed.size)sourceFail('MissingMapping',initial.syntax,'identity contract omits declared source');
  const expectedAssets=new Set<string>();for(const raw of data.contract_assets){const item=object(raw,initial.syntax),relative=commerceRelativePath(String(item.path));if(expectedAssets.has(relative))sourceFail('DuplicateSymbol',point(relative),'duplicate identity asset');expectedAssets.add(relative);const file=read(relative,'contract');if(file.sha256!==item.sha256||Number(file.size)!==item.bytes)sourceFail('StaleOwner',point(relative),'contract identity differs from actual file');if(!contracts.has(relative))contracts.set(relative,parseCommerceContractJson(file.text,relative));}
  for(const file of files.values())if(file.kind==='contract'&&!expectedAssets.has(file.relative)&&contracts.get(file.relative)!==identities)sourceFail('MissingMapping',point(file.relative),'identity contract omits referenced contract');
 }
 const linked=linkCommerceSourceModules([...parsed.values()],application.id,contracts),rows=[...files.values()].map(f=>Object.freeze({path:f.relative,sha256:f.sha256,bytes:Number(f.size),kind:f.kind})).sort((a,b)=>Buffer.compare(Buffer.from(a.path),Buffer.from(b.path)));
 const source_sha256=sha(JSON.stringify(rows)),inspection:CommerceCapturedInspection=Object.freeze({source_sha256,application:application.id,files:Object.freeze(rows),linked,authority_effect:'none'}),handle:CommerceCapturedSource=Object.freeze({kind:'original-alch-commerce-source',source_sha256});
 registry.set(handle,{root,supplied_root,root_device:root_stat.dev,root_inode:root_stat.ino,files,inspection,disposed:false});assertCommerceSourceCurrent(handle);return handle;
}
function original(handle:CommerceCapturedSource):CaptureState {const state=handle&&typeof handle==='object'?registry.get(handle):undefined;if(!state)sourceFail('ForeignOwner',point('application.alch'),'actual original Alch source handle required');if(state.disposed)sourceFail('DisposedOwner',point('application.alch'),'source handle is disposed');return state;}
export function assertCommerceSourceCurrent(handle:CommerceCapturedSource):void {
 const state=original(handle);let root:string;try{root=realpathSync(state.supplied_root);}catch{return sourceFail('StaleOwner',point('application.alch'),'source root is missing');}const root_stat=lstatSync(root,{bigint:true});if(root!==state.root||root_stat.dev!==state.root_device||root_stat.ino!==state.root_inode)sourceFail('StaleOwner',point('application.alch'),'source root changed');
 for(const before of state.files.values()){
  let now:FileState;try{now=readOriginal(state.root,before.relative,before.kind);}catch{return sourceFail('StaleOwner',point(before.relative),'captured source/asset no longer readable/current');}
  if(now.physical!==before.physical||now.device!==before.device||now.inode!==before.inode||now.modified!==before.modified||now.size!==before.size||now.sha256!==before.sha256)sourceFail('StaleOwner',point(before.relative),'captured source/asset changed');
 }
}
export function inspectCommerceSource(handle:CommerceCapturedSource):CommerceCapturedInspection {assertCommerceSourceCurrent(handle);return original(handle).inspection;}
export function disposeCommerceSource(handle:CommerceCapturedSource):void {const state=original(handle);state.disposed=true;}
