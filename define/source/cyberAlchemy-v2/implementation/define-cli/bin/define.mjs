#!/usr/bin/env node
import {runDefineCli} from "../src/cli.mjs";

process.exitCode = await runDefineCli(process.argv.slice(2));
