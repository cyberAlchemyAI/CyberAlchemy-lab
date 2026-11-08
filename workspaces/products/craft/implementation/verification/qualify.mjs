/** Repeatable broader local verification; keeps one current result, no old run archive.
 * Open questions: README.md. Recorded fixtures only; no publication or runtime cutover.
 */
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,lstatSync,realpathSync,statSync,existsSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {implementationRoot as root,labRoot,upstreamRoot,domainSource} from '../source-bindings.mjs';
import {prepareDistribution,selectedNode,cleanEnvironment,walk,pin} from './distribution.mjs';

const local=path.join(root,'.local'),json=f=>JSON.parse(readFileSync(f,'utf8'));
mkdirSync(local,{recursive:true});
const digest=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
function step(id,command,{cwd=root,env={}}={}){
  console.log('stage '+id);const started=Date.now(),result=spawnSync(command[0],command.slice(1),{cwd,env:{...cleanEnvironment(),...env},encoding:'utf8',maxBuffer:32*1024*1024});
  const log=path.join(local,'broader-'+id+'.log');writeFileSync(log,String(result.stdout??'')+String(result.stderr??''));
  return {...result,record:{id,exit_code:result.status,signal:result.signal,duration_ms:Date.now()-started,log:pin(log)}};
}
function distribution(){
  const workspace=mkdtempSync(path.join(tmpdir(),'craft-broader-'));
  const result=prepareDistribution(workspace,{step:(id,args,options)=>{const row=step(id,args,options);assert.equal(row.status,0,id+': '+String(row.stderr||row.stdout||row.error).slice(-2000));return row;}});
  writeFileSync(path.join(local,'broader-distribution.json'),JSON.stringify({workspace,report:result.file,consumer:result.consumer})+'\n');
  const apps=step('applications-run',[selectedNode,path.join(root,'verification/run-applications.mjs')]);
  // Tests can fail; collection must preserve their exact counts and failures.
  return apps.record;
}
function components(){
  const source_inputs=[...['test-derivation-engine/src','tools/minted-project','tools/lib','spec','formalization/evf','operational-resilience'].flatMap(p=>walk(path.join(root,p))),...walk(path.join(root,'verification')).filter(p=>p.endsWith('.mjs')),
    ...walk(path.join(labRoot,'craft/authority/definitions')),...['graph-law-request.v1.schema.json','graph-law-join-receipt.v1.schema.json','graph-law-provider-receipt.v1.schema.json'].map(p=>domainSource('development/evolvable-validation-framework/contracts/'+p)),...['source-bindings.mjs','source-layout.json','verification/qualify.mjs','operational-resilience/body-war-canary-test-all.sh','alchlang/node_modules/typescript/package.json','node_modules/tsx/package.json'].map(p=>path.join(root,p))].filter(p=>!p.includes('/__pycache__/')&&!p.endsWith('.pyc')&&!p.endsWith('/component.json')).sort().map(pin);
  const checks=[];
  checks.push(step('tde',[selectedNode,path.join(root,'test-derivation-engine/node_modules/vitest/vitest.mjs'),'run','--maxWorkers=1','--minWorkers=1','--no-file-parallelism','--reporter=json','--outputFile='+path.join(local,'broader-tde-result.json')],{cwd:path.join(root,'test-derivation-engine')}).record);
  checks.push(step('evf',[path.join(upstreamRoot,'tools/toolchain/run'),'cargo','test','--offline','--locked','--workspace','--manifest-path',path.join(root,'formalization/evf/Cargo.toml')],{env:{CARGO_TARGET_DIR:path.join(local,'evf-test-target')}}).record);
  checks.push(step('body-war',['bash',path.join(root,'operational-resilience/body-war-canary-test-all.sh')]).record);
  const body=path.join(root,'operational-resilience');
  // The aggregate fails closed. Still execute the independent, pure test owners.
  for(const name of ['evaluator','evidence','observer','recovery','rollback','tabletop','workload'])checks.push(step('body-war-python-'+name,['python3','-m','unittest','discover','-s','test','-p','test_body_war_canary_'+name+'.py'],{cwd:body}).record);
  checks.push(step('body-war-static',['python3',path.join(body,'body-war-canary-validate-static.py')]).record);
  for(const input of source_inputs)assert.equal(pin(input.path).sha256,input.sha256,'component input changed: '+input.path);
  writeFileSync(path.join(local,'broader-components.json'),JSON.stringify({checks,source_inputs,inputs_unchanged:true,finished_at:new Date().toISOString()},null,2)+'\n');
}
function collect(){
  const apps=json(path.join(local,'broader-applications.json')),component=json(path.join(local,'broader-components.json')),tde=json(path.join(local,'broader-tde-result.json'));
  assert(['passed','failed'].includes(apps.status));assert(component.inputs_unchanged&&apps.inputs_unchanged);
  let preferenceRepair=null,focused=null,portfolioRetest=null;
  const originalConnected=apps.checks.find(x=>x.id==='connected'),originalConnectedLog=path.join(local,'broader-applications-connected.log');
  assert.equal(pin(originalConnectedLog).sha256,originalConnected.log_sha256);
  const originalConnectedText=readFileSync(originalConnectedLog,'utf8');
  const originalFailureTitles=[...originalConnectedText.matchAll(/^\s*not ok \d+ - ([^\r\n]+)/gm)].map(m=>m[1]);
  const stopFile=path.join(local,'broader-portfolio-initial-stop.json'),initialStop=existsSync(stopFile)?json(stopFile):null;
  const focusedFile=path.join(local,'broader-preference-retest.json'),repairFile=path.join(local,'broader-preference-repair.json');
  if(apps.status==='failed'&&existsSync(focusedFile)&&existsSync(repairFile)){
    const candidate=json(focusedFile),repair=json(repairFile),connected=apps.checks.find(x=>x.id==='connected');
    if(candidate.original_matrix_finished_at===apps.finished_at&&candidate.original_connected_log_sha256===connected.log_sha256){
      assert.equal(repair.target,path.join(root,'verification/connected-applications-recovery.test.mjs'));
      assert.equal(apps.source_inputs.find(x=>x.path===repair.target).sha256,repair.original_sha256);
      assert.equal(pin(repair.target).sha256,repair.current_sha256);
      const current=readFileSync(repair.target,'utf8');assert.equal(current.split(repair.new_fragment).length,2);
      assert.equal(createHash('sha256').update(current.replace(repair.new_fragment,repair.original_fragment)).digest('hex'),repair.original_sha256,'test changes must be confined to the declared preference lease repair');
      assert.deepEqual(candidate.package_tuple,apps.distribution.archives.map(({name,version,sha256})=>({name,version,sha256})));
      assert.equal(candidate.selectors.CRAFT_CONNECTED_CASE,'query-permission-and-preference');assert.equal(candidate.selectors.CRAFT_CONNECTED_BRANCH,'preference');
      assert(candidate.inputs_unchanged);if(candidate.status==='passed')assert.deepEqual(candidate.counts,{tests:3,pass:3,fail:0,skipped:0,cancelled:0,todo:0});
      assert(originalConnectedText.includes('C13_WORKFLOW_STALE_CLAIM'),'the declared lease failure must exist in the original run');
      preferenceRepair={...repair,module_unchanged_outside_declared_fragment:true,package_tuple_unchanged:true,full_matrix_repeated_after_test_only_repair:false};focused=candidate;
    }
  }
  const portfolioFile=path.join(local,'broader-portfolio-retest.json');
  if(existsSync(portfolioFile)){
    const candidate=json(portfolioFile);
    if(candidate.original_matrix_finished_at===apps.finished_at){
      assert.equal(candidate.mode,'portfolio');assert(candidate.inputs_unchanged);
      assert.deepEqual(candidate.package_tuple,apps.distribution.archives.map(({name,version,sha256})=>({name,version,sha256})));
      if(candidate.status==='passed')assert.deepEqual(candidate.counts,{tests:6,pass:6,fail:0,skipped:0,cancelled:0,todo:0});
      portfolioRetest=candidate;
    }
  }
  const commandAliases=[];
  for(const archive of apps.distribution.archives){
    const home=path.join(apps.distribution.consumers.direct,'node_modules',archive.name),metadata=json(path.join(home,'package.json'));
    const bins=typeof metadata.bin==='string'?{[archive.name.split('/').at(-1)]:metadata.bin}:metadata.bin??{};
    for(const [name,relative] of Object.entries(bins)){
      const alias=path.join(apps.distribution.consumers.direct,'node_modules/.bin',name),target=path.join(home,relative);
      assert(lstatSync(alias).isSymbolicLink());assert.equal(realpathSync(alias),realpathSync(target));assert(statSync(target).mode&0o111);
      commandAliases.push({name,package:archive.name,target:relative,sha256:pin(target).sha256});
    }
  }
  for(const archive of apps.distribution.local_dependency_archives){
    const home=path.join(apps.distribution.consumers.direct,'node_modules',archive.name);
    const sourceHome=path.join(upstreamRoot,'output/craft-connected-applications-2026-11-02/distribution-repaired/direct-consumer/node_modules',archive.name);
    for(const relative of archive.files)assert.equal(pin(path.join(home,relative)).sha256,pin(path.join(sourceHome,relative)).sha256,'repacked dependency differs: '+archive.name+'/'+relative);
  }
  const tdeFailures=tde.testResults.flatMap(s=>s.assertionResults.filter(a=>a.status==='failed').map(a=>({file:path.relative(root,s.name),test:a.fullName,message:a.failureMessages.join(' ').split('\n')[0]})));
  const checks=component.checks.map(row=>({...row,log:{path:path.relative(labRoot,row.log.path),sha256:row.log.sha256}}));
  const originalTestInputs=apps.source_inputs.map(p=>preferenceRepair&&p.path===preferenceRepair.target?{path:p.path,sha256:preferenceRepair.current_sha256}:p);
  const allInputs=[...apps.distribution.source_inputs,...apps.distribution.local_dependency_archives.flatMap(a=>a.source_inputs),...originalTestInputs,...(focused?.source_inputs??[]),...(portfolioRetest?.source_inputs??[]),...component.source_inputs];
  for(const input of allInputs)assert.equal(pin(input.path).sha256,input.sha256,'qualified input changed: '+input.path);
  const selectedInputs=[...new Map(allInputs.map(p=>[p.path,p])).values()].sort((a,b)=>a.path.localeCompare(b.path));
  const evf=readFileSync(path.join(local,'broader-evf.log'),'utf8'),body=readFileSync(path.join(local,'broader-body-war.log'),'utf8');
  const evfCounts=[...evf.matchAll(/test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored/g)].reduce((a,m)=>({passed:a.passed+Number(m[1]),failed:a.failed+Number(m[2]),ignored:a.ignored+Number(m[3])}),{passed:0,failed:0,ignored:0});
  const nodeCount=key=>Number(body.match(new RegExp('(?:ℹ|#) '+key+' (\\d+)'))?.[1]??0);
  const python=checks.filter(c=>c.id.startsWith('body-war-python-')).map(c=>({id:c.id,exit_code:c.exit_code,tests:Number(readFileSync(path.join(labRoot,c.log.path),'utf8').match(/Ran (\d+) tests?/)?.[1]??0)}));
  const report={schema_version:'craft.broader-local-qualification/v1',status:checks.some(c=>c.exit_code!==0)||apps.status!=='passed'?'completed-with-gaps':'passed-local-scope',finished_at:new Date().toISOString(),authority_effect:'none',toolchain:{node:{version:process.version,...pin(selectedNode)}},
    installed:{status:apps.status,checks:apps.checks,original_connected_failed_titles:originalFailureTitles,command_aliases:commandAliases,package_tuple:apps.distribution.archives.map(({name,version,sha256})=>({name,version,sha256})),dependency_archives:apps.distribution.local_dependency_archives.map(({name,version,sha256})=>({name,version,sha256})),scope:apps.distribution.scope,provider_model_scope:'Recorded fixtures only; no real provider or model-quality result.',inputs_unchanged_during_original_run:apps.inputs_unchanged,test_only_repair:preferenceRepair,focused_retest:focused?{status:focused.status,counts:focused.counts,selectors:focused.selectors,duration_ms:focused.duration_ms,log_sha256:focused.log_sha256,scope:focused.scope}:null,portfolio_retest:portfolioRetest?{status:portfolioRetest.status,counts:portfolioRetest.counts,duration_ms:portfolioRetest.duration_ms,log_sha256:portfolioRetest.log_sha256,scope:portfolioRetest.scope,fixture_lifetime:portfolioRetest.fixture_lifetime}:null,initial_portfolio_stop:initialStop?.original_matrix_finished_at===apps.finished_at?initialStop.reason:null,counting_rule:'Original whole-matrix counts retain their failures and interrupted portfolio. The focused preference leaf/group/root and full portfolio rerun are separate results, never added to the original totals.'},
    tde:{total:tde.numTotalTests,passed:tde.numPassedTests,failed:tde.numFailedTests,pending:tde.numPendingTests,success:tde.success,failures:tdeFailures},
    evf:{...evfCounts,exit_code:checks.find(c=>c.id==='evf').exit_code,scope:'Workspace compilation and eight kernel contract tests; provider binaries contain no tests. No live provider qualification.'},
    body_war:{aggregate_exit_code:checks.find(c=>c.id==='body-war').exit_code,node:{tests:nodeCount('tests'),passed:nodeCount('pass'),failed:nodeCount('fail')},python,static_exit_code:checks.find(c=>c.id==='body-war-static').exit_code,classification:'reference-application',runtime_state:'not-qualified',aggregate_failure:body.includes('AssertionError:')?body.split('AssertionError:').at(-1).trim():null},
    commands:checks,source_inputs:selectedInputs,
    selected_input_set_sha256:digest(selectedInputs),selected_inputs_unchanged:preferenceRepair===null,selected_inputs_current:true,inputs_unchanged_during_each_run:true,runtime_package_inputs_unchanged_across_runs:true,repacked_dependency_files_match_shared_inputs:true,temporary_packages:'Archives and unpacked consumer are test-only, not publication artifacts or copied host runtimes.',
    historical_evidence_restored:false,publication:false,global_consumer_cutover:false,listeners_started:0,
    not_qualified:['real providers','measured model quality','production identity','production deployment','default runtime cutover','full TDE/EVF application certification','Body War live execution/commissioning','optional ARE agent integration','registry installation'],
    open_questions_ref:'craft/implementation/verification/README.md'};
  writeFileSync(path.join(labRoot,'craft/work/outcomes/current-verification/broader-qualification.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:report.status,applications:apps.checks.map(r=>({id:r.id,status:r.status,counts:r.counts})),tde:{passed:report.tde.passed,failed:report.tde.failed,pending:report.tde.pending},evf:report.evf,body_war:report.body_war}));
  if(report.status!=='passed-local-scope')process.exitCode=1;
}
function cleanup(){
  const state=json(path.join(local,'broader-distribution.json')),workspace=path.resolve(state.workspace);
  assert.equal(path.dirname(workspace),realpathSync(tmpdir()));assert(path.basename(workspace).startsWith('craft-broader-'));
  assert(lstatSync(workspace).isDirectory()&&!lstatSync(workspace).isSymbolicLink());
  assert.equal(state.report,path.join(workspace,'DISTRIBUTION.json'));
  const distribution=json(state.report),apps=json(path.join(local,'broader-applications.json'));
  assert.equal(distribution.destination,workspace);assert.equal(distribution.consumers.direct,path.join(workspace,'consumer'));
  assert.equal(json(path.join(workspace,'consumer/package.json')).name,'craft-isolated-local-consumer');
  assert.notEqual(apps.status,'running','original owners must finish before cleanup');
  for(const mode of ['preference','portfolio']){const file=path.join(local,'broader-'+mode+'-retest.json');if(existsSync(file)){const result=json(file);if(result.original_matrix_finished_at===apps.finished_at)assert.notEqual(result.status,'running','retest owners must finish before cleanup');}}
  const report=json(path.join(labRoot,'craft/work/outcomes/current-verification/broader-qualification.json'));
  assert(report.selected_inputs_current);assert.deepEqual(report.installed.package_tuple,distribution.archives.map(({name,version,sha256})=>({name,version,sha256})));
  rmSync(workspace,{recursive:true,force:true});console.log(JSON.stringify({temporary_workspace_removed:workspace,host_runtimes_removed:false}));
}
const mode=process.argv[2]??'all';
if(mode==='all'){distribution();components();collect();cleanup();}
else if(mode==='--components')components();else if(mode==='--collect')collect();else if(mode==='--cleanup')cleanup();else throw Error('Usage: qualify.mjs [--components | --collect | --cleanup]');
