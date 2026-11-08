import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync, mkdirSync, mkdtempSync, writeFileSync, linkSync, unlinkSync, rmdirSync, rmSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { loadAlchLangSource } from "./source-file.js";
import { loadDomainSpecCompiler, type DomainSpecCompiler } from "./domainspec-cli.js";
import { lowerDomainSpec, type DomainSpecLowering } from "./lower-domainspec.js";
import { digest, json, symbol, fields, DOMAINSPEC_PROFILE, EXACT_PROFILE, EXACT_REALIZATION } from "./domainspec-profile.js";

function inventory(root: string): Record<string,string> {
 const out:Record<string,string>={};
 const walk=(dir:string)=>{for(const e of readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){const p=path.join(dir,e.name);if(e.isSymbolicLink())throw new Error(`DS_SYMLINK:${p}`);if(e.isDirectory())walk(p);else if(e.isFile())out[path.relative(root,p).split(path.sep).join("/")]=digest(readFileSync(p));else throw new Error(`DS_SPECIAL_FILE:${p}`);}};walk(root);return out;
}
function compilerInventory(compiler:DomainSpecCompiler): Record<string,string> {
 const root=compiler.binding.package_root;const manifest=JSON.parse(readFileSync(path.join(root,"package.json"),"utf8"));const files:Record<string,string>={"package.json":digest(readFileSync(path.join(root,"package.json")))};
 for(const name of manifest.files??[]){if(typeof name!=="string" || name.includes("..") || path.isAbsolute(name))throw new Error("DS_PACKAGE_FILES");const p=path.join(root,name);if(!existsSync(p))continue;if(lstatSync(p).isSymbolicLink())throw new Error("DS_PACKAGE_SYMLINK");if(lstatSync(p).isDirectory())for(const [rel,hash] of Object.entries(inventory(p)))files[`${name}/${rel}`]=hash;else files[name]=digest(readFileSync(p));}
 if(!Object.keys(files).some(n=>n.startsWith("dist/")))throw new Error("DS_PACKAGE_BUILD_REQUIRED");return Object.fromEntries(Object.entries(files).sort(([a],[b])=>a.localeCompare(b)));
}
function capture(sourcePath:string, bindingsPath:string){const source=readFileSync(sourcePath,"utf8");const bindingBytes=readFileSync(bindingsPath,"utf8");const loaded=loadAlchLangSource(sourcePath);if(digest(readFileSync(sourcePath))!==digest(source))throw new Error("DS_SOURCE_DRIFT");return {lowering:lowerDomainSpec(loaded.carrier,JSON.parse(bindingBytes),source),source,bindingBytes};}
function writeFiles(root:string,files:Record<string,string>){for(const [name,bytes] of Object.entries(files).sort(([a],[b])=>a.localeCompare(b))){const p=path.join(root,name);mkdirSync(path.dirname(p),{recursive:true});writeFileSync(p,bytes,{flag:"wx"});}}
function invoke(compiler:DomainSpecCompiler,args:string[]){let stdout="",stderr="";const code=compiler.runCli(args,{stdout:v=>{stdout+=v;},stderr:v=>{stderr+=v;}});if(code)throw new Error(`DS_COMPILER_FAILED:${code}:${stderr.trim()}`);return JSON.parse(stdout);}
export function renderDomainSpecApi(lower:DomainSpecLowering): string {
 const exact=lower.bindings.profile===EXACT_PROFILE;
 const queries:Record<string,unknown>={},calculations:Record<string,unknown>={};
 const imports:string[]=[];const mappings:Record<string,unknown>={};const policies:Record<string,unknown>={};const functions:string[]=[];
 
 for(const m of lower.model.mappings){const alias=`fn${imports.length}`;imports.push(`import * as ${alias} from "./generated/src/domainspec/typescript/${lower.feature}/${lower.symbols[m.id]}.js";`);functions.push(`${JSON.stringify(m.id)}:implementation(${alias})`);mappings[m.id]={fields:fields(lower.model,m.source_ref).map(f=>({id:f.id,target:symbol(f.id,"_"),type:f.type})),outputs:m.clauses.map(c=>({id:c.target_field,target:symbol(c.target_field,"_")}))};}
 for(const p of lower.model.policies){const alias=`fn${imports.length}`;imports.push(`import * as ${alias} from "./generated/src/domainspec/typescript/${lower.feature}/${lower.symbols[p.id]}.js";`);functions.push(`${JSON.stringify(p.id)}:implementation(${alias})`);policies[p.id]={fields:p.input_facts.map(id=>{const f=lower.model.facts.find(f=>f.id===id)!;return {id,target:symbol(id,"_"),type:f.type};}),targets:Object.fromEntries([...new Set([...p.cases.map(c=>c.target_ref),p.default_target_ref])].map(t=>[`${lower.feature}:${lower.symbols[t]}`,t]))};}
 if(exact){
   const fact=(id:string)=>{const f=lower.model.facts.find(f=>f.id===id)!;return {id,target:symbol(id,"_"),type:f.type};};
   for(const q of lower.model.queries){const alias=`fn${imports.length}`;imports.push(`import * as ${alias} from "./generated/src/domainspec/typescript/${lower.feature}/${lower.symbols[q.id]}.js";`);functions.push(`${JSON.stringify(q.id)}:implementation(${alias})`);queries[q.id]={fields:fields(lower.model,q.source_ref).map(f=>fact(f.id)),inputs:q.input_facts.map(fact),outputs:q.projection.map(id=>({id,target:symbol(id,"_")}))};}
   for(const c of lower.model.calculations){const alias=`fn${imports.length}`;imports.push(`import * as ${alias} from "./generated/src/domainspec/typescript/${lower.feature}/${lower.symbols[c.id]}.js";`);functions.push(`${JSON.stringify(c.id)}:implementation(${alias})`);calculations[c.id]={inputs:c.input_facts.map(fact)};}
 }
 return imports.join("\n")+`
function implementation(module:Record<string,unknown>):Function {const exported=Object.values(module).filter((value):value is Function=>typeof value==="function");if(exported.length!==1)throw new Error("ALCH_GENERATED_EXPORT_CONTRACT");return exported[0];}
const implementations: Record<string, Function> = {${functions.join(",")}};
const mappings: any = ${JSON.stringify(mappings)};
const policies: any = ${JSON.stringify(policies)};
const queries: any = ${JSON.stringify(queries)};
const calculations: any = ${JSON.stringify(calculations)};
function input(value: unknown, fields: any[], required: boolean, numericStrings=false): Record<string,unknown> {
 if(!value || typeof value!=="object" || Array.isArray(value) || ![Object.prototype,null].includes(Object.getPrototypeOf(value)))throw new Error("ALCH_INPUT_RECORD");
 const out:Record<string,unknown>=Object.create(null);
 for(const f of fields){const desc=Object.getOwnPropertyDescriptor(value,f.id);if(!desc){if(required)throw new Error("ALCH_MISSING_INPUT:"+f.id);continue;}if(!("value" in desc))throw new Error("ALCH_INPUT_TYPE:"+f.id);
 if(f.type==="integer") {
   const value=desc.value;
   const valid=typeof value==="bigint" || typeof value==="number" && Number.isSafeInteger(value) || numericStrings && typeof value==="string" && /^(0|[1-9][0-9]*)$/.test(value);
   if(!valid)throw new Error(numericStrings?"CALCULATION_INPUT_TYPE":"ALCH_INPUT_TYPE:"+f.id);
   if(BigInt(value)<0n || BigInt(value)>18446744073709551615n)throw new Error(numericStrings?"CALCULATION_RANGE":"ALCH_INPUT_RANGE:"+f.id);
 }else if(typeof desc.value!==(f.type==="boolean"?"boolean":"string"))throw new Error("ALCH_INPUT_TYPE:"+f.id);
 out[f.target]=desc.value;}
 return out;
}
export function evaluateMapping(id:string, value:unknown): Readonly<Record<string,unknown>> {
 if(!Object.hasOwn(mappings,id))throw new Error("ALCH_UNKNOWN_MAPPING:"+id);const m=mappings[id];const result=implementations[id](input(value,m.fields,false));const out:Record<string,unknown>={};for(const f of m.outputs)if(Object.hasOwn(result,f.target))Object.defineProperty(out,f.id,{value:result[f.target],enumerable:true});return Object.freeze(out);
}
export function selectPolicy(id:string,value:unknown):string {
 if(!Object.hasOwn(policies,id))throw new Error("ALCH_UNKNOWN_POLICY:"+id);const p=policies[id];const result=implementations[id](input(value,p.fields,${exact?"false":"true"}));if(!Object.hasOwn(p.targets,result))throw new Error("ALCH_UNKNOWN_TARGET");return p.targets[result];
}
${exact ? `
export function evaluateCalculation(id:string,value:unknown):bigint {
 if(!Object.hasOwn(calculations,id))throw new Error("ALCH_UNKNOWN_CALCULATION:"+id);
 return implementations[id](input(value,calculations[id].inputs,false,true));
}
export function evaluateQuery(id:string,rows:readonly unknown[],parameters:unknown={}):readonly Readonly<Record<string,unknown>>[] {
 if(!Object.hasOwn(queries,id))throw new Error("ALCH_UNKNOWN_QUERY:"+id);
 if(!Array.isArray(rows))throw new Error("ALCH_QUERY_ROWS");
 const q=queries[id],args=input(parameters,q.inputs,false);
 const results=implementations[id](rows.map(row=>input(row,q.fields,false)),args);
 return Object.freeze(results.map((result:Record<string,unknown>)=>Object.freeze(Object.fromEntries(q.outputs.map((f:any)=>[f.id,result[f.target]])))));
}
` : ""}`;
}
// Claim a new directory exclusively; manifest is linked last as the completion marker.
// Cleanup touches only inodes created by this invocation, preserving foreign additions.
function publish(stage:string,target:string){
 const owned:Array<{p:string;ino:number;dev:number;directory:boolean}>=[];
 const remember=(p:string,directory:boolean)=>{const st=lstatSync(p);owned.push({p,ino:st.ino,dev:st.dev,directory});};
 try{mkdirSync(target);remember(target,true);
  const paths=Object.keys(inventory(stage)).sort((a,b)=>a==="manifest.json"?1:b==="manifest.json"?-1:a.localeCompare(b));
  for(const rel of paths){const current=lstatSync(target);const root=owned[0];if(current.ino!==root.ino || current.dev!==root.dev || current.isSymbolicLink() || realpathSync(target)!==target)throw new Error("DS_OUTPUT_REPLACED");const p=path.join(target,rel);const components=rel.split("/").slice(0,-1);let dir=target;for(const part of components){dir=path.join(dir,part);if(!existsSync(dir)){mkdirSync(dir);remember(dir,true);}if(lstatSync(dir).isSymbolicLink() || realpathSync(dir)!==dir)throw new Error("DS_OUTPUT_SYMLINK");}linkSync(path.join(stage,rel),p);remember(p,false);}
 }catch(error){for(const item of owned.reverse()){try{const st=lstatSync(item.p);if(st.ino===item.ino && st.dev===item.dev){if(item.directory)rmdirSync(item.p);else unlinkSync(item.p);}}catch{/* Foreign additions and replacements are preserved. */}}throw error;}
}
export interface DomainSpecBuildOptions { bindingsPath?: string; packageRoot?: string; generate?: boolean; profile?: string; composition?: Record<string,unknown>; language?: "typescript"|"rust"; applicationLayout?: boolean }
export function domainSpecProjectFiles(lower:DomainSpecLowering, compiler:DomainSpecCompiler, composition?:Record<string,unknown>):Record<string,string>{
 if(!composition)return lower.files;
 const core_bindings:Record<string,unknown>={};
 for(const term of lower.model.terms)core_bindings[term.id]={selector:`${lower.feature}:${lower.symbols[term.id]}`,fields:Object.fromEntries(fields(lower.model,term.id).map(f=>[f.id,symbol(f.id,"_")]))};
 for(const calc of lower.model.calculations)core_bindings[calc.id]={selector:`${lower.feature}:${lower.symbols[calc.id]}`,fields:Object.fromEntries(calc.input_facts.map(id=>[id,symbol(id,"_")]))};
 const source={...composition,ontology:compiler.normalizeCompositionOntology(composition.ontology),id:'function',schema_version:'domainspec.project-composition/v1',core_bindings};
 const project={...JSON.parse(lower.files['project.json']),schema_version:'domainspec.project/v2',compositions:['function']};
 return {...lower.files,'project.json':json(project),'compositions/function.json':json(source)};
}
export async function buildDomainSpec(sourcePath:string,outputPath:string,options:DomainSpecBuildOptions={}) {
 const source=path.resolve(sourcePath);const bindingsPath=path.resolve(options.bindingsPath??`${source}.domainspec.json`);const target=path.resolve(outputPath);const parent=path.dirname(target);
 if(!existsSync(parent) || realpathSync(parent)!==parent || !lstatSync(parent).isDirectory())throw new Error("DS_OUTPUT_PARENT:existing real directory required");
 if(existsSync(target))throw new Error(`DS_OUTPUT_EXISTS:${target}`);
 const captured=capture(source,bindingsPath);if(captured.lowering.bindings.profile!==(options.profile??DOMAINSPEC_PROFILE))throw new Error("DS_PROFILE_BINDING_MISMATCH");const compiler=await loadDomainSpecCompiler(options.packageRoot);if(captured.lowering.bindings.profile===EXACT_PROFILE && !compiler.supportsExactUInt64)throw new Error("DS_EXACT_REALIZATION_UNAVAILABLE: rebuild the compatible compiler");const compilerFiles=compilerInventory(compiler);
 const stage=mkdtempSync(path.join(parent,".alchlang-stage-"));
 try{const project=path.join(stage,"project");writeFiles(project,domainSpecProjectFiles(captured.lowering,compiler,options.composition));const compiled=compiler.compileProject(project);
  writeFiles(stage,{"trace.json":json(captured.lowering.trace),"bindings.json":captured.bindingBytes,"source.alch":captured.source,"certificate.json":json(compiled.certificate),"compiler-files.json":json(compilerFiles)});
  if(options.generate){const language=options.language??"typescript";const profileArgs=language==="typescript"&&captured.lowering.bindings.profile===EXACT_PROFILE?["--realization-profile",EXACT_REALIZATION]:[];if(options.applicationLayout)profileArgs.push("--output-layout",compiler.applicationLayoutId);const generated=path.join(stage,"generated");invoke(compiler,["build",project,"--language",language,"--target-root",generated,...profileArgs]);const verification=invoke(compiler,["verify",project,"--language",language,"--target-root",generated,...profileArgs]);if(verification.result!=="pass")throw new Error("DS_GENERATED_VERIFICATION");if(language==="typescript")writeFileSync(path.join(stage,"domain.ts"),options.applicationLayout?renderDomainSpecApi(captured.lowering).replaceAll("./generated/src/domainspec/typescript/"+captured.lowering.feature+"/","./"+captured.lowering.feature+"/"):renderDomainSpecApi(captured.lowering),{flag:"wx"});}
  if(digest(readFileSync(source))!==digest(captured.source) || digest(readFileSync(bindingsPath))!==digest(captured.bindingBytes) || json(compilerInventory(compiler))!==json(compilerFiles))throw new Error("DS_INPUT_DRIFT");
  const manifest={schema_version:"alchlang.domainspec-build/v1",profile:captured.lowering.bindings.profile,source_sha256:digest(captured.source),bindings_sha256:digest(captured.bindingBytes),compiler:{package:compiler.binding.package,version:compiler.binding.version,files_sha256:digest(json(compilerFiles))},files:inventory(stage),generated_typescript:!!options.generate&&options.language!=="rust",...(options.language==="rust"?{generated_rust:!!options.generate}:{}),authority_effect:"none"};writeFileSync(path.join(stage,"manifest.json"),json(manifest),{flag:"wx"});publish(stage,target);return {status:"built",output_directory:target,nodes:compiled.graph.nodes.length,source_sha256:manifest.source_sha256,authority_effect:"none"};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
export async function checkDomainSpec(sourcePath:string,options:Omit<DomainSpecBuildOptions,"generate">={}){
 const source=path.resolve(sourcePath);const bindingsPath=path.resolve(options.bindingsPath??`${source}.domainspec.json`);const captured=capture(source,bindingsPath);if(captured.lowering.bindings.profile!==(options.profile??DOMAINSPEC_PROFILE))throw new Error("DS_PROFILE_BINDING_MISMATCH");const compiler=await loadDomainSpecCompiler(options.packageRoot);if(captured.lowering.bindings.profile===EXACT_PROFILE && !compiler.supportsExactUInt64)throw new Error("DS_EXACT_REALIZATION_UNAVAILABLE: rebuild the compatible compiler");const before=compilerInventory(compiler);const stage=mkdtempSync(path.join(os.tmpdir(),"alchlang-check-"));
 try{writeFiles(stage,domainSpecProjectFiles(captured.lowering,compiler,options.composition));const result=compiler.compileProject(stage);if(digest(readFileSync(source))!==digest(captured.source)||digest(readFileSync(bindingsPath))!==digest(captured.bindingBytes)||json(before)!==json(compilerInventory(compiler)))throw new Error("DS_INPUT_DRIFT");return {status:"valid",profile:captured.lowering.bindings.profile,nodes:result.graph.nodes.length,source_sha256:captured.lowering.source_sha256,authority_effect:"none"};}finally{rmSync(stage,{recursive:true,force:true});}
}
