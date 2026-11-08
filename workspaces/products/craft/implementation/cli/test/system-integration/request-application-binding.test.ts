import test from 'node:test';
import assert from 'node:assert/strict';
import {businessApplicationFixture} from '../helpers/business-application.ts';
import {compileRequestApplicationBindingV1,assertRequestApplicationBindingV1,assertApplicationIntegrationBinding} from '../../src/system-integration/application-binding-v1.ts';
import {compileRequestApplicationGraphV1,assertCompiledRequestApplicationGraphV1,assertCompiledApplicationGraph} from '../../src/system-integration/application-graph-v1.ts';
import {decodeRequestApplicationSourceV1} from '../../src/system-integration/request-application-source-v1.ts';
import path from 'node:path';
import {assertRequestSchema} from '../helpers/request-schema.ts';
// Open questions: native/public/installed qualifications BA09–18.
test('request-only graph closes exact Mapping/Operation types without provider partitions, with one request contract per Operation',async t=>{
 const f=await businessApplicationFixture(t),source=structuredClone(f.source);source.entries.push({...source.entries[0]!,id:'receiveAgain',route:{method:'POST',path:'/receiveAgain'}});
 const b=compileRequestApplicationBindingV1(f.graph,source,f.plan),g=b.application_graph;assertRequestApplicationBindingV1(b);assertCompiledRequestApplicationGraphV1(g);
 assert.deepEqual(b,compileRequestApplicationBindingV1(f.graph,source,f.plan));assert.equal(g.nodes.filter(n=>n.node_kind==='inbound-endpoint').length,2);assert.equal(g.nodes.filter(n=>n.node_kind==='request-contract').length,1);
 assert.deepEqual(g.edges.filter(e=>e.relationship_authority==='integration').map(e=>e.relationship).sort(),['accepts-request','invokes','invokes']);assert.equal(g.runtime_bindings.length,2);assert.equal(g.operation_requests[0]!.bindings.length,2);
 assert.deepEqual(g.runtime_bindings[0]!.inputs,[{parameter:'payload',value_type:{kind:'named',selector:'commerce:order-notice'},source:{kind:'protocol-body',reference:'protocol-operation:commerce:receiveAgain#request',path:['payload']}}]);
 assert.equal(g.runtime_guarantees_observed,false);assert.equal(b.authority_effect,'none');assert.throws(()=>assertApplicationIntegrationBinding(b),/SNAPSHOT/);assert.throws(()=>assertCompiledApplicationGraph(g),/SNAPSHOT/);
 for(const [file,value]of [['request-application-source-v1.schema.json',source],['compiled-request-application-graph-v1.schema.json',g],['request-application-binding-v1.schema.json',b]] as const)assertRequestSchema(path.join(f.cli,'contracts'),file,value,{...value,proof:true});
});
test('request binding rejects forged custody, unknown/wrong-kind endpoints, parameters, routes, schema extras and input hooks',async t=>{
 const f=await businessApplicationFixture(t),b=compileRequestApplicationBindingV1(f.graph,f.source,f.plan);
 assert.throws(()=>assertRequestApplicationBindingV1(structuredClone(b)),/SNAPSHOT/);assert.throws(()=>assertCompiledRequestApplicationGraphV1(structuredClone(b.application_graph)),/SNAPSHOT/);assert.throws(()=>compileRequestApplicationBindingV1(structuredClone(f.graph),f.source,f.plan));assert.throws(()=>compileRequestApplicationBindingV1(f.graph,f.source,structuredClone(f.plan)));
 for(const [mutate,pattern]of [
  [(s:any)=>s.entries[0].operation_ref='commerce:missing',/ENDPOINT/],[(s:any)=>s.entries[0].operation_ref='commerce:order-notice',/ENDPOINT_KIND/],
  [(s:any)=>s.entries[0].mapping_arguments=[],/MAPPING_ARGUMENTS/],[(s:any)=>s.entries[0].request_parameter='other',/REQUEST_TYPE/],
  [(s:any)=>s.entries.push({...s.entries[0],id:'other'}),/DUPLICATE/],[(s:any)=>s.entries[0].access.kind='protected',/UNSUPPORTED/],[(s:any)=>s.runtime={},/SCHEMA/],[(s:any)=>s.entries[0].route.path='/../outside',/SCHEMA/],
 ] as const){const s=structuredClone(f.source);mutate(s);assert.throws(()=>compileRequestApplicationBindingV1(f.graph,s,f.plan),pattern);}
 let reads=0;const hook={get schema_version(){reads++;return f.source.schema_version},source_id:'commerce',entries:f.source.entries};assert.throws(()=>decodeRequestApplicationSourceV1(hook),/inert data/);assert.equal(reads,0);
});
