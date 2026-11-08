import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";
import { publicApiApplication } from "../fixtures/public-api-application.ts";
import { repositoryToolchain, typeScriptToolchain } from "../helpers/local-toolchain.ts";

const cli = path.resolve(import.meta.dirname, "../..");
function run(command: string, args: string[], cwd: string, env = process.env) {
  const result = spawnSync(command, args, { cwd, env, encoding: "utf8", timeout: 120000 });
  assert.equal(result.status, 0, `${result.error?.message ?? ""}\n${result.stdout}\n${result.stderr}`);
}

test("whole application preserves and executes public API mappings in all three language profiles", t => {
  const f = publicApiApplication(t, true), hashes: string[] = [];
  for (const language of ["typescript", "python", "rust"] as const) {
    const plan = planWholeApplicationV1(f.root, f.selection(language), f.source);
    hashes.push(plan.binding_sha256);
    const root = path.join(f.temporary, language);
    for (const artifact of plan.artifacts) {
      const target = path.join(root, artifact.relative_path); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, artifact.content);
    }
    if (language === "typescript") {
      const money = plan.artifacts.find(a => a.relative_path.includes('/mappings/') && /public[-_]money\.ts$/.test(a.relative_path))!;
      assert.ok(money, 'Value Object projection module');
      run(process.execPath, [typeScriptToolchain().compiler, "-p", "tsconfig.json", "--noEmit"], root);
      run(process.execPath, [path.join(cli, "node_modules/tsx/dist/cli.mjs"), "--eval", `import {RUNTIME_MAPPING_INVOCATIONS as mappings} from './src/integrations/runtime-bindings.ts';
        import {mappingPublicMoney as projectMoney} from './${money.relative_path}';
        const money=projectMoney({payload:{id:'1',net:'0',fee:'3'}});
        if(money.quantity!==0n||money.note!=='projection')throw Error('Value Object projection');
        const payload={id:'18446744073709551615',net:'7',fee:'3'};
        for(const id of ['api-mapping:authorize-request','api-mapping:authorize-response']) {
          const result=mappings[id]({payload}); if(result.id!==18446744073709551615n||result.net!==7n||result.fee!==3n)throw Error('public projection');
          let rejected=false;try{mappings[id]({payload:{...payload,id:'-1'}})}catch{rejected=true}if(!rejected)throw Error('invalid UInt64');
        }`], root);
    } else if (language === "python") {
      const money = plan.artifacts.find(a => a.relative_path.includes('/mappings/') && !a.relative_path.includes('/_providers/') && /public[-_]money\.py$/.test(a.relative_path))!;
      assert.ok(money, 'Value Object projection module');
      run("python3", ["-c", `from commerce_corpus.integrations.domain_bindings import ApplicationInput
from ${money.relative_path.slice(4,-3).replaceAll('/', '.')} import mapping_public_money as project_money
money = project_money({'payload': {'id': 1, 'net': 0, 'fee': 3}})
assert money['quantity'] == 0 and money['note'] == 'projection'
from commerce_corpus.integrations.runtime_bindings import RUNTIME_MAPPING_INVOCATIONS
for key in ['api-mapping:authorize-request','api-mapping:authorize-response']:
    result = RUNTIME_MAPPING_INVOCATIONS[key]({'payload': {'id': 18446744073709551615, 'net': 7, 'fee': 3}})
    assert result['id'] == 18446744073709551615 and result['net'] == 7 and result['fee'] == 3
    try:
        RUNTIME_MAPPING_INVOCATIONS[key]({'payload': {'id': -1, 'net': 7, 'fee': 3}})
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError('invalid UInt64 accepted')
`], root, { ...process.env, PYTHONPATH: path.join(root, "src") });
    } else {
      const api = plan.artifacts.find(a => a.relative_path.includes("/interfaces/") && a.content.includes('DOMAINSPEC_SELECTOR: &str = "commerce:api"'))!;
      assert.ok(api);
      const module = "crate::" + api.relative_path.slice(4, -3).replaceAll("/", "::");
      const money = plan.artifacts.find(a => a.relative_path.includes('/mappings/') && a.content.includes('DOMAINSPEC_SELECTOR: &str = "commerce:public-money"'))!;
      assert.ok(money, 'Value Object projection module');
      const moneyModule = 'crate::' + money.relative_path.slice(4,-3).replaceAll('/', '::');
      fs.appendFileSync(path.join(root, "src/lib.rs"), `\n#[cfg(test)] mod public_api_test { #[test] fn projection() {
        let zero=${module}::Response {id:1,net:0,fee:3};
        let money=${moneyModule}::public_money(&zero);
        assert_eq!(money.quantity,0);assert_eq!(money.note,Some("projection".to_string()));
        let payload=${module}::Response {id:u64::MAX,net:7,fee:3};
        let request=crate::integrations::runtime_bindings::invoke_api_mapping_authorize_request(&payload);
        let response=crate::integrations::runtime_bindings::invoke_api_mapping_authorize_response(&request);
        assert_eq!(response,payload);
      } }\n`);
      run(repositoryToolchain(), ["cargo", "test", "--offline", "--lib"], root, { ...process.env, CARGO_TARGET_DIR: path.join(root, "target") });
    }
  }
  assert.equal(new Set(hashes).size, 1);
});
