import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const evidenceRoot = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers");
const qualificationPath = path.join(evidenceRoot, "successor-v6-candidate/qualification.json");
const historicalQualificationPath = path.join(evidenceRoot, "successor-v5-candidate/qualification.json");
const languages = ["typescript", "python", "rust"] as const;
const startup = { typescript: "http-listener", python: "asgi-http-listener", rust: "axum-http-listener" } as const;
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");


const implementation = "language/capabilities/alchlang/plans/general-compiler-v1/implementation";
const planRoot = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1";
const p01Path = planRoot + "/evidence/p01-package-boundaries/qualification.v5-candidate.json";
const read = (file: string) => JSON.parse(fs.readFileSync(path.join(repo, file), "utf8"));
function sourceEnvelope(value: any) {
  const p01 = read(p01Path), boundaries = read(value.bindings.package_boundaries.path);
  const p01Paths = [
    ...Object.values(p01.bindings).map((b: any) => b.path as string),
    p01.supersedes_previous_qualification.path, p01.inherited_boundary.path, p01.dag.path,
    ...["package.json","package-lock.json","tsconfig.json","tsconfig.build.json","scripts/run-toolchain.mjs","scripts/copy-event-templates.mjs"].map(f => implementation + "/" + f),
    "tools/toolchain/run","tools/toolchain/lock.json","craft/projects/domainspec-v2/impl/cli/package-lock.json",
    ...boundaries.packages.flatMap((item: any) => item.files.map((f: string) => implementation + "/" + f)),
    ...boundaries.domainspec_cli.expanded_files.map((f: string) => boundaries.domainspec_cli.package_root + "/" + f),
  ];
  const p01Rows = [...new Set<string>(p01Paths)].sort().map(file => {
    const absolute = path.join(repo, file);
    assert.equal(fs.lstatSync(absolute).isFile(), true);
    assert.equal(fs.realpathSync(absolute), absolute);
    return {path: file, sha256: sha256(absolute)};
  });
  assert.deepEqual(p01.source_envelope, {schema_version: "alchlang.p01-source-envelope/v1-candidate",
    algorithm: "sha256-json-sorted-repository-path-file-sha256/v1", file_count: p01Rows.length,
    sha256: crypto.createHash("sha256").update(JSON.stringify(p01Rows)).digest("hex")});
  const selected = [...p01Paths,p01Path,value.supersedes_previous_qualification.path,
    value.supersedes_historical_qualification.path,value.inherited_boundaries.O01.path,
    ...["scripts/qualify-p02-clean-consumers-v6.ts","scripts/qualify-p02-clean-consumers.ts",
      "test/application-p02-qualification.test.ts","scripts/materialize-application-v1-examples.ts",
      "CLEAN-CONSUMER.md","test/fixtures/application-whole-fixture.ts"].map(f => implementation + "/" + f)];
  const rows = [...new Set<string>(selected)].sort().map(file => {
    const absolute = path.join(repo,file);
    assert.equal(fs.lstatSync(absolute).isFile(),true);
    assert.equal(fs.realpathSync(absolute),absolute);
    return {path:file,sha256:sha256(absolute)};
  });
  return {schema_version:"alchlang.p02-source-envelope/v1-candidate",
    algorithm:"sha256-json-sorted-repository-path-file-sha256/v1",file_count:rows.length,
    sha256:crypto.createHash("sha256").update(JSON.stringify(rows)).digest("hex")};
}

function validateBinding(binding: { path: string; sha256: string }): void {
  assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
}

