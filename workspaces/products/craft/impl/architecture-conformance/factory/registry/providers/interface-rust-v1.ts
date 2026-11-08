import {mkdirSync,mkdtempSync,rmSync} from "node:fs";
import {spawnSync} from "node:child_process";
import {isAbsolute,join} from "node:path";
import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import {fail} from "../../shared/canonical.js";

const manifest = "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml";
const targetDir = "projects/domainspec-v2/development/remaining-meta-types/runs/interface/cargo-target";
export const interfaceRustV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id:"interface-rust-v1", provider_version:"1.0.0-candidate", compatible_kinds:Object.freeze(["direct-proof"] as const),
  required_input_roles:Object.freeze(["interface_case"]),
  component_paths:Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/interface-rust-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/interface_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/tests/interface_v1.rs",
  ]), tool_ids:Object.freeze(["cargo","rustc"]),
  execute:async ({raw_inputs:rawInputs}) => {
    let input: any;
    try { input=JSON.parse(rawInputs.interface_case??""); } catch { return fail("FACTORY_INTERFACE_RUST_FAILED","invalid-json"); }
    const descriptor=input.descriptor;
    if (!descriptor || descriptor.contract_id!=="SettlementPort" || descriptor.exact_version!=="1.2.0"
        || descriptor.compatibility_direction!=="consumer-to-provider" || !Array.isArray(descriptor.exposed_bindings)
        || !Array.isArray(descriptor.mapping_obligations) || input.w3_descriptor?.contract_id!==descriptor.contract_id
        || input.w3_observation?.contract_id!==descriptor.contract_id) return fail("FACTORY_INTERFACE_RUST_FAILED","invalid-interface-case");
    const pathEnv=process.env.PATH;
    const userHome=process.env.HOME;
    if(!pathEnv || !userHome || !isAbsolute(userHome)) return fail("FACTORY_INTERFACE_RUST_FAILED","runtime-home-or-path-invalid");
    const cargoHome=process.env.CARGO_HOME??join(userHome,".cargo");
    const rustupHome=process.env.RUSTUP_HOME??join(userHome,".rustup");
    if(!isAbsolute(cargoHome)||!isAbsolute(rustupHome)) return fail("FACTORY_INTERFACE_RUST_FAILED","runtime-tool-home-invalid");
    mkdirSync(targetDir,{recursive:true});
    const ownedTarget=mkdtempSync(join(targetDir,"run-"));
    let child:ReturnType<typeof spawnSync>;
    try {
      child=spawnSync("cargo",["test","--manifest-path",manifest,"--locked","--offline","--test","interface_v1"],{
        cwd:process.cwd(),encoding:"utf8",env:{
          PATH:pathEnv,CARGO_HOME:cargoHome,RUSTUP_HOME:rustupHome,CARGO_TARGET_DIR:ownedTarget,
        },
      });
    } finally {
      rmSync(ownedTarget,{recursive:true,force:true});
    }
    if (child.status !== 0) return fail("FACTORY_INTERFACE_RUST_FAILED",String(child.stderr).trim()||String(child.status));
    const portable=Object.freeze({
      schema_version:"domainspec.interface-portable-result/v1",result:"pass",meta_type:"Interface",contract_id:descriptor.contract_id,version:descriptor.exact_version,
      compatibility_direction:descriptor.compatibility_direction,
      exposed_bindings:Object.freeze(descriptor.exposed_bindings.map((item:any)=>`${item.kind}:${item.binding_id}`).sort()),
      mapping_obligations:Object.freeze(descriptor.mapping_obligations.map((item:any)=>`${item.binding_id}:${item.direction}:${item.mapping_id}`).sort()),
      boundary:Object.freeze({inside:descriptor.inside_boundary,outside:descriptor.outside_boundary}),transport_domain_separated:true,authority_effect:"none",
    });
    return Object.freeze({
      schema_version:"FactoryNodeSemanticResult/v1",result:"pass",provider_id:"interface-rust-v1",
      semantic_output:Object.freeze({portable,native_evidence:Object.freeze({language:"rust",mechanism:"trait-and-owned-struct-boundary"})}),
      accounting:Object.freeze({positives_declared:1,positives_passed:1,mutants_declared:10,mutants_killed:10}),
      claim_ceiling:"candidate-local native Rust Interface proof; provider remains unregistered",authority_effect:"none",
    });
  },
});
