# Run a Lab evidence reader from Paperclip

The pilot owner asked how to use Paperclip to run the Lab and reported that
Paperclip is not installed. This setup targets WSL, where this repository and
the Lab Python environment reside. Node 26.8.1 is available here.

Paperclip assigns and tracks tasks. The Lab runner authenticates independently
and performs bounded reads. Begin with one evidence reader; implementation,
admission, tool dispatch and release require their own qualified Lab interfaces.

## Install and select the first reader

Paperclip's published version inspected on 2026-10-12 is `2026.1005.0`. Its CLI
requires Node 24.11 or newer. The official onboarding command, pinned to that
version, is:

```bash
npx paperclipai@2026.1005.0 onboard --yes
```

This command creates a local Paperclip instance. It has **not** been executed
for this pilot. Package inspection occurred in a temporary directory without
starting the server, creating a company or registering an agent.

Once the Lab pilot prerequisites pass and the local instance is selected,
create a company named `CyberAlchemy Lab` and a `process` agent named
`Lab evidence reader`. Select this repository as the working directory.

The inspected published adapter launches an executable with a separate `args`
array and `shell: false`. Set `command` to:

```text
/tmp/cal-R02-environment-0001/bin/python
```

Set `cwd` to `/home/vlad_/projects/CyberAlchemy-lab`. Start `args` with `-I`,
`-B`, and the absolute path to
`product/lab/release-candidates/v1/interface/paperclip-runner-v3/runner.py`.
Then supply the nine required API/policy/key/plan selectors described in the
runner's README. Set `timeoutSec` to 960 and the runner's `--timeout-seconds`
to 900. The independently provisioned Lab permission must cover the episode.

API96 has a passing direct read-runner qualification for three authenticated
reads. Its full regression has a real Session timing failure, and the successor
API is still under qualification. Those observations do not establish the R05
pilot prerequisites. Final API selection and actual private policy/key custody
remain pending; this is not an executable agent configuration yet.

Keep the private Lab key outside the repository and Paperclip task text. The
runner accepts an independently pinned owner-only file. Paperclip's injected
token and company/agent identifiers do not confer Lab authority.

## First pilot task

Use the owner's actual question: **How can I use Paperclip to run the Lab?**
The first technical task should inspect Lab status and the selected catalog.
Keep the direct-run observations and Paperclip-run observations separately.
Record elapsed setup time, failed attempts, the evidence retrieved, and the
owner's own assessment of whether the result helped them operate the Lab.

An exit code records process completion. Lab Work satisfaction, the three
required pilot journeys and the final owner checkpoint need their separate
evidence. No human usefulness result has been recorded yet.

Sources: [official installation instructions](https://github.com/paperclipai/paperclip#quickstart),
[process adapter documentation](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md),
and the published `@paperclipai/server@2026.1005.0` process adapter code inspected
from its integrity-checked npm archive. Installed-instance compatibility remains
unverified.
