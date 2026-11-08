import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const HISTORICAL_BACKEND_ROOT = fileURLToPath(
  new URL("../../../__fixtures__/poker-team-backend/", import.meta.url),
);

const MANIFEST_SHA256 = "28595c7127de554cca271036ad009ea42f163ba5df30ecd97c81c7c886411e2d";
const SOURCE_COMMIT = "6c990537662dca7abe3f77f3aff35ae897db2bf6";
const SOURCE_FILES = [
  "domain/__derived__/financial-settlement.sfol.adapter.ts",
  "domain/deal/deal.service.ts",
  "domain/limit/limit.service.ts",
  "domain/makeup/makeup-policy.service.ts",
  "domain/player-stats/player-stats-window.vo.ts",
  "domain/player-stats/player-stats.entity.ts",
  "domain/player-stats/player-stats.repository.ts",
  "domain/player/player.entity.ts",
  "domain/player/player.repository.ts",
  "domain/settlement/settlement.events.ts",
  "domain/settlement/settlement.service.ts",
  "domain/shared/financial-write-unit-of-work.ts",
  "domain/transaction/transaction.entity.ts",
  "domain/transaction/transaction.repository.ts",
  "infrastructure/telemetry/instruments.ts",
  "use-cases/financial-settlement/generate-settlement.ts",
  "use-cases/financial-settlement/settlement-kpi-runtime.ts",
  "use-cases/financial-settlement/settlement.dto.ts",
] as const;

type Manifest = {
  readonly schema_version: string;
  readonly source_repository: string;
  readonly source_commit: string;
  readonly purpose: string;
  readonly authority_effect: string;
  readonly entries: readonly {
    readonly path: string;
    readonly sha256: string;
    readonly size_bytes: number;
    readonly git_blob_oid: string;
  }[];
};

export class HistoricalBackendError extends Error {
  readonly code = "HISTORICAL_BACKEND_DRIFT";
  constructor(message: string) {
    super(message);
    this.name = "HistoricalBackendError";
  }
}

function fail(message: string): never {
  throw new HistoricalBackendError(message);
}

function sha256(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function blobOid(bytes: Buffer): string {
  return createHash("sha1")
    .update(Buffer.from(`blob ${bytes.length}\0`))
    .update(bytes)
    .digest("hex");
}

function listRegularFiles(root: string, directory = root): string[] {
  const result: string[] = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (entry.isSymbolicLink()) fail(`symlink in historical backend: ${absolute}`);
    if (entry.isDirectory()) result.push(...listRegularFiles(root, absolute));
    else if (entry.isFile()) result.push(relative(root, absolute).replaceAll("\\", "/"));
    else fail(`non-regular historical backend entry: ${absolute}`);
  }
  return result.sort();
}

/** Verifies immutable historical test source; it grants no current-application claim. */
export function verifyHistoricalPokerTeamBackend(root = HISTORICAL_BACKEND_ROOT): string {
  try {
    const rootStat = lstatSync(root);
    if (!rootStat.isDirectory() || rootStat.isSymbolicLink()) fail("historical backend root is not a real directory");
    const manifestPath = join(root, "IMPORT-MANIFEST.json");
    const manifestStat = lstatSync(manifestPath);
    if (!manifestStat.isFile() || manifestStat.isSymbolicLink()) fail("historical backend manifest is not a real file");
    const manifestBytes = readFileSync(manifestPath);
    if (sha256(manifestBytes) !== MANIFEST_SHA256) fail("historical backend manifest digest drifted");
    const manifest = JSON.parse(manifestBytes.toString("utf8")) as Manifest;
    if (
      manifest.schema_version !== "tde.historical-poker-team-backend/v1-candidate" ||
      manifest.source_repository !== "https://github.com/vrondelli/poker-team.git" ||
      manifest.source_commit !== SOURCE_COMMIT ||
      manifest.purpose !== "historical-p4-r4-regression-only" ||
      manifest.authority_effect !== "none"
    ) fail("historical backend provenance drifted");

    const expected = SOURCE_FILES.map((path) => `backend/src/${path}`).sort();
    const selected = manifest.entries.map((entry) => entry.path).sort();
    if (selected.length !== 18 || selected.some((path, index) => path !== expected[index])) {
      fail("historical backend selected-path denominator drifted");
    }
    const observed = listRegularFiles(root);
    const permitted = ["IMPORT-MANIFEST.json", ...expected].sort();
    if (observed.length !== permitted.length || observed.some((path, index) => path !== permitted[index])) {
      fail("historical backend file set drifted");
    }
    for (const entry of manifest.entries) {
      const bytes = readFileSync(join(root, entry.path));
      if (bytes.length !== entry.size_bytes || sha256(bytes) !== entry.sha256 || blobOid(bytes) !== entry.git_blob_oid) {
        fail(`historical backend bytes drifted: ${entry.path}`);
      }
    }
    return join(root, "backend", "src");
  } catch (error) {
    if (error instanceof HistoricalBackendError) throw error;
    fail(`historical backend unavailable: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export async function importHistoricalPokerTeamBackendModule(
  module: "p4-adapter" | "r4-settlement",
  root = HISTORICAL_BACKEND_ROOT,
): Promise<unknown> {
  const sourceRoot = verifyHistoricalPokerTeamBackend(root);
  const selected = module === "p4-adapter"
    ? "domain/__derived__/financial-settlement.sfol.adapter.ts"
    : "domain/settlement/settlement.service.ts";
  return import(pathToFileURL(join(sourceRoot, selected)).href);
}
