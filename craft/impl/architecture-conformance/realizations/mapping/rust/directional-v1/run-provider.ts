import {readFileSync} from "node:fs";import {mappingRustV1Provider} from "../../../../factory/registry/providers/mapping-rust-v1.js";
const input=readFileSync(0,"utf8");const result=await mappingRustV1Provider.execute({raw_inputs:{mapping_case:input}} as never);process.stdout.write(`${JSON.stringify(result)}\n`);
