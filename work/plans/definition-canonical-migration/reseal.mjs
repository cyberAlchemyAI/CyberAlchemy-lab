import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';import path from 'node:path';
import {captureImplementation} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),load=f=>JSON.parse(readFileSync(f)),put=(f,v)=>writeFileSync(f,JSON.stringify(v,null,2)+'\n'),binding=f=>({path:path.relative(root,f),sha256:digest(readFileSync(f)),bytes:readFileSync(f).length});
const selected=captureImplementation(),mf=path.join(here,'EXECUTION-MANIFEST.json');const old=load(mf);mkdirSync(path.join(here,'implementation-history'),{recursive:true});put(path.join(here,'implementation-history',old.digest+'.json'),old);put(mf,selected);
const tf=path.join(here,'runtime-trust.json'),trust=load(tf);trust.implementation=binding(mf);put(tf,trust);
const sf=path.join(root,'authority/profiles/shared-records/current.json'),selection=load(sf);selection.implementation=selected.digest;selection.execution_manifest=binding(mf);put(sf,selection);
const cf=path.join(root,'implementation/lab-runtime/shared-workflow.json'),config=load(cf);config.execution_selection=binding(sf);put(cf,config);console.log(selected.digest);
