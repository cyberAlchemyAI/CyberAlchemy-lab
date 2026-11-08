#!/usr/bin/env node
import {main} from './cli.js';

process.env.ALCHLANG_DISTRIBUTION='rust';
main().catch((error:unknown)=>{
  console.error(error instanceof Error?error.message:String(error));
  process.exitCode=1;
});
