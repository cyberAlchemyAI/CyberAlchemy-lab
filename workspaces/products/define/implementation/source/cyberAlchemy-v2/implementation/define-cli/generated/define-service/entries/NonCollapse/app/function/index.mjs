
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"26e61223bd3950abf1d90adcaa478db855573d2463d96c51e6c9bf1cb987e4ef","ontology_sha256":"f6efe17e79ea1187d388ec7907c8a99aa4043a571171cb917eea16805e20758f","behavior_sha256":"a354b9ed87bac1215b9ecf1c1ea5cb2203889e5e3a7c1f6403dde601e63c8429","contract_sha256":"a2b35c5b06e110dc1b9b0dcdfd250808c4b164ffb3dd30dfe61f8da2da7afc2c"},manifest},createBoundary,modules);
export default {fetch:handler};
