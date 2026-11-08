import fs from "node:fs";
import os from "node:os";
import path from "node:path";

/** A temporary successor of the commerce fixture; canonical example bytes stay intact. */
export function publicApiApplication(t: { after(fn: () => void): void }, valueObjectProjection = false) {
  const example = path.resolve(import.meta.dirname, "../../examples/reconciled-commerce");
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "ds-public-api-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const root = path.join(temporary, "source"); fs.cpSync(path.join(example, "source"), root, { recursive: true });
  const read = (file: string) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
  const write = (file: string, value: unknown) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2) + "\n");
  const feature = read("specs/commerce/feature.json");
  const type = { kind: "contract", interface_selector: "commerce:api", contract_id: "response" };
  for (const id of ["public-api-request", "public-api-response"]) {
    feature.nodes.push(id); feature.edges.push(`${id}-maps-api`);
    write(`specs/commerce/nodes/${id}.json`, { schema_version: "domainspec.node/v1", feature_id: "commerce", node_id: id, kind: "Mapping", body: {
      description: "Explicit public-to-public API projection.", target: "commerce:api", typed_contract: {
        schema_version: "domainspec.typed-mapping/v3", ontology_mapping: "FIXTURE-" + id.toUpperCase(), inputs: [{ name: "payload", type, use: null }],
        target: type, target_use: null, total: true,
        fields: ["id", "net", "fee"].map(target => ({ target, value: { op: "path", root: "payload", properties: [`R13-RESPONSE#${target}`] }, default: null })),
      },
    } });
    write(`specs/commerce/edges/${id}-maps-api.json`, { schema_version: "domainspec.edge/v1", feature_id: "commerce", edge_id: `${id}-maps-api`, relationship: "maps", source_node_id: id, target_node_id: "api", scope: "feature" });
  }
  if (valueObjectProjection) {
    feature.nodes.push("public-money"); feature.edges.push("public-money-maps-money");
    write("specs/commerce/nodes/public-money.json", { schema_version: "domainspec.node/v1", feature_id: "commerce", node_id: "public-money", kind: "Mapping", body: {
      description: "Project Money fields without constructing or enforcing its positive invariant.", target: "commerce:money", typed_contract: {
        schema_version: "domainspec.typed-mapping/v3", ontology_mapping: "FIXTURE-PUBLIC-MONEY", inputs: [{ name: "payload", type, use: null }],
        target: {kind: "named", selector: "commerce:money"}, target_use: null, total: true,
        fields: [
          {target: "quantity", value: {op: "path", root: "payload", properties: ["R13-RESPONSE#net"]}, default: null},
          {target: "note", value: {op: "literal", type: "String", value: "projection"}, default: null},
        ],
      },
    } });
    write("specs/commerce/edges/public-money-maps-money.json", {schema_version: "domainspec.edge/v1", feature_id: "commerce", edge_id: "public-money-maps-money", relationship: "maps", source_node_id: "public-money", target_node_id: "money", scope: "feature"});
  }
  write("specs/commerce/feature.json", feature);
  const source = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));
  const member = source.external_api.external_api_contracts[0].operations[0];
  member.request_type_ref = "commerce:api#response"; member.result_type_ref = "commerce:api#response";
  const binding = source.external_api.external_api_bindings[0];
  binding.request_mapper_ref = "commerce:public-api-request"; binding.response_mapper_ref = "commerce:public-api-response";
  const request = source.external_api.api_mappings.find((m: any) => m.mapping_id === "api-mapping:authorize-request");
  request.mapper_ref = binding.request_mapper_ref; request.source_ref = member.request_type_ref;
  const response = source.external_api.api_mappings.find((m: any) => m.mapping_id === "api-mapping:authorize-response");
  response.mapper_ref = binding.response_mapper_ref; response.target_ref = member.result_type_ref;
  return { temporary, root, source, type, selection: (language: string) => JSON.parse(fs.readFileSync(path.join(example, `selections/${language}.json`), "utf8")) };
}
