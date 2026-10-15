# CyberAlchemy website deployment

**Status: deployed and verified**

Public entry: <https://cyberalchemize.com/>. The reviewed root entry redirects to the new Paper & crimson homepage at <https://cyberalchemize.com/governance-lab-series/index.html>.

The user explicitly requested replacement of the co-op homepage after the completed local review. Deployment used the existing co-op VPS route found in `../domainspec-core/projects/co-op-engine/infra/`, adapting the live configuration rather than running its broader historical full-deployment script.

Release: `lab-20261015T042807Z-a9aa3c2652f7`

Reviewed ZIP SHA-256: `3c67bc377be92144e8ce9daf3ce4b919f14ebd286eedee364131aeec4ebd0cbc`

Release manifest SHA-256: `a9aa3c2652f7197847a30b4ab8306d5374a56dac833ac0693be5bb9c15c029c6`

## Scope and preservation

Replaced `/srv/co-op-engine/site/index.html`; added the reviewed `governance-lab-series`, `craft-documentation-proposal`, `robot-learning-series`, release manifest and empty `.nojekyll` build marker. Added explicit Nginx locations for those three public directories and the manifest. The build marker is retained on disk but not publicly routed. No SPA fallback was added.

All eight preexisting secondary files are byte-exact. `/craft`, `/bella`, `/agent-orchestration`, `/agent-orchestration-guide` and protected `/domainspec/` retain their content and existing headers. Compose, routing environment and authentication file were unchanged. The same Nginx image was reused without pulling. Only `coop-engine-site` was recreated; every other container retained its identity, start time and image. Existing prior deployment backups were left intact.

## Proof

- Staged 1,244 files (1,236 reviewed release files plus eight preserved secondary files). Nginx configuration validated; every file was readable by the Nginx worker. Live files/configuration were checked for drift before cutover.
- All 1,235 non-hidden release files downloaded over verified HTTPS with byte-exact hashes and appropriate HTML/CSS/JavaScript/JSON/SVG MIME types. The existing route/body/header comparison passed across ten public/protected probes. Protected DomainSpec requests remain 401; unknown and non-public configuration paths remain 404.
- Final remote integrity verified every manifest entry and preserved configuration, credentials, secondary files and unrelated containers.
- Live Chromium covered 44 states across 11 surface families, 390/1440 widths and both themes: zero overflow, broken images, HTTP failures, CSP violations, console errors or runtime errors. Six real interaction checks passed: Actor search navigation, reading progress persistence, path destination, apex legacy fragment/theme preservation, hero theme/artwork, and keyboard model tabs. Four live accessibility states had zero violations.
- The preceding local release review passed 41,828 build checks plus Chromium, Firefox and WebKit verification. `live-browser.json`, `public-verification.json`, logs and screenshots supply deployment-specific evidence.

## Rollback

Private rollback copy: `/srv/co-op-engine/deployments/lab-20261015T042807Z-a9aa3c2652f7/rollback`. Original live directory/configuration were additionally retained alongside it as `live-before-site` and `live-before-nginx.conf`. Neither is in the web root. The private rollback folder contains original authentication/configuration material and must not be published or downloaded into the static artifact.

`remote-deploy.py` retains this release's explicit rollback operation. Before any later rollback, inspect current live state and obtain authorization for that new operational action; do not reuse this release's baseline as authority for an unrelated later change. The helper preserves original files and recreates only the existing static service.

No Git commit, push, repository-wide publication, database change or unrelated-service restart was performed. No physical-device or assistive-technology user session is inferred from the browser-engine checks.
