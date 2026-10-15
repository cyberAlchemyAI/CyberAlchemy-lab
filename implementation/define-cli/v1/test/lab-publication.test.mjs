import assert from 'node:assert/strict';
import {test} from 'node:test';
import {mkdtempSync,mkdirSync,existsSync,symlinkSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {publishDirectory} from '../src/publish-directory.mjs';
for(const type of ['empty-directory','symlink','new-target'])test(`Atomic publication handles ${type}`,()=>{
 const root=mkdtempSync(join(tmpdir(),'define-publish-'));const stage=join(root,'stage'),target=join(root,'target');mkdirSync(stage);
 try {
  if(type==='empty-directory')mkdirSync(target);
  if(type==='symlink')symlinkSync(stage,target);
  if(type==='new-target'){publishDirectory(stage,target);assert.equal(existsSync(stage),false);assert.equal(existsSync(target),true);}
  else{assert.throws(()=>publishDirectory(stage,target),/publication refused/);assert.equal(existsSync(stage),true);}
 }finally{rmSync(root,{recursive:true,force:true});}
});
