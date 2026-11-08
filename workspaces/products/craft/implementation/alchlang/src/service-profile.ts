import {moduleImports} from './module-types.js';

export type ServiceEntryDeclaration={id:string;functionAlias:string;meaning:string|null;ontology:string|null;line:number};
export type ServiceSource={domain:string;service:{id:string;meaning:string|null;ontology:string|null;line:number};imports:ReturnType<typeof moduleImports>;entries:ServiceEntryDeclaration[]};

const fail=(message:string):never=>{throw Error('ALCH_SERVICE: '+message);};
const safe=(value:string)=>/^[A-Za-z_][A-Za-z0-9_]*$/.test(value)&&!['__proto__','constructor','prototype'].includes(value);
const quoted=(value:string,label:string):string=>{let parsed:unknown;try{parsed=JSON.parse(value);}catch{return fail(label+' must be quoted');}if(typeof parsed!=='string'||!parsed.trim())fail(label+' must be nonempty');return parsed as string;};

export function parseServiceSource(source:string):ServiceSource{
 if(source.startsWith('\uFEFF')||source.includes('```'))fail('plain UTF-8 .alch required');
 const domainRows=[...source.matchAll(/^domain ([A-Za-z0-9_-]+)(?:\s+"(?:[^"\\]|\\.)*")?$/gm)];
 if(domainRows.length!==1)fail('exactly one domain required');
 const profiles=[...source.matchAll(/^profile (.+)$/gm)];if(profiles.length!==1||profiles[0][1]!=='service-v1')fail('profile service-v1 must appear once');
 const imports=moduleImports(source);if(imports.length<1)fail('at least one function import required');
 const blocks:{kind:'service'|'entry';id:string;rows:string[];line:number}[]=[];let current:typeof blocks[number]|undefined;
 const lines=source.split(/\r?\n/);
 for(let index=0;index<lines.length;index++){
  const line=lines[index];
  if(!line.trim()||line.trimStart().startsWith('#'))continue;
  if(/^\S/.test(line)){
   current=undefined;
   if(/^domain |^profile |^owner |^import /.test(line))continue;
   const match=/^(service|entry) ([A-Za-z_][A-Za-z0-9_]*):$/.exec(line);
   if(match===null)fail(`line ${index+1}: unsupported declaration`);
   current={kind:match![1] as 'service'|'entry',id:match![2],rows:[],line:index+1};blocks.push(current);continue;
  }
  if(!current||!/^  \S/.test(line))fail(`line ${index+1}: two-space service clause required`);
  current!.rows.push(line.trim());
 }
 const services=blocks.filter(b=>b.kind==='service');if(services.length!==1)fail('exactly one service required');
 const entryBlocks=blocks.filter(b=>b.kind==='entry');if(entryBlocks.length<2)fail('a service requires at least two entries');if(entryBlocks.length>32)fail('entry limit');
 const annotations=(block:typeof blocks[number],allowed:string[])=>{const values:Record<string,string>={};for(const row of block.rows){const match=/^(\S+) (.+)$/.exec(row);if(match===null||!allowed.includes(match[1])||Object.hasOwn(values,match[1]))fail(`invalid or duplicate ${block.kind} clause ${row}`);values[match![1]]=match![2];}return values;};
 const serviceValues=annotations(services[0],['meaning','ontology']);
 if(serviceValues.ontology&&!/^"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+"$/.test(serviceValues.ontology))fail('service ontology identity');
 const service={id:services[0].id,meaning:serviceValues.meaning?quoted(serviceValues.meaning,'service meaning'):null,ontology:serviceValues.ontology?quoted(serviceValues.ontology,'service ontology'):null,line:services[0].line};
 const aliases=new Set(imports.map(row=>row.alias)),entryIds=new Set<string>(),used=new Set<string>();
 const entries=entryBlocks.map(block=>{
  if(!safe(block.id)||entryIds.has(block.id))fail('duplicate or unsafe entry');entryIds.add(block.id);
  const values=annotations(block,['function','meaning','ontology']);
  if(!values.function||!safe(values.function)||!aliases.has(values.function))fail('entry function binding');
  if(used.has(values.function))fail('function import may be exposed once');used.add(values.function);
  if(values.ontology&&!/^"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+"$/.test(values.ontology))fail('entry ontology identity');
  return {id:block.id,functionAlias:values.function,meaning:values.meaning?quoted(values.meaning,'entry meaning'):null,ontology:values.ontology?quoted(values.ontology,'entry ontology'):null,line:block.line};
 });
 if(used.size!==imports.length)fail('every function import must be exposed exactly once');
 return {domain:domainRows[0][1],service,imports,entries};
}
