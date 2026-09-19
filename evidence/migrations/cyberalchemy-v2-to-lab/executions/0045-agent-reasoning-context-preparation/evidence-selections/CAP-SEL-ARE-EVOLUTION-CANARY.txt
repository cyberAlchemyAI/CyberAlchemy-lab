#!/usr/bin/env node
import {projectCanaryResult, runFixtureEvolutionCanary} from "../src/evolution-canary.mjs";

const result = projectCanaryResult(await runFixtureEvolutionCanary());
process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
process.exitCode = result.status === "RECOMMEND" ? 0 : 1;
