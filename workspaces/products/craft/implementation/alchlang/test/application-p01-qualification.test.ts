import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const evidence = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence";
const previousPath = `${evidence}/p01-package-boundaries/qualification.v4-candidate.json`;
const currentPath = `${evidence}/p01-package-boundaries/qualification.v5-candidate.json`;
const l3xPath = `${evidence}/l3-completion/qualification.v4-candidate.json`;
const dagPath = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/EXECUTION-DAG.json";
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const read = (file: string) => JSON.parse(fs.readFileSync(path.join(repo, file), "utf8"));
const digest = (file: string) => sha256(path.join(repo, file));
const implementation = 'language/capabilities/alchlang/plans/general-compiler-v1/implementation';
const cliTestPath = implementation + '/test/package-release-cli.test.ts';
const contentAlgorithm = 'sha256-json-sorted-path-size-sha256/v1';

function sourceEnvelope(value: any) {
  const boundaries = read(value.bindings.package_boundaries.path);
  const paths = new Set<string>([
    ...Object.values(value.bindings).map((binding: any) => binding.path as string),
    previousPath, l3xPath, dagPath,
    ...['package.json','package-lock.json','tsconfig.json','tsconfig.build.json',
      'scripts/run-toolchain.mjs','scripts/copy-event-templates.mjs'].map(file => implementation + '/' + file),
    'tools/toolchain/run','tools/toolchain/lock.json',
    'craft/projects/domainspec-v2/impl/cli/package-lock.json',
    ...boundaries.packages.flatMap((item: any) => item.files.map((file: string) => implementation + '/' + file)),
    ...boundaries.domainspec_cli.expanded_files.map((file: string) => boundaries.domainspec_cli.package_root + '/' + file),
  ]);
  const rows = [...paths].sort().map(file => {
    const absolute = path.join(repo, file);
    assert.equal(fs.lstatSync(absolute).isFile(), true, 'nonregular source: ' + file);
    assert.equal(fs.realpathSync(absolute), absolute, 'symlinked source: ' + file);
    return {path: file, sha256: digest(file)};
  });
  return {schema_version: 'alchlang.p01-source-envelope/v1-candidate',
    algorithm: 'sha256-json-sorted-repository-path-file-sha256/v1',
    file_count: rows.length, sha256: crypto.createHash('sha256').update(JSON.stringify(rows)).digest('hex')};
}

const inspectScript = [
  'import gzip,hashlib,io,json,os,sys,tarfile',
  'archive=sys.argv[1]',
  "assert os.path.getsize(archive)<=64*1024*1024, 'P01_ARCHIVE_SIZE'",
  'with gzip.open(archive,"rb") as compressed: raw=compressed.read(256*1024*1024+1)',
  "assert len(raw)<=256*1024*1024, 'P01_ARCHIVE_TAR_SIZE'",
  'rows=[];seen=set();total=0',
  'with tarfile.open(fileobj=io.BytesIO(raw),mode="r:") as stream:',
  ' for member in stream:',
  "  assert len(rows)<10000, 'P01_ARCHIVE_MEMBER_COUNT'",
  "  assert member.isfile(), 'P01_ARCHIVE_NONREGULAR'",
  "  assert member.name.startswith('package/'), 'P01_ARCHIVE_PATH'",
  "  relative=member.name[len('package/'):]",
  "  assert relative and chr(92) not in relative and all(p not in ('','.','..') for p in relative.split('/')), 'P01_ARCHIVE_PATH'",
  "  assert relative not in seen, 'P01_ARCHIVE_DUPLICATE'",
  "  assert 0<=member.size<=32*1024*1024, 'P01_ARCHIVE_MEMBER_SIZE'",
  '  total+=member.size',
  "  assert total<=256*1024*1024, 'P01_ARCHIVE_UNCOMPRESSED_SIZE'",
  '  seen.add(relative)',
  '  handle=stream.extractfile(member)',
  "  assert handle is not None, 'P01_ARCHIVE_CONTENT'",
  '  data=handle.read(member.size+1)',
  "  assert len(data)==member.size, 'P01_ARCHIVE_CONTENT'",
  "  rows.append({'path':relative,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})",
  "rows.sort(key=lambda row:row['path'])",
  "fingerprint=hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()",
  "print(json.dumps({'filename':os.path.basename(archive),'archive_sha256':hashlib.sha256(open(archive,'rb').read()).hexdigest(),'size_bytes':os.path.getsize(archive),'entry_count':len(rows),'content_manifest_sha256':fingerprint,'paths':[r['path'] for r in rows]}))",
].join('\n');

