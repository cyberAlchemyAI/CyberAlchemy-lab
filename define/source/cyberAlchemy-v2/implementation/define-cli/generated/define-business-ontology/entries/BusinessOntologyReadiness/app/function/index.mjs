
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"8f3b37cd307d4a18d8b5cc4c7d2079ddad8cbf32d87f14aa4d6426c5b2c5ce29","ontology_sha256":"4b38793c066db4c15493b29bb84441518c57f523049950f99d6c69ef5974839e","behavior_sha256":"30b33fc3aef03fb9c1c0349c2e585c6a5908235f2e21da05d5042dfa7ebaf000","contract_sha256":"08750553ef98484b49d10f0baf01cbf25751f4165a2c75f5effac8f166efb506"},manifest},createBoundary,modules);
export default {fetch:handler};
