# Run the local Lab fixture product

From a checkout of this branch on WSL with Python 3, Docker Engine and Docker Compose available, run:

```bash
bash implementation/lab-runtime/local-host/run-local-product.sh
```

The build downloads a digest-pinned Python base and hash-locked wheels. The command stages and verifies the selected public source package, builds a unique image, runs two isolated containers, and removes its temporary build context and image tag at exit. Fixture execution has no network, host checkout mount, persistent volume or exposed port.

Success prints both `CyberAlchemy Lab — local Source → Reader → Mapper → Context fixture: PASS` and `CyberAlchemy Lab — local Work journey: PASS`, then exits zero. The first journey signs and reads a disposable Source, maps 15 nodes and 10 edges, and binds 25 Context references. The second reviews a Work proposal, refuses an altered signed proposal, commits one local sequence, proves idempotent retry and fresh-process replay, and closes and erases its short-lived Session. Both report zero external effects.

This command demonstrates the smaller runnable fixture slice. For the integrated 34-operation local runtime, fresh artifact installation and operator commands, use [LOCAL-ENGINEERING-RELEASE.md](LOCAL-ENGINEERING-RELEASE.md). The fixture slice has no protected Source8 credentials, owner admission or canonical release effect. Its inputs and behavior are pinned by `source-manifest.json`, `package-release.json`, the Dockerfile, the wheel lock, and the runtime verifier in this directory.
