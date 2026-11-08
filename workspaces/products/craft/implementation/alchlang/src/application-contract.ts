import {readFileSync,realpathSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {loadAlchLangSource} from './source-file.js';
import {lowerDomainSpec} from './lower-domainspec.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
// Syntax/lowering only. DomainSpec owns semantic checks and generation; ../APPLICATION.md.
type Decl={kind:string;id:string;file:string;line:number;[key:string]:any};
const hash=(x:string|Buffer)=>createHash('sha256').update(x).digest('hex');
const fail=(s:string):never=>{throw Error('ALCH_APPLICATION: '+s);};
const identifier=(s:unknown):s is string=>typeof s==='string'&&/^[A-Za-z][A-Za-z0-9_]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);
function safeJson(x:any){if(x&&typeof x==='object'){for(const k of Object.keys(x)){if(['constructor','prototype','__proto__'].includes(k))fail('unsafe key');safeJson(x[k]);}}}
function parseApplication(sourcePath:string){
 if(path.extname(sourcePath)!=='.alch')fail('application source extension');sourcePath=realpathSync(sourcePath);const root=path.dirname(sourcePath),seen=new Set<string>(),active=new Set<string>(),declarations:Decl[]=[],sources:Record<string,string>={};
 function file(from:string,ref:unknown){if(typeof ref!=='string'||path.isAbsolute(ref))return fail('relative source required');const p=path.resolve(path.dirname(from),ref);if(!p.startsWith(root+path.sep))return fail('source escapes application root');let current=root;for(const part of path.relative(root,p).split(path.sep)){current=path.join(current,part);if(lstatSync(current).isSymbolicLink())fail('source symlink');}if(!lstatSync(p).isFile())fail('source must be a file');return realpathSync(p);}
 function bind(from:string,ref:string){const p=file(from,ref);sources[path.relative(root,p)]=hash(readFileSync(p));return p;}
 function visit(p:string){if(path.extname(p)!=='.alch')fail('module source extension');if(active.has(p))fail('cyclic import');if(seen.has(p))return;if(seen.size>=32)fail('module limit');seen.add(p);active.add(p);const source=readFileSync(p,'utf8');if(Buffer.byteLength(source)>131072)fail('module size limit');sources[path.relative(root,p)]=hash(source);let block:Decl|undefined;const top:Record<string,string>={};
  for(const [i,line]of source.split(/\r?\n/).entries()){
   if(!line.trim()||line.trimStart().startsWith('#'))continue;
   if(line.startsWith('  ')){const m=/^  ([a-z]+) (.+)$/.exec(line);if(!block||!m||Object.hasOwn(block,m[1]!))fail(p+':'+(i+1)+' duplicate/invalid clause');let v;try{v=JSON.parse(m![2]!);}catch{return fail(p+':'+(i+1)+' clause value must be JSON');}safeJson(v);block![m![1]!]=v;continue;}
   block=undefined;const imp=/^import ([A-Z][A-Za-z0-9]*) from ("[^"\n]+")$/.exec(line);if(imp){visit(file(p,JSON.parse(imp[2]!)));continue;}
   const decl=/^([a-z]+) ([A-Z][A-Za-z0-9]*):$/.exec(line);if(decl){if(!identifier(decl[2]))fail('unknown declaration');if(declarations.some(d=>d.id===decl[2]))fail('duplicate declaration '+decl[2]);block={kind:decl[1]!,id:decl[2]!,file:p,line:i+1};declarations.push(block);continue;}
   const m=/^(domain|profile|owner) (.+)$/.exec(line);if(!m||Object.hasOwn(top,m[1]!))fail(p+':'+(i+1)+' invalid header');top[m![1]!]=m![2]!;
  }
  if(top.profile!=='bound-application-v1'||!top.domain||!top.owner)fail('application profile/domain/owner required');active.delete(p);
 }
 visit(sourcePath);
 const core_projects:Record<string,Record<string,string>>={};
 for(const d of declarations.filter(d=>d.kind==='model')){
  const source=bind(d.file,d.source),sidecar=bind(d.file,d.source+'.domainspec.json');
  const bytes=readFileSync(source,'utf8');const lowered=lowerDomainSpec(loadAlchLangSource(source).carrier,JSON.parse(readFileSync(sidecar,'utf8')),bytes);
  if(lowered.bindings.profile!==d.profile)fail('core profile binding mismatch');
  core_projects[d.id]=lowered.files;
 }
 return {root,ontology:{schema_version:'domainspec.application-ontology/v1-candidate',profile:'bound-application-v1',declarations:declarations.map(d=>({...d,file:path.relative(root,d.file)})),sources,core_projects,authority_effect:'none'}};
}
export async function loadApplication(source:string){const parsed=parseApplication(source);const compiler=await loadDomainSpecCompiler();return compiler.loadApplicationOntology(parsed.ontology,parsed.root);}
export async function checkApplication(source:string){const parsed=parseApplication(source);const compiler=await loadDomainSpecCompiler();return compiler.checkApplicationOntology(parsed.ontology,parsed.root);}
export async function buildApplication(source:string,output:string){const parsed=parseApplication(source);const compiler=await loadDomainSpecCompiler();return compiler.buildApplicationOntology(parsed.ontology,parsed.root,path.resolve(output));}
