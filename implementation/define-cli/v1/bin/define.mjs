#!/usr/bin/env node
import {runLabDefine} from '../src/lab-cli.mjs';
process.exitCode = await runLabDefine(process.argv.slice(2));
