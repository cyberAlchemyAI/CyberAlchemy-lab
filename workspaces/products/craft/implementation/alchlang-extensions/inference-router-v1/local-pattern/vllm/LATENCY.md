# Live Qwen latency diagnosis

Status: measured diagnostic evidence, authority effect none.
Raw timings and metric snapshots (result record excluded). Eight sequential generation
requests, four direct and four through Alch; same short greeting, output cap 256,
default sampling. No configuration changes. Temporary service/tunnel closed.

The initial ~2.35 seconds measured total completion, not time to first text. Fresh
samples ranged from 1.02 to 1.86 seconds through Alch and 1.53 to 2.02 seconds direct.
Variable output lengths mean this is not a controlled fixed-token overhead benchmark.

The vLLM histogram count increased by exactly eight. Differences in sums divided
by eight give mean queue 0.032 ms, prefill 73.174 ms, decode 1226.144 ms, and server
end-to-end 1304.644 ms. The largest measured server component is decoding, not queueing.

Direct streams began reasoning at 308/338 ms, then visible content at 1388/1411 ms.
They generated 130–132 reasoning characters alongside only 11 visible characters.
The binding omits reasoning metadata from public output, but the engine still spends
time generating it. Reported completion counts were 18–48 across these requests;
reasoning-token counts were not separately reported, so they are not inferred as
exact counts from character lengths.

Remote health took 140–142 ms (a network/server round-trip baseline, not pure wire
latency). The separate /tokenize call took 132–142 ms, median 138 ms. This is a real
additional round trip before every model invocation. Local service health took
4–15 ms but is not a measurement of the full invocation pipeline's CPU overhead.
Direct and Alch streams both producing 35 completion tokens took approximately
1.54 and 1.74 seconds respectively; their ~0.20-second difference is only indicative.

## Open Questions

A controlled per-request comparison of reasoning enabled/disabled could quantify
an optional faster mode. Do not remove the tokenizer context check simply to save
a round trip; any replacement must preserve its safety bound. Larger prompts,
concurrent load, cold starts, exact pipeline CPU timing and remote GPU hardware
performance were not measured. These results diagnose the short greeting workflow,
not overall model quality or production capacity.
