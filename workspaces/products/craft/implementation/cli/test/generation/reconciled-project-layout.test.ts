import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  PROJECT_LAYOUT,
  RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256,
  planProjectBuild,
  publishProjectBuild,
  runCli,
  selectReconciledProjectArtifacts,
  verifyProjectBuild,
} from '../../src/index.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {commerceSourceRoot, loadCommerceCorpus, writeArtifacts} from '../helpers/reconciled-commerce-corpus.ts';
import {nodeExecutable, repositoryToolchain, typeScriptToolchain} from '../helpers/local-toolchain.ts';

const {compiler: typescriptCompiler, typeRoots: nodeTypes}=typeScriptToolchain();
const python='/usr/bin/python3';
const cargo=repositoryToolchain();

function workspace(t:test.TestContext,prefix:string):string {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),prefix));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  return root;
}

function allFiles(root:string,extension:string):string[] {
  const files:string[]=[];
  const walk=(directory:string):void=>{
    for(const entry of fs.readdirSync(directory,{withFileTypes:true})){
      const file=path.join(directory,entry.name);
      if(entry.isDirectory())walk(file);else if(file.endsWith(extension))files.push(file);
    }
  };
  walk(root);return files.sort();
}

test('project layout is deterministic and gives every profile one coherent native source tree',()=>{
  const corpus=loadCommerceCorpus();
  assert.equal(sha256(fs.readFileSync(path.resolve(import.meta.dirname,'../../contracts/reconciled-project-layout-definition.json'))),RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256);
  for(const [language,plan] of Object.entries(corpus.plans)){
    const first=selectReconciledProjectArtifacts(plan),second=selectReconciledProjectArtifacts(plan);
    assert.deepEqual(first,second,language);
    assert.equal(first.output_layout,PROJECT_LAYOUT.id);
    assert.ok(first.source_view_sha256);
    assert.ok(first.artifacts.every(row=>row.relative_path.startsWith('src/')||(language==='rust'&&['Cargo.toml','Cargo.lock'].includes(row.relative_path))),language);
    assert.ok(first.artifacts.some(row=>row.relative_path.includes('/features/commerce/domain/')),language);
    assert.ok(first.artifacts.some(row=>row.relative_path.includes('/features/commerce/application/')),language);
    assert.ok(!first.artifacts.some(row=>row.relative_path.includes('/features/commerce/src/')),language);
  }
  const typescript=selectReconciledProjectArtifacts(corpus.plans.typescript);
  assert.ok(typescript.artifacts.some(row=>row.relative_path==='src/shared/domain/enum.ts'));
  const pythonView=selectReconciledProjectArtifacts(corpus.plans.python);
  assert.ok(pythonView.artifacts.some(row=>row.relative_path==='src/commerce_corpus/shared/domain/values.py'));
  const rust=selectReconciledProjectArtifacts(corpus.plans.rust);
  assert.ok(rust.artifacts.some(row=>row.relative_path==='src/lib.rs'));
  assert.ok(rust.artifacts.some(row=>row.relative_path==='src/features/commerce/domain/types/order.rs'));
});

test('project-layout TypeScript, Python and Rust bytes compile in their published native structures',t=>{
  const corpus=loadCommerceCorpus(),root=workspace(t,'domainspec-project-layout-native-');

  const typescript=selectReconciledProjectArtifacts(corpus.plans.typescript),typescriptRoot=path.join(root,'typescript');
  writeArtifacts(typescriptRoot,typescript.artifacts);
  const output=path.join(root,'typescript-dist'),typescriptFiles=allFiles(path.join(typescriptRoot,'src'),'.ts');
  execFileSync(nodeExecutable(),[typescriptCompiler,'--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',nodeTypes,'--target','ES2022','--module','NodeNext','--rootDir',path.join(typescriptRoot,'src'),'--outDir',output,...typescriptFiles],{encoding:'utf8',timeout:120000});

  const pythonView=selectReconciledProjectArtifacts(corpus.plans.python),pythonRoot=path.join(root,'python');
  writeArtifacts(pythonRoot,pythonView.artifacts);
  execFileSync(python,['-I','-S','-B','-m','compileall','-q',path.join(pythonRoot,'src')],{encoding:'utf8',timeout:120000});
  const imports=pythonView.modules.map(row=>row.relative_path.slice(4,-3).replaceAll('/','.').replace(/\.__init__$/, '')).filter(Boolean);
  execFileSync(python,['-I','-S','-B','-c',`import sys\nsys.path.insert(0,${JSON.stringify(path.join(pythonRoot,'src'))})\n${imports.map(name=>`__import__(${JSON.stringify(name)})`).join('\n')}`],{encoding:'utf8',timeout:120000});

  const rust=selectReconciledProjectArtifacts(corpus.plans.rust),rustRoot=path.join(root,'rust');
  writeArtifacts(rustRoot,rust.artifacts);
  execFileSync(cargo,['cargo','check','--quiet','--offline','--locked'],{cwd:rustRoot,encoding:'utf8',timeout:120000,env:{...process.env,RUSTFLAGS:'-Awarnings'}});
});

test('build, receipt and verification bind the selected project layout for every profile',t=>{
  const corpus=loadCommerceCorpus(),root=workspace(t,'domainspec-project-layout-output-');
  for(const language of ['typescript','python','rust'] as const){
    const selection=corpus.selections[language],build=planProjectBuild(commerceSourceRoot,language,undefined,PROJECT_LAYOUT.id,selection),target=path.join(root,language);
    const publication=publishProjectBuild(build,target);
    assert.equal(publication.receipt_path,PROJECT_LAYOUT.receipt);
    assert.equal(build.receipt.output_layout,PROJECT_LAYOUT.id);
    assert.equal(verifyProjectBuild(commerceSourceRoot,language,target,undefined,PROJECT_LAYOUT.id,selection).result,'pass');
    assert.equal(fs.readFileSync(path.join(target,PROJECT_LAYOUT.receipt),'utf8'),canonicalJson(build.receipt)+'\n');
  }
  const selectionFile=path.join(root,'typescript-selection.json'),cliTarget=path.join(root,'typescript-cli');
  fs.writeFileSync(selectionFile,JSON.stringify(corpus.selections.typescript));
  let stdout='';
  const code=runCli(['build',commerceSourceRoot,'--language','typescript','--target-root',cliTarget,'--output-layout',PROJECT_LAYOUT.id,'--compilation-selection',selectionFile],{stdout:value=>{stdout+=value;},stderr:value=>{stdout+=value;}});
  assert.equal(code,0,stdout);
  assert.equal(JSON.parse(stdout).receipt_path,PROJECT_LAYOUT.receipt);
  assert.ok(fs.existsSync(path.join(cliTarget,'src/features/commerce/domain/entities/order.ts')));
  assert.throws(()=>planProjectBuild('/path/that/must/not/be/read','typescript',undefined,PROJECT_LAYOUT.id),/requires a reconciled compilation selection/);
});