function validateReport(report: any, language: typeof languages[number]): void {
  assert.equal(report.schema_version, "alchlang.p02-clean-consumer-report/v1-candidate");
  assert.equal(report.task, "P02");
  assert.equal(report.language, language);
  assert.equal(report.result, "pass");
  assert.equal(report.authority_effect, "none");
  assert.equal(report.installed_outside_checkout, true);
  assert.equal(report.documented_source.package, "@cyberalchemy/alchlang");
  assert.equal(report.documented_source.path, `examples/application-v1/${language}/commerce.alch`);
  assert.deepEqual(report.installed_packages.map((item: any) => item.name),
    language === "rust" ? ["@cyberalchemy/alchlang", "@domainspec-v2/cli", "@cyberalchemy/alchlang-rust"] : ["@cyberalchemy/alchlang", "@domainspec-v2/cli"]);
  if (language === "rust") assert.ok(report.installed_packages.some((item: any) => item.name === "@cyberalchemy/alchlang-rust"));
  if (language === "typescript") assert.equal(report.installed_packages.some((item: any) => item.name === "@cyberalchemy/alchlang-local-host"), false);
  assert.deepEqual(report.application.check.status, "valid");
  assert.equal(report.application.check.scope, "provider-application-artifacts");
  assert.equal(report.application.lowering, "pass");
  assert.equal(report.application.build.status, "built");
  assert.equal(report.application.verify_before.status, "verified");
  assert.equal(report.application.verify_after.status, "verified");
  assert.equal(report.application.verify_before.manifest_sha256, report.application.build.manifest_sha256);
  assert.equal(report.application.verify_after.manifest_sha256, report.application.build.manifest_sha256);
  assert.equal(report.application.native.native_compilation, "pass");
  const dependencyInstall = {typescript:"npm-ci-locked-registry-read",python:"pip-locked-registry-read",rust:"cargo-locked-offline"};
  assert.equal(report.application.native.dependency_install,dependencyInstall[language]);
  assert.equal(typeof report.application.native.compiler,"string");
  assert.ok(report.application.native.compiler.length>0);
  if(language==="python") {
    assert.match(report.application.native.compiler_identity.executable_sha256,/^[a-f0-9]{64}$/u);
    assert.equal(report.application.native.compiler_identity.base_executable_sha256,report.application.native.compiler_identity.executable_sha256);
    assert.equal(report.application.native.compiler_identity.version,report.application.native.compiler);
  }
  assert.deepEqual(report.application.native.scenario, {
    language,
    startup: startup[language],
    invalid_status: 401,
    valid_status: 202,
    handler_invocations: 1,
    result: "pass",
  });
  assert.deepEqual(report.application.inspection.integration_relationships, ["accepts-request", "invokes", "produces-message-contract", "publishes-event", "reads-payload-from"]);
  assert.equal(report.application.inspection.inbound_route.method, "POST");
  assert.match(report.application.inspection.inbound_route.path, /^\/[A-Za-z0-9/_-]+$/u);
  assert.equal(report.application.inspection.inbound_route.path.includes("//"), false);
  assert.ok(report.application.inspection.files.external_api_routes.sha256);
  assert.deepEqual(report.cleanup, { consumer_root_disposed: true, native_root_disposed: true, task_owned_temporary_resources_disposed: true });
  assert.equal(report.product_owner_validation, "deferred-to-L4X");
  assert.equal(report.publication, false);
  assert.equal(report.release, false);
  assert.equal(report.deployment, false);
  assert.doesNotMatch(JSON.stringify(report), /alchlang-p02-clean-consumers-/u);
  assert.match(report.claim_ceiling, /P02 clean installed-consumer construction evidence only/u);
}

