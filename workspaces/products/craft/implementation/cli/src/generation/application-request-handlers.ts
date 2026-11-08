import { canonicalJson } from "../input/source-manifest.js";
import type { CompiledOperationRequestContractV1, CompiledRuntimeMappingBindingV1 } from "../system-integration/application-graph-v1.js";
import { outputImport } from "./output-layout.js";

export interface ApplicationRequestOperationModule {
  readonly operation_ref: string;
  readonly relative_path: string;
  readonly callable: string;
}

/** Called only after whole-application graph, request and native module checks. */
export function renderApplicationRequestHandlers(
  relativePath: string,
  requests: readonly CompiledOperationRequestContractV1[],
  bindings: readonly CompiledRuntimeMappingBindingV1[],
  modules: readonly ApplicationRequestOperationModule[],
): string {
  const fail = (message: string): never => { throw new TypeError(`DS_APPLICATION_REQUEST_HANDLER:${message}`); };
  const operations = [...modules].sort((a, b) => a.operation_ref < b.operation_ref ? -1 : a.operation_ref > b.operation_ref ? 1 : 0);
  const imports = operations.map((row, i) => `import {${row.callable} as operation_${i}} from ${JSON.stringify(outputImport(relativePath, row.relative_path).replace(/\.ts$/, ".js"))};`);
  imports.push('import {RUNTIME_MAPPING_INVOCATIONS} from "./runtime-bindings.js";');
  let usesPath = false;
  const descriptors: unknown[] = [];
  const handlers = requests.flatMap(request => request.bindings.map(connection => ({ request, connection })))
    .sort((a, b) => a.connection.mapping_binding_ref < b.connection.mapping_binding_ref ? -1 : a.connection.mapping_binding_ref > b.connection.mapping_binding_ref ? 1 : 0);
  if (new Set(handlers.map(row => row.connection.mapping_binding_ref)).size !== handlers.length) fail("duplicate Mapping binding handler");
  const rows = handlers.map(({ request, connection }) => {
    const i = operations.findIndex(row => row.operation_ref === request.operation_ref);
    if (i < 0) return fail("missing exact Operation module");
    const operation = `operation_${i}`, binding = bindings.find(row => row.binding_id === connection.mapping_binding_ref);
    if (!binding || binding.target_ref !== request.request_ref || binding.source_ref !== connection.source_ref
      || !["protocol-to-application", "message-to-application"].includes(binding.direction)) return fail("request Mapping identity differs");
    const mapping = `RUNTIME_MAPPING_INVOCATIONS[${JSON.stringify(binding.binding_id)}]`;
    const fromBody = (parts: readonly string[]) => {
      if (!parts.length) return "body";
      usesPath = true; return `readPath(body,${JSON.stringify(parts)})`;
    };
    const mappingArguments = binding.inputs.map(input => {
      if (!["protocol-body", "message-body", "direct-value"].includes(input.source.kind) || input.source.reference !== connection.source_ref) return fail("unsupported request source kind");
      return `[${JSON.stringify(input.parameter)}]:${fromBody(input.source.path)} as Parameters<typeof ${mapping}>[0][${JSON.stringify(input.parameter)}]`;
    });
    const parameters = connection.parameters.map(parameter => {
      const value = parameter.source.kind === "mapping-result" ? "mapped" : `${fromBody(parameter.source.path)} as Parameters<typeof ${operation}>[0][${JSON.stringify(parameter.parameter)}]`;
      if (parameter.source.kind === "mapping-result" && parameter.source.path.length) return fail("nested Mapping-result projection is unsupported");
      return `[${JSON.stringify(parameter.parameter)}]:${value}`;
    });
    const needsBody = binding.inputs.length > 0 || connection.parameters.some(parameter => parameter.source.kind === "source-body");
    const keepsMapping = connection.parameters.some(parameter => parameter.source.kind === "mapping-result");
    descriptors.push({ mapping_binding_ref: binding.binding_id, mapping_ref: binding.mapping_ref, operation_ref: request.operation_ref,
      request_ref: request.request_ref, source_ref: connection.source_ref, operation_module: operations[i]!.relative_path });
    return `[${JSON.stringify(binding.binding_id)}]:async (${needsBody ? "body" : "_body"}:unknown,dependencies:Parameters<typeof ${operation}>[1]):Promise<Awaited<ReturnType<typeof ${operation}>>>=>{
  ${keepsMapping ? "const mapped=" : ""}${mapping}({${mappingArguments.join(",")}});
  const request:Parameters<typeof ${operation}>[0]=Object.freeze({${parameters.join(",")}});
  return ${operation}(request,dependencies);
}`;
  });
  const reader = usesPath ? `function readPath(value:unknown,parts:readonly string[]):unknown {
  let current=value;
  for(const part of parts){
    if(current===null||typeof current!=="object"||Array.isArray(current))throw new TypeError("APPLICATION_REQUEST_PATH");
    const field=Object.getOwnPropertyDescriptor(current,part);
    if(!field||!("value" in field))throw new TypeError("APPLICATION_REQUEST_PATH");
    current=field.value;
  }
  return current;
}\n` : "";
  return `${imports.join("\n")}\n${reader}export const APPLICATION_REQUEST_HANDLERS=Object.freeze({${rows.join(",\n")}});\nexport type ApplicationRequestHandlerRef=keyof typeof APPLICATION_REQUEST_HANDLERS;\nexport const APPLICATION_REQUEST_HANDLER_BINDINGS=${canonicalJson(descriptors)} as const;\n`;
}

import {assertDirectBusinessSourceGraphV2Current,type CheckedDirectBusinessSourceGraphV2} from '../formalization/direct-condition-binding.js';
/** U05 pure invocation: no transaction dependency, async evaluator or host hook.
 * Open Questions: G01/U08 actual selected generated/native handler join. */
export function renderDirectApplicationInvocationV2(source:CheckedDirectBusinessSourceGraphV2):string {
 assertDirectBusinessSourceGraphV2Current(source);
 return `import {runOperation,fromU0Submission,toU0Submission} from './operation.mjs';
export {U0InputContractError} from './operation.mjs';
export const U0_ABI='craft.u0.pure-submission/v1-candidate' as const;
export const U0_SOURCE_CHECK=${JSON.stringify(source.check_sha256)};
export type Submission=Readonly<{id:bigint;verified:boolean}>;
export type Outcome=Readonly<{kind:'completed';value:Submission}>|Readonly<{kind:'rejected';code:${JSON.stringify(source.operation.rejection_code)}}>;
export function invoke(input:Submission):Outcome{
 const result=runOperation(fromU0Submission(input));
 if(result.kind==='rejected')return result;
 return Object.freeze({kind:'completed',value:toU0Submission(result.value)});
}
`;
}
