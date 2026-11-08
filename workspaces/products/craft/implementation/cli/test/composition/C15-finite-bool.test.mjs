import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericSemanticOwner} from '../../src/generic/semantic-reconstruction.ts';
import {createGenericComputationDomainOwner} from '../../src/generic/computation-domain.ts';
import {createGenericSourceComputation} from '../../src/generic/pure-source-stage.ts';
import {exportGenericFiniteBoolSmtModel,GenericFormalUnsupportedError} from '../../src/generic/formal-finite-bool.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const bounds=JSON.parse(readFileSync(path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05/bounds.json'),'utf8'));
const profile={id:'test-node-bounded-values',path:'profile.json',sha256:'a'.repeat(64)};
const source='module Logic version 1\nrule Both:\n  input a Bool\n  input b Bool\n  expression a and b\n';

async function fixture(text=source,limits=bounds.computation.limits){
 const root=mkdtempSync(path.join(tmpdir(),'craft-c15-bool-'));mkdirSync(path.join(root,'source'));mkdirSync(path.join(root,'contracts'));
 writeFileSync(path.join(root,'source/business.alch'),text);
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({...bounds,computation:{...bounds.computation,limits}}));
 writeFileSync(path.join(root,'application.alch'),'module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source source/business.alch\n  computation-bounds contracts/bounds.json\n');
 const sources=createCoreCommerceSourceOwner();
 try{
  const capture=sources.prepare(root,'application.alch'),semantics=createGenericSemanticOwner(sources),semantic=semantics.check(capture),domain=createGenericComputationDomainOwner(sources,capture,semantics,semantic);
  const selected=text.includes('rule IsOne:')?'Logic.IsOne':text.includes('rule IsVerified:')?'Logic.IsVerified':text.includes('calculation Number:')?'Logic.Number':'Logic.Both';
  const texts=sources.inspect(capture).files.filter(file=>file.path.endsWith('.alch')).map(file=>({path:file.path,text:file.text}));
  const proposal=createGenericSourceComputation(texts,selected,limits).contract,handle=domain.check(proposal);
  return {root,domain,handle,cleanup:()=>rmSync(root,{recursive:true,force:true})};
 }catch(error){rmSync(root,{recursive:true,force:true});throw error;}
}

test('C15 finite SMT model enumerates all canonical Bool inputs and exact metered observations without claims',async()=>{
 const f=await fixture();try{
  const model=exportGenericFiniteBoolSmtModel(f.domain,f.handle,profile);
  assert.equal(model.language,'smtlib2');assert.equal(model.scope,'one-pure-computation-canonical-bool-leaves');
  assert.equal(model.profile_binding,'caller-supplied-unverified-pending-original-sdk-join');
  assert.deepEqual(model.observations.map(row=>[row.input.a,row.input.b,row.result.ok&&row.result.wire]),[[false,false,'false'],[true,false,'false'],[false,true,'false'],[true,true,'true']]);
  assert.ok(model.observations.every(row=>Number.isSafeInteger(row.result.fuel_used)&&row.result.fuel_used>0));
  assert.ok(model.observations[0].result.fuel_used<model.observations[1].result.fuel_used,'short-circuit fuel remains observable');
  assert.match(model.smtlib2,/\(declare-datatypes \(\) \(\(EvalResult/);
  assert.deepEqual(model.input_symbols,['input_0','input_1']);
  assert.deepEqual(model.input_paths,[{argument:'a',field:null,symbol:'input_0'},{argument:'b',field:null,symbol:'input_1'}]);
  assert.match(model.smtlib2,/\(define-fun Evaluate \(\(input_0 Bool\) \(input_1 Bool\)\) EvalResult/);
  assert.ok(model.smtlib2.split('\n').length>=8,'SMT-LIB statements require real newlines');
  assert.equal(model.smtlib2.includes('\\n'),false,'SMT-LIB must not contain literal backslash-n separators');
  assert.equal(model.observations.length,2**model.input_names.length);
  assert.equal(model.claim_ceiling.includes('no-generated-code-parity'),true);
 }finally{f.cleanup();}
});

test('C15 finite model covers a Rule over a flat Bool business record',async()=>{
 const business='module Logic version 1\nvalue-object Request:\n  verified Bool\n  flagged Bool\nrule IsVerified:\n  input request Request\n  expression request.verified and not request.flagged\n';
 const f=await fixture(business);try{
  const model=exportGenericFiniteBoolSmtModel(f.domain,f.handle,profile);
  assert.deepEqual(model.input_paths,[{argument:'request',field:'flagged',symbol:'input_0'},{argument:'request',field:'verified',symbol:'input_1'}]);
  assert.deepEqual(model.observations.map(row=>[row.input.request.verified,row.input.request.flagged,row.result.ok&&row.result.wire]),[[false,false,'false'],[false,true,'false'],[true,false,'true'],[true,true,'false']]);
  assert.match(model.smtlib2,/\(define-fun Evaluate \(\(input_0 Bool\) \(input_1 Bool\)\) EvalResult/);
 }finally{f.cleanup();}
});

test('C15 bounded-fuel failures are explicit formal result branches',async()=>{
 const f=await fixture(source,{...bounds.computation.limits,fuel:10});try{
  const model=exportGenericFiniteBoolSmtModel(f.domain,f.handle,profile);
  assert.ok(model.observations.some(row=>!row.result.ok));
  assert.ok(model.observations.filter(row=>!row.result.ok).every(row=>row.result.error_json.includes('ResourceLimit')));
  assert.match(model.smtlib2,/ResourceLimit/);
 }finally{f.cleanup();}
});

test('C15 finite exporter rejects unsupported input, result, profile and foreign owner',async()=>{
 const badInput=await fixture('module Logic version 1\nrule IsOne:\n  input n UInt64\n  expression n == 1\n');
 const badResult=await fixture('module Logic version 1\ncalculation Number:\n  pure\n  result UInt64\n  expression 1\n');
 try{
  assert.throws(()=>exportGenericFiniteBoolSmtModel(badInput.domain,badInput.handle,profile),error=>error instanceof GenericFormalUnsupportedError&&error.code==='UnsupportedInput');
  assert.throws(()=>exportGenericFiniteBoolSmtModel(badResult.domain,badResult.handle,profile),error=>error instanceof GenericFormalUnsupportedError&&error.code==='UnsupportedResult');
  assert.throws(()=>exportGenericFiniteBoolSmtModel(badInput.domain,badInput.handle,{...profile,sha256:'not-a-digest'}),error=>error instanceof GenericFormalUnsupportedError);
  assert.throws(()=>exportGenericFiniteBoolSmtModel({},badInput.handle,profile));
 }finally{badInput.cleanup();badResult.cleanup();}
});

test('C15 source mutation invalidates original domain before export',async()=>{
 const f=await fixture();try{
  writeFileSync(path.join(f.root,'source/business.alch'),source.replace('a and b','a or b'));
  assert.throws(()=>exportGenericFiniteBoolSmtModel(f.domain,f.handle,profile));
 }finally{f.cleanup();}
});
