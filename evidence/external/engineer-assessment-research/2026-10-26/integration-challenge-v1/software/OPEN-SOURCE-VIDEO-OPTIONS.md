# Open source video capture and upload reuse

Status: **source review and implementation spike proposal, 2026-10-26**. No package has been installed, browser tested or selected for release. This review narrows the [integration stack](INTEGRATION-STACK.md) and [recovery contract](RECOVERY-PROTOCOL.md); it does not change administration or data-collection authority.

## Recommendation to test first

Build a synthetic-media proof with **Uppy Dashboard + Webcam + Audio + Tus client, and a self-hosted tusd S3 backend**. Uppy Webcam supports `video-audio`; its Audio plugin can cover a separately permitted audio response mode. Tus resumes a finished file after network interruption, and tusd stores completed uploads in S3-compatible storage. Keep the app's assignment, ten-minute server deadline, consent, case reveal, purpose, upload receipt, media verification and retention rules outside these libraries. [Webcam](https://uppy.io/docs/webcam/), [Audio](https://uppy.io/docs/audio/), [Uppy Tus](https://uppy.io/docs/tus/), [tusd](https://tus.github.io/tusd/), [tusd S3 storage](https://tus.github.io/tusd/storage-backends/aws-s3/).

This is the least custom **end-to-end candidate**, not an unconditional selection. Tusd adds an upload service and its documented pre-create authorization checks do not, by themselves, prove that the same user resumes a bearer upload URL. The app must bind upload creation to an assignment, constrain upload URL lifetime and access, reconcile completion idempotently, and verify the stored object before scoring. Tusd `post-finish` hooks are asynchronous; they cannot be the sole reliable job queue or final media receipt. [Tusd hooks and authorization caveat](https://tus.github.io/tusd/advanced-topics/hooks/).

For a participant-selected blurred recording, the [blur and assistance safeguard review](BLUR-AND-ASSISTANCE-SAFEGUARDS.md) proposes a processed canvas `MediaRecorder` stream, then Uppy upload. Uppy Webcam remains the unblurred capture candidate; the privacy mode needs a separate capture adapter.

## What each option covers

| Option | Reusable part | Fit and gap for this assessment | Decision |
| --- | --- | --- | --- |
| Uppy Webcam / Audio / Dashboard | Camera and microphone UI, recording, preview and file handoff; MIT-licensed Uppy | Strong pilot UI candidate. Documentation shows recording length but no assessment-grade server deadline/reveal/one-attempt contract. Mobile native camera behavior and forced stop must be tested. | **Spike first** for capture UI. |
| Uppy Tus + self-hosted tusd/S3 | Client retries/resume plus upload server and S3 storage | Best fully open source transport candidate. Adds service operations and bearer URL/auth integration. Completion still needs app verification and reconciliation. | **Spike first** for transport. |
| Uppy AwsS3 direct multipart | Browser-to-S3 part upload/retry, signing API | Avoids tusd. Current v6 `signRequest` flow has Uppy perform create, list, complete and abort S3 operations from the browser. That conflicts with the current app-owned `media-commit` rule unless we explicitly redesign custody and verification. Force multipart for pilot-sized files if used; default threshold is over 100 MiB. | Backup if transport service cost/complexity is worse and custody design is approved. |
| Uppy Golden Retriever | Some browser state and selected-file restoration | Default IndexedDB blob limit is 10 MiB; large-file Service Worker references are temporary and do not survive browser restarts. It does not promise recovery of a recording still in progress. | Optional aid only, never recovery guarantee. |
| videojs-record / RecordRTC | Browser recording libraries | Useful capture alternatives, but neither supplies the complete case/consent/upload/recovery system. Test only if Uppy capture UI cannot meet the timer or mobile mode requirements. | Reserve alternatives. |
| WebRTC server recorders, such as aiortc | Live media transfer and server recording | Adds live-network dependence, signaling and media-server operations to a task that can record locally then upload. It is a poor fit for offline capture continuity. | Do not add to first spike. |

Sources: [Uppy AwsS3](https://uppy.io/docs/aws-s3/), [Uppy v6 migration](https://uppy.io/docs/guides/migration-guides/), [Golden Retriever](https://uppy.io/docs/golden-retriever/), [videojs-record](https://github.com/collab-project/videojs-record), [RecordRTC](https://github.com/muaz-khan/RecordRTC), [aiortc](https://github.com/aiortc/aiortc).

## Contract the libraries do not own

1. `start` must precede case exposure, pin the server deadline and reveal schedule, and limit one scored slot to one verified media object. The UI must stop local capture at ten minutes and the backend must independently reject over-limit or invalid media. A recorder's display timer is not acceptance evidence.
2. Preserve offline capture only while the live tab, recorder and local storage remain healthy and no mandatory reveal is missed. A tab/device crash during recording is a technical review case. A completed blob may be uploaded or resumed later under the policy window; upload progress is not a valid answer receipt.
3. Admit no upload without a purpose-bound assignment, scoped authenticated creation, private key, bounded size and expiration. Treat the resumable upload URL as a bearer secret. Persist upload ID, attempt ID and status in the application's `upload_attempt` record.
4. On completion, the app checks its own assignment and upload state, object size, digest, container/codec, duration, audio presence and decodability before creating `media_object` and enqueueing ASR. Reconcile duplicate or missing hooks by polling; never trust a client “success” event or a storage ETag as the whole-file digest.
5. Keep deletion and withdrawal authoritative in the app and test cleanup of tusd metadata, partial uploads, final objects and derived transcripts. Changing uploader changes the implementation of recovery, not the participant's recovery policy.

## Synthetic spike and decision gate

Use synthetic ten-minute clips at the planned 75–150 MB range. Pin package/container versions and licenses in the spike lockfile. Test Chrome, Firefox and Safari on supported desktop/mobile devices, HTTPS permission denial, mobile camera handoff, exact stop at 10 minutes, lost API/storage connection while recording, tab close mid-recording, close/reopen after a finished capture, upload interruption/expiry, duplicate completion, wrong-assignment reuse, corrupt/truncated media, withdrawal mid-upload and ASR after verified receipt. Measure capture success, recoverable-upload rate, p95 upload wait, server CPU/network, residual orphan bytes and mode-specific failure rates.

Choose Uppy/Tus only if these checks preserve the existing [recovery invariants](RECOVERY-PROTOCOL.md) and private media custody. If the Webcam plugin cannot enforce the assessment capture flow, keep Uppy for upload UI and use a thin native `MediaRecorder` capture adapter. If tusd authorization or operating cost is unacceptable, keep the existing app-owned S3 multipart path. No production choice follows from documentation alone.
