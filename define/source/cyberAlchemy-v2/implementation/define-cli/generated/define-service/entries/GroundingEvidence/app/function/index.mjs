
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"a85d349c980b35fa85ddf814263918ffa0fe6901741742964e7edf88dc5fd950","ontology_sha256":"433428a4f5e9df8cc43a471423f6a271b3d20d4d387b46bf1e7f17d02a59182f","behavior_sha256":"973ce15817d622e87cd6f9cefb71d92db1efc50615a746711ae89a14d7434420","contract_sha256":"4848d0e8276222716e4e4eb6d17f4a121a401f08db064f59d251d2e4521c35df"},manifest},createBoundary,modules);
export default {fetch:handler};
