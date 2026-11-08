
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"8c0f95c803b31769ff88937d17a2f7a9dff01bfd69ce6dc7f10dbf758ff38ca1","ontology_sha256":"599f6f4666b6404442b686dcf5128748280483e387a7483c6e516dbae7a7498a","behavior_sha256":"e367c482612641e5721dd41d88efaf16d9ba22b99de67d3e9fb2b6c430526892","contract_sha256":"b2e7a411839019caf06592c1362e6efaa8d9c5d292a9c00b43ffc472a8618148"},manifest},createBoundary,modules);
export default {fetch:handler};
