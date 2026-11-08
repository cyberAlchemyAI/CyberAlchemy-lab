/** One clean installed proof for generated connected applications and portfolio.
 * Consumes an existing local distribution; never builds, hosts or publishes.
 * Open Questions: goals/plans/craft-connected-applications-2026-11-02/DESIGN.md. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync,mkdirSync,existsSync,copyFileSync,renameSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const repository=path.resolve(import.meta.dirname,'../../..'),here=import.meta.dirname;
const core=path.resolve(here,'../cli'),native=path.resolve(here,'../profiles/ai');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex'),json=file=>JSON.parse(readFileSync(file,'utf8'));
const ref=file=>({path:path.resolve(file),sha256:sha(readFileSync(file))});
const walk=directory=>readdirSync(directory,{withFileTypes:true}).flatMap(row=>['node_modules','.git','.work'].includes(row.name)?[]:row.isDirectory()?walk(path.join(directory,row.name)):row.isFile()?[path.join(directory,row.name)]:[]);
const counts=text=>Object.fromEntries(['tests','pass','fail','cancelled','skipped','todo'].map(name=>[name,Number(text.match(new RegExp('^# '+name+' ([0-9]+)$','m'))?.[1]??0)]));
const assertPins=pins=>{for(const pin of pins)assert.equal(sha(readFileSync(pin.path)),pin.sha256,'captured input changed: '+pin.path);};
function copyPinnedInput(source,target,transform){const captured=readFileSync(source),originalSha=sha(captured),expected=transform?Buffer.from(transform(new TextDecoder('utf-8',{fatal:true}).decode(captured)),'utf8'):captured,expectedSha=sha(expected);writeFileSync(target,expected);assert.equal(sha(readFileSync(source)),originalSha,'source changed during installed check copy: '+source);assert.equal(sha(readFileSync(target)),expectedSha,'installed check differs from captured/transformed bytes: '+target);return {original:{path:path.resolve(source),sha256:originalSha},installed:{path:path.resolve(target),sha256:expectedSha},transform:{kind:originalSha===expectedSha?'exact-byte-copy':'installed-private-native-imports',expected_sha256:expectedSha}};}

export function prepareInstalledConnectedChecks({distributionReport,label='focused-'+Date.now()}={}){
 assert.equal(process.versions.node,'26.12.1','selected Node runtime required');assert.ok(path.isAbsolute(distributionReport??''),'existing absolute DISTRIBUTION.json required');
 const distribution=json(distributionReport);assert.equal(distribution.status,'built-and-installed');
 // Validate the exact built tuple before assigning an applicable result. A stale
 // package may still work, but it cannot prove the current mutable objective.
 assertPins(distribution.source_inputs);for(const archive of distribution.archives)assert.equal(sha(readFileSync(archive.file??archive.path)),archive.sha256,'archive identity changed');
 for(const file of distribution.native_build.files){assert.equal(sha(readFileSync(path.join(native,file.path))),file.sha256,'selected native source differs');for(const consumer of Object.values(distribution.consumers))assert.equal(sha(readFileSync(path.join(consumer,'node_modules/@craft/ai-profiles',file.path))),file.sha256,'installed native differs');}
 const consumer=distribution.consumers.direct;assert.ok(path.isAbsolute(consumer));const installedCore=path.join(consumer,'node_modules/@domainspec-v2/cli'),library=path.join(installedCore,'examples/technical-profile-source');
 for(const source of walk(path.join(core,'examples/technical-profile-source')))assert.equal(sha(readFileSync(path.join(installedCore,path.relative(core,source)))),sha(readFileSync(source)),'installed source example differs: '+source);
 const testNames=['recorded-marketing-fixture.test.mjs','application-system-bindings.test.mjs','connected-applications-recovery.test.mjs','portfolio-business-applications.test.mjs'],helperNames=['connected-application-fixtures.mjs','service-profile-fixtures.mjs','recorded-marketing-fixture.mjs'];
 const testsAndHelpers=[...[...testNames,...helperNames].map(name=>path.join(here,name)),path.join(native,'native/application/gateway-source-subjects.test.mjs')];for(const file of testsAndHelpers)assert.ok(existsSync(file),'selected test/helper required: '+file);
 const requiredPortfolioTitle='generated portfolio applications consume genuine current RAG answers through source-selected cited review';assert.ok(readFileSync(path.join(here,'portfolio-business-applications.test.mjs'),'utf8').includes(requiredPortfolioTitle),'genuine cited integration test must exist before final proof');
 assert.ok(typeof label==='string'&&/^[A-Za-z0-9_-]+$/.test(label),'bounded installed check label');const testDirectory=path.join(consumer,'connected-checks',label);assert.equal(existsSync(testDirectory),false,'fresh installed test-copy directory');mkdirSync(testDirectory,{recursive:true});
 const copied=[];for(const source of testsAndHelpers){const target=path.join(testDirectory,path.basename(source));
  // Private native imports address the exact installed implementation. Local
  // fixture imports retain their copied sibling paths; no source loader runs.
  copied.push(copyPinnedInput(source,target,text=>text.replace(/(from\s+)(['"])(\.[^'"]+)\2/g,(original,prefix,_quote,specifier)=>{const file=path.resolve(path.dirname(source),specifier),relative=path.relative(native,file);if(relative===''||relative==='..'||relative.startsWith('..'+path.sep)||path.isAbsolute(relative))return original;return prefix+JSON.stringify(pathToFileURL(path.join(consumer,'node_modules/@craft/ai-profiles',relative)).href);})));}
 const fixtureRoot=path.join(testDirectory,'reference-fixtures'),referenceSource=path.join(here,'fixtures'),fixtureNames=['invoice/fixtures/posting-inputs.json','invoice/fixtures/journey-cases.json','invoice/fixtures/invoice-text.pdf','invoice/fixtures/invoice-image-only.pdf','marketing/fixtures/journey-cases.json','crm/preferences.alch','crm/journey.alch','crm/entries.alch',...walk(path.join(referenceSource,'crm/contracts')).map(file=>path.relative(referenceSource,file))];
 const copiedFixtures=[];for(const name of fixtureNames){const target=path.join(fixtureRoot,name);mkdirSync(path.dirname(target),{recursive:true});copiedFixtures.push(copyPinnedInput(path.join(referenceSource,name),target));}
 const env={...process.env,PATH:path.dirname(process.execPath)+path.delimiter+process.env.PATH,npm_config_offline:'true'};
 for(const key of Object.keys(env))if(key==='NODE_OPTIONS'||key==='NODE_PATH'||key.startsWith('CRAFT_')||key.startsWith('ALCHLANG_'))delete env[key];
 Object.assign(env,{CRAFT_PROFILE_INPUT_INSTALLED_ROOT:consumer,CRAFT_SERVICE_REFERENCE_FIXTURE_ROOT:fixtureRoot,CRAFT_KEEP_PROFILE_INPUT_TEST_OUTPUT:'1',CRAFT_KEEP_PORTFOLIO_OUTPUT:'1'});
 return {distribution,consumer,installedCore,library,testDirectory,copied,copiedFixtures,fixtureRoot,fixtureNames,referenceSource,testsAndHelpers,requiredPortfolioTitle,environment:env};
}