function validateQualification(value: any): void {
  assert.equal(value.schema_version, "alchlang.p02-clean-consumers-qualification/v6-candidate");
  assert.equal(value.task, "P02");
  assert.equal(value.result, "blocked");
  assert.equal(value.consumer_result, "pass");
  assert.equal(value.authority_effect, "none");
  assert.match(value.date, /^\d{4}-\d{2}-\d{2}$/u);
  assert.equal(value.supersedes_historical_qualification.path,
    "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/qualification.json");
  validateBinding(value.supersedes_historical_qualification);
  assert.equal(value.supersedes_previous_qualification.path,
    "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v5-candidate/qualification.json");
  validateBinding(value.supersedes_previous_qualification);
  assert.equal(value.inherited_boundaries.P01.path,
    "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p01-package-boundaries/qualification.v5-candidate.json");
  for (const binding of Object.values(value.inherited_boundaries) as Array<{ path: string; sha256: string }>) validateBinding(binding);
  for (const binding of Object.values(value.bindings) as Array<{ path: string; sha256: string }>) validateBinding(binding);
  assert.deepEqual(Object.keys(value.bindings), ["qualifier","historical_qualifier","qualification_validator","example_materializer","example_guide","package_boundaries","fixture_generator","package_builder"]);
  const expectedBindingPaths: Record<string,string> = {
    qualifier: implementation + "/scripts/qualify-p02-clean-consumers-v6.ts",
    historical_qualifier: implementation + "/scripts/qualify-p02-clean-consumers.ts",
    qualification_validator: implementation + "/test/application-p02-qualification.test.ts",
    example_materializer: implementation + "/scripts/materialize-application-v1-examples.ts",
    example_guide: implementation + "/CLEAN-CONSUMER.md",
    package_boundaries: implementation + "/package-boundaries.json",
    fixture_generator: implementation + "/test/fixtures/application-whole-fixture.ts",
    package_builder: implementation + "/scripts/package-release.mjs",
  };
  for(const [key,binding] of Object.entries(value.bindings) as Array<[string,any]>) assert.equal(binding.path,expectedBindingPaths[key]);
  assert.deepEqual(Object.keys(value.inherited_boundaries), ["P01","O01"]);
  assert.equal(value.inherited_boundaries.O01.path, planRoot + "/O01-COMPLETION.md");
  assert.deepEqual(value.inherited_boundaries.P01, {path:p01Path,sha256:sha256(path.join(repo,p01Path)),result:"blocked",package_shape_result:"scoped-pass"});
  assert.equal(read(p01Path).result,"blocked");
  assert.deepEqual(value.source_envelope,sourceEnvelope(value));
  assert.deepEqual(value.execution_controls,{selected_sources_before_after:"identical",default_archives_before_after:"identical",installed_realpaths_confined:true,checkout_override_environment_removed:true,measurement_stdout_only:true});
  assert.equal(value.archive_content_algorithm,"sha256-json-sorted-path-size-sha256/v1");
  assert.deepEqual(value.archive_observations.map((item:any)=>item.id),["domainspec-cli","core","rust","local-host"]);
  assert.deepEqual(value.archive_observations.slice(1),read(p01Path).archive_observations);
  assert.equal(value.archive_observations[0].entry_count,read(value.bindings.package_boundaries.path).domainspec_cli.expanded_files.length);
  for(const item of value.archive_observations){
    assert.match(item.archive_sha256,/^[a-f0-9]{64}$/u);
    assert.match(item.content_manifest_sha256,/^[a-f0-9]{64}$/u);
    assert.ok(Number.isSafeInteger(item.size_bytes)&&item.size_bytes>0&&item.size_bytes<=64*1024*1024);
  }
  assert.deepEqual(Object.keys(value.reports),languages);
  assert.deepEqual(value.languages.map((item:any)=>[item.language,item.result]),languages.map(language=>[language,"pass"]));

  const reports = languages.map(language => {
    const binding = value.reports[language];
    assert.equal(binding.path, planRoot + "/evidence/p02-clean-consumers/successor-v6-candidate/" + language + ".json");
    validateBinding(binding);
    assert.equal(value.languages.find((item: any) => item.language === language).report_sha256, binding.sha256);
    const report = JSON.parse(fs.readFileSync(path.join(repo, binding.path), "utf8"));
    validateReport(report, language);
    for(const [key,id] of [["domainspec_cli","domainspec-cli"],["core","core"],["rust","rust"],["local-host","local-host"]]){
      const archive = value.archive_observations.find((item:any)=>item.id===id);
      assert.equal(report.package_archives[key].sha256,archive.archive_sha256);
      assert.equal(report.package_archives[key].size_bytes,archive.size_bytes);
      if(key!=="domainspec_cli") assert.equal(report.package_archives[key].file_count,archive.entry_count);
    }
    assert.equal(report.date, value.date);
    return report;
  });
  assert.equal(new Set(reports.map(report => report.application.inspection.files.application_graph.sha256)).size, 1);
  assert.equal(new Set(reports.map(report => report.application.inspection.inbound_route.path)).size, 1);
  assert.deepEqual(value.validation.clean_consumer_reports, { tests: 3, passed: 3, failed: 0, skipped: 0 });
  assert.equal(value.validation.check_lower_build_verify_native_scenario_inspection_cleanup, "pass");
  assert.equal(value.validation.cross_language_application_graph_bytes, "identical");
  assert.equal(value.validation.product_owner_validation, "deferred-to-L4X");
  assert.deepEqual(value.hard_stops,{undocumented_repair:false,weaker_language_path:false,checkout_link_or_fallback:false,owned_temporary_residue:false,publication_or_release_performed:false,product_approval_inferred:false,authority_effect_inferred:false});
  assert.match(value.claim_ceiling,/P02 lifecycle remains blocked by P01 v5\/L3X/u);
  assert.match(value.claim_ceiling, /no candidate freeze/u);
}

