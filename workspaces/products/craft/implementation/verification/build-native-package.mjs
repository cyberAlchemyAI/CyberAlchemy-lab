// Ordinary mutable distribution build; no release publication or sealed candidate.
// Open Questions: README.md.
import {mkdirSync,readdirSync,readFileSync,writeFileSync,lstatSync} from 'node:fs';
import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(import.meta.dirname,'..'),source=path.join(root,'profiles/ai');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function stageNativePackage(destination){
 if(!path.isAbsolute(destination))throw Error('Absolute task-owned destination required');mkdirSync(destination,{recursive:true});const files=[];
 const copy=relative=>{const from=path.join(source,relative),stat=lstatSync(from);if(!stat.isFile()||stat.isSymbolicLink())throw Error('Regular native distribution file required');const bytes=readFileSync(from),to=path.join(destination,relative);mkdirSync(path.dirname(to),{recursive:true});writeFileSync(to,bytes);if(sha(readFileSync(from))!==sha(bytes))throw Error('Source changed during native package build: '+relative);files.push({path:relative,sha256:sha(bytes),bytes:bytes.length});};
 for(const name of ['package.json','npm-shrinkwrap.json','README.md','LICENSE'])copy(name);
 const walk=relative=>{for(const e of readdirSync(path.join(source,relative),{withFileTypes:true})){if(e.isSymbolicLink())throw Error('No native distribution source links');if(e.isDirectory()){if(!['node_modules','sdk-test','fixtures','test','.work'].includes(e.name))walk(relative+'/'+e.name);}else if(!/\.(test|spec)[.]mjs$/.test(e.name)&&!['parser.test.mjs','retrieval.test.mjs','package-lock.json'].includes(e.name)&&/\.(mjs|json|md|alch)$/.test(e.name))copy(relative+'/'+e.name);}};walk('native');
 for(const e of readdirSync(path.join(source,'profiles'),{withFileTypes:true}))if(e.isFile()&&e.name.endsWith('.json'))copy('profiles/'+e.name);
 return {schema_version:'craft.native-distribution-build/v1',destination,files:files.sort((a,b)=>a.path.localeCompare(b.path)),qualification:'working-local-distribution;not-provider-ready'};
}
if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url){if(!process.argv[2])throw Error('Supply task-owned destination');console.log(JSON.stringify(stageNativePackage(path.resolve(process.argv[2]))));}
