import {readFileSync} from "node:fs";
import {stateMachineRustV1Provider} from "../../../../factory/registry/providers/state-machine-rust-v1.js";
const input=readFileSync(0,"utf8"),result=await stateMachineRustV1Provider.execute({raw_inputs:{state_machine_case:input}} as never);
process.stdout.write(JSON.stringify(result)+"\n");
