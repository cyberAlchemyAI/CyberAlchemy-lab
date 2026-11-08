import {execFile} from "node:child_process";
import {existsSync,readdirSync,rmdirSync} from "node:fs";
import {join} from "node:path";
import {describe,expect,it} from "vitest";

const runner="projects/domainspec-v2/impl/architecture-conformance/acceptance/interface/wp-rmt-002/replay/run-interface-parity.ts";
const tsx="projects/domainspec-v2/impl/node_modules/.bin/tsx";
const cargoRoot="projects/domainspec-v2/development/remaining-meta-types/runs/interface/cargo-target";
const childEnv=()=>{
  const home=process.env.HOME;
  if(!home) throw new Error("RMT_IFACE_REPLAY_HOME_MISSING");
  return {PATH:process.env.PATH??"",HOME:home,CARGO_HOME:process.env.CARGO_HOME??join(home,".cargo"),RUSTUP_HOME:process.env.RUSTUP_HOME??join(home,".rustup")};
};
type Attempt={status:number;stdout:string;stderr:string;pid:number};
const execute=(mode:string):Promise<Attempt>=>new Promise((resolve)=>{
  const child=execFile(tsx,[runner,mode],{cwd:process.cwd(),env:childEnv(),maxBuffer:1024*1024},(error,stdout,stderr)=>{
    resolve({status:typeof (error as NodeJS.ErrnoException|null)?.code==="number"?(error as unknown as {code:number}).code:0,stdout,stderr,pid:child.pid!});
  });
});
const decode=(stdout:string)=>{
  const lines=stdout.split(/\r?\n/u).filter((line)=>line.length>0);
  if(lines.length!==1) throw new Error("RMT_IFACE_REPLAY_RECEIPT_CARDINALITY");
  return JSON.parse(lines[0]!);
};

describe("WP-RMT-002 Interface fresh-process replay",()=>{
  it("replays all three providers in two real processes and cleans exact owned residue",async()=>{
    expect(existsSync(cargoRoot),"pre-existing Cargo root is preserved and blocks this isolated proof").toBe(false);
    const attempts=await Promise.all([execute("--emit"),execute("--emit")]);
    for(const attempt of attempts) expect(attempt.status,attempt.stderr).toBe(0);
    expect(attempts[0]!.pid).not.toBe(attempts[1]!.pid);
    const receipts=attempts.map(({stdout})=>decode(stdout));
    expect(receipts[1]).toEqual(receipts[0]);
    expect(receipts[0]).toMatchObject({
      result:"pass",fresh_process_count_declared:2,provider_ids:["interface-typescript-v1","interface-python-v1","interface-rust-v1"],
      parity_receipt:{sha256:"a1ffa95e8424dbd715fa01ce8b2b8285df70f97c182ccdc0148a8130496e4e25"},authority_effect:"none",
    });
    expect(attempts[0]!.stdout).not.toContain(String(attempts[0]!.pid));
    expect(existsSync(cargoRoot)).toBe(true);
    expect(readdirSync(cargoRoot)).toEqual([]);
    rmdirSync(cargoRoot);
    expect(existsSync(cargoRoot)).toBe(false);
  },120_000);

  it("preserves nonzero failure and rejects malformed multi-receipt output",async()=>{
    const failed=await execute("--fail");
    expect(failed.status).toBe(23);
    expect(failed.stderr).toContain("RMT_IFACE_REPLAY_PROBE_FAILURE");
    const malformed=await execute("--malformed-output");
    expect(malformed.status).toBe(0);
    expect(()=>decode(malformed.stdout)).toThrowError("RMT_IFACE_REPLAY_RECEIPT_CARDINALITY");
    expect(existsSync(cargoRoot)).toBe(false);
  });
});
