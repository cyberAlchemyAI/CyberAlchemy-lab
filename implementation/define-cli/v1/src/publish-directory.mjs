import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
export function publishDirectory(source,target) {
  const run=spawnSync(process.env.DEFINE_PYTHON ?? 'python3',[resolve(import.meta.dirname,'../publish_directory.py'),source,target],{encoding:'utf8',timeout:10000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  if(run.error || run.status!==0) throw new Error(run.error?.message ?? run.stderr.trim() ?? 'Directory publication failed');
}
