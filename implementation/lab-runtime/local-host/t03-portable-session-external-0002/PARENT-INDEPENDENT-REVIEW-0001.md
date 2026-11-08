# Independent portable Session external-input review

PASS for this narrow repair. Reviewed the full diff from the selected API75 predecessor and the unchanged original capture verifier. The helper collects only closed path/SHA-256 external declarations from the four independently selected family manifests, requires each declaration to occur in that same manifest's exact file inventory, rejects conflicting digests and undeclared absolute union members, and passes the resulting explicit selection to the original `verify_inputs` implementation. It supplies no caller-selected path or broader filesystem permission.

A review finding about POSIX leading `//` locators was corrected in this successor; canonical absolute paths must have one leading slash. The original verifier still opens actual files/ancestors without following links and checks their exact bytes. The repair does not bypass Source, expiry, Actor, Reader or native-executable checks, and rewrites no signed record.

Independently reran all nine component cases normally and with optimization, including the actual pinned capture implementation's selected-external behavior, physical byte mutation and symlink refusals, missing declaration, conflicting SHA, unlisted external, relative/noncanonical locator and forbidden extra mode field. All passed. Actual Reader Service/Session construction and the learning lifecycle still require a fresh run on the combined selected native candidate.

Postimage SHA-256: `e785cac6101b8680b58ce17ceacbb5e61d151d6c0e8a5a3152a447ccc31a85b2`.
