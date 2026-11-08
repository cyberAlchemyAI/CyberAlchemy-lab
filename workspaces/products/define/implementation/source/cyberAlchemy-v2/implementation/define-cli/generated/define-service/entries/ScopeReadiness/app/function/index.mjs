
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"1597404f71acee0e9c0ec7c1d94e71a22b0decf2b9d9d3413bef6f327ac4ecb2","ontology_sha256":"f4faf11b01edc8dc721585edc685d3f84cf2bc4453da3cbfb33c4301fad90f7d","behavior_sha256":"dd37913c03bf1e1972b650f4687455cb30b70b0b2ef2569c6e36cb02f0bb92de","contract_sha256":"9e4d2e65f7738ed76a4c5802680bbf4d9d520a3c0a12aaa1507e57663a3e3d08"},manifest},createBoundary,modules);
export default {fetch:handler};
