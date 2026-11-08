import type { FactoryRunLockV1 } from "./factory-run-lock-v1.js";
import type { FactoryRunRequestV1 } from "./factory-run-request-v1.js";

export type FactoryRunPlanV1 = Readonly<{
  schema_version: "FactoryRunPlan/v1";
  request: FactoryRunRequestV1;
  lock: FactoryRunLockV1;
  run_id: string;
  authority_effect: "none";
}>;
