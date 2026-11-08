
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"fcb208b9d8c04177d7869bd5975df4b0a3986d4fb1b1c537f108dbc9e0d9a426","ontology_sha256":"0f82f8ca9bf2a635649d0afc90225470fc5b56b1b1df46822e1dd1646205af56","behavior_sha256":"1dfbabef687a24f88fabc45b608ef9a85ecfbaf6712e73df44d8121f23df0706","contract_sha256":"7fe09af9e6da82d1d751b4ba42f3a13fd76be03c4ff8fd85fd0fdceb9fb2a905"},manifest},createBoundary,modules);
export default {fetch:handler};
