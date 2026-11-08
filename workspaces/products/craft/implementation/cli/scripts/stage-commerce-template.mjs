#!/usr/bin/env node
/** Keep the authored repository emitter beside compiled modules. The emitter
 * needs TypeScript declarations that tsc removes from its JavaScript output. */
import {stripTypeScriptTypes} from 'node:module';
import {copyFileSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(root,'src','commerce','commerce-sqlite-repository-runtime-v1.ts');
const target=path.join(root,'dist','commerce','commerce-sqlite-repository-runtime-v1.ts');
mkdirSync(path.dirname(target),{recursive:true});
copyFileSync(source,target);
if(!readFileSync(target).equals(readFileSync(source)))
 throw Error('CRAFT_COMMERCE_TEMPLATE_STAGE_MISMATCH');
const runtime=path.join(root,'profiles','commerce-local-v1-candidate','runtime');
for(const name of ['sqlite-physical-layout','sqlite-unit-of-work']){
 const authored=readFileSync(path.join(runtime,name+'.ts'),'utf8');
 const emitted=stripTypeScriptTypes(authored,{mode:'strip'}).replaceAll('../../../src/','../../../dist/');
 if(emitted.includes('../../../src/'))throw Error('CRAFT_COMMERCE_PROFILE_CHECKOUT_IMPORT:'+name);
 writeFileSync(path.join(runtime,name+'.js'),emitted);
}
