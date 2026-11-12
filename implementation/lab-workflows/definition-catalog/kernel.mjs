import {readFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {implementationRoot as craftRoot} from '../../../workspaces/products/craft/implementation/source-bindings.mjs';
import {createSourceOperationCompiler} from '../../artifact-runtime/compile-source-operation.mjs';
import {evaluateArtifact} from '../../artifact-runtime/pure-operation.mjs';
const here=import.meta.dirname,sha=b=>createHash('sha256').update(b).digest('hex');
export const source=sha(JSON.stringify(['placement.alch','application.alch','../../lab-runtime/alchlang/shared-records/contracts/bounds.json'].map(f=>[f,sha(readFileSync(path.join(here,f)))])));
export const output=path.join(here,'.local',source);
export async function place(value){
 if(!existsSync(path.join(output,'manifest.json'))){mkdirSync(path.dirname(output),{recursive:true});const c=await createSourceOperationCompiler(path.join(craftRoot,'cli'));c.compile({modelRoot:path.resolve(here,'../../..'),applicationPath:'implementation/lab-workflows/definition-catalog/application.alch',pureSources:true,selector:'Lab.DefinitionCatalog.PlaceDefinition',outputDirectory:output});}
 const r=await evaluateArtifact(output,'operation.mjs',{value},{manifest_sha256:sha(readFileSync(path.join(output,'manifest.json')))});if(!r.ok)throw Error(JSON.stringify(r.error));const v=JSON.parse(new TextDecoder().decode(r.wire));if(v.tag!=='Returned')throw Error(v.fields.code);return v.fields.value;
}

export function destination(root,plan){
 for(const segment of [plan.folder,plan.version])if(!/^[A-Za-z0-9._-]+$/.test(segment)||segment==='.'||segment==='..')throw Error('unsafe-definition-path');
 const home=path.resolve(root,plan.home),target=path.resolve(home,plan.area,plan.collection,plan.folder,plan.version);
 if(home!==root&&!home.startsWith(root+path.sep)||!target.startsWith(home+path.sep))throw Error('definition-path-outside-workspace');
 return target;
}

function canonical(value){if(Array.isArray(value))return value.map(canonical);if(value!==null&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])]));return value;}
export function semanticDigest(definition){
 const keys=['term','aliases','semantic_owner_ref','scope','voices','boundaries','typed_relations','primary_consumer_refs','evidence_refs','residue_refs','claim_ceiling'];
 return sha(Buffer.from(JSON.stringify(canonical(Object.fromEntries(keys.map(k=>[k,definition[k]]))))));
}

export function folderName(term){const name=term.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');if(!name)throw Error('readable-definition-name-required');return name;}
