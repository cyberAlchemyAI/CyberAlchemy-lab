# Run bounded Lab reads from Paperclip

This candidate runner gives Paperclip's `process` adapter a local command that
performs nonce-authenticated Lab reads and exits. It uses a separately selected
Lab policy, reader credential, source hash and protocol hash. Paperclip task IDs
and its API token do not grant Lab permission.

The runner can call `lab.status`, `catalog.get`, `artifact.inspect` and
`artifact.query`. It retains the source cut learned by the initial status call,
checks reply/request/profile/context bindings, and closes the child process.
A refusal, timeout, changed source or incomplete exit makes the runner fail.
It makes no Paperclip API calls and forwards no `PAPERCLIP_*` environment
variables into Lab. Its result reports technical reads; human usefulness remains
unknown until the pilot owner responds.

## Paperclip configuration

Paperclip is not installed on the pilot owner's machine yet. No Paperclip
installation, company/agent creation, server start or external issue update has
been performed by this package.

After selecting a qualified API and independently provisioning the isolated
reader policy and its private credential, configure a `process` agent with
`command` pointing to the Python runner, `cwd` pointing to the repository and a
timeout covering the whole episode. Pass these runner arguments:

| Argument | Exact selection |
| --- | --- |
| `--api-root` | Frozen qualified sibling API directory |
| `--source-sha256` | Independently verified API source-manifest hash |
| `--profile-sha256` | Selected protocol-profile hash |
| `--policy`, `--policy-sha256` | Independently provisioned isolated policy and its exact hash |
| `--reader-key`, `--reader-key-sha256` | Matching private Ed25519 reader file and its independently selected hash |
| `--plan`, `--plan-sha256` | Selected read plan and exact hash |
| `--timeout-seconds` | Actual entire episode limit, at most 900 seconds |

The current credential/policy custody scope is an owner-only `/tmp` namespace.
It is appropriate for the isolated candidate pilot and does not supply a stable
operational deployment. Do not copy a private credential into this repository or
Paperclip task text. A stable host/credential topology belongs to independently
scoped operational work.

Run the command directly first. Then run that same command through Paperclip
and compare the recorded observations. An exit code alone does not close Work,
Lab acceptance, owner usability or admission.

## Pilot evidence

The owner selected the genuine question: "how can i use paperclip to run the lab"
and identified themselves as pilot owner. They also reported that Paperclip is
not installed yet. These are study inputs, not completed pilot observations.
R05 starts only after its API/context/transport prerequisites pass. Preserve
setup time, failed attempts and the owner's own usefulness assessment.

Official sources checked on 2026-10-12:

- [Paperclip adapter overview](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/overview.md): local agent runtime selection.
- [Process adapter](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md): command, working directory, environment and timeout configuration; process result handling.
- [Adapter interface](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/creating-an-adapter.md): the future custom-adapter boundary if structured transcripts are needed.

This source review does not establish compatibility with an installed Paperclip
version or a running Paperclip server; those observations remain pending.
