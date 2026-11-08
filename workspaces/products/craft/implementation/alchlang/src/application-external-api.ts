import { parseDomainSource } from "./parser.js";
import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { ApplicationType } from "./application-source.js";
import type { DomainSpecCompiler } from "./domainspec-cli.js";

type Obj = Record<string, any>;
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
function exact(value: unknown, keys: string[], at: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value) || json(Object.keys(value).sort()) !== json([...keys].sort())) return fail("APPLICATION_API_BINDING", at, "unexpected or missing member");
  return value as Obj;
}
function coverage(values: string[], expected: string[], at: string): void {
  if (new Set(values).size !== values.length || json([...values].sort()) !== json([...expected].sort())) fail("APPLICATION_API_COVERAGE", at, "exact authored binding coverage required");
}

/** Formation only: route intent and named payload identities are not an HTTP runtime. */
export function lowerApplicationExternalApi(source: string, input: unknown, compiler: Pick<DomainSpecCompiler, "compileExternalApiComposition">) {
  const root = exact(input, ["schema_version", "source_sha256", "composition", "declarations", "external_apis", "contract_refs"], "$external-api");
  if (root.schema_version !== "alchlang.application-external-api/v1-candidate" || root.source_sha256 !== digest(source)) fail("APPLICATION_API_SOURCE", "$external-api", "source bytes or binding version differ");
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_API_PROFILE", "$", "explicit application profile required");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const declarations = model.integrations.filter(d => d.kind === "inbound-endpoint" || d.kind === "outbound-call");
  if (!declarations.length) fail("APPLICATION_API_COVERAGE", "$", "no API declaration");
  const choices = exact(root.declarations, declarations.map(d => d.id), "$declarations");
  const outbound = declarations.filter(d => d.kind === "outbound-call");
  const apis = exact(root.external_apis, [...new Set(outbound.map(d => d.external_api.ref))], "$external_apis");
  const contractNames = [...new Set(outbound.flatMap(d => [d.request.ref, d.response.ref]))];
  const contracts = exact(root.contract_refs, contractNames, "$contract_refs");
  for (const [name, ref] of Object.entries(contracts)) if (typeof ref !== "string" || !ref.trim()) fail("APPLICATION_API_TYPE", `$contract_refs/${name}`, "explicit backend payload reference required");
  if (new Set(Object.values(contracts)).size !== contractNames.length) fail("APPLICATION_API_IDENTITY", "$contract_refs", "distinct authored payloads cannot collapse into one backend identity");
  const byId = new Map(model.declarations.map(d => [d.id, d]));
  const selector = (id: string) => `${symbol(model.domain_id)}:${symbol(id)}`;
  const selected = new Map(model.declarations.map(d => [selector(d.id), d]));
  if (selected.size !== model.declarations.length) fail("APPLICATION_SYMBOL_COLLISION", "$", "domain identities collide");
  // Report authored contract/operation/failure mistakes at their source before
  // the backend's broader composition validator reports an unresolved dependency.
  const raw = root.composition as Obj;
  for (const d of outbound) {
    const at = `$line:${d.source_line}`;
    if (byId.get(d.operation.ref)?.kind !== "operation") fail("APPLICATION_API_OPERATION", at, "outbound path must select a declared Operation");
    const choice = choices[d.id] as Obj;
    const binding = raw?.external_api_bindings?.find?.((item: Obj) => item.binding_id === choice?.binding_ref);
    if (!binding) fail("APPLICATION_API_REFERENCE", at, "outbound path must select a declared API binding");
    const contract = raw?.external_api_contracts?.find?.((item: Obj) => item.contract_id === binding.external_api_contract_ref);
    if (!contract) fail("APPLICATION_API_CONTRACT", at, "external API contract must be declared");
    if (!contract.operations?.some?.((item: Obj) => `${contract.contract_id}#${item.operation_id}` === binding.contract_operation_ref)) {
      fail("APPLICATION_API_OPERATION", at, "external API contract operation must be declared");
    }
    if (!raw?.api_failure_mappings?.some?.((item: Obj) => item.mapping_id === binding.failure_mapping_ref)) {
      fail("APPLICATION_API_FAILURE", at, "external API failure mapping must be declared");
    }
  }
  const composition = compiler.compileExternalApiComposition(root.composition);
  for (const name of Object.keys(apis)) if (byId.has(name)) fail("APPLICATION_API_IDENTITY", "$external_apis", "API alias cannot shadow a domain declaration");
  coverage(Object.values(apis).map(value => exact(value, ["contract_ref", "interface_ref"], "$external_apis").contract_ref), composition.external_api_contracts.map((c: Obj) => c.contract_id), "$external_apis");
  const payloadType = (name: string, at: string): ApplicationType => {
    const parts = name.split(".");
    const owner = byId.get(parts[0]!);
    if (parts.length === 2 && owner?.kind === "interface" && owner.contracts.some(c => c.id === parts[1])) return { kind: "public-contract", interface: owner.id, contract: parts[1]! };
    if (parts.length === 1 && (owner?.kind === "entity" || owner?.kind === "value-object")) return { kind: "declaration", ref: owner.id };
    return fail("APPLICATION_API_TYPE", at, "request/response must resolve to a declared value or qualified Interface contract");
  };
  const inboundIds: string[] = [], outboundIds: string[] = [], mappingIds: string[] = [];
  const decisionJoins: { source_id: string; binding_ref: string; contract_operation_ref: string; operation_ref: string;
    response_mapper_ref: string; decision_mapper_ref: string; response_type: ApplicationType; decision_input_type: ApplicationType }[] = [];
  const routes: { source_id: string; binding_ref: string; protocol_operation_ref: string; method: string; path: string }[] = [];
  const references = declarations.map(d => {
    const at = `$line:${d.source_line}`, choice = exact(choices[d.id],
      d.kind === "outbound-call" && d.decision_mapping ? ["binding_ref", "decision_mapper_ref"] : ["binding_ref"], at);
    const binding = (d.kind === "inbound-endpoint" ? composition.inbound_endpoint_bindings : composition.external_api_bindings).find((b: Obj) => b.binding_id === choice.binding_ref);
    if (!binding) return fail("APPLICATION_API_REFERENCE", at, "missing API binding of authored kind");
    const operation = byId.get(d.operation.ref);
    if (operation?.kind !== "operation") return fail("APPLICATION_API_OPERATION", at, "path must select a declared Operation");
    const requestType = payloadType(d.request.ref, at), responseType = payloadType(d.response.ref, at);
    const request = selected.get(binding.request_mapper_ref), response = selected.get(binding.response_mapper_ref);
    if (request?.kind !== "mapping" || response?.kind !== "mapping") return fail("APPLICATION_API_MAPPING", at, "both explicit mappers must resolve to declared Mapping nodes");
    const requestMapping = composition.api_mappings.find((m: Obj) => m.mapper_ref === binding.request_mapper_ref)!;
    const responseMapping = composition.api_mappings.find((m: Obj) => m.mapper_ref === binding.response_mapper_ref)!;
    if (requestMapping.total !== request.total || responseMapping.total !== response.total) fail("APPLICATION_API_MAPPING", at, "mapping totality differs");
    if (!request.inputs.some(p => json(p.type) === json(requestType)) || json(payloadType(response.target, at)) !== json(responseType)) fail("APPLICATION_API_PAYLOAD", at, "authored request/response disagree with the explicit mapper boundary types");
    const kernel = composition.integration_kernel.integration_bindings.find((b: Obj) => b.binding_id === binding.integration_binding_ref)!;
    if (kernel.provider_realization_ref !== binding.provider_realization_ref) fail("APPLICATION_API_KERNEL", at, "kernel and API provider realization differ");
    if (binding.authentication_binding_ref !== null && !composition.authentication_bindings.some((a: Obj) => a.binding_id === binding.authentication_binding_ref && a.integration_boundary_ref === binding.binding_id)) fail("APPLICATION_API_AUTH", at, "explicit authentication reference must resolve at this boundary");
    mappingIds.push(requestMapping.mapping_id, responseMapping.mapping_id);
    if (d.kind === "inbound-endpoint") {
      if (binding.operation_ref !== selector(operation.id) || kernel.logical_boundary_ref !== selector(operation.id)) fail("APPLICATION_API_OPERATION", at, "inbound path selects a different Operation");
      if (kernel.failure_mapping_ref !== binding.failure_mapping_ref) fail("APPLICATION_API_KERNEL", at, "inbound failure mapping differs from kernel");
      if (json(payloadType(request.target, at)) !== json(operation.input) || !response.inputs.some(p => json(p.type) === json(operation.output))) fail("APPLICATION_API_PAYLOAD", at, "request/result mapping does not match the Operation types");
      coverage(requestMapping.input_paths.map((p: Obj) => p.parameter), request.inputs.map(p => symbol(p.name, "_")), at);
      inboundIds.push(binding.binding_id);
      routes.push({ source_id: d.id, binding_ref: binding.binding_id, protocol_operation_ref: binding.protocol_operation_ref, method: d.protocol.method, path: d.protocol.path });
    } else {
      const api = exact(apis[d.external_api.ref], ["contract_ref", "interface_ref"], at);
      const boundary = byId.get(api.interface_ref);
      if (boundary?.kind !== "interface") fail("APPLICATION_API_INTERFACE", at, "external API alias must explicitly select a declared Interface boundary");
      const contract = composition.external_api_contracts.find((c: Obj) => c.contract_id === api.contract_ref);
      const member = contract?.operations.find((m: Obj) => `${contract.contract_id}#${m.operation_id}` === binding.contract_operation_ref);
      if (!contract || binding.external_api_contract_ref !== contract.contract_id || !member || !contract.consumer_role_refs.includes(selector(operation.id))) fail("APPLICATION_API_OPERATION", at, "outbound API contract or consumer differs");
      if (kernel.logical_boundary_ref !== selector(boundary!.id) || kernel.contract_ref !== contract.contract_id) fail("APPLICATION_API_KERNEL", at, "domain Interface boundary and external contract must both match explicitly");
      if (member.request_type_ref !== contracts[d.request.ref] || member.result_type_ref !== contracts[d.response.ref]) fail("APPLICATION_API_PAYLOAD", at, "outbound named payload references differ");
      const failure = composition.api_failure_mappings.find((m: Obj) => m.mapping_id === binding.failure_mapping_ref)!;
      if (kernel.failure_mapping_ref !== failure.kernel_failure_mapping_ref) fail("APPLICATION_API_KERNEL", at, "outbound failure translation differs from kernel");
      if (d.decision_mapping) {
        const mapperRef = selector(d.decision_mapping.ref);
        const decision = selected.get(mapperRef);
        if (choice.decision_mapper_ref !== mapperRef) {
          fail("APPLICATION_API_DECISION_MAPPING", `$line:${d.decision_mapping.source_line}`, "decision Mapping binding differs from authored reference");
        }
        const decisionMapping = decision?.kind === "mapping" ? decision : fail("APPLICATION_API_DECISION_MAPPING",
          `$line:${d.decision_mapping.source_line}`, "declared decision Mapping must resolve by exact identity");
        if (decisionMapping.inputs.length !== 1 || json(decisionMapping.inputs[0]!.type) !== json(responseType)
          || json(payloadType(decisionMapping.target, at)) !== json(operation.input)) {
          fail("APPLICATION_API_DECISION_MAPPING", `$line:${d.decision_mapping.source_line}`,
            "decision Mapping must project the provider response into the existing Operation input type");
        }
        decisionJoins.push({ source_id: d.id, binding_ref: binding.binding_id,
          contract_operation_ref: binding.contract_operation_ref, operation_ref: selector(operation.id),
          response_mapper_ref: binding.response_mapper_ref, decision_mapper_ref: mapperRef,
          response_type: responseType, decision_input_type: operation.input });
      }
      outboundIds.push(binding.binding_id);
    }
    return { source_id: d.id, kind: d.kind, source_line: d.source_line, binding_ref: binding.binding_id, operation_ref: selector(operation.id), request: requestType, response: responseType, request_mapper_ref: binding.request_mapper_ref, response_mapper_ref: binding.response_mapper_ref };
  });
  coverage(inboundIds, composition.inbound_endpoint_bindings.map((b: Obj) => b.binding_id), "$inbound");
  coverage(outboundIds, composition.external_api_bindings.map((b: Obj) => b.binding_id), "$outbound");
  coverage([...new Set(mappingIds)], composition.api_mappings.map((m: Obj) => m.mapping_id), "$mappings");
  coverage(routes.map(r => `${r.method} ${r.path}`), [...new Set(routes.map(r => `${r.method} ${r.path}`))], "$routes");
  const sourceComposition = JSON.parse(json(root.composition));
  const sourceFile = json(sourceComposition), compiledFile = json(composition), routesFile = json({ schema_version: "alchlang.application-api-routes/v1-candidate", routes, runtime_listener_observed: false, authority_effect: "none" });
  const decisionFile = decisionJoins.length ? json({ schema_version: "alchlang.application-api-decision-joins/v1-candidate",
    source_sha256: digest(source), joins: decisionJoins, runtime_calls_observed: false, authority_effect: "none" }) : undefined;
  const trace = { schema_version: "alchlang.application-external-api-trace/v1-candidate", source_sha256: digest(source), binding_sha256: digest(json(input)), composition_sha256: digest(sourceFile), compiled_composition_sha256: digest(compiledFile), routes_sha256: digest(routesFile), references,
    deferred_integrations: model.integrations.filter(d => d.kind !== "inbound-endpoint" && d.kind !== "outbound-call").map(d => ({ id: d.id, kind: d.kind })), payload_type_join: "required",
    ...(decisionFile ? { decision_joins_sha256: digest(decisionFile) } : {}), runtime_calls_observed: false, authority_effect: "none" };
  return { sourceComposition, composition, trace, ...(decisionFile ? { decisionJoins } : {}), files: {
    "external-api-composition.json": sourceFile, "external-api-compiled.json": compiledFile, "external-api-routes.json": routesFile,
    ...(decisionFile ? { "external-api-decision-joins.json": decisionFile } : {}), "external-api-trace.json": json(trace) } };
}

export function assertApplicationExternalApiCurrent(source: string, input: unknown, compiler: Pick<DomainSpecCompiler, "compileExternalApiComposition">, candidate: ReturnType<typeof lowerApplicationExternalApi>): void {
  if (json(candidate) !== json(lowerApplicationExternalApi(source, input, compiler))) fail("APPLICATION_API_STALE", "$", "candidate differs from exact source and bindings");
}
