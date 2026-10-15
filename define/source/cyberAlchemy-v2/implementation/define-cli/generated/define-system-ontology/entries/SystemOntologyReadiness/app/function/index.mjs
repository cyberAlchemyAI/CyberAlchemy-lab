
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"30d6d2309521aa6bf68f102e8cd9e61076cecc82238e87eb33d83b61c0c213c3","ontology_sha256":"1004b686cd1bb482cbc9f1cb62d8920964ab6423ec4d04d188e92ca3c86ebbea","behavior_sha256":"21261d8ab22ae0077010c0c5745eae7b303571cc204842e421ebd472697a3a78","contract_sha256":"d8ffb1bfd29d7dcbc0cf61a80eea1c1fea3e8505c136bbb851a726ce30fa414e"},manifest},createBoundary,modules);
export default {fetch:handler};
