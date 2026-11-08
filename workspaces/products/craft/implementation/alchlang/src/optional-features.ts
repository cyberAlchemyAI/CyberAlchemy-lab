import {pathToFileURL} from 'node:url';

export type AlchLangDistribution='full'|'core'|'rust'|'local-host';
export type OptionalFeature='rust'|'local-host';

export function distribution():AlchLangDistribution {
  const value=process.env.ALCHLANG_DISTRIBUTION??'full';
  if(!['full','core','rust','local-host'].includes(value))throw Error(`ALCHLANG_DISTRIBUTION_INVALID:${value}`);
  return value as AlchLangDistribution;
}

export function requireOptionalFeature(feature:OptionalFeature):void {
  const selected=distribution();
  if(selected==='full'||selected===feature||selected==='local-host'&&feature==='rust')return;
  const command=feature==='rust'?'alchlang-rust':'alchlang-local-host';
  throw Error(`ALCHLANG_OPTIONAL_FEATURE_REQUIRED:${feature}: use ${command}`);
}

export function runCli(moduleUrl:string,main:()=>Promise<void>):void {
  const executable=process.argv[1];
  if(!executable||pathToFileURL(executable).href!==moduleUrl)return;
  main().catch((error:unknown)=>{
    console.error(error instanceof Error?error.message:String(error));
    process.exitCode=1;
  });
}
