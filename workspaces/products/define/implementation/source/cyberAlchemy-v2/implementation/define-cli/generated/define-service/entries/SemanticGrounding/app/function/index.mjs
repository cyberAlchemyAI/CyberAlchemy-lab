
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"e3950d6e1027d765eb7b737ac4d7295862b9dc116217e21a490492d9dd6ee0f1","ontology_sha256":"da955ab241c36c1ce755cafa04892d4441f26ebebac8600437b896d24d92a7dc","behavior_sha256":"3fe064169270e8a1ebad38115d659a4e5571ffda9f9766b4f4aed8f8306fe036","contract_sha256":"e12b1bc7e4ac8bcae9e02beb88096b9f9ed12165c1af5a26ccc71dc47697eea8"},manifest},createBoundary,modules);
export default {fetch:handler};
