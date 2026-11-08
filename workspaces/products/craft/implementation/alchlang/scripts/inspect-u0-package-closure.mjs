#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {materializePackageBoundaries,validatePackageBoundaries} from './materialize-package-boundaries.mjs';
// Fresh private prototype closure; never refresh the historical release allowlist.
// Open Questions: H01 provisional installed runner and F00 fixed candidate freeze.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export function inspectU0PackageClosure(){
 const boundaries=materializePackageBoundaries();validatePackageBoundaries(boundaries);
 const core=boundaries.packages.find(p=>p.id==='core'),repo=path.resolve(root,'../../../../../..'),craft=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
 const requiredFrontend=['dist/business-authoring-project-v2.js','dist/business-authoring-command-v2.js','dist/business-authoring-prepare.js','dist/application-executable.js','dist/core-cli.js','runtime-sources/boundary-runtime.ts'];
 for(const file of requiredFrontend)if(!core.files.includes(file))throw Error('U0_FRONTEND_CLOSURE_MISSING:'+file);
 const requiredCraft=['dist/profile-engine/u0-bootstrap-v4.js','dist/profile-engine/loader-v4.js','contracts/business-support-cell-v2.schema.json','contracts/business-output-result-v2.schema.json','profiles/node-http-entry-u0-v4/profile.json'];
 const descriptor=JSON.parse(fs.readFileSync(path.join(craft,'profiles/node-http-entry-u0-v4/profile.json'),'utf8'));
 for(const file of [...requiredCraft,...descriptor.assets.map(a=>'profiles/node-http-entry-u0-v4/'+a.path)])if(!boundaries.domainspec_cli.expanded_files.includes(file))throw Error('U0_CRAFT_CLOSURE_MISSING:'+file);
 const artifacts=(packageRoot,files)=>files.map(file=>{const bytes=fs.readFileSync(path.join(packageRoot,file));return {path:file,sha256:sha(bytes),bytes:bytes.length};});
 return {schema_version:'craft.u0-package-closure/v1-candidate',frontend:{name:core.name,files:artifacts(root,core.files.filter(f=>f!=='package.json'&&f!=='README.md')),exports:core.exports,bin:core.bin},craft:{name:boundaries.domainspec_cli.name,files:artifacts(craft,boundaries.domainspec_cli.expanded_files)},historical_release_allowlist_modified:false,installed_qualification:'not-performed',publication_performed:false,authority_effect:'none',open_questions_ref:'docs/BUSINESS-AUTHORING.md'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(inspectU0PackageClosure(),null,2));
