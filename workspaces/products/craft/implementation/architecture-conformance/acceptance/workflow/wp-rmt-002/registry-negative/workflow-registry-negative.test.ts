import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {describe,expect,it} from "vitest";
import {listFactoryNodeProvidersV1} from "../../../../factory/registry/factory-node-registry-v1.js";
const registryPath="projects/domainspec-v2/impl/architecture-conformance/factory/registry/factory-node-registry-v1.ts",registrySha256="2497f2e047e023de2738bac4b815e6b0212560dcfc8053982c94f4a529a9f51b";
describe("WP-RMT-002 Workflow registry nonmembership",()=>{it("keeps all State Machine and Workflow direct provider ids absent from the unchanged registry",()=>{const bytes=readFileSync(registryPath);expect(createHash("sha256").update(bytes).digest("hex")).toBe(registrySha256);const ids=listFactoryNodeProvidersV1().map(({provider_id})=>provider_id);expect(ids).toContain("typescript-w4-orchestration-lifecycle-v1");for(const id of["state-machine-typescript-v1","state-machine-python-v1","state-machine-rust-v1","workflow-typescript-v1","workflow-python-v1","workflow-rust-v1"])expect(ids).not.toContain(id);expect(new Set(ids).size).toBe(ids.length);});});
