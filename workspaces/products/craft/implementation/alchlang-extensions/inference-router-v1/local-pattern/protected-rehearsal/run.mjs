import {readFileSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
// Run with the shared tools/toolchain/run launcher. Open Questions: README.md.
const here=dirname(fileURLToPath(import.meta.url)),base=resolve(here,'../..'),root=resolve(base,'../../../../../../..');
const binding=JSON.parse(readFileSync(join(base,'compiler-binding.json'))),ds=resolve(root,binding.package_root_relative_to_repository);
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
if(sha(join(ds,'package.json'))!==binding.package_sha256)throw Error('COMPILER_PACKAGE_DRIFT');
for(const [p,h]of Object.entries(binding.dist_files))if(sha(join(ds,p))!==h)throw Error('COMPILER_INPUT_DRIFT: '+p);
const env={...process.env,ALCHLANG_TYPESCRIPT_COMPILER:process.env.ALCHLANG_TYPESCRIPT_COMPILER??resolve(root,binding.typescript_compiler),ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:ds};
for(const [cmd,args]of [['cargo',['build','--locked','--manifest-path',resolve(root,'auth-foundation/implementation/tenant-bridge/Cargo.toml')]],[process.execPath,['--test',join(here,'rehearsal.test.mjs')]]]){
 const result=spawnSync(cmd,args,{env,stdio:'inherit'});if(result.error)throw result.error;if(result.status!==0){process.exitCode=result.status??1;break;}
}
