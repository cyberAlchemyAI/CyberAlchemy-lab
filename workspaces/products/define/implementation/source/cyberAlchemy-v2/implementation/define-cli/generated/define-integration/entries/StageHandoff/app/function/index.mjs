
import {createBoundary} from '../../runtime/boundary.mjs';
import {createTracedInvoker} from '../../runtime/invocation-trace.mjs';
import ontology from '../../provenance/function/ontology.json' with {type:'json'};
import manifest from '../../manifest.json' with {type:'json'};
import {execute,validateInput} from './behavior.mjs';
import api from '../../domain/typescript/lib/index.js';
import model from '../../provenance/function/function.json' with {type:'json'};
import bindings from '../../provenance/function/bindings.json' with {type:'json'};
const modules={};
export function createInvoker(observe){const relay=event=>{const n=ontology.nodes.find(n=>n.name===event.declaration)??ontology.nodes.find(n=>n.kind==='result');observe?.({...event,definition:event.definition??(n?{name:n.name,id:n.id,source:n.source,clauses:n.clauses}:null)});};return createBoundary(model,bindings,scope=>execute(scope,api,relay),scope=>validateInput(scope,relay),modules,relay,(scope,binding)=>execute(scope,api,relay,binding),(scope,binding)=>execute(scope,api,relay,binding,'input'));};
export const {invoke,handler}=createInvoker();
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"bd961fcac94ef43f4497e658f99c6ad3818df7ffe7899de79fcf4fc44daffc8b","ontology_sha256":"804efb564009882c46e62640b630e907f39e31c6e56e33956d847b01ef6e2b97","behavior_sha256":"b32a019e3df0ddd26dceb48e95a70d58997ef147b62dcbe6a251917f48960437","contract_sha256":"0fe4546e4021ca2116375837d3ac18849c08c644fb5fa00d629268d6eb4c576e"},manifest},createBoundary,modules);
export default {fetch:handler};
