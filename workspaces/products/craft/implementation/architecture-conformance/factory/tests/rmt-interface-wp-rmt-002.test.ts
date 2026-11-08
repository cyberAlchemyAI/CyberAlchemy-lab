import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {runInterfaceParity} from "../../acceptance/interface/wp-rmt-002/replay/run-interface-parity.js";

describe("WP-RMT-002 Interface factory candidate fixture",()=>{
  it("executes exactly three direct unregistered providers",async()=>{
    const fixture=JSON.parse(readFileSync("projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-interface-wp-rmt-002.request.json","utf8"));
    expect(fixture.provider_ids).toEqual(["interface-typescript-v1","interface-python-v1","interface-rust-v1"]);
    expect(fixture.provider_registration_status).toBe("unregistered");
    const result=await runInterfaceParity();
    expect(result).toMatchObject({result:"pass",provider_ids:fixture.provider_ids,parity_receipt:{sha256:"a1ffa95e8424dbd715fa01ce8b2b8285df70f97c182ccdc0148a8130496e4e25"}});
  },120_000);
});
