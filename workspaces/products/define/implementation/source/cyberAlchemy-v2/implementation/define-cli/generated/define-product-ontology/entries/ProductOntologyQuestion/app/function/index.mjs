
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"cf5cd47c86fa0d3bd04f560142323075b75240d3e26f376bf97debcd7eda0229","ontology_sha256":"6996a046f9575679b2387892472da6ea7d126ee0ee45f17513fae2416682577c","behavior_sha256":"742c29809a0ba053114f974e2fd5d1c1ef359b5c1fd395934767e8179a680375","contract_sha256":"9e71d01f5c91dc9f7519840006d89b5724bc6f1edcdca38d48c5737b6c18523f"},manifest},createBoundary,modules);
export default {fetch:handler};
