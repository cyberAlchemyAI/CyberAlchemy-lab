# Hackathon v1.1 — confirmed schedule and categories

Status: **published and verified** at <https://cyberalchemize.com/governance-lab-series/hackathon.html>.

## User-confirmed schedule and selection

All times are Brasília (UTC-3), in 2026.

- Registration: October 16 at18:00 through October23 at23:59:59. The existing18:00 opening time was retained.
- Project month: October24 at00:00 through November23 at23:59:59.
- Voting: November24 at12:00 through November25 at18:00.
- Provisional results: November25 at18:30; reports by20:00; final results by23:59:59.
- One new solo project in exactly one category. Studio front-end is a new Lab/Craft Studio interface, with visual invention and useful UX features in service of human–machine ergonomics. Open projects retains the original challenge and all six inspiration prompts.
- One US$200 subscription reimbursement prize per category (US$400 total maximum). Each participant submits one final ballot with one choice or abstention per category. No self-votes; choices are validated independently. Ties are resolved within their category, and unawarded prizes do not transfer.

## Maintained changes

Updated hackathon.json, the event renderer and Python/browser status logic, event/home templates, category layout, README, and the PDF/Word rules. Registration and building now have independent windows, preventing registration staying open throughout the project month. Scheduled dates do not establish form readiness; missing forms and unverified ballots remain unavailable.

Added editable hackathon-rules.json plus tools/build_hackathon_rules.py. Both downloads are generated from the same text/config and the normal build rejects stale source, schedule or download hashes. The six-page PDF and Word edition contain the same73 paragraphs. Rulesv1.1 highlights the schedule, categories and voting revision; existing age, solo/new-project, ownership, privacy and reimbursement terms remain.

Added maintained hackathon-forms.json and tools/prepare_hackathon_forms.py, refreshing FORMS-COPY.txt and GOOGLE-FORMS-SETUP.html consistently (three forms,22 questions). The project form requires one category; the ballot has one multiple-choice question per category, each with Abstain. These local instructions do not change organizer-owned Google Forms. Registration/submission/gallery/voting URLs remain null.

Calendar now contains seven UTC events, including separate registration-close and build-start reminders. Previously published event UIDs are preserved, sequence increments to1, and long lines are folded while retaining their values. Historical dates inside those opaque UIDs are identities, not current event dates.

## Verification

- Normal staged build:41,828 checks passed;498 HTML routes and806 search entries. Existing routes/hrefs/fragment IDs preserved. Intentional prose changes are restricted to the homepage announcement and event page. All454 formal record bodies,14 runtime articles and552 captured source files remain exact. The six original inspiration texts are exact.
- Six Python unit tests check registration/build boundaries, pending/unverified actions, calendar UTC timestamps/UID compatibility/line folding, stale-rule rejection and corrupt-download rejection. Forty Python/browser phase/action comparisons pass. All59 curated search queries and delivery/parity regressions pass.
- PDF/DOCX comparison:73 paragraphs agree, old schedule wording absent, revised category/vote/prize terms present. First/last PDF pages rendered and first-page visual inspected. Impeccable's UI detector reported zero findings.
- Local and live browser review each covered16 states (320/390/768/1440 widths, both themes, home/event), plus no-script reading, rendered future phases and Studio search. No overflow, broken images, stale visible schedule, runtime errors or accessibility violations. Five interaction/content checks and two accessibility states passed in each run. The final post-review build changed only calendar line folding; UI bytes were otherwise unchanged before the live confirmation.
- All1,235 public release files downloaded via verified HTTPS match the release, including both rules downloads and the calendar. Ten old public/protected route checks pass; DomainSpec remains401 to anonymous visitors. Nginx, Compose, credentials, eight secondary files, other container identities/start times and static image remain unchanged. A previous hashed event stylesheet is retained for compatibility, giving1,245 installed files including preserved secondary content.

## Release and rollback

Release: `lab-20261015T051446Z-7708a94f4cf5`.

ZIP SHA-256: `8e0f0c886dee72e91cf813f3005f7435ed5b819a1bf82d8515dd3ef335a432cb`.

Manifest SHA-256: `7708a94f4cf50ddfd219a5e80b617fb048634ad5066316f7bd71ad0202b97f78`.

Private rollback: `/srv/co-op-engine/deployments/lab-20261015T051446Z-7708a94f4cf5/rollback`. Prior rollbacks remain; no Git commit/push, participant-data access, Google Forms mutation or unrelated-service restart occurred. Only the static service was recreated with its existing image. Browser-engine checks are not physical-device, human usability or actual-ballot-control verification.

Evidence: RECEIPT.json and live results here; local browser, document, source-before and preservation evidence under output/playwright/hackathon-20261015/.
