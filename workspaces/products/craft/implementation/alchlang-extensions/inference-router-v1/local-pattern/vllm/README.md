# Configure and run a vLLM engine

Status: local workspace candidate. Open questions are below. The remote instance
is operator-owned; setup does not install software or change its running services.

From this checkout, using the SSH address supplied for Vast instance 50212590:

```bash
tools/inference-reference configure-engine --host 136.56.33.107 --ssh-port 25453
```

Run on the machine with your SSH key or agent. SSH host trust must already exist:
connect normally first and verify the fingerprint using your instance's trusted
connection details. The script uses strict host checking and noninteractive key
authentication; it does not enroll keys or accept unknown host identities. Set
`--user` if the instance uses a user other than root. An optional `--identity-file`
is an absolute key path passed to SSH, never read by this program. SSH configuration
files are not used; supply the host, port and identity explicitly as needed.

Setup asks for missing settings, inspects listening TCP ports through a fixed
read-only Python 3 script on the selected instance, and queries `/v1/models` on
those internal ports. Discovery probes at most 64 listeners with bounded time and
response size. Multiple model APIs require selection. No model name or internal
vLLM port is guessed from the template label. This also avoids the public Caddy
HTTP/Basic endpoint observed on external port 25563.

If internal discovery cannot find an unauthenticated API, pass its known port with
`--remote-port PORT`. If vLLM itself requires a bearer token, set it in your local
environment and add `--token-env VLLM_API_TOKEN`; that environment variable must
remain available when checking/starting the engine. Never pass token values on the
command line. Discovery does not read remote environment variables or secrets.

A direct connection is also supported:

```bash
tools/inference-reference configure-engine --base-url https://your-engine.example --token-env VLLM_API_TOKEN
```

Supply the origin, without `/v1`, query parameters or URL credentials. Only HTTPS
or numeric `http://127.0.0.1` is accepted. For private certificates, use Node's
normal `NODE_EXTRA_CA_CERTS` configuration with a trusted certificate; no insecure
TLS mode is provided. A manually established local tunnel can use the loopback
option. This HTTP client requires a direct endpoint; it does not configure proxies.

Setup discovers the exact served model ID, obtains its context limit when reported,
checks `/tokenize`, and saves a new mode-0600 file at
`~/.config/alch-inference/engine.json`. It stores connection/model settings and
optional secret environment-variable names, never secret values. It refuses to
write inside this repository or overwrite an existing configuration. Use
`--config /absolute/new-file.json` to configure another engine or replace a dynamic
address. The API remains loopback-only on your machine.

```bash
tools/inference-reference check-engine
tools/inference-reference test-engine
tools/inference-reference engine
```

`check-engine` verifies model presence and tokenizer access without inference.
`test-engine` sends two short prompts through the complete service, one JSON and
one SSE request, then closes everything. `engine` starts the SSH tunnel, translator
and accepted Alch/DomainSpec service and prints its actual loopback API address.
All three accept `--config FILE`. Ctrl+C closes the service and its tunnel; tunnel
exit also stops the service. No daemon or automatic reconnect/retry is installed.

At the printed service address, call the existing API using alias `vllm-chat`:

```bash
curl --fail-with-body -H 'Content-Type: application/json' -d '{"task":"text.generate","model":"vllm-chat","input":{"messages":[{"role":"user","content":"Hello"}]},"parameters":{"max_output_tokens":32}}' http://127.0.0.1:PRINTED_PORT/v1/inference
```

Use `configure-engine --help` for noninteractive flags (`--yes`, exact model,
context/output limits, timeout and output file). Omitting a setting that cannot
be safely discovered fails with an explicit diagnostic in noninteractive mode.
Configuration success proves connectivity and tokenization, not generation;
`test-engine` is the separate generation check.

## Contract and implementation boundaries

The public API, selection, custody, errors and stream lifecycle still come from
Alch declarations compiled through DomainSpec into the accepted bundle. The new
native translator normalizes vLLM wire data into `alch-local-text/v1`; it does not
replace those policies. No DomainSpec schema change is required for this binding.
It uses one configured engine and a fresh private bearer credential between the
service and loopback translator. Authentication to the engine is independent of
client/tenant authentication. This command runs the public local composition;
the protected Auth Foundation rehearsal remains available separately.

Requests use `/v1/chat/completions` with text messages, `n: 1`, `max_tokens` and the
stream flag. JSON uses assistant `content`; SSE maps content deltas, a finish
reason, optional usage trailer and `[DONE]`. Reasoning metadata is omitted; a
reasoning-only response is not synthesized into an answer. Tool calls and
multimodal output are unsupported. Missing usage remains null. Incomplete SSE,
invalid choices, redirects and upstream failures fail closed without retry.

Each prompt is checked through `/tokenize` using the same model/messages and
`add_generation_prompt: true` before generation. The configured input budget is
`contextLimit - outputLimit`, keeping the accepted selector's conservative bound
valid. No tools or custom chat-template overrides are injected. The server remains
responsible for applying the same model/template to tokenization and generation.
Context overflow or unavailable tokenization blocks the call. A model swap under
the same ID is not cryptographically detected; rerun setup after engine changes.

The existing deadline is at most 30 seconds for tokenization plus generation.
Public requests and normalized streams remain bounded by the accepted contract;
upstream bodies/streams are capped at 1 MiB and upstream SSE frames at 64 KiB.
Local resource cleanup does not prove remote GPU computation stopped.

## Sources

- [Vast base-image connection contract](https://github.com/vast-ai/base-image/blob/main/README.template.md): SSH forwarding to internal services and Caddy separation.
- [vLLM chat API](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/): compatible serving surface.
- [vLLM tokenization implementation](https://docs.vllm.ai/en/latest/api/vllm/entrypoints/serve/tokenize/serving/): chat-template tokenization and count.
- [Existing local protocol](../PROTOCOL.md), [construction plan](PLAN.md).

## Open Questions

The live Vast endpoint, actual model ID, tokenizer availability and generation
latency must be verified through the operator commands. No specific Qwen model
revision or template tag compatibility is claimed from the user's display label.
Longer deadlines, full tokenizer pinning, persistent hosted service operation and
model-specific reasoning controls are separate follow-ups if real measurements
require them. The dynamic address and SSH trust remain operator-owned.
