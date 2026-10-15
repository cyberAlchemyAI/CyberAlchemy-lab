
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"1e1f8d3abfd0618e9e4f1cf1b60845738aea2fdf3a067fc0acdb0c174af36eb2","ontology_sha256":"b441f4eaa7ecc5bf3965ddf9ccfa6072f294bdaa0d336ee3722e18c83bed5af6","behavior_sha256":"f565cdb9bf02fd0239a7ba06a831adf04e10309f2d0f7e4a4fb0cb727f6fdb10","contract_sha256":"c50b0dbcaeb212a19dd498b40684876b2447a79ea1523b130db76b6407595d43"},manifest},createBoundary,modules);
export default {fetch:handler};
