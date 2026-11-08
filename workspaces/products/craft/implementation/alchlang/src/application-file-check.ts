import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { loadApplicationFile, assertApplicationFileCurrent, type ApplicationFileOptions } from "./application-file-input.js";
import { compileApplicationExecutable } from "./application-executable.js";
import { compileApplicationWhole } from "./application-whole.js";
import { digest, json } from "./domainspec-profile.js";
import { validateExactFormalSourceRef } from "./formal-claim-lowering.js";

/** Shared source plan for check/build/verify. No provider execution or destination writes. */
export async function prepareApplicationFilePlan(sourcePath: string, options: ApplicationFileOptions = {}) {
  const loaded = await loadApplicationFile(sourcePath, options);
  const root = mkdtempSync(path.join(os.tmpdir(), "alch-application-check-"));
  try {
    for (const [relative, bytes] of Object.entries(loaded.candidate.projectFiles)) {
      validateExactFormalSourceRef({ path: relative, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true }, "$project");
      const target = path.join(root, relative);
      mkdirSync(path.dirname(target), { recursive: true });
      writeFileSync(target, bytes, { flag: "wx" });
    }
    const graph = loaded.compiler.compileProject(root).graph;
    const whole = loaded.observation === undefined ? undefined
      : compileApplicationWhole(loaded.candidate, graph, loaded.observation, loaded.compiler);
    const executable = whole?.executable ?? compileApplicationExecutable(loaded.candidate, graph, loaded.compiler);
    assertApplicationFileCurrent(loaded);
    const sourceSha256 = loaded.inputs[path.basename(loaded.source_path)]!;
    const inputsSha256 = digest(json(loaded.inputs));
    const executableTraceSha256 = digest(json(executable.trace));
    const entryManifestSha256 = loaded.entry_manifest ? digest(json(loaded.entry_manifest)) : null;
    const currentnessReceipt = Object.freeze({
      schema_version: "alchlang.application-currentness-receipt/v1-candidate" as const,
      status: "current" as const,
      source_sha256: sourceSha256,
      inputs_sha256: inputsSha256,
      input_count: Object.keys(loaded.inputs).length,
      domain_manifest_sha256: graph.source_manifest.manifest_sha256,
      executable_trace_sha256: executableTraceSha256,
      entry_manifest_sha256: entryManifestSha256,
      whole_application_plan_sha256: whole?.wholeApplication.plan_sha256 ?? null,
      provider_application_plan_sha256: whole?.application.plan_sha256 ?? null,
      unsupported_residue: Object.freeze([]) as readonly never[],
      authority_effect: "none" as const,
    });
    const report = { status: "valid" as const, profile: "application-v1" as const,
      scope: whole ? "provider-application-artifacts" as const : "executable" as const,
      source_sha256: sourceSha256,
      inputs_sha256: inputsSha256, domain_manifest_sha256: graph.source_manifest.manifest_sha256,
      executable_trace_sha256: executableTraceSha256, nodes: graph.nodes.length,
      generated_artifacts: (whole?.application.artifacts ?? executable.view.artifacts).length,
      ...(loaded.entry_manifest ? { selected_entry: loaded.entry_manifest.selected_entry,
        entry_manifest_sha256: digest(json(loaded.entry_manifest)) } : {}),
      ...(whole ? { runtime_binding_sha256: whole.runtimeBinding.runtime_binding_sha256,
        whole_application_plan_sha256: whole.wholeApplication.plan_sha256,
        provider_application_plan_sha256: whole.application.plan_sha256 } : {}),
      unsupported_residue: currentnessReceipt.unsupported_residue,
      currentness_receipt: currentnessReceipt,
      currentness_receipt_sha256: digest(json(currentnessReceipt)),
      runtime_guarantees_observed: false as const, authority_effect: "none" as const };
    const result={ loaded, report, executable, whole, graph, workspace:root };
    preparedFiles.add(result);return result;
  } catch(error) { rmSync(root, { recursive: true, force: true });throw error; }
}

const preparedFiles=new WeakSet<object>();
export function assertPreparedApplicationFileCurrent(value:Awaited<ReturnType<typeof prepareApplicationFilePlan>>):void {
 if(!preparedFiles.has(value))throw Error('APPLICATION_PLAN_UNREGISTERED');assertApplicationFileCurrent(value.loaded);
}
export function disposePreparedApplicationFile(value:Awaited<ReturnType<typeof prepareApplicationFilePlan>>):void {
 if(!preparedFiles.delete(value))throw Error('APPLICATION_PLAN_UNREGISTERED');rmSync(value.workspace,{recursive:true,force:true});
}
export async function planApplicationFile(sourcePath:string,options:ApplicationFileOptions={}){
 const prepared=await prepareApplicationFilePlan(sourcePath,options);
 try{return {loaded:prepared.loaded,report:prepared.report,executable:prepared.executable,whole:prepared.whole};}
 finally{disposePreparedApplicationFile(prepared);}
}

/** Public source check: compile in owned scratch space; do not execute providers. */
export async function checkApplicationFile(sourcePath: string, options: ApplicationFileOptions = {}) {
  return (await planApplicationFile(sourcePath, options)).report;
}
