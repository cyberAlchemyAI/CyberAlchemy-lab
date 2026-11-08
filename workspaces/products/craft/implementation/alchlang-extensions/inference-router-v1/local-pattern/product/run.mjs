import {createRunner} from './process-runner.mjs';
import {validateSuites} from './validation.mjs';
import {mkdirSync,readFileSync,existsSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {verifyProduct,root,base,here,sha} from './package.mjs';
// Operator entry and evidence orchestration; no inference policy. Open Questions: OPERATOR.md.
const mode=process.argv[2]??'help';
const engineModes=['configure-engine','engine','check-engine','test-engine'];
if(!['help','verify','demo','serve','rehearse','validate',...engineModes].includes(mode)||!engineModes.includes(mode)&&process.argv.length>(mode==='validate'?4:3))throw Error('Usage: tools/inference-reference help|verify|demo|serve|rehearse|validate [new-evidence-directory] or configure-engine|engine|check-engine|test-engine [options]');
if(mode==='help'){
 console.log('Inference reference product (mock engines; no LLM required)\nverify: check exact packaged inputs\ndemo: run 11 API checks and stop\nserve: run demo and keep API open until Ctrl+C\nrehearse: test protected/durable API across process restarts\nvalidate NEW_DIRECTORY: run consolidated suites and save evidence\nconfigure-engine: configure a vLLM connection (--help for options)\nengine: serve using saved engine settings\ncheck-engine: verify model and tokenizer\ntest-engine: run two real inference checks\nOperator guide: '+join(here,'OPERATOR.md'));
}else{
 const identity=verifyProduct();console.log('Verified reference candidate: '+identity.files+' files; '+identity.manifest_sha256);
 const compiler=JSON.parse(readFileSync(join(base,'compiler-binding.json')));
 const env={...process.env,ALCHLANG_TYPESCRIPT_COMPILER:resolve(root,compiler.typescript_compiler),ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:resolve(root,compiler.package_root_relative_to_repository)};
 const {run,stop}=createRunner({cwd:root,env});
 const interrupt=()=>stop('SIGINT'),terminate=()=>stop('SIGTERM');process.on('SIGINT',interrupt);process.on('SIGTERM',terminate);
 try{
  if(mode==='verify')console.log('PASS');
  else if(engineModes.includes(mode))await run([join(base,'local-pattern/vllm/cli.mjs'),mode,...process.argv.slice(3)]);
  else if(mode==='demo'||mode==='serve')await run([join(base,'local-pattern/demo/run.mjs'),...(mode==='serve'?['--serve']:[])]);
  else if(mode==='rehearse')await run([join(base,'local-pattern/protected-rehearsal/run.mjs')]);
  else{
   if(!process.argv[3])throw Error('VALIDATION_OUTPUT_REQUIRED');const output=resolve(process.argv[3]);if(existsSync(output))throw Error('VALIDATION_OUTPUT_EXISTS');mkdirSync(output,{recursive:true});
   const impl=resolve(base,'../../implementation'),af=resolve(root,'auth-foundation/implementation/inference-browser');
   const suites=[
    ['vllm',['--test',join(base,'local-pattern/vllm/vllm.test.mjs')],11],
    ['package',['--test',join(here,'package.test.mjs'),join(here,'operator.test.mjs')],6],
    ['demo',['--test',join(base,'local-pattern/demo/demo.test.mjs')],5],
    ['protected-durable',[join(base,'local-pattern/protected-rehearsal/run.mjs')],1],
    ['local-pattern',['--test',join(base,'local-pattern/pattern.test.mjs')],13],
    ['service',[join(base,'run.mjs'),'test'],121],
    ['authentication',['--test',...['consumer','state','renewal'].map(n=>join(af,n+'.test.mjs'))],38],
    ['custody-tls',['--test',...['durable-custody/custody','reconciliation/reconciliation','ingress/ingress'].map(n=>join(base,'security',n+'.test.mjs'))],30],
    ['compatibility',['--import',join(impl,'node_modules/tsx/dist/loader.mjs'),'--test',join(impl,'test/service-profile.test.ts')],3]
   ];
   await validateSuites({output,identity,suites,run,verifyProduct,here});
  }
 }finally{process.off('SIGINT',interrupt);process.off('SIGTERM',terminate);}
}
