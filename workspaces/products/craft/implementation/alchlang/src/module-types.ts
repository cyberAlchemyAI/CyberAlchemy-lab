import {digest} from './domainspec-profile.js';
export type ModuleInterface={source_sha256:string;source_text:string;input:string;output:string;schemas:Record<string,any>;statuses:Record<string,number>};
export function moduleImports(source:string){return source.split(/\r?\n/).flatMap((line,index)=>{if(!line.startsWith('import '))return [];const m=/^import ([A-Z][A-Za-z0-9]*) from ("(?:[^"\\]|\\.)*")$/.exec(line);if(!m)throw Error(`ALCH_MODULE: ${index+1}: invalid import`);const file=JSON.parse(m[2]);if(typeof file!=='string'||!file.startsWith('.')||!file.endsWith('.alch'))throw Error(`ALCH_MODULE: ${index+1}: relative .alch import required`);return [{alias:m[1],file,line:index+1}];});}
export function linkModuleTypes(source:string,modules:Record<string,ModuleInterface>){
 const imports=moduleImports(source);if(new Set(imports.map(i=>i.alias)).size!==imports.length)throw Error('ALCH_MODULE: duplicate alias');
 if(JSON.stringify(imports.map(i=>i.alias).sort())!==JSON.stringify(Object.keys(modules).sort()))throw Error('ALCH_MODULE: source resolver required or unused module');
 for(const row of imports)if(new RegExp('^(?:entity|value-object|schema|calculation|mapping|query|rule|result|integration|endpoint) '+row.alias+':$','m').test(source))throw Error('ALCH_MODULE: alias conflicts with declaration');
 let linked=source.split(/\r?\n/).map(line=>line.startsWith('import ')?'':line.trimStart().startsWith('#')?line:line.replace(/"(?:[^"\\]|\\.)*"|(?<![\w.])([A-Z][A-Za-z0-9]*)\.(\w+)/g,(token,alias,name)=>{if(!alias||!modules[alias])return token;if(!modules[alias].schemas[name])throw Error(`ALCH_MODULE: unknown imported type ${token}`);return alias+'__'+name;})).join('\n');
 const origins:Record<string,number>={};for(const row of imports){const m=modules[row.alias];if(digest(m.source_text)!==m.source_sha256)throw Error('ALCH_MODULE: source digest');
  for(const [name,fields]of Object.entries(m.schemas)){const qualified=row.alias+'__'+name;origins[qualified]=row.line;linked+='\n\nschema '+qualified+':\n';for(const [field,s]of Object.entries(fields) as [string,any][]){const t=s.type==='list'?s.items:s.type;const target=m.schemas[t]?row.alias+'__'+t:t;linked+='  '+field+': '+target+(s.type==='list'?'[]':'')+Object.entries(s).filter(([k])=>!['type','items'].includes(k)).map(([k,v])=>['optional','nullable'].includes(k)?v?' '+k:'':' '+k+' '+JSON.stringify(v)).join('')+'\n';}}
 }
 return {source:linked,origins};
}