function inspectArchive(file: string) {
  const result = spawnSync('python3',['-I','-c',inspectScript,file],{encoding:'utf8',timeout:30000,maxBuffer:2*1024*1024});
  assert.equal(result.status,0,result.stderr);
  return JSON.parse(result.stdout);
}

function defaultArchiveSnapshot() {
  const version=read(implementation+'/package.json').version;
  const base=path.join(repo,implementation,'package-artifacts',version,'split-release');
  const rows: Array<Record<string,string>>=[];
  function visit(file: string) {
    let stat: fs.Stats;
    try { stat=fs.lstatSync(file); } catch(error) {
      if((error as NodeJS.ErrnoException).code==='ENOENT'){rows.push({path:path.relative(base,file),type:'absent'});return;}
      throw error;
    }
    const relative=path.relative(base,file);
    if(stat.isSymbolicLink())rows.push({path:relative,type:'symlink',target:fs.readlinkSync(file)});
    else if(stat.isDirectory()){rows.push({path:relative,type:'directory'});for(const entry of fs.readdirSync(file).sort())visit(path.join(file,entry));}
    else if(stat.isFile())rows.push({path:relative,type:'file',sha256:sha256(file)});
    else rows.push({path:relative,type:'other'});
  }
  visit(base);return rows;
}

