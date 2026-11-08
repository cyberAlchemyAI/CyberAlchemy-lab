import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {compileStateMigration} from '../src/state-migration.js';
const source=readFileSync(new URL('../../extensions/state-migrations-v1/orders-v2.alch',import.meta.url),'utf8');

test('migration emits a public DomainSpec Mapping and preserves old request/event inputs',async()=>{
  const plan=await compileStateMigration(source);
  assert.match(plan.generated.source,/domainspec.declarative-function\/v1/);
  const module=await import('data:text/javascript;base64,'+Buffer.from(plan.generated.source).toString('base64'));
  assert.deepEqual(module.execute({},{}),{schemaVersion:'v2'});
  assert.match(plan.normalized,/schemaVersion: string optional/);
  assert.equal((plan.normalized.match(/field schemaVersion default/g)??[]).length,1);
  assert.ok(!plan.normalized.split('\n').filter(l=>/^  (input|payload) /.test(l)).some(l=>l.includes('schemaVersion')));
  assert.deepEqual(plan.manifest.operations,['place-order','record-order']);
});
for(const [name,change] of Object.entries({
  'wrong literal':(s:string)=>s.replace('default string "v2"','default string 2'),
  'expression instead of literal':(s:string)=>s.replace('default string "v2"','default string input.value'),
  'existing field':(s:string)=>s.replace('field schemaVersion','field orderId'),
  'unknown subject':(s:string)=>s.replace('subject OrderOperation\n  mapper','subject Unknown\n  mapper'),
  'missing source binding':(s:string)=>s.replace(/^  from-contract .+\n/m,''),
  'duplicate field':(s:string)=>s+'  field other default string "v3"\n',
  'unsafe mapper':(s:string)=>s.replace('mapper AddSchemaVersion','mapper constructor'),
  'second migration':(s:string)=>s+'\nmigration second:\n',
}))test('migration rejects '+name,async()=>{await assert.rejects(compileStateMigration(change(source)));});

test('boolean and integer default mappings retain scalar types',async()=>{
  for(const [literal,value] of [['boolean true',true],['integer 2',2]] as const){
    const plan=await compileStateMigration(source.replace('string "v2"',literal));
    const module=await import('data:text/javascript;base64,'+Buffer.from(plan.generated.source).toString('base64'));
    assert.deepEqual(module.execute({},{}),{schemaVersion:value});
  }
});
