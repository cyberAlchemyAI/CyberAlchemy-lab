import assert from 'node:assert/strict';
import {existsSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Source workspace check only. Public frontend packages use local generated data;
// no installed consumer reads a sibling Core checkout. Open Questions: U0-SHARED-CONTRACTS.md.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const alch=path.resolve(core,'../alchlang');
export const BUSINESS_MIRROR_FILES_V2=Object.freeze([
 'business-authoring-protocol-v2.ts','business-authoring-identity-protocol-v2.ts',
 'business-authoring-coverage-contract-v2.ts','business-authoring-contract-registry-v2.ts',
 'business-authoring-stages-v2.ts','u0-realization-contract.ts',
]);
export function expectedBusinessMirrorV2(name,source){
 assert(BUSINESS_MIRROR_FILES_V2.includes(name),'fixed Core mirror inventory required');
 let body=source;
 if(name==='u0-realization-contract.ts'){
  const marker='/** Checks the actual finite native configuration domain only.';
  assert.equal(source.split(marker).length,2,'native data/implementation boundary changed');
  body=source.slice(0,source.indexOf(marker)).replace(/^import .*;\n/gm,'');
 }else if(name==='business-authoring-coverage-contract-v2.ts'){
  const marker='const frozen=';
  assert.equal(source.split(marker).length,2,'coverage data/implementation boundary changed');
  body=source.slice(0,source.indexOf(marker)).replace(/^import (?!type ).*;\n/gm,'');
 }
 assert(!/^import (?!type )/m.test(body),'a shared data mirror cannot import a runtime owner');
 assert(!/export (?:async )?function\s/.test(body),'a shared data mirror cannot implement a runtime owner');
 return `// GENERATED from Core ${name}; canonical owner is Core.\n`+body;
}
export function checkBusinessMirrorV2(name,source,actual){
 assert.equal(actual,expectedBusinessMirrorV2(name,source),`Core/Alch contract mirror drift:${name}`);
}
export function materializeBusinessMirrorsV2(write=false){
 const rows=[];
 for(const name of BUSINESS_MIRROR_FILES_V2){
  const source=readFileSync(path.join(core,'src/profile-engine',name),'utf8');
  const target=path.join(alch,'src',name),expected=expectedBusinessMirrorV2(name,source);
  if(write&&(!existsSync(target)||readFileSync(target,'utf8')!==expected))writeFileSync(target,expected);
  checkBusinessMirrorV2(name,source,readFileSync(target,'utf8'));
  rows.push({file:name,bytes:Buffer.byteLength(expected),owner:'Core',projection:'data-only'});
 }
 return rows;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 assert(process.argv.slice(2).every(arg=>arg==='--write'||arg==='--check'),'only --write or --check allowed');
 assert(process.argv.slice(2).length<=1,'one explicit materialization mode required');
 process.stdout.write(JSON.stringify({result:'pass',mirrors:materializeBusinessMirrorsV2(process.argv.includes('--write'))})+'\n');
}