function measureArchives(value: any) {
  const before=sourceEnvelope(value),defaultBefore=defaultArchiveSnapshot();
  const work=fs.mkdtempSync(path.join(os.tmpdir(),'alchlang-p01-v5-'));
  try {
    const result=spawnSync(process.execPath,[path.join(repo,implementation,'scripts/package-release.mjs'),work],
      {cwd:repo,encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});
    assert.equal(result.status,0,result.stderr);
    const packed=JSON.parse(result.stdout),boundaries=read(value.bindings.package_boundaries.path);
    assert.deepEqual(packed.artifacts.map((item:any)=>item.id),['core','rust','local-host']);
    const observed=packed.artifacts.map((artifact:any)=>{
      assert.equal(path.dirname(artifact.file),work);
      const inspected=inspectArchive(artifact.file);
      assert.deepEqual(inspected.paths,boundaries.packages.find((item:any)=>item.id===artifact.id).files);
      const {paths: _paths,...summary}=inspected;
      return {id:artifact.id,...summary};
    });
    return observed;
  } finally {
    fs.rmSync(work,{recursive:true,force:true});
    assert.deepEqual(sourceEnvelope(value),before,'selected source bytes changed during packaging');
    assert.deepEqual(defaultArchiveSnapshot(),defaultBefore,'packaging changed the repository default archives');
  }
}
let observedArchives: any[] | undefined;

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.p01-package-boundaries-qualification/v5-candidate");
  assert.equal(value.task, "P01");
  assert.equal(value.result, "blocked");
  assert.equal(value.package_shape_result, "scoped-pass");
  assert.equal(value.authority_effect, "none");
  assert.deepEqual(value.supersedes_previous_qualification, { path: previousPath, sha256: digest(previousPath) });
  assert.deepEqual(value.inherited_boundary, { task: "L3X", path: l3xPath, sha256: digest(l3xPath), result: "blocked" });
  assert.equal(read(l3xPath).result, "blocked");
  assert.deepEqual(value.dag, { path: dagPath, sha256: digest(dagPath), node: "P01" });
  const previous = read(previousPath);
  assert.deepEqual(Object.keys(value.bindings), [...Object.keys(previous.bindings),'package_release_cli_test']);
  for (const [key, binding] of Object.entries(value.bindings) as Array<[string, { path: string; sha256: string }]>) {
    assert.equal(binding.path, key==='package_release_cli_test'?cliTestPath:previous.bindings[key].path);
    assert.equal(binding.sha256, digest(binding.path), binding.path);
  }
  assert.deepEqual(value.packages.map((item: any) => item.id), ["core", "rust", "local-host", "domainspec-cli"]);
  assert.deepEqual(value.packages.map((item: any) => item.file_count), [246, 219, 227, 1595]);
  assert.deepEqual(value.packages.map((item: any) => item.allowlist_sha256), [
    "d0c58f97f31fa6657d8f34f4251286b2156646fe9032fb62e5d7d15c80533569",
    "7ae69b4b4f1468934c433d5cca260b272833d7c66ebd9814fe01a433e1546c23",
    "3362f7dc0b7811f301d8643e34c8c8e3a7ef2b9672dd789d18bc69d4c11d1b50",
    "05081140422cf4c3bc17eb0c2c4a6f80f4830f040f73b8a5335c180e11169edb",
  ]);
  assert.deepEqual(value.packages.map((item: any) => item.name), previous.packages.map((item: any) => item.name));
  const boundaries = read(value.bindings.package_boundaries.path);
  assert.deepEqual(value.packages.slice(0, 3).map((item: any) => [item.id, item.name, item.file_count, item.allowlist_sha256]),
    boundaries.packages.map((item: any) => [item.id, item.name, item.files.length, item.allowlist_sha256]));
  assert.deepEqual([value.packages[3].name, value.packages[3].file_count, value.packages[3].allowlist_sha256],
    [boundaries.domainspec_cli.name, boundaries.domainspec_cli.expanded_files.length, boundaries.domainspec_cli.expanded_allowlist_sha256]);
  assert.ok(value.packages.every((item: any) => item.exact_export_map === true && item.checkout_only_declaration_imports === 0));
  assert.equal(value.validation.typecheck, "pass");
  assert.equal(value.validation.build, "pass");
  assert.equal(value.validation.boundary_check, "pass");
  assert.deepEqual(value.validation.package_boundary_suite, { tests: 5, passed: 5, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.optional_layer_suite, { tests: 3, passed: 3, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.package_release_cli_suite, { tests: 5, passed: 5, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.combined_package_suite, { tests: 13, passed: 13, failed: 0, skipped: 0 });
  assert.deepEqual(value.source_envelope,sourceEnvelope(value));
  assert.equal(value.archive_content_algorithm,contentAlgorithm);
  observedArchives ??= measureArchives(value);
  assert.deepEqual(value.archive_observations,observedArchives);
  assert.deepEqual(value.hard_stops, { broad_directory_copy_used_as_allowlist: false, development_residue_packaged: false,
    checkout_only_declaration_import_present: false, missing_export_target: false, alchlang_archive_inventory_differs_from_allowlist: false,
    domainspec_cli_expanded_inventory_differs_from_allowlist: false, clean_consumer_claimed_before_p02: false,
    publication_or_release_performed: false, authority_effect_inferred: false });
  assert.match(value.claim_ceiling, /P01 lifecycle remains blocked by current L3X v4/u);
  assert.match(value.claim_ceiling, /three AlchLang archives/u);
  assert.equal(value.open_questions.length, 2);
}

test("P01 v5 separates freshly replayed package-shape evidence from blocked lifecycle qualification", () => {
  validate(read(currentPath));
});

test("P01 v5 rejects false passes, stale inputs, fabricated counts and archive-scope expansion", () => {
  const original = read(currentPath);
  for (const mutate of [
    (value: any) => { value.result = "scoped-pass"; },
    (value: any) => { value.inherited_boundary.result = "scoped-pass"; },
    (value: any) => { value.inherited_boundary.path = previousPath; },
    (value: any) => { value.bindings.package_boundaries.sha256 = "0".repeat(64); },
    (value: any) => { value.bindings.public_execution_request.sha256 = "0".repeat(64); },
    (value: any) => { value.packages[0].allowlist_sha256 = "0".repeat(64); },
    (value: any) => { value.packages[0].file_count += 1; },
    (value: any) => { value.packages[1].checkout_only_declaration_imports = 1; },
    (value: any) => { value.validation.combined_package_suite.passed = 7; },
    (value: any) => { value.validation.build = "not_run_current"; },
    (value: any) => { delete value.bindings.package_release_cli_test; },
    (value: any) => { value.bindings.package_release_cli_test.sha256 = "0".repeat(64); },
    (value: any) => { value.bindings.package_release_cli_test.path = previousPath; },
    (value: any) => { value.bindings.extra = value.bindings.package_builder; },
    (value: any) => { value.validation.package_release_cli_suite.passed = 4; },
    (value: any) => { value.validation.combined_package_suite.tests = 8; },
    (value: any) => { value.source_envelope.sha256 = "0".repeat(64); },
    (value: any) => { value.source_envelope.file_count += 1; },
    (value: any) => { value.archive_content_algorithm = "names-only"; },
    (value: any) => { value.archive_observations[0].archive_sha256 = "0".repeat(64); },
    (value: any) => { value.archive_observations[1].content_manifest_sha256 = "0".repeat(64); },
    (value: any) => { value.archive_observations[2].entry_count += 1; },
    (value: any) => { value.hard_stops.broad_directory_copy_used_as_allowlist = true; },
    (value: any) => { value.hard_stops.domainspec_cli_expanded_inventory_differs_from_allowlist = true; },
    (value: any) => { value.claim_ceiling = "P01 lifecycle complete"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validate(changed));
  }
});

test("historical P01 v2 through v4 remain intact but are not current", () => {
  for (const file of [`${evidence}/p01-package-boundaries/qualification.v2-candidate.json`,`${evidence}/p01-package-boundaries/qualification.v3-candidate.json`]) {
    const historical = read(file);
    assert.notEqual(digest(historical.bindings.package_boundaries.path), historical.bindings.package_boundaries.sha256);
    assert.throws(() => validate(historical));
  }
  const previous=read(previousPath);
  assert.notEqual(digest(previous.bindings.package_builder.path),previous.bindings.package_builder.sha256);
  assert.throws(()=>validate(previous));
});

test('P01 archive inspector checks regular bytes and rejects links, traversal and duplicates',()=>{
  const work=fs.mkdtempSync(path.join(os.tmpdir(),'alchlang-p01-archive-controls-'));
  const create=[
    'import io,sys,tarfile',
    'archive,kind=sys.argv[1:]',
    'with tarfile.open(archive,"w:gz") as stream:',
    " member=tarfile.TarInfo({'traversal':'package/../escape','backslash':'package/'+chr(92)+'..'+chr(92)+'escape'}.get(kind,'package/file.txt'))",
    " if kind=='link': member.type=tarfile.SYMTYPE;member.linkname='outside';stream.addfile(member)",
    ' else:',
    '  member.size=2;stream.addfile(member,io.BytesIO(b"ok"))',
    "  if kind=='duplicate': stream.addfile(member,io.BytesIO(b'ok'))",
  ].join('\n');
  try {
    for(const kind of ['valid','link','traversal','backslash','duplicate']){
      const file=path.join(work,kind+'.tgz');
      const result=spawnSync('python3',['-I','-c',create,file,kind],{encoding:'utf8',timeout:30000});
      assert.equal(result.status,0,result.stderr);
      if(kind==='valid'){
        const observed=inspectArchive(file);
        assert.deepEqual(observed.paths,['file.txt']);assert.equal(observed.entry_count,1);
        const rows=[{path:'file.txt',size_bytes:2,sha256:crypto.createHash('sha256').update('ok').digest('hex')}];
        assert.equal(observed.content_manifest_sha256,crypto.createHash('sha256').update(JSON.stringify(rows)).digest('hex'));
      }else assert.throws(()=>inspectArchive(file),new RegExp(kind==='link'?'P01_ARCHIVE_NONREGULAR':kind==='duplicate'?'P01_ARCHIVE_DUPLICATE':'P01_ARCHIVE_PATH'));
    }
  }finally{fs.rmSync(work,{recursive:true,force:true});}
});
