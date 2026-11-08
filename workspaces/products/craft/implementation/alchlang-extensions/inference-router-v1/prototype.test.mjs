import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parsed} from './prototype.mjs';
import {parseDeclarativeSource} from '../../implementation/dist/declarative-profile.js';
import {validateSchema} from '../../implementation/dist/function-runtime.js';
const source=readFileSync(new URL('provider-selection.alch',import.meta.url),'utf8');
const request={request_id:'r1',tenant_id:'t1',task:'text.generate',required_context_tokens:512,max_output_tokens:256,stream:false};
const provider={binding_id:'fixture-provider-a',binding_version:'fixture-v1',model:'fixture-chat-a',enabled:true,tenant_allowed:true,task:'text.generate',context_limit:4096,output_limit:1024,streaming:true,rank:10};
test('existing parser deterministically projects authored Alch to the DomainSpec contract',()=>{
 assert.deepEqual(parseDeclarativeSource(source).contract,parsed.contract);
 assert.equal(parsed.contract.schema_version,'domainspec.declarative-function/v1');
 assert.equal(parsed.model.endpoint.path,'/internal/select-provider');
});
test('input contract accepts automatic and explicit model selection',()=>{
 for(const r of [request,{...request,model:'fixture-chat-a'}])assert.doesNotThrow(()=>validateSchema(parsed.model,'RoutingRequest',r));
});
test('caller input cannot introduce destinations, secrets or invalid token estimates',()=>{
 for(const r of [{...request,url:'https://example.com'},{...request,token:'secret'},{...request,required_context_tokens:-1},{...request,max_output_tokens:0},{...request,stream:'true'},{...request,model:null}])assert.throws(()=>validateSchema(parsed.model,'RoutingRequest',r));
});
test('catalog contract rejects unversioned bindings, secret fields and malformed ranks',()=>{
 for(const patch of [{binding_version:undefined},{rank:-1},{rank:1.5},{credential:'secret'}])assert.throws(()=>validateSchema(parsed.model,'Provider',{...provider,...patch}));
});
test('unsupported declarative clauses reject instead of becoming opaque success',()=>{
 assert.throws(()=>parseDeclarativeSource(source.replace('  select row','  select-best row')));
 assert.throws(()=>parseDeclarativeSource(source.replace('  when Available yield','  silently-retry Available yield')));
});
test('every business relation resolves to a candidate definition',()=>{
 const ontology=JSON.parse(readFileSync(new URL('business-ontology.json',import.meta.url),'utf8'));
 const ids=new Set(ontology.nodes.map(n=>n.id));assert.equal(ids.size,8);
 for(const r of ontology.relations){assert.ok(ids.has(r.source_concept_id));assert.ok(ids.has(r.target_concept_id));}
});
