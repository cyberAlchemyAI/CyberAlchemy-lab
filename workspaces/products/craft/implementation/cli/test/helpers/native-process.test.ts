import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {NativeProcessFailure,nativeProcessFailure,readNativeObserver,isLeanDecideFailure} from './native-process.ts';
// Open Questions: goals/plans/domainspec-alchlang-review-repair/C4-NATIVE-FAILURE-ACCOUNTING.v1.md#open-questions

const node=(source:string,timeout=5000)=>execFileSync(process.execPath,['--input-type=module','-e',source],{encoding:'utf8',timeout,stdio:'pipe'});
const pass={result:'pass',interfaces:1,fields:2},fail={result:'fail',error:'exact field projection'};
const json=(value:unknown)=>JSON.stringify(value)+'\n';
function caught(execute:()=>unknown):unknown{try{execute();}catch(error){return error;}assert.fail('expected a real child-process failure');}
const exit=(stdout:string,status=1)=>Object.assign(new Error('child exited nonzero'),{status,signal:null,stdout,stderr:''});

test('real child successful stdout follows the existing observer pass protocol',()=>{
  assert.deepEqual(readNativeObserver(()=>node(`console.log(${JSON.stringify(JSON.stringify(pass))});`)),pass);
});
test('real child normal exit1 follows the existing observer rejection protocol',()=>{
  assert.deepEqual(readNativeObserver(()=>node(`console.log(${JSON.stringify(JSON.stringify(fail))});process.exitCode=1;`)),fail);
});
test('real child compiler failure retains cause, nonzero status and both streams',()=>{
  const cause=caught(()=>node('process.stdout.write("compiler stdout");process.stderr.write("compiler diagnostic");process.exitCode=2;'));
  const error=nativeProcessFailure('compiler',cause);
  assert.equal(error.cause,cause);assert.equal(error.status,2);assert.equal(error.signal,null);assert.equal(error.code,null);assert.equal(error.failure_kind,'exit');
  assert.equal(error.stdout,'compiler stdout');assert.equal(error.stderr,'compiler diagnostic');assert.match(error.message,/compiler diagnostic/);
  assert.equal(isLeanDecideFailure(error),false);
});
test('real absent executable remains ENOENT with its original cause, not a semantic rejection',t=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-native-process-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const missing=path.join(root,'missing-tool');assert.equal(fs.existsSync(missing),false);
  const cause=caught(()=>execFileSync(missing,[],{encoding:'utf8',timeout:1000})),error=nativeProcessFailure('missing native tool',cause);
  assert.equal(error.cause,cause);assert.equal(error.code,'ENOENT');assert.equal(error.status,null);assert.equal(error.failure_kind,'spawn-or-transport');
  assert.match(error.message,/ENOENT/);assert.doesNotMatch(error.message,/undefinedundefined/);assert.equal(isLeanDecideFailure(error),false);
  assert.throws(()=>readNativeObserver(()=>{throw cause;}),e=>e instanceof NativeProcessFailure&&e.cause===cause&&e.code==='ENOENT');
});
test('real timeout with valid-looking rejection stdout cannot count as an observer rejection',()=>{
  const cause=caught(()=>node(`console.log(${JSON.stringify(JSON.stringify(fail))});setInterval(()=>{},1000);`,1000));
  const error=nativeProcessFailure('timeout',cause);
  assert.equal(error.code,'ETIMEDOUT');assert.equal(error.failure_kind,'spawn-or-transport');assert.equal(error.stdout,json(fail));assert.equal(isLeanDecideFailure(error),false);
  assert.throws(()=>readNativeObserver(()=>{throw cause;}),e=>e instanceof NativeProcessFailure&&e.cause===cause&&e.code==='ETIMEDOUT');
});
test('real terminated child cannot count as an observer or Lean rejection',()=>{
  const cause=caught(()=>node(`console.log(${JSON.stringify(JSON.stringify(fail))});process.kill(process.pid,'SIGTERM');`)),error=nativeProcessFailure('signal',cause);
  assert.equal(error.signal,'SIGTERM');assert.equal(error.status,null);assert.equal(error.failure_kind,'signal');assert.equal(error.stdout,json(fail));assert.equal(isLeanDecideFailure(error),false);
  assert.throws(()=>readNativeObserver(()=>{throw cause;}),e=>e instanceof NativeProcessFailure&&e.cause===cause&&e.signal==='SIGTERM');
});

