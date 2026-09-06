export type FactoryProcessObservationV1 = Readonly<{
  schema_version: "FactoryProcessObservation/v1";
  run_id: string;
  coordinator_pid: number;
  staging_path: string;
  output_path: string;
  started_at: string;
  finished_at: string;
  child_pids: readonly number[];
  cleanup: "pass" | "published-with-cleanup-residue";
  authority_effect: "none";
}>;
