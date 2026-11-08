/** Exercise the two exact compiler archives from a clean consumer.
 * Set CRAFT_C14_CLI_TARBALL and CRAFT_C14_ALCH_TARBALL to freshly built,
 * absolute archives. No publication or local hosting is involved.
 * Open Questions: goals/plans/craft-alchlang-generic-applications-2026-10-18-r5/BUILD-MODE.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';

const craftArchive=process.env.CRAFT_C14_CLI_TARBALL;
const alchArchive=process.env.CRAFT_C14_ALCH_TARBALL;
const sha256=file=>createHash('sha256').update(readFileSync(file)).digest('hex');

test('C14 current Craft and AlchLang archives run the installed zero-claim starter unchanged',
 {skip:!craftArchive||!alchArchive},()=>{
  for(const archive of [craftArchive,alchArchive]){
   assert.equal(path.isAbsolute(archive),true,'compiler archive must be absolute');
   assert.equal(existsSync(archive),true,'compiler archive must exist');
  }
  const before={craft:sha256(craftArchive),alch:sha256(alchArchive)};
  const work=mkdtempSync(path.join(tmpdir(),'craft-c14-paired-archives-'));
  try{
   const consumer=path.join(work,'consumer');mkdirSync(consumer);
   writeFileSync(path.join(consumer,'package.json'),'{"name":"c14-paired-consumer","private":true,"type":"module"}\n');
   const env={...process.env,npm_config_update_notifier:'false'};
   delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
   const install=spawnSync('npm',['install','--offline','--ignore-scripts','--no-audit','--no-fund','--save-exact',
    craftArchive,alchArchive,'typescript@6.0.3','@types/node@26.4.0'],
    {cwd:consumer,env,encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024});
   assert.equal(install.status,0,`clean archive install failed:\n${install.stdout}\n${install.stderr}`);
   const runner=path.join(consumer,'node_modules/@cyberalchemy/alchlang/examples/cli-preview/run.mjs');
   assert.equal(existsSync(runner),true,'installed starter runner absent');
   const output=path.join(work,'preview');
   const result=spawnSync(process.execPath,[runner,'--out',output],
    {cwd:consumer,env,encoding:'utf8',timeout:900000,maxBuffer:16*1024*1024});
   assert.equal(result.status,0,`installed starter failed:\n${result.stdout}\n${result.stderr}`);
   const report=JSON.parse(readFileSync(path.join(output,'journey.json'),'utf8'));
   assert.equal(report.status,'pass');
   assert.equal(report.frozen_package_bytes_preserved,true);
   assert.equal(report.packages.alch.version,'0.7.0-candidate.0');
   assert.equal(report.packages.craft.version,'1.3.0');
   assert.ok(report.commands.some(row=>row.id==='ALCH-01'&&row.exit_code===0));
   assert.ok(report.commands.some(row=>row.id==='ALCH-06-good'&&row.exit_code===0));
   assert.deepEqual({craft:sha256(craftArchive),alch:sha256(alchArchive)},before,
    'installed proof must preserve both exact compiler archives');
  }finally{rmSync(work,{recursive:true,force:true});}
 });
