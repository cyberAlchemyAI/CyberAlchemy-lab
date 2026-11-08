# Software stack and dependency coverage

Status: candidate design inventory. The [25 component records](component-index.json) identify named services, packages, browser APIs and tools. An option's `component_refs` link it to those identities. No component has a selected version, verified upstream publisher, license/terms decision or processor clearance. The [Integration Binding carrier](../carriers/integration-binding/v1/artifact.json) is prepared for an exact release choice, with **zero** binding instances.

| Software boundary | Current named candidate or design | Current record and next gap |
| --- | --- | --- |
| Browser capture and upload | Uppy Webcam/Tus, tusd, native browser media APIs, S3 multipart and SDKs | [IG-01/02](README.md) and component identities; browser/version, authorization and recovery checks remain open. |
| Private storage and transcription | S3, R2, Transcribe, faster-whisper and SDKs | [IG-03/04](README.md); region, legal recipient, terms, cost, language quality and deletion remain open. |
| Blur and assistance | MediaPipe, TensorFlow.js, LiveKit processor, Safe Exam Browser and browser APIs | [IG-05/06](README.md); device performance, preview/record parity, access burden and false-warning study remain open. |
| Frontend and structured state | React, TypeScript, provisional Mantine UI and PostgreSQL | A pinned local Mantine prototype builds, but production package selection, exact UI contract verification, database host, migrations and backup/restore require B0 decisions. |
| Media validation | ffprobe and a decoder test | ffprobe identity only; decoder image/version, malicious media isolation and output evidence remain open. |
| Local object store | S3-compatible test service | Service image and license deliberately unnamed in [integration stack](../../software/INTEGRATION-STACK.md); B0 must select and pin one before claiming conformance. |
| API framework, database driver and migrations | TypeScript server and PostgreSQL driver/migration tool | No vendor or package selected; create component identities and compare alternatives at B0. |
| Scoring model/provider | `ScorerAdapter` only | No model vendor selected; E03/E05 validity, data route, version, prompt, cost and failure checks precede an option review. |
| Identity, invitations and notifications | App modules and private invite flow | No external identity/email service selected; data flows, delivery failures and provider terms need review if externalized. |
| Hosting, secrets and observability | Separate environments, audit log and outbox design | No cloud host, secret manager, telemetry vendor or queue product selected; deployment and incident design remain open. |

For each named technology, resolve upstream identity, exact package/service version or browser support range, license/terms, security and maintenance status, data processed and sent, region and legal recipient where applicable, accessibility, cost, operating owner and exit or replacement route. An owner selection follows the option review and verification evidence; the release binding then pins the actual lockfile or service version, environment, configuration digest, data route, decision, approval and rollback. A dependency scan or lockfile can supply evidence for that binding, but does not itself authorize one.

For a managed vendor, the product name in a Technology Component record does not identify the contracting legal entity. A future processor/supplier review must bind that entity, data and subprocessors, region, retention/deletion terms, security evidence and exit obligations to an attributable owner decision. The Lab's `Contract/v1` and `Decision/v2` are candidate routes for the resulting governed agreement and approval, subject to their owners and exact carrier fit. No such contract or decision record exists here. Open source license review is also a separate release gate; a package name or repository link is not proof of license entitlement.

The Lab's [Implementation/v1](../../../CyberAlchemy-lab/authority/artifact-types/implementation/v1/schema.json) can represent a realized capability after a build. This project's component inventory and release binding answer narrower package, service and deployment questions. The two local Artifact Type Requests remain unadmitted.