test("P02 qualification binds three complete clean installed-consumer reports", () => {
  validateQualification(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("historical P02 v5 qualification remains intact but is not current", () => {
  const historical = JSON.parse(fs.readFileSync(historicalQualificationPath, "utf8"));
  assert.notEqual(sha256(path.join(repo, historical.bindings.package_boundaries.path)), historical.bindings.package_boundaries.sha256);
  assert.throws(() => validateQualification(historical));
});

test("P02 qualification rejects stale bindings, weaker language paths, residue and product inference", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.result = "pass"; },
    (value: any) => { value.consumer_result = "blocked"; },
    (value: any) => { value.inherited_boundaries.P01.result = "pass"; },
    (value: any) => { value.bindings.extra = value.bindings.qualifier; },
    (value: any) => { delete value.bindings.package_builder; },
    (value: any) => { value.bindings.qualification_validator.path = value.bindings.qualifier.path; },
    (value: any) => { value.source_envelope.sha256 = "0".repeat(64); },
    (value: any) => { value.source_envelope.file_count += 1; },
    (value: any) => { value.archive_observations[1].archive_sha256 = "0".repeat(64); },
    (value: any) => { value.archive_observations[2].content_manifest_sha256 = "0".repeat(64); },
    (value: any) => { value.archive_observations[0].entry_count += 1; },
    (value: any) => { value.execution_controls.checkout_override_environment_removed = false; },
    (value: any) => { value.execution_controls.default_archives_before_after = "changed"; },
    (value: any) => { delete value.hard_stops.owned_temporary_residue; },
    (value: any) => { value.languages.pop(); },
    (value: any) => { value.bindings.qualifier.sha256 = "0".repeat(64); },
    (value: any) => { value.supersedes_historical_qualification.sha256 = "0".repeat(64); },
    (value: any) => { value.supersedes_previous_qualification.sha256 = "0".repeat(64); },
    (value: any) => { value.reports.python.sha256 = "0".repeat(64); },
    (value: any) => { value.validation.cross_language_application_graph_bytes = "different"; },
    (value: any) => { value.hard_stops.weaker_language_path = true; },
    (value: any) => { value.hard_stops.owned_temporary_residue = true; },
    (value: any) => { value.validation.product_owner_validation = "pass"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validateQualification(changed));
  }
});

test("P02 reports reject incomplete native paths, checkout use, residue and effect claims", () => {
  const qualification = JSON.parse(fs.readFileSync(qualificationPath,"utf8"));
  for(const language of languages) {
    const original = read(qualification.reports[language].path);
    for(const mutate of [
      (value:any)=>{value.installed_outside_checkout=false;},
      (value:any)=>{value.installed_packages.pop();},
      (value:any)=>{value.application.native.native_compilation="not-run";},
      (value:any)=>{value.application.native.dependency_install="system-modules";},
      (value:any)=>{value.application.native.compiler="";},
      (value:any)=>{value.application.native.scenario.handler_invocations=2;},
      (value:any)=>{value.application.native.scenario.invalid_status=202;},
      (value:any)=>{value.application.verify_after.manifest_sha256="0".repeat(64);},
      (value:any)=>{value.cleanup.native_root_disposed=false;},
      (value:any)=>{value.product_owner_validation="pass";},
      (value:any)=>{value.publication=true;},
    ]) {
      const changed=structuredClone(original);mutate(changed);
      assert.throws(()=>validateReport(changed,language));
    }
  }
});
