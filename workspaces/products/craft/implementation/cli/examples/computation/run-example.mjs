#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
const require=createRequire(import.meta.url);
const args=process.argv.slice(2),options={};
for(let n=0;n<args.length;n+=2){if(!['--cli','--tsc','--out'].includes(args[n])||!args[n+1])throw Error('Usage: run-example.mjs [--cli /path/main.js] [--tsc /path/typescript/bin/tsc] [--out /new/path]');options[args[n].slice(2)]=path.resolve(args[n+1]);}
const cli=options.cli??path.resolve(import.meta.dirname,'../../dist/cli/main.js');
const tsc=options.tsc??require.resolve('typescript/bin/tsc');
const {bindComputationSource,unwrapComputationSource,evaluateComputationObserved,evaluateComputationJsonObserved}=await import(pathToFileURL(path.resolve(path.dirname(cli),'../index.js')).href);
const scratch=options.out??fs.mkdtempSync(path.join(os.tmpdir(),'domainspec-computation-example-'));
if(options.out){if(fs.existsSync(scratch))throw Error('Example output directory must be new');fs.mkdirSync(scratch,{recursive:true});}
const invoke=(program,argv,success=true)=>{const p=spawnSync(process.execPath,[program,...argv],{encoding:'utf8'});if(success)assert.equal(p.status,0,p.stderr||p.stdout);else assert.notEqual(p.status,0,'negative control unexpectedly accepted');return p;};
const version=invoke(tsc,['--version']).stdout.trim();assert.equal(version,'Version 6.0.3','Installed consumer qualification requires normal TypeScript 6.0.3');
const cases=JSON.parse(fs.readFileSync(new URL('./cases.json',import.meta.url),'utf8')).cases;
const results=[];
for(const entry of cases){
 const contract=path.join(scratch,entry.id+'.craft.json'),input=path.join(scratch,entry.id+'.input.json');
 fs.copyFileSync(path.join(import.meta.dirname,entry.contract),contract);fs.copyFileSync(path.join(import.meta.dirname,entry.input),input);
 const output=path.join(scratch,entry.id+'-generated'),compiled=path.join(scratch,entry.id+'-compiled');
 invoke(cli,['computation','check',contract]);invoke(cli,['computation','build',contract,'--out',output]);invoke(cli,['computation','verify',contract,'--out',output]);
 fs.mkdirSync(compiled);fs.writeFileSync(path.join(compiled,'package.json'),' {"type":"module"}\n');
 invoke(tsc,['--ignoreConfig',path.join(output,'computation.ts'),'--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--noUncheckedIndexedAccess','--exactOptionalPropertyTypes','--lib','ES2022,DOM','--outDir',compiled]);
 const native=await import(pathToFileURL(path.join(compiled,'computation.js')).href),wire=JSON.parse(fs.readFileSync(input,'utf8'));
 const result=native.runComputation(wire);assert.equal(result.ok,true);assert.deepEqual(result.value,entry.expected);assert.deepEqual(native.runComputationJson(fs.readFileSync(input,'utf8')),result);
 const reference=invoke(cli,['computation','run',contract,'--input',input]);const ref=JSON.parse(reference.stdout);assert.deepEqual({ok:ref.ok,value:ref.value,fuel_used:ref.fuel_used},result);
 const checked=unwrapComputationSource(JSON.parse(fs.readFileSync(contract,'utf8'))).checked,observed=native.runComputationObserved(wire);assert.deepEqual(observed.result,result);assert.deepEqual(observed,evaluateComputationObserved(checked,wire));assert.deepEqual(native.runComputationJsonObserved(fs.readFileSync(input,'utf8')),evaluateComputationJsonObserved(checked,fs.readFileSync(input,'utf8')));assert.deepEqual(observed.policy_decisions,entry.expected_policy_decisions??[]);
 results.push({id:entry.id,expected_value_pass:true,native_reference_parity:true,observed_api_parity:true,policy_decisions:observed.policy_decisions,fuel_used:result.fuel_used});
}
// A model edit must change generated native behavior while old bytes remain protected.
const original=path.join(scratch,'record-reducer.craft.json'),before=fs.readFileSync(original,'utf8'),edited=JSON.parse(before);
edited.contract.functions[0].body.fields.count.right.value='2';fs.writeFileSync(original,JSON.stringify(edited));
invoke(cli,['computation','check',original],false); // Current declaration fingerprint rejects the unbound edit.
const declaration_meanings=Object.fromEntries(Object.entries(edited.declarations).map(([selector,binding])=>[selector,binding.meaning]));
declaration_meanings['$.functions[0]']='Add two count units for each retained amount and add the explicit UInt64 amount to the summary total without any external effect.';
declaration_meanings['$.records[1]']='Closed accumulated summary with exact UInt64 count units, two per accepted order, and total amount.';
const rebound=bindComputationSource(edited.contract,{owner_ref:edited.owner.owner_ref,meaning:'Accumulate two count units per accepted order and sum their exact UInt64 amounts after completing filter and mapping in order.',declaration_meanings});
fs.writeFileSync(original,JSON.stringify(rebound));
const bare=path.join(scratch,'unbound-full-contract.json');fs.writeFileSync(bare,JSON.stringify(edited.contract));invoke(cli,['computation','check',bare],false);
invoke(cli,['computation','build',original,'--out',path.join(scratch,'record-reducer-generated')],false);
const editOutput=path.join(scratch,'record-reducer-edit-generated'),editCompiled=path.join(scratch,'record-reducer-edit-compiled');invoke(cli,['computation','build',original,'--out',editOutput]);
fs.mkdirSync(editCompiled);fs.writeFileSync(path.join(editCompiled,'package.json'),'{"type":"module"}\n');
invoke(tsc,['--ignoreConfig',path.join(editOutput,'computation.ts'),'--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--lib','ES2022,DOM','--outDir',editCompiled]);
const changed=await import(pathToFileURL(path.join(editCompiled,'computation.js')).href);assert.deepEqual(changed.runComputation(JSON.parse(fs.readFileSync(path.join(scratch,'record-reducer.input.json'),'utf8'))).value,{count:'4',total:'1250'});
fs.writeFileSync(original,before);invoke(cli,['computation','verify',original,'--out',path.join(scratch,'record-reducer-generated')]);
const tampered=path.join(scratch,'record-reducer-generated/computation.ts'),source=fs.readFileSync(tampered,'utf8');fs.appendFileSync(tampered,'\n// negative tamper control\n');invoke(cli,['computation','verify',original,'--out',path.dirname(tampered)],false);fs.writeFileSync(tampered,source);invoke(cli,['computation','verify',original,'--out',path.dirname(tampered)]);
const report={schema_version:'domainspec.computation-installed-example/v1-candidate',status:'pass',typescript:version,scratch,results,authored_model_edit:{before:{count:'2',total:'1250'},after:{count:'4',total:'1250'},native_behavior_changed:true},controls:{stale_declaration_binding_rejected:true,unbound_full_contract_rejected:true,explicit_meaning_rebound_after_model_edit:true,changed_source_no_overwrite:true,artifact_tamper_rejected:true,restored_artifact_verified:true},open_questions_ref:path.join(import.meta.dirname,'README.md')};
fs.writeFileSync(path.join(scratch,'example-result.json'),JSON.stringify(report,null,2)+'\n');process.stdout.write(JSON.stringify(report,null,2)+'\n');
