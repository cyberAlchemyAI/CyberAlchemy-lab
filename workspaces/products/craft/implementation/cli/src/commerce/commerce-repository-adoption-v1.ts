/** Exact-byte adoption of a previously generated private repository directory.
 * It creates no files and grants no store, query, or execution authority.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import {createHash} from 'node:crypto';
import {lstatSync,readdirSync} from 'node:fs';
import {stripTypeScriptTypes} from 'node:module';
import path from 'node:path';
import {coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCorePhysicalCaptures,readCorePhysicalFile,type CorePhysicalFile} from './commerce-core-physical.js';

const where={path:'service-sqlite-repository-adoption',start:0,end:0};
const hash=(text:string)=>createHash('sha256').update(text).digest('hex');
const memberName=(name:string)=>name!=='.'&&name!=='..'&&/^[A-Za-z0-9._-]+$/.test(name)&&!name.includes('/')&&
 !name.includes('\\')&&name.length<=255;

export interface CommerceAdoptedRepositoryV1 {
 readonly files:readonly CorePhysicalFile[];
 readonly physical:Readonly<{assertCurrent():void}>;
}

/** The caller supplies freshly emitted source/profile output. Adopt only when
 * every on-disk member, including each JS twin and the manifest, matches it. */
export function adoptCommerceGeneratedRepositoryV1(
 directory:string,generated:Readonly<{files:readonly Readonly<{path:string;text:string}>[];manifest:Readonly<Record<string,unknown>>}>,
):CommerceAdoptedRepositoryV1 {
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory||
  directory.endsWith(path.sep)||directory.length>4096)
  fail('InvalidContract',where,'normalized absolute repository directory required');
 let directoryStat:ReturnType<typeof lstatSync>;
 try{directoryStat=lstatSync(directory);}catch{return fail('StaleOwner',where,'existing generated repository directory required');}
 if(!directoryStat.isDirectory()||directoryStat.isSymbolicLink()||(directoryStat.mode&0o077)!==0)
  fail('StaleOwner',where,'private nonsymlink repository directory required');
 const expected=new Map<string,string>();
 const add=(name:string,text:string)=>{
  if(!memberName(name)||expected.has(name)||typeof text!=='string')
   fail('InvalidContract',where,'unique flat generated repository member required');
  expected.set(name,text);
 };
 for(const member of generated.files){
  add(member.path,member.text);
  if(member.path.endsWith('.ts'))add(member.path.slice(0,-3)+'.js',stripTypeScriptTypes(member.text));
 }
 add('repository-manifest.json',JSON.stringify(generated.manifest,null,2)+'\n');
 const names=[...expected.keys()].sort();
 const checkMembers=()=>{
  let found:string[];
  try{found=readdirSync(directory).sort();}catch{return fail('StaleOwner',where,'generated repository directory unavailable');}
  if(found.some(name=>!expected.has(name)))fail('InvalidContract',where,'unexpected generated repository member');
  if(found.length!==names.length||found.some((name,index)=>name!==names[index]))
   fail('StaleOwner',where,'generated repository member is missing');
 };
 checkMembers();
 const files:CorePhysicalFile[]=[];
 for(const [name,text] of expected){
  const actual=readCorePhysicalFile(path.join(directory,name));
  if(actual.file.bytes!==Buffer.byteLength(text)||actual.file.sha256!==hash(text)||actual.text!==text)
   fail('StaleOwner',where,'generated repository member differs from selected source and profile');
  files.push(actual);
 }
 checkMembers();
 const captured=pinCorePhysicalCaptures(files);
 const physical=Object.freeze({assertCurrent(){captured.assertCurrent();checkMembers();}});
 physical.assertCurrent();
 return Object.freeze({files:Object.freeze(files),physical});
}
