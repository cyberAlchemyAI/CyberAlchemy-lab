import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {compiledProfileFixture,createProfileFixture} from './profile-fixture.js';
import {composeProfile} from '../../src/profile-engine/compose.js';
import {loadProfileProject} from '../../src/profile-engine/loader.js';
import {renderProfilePlan,renderProfileTemplate} from '../../src/profile-engine/render.js';
import {compileProfileDomainFiles,qualifyNativeFiles} from '../../src/profile-engine/native-check.js';
import {dataDigest,sha256} from '../../src/profile-engine/contracts.js';
// Open questions: PE14 actual application composition and PE23 installed qualification.
const compiler=path.resolve(import.meta.dirname,'../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules/typescript/bin/tsc');
async function rendered(t:{after(fn:()=>void):void}){
 const f=await compiledProfileFixture(t),snapshot=loadProfileProject(path.join(f.root,'project.json'),{engine:f.identity.engine,tools:[{key:'typescript-entry',path:compiler},{key:'typescript-parser',path:path.join(path.dirname(path.dirname(compiler)),'lib/typescript.js')}]}),plan=renderProfilePlan(composeProfile(f.selection,f.functions)),files=compileProfileDomainFiles(snapshot,plan,compiler);
 return {...f,snapshot,plan,files};
}
test('complete service checks final glue and executes independent outcomes with no ambient effects',async t=>{
 const f=await rendered(t),receipt=qualifyNativeFiles(f.snapshot,f.files,compiler);
 for(const file of ['app/index.mjs','entries/requestQuote.mjs','entries/describeQuotePolicy.mjs','runtime/profile-http.mjs'])assert.ok(receipt.checked_files.includes(file));
 assert.ok(receipt.typed_emissions.includes('functions/requestQuote/runtime/boundary.mjs'));assert.ok(!Object.keys(f.files).some(p=>p.endsWith('server.mjs')));
 const output=path.join(f.root,'rendered');for(const [file,body]of Object.entries(f.files)){const target=path.join(output,file);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,body);}
 const require=createRequire(import.meta.url),saved:{object:any;key:string;value:any}[]=[];let forbidden=0;
 for(const [object,key]of [[globalThis,'fetch'],[require('node:http'),'createServer'],[require('node:net'),'connect'],[require('node:net'),'createServer'],[require('node:child_process'),'spawn'],[require('node:child_process'),'execFileSync']] as const){saved.push({object,key,value:(object as any)[key]});(object as any)[key]=()=>{forbidden++;throw Error('forbidden ambient effect');};}syncBuiltinESMExports();
 try{
  const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
  for(const c of oracle.cases){let calls=0;const response=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'},{fetch:async(url:URL,options:RequestInit)=>{calls++;assert.equal(options.method,'GET');assert.equal(url.searchParams.get('sku'),c.input.sku);return new Response(JSON.stringify(c.external),{headers:{'content-type':'application/json'}});}});
   const actual=await response.json();if(c.expected_error){assert.equal(actual.error,c.expected_error,c.id);if(c.expected_error==='FUNCTION_INPUT_SCHEMA')assert.equal(calls,0);}else assert.deepEqual(actual,c.expected,c.id);
  }
  assert.equal(forbidden,0);
 }finally{for(const s of saved.reverse())s.object[s.key]=s.value;syncBuiltinESMExports();}
});
test('missing exports, imports and wrong public input/result/environment contracts fail native qualification',async t=>{
 const f=await rendered(t);qualifyNativeFiles(f.snapshot,f.files,compiler);
 const negatives:[string,string][]=[
  ['entries/requestQuote.mjs',f.plan['entries/requestQuote.mjs']!.replace('{createInvoker}','{missingExport}')],
  ['entries/requestQuote.mjs',f.plan['entries/requestQuote.mjs']!.replace('runtime/profile-http.mjs','runtime/absent.mjs')],
  ['contract-input.ts',"import {handler} from './app/index.mjs'; handler(42);\n"],
  ['contract-result.ts',"import {handler} from './app/index.mjs'; const value:Promise<string>=handler(new Request('https://test.invalid'));\n"],
  ['contract-env.ts',"import {handler} from './app/index.mjs'; handler(new Request('https://test.invalid'),{DEPENDENCY_INVENTORY_URL:42});\n"],
 ];
 for(const [file,body]of negatives){const altered=compileProfileDomainFiles(f.snapshot,{...f.plan,[file]:body},compiler);assert.throws(()=>qualifyNativeFiles(f.snapshot,altered,compiler),/PROFILE_NATIVE_CHECK_FAILED|PROFILE_NATIVE_IMPORT_MISSING/,file);}
 const forged={...f.files};assert.throws(()=>qualifyNativeFiles(f.snapshot,forged,compiler),/PROFILE_NATIVE_CHECK_FAILED/);
 const tampered={...f.plan,'functions/requestQuote/runtime/boundary.mjs':'export const invoke=()=>({status:"quoted"});\n'};assert.throws(()=>compileProfileDomainFiles(f.snapshot,tampered,compiler),/PROFILE_RUNTIME_EMISSION_MISMATCH/);
});
test('locked templates allow typed holes, bounded iteration and declared owned includes only',t=>{
 const child='export const {{name}}={{value}};\n',parent='{{> child}}\n{{#each rows}}const {{name}}={{value}};\n{{/each}}',f=createProfileFixture(t,p=>{p.assets=[{id:'child',path:'child.tpl',kind:'template',sha256:sha256(child),includes:[],holes:{name:'identifier',value:'json'}},{id:'parent',path:'parent.tpl',kind:'template',sha256:sha256(parent),includes:['child'],holes:{name:'identifier',value:'json'}}];});
 writeFileSync(path.join(f.root,'profile/child.tpl'),child);writeFileSync(path.join(f.root,'profile/parent.tpl'),parent);const pkg=f.load().packages[0]!;
 const value=renderProfileTemplate(pkg,'parent',{name:'safe',value:'quote"\n',rows:[{name:'next',value:7}]});assert.ok(value.includes('export const safe="quote\\\"\\n";'));assert.ok(value.includes('const next=7;'));
 assert.throws(()=>renderProfileTemplate(pkg,'parent',{name:'x;process.exit()',value:null,rows:[]}),/PROFILE_TEMPLATE_IDENTIFIER/);
 assert.throws(()=>renderProfileTemplate(pkg,'parent',{name:'x',value:null,rows:'arbitrary code'}),/PROFILE_TEMPLATE_ITERATION/);
 assert.throws(()=>renderProfileTemplate(pkg,'outside',{}),/PROFILE_TEMPLATE_UNOWNED/);
 assert.equal(dataDigest(f.load().lock),dataDigest(f.load().lock));
});
