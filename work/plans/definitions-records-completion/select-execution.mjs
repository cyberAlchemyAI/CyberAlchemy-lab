import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';import path from 'node:path';
import {captureImplementation} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),put=(f,v)=>writeFileSync(path.resolve(root,f),JSON.stringify(v,null,2)+'\n'),load=f=>JSON.parse(readFileSync(path.resolve(root,f))),binding=f=>{const raw=readFileSync(path.resolve(root,f));return {path:f,sha256:digest(raw),bytes:raw.length};},P=path.relative(root,here);
const priorManifest=path.join(here,'EXECUTION-MANIFEST.json');if(existsSync(priorManifest)){const prior=load(priorManifest);mkdirSync(path.join(here,'implementation-history'),{recursive:true});put(P+'/implementation-history/'+prior.digest+'.json',prior);}
const manifest=captureImplementation();put(P+'/EXECUTION-MANIFEST.json',manifest);
const trust=load(P+'/runtime-trust.json')??{};
trust.implementation=binding(P+'/EXECUTION-MANIFEST.json');
put(P+'/runtime-trust.json',trust);
const previous=load(P+'/PREVIOUS-EXECUTION-SELECTION.json');
put('authority/profiles/shared-records/current.json',{...previous,implementation:manifest.digest,execution_manifest:trust.implementation,authorization:binding(P+'/AUTHORIZATION.json'),supersedes:binding(P+'/PREVIOUS-EXECUTION-SELECTION.json'),reason:'User-authorized nine-finding definitions and records workflow repair; original model and signed artifacts remain historically qualified.'});
const active=load('implementation/lab-runtime/shared-workflow.json');active.trust=P+'/runtime-trust.json';active.execution_selection=binding('authority/profiles/shared-records/current.json');put('implementation/lab-runtime/shared-workflow.json',active);console.log(manifest.digest);
