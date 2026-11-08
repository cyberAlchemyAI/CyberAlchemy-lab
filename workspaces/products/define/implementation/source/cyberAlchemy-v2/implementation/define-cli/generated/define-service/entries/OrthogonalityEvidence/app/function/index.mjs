
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"51c905da760fc0c07a0a678cb2046312fb6d64b9b71e84240d1b6a470826b710","ontology_sha256":"439a1a65fa77af241edc22569c4610688781e9727fcf12432690aac3cbd0840d","behavior_sha256":"7ce9a2961c0b0e3e1002a39f05b6e00fe5918cefb56bbabdbeb72f06a4e07892","contract_sha256":"5d903c669c8d01410595710be03fd7ade5b0ac18a6f58a879e4ecea7cc239466"},manifest},createBoundary,modules);
export default {fetch:handler};
