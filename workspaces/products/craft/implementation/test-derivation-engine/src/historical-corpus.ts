import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

export const HISTORICAL_CORPUS_ROOT = fileURLToPath(
  new URL("../__fixtures__/poker-team-corpus/", import.meta.url),
);

const MANIFEST_SHA256 =
  "6ae0373ac7b7805e549a9cb57c0a3ddd113fdac8ca3c8c071a39ef1963093dfe";
const SOURCE_COMMIT = "6c990537662dca7abe3f77f3aff35ae897db2bf6";
const FEATURES = [
  "financial-settlement", "player-onboarding", "auth-access-control",
  "player-makeup", "player-management", "player-progression", "player-stats",
] as const;
const FILES = [
  "states.md", "operations.md", "interfaces.md", "events.md", "workflows.md",
  "queries.md", "mappings.md", "domain.md", "TEST-SPEC.md",
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

export class HistoricalCorpusError extends Error {
  readonly code = "HISTORICAL_CORPUS_DRIFT";
  constructor(message: string) {
    super(message);
    this.name = "HistoricalCorpusError";
  }
}

function fail(message: string): never {
  throw new HistoricalCorpusError(message);
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
    if (entry.isSymbolicLink()) fail(`symlink in historical corpus: ${absolute}`);
    if (entry.isDirectory()) result.push(...listRegularFiles(root, absolute));
    else if (entry.isFile()) result.push(relative(root, absolute).replaceAll("\\", "/"));
    else fail(`non-regular historical corpus entry: ${absolute}`);
  }
  return result.sort();
}

/** Verifies a historical test fixture, never an active application source. */
export function verifyHistoricalPokerTeamCorpus(root = HISTORICAL_CORPUS_ROOT): string {
  try {
    const rootStat = lstatSync(root);
    if (!rootStat.isDirectory() || rootStat.isSymbolicLink()) fail("historical corpus root is not a real directory");
    const manifestPath = join(root, "IMPORT-MANIFEST.json");
    const manifestStat = lstatSync(manifestPath);
    if (!manifestStat.isFile() || manifestStat.isSymbolicLink()) fail("historical corpus manifest is not a real file");
    const manifestBytes = readFileSync(manifestPath);
    if (sha256(manifestBytes) !== MANIFEST_SHA256) fail("historical corpus manifest digest drifted");
    const manifest = JSON.parse(manifestBytes.toString("utf8")) as Manifest;
    if (
      manifest.schema_version !== "tde.historical-poker-team-corpus/v1-candidate" ||
      manifest.source_repository !== "https://github.com/vrondelli/poker-team.git" ||
      manifest.source_commit !== SOURCE_COMMIT ||
      manifest.purpose !== "historical-parser-roundtrip-regression-only" ||
      manifest.authority_effect !== "none"
    ) fail("historical corpus provenance drifted");

    const expected = FEATURES.flatMap((feature) => FILES.map((file) => `docs/features/${feature}/${file}`)).sort();
    const selected = manifest.entries.map((entry) => entry.path).sort();
    if (selected.length !== 63 || selected.some((path, index) => path !== expected[index])) {
      fail("historical corpus selected-path denominator drifted");
    }
    const observed = listRegularFiles(root);
    const permitted = ["IMPORT-MANIFEST.json", ...expected].sort();
    if (observed.length !== permitted.length || observed.some((path, index) => path !== permitted[index])) {
      fail("historical corpus file set drifted");
    }
    for (const entry of manifest.entries) {
      const bytes = readFileSync(join(root, entry.path));
      if (bytes.length !== entry.size_bytes || sha256(bytes) !== entry.sha256 || blobOid(bytes) !== entry.git_blob_oid) {
        fail(`historical corpus bytes drifted: ${entry.path}`);
      }
    }
    return join(root, "docs", "features");
  } catch (error) {
    if (error instanceof HistoricalCorpusError) throw error;
    fail(`historical corpus unavailable: ${error instanceof Error ? error.message : String(error)}`);
  }
}
