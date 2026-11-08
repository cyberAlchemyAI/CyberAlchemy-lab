# Local Runtime and CLI v1 extension

This candidate extension adds an explicit textual parser, local artifact writer,
rule/action runtime, injected SQLite and HTTP adapters, and local npm packaging
to the accepted general compiler predecessor. It does not change the predecessor
meaning or grant external effects.

The runtime boundary is fail-closed: rules, permissions, authority grants and an
adapter must all resolve before an action can run. HTTP hosts are allowlisted;
SQLite paths and generated output paths are caller-selected local paths.
