# Mantine experience prototype

Status: runnable **design prototype**. This uses React, TypeScript, Vite and Mantine. It makes the six-stage participant journey explorable with themed controls. All choices are ephemeral React state; there is no account, recording, upload, analytics, API or persisted data.

```bash
cd /home/vlad_/projects/engineer-assessment/design/mantine-prototype
npm ci
npm run dev -- --port 5175 --strictPort
```

Open `http://127.0.0.1:5175/` while the server runs. `npm run build` performs TypeScript and production bundle checks. The visual comparison is the earlier [static HTML concept](../prototype.html). The [option review](../COMPONENT-LIBRARY-REVIEW.md) explains the provisional choice, boundaries, alternatives and challenge triggers.

The candidate theme is centralized in [theme.ts](src/theme.ts) and reads the action color and font family from the [token source](../tokens.json); [prototype.css](src/prototype.css) carries layout and the custom recording-stage presentation. Before product implementation, generate the complete theme and CSS mapping from tokens with drift checks, review real mobile/browser states, and keep all recording, rights and scoring logic under their existing contracts.
