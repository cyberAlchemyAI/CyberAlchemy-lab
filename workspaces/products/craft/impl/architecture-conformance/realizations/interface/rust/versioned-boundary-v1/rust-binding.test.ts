import {describe,expect,it} from "vitest";
import {createHash} from "node:crypto";
import {existsSync,readFileSync,readdirSync,rmdirSync} from "node:fs";
import {spawn} from "node:child_process";
import {join} from "node:path";
import {interfaceRustV1Provider} from "../../../../factory/registry/providers/interface-rust-v1.js";
import {makeSettlementInterfaceCase} from "../../../../targets/typescript/interface-v1.js";

describe("Interface Rust realization binding",()=>{
  const root="projects/domainspec-v2/development/remaining-meta-types/runs/interface/cargo-target";
  const removeEmptyOwnedParent=()=>{
    expect(readdirSync(root)).toEqual([]);
    rmdirSync(root);
    expect(existsSync(root)).toBe(false);
  };
  it("hash-closes target and provider bytes",()=>{
    const binding=JSON.parse(readFileSync("projects/domainspec-v2/impl/architecture-conformance/realizations/interface/rust/versioned-boundary-v1/rust-binding.json","utf8"));
    for(const ref of [binding.target,binding.provider,binding.w3_observer,binding.interface_extension]){
      const bytes=readFileSync(ref.path);
      expect(createHash("sha256").update(bytes).digest("hex")).toBe(ref.sha256);
      if(ref.size_bytes!==undefined) expect(bytes.length).toBe(ref.size_bytes);
    }
    expect(binding.registered).toBe(false);
  });
  it("executes locked offline native controls and keeps evidence separate",async()=>{
    expect(existsSync(root),"pre-existing transient root must be preserved, not deleted by this proof").toBe(false);
    const result=await interfaceRustV1Provider.execute({raw_inputs:{interface_case:JSON.stringify(makeSettlementInterfaceCase())}} as never);
    expect(result).toMatchObject({result:"pass",provider_id:"interface-rust-v1",authority_effect:"none"});
    expect(result.semantic_output).toMatchObject({portable:{meta_type:"Interface",contract_id:"SettlementPort"},native_evidence:{language:"rust"}});
    removeEmptyOwnedParent();
  },120_000);
  it("isolates concurrent executions and leaves zero owned Cargo residue",async()=>{
    expect(existsSync(root),"pre-existing transient root must be preserved, not deleted by this proof").toBe(false);
    const runner="projects/domainspec-v2/impl/architecture-conformance/realizations/interface/rust/versioned-boundary-v1/run-provider.ts";
    const tsx="projects/domainspec-v2/impl/node_modules/.bin/tsx";
    const home=process.env.HOME;
    expect(home).toBeTruthy();
    const run=()=>new Promise<{status:number|null;stdout:string;stderr:string}>((resolve,reject)=>{
      const child=spawn(tsx,[runner],{cwd:process.cwd(),env:{
        PATH:process.env.PATH??"",HOME:home!,CARGO_HOME:process.env.CARGO_HOME??join(home!,".cargo"),
        RUSTUP_HOME:process.env.RUSTUP_HOME??join(home!,".rustup"),
      }});
      let stdout=""; let stderr="";
      child.stdout.setEncoding("utf8").on("data",chunk=>{stdout+=chunk;});
      child.stderr.setEncoding("utf8").on("data",chunk=>{stderr+=chunk;});
      child.on("error",reject);
      child.on("close",status=>resolve({status,stdout,stderr}));
      child.stdin.end(JSON.stringify(makeSettlementInterfaceCase()));
    });
    const attempts=await Promise.all([run(),run()]);
    for(const attempt of attempts){expect(attempt.status,attempt.stderr).toBe(0);expect(JSON.parse(attempt.stdout).result).toBe("pass");}
    removeEmptyOwnedParent();
  },120_000);
});
