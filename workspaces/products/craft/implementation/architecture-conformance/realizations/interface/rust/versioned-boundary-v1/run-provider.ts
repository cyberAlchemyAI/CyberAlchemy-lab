import {readFileSync} from "node:fs";
import {interfaceRustV1Provider} from "../../../../factory/registry/providers/interface-rust-v1.js";

const input=readFileSync(0,"utf8");
const result=await interfaceRustV1Provider.execute({raw_inputs:{interface_case:input}} as never);
process.stdout.write(`${JSON.stringify(result)}\n`);
