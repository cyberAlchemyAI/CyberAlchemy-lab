# Selected runtime privacy runner

`run_privacy.py` constructs actual Source/Reader/Service/resources through the
unchanged selected API's inherited Session fixture. It writes a unique note to
real Session RAM, then exercises successful and refused API reads, malformed
wire input, a forbidden typed Vault write, close and a fresh custodian reading
closed metadata. It checks the held note buffer was zeroed and the restarted
custodian has no live Session.

The runner scans wire replies, owned journal/object files and captured
stdout/stderr for the unique sentinel's raw bytes, Base64 and hexadecimal forms.
It prints no sentinel, exception values, hostile response bodies or private
runtime paths. Its private result file is created exclusively. The selected
Source and profile are guarded at entry and exit.

Use the selected isolated native Python/loader with `-I -B -S`; supply its real
`deps` directory and the exact selected API/source/profile on this trusted CLI.
A caller's wire message cannot select this test fixture or runtime. No clocks,
Service methods or runtime permission checks are replaced.

The actual API73 run in `RUN-API73-0001.json` passed: eight wire replies and
54 owned journal/object files contained no sentinel; captured stdout/stderr
contained zero runtime bytes. The actual held RAM buffer was zeroed, the private
Vault write was refused without a new object, and the fresh custodian had zero
live Sessions while reading closed metadata. The runner closed all owned
resources and its process exited successfully.

This qualifies the named API73 Session/Vault/restart surfaces only. Machine, workflow,
export and final release-package paths still need their own integrated evidence.
No real protected input, arbitrary encoding coverage or original T20 acceptance
is claimed from this fixture runner.
