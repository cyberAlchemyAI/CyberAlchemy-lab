import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync,symlinkSync,realpathSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {resolveTypeScriptCompiler,FUNCTION_TYPESCRIPT_VERSION} from '../src/function-builder.js';

// Open questions: PE22 installed generation receipt in the profile-engine plan.
function fixture(t:{after(fn:()=>void):void}){
 const root=mkdtempSync(path.join(os.tmpdir(),'profile-tsc-discovery-'));
 t.after(()=>rmSync(root,{recursive:true,force:true}));return root;
}
function compiler(root:string,version=FUNCTION_TYPESCRIPT_VERSION){
 const pkg=path.join(root,'node_modules/typescript');mkdirSync(path.join(pkg,'bin'),{recursive:true});
 writeFileSync(path.join(pkg,'package.json'),JSON.stringify({name:'typescript',version,bin:{tsc:'bin/tsc'}}));
 const entry=path.join(pkg,'bin/tsc');writeFileSync(entry,"process.stdout.write('fixture only');\n");
 mkdirSync(path.join(root,'node_modules/.bin'),{recursive:true});symlinkSync('../typescript/bin/tsc',path.join(root,'node_modules/.bin/tsc'));
 return entry;
}
for(const layout of ['ordinary','scoped','nested'] as const)test(`installed compiler discovery follows ${layout} npm layout`,t=>{
 const root=fixture(t),entry=compiler(root);
 const alch=path.join(root,'node_modules/@cyberalchemy/alchlang');
 const craft=path.join(root,'node_modules',layout==='ordinary'?'domainspec':layout==='scoped'?'@domainspec-v2/cli':'consumer/node_modules/@domainspec-v2/cli');
 mkdirSync(alch,{recursive:true});mkdirSync(craft,{recursive:true});
 assert.equal(resolveTypeScriptCompiler(craft,undefined,alch),realpathSync(entry));
});
test('missing installed compiler rejects with an actionable diagnostic',t=>{
 const root=fixture(t);assert.throws(()=>resolveTypeScriptCompiler(root,undefined,root),/FUNCTION_TYPESCRIPT_COMPILER_MISSING.*typescript@6\.0\.3/);
});
test('explicit compiler entry is validated and does not silently fall back',t=>{
 const root=fixture(t),entry=compiler(root);
 assert.equal(resolveTypeScriptCompiler(root,entry,root),realpathSync(entry));
 assert.throws(()=>resolveTypeScriptCompiler(root,path.join(root,'absent'),root),/FUNCTION_TYPESCRIPT_COMPILER_MISSING/);
 const arbitrary=path.join(root,'wrapper.js');writeFileSync(arbitrary,'');
 assert.throws(()=>resolveTypeScriptCompiler(root,arbitrary,root),/FUNCTION_TYPESCRIPT_COMPILER_INVALID/);
});
test('incompatible installed and explicit compiler versions reject',t=>{
 const root=fixture(t),entry=compiler(root,'7.0.2');
 assert.throws(()=>resolveTypeScriptCompiler(root,entry,root),/FUNCTION_TYPESCRIPT_COMPILER_VERSION/);
 assert.throws(()=>resolveTypeScriptCompiler(root,undefined,root),/FUNCTION_TYPESCRIPT_COMPILER_MISSING.*rejected/);
});
test('an unrelated executable cannot masquerade as the declared compiler',t=>{
 const root=fixture(t);compiler(root);const other=path.join(root,'node_modules/typescript/bin/other');writeFileSync(other,'');
 assert.throws(()=>resolveTypeScriptCompiler(root,other,root),/FUNCTION_TYPESCRIPT_COMPILER_INVALID/);
});
