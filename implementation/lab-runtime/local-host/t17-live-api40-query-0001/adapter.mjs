// Invoke the cached published Paperclip process adapter without a server or DB.
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const [modulePath, moduleSha, configPath] = process.argv.slice(2);
if (!modulePath || !moduleSha || !configPath) throw new Error('selected adapter and config required');
const selected = await readFile(modulePath);
if (createHash('sha256').update(selected).digest('hex') !== moduleSha) throw new Error('adapter bytes changed');
const config = JSON.parse(await readFile(configPath, 'utf8'));
const { execute } = await import(pathToFileURL(modulePath).href);
const logs = [];
const result = await execute({
  runId: 't17-local-api40-read-only',
  agent: { id: 't17-local-paperclip-process-agent', companyId: 't17-disposable-local-company' },
  config,
  authToken: 't17-public-noncredential-marker',
  onLog: async (stream, chunk) => logs.push({ stream, bytes: Buffer.byteLength(chunk) }),
});
process.stdout.write(JSON.stringify({
  schema_version: 'lab-t17-paperclip-process-adapter-result/v1',
  exit_code: result.exitCode,
  signal: result.signal ?? null,
  timed_out: result.timedOut,
  error_message: result.errorMessage ?? null,
  result_json: result.resultJson ?? null,
  log_events: logs,
  paperclip_server_started: false,
  paperclip_api_called: false,
}) + '\n');
if (result.exitCode !== 0 || result.timedOut) process.exitCode = 1;
