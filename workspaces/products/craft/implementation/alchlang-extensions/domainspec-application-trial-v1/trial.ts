import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import os from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { compileCarrier, parseDomainSource, evaluateCalculation, evaluateQuery, evaluateMapping, evaluatePolicy, CompilationRejected } from "../../implementation/src/index.js";
import { checkDomainSpec } from "../../implementation/src/domainspec-project-writer.js";
import { lowerDomainSpec } from "../../implementation/src/lower-domainspec.js";
import { defaultDomainSpecPackageRoot, loadDomainSpecCompiler } from "../../implementation/src/domainspec-cli.js";
import { digest, json } from "../../implementation/src/domainspec-profile.js";
import { resolveTypeScriptCompiler } from "../../implementation/src/function-builder.js";
const here = path.dirname(fileURLToPath(import.meta.url));
const impl = path.resolve(here, "../../implementation");
const files = (dir: string): string[] => readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? files(path.join(dir,e.name)) : [path.join(dir,e.name)]);

export async function runTrial() {
  const sourcePath = path.join(impl,"examples/typed-backend.alch");
  const source = readFileSync(sourcePath,"utf8");
  const bindingsPath = path.join(here,"typed-commerce.bindings.json");
  const compiled = compileCarrier(parseDomainSource(source).carrier);
  const model = compiled.plan.model;
  const local: any = await import(`data:text/javascript;base64,${Buffer.from(compiled.files["domain.typed-backend.ts"]).toString("base64")}`);
  const rows = [
    {order_id:"low",amount:20,status:"open"},
    {order_id:"tie-first",amount:140,status:"open"},
    {order_id:"closed",amount:300,status:"closed"},
    {order_id:"tie-second",amount:140,status:"open"},
  ];
  const before = structuredClone(rows);
  assert.deepEqual(local.evaluateQuery("OpenOrders", rows), evaluateQuery(model.queries[0], rows));
  assert.deepEqual(local.evaluateQuery("OpenOrders", rows), [{order_id:"tie-first",amount:140},{order_id:"tie-second",amount:140}]);
  assert.deepEqual(rows,before);
  for (const amount of [0,100,101,140,Number.MAX_SAFE_INTEGER]) {
    for (const c of model.calculations) assert.equal(local.evaluateCalculation(c.id,{amount}),evaluateCalculation(c,{amount}));
    assert.equal(local.evaluatePolicy("FeePolicy",{amount}),evaluatePolicy(model.policies[0],{amount}));
    assert.deepEqual(local.evaluateMapping("SummarizeOrder",{order_id:"order",amount}),evaluateMapping(model.mappings[0],{order_id:"order",amount}));
  }
  assert.throws(()=>local.evaluateCalculation("ApplyFee",{amount:(1n<<64n)-1n}),/CALCULATION_OVERFLOW/);
  let rejection: unknown;
  try { await checkDomainSpec(sourcePath,{bindingsPath}); } catch (error) { rejection=error; }
  assert.ok(rejection instanceof CompilationRejected);
  assert.ok(rejection.issues.some(i=>i.code==="DS_UNSUPPORTED" && i.path==="queries"));

  // A separately authored compiler probe, never passed off as application lowering.
  // It binds the existing constant fixture's node to ApplyFee's actual expression.
  const temp=mkdtempSync(path.join(os.tmpdir(),"alch-commerce-trial-"));
  let compilerBinding;
  let upstreamError="";
  try {
    const probeSource=readFileSync(path.join(impl,"examples/domainspec-order.alch"),"utf8");
    const lower=lowerDomainSpec(parseDomainSource(probeSource).carrier,JSON.parse(readFileSync(path.join(impl,"examples/domainspec-order.alch.domainspec.json"),"utf8")),probeSource);
    const nodePath="specs/delivery-example/nodes/express-fee.json";
    const node=JSON.parse(lower.files[nodePath]);
    node.body.description="Compatibility probe: supplied UInt64 amount plus five; not the delivery application's constant.";
    node.body.inputs=["amount"];
    node.body.typed_contract.inputs=[{name:"amount",type:{kind:"scalar",name:"UInt64"}}];
    node.body.typed_contract.expression={op:"add",left:{op:"input",name:"amount"},right:{op:"literal",value:5}};
    lower.files[nodePath]=json(node);
    const project=path.join(temp,"project"),generated=path.join(temp,"generated");
    for(const [name,bytes] of Object.entries(lower.files)){const p=path.join(project,name);mkdirSync(path.dirname(p),{recursive:true});writeFileSync(p,bytes);}
    const compiler=await loadDomainSpecCompiler();compilerBinding=compiler.binding;
    compiler.compileProject(project);
    let stderr="";
    assert.equal(compiler.runCli(["build",project,"--language","typescript","--target-root",generated],{stdout(){},stderr(v){stderr+=v;}}),0,stderr);
    const tsc=resolveTypeScriptCompiler(defaultDomainSpecPackageRoot());
    const js=path.join(temp,"js");
    execFileSync(process.execPath,[tsc,"--strict","--skipLibCheck","--target","ES2022","--module","commonjs","--rootDir",generated,"--outDir",js,...files(generated).filter(p=>p.endsWith(".ts"))],{cwd:temp,encoding:"utf8"});
    const generatedApi=await import(pathToFileURL(path.join(js,"src/domainspec/typescript/delivery-example/express-fee.js")).href);
    assert.equal(generatedApi.expressFee({amount:140}),145);
    try{generatedApi.expressFee({amount:Number.MAX_SAFE_INTEGER});}catch(error){upstreamError=String(error);}
    assert.match(upstreamError,/Calculation overflow/);
    assert.equal(evaluateCalculation(model.calculations.find(c=>c.id==="ApplyFee")!,{amount:Number.MAX_SAFE_INTEGER}),9007199254740996n);
  } finally {rmSync(temp,{recursive:true,force:true});}
  assert.equal(digest(readFileSync(sourcePath)),digest(source));
  return {
    schema_version:"alchlang.application-trial/v1-candidate",
    application:"typed-commerce",source:"implementation/examples/typed-backend.alch",source_sha256:digest(source),bindings_sha256:digest(readFileSync(bindingsPath)),
    local_generated_application:"pass",query_ties_filter_limit_projection:"pass",mapping_and_policy_boundaries:"pass",
    target_migration:"blocked",target_diagnostics:rejection.issues,
    numeric_probe:{status:"incompatible",input:"9007199254740991",alchlang_result:"9007199254740996",domainspec_result:upstreamError,ordinary_input:140,ordinary_result:145},
    compiler:compilerBinding,
    gaps:["Query lowering and stable ordering/filter/projection parity","integer record and Mapping representation","parameterized UInt64 arithmetic preserving range and failures","ordered numeric Policy comparisons and non-executing selection"],
    product_approval:"not_recorded",authority_effect:"none",
  };
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const result=await runTrial();
  if(process.argv.length===4 && process.argv[2]==="--out")writeFileSync(path.resolve(process.argv[3]),json(result),{flag:"wx"});
  else if(process.argv.length!==2)throw new Error("Usage: trial.ts [--out new-result.json]");
  process.stdout.write(json(result));
}
