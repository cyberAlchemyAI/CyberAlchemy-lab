
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"add7a237dec0004e7ce689559c3e4c97d94868087e62d751ee8d12d67c392f7c","ontology_sha256":"6dc4c61af9e23d14db383d8b016a1122d6ee8f9ee80e740c2a850626a65e4e96","behavior_sha256":"4316cbbeb8df1db44b2bc1b9937eca4fd0e37c99aa48796e60c1332352394bde","contract_sha256":"3064d4a2900f589ac3bfe6c2752bcb817520bf02ac725b33bde4a29d807b2638"},manifest},createBoundary,modules);
export default {fetch:handler};
