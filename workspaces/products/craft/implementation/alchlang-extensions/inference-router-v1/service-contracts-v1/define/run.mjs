import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
// Replay the exact scripted Define scope; candidate only. Open Questions: ../README.md.
const base=dirname(fileURLToPath(import.meta.url));
const pack=JSON.parse(readFileSync(resolve(base,'cli-result.json'),'utf8')).definition_pack;
const root=resolve(base,'../../../../../../../../..');
const args=[resolve(root,'implementation/define-cli/bin/define.mjs'),'run',...['goal','intent','context','consumer'].flatMap(k=>['--'+k,pack[k]]),'--input',resolve(base,'cli-input.json'),'--json',...(process.argv[2]?['--output',resolve(process.argv[2])]:[])];
const result=spawnSync(process.execPath,args,{stdio:'inherit'});if(result.error)throw result.error;process.exitCode=result.status??1;