const invalid:[string,()=>string|Buffer][]=[
  ['exit0 fail',()=>json(fail)],
  ['exit1 pass',()=>{throw exit(json(pass));}],
  ['exit2 fail',()=>{throw exit(json(fail),2);}],
  ['empty stdout',()=>{throw exit('');}],
  ['malformed JSON',()=>{throw exit('{broken\n');}],
  ['two JSON objects',()=>json(pass)+json(pass)],
  ['duplicate JSON keys',()=>'{"result":"fail","result":"pass","interfaces":1,"fields":2}\n'],
  ['extra stdout',()=>json(pass)+'noise\n'],
  ['extra fields',()=>json({...pass,claimed:true})],
  ['invented error result',()=>{throw exit(json({result:'error',error:'missing tool'}));}],
  ['empty rejection reason',()=>{throw exit(json({result:'fail',error:''}));}],
  ['nonstring rejection reason',()=>{throw exit(json({result:'fail',error:3}));}],
  ['missing rejection reason',()=>{throw exit(json({result:'fail'}));}],
  ['negative count',()=>json({...pass,fields:-1})],
  ['fractional count',()=>json({...pass,interfaces:1.5})],
  ['string count',()=>json({...pass,fields:'2'})],
  ['missing count',()=>json({result:'pass',interfaces:1})],
  ['null result',()=>'null\n'],
  ['array result',()=>'[]\n'],
  ['JSON without LF',()=>JSON.stringify(pass)],
  ['null status',()=>{throw {...exit(json(fail)),status:null};}],
  ['status string',()=>{throw {...exit(json(fail)),status:'1'};}],
  ['timeout code',()=>{throw {...exit(json(fail)),code:'ETIMEDOUT'};}],
  ['output bound error',()=>{throw {...exit(json(fail)),code:'ENOBUFS'};}],
  ['signal with status',()=>{throw {...exit(json(fail)),signal:'SIGTERM'};}],
  ['transport error property',()=>{throw {...exit(json(fail)),error:Error('transport')};}],
  ['timed outcome',()=>{throw {...exit(json(fail)),timed:true};}],
];
for(const [name,execute] of invalid)test('synthetic protocol guard rejects '+name,()=>assert.throws(()=>readNativeObserver(execute),NativeProcessFailure));

test('malformed exit1 JSON preserves the actual original failure and stderr',()=>{
  const cause=Object.assign(exit('{\n'),{stderr:'actual provider diagnostic'});
  assert.throws(()=>readNativeObserver(()=>{throw cause;}),e=>e instanceof NativeProcessFailure&&e.cause===cause&&e.stdout==='{\n'&&e.stderr==='actual provider diagnostic'&&/protocol/.test(e.message));
});
test('buffer output is decoded without altering the original captured buffers',()=>{
  const stdout=Buffer.from('native output'),stderr=Buffer.from('native diagnostic'),cause={status:2,signal:null,stdout,stderr};
  const error=nativeProcessFailure('buffered tool',cause);assert.equal(error.cause,cause);assert.equal(cause.stdout,stdout);assert.equal(cause.stderr,stderr);assert.equal(error.stdout,'native output');assert.equal(error.stderr,'native diagnostic');
  assert.deepEqual(readNativeObserver(()=>Buffer.from(json(pass))),pass);
});
test('bounded display keeps full native diagnostic available for precise predicates',()=>{
  const diagnostic='x'.repeat(10000)+'\nCurrent.lean:1:1: error: Tactic `decide` failed\nfalse\n';
  const error=nativeProcessFailure('synthetic Lean diagnostic',exit(diagnostic,2));
  assert.ok(error.message.length<=6000);assert.equal(error.stdout,diagnostic);assert.equal(isLeanDecideFailure(error,true),true);
});
test('synthetic Lean predicate requires normal nonzero exit and kernel-specific diagnostic',()=>{
  const source='Current.lean:1:1: error: Tactic `decide` failed\nfalse\n';
  assert.equal(isLeanDecideFailure(nativeProcessFailure('synthetic',exit(source,2)),true),true);
  for(const changes of [{status:0},{status:null},{signal:'SIGTERM'},{code:'ENOENT'},{timed:true},{error:Error('transport')}])assert.equal(isLeanDecideFailure(nativeProcessFailure('synthetic',{...exit(source),...changes}),true),false);
  for(const diagnostic of ['failed','decide\nfalse\n','error: unrelated syntax\nfalse\n'])assert.equal(isLeanDecideFailure(nativeProcessFailure('synthetic',exit(diagnostic))),false);
  const coverage=nativeProcessFailure('synthetic',exit('Current.lean:1:1: error: currentStructuralReferencesHold rejected'));
  assert.equal(isLeanDecideFailure(coverage),true);assert.equal(isLeanDecideFailure(coverage,true),false);
  assert.equal(isLeanDecideFailure(Error('error: decide failed\nfalse\n')),false);
});
