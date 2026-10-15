# Use Paperclip to run a Lab evidence reader

Paperclip can start the Lab reader as a `process` agent and retain its output.
Start with status and catalog reads. The prepared runner also supports artifact
inspection and queries. Engineering changes, admission and release need their
own Lab operation channels and permissions; this reader does not execute them.

This setup selects candidate API12. Its focused common API checks passed;
full regression remains running and has an inherited assertion expecting 24
operations where the current contract declares 34. The original failure is
retained. This preparation is not a qualified pilot episode or an installed
Paperclip instance.

## 1. Select the local Paperclip instance

The repository and Python runtime are in WSL. Use Paperclip in the same WSL
environment so the absolute paths below resolve. The inspected published version
is `2026.1005.0`; its CLI requires Node 24.11 or newer. After a separately scoped
local setup is selected, the pinned onboarding command is:

```bash
npx paperclipai@2026.1005.0 onboard --yes
```

This command has not been executed for the pilot. It creates local Paperclip
state and starts onboarding. The existing candidate pilot protocol excludes
installation and network services, so this setup is a separate operation.

Create a company named `CyberAlchemy Lab` and a `process` agent named
`Lab evidence reader` in that selected local instance.

## 2. Bind the reader configuration

Use [process-adapter.template.json](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/pilot/preparation-v5/process-adapter.template.json).
Its executable, repository path, runner path, API source and protocol hashes
are selected. Replace the four explicit policy/key placeholders with the paths
and independent SHA-256 hashes from the actual authorized reader setup.
The template cannot execute until those selections exist.

The policy and Ed25519 key must reside in the selected owner's private `/tmp`
directory, with directory mode `0700` and file mode `0600`. The runner verifies
the independent hashes, policy, matching key and actual nonce challenge. These
are Lab credentials; Paperclip's task, company, agent and token do not grant
Lab permission. Keep the key bytes out of task text and this repository.

The published adapter inspected here uses `command` as the executable and a
separate `args` array, spawning with `shell: false`. Preserve the template's
argument array. Paperclip's documentation has a combined-command example;
the inspected package and actual process probe determine this configuration.

Run the selected command directly, then configure the same command and args in
Paperclip. `timeoutSec` is 960 and the reader's entire-episode timeout is 900.
The independently provided Lab grant must cover the actual attempt.

The initial plan obtains status and catalog. The runner performs an initial
status call to bind the cut, so this plan produces three authenticated reads.
It emits a JSON result on stdout and exits. Paperclip records process success
from the exit status; the runner makes no Paperclip API calls or issue updates.

## 3. Inspect the result as pilot owner

Your engineering question is: **How can I use Paperclip to run the Lab?**

Your confirmed research question is: **What verified evidence shows Paperclip
can run Lab tasks, and what is still unproven?**

Check the selected source cut, the catalog and the answer's limits. The existing
evidence proves that the published process adapter can invoke runner3 for
authenticated reads against the earlier API96. Common API12 has its own focused
22-check result. A new adapter run against API12 is pending; earlier evidence
does not qualify its successor.

Still unproven: compatibility with your installed server, company/agent setup,
real owner usefulness, engineering-action execution through Paperclip and a
complete Lab release. The pilot additionally requires a fresh Session journey:
this read runner does not support `session.open` or `session.close`, so that
journey must use the separately qualified Session interface.

Before actual pilot use, freeze the subject, success criteria, qualified API,
protocol, current grant and permitted operations. Record actual setup and answer
time, failures, costs and your own usefulness score: 1 unusable, 2 substantial
extra work, 3 mixed, 4 useful with correction, 5 useful without substantial
correction. A missing baseline remains unknown; successful process exit alone
does not establish usefulness.

Sources checked on 2026-10-12: [official quickstart](https://github.com/paperclipai/paperclip#quickstart),
[process adapter documentation](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md),
and the integrity-checked published `@paperclipai/server@2026.1005.0` package.
Exact local evidence bindings are in
[technical-evidence.json](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/pilot/preparation-v5/technical-evidence.json).
