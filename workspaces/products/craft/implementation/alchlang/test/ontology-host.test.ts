import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {compileOntologyHost,schemasFromOntology,factsFromOntology} from '../src/ontology-host.js';
const source=readFileSync(new URL('../../extensions/ontology-schema-v1/orders-v2.alch',import.meta.url),'utf8');

test('one property derives ontology, schemas, state default and DomainSpec mapper',async()=>{
  const plan=await compileOntologyHost(source);
  const prop=plan.ontology.records.OrderOperation.properties.find(p=>p.name==='schemaVersion')!;
  assert.equal(prop.default,'v2');assert.equal(prop.required,false);
  assert.equal(plan.schemas.facts.OrderOperation.properties.schemaVersion.default,'v2');
  assert.ok(!plan.schemas.facts.OrderOperation.required.includes('schemaVersion'));
  assert.ok(plan.schemas.states['place-order'].required.includes('schemaVersion'));
  assert.ok(!plan.normalized.split('\n').filter(l=>/^  (input|payload) /.test(l)).some(l=>l.includes('schemaVersion')));
  assert.equal(plan.generated.length,1);const g=plan.generated[0];
  assert.equal(g.descriptor.property_id,prop.id);
  assert.equal(Object.hasOwn(g.descriptor,'from_contract'),false);
  const module=await import('data:text/javascript;base64,'+Buffer.from(g.output.source).toString('base64'));
  assert.deepEqual(module.execute({},{}),{schemaVersion:'v2'});
});

test('schema projector consumes typed ontology without rereading Alch source',async()=>{
  const {ontology}=await compileOntologyHost(source);const changed=structuredClone(ontology);
  changed.records.OrderOperation.properties.find(p=>p.name==='schemaVersion')!.type='boolean';
  changed.records.OrderOperation.properties.find(p=>p.name==='schemaVersion')!.default=true;
  assert.equal(schemasFromOntology(changed).facts.OrderOperation.properties.schemaVersion.type,'boolean');
  assert.equal(factsFromOntology(changed).find(p=>p.id==='schemaVersion')!.type,'boolean');
});

test('property identities survive comments and source reformatting',async()=>{
  const a=await compileOntologyHost(source),b=await compileOntologyHost('# Comment\n'+source.replace('entity OrderOperation:\n','entity OrderOperation:\n  # The default stays explicit.\n'));
  assert.notEqual(a.ontology.source_sha256,b.ontology.source_sha256);
  assert.deepEqual(a.ontology.records,b.ontology.records);
  assert.equal(a.generated[0].directory,b.generated[0].directory);
});

test('initial version needs no default and no migration declaration',async()=>{
  const p=await compileOntologyHost(source.replace('  schemaVersion: string optional default "v2"\n',''));
  assert.equal(p.generated.length,0);
  assert.ok(!Object.hasOwn(p.schemas.facts.OrderOperation.properties,'schemaVersion'));
});

for(const [name,change] of Object.entries({
  'required default':(s:string)=>s.replace('optional default','required default'),
  'wrong literal type':(s:string)=>s.replace('default "v2"','default true'),
  'expression default':(s:string)=>s.replace('default "v2"','default input.value'),
  'record default':(s:string)=>s.replace('string optional default "v2"','record optional default {}'),
  'duplicate mapping':(s:string)=>s.replace('mapping OrderState:\n','mapping OrderState:\n  field schemaVersion default string "v2"\n'),
}))test('ontology host rejects '+name,async()=>assert.rejects(compileOntologyHost(change(source))));

test('existing defaults remain available when a later field is declared',async()=>{
  const p=await compileOntologyHost(source.replace('entity OrderOperation:\n','entity OrderOperation:\n  archived: boolean optional default false\n'));
  assert.equal(p.generated.length,2);
  assert.deepEqual(new Set(p.generated.map(g=>g.descriptor.field)),new Set(['schemaVersion','archived']));
});
