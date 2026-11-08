import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const benchmarkRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(benchmarkRoot, "..");
let repositoryRoot = packageRoot;
while (!existsSync(join(repositoryRoot, ".git"))) {
  const parent = dirname(repositoryRoot);
  if (parent === repositoryRoot) throw new Error("Could not resolve repository root");
  repositoryRoot = parent;
}

const stamp = new Date().toISOString().replace(/[:.]/g, "-");
const outputRoot = join(repositoryRoot, "output", "playwright", "ux-validator", `alchlang-pareto-${stamp}`);
const frontend = spawnSync(process.execPath, [join(benchmarkRoot, "frontend-benchmark.mjs")], {
  cwd: packageRoot,
  env: { ...process.env, ALCHLANG_BENCHMARK_OUTPUT: outputRoot },
  stdio: "inherit",
});
const tournament = spawnSync(process.execPath, [join(benchmarkRoot, "pareto-tournament.mjs"), outputRoot, ...process.argv.slice(2)], {
  cwd: packageRoot,
  stdio: "inherit",
});
if ((frontend.status || 0) !== 0 || (tournament.status || 0) !== 0) process.exitCode = 1;
