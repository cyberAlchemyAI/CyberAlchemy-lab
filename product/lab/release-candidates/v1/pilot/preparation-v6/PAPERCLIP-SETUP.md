# Connect Paperclip to the Lab

Use Paperclip to assign and track work. Add a Lab reader as a process agent so
Paperclip can start the reader and show its result. The first setup reads Lab
status and its catalog. Engineering actions need their own configured Lab
channels and permissions.

The published Paperclip process adapter passed an actual API14 check: three
authenticated reads, six refusal checks, unchanged original source guards,
exit 0 and temporary credential cleanup. Paperclip is still uninstalled here.
This result establishes the adapter connection; the human pilot and full Lab
release remain open. Exact evidence is in
[technical-evidence.json](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/pilot/preparation-v6/technical-evidence.json).

## Local setup

1. Run Paperclip in the same WSL environment as this repository. The inspected
   package version is `2026.1005.0`; Node 24.11 or newer is required. A selected
   local installation can use `npx paperclipai@2026.1005.0 onboard --yes`.
   This creates persistent local Paperclip state and starts onboarding; it has
   not been run as part of the candidate pilot. The existing pilot protocol
   excludes installation and network services, so actual setup needs its own
   concrete scope.
2. Create a company named `CyberAlchemy Lab` and a process agent named
   `Lab evidence reader`. Use the command, argument array and working directory
   from [process-adapter.template.json](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/pilot/preparation-v6/process-adapter.template.json).
3. Before running it, supply a fresh authorized reader policy and key. Replace
   the four policy/key placeholders with their absolute private paths and
   independently selected SHA-256 hashes. Keep the directory mode `0700` and
   credential files `0600`. The actual authentication checks policy, key,
   nonce, source and expiry. A Paperclip company or task does not grant Lab
   permission. Do not paste key bytes into a task.
4. Run that exact command directly, then run the same configuration in
   Paperclip. A successful first run returns JSON containing status, status
   and catalog reads. The extra status read establishes the selected source
   cut. The process exits; it does not update Paperclip tasks through its API.

The adapter uses an executable plus a separate argument array with
`shell: false`. Preserve the array. `timeoutSec` is 960; the reader's whole
episode is bounded to 900 seconds. Permission must cover the actual attempt.

## Your pilot

Your engineering question is **How can I use Paperclip to run the Lab?**
Your research question is **What verified evidence shows Paperclip can run Lab
tasks, and what is still unproven?** You reported that you do not know how to
connect it yet; no timed baseline was performed.

After setup, inspect the returned source cut and catalog. The verified answer
so far is that Paperclip's published process adapter can launch the Lab reader
for these authenticated reads against API14. The runner also supports artifact
inspection and queries, but this adapter episode exercised only status and
catalog. Running engineering changes through Paperclip, compatibility with
your installed instance and actual usefulness still need observed work.

The pilot also requires a real fresh Session journey through the qualified
Session interface. This four-operation reader runner does not open Sessions.
Freeze the task, subject, success criteria, qualified source and permitted
operations before the human episode. Record actual setup and answer time,
failures and your usefulness score from 1 (unusable) to 5 (useful without
substantial correction). Missing answers remain unknown.

Sources checked on 2026-10-13: [official quickstart](https://github.com/paperclipai/paperclip#quickstart)
and [process adapter documentation](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md).
The inspected immutable package and actual process result determine the
selected configuration. This guide does not claim compatibility with a newer
package or an installed server.
