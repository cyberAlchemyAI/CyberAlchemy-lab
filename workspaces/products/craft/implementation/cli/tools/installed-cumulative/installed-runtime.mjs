/** Run unchanged source-authored integration cases with an immutable installed
 * compiler. Only compiler/profile module locations change, never test bodies.
 * Open Questions: README.md#open-questions. */
import assert from 'node:assert/strict';
import {registerHooks} from 'node:module';
import {existsSync,readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const original=fileURLToPath(new URL('../../',import.meta.url)).replace(/\/$/,'');
const installed=process.env.CRAFT_TEST_INSTALLED_CLI_ROOT;
assert.ok(installed&&path.isAbsolute(installed),'absolute installed CLI root required');
assert.equal(realpathSync(installed),installed,'canonical installed CLI root required');
assert.equal(JSON.parse(readFileSync(path.join(installed,'package.json'))).name,'@domainspec-v2/cli');
assert.ok(installed.includes(path.sep+'node_modules'+path.sep),'an installed package is required');
function redirect(url){
 if(!url.startsWith('file:'))return null;
 const file=fileURLToPath(url);
 let relative;
 if(file.startsWith(installed+'/src/'))relative='dist/'+file.slice((installed+'/src/').length).replace(/\.ts$/,'.js');
 else if(file.startsWith(original+'/src/'))relative='dist/'+file.slice((original+'/src/').length).replace(/\.ts$/,'.js');
 else if(file.startsWith(original+'/dist/'))relative=file.slice((original+'/').length);
 else if(file.startsWith(original+'/profiles/'))relative=file.slice((original+'/').length);
 else return null;
 const target=path.join(installed,relative);
 assert.ok(existsSync(target),'installed compiler member missing: '+relative);
 assert.ok(realpathSync(target).startsWith(installed+path.sep),'installed member escapes selected package');
 return pathToFileURL(target).href;
}
registerHooks({resolve(specifier,context,nextResolve){
 let candidate;
 if(specifier.startsWith('file:')||specifier.startsWith('./')||specifier.startsWith('../')||specifier.startsWith('/')){
  candidate=new URL(specifier,context.parentURL??pathToFileURL(original+'/').href).href;
  const target=redirect(candidate);if(target)return nextResolve(target,context);
 }
 const resolved=nextResolve(specifier,context),target=redirect(resolved.url);
 return target?nextResolve(target,context):resolved;
}});
