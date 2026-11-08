import { CompilationRejected } from "./model.js";
import { parseDomainSource } from "./parser.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { ApplicationDeclaration, ApplicationInterfaceDeclaration, ApplicationMappingDeclaration, ApplicationPublicType, ApplicationType } from "./application-source.js";

const fail = (code: string, line: number, message: string): never => {
  throw new CompilationRejected([{ code, path: `$line:${line}`, message }]);
};
const same = (left: unknown, right: unknown) => json(left) === json(right);

function publicType(boundary: ApplicationInterfaceDeclaration, type: ApplicationPublicType): ApplicationType {
  if (type.kind === "contract") return { kind: "public-contract", interface: boundary.id, contract: type.ref };
  if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return { kind: type.kind, element: publicType(boundary, type.element) };
  return type as ApplicationType;
}

function declared(model: ApplicationFormalSource, id: string, kind: ApplicationDeclaration["kind"], line: number): ApplicationDeclaration {
  const node = model.declarations.find(item => item.id === id);
  if (node?.kind !== kind) fail("APPLICATION_WRITE_REFERENCE", line, `expected declared ${kind} ${id}`);
  return node!;
}

/** Source-only write/inspect join. It grants no native binding, dispatch, or replay authority. */
export function deriveApplicationExternalWriteBindings(source: string) {
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_WRITE_PROFILE", 1, "application-v1 source required");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const writes = model.integrations.filter(item => item.kind === "outbound-write");
  if (!writes.length) fail("APPLICATION_WRITE_COVERAGE", 1, "at least one outbound-write declaration required");
  const selectedPairs = new Set<string>();
  const bindings = writes.map(row => {
    const operation = declared(model, row.operation.ref, "operation", row.operation.source_line);
    const boundary = declared(model, row.interface.ref, "interface", row.interface.source_line);
    if (operation.kind !== "operation" || boundary.kind !== "interface") throw new Error("unreachable");
    if (boundary.boundary_kind !== "external" || boundary.members.length !== 2) {
      fail("APPLICATION_WRITE_PAIR", row.interface.source_line, "write and inspect require one external Interface with exactly two exposures");
    }
    const write = boundary.members.find(member => member.operation === row.write.ref);
    const inspect = boundary.members.find(member => member.operation === row.inspect.ref);
    if (!write || !inspect || write === inspect || !same(write.request, inspect.request) || !same(write.result, inspect.result)) {
      fail("APPLICATION_WRITE_PAIR", row.source_line, "write and inspect must be distinct Interface exposures with identical request and result types");
    }
    const pair = `${boundary.id}#${row.write.ref}#${row.inspect.ref}`;
    if (selectedPairs.has(pair)) fail("APPLICATION_WRITE_PAIR", row.source_line, "one write/inspect pair cannot be selected twice");
    selectedPairs.add(pair);
    const wireRequest = publicType(boundary, write!.request), wireResult = publicType(boundary, write!.result);
    const mapping = (id: string, line: number, input: ApplicationType, output: ApplicationType): ApplicationMappingDeclaration => {
      const node = declared(model, id, "mapping", line);
      if (node.kind !== "mapping") throw new Error("unreachable");
      const target = node.target.includes(".")
        ? { kind: "public-contract", interface: node.target.split(".")[0], contract: node.target.split(".")[1] } as ApplicationType
        : { kind: "declaration", ref: node.target } as ApplicationType;
      if (!node.total || node.inputs.length !== 1 || !same(node.inputs[0]!.type, input) || !same(target, output)) {
        fail("APPLICATION_WRITE_MAPPING", line, `Mapping ${id} must be total and map one exact typed input to the selected result`);
      }
      return node;
    };
    const request = mapping(row.request_mapping.ref, row.request_mapping.source_line, operation.input, wireRequest);
    const inspection = mapping(row.inspect_request_mapping.ref, row.inspect_request_mapping.source_line, operation.input, wireRequest);
    const response = mapping(row.response_mapping.ref, row.response_mapping.source_line, wireResult, operation.output);
    if (new Set([request.id, inspection.id, response.id]).size !== 3) {
      fail("APPLICATION_WRITE_MAPPING", row.source_line, "write request, inspect request, and response require distinct Mappings");
    }
    const qualify = (id: string) => `${symbol(model.domain_id)}:${symbol(id)}`;
    return { source_id: row.id, source_line: row.source_line, operation_ref: qualify(operation.id), interface_ref: qualify(boundary.id),
      interface_version: boundary.version, write_member_ref: `${qualify(boundary.id)}#${symbol(row.write.ref)}`,
      inspect_member_ref: `${qualify(boundary.id)}#${symbol(row.inspect.ref)}`,
      request_type: operation.input, result_type: operation.output, wire_request_type: wireRequest, wire_result_type: wireResult,
      request_mapping_ref: qualify(request.id), inspect_request_mapping_ref: qualify(inspection.id), response_mapping_ref: qualify(response.id),
      ambiguous_outcome: { unknown: row.on_unknown.action, unresolved: row.on_unresolved.action, conflict: row.on_conflict.action } };
  });
  const artifact = { schema_version: "alchlang.application-external-write/v1-candidate", source_sha256: digest(source), bindings,
    native_binding_status: "unbound", execution_policy: "refused-until-original-durable-external-owner", runtime_calls_observed: false,
    authority_effect: "none" };
  return { artifact, files: { "external-write-source-bindings.json": json(artifact) } };
}
