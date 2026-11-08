import type { OperationPattern } from "../registry-compiler.js";

export const generatedOperationPatterns = [
  {
    "pattern_id": "operation-port",
    "architecture_pattern_status": "candidate",
    "meta_type": {
      "id": "DS-D1.4",
      "status": "closed"
    },
    "integration_binding": {
      "id": "target-neutral-port",
      "status": "closed"
    },
    "generator": {
      "id": "typescript-operation-port-v1",
      "status": "closed"
    },
    "conformance": {
      "id": "general-compiler-v1-action-port-tests",
      "status": "closed"
    },
    "availability": "available",
    "generated_artifacts": [
      "domain.tools.ts"
    ],
    "blockers": []
  },
  {
    "pattern_id": "transactional-outbox",
    "architecture_pattern_status": "candidate",
    "meta_type": {
      "id": "DS-D1.4",
      "status": "closed"
    },
    "integration_binding": {
      "id": "sqlite-transactional-outbox",
      "status": "closed"
    },
    "generator": {
      "id": "typescript-sqlite-transactional-outbox-v1",
      "status": "closed"
    },
    "conformance": {
      "id": "transactional-outbox-executable-tests",
      "status": "closed"
    },
    "availability": "available",
    "generated_artifacts": [
      "domain.outbox.port.ts",
      "domain.outbox.sqlite.ts",
      "domain.outbox.migration.sql",
      "domain.outbox.worker.ts",
      "domain.outbox.provider.ts",
      "domain.outbox.test.ts",
      "domain.generation-manifest.json"
    ],
    "blockers": []
  }
] as const satisfies readonly OperationPattern[];
