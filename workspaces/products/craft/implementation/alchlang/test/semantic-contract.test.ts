import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import test from 'node:test';
import {buildSemanticContract,checkSemanticContract,compileSemanticContract,executeSemanticOperation} from '../src/semantic-contract.js';

const sourcePath=path.resolve(import.meta.dirname,'../../extensions/semantic-contract-v1/semantic-prelude.alch');
const fixturePath=path.resolve(path.dirname(sourcePath),'semantic-prelude.fixtures.json');
const files=(root:string):string[]=>readdirSync(root,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(path.join(root,entry.name)):[path.join(root,entry.name)]);
const temporary=(t:{after(fn:()=>void):void})=>{const root=mkdtempSync(path.join(os.tmpdir(),'alch-semantic-contract-test-'));t.after(()=>rmSync(root,{recursive:true,force:true}));return root;};
const sha=(value:string|Buffer)=>createHash('sha256').update(value).digest('hex');

test('semantic contract declares canonical concepts and validates bounded fixtures',async()=>{
 const compiled=await compileSemanticContract(sourcePath),check=await checkSemanticContract(sourcePath);
 assert.equal(check.status,'valid');assert.deepEqual(check.validations,{total:11,passed:11,failed:0});
 assert.equal(compiled.declarations.filter(item=>item.kind==='axiom').length,4);
 assert.equal(compiled.declarations.filter(item=>item.kind==='invariant').length,7);
 assert.equal(compiled.declarations.filter(item=>item.kind==='governed-by').length,1);
 assert.equal(compiled.ontology.ontology_admitted,false);assert.equal(compiled.ontology.constitution_adopted,false);
 assert.ok(compiled.ontology.nodes.every(node=>typeof node.id==='string'&&node.id.length>0));
 assert.equal(compiled.report.status,'pass');assert.match(compiled.report.claim,/Finite fixtures only/);
});

test('runtime operations preserve non-collapse, normalization and ordered distinct reasons',()=>{
 assert.equal(executeSemanticOperation('normalize-nfkc','Café'),'Café');
 assert.equal(executeSemanticOperation('canonical-text','  ＤＥＦＩＮＥ  '),'define');
 assert.equal(executeSemanticOperation('semantic-key',' Release—Gate '),'release gate');
 assert.equal(executeSemanticOperation('contains-token',{text:'predefined runtime',token:'define'}),false);
 assert.equal(executeSemanticOperation('contains-token',{text:'define runtime',token:'define'}),true);
 assert.equal(executeSemanticOperation('contains-phrase',{text:'The release-gate is ready',phrase:'release gate'}),true);
 assert.equal(executeSemanticOperation('contains-phrase',{text:'A predefined runtime',phrase:'define'}),false);
 assert.deepEqual(executeSemanticOperation('append-reason',{reasons:['scope-open'],reason:'language-open'}),['scope-open','language-open']);
 assert.deepEqual(executeSemanticOperation('append-reason',{reasons:['scope-open'],reason:'scope-open'}),['scope-open']);
 assert.deepEqual(executeSemanticOperation('append-reason',{reasons:[],reason:'ＤＥＦＩＮＥ'}),['ＤＥＦＩＮＥ']);
});

test('build is deterministic and traverses ontology then Craft compilation',async t=>{
 const root=temporary(t),first=path.join(root,'first'),second=path.join(root,'second');await buildSemanticContract(sourcePath,first);await buildSemanticContract(sourcePath,second);
 const firstFiles=files(first).map(file=>path.relative(first,file)).sort(),secondFiles=files(second).map(file=>path.relative(second,file)).sort();assert.deepEqual(firstFiles,secondFiles);
 for(const relative of firstFiles)assert.deepEqual(readFileSync(path.join(first,relative)),readFileSync(path.join(second,relative)),relative);
 const manifest=JSON.parse(readFileSync(path.join(first,'manifest.json'),'utf8'));assert.deepEqual(manifest.pipeline,['alch-source','semantic-contract-ontology','craft-project','domainspec-compile','runtime-projection','fixture-validation']);
 for(const [relative,expected] of Object.entries(manifest.files))assert.equal(sha(readFileSync(path.join(first,relative))),expected);
 const certificate=JSON.parse(readFileSync(path.join(first,'evidence/craft/certificate.json'),'utf8'));assert.equal(certificate.compiler.package,'@domainspec-v2/cli');assert.equal(certificate.authority_effect,'none');
 const runtime=await import(pathToFileURL(path.join(first,'app/prelude.mjs')).href);assert.equal(runtime.invoke('contains-token',{text:'predefined',token:'define'}),false);
});

test('semantic contract fails closed on Law, unresolved grounding, authority activation and failed fixtures',async t=>{
 const root=temporary(t),source=readFileSync(sourcePath,'utf8'),fixtures=readFileSync(fixturePath,'utf8');
 const attempt=async(name:string,sourceBytes:string,fixtureBytes=fixtures)=>{const dir=path.join(root,name);await import('node:fs').then(fs=>fs.mkdirSync(dir));writeFileSync(path.join(dir,'semantic-prelude.alch'),sourceBytes);writeFileSync(path.join(dir,'semantic-prelude.fixtures.json'),fixtureBytes);return compileSemanticContract(path.join(dir,'semantic-prelude.alch'));};
 await assert.rejects(attempt('law',source.replace('axiom UnicodeRepresentationMultiplicity:','law UnicodeRepresentationMultiplicity:')),/unsupported top-level statement/);
 await assert.rejects(attempt('grounding',source.replace('grounded-by UnicodeRepresentationMultiplicity','grounded-by MissingAxiom')),/grounded-by must reference axiom/);
 await assert.rejects(attempt('authority',source.replace('  adopted false','  adopted true')),/constitutions must remain candidate/);
 await assert.rejects(attempt('fixture',source,fixtures.replace('"expected": false','"expected": true')),/fixture validation failed/);
});
