import {createInterface} from 'node:readline/promises';
import {stdin,stdout} from 'node:process';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {existsSync} from 'node:fs';
import {configuration,defaultConfig,saveConfiguration,readConfiguration,authHeaders,sshSettings,endpoint,fail} from './config.mjs';
import {discoverRemote} from './ssh.mjs';
import {models} from './transport.mjs';
import {connect,checkConnection,startEngine,smoke} from './engine.mjs';
// Open Questions: README.md. No credential values are accepted on the command line.
export function parseOptions(args){
 const options={};const flags=['config','host','ssh-port','user','identity-file','remote-port','base-url','model','alias','context-limit','output-limit','timeout-ms','token-env'];
 for(let i=0;i<args.length;i++){
  if(['--yes','--help'].includes(args[i])){options[args[i].slice(2)]=true;continue;}
  const key=args[i].slice(2);if(!args[i].startsWith('--')||!flags.includes(key)||Object.hasOwn(options,key)||!args[i+1]||args[i+1].startsWith('--'))fail('INVALID_ENGINE_OPTION');options[key]=args[++i];
 }
 if(options['base-url']&&['host','ssh-port','user','identity-file','remote-port'].some(k=>options[k]))fail('CONFLICTING_CONNECTION_OPTIONS');return options;
}
const help=`Engine commands:
  configure-engine --host HOST --ssh-port PORT [--user root] [--identity-file ABS_PATH]
  configure-engine --base-url https://ENGINE [--token-env VLLM_API_TOKEN]
  engine [--config FILE]       Start service and SSH tunnel until Ctrl+C
  check-engine [--config FILE] Check model and tokenizer without inference
  test-engine [--config FILE]  Run two short real inference requests and stop
Setup options: --remote-port PORT (skip SSH discovery), --model ID, --alias NAME,
  --context-limit N, --output-limit N, --timeout-ms N, --config NEW_FILE, --yes.
Secrets come only from the named environment variable or existing SSH keys.
Default private config: ${defaultConfig}`;
export async function configure(options,{signal,report=console.log}={}){
 const path=resolve(options.config??defaultConfig);if(existsSync(path))fail('ENGINE_CONFIG_EXISTS: use --config with a new filename');
 const interactive=!options.yes&&stdin.isTTY;const rl=interactive?createInterface({input:stdin,output:stdout}):null;
 const ask=async(label,fallback)=>{signal?.throwIfAborted();if(!rl){if(fallback===undefined)fail('ENGINE_SETTING_REQUIRED: '+label);return String(fallback);}const answer=await rl.question(label+(fallback===undefined?'':` [${fallback}]`)+': ',{signal});return answer.trim()||String(fallback??'');};
 let connection,session;
 try{
  let tokenEnv=options['token-env'];
  if(options['base-url'])connection={type:'direct',baseUrl:endpoint(options['base-url'])};
  else{
   const ssh=sshSettings({host:options.host??await ask('SSH host'),port:Number(options['ssh-port']??await ask('SSH port',22)),user:options.user??await ask('SSH user','root'),...(options['identity-file']?{identityFile:resolve(options['identity-file'])}:{})});
   let port=options['remote-port'];
   if(!port){report('Discovering model APIs through SSH…');const found=await discoverRemote(ssh,{signal});
    if(!found.length)fail('NO_MODEL_API_DISCOVERED: check that vLLM is running, or provide --remote-port and --token-env for an authenticated internal API');
    for(const item of found)report('Internal port '+item.port+': '+item.models.map(m=>m.id).join(', '));
    port=found.length===1?found[0].port:await ask('Select internal port');if(!found.some(f=>f.port===Number(port)))fail('UNLISTED_ENGINE_PORT');
   }
   connection={type:'ssh',ssh:{...ssh,remotePort:Number(port)}};
  }
  session=await connect({connection},{signal});
  const available=await models(session.baseUrl,{headers:authHeaders({tokenEnv}),signal:signal?AbortSignal.any([signal,AbortSignal.timeout(10000)]):AbortSignal.timeout(10000)});
  for(const m of available)report('Served model: '+m.id+(m.max_model_len?' (context '+m.max_model_len+')':''));
  const model=options.model??(available.length===1?available[0].id:await ask('Select exact model ID'));
  const chosen=available.find(m=>m.id===model);if(!chosen)fail('CONFIGURED_MODEL_NOT_SERVED');
  const c=configuration({schema_version:'alch.vllm-engine/v1',connection,model,alias:options.alias??await ask('Public model alias','vllm-chat'),contextLimit:Number(options['context-limit']??await ask('Context limit',chosen.max_model_len)),outputLimit:Number(options['output-limit']??await ask('Maximum output tokens',256)),timeoutMs:Number(options['timeout-ms']??await ask('Deadline in milliseconds (maximum 30000)',30000)),...(tokenEnv?{tokenEnv}:{})});
  await checkConnection(c,session.baseUrl,{signal});signal?.throwIfAborted();saveConfiguration(path,c);report('Configured '+c.alias+' in '+path);report('Connectivity and tokenizer passed. Run test-engine for real JSON/SSE inference, or engine to serve.');return c;
 }finally{rl?.close();await session?.close();}
}
export async function main(args=process.argv.slice(2)){
 const [mode,...rest]=args,options=parseOptions(rest);if(options.help){console.log(help);return;}
 if(!['configure-engine','engine','check-engine','test-engine'].includes(mode))fail('INVALID_ENGINE_COMMAND');
 if(mode!=='configure-engine'&&Object.keys(options).some(k=>k!=='config'))fail('ENGINE_COMMAND_ONLY_ACCEPTS_CONFIG');
 const controller=new AbortController(),stop=()=>controller.abort();process.once('SIGINT',stop);process.once('SIGTERM',stop);
 try{
  if(mode==='configure-engine')await configure(options,{signal:controller.signal});
  else{
   const c=readConfiguration(options.config??defaultConfig);
   if(mode==='check-engine'){const session=await connect(c,{signal:controller.signal});try{await checkConnection(c,session.baseUrl,{signal:controller.signal});console.log('PASS: served model and tokenizer');}finally{await session.close();}}
   else{
    const engine=await startEngine(c,{signal:controller.signal});try{
     if(mode==='test-engine')console.log(JSON.stringify(await smoke(engine.url,{signal:AbortSignal.any([engine.signal,AbortSignal.timeout(c.timeoutMs*2+1000)])})));
     else{console.log('Inference service: '+engine.url+'\nModel alias: '+c.alias+'\nPress Ctrl+C to stop service and tunnel.');if(!engine.signal.aborted)await new Promise(r=>engine.signal.addEventListener('abort',r,{once:true}));if(!controller.signal.aborted)fail('ENGINE_CONNECTION_CLOSED');}
    }finally{await engine.close();}
   }
  }
 }catch(error){if(!controller.signal.aborted){console.error(error.message);process.exitCode=1;}}
 finally{process.off('SIGINT',stop);process.off('SIGTERM',stop);}
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url)await main();
