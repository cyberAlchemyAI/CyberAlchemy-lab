# Manual browser and accessibility review

Use this with the portable documentation release. This is an evaluator's checklist, separate from the newcomer study. Keep the study facilitator's answer rubric separate from participants.

Record the release ZIP digest from `documentation-release.json`, operating system, browser and version, actual screen reader and version, and delivery mode (extracted local files or localhost). Note observed wording, keyboard steps, failures and screenshots where relevant. A browser engine's accessibility tree does not substitute for what a screen reader announces.

## Screen-reader session

Use a screen reader you can operate, such as NVDA, VoiceOver, Narrator or Orca. Do not count an automated accessibility scan as this session. Start at `governance-lab-series/start-here.html` in the extracted release.

| Task | What to inspect | Evidence to record |
| --- | --- | --- |
| Find the practical guides | Navigate landmarks, headings and links to **Prepare an assessment**. | Navigation names, heading order, whether the destination and current topic are understandable. |
| Search with the keyboard | Focus **Search all documentation**, enter **Delegation**, read the result count, reach a result and activate it. Press Escape from results on a second attempt. | Actual announcements, result names, destination, focus return and whether the popup stays closed. |
| Read a formula | Open the guide's **Authority and meaning**, then **Read the full definition**. Read the completeness expression and its symbol explanations. | Whether S, A, F and E can be associated with snapshot, account, filters and output, and the plain-language criterion is recoverable. |
| Read a table | Open **Follow an incident** and the assessment table. Move through its rows and columns. | Announced row/column headings and whether observation, cause, impact and recovery remain distinguishable. |
| Inspect an exact record | Open **Complete examples**, choose Work and expand **Read the complete specimen**. | Disclosure state, code reading, invented identity, candidate standing and the one-field contrasting failure. |
| Read the system map without the picture | Open **Interactive system map**, choose Governance and use **Relationship list**. Change the governance perspective and select a concept. | Control names/states, concept feedback, ordered relationships and whether feedback is discoverable. |
| Inspect a Craft diagram | Open Craft's **Definition** topic and its visible diagram opener; use the dialog, then Escape. | Dialog name, image description, keyboard scrolling, close behavior and return to the opener. |
| Check zoom and narrow layouts | Repeat search and navigation at 200% and 400% browser zoom. | Any inaccessible controls, lost text or focus obscured by the header. Record two-dimensional diagram scrolling separately. |

For each task use **worked / worked with difficulty / failed / not attempted**. Describe the observed failure rather than inferring one from an automated warning. When a failure is fixed, repeat the same task against the new artifact and identify that revision.

## Actual Safari session

Use Safari on an available macOS or iOS device and record its actual version. The existing Linux WebKit results remain a separate evidence source.

1. Extract the whole archive and preserve both documentation directories. Check local-file delivery where supported; record any platform restriction. A localhost run can be an additional, separately identified delivery check.
2. Visit the guide, a practical page, an expanded essay, a reference entry and Craft. Confirm direct anchors and browser Back/Forward.
3. Search for **what lets an agent act?** from the guide, library and Craft. The reviewed destination is **Resume agent work → Check current authority**.
4. Expand the Work specimen. Navigate the system map's perspectives and relationship list. Open and dismiss a Craft diagram.
5. Visit the legacy authority, provenance and lifecycle pages. Confirm their canonical guide destinations and preserved deep links.
6. Use mobile navigation where applicable, text enlargement and keyboard access where a keyboard is available. Report unavailable hardware rather than recording it as a pass.

## Report and decision

Send the completed checklist or notes with the release/environment identifiers. The maintainer should map each observed barrier to its page and control, reproduce it where possible, fix it or record an explicit open question, and repeat the affected task. These observations are specific to their environment; they do not establish universal accessibility or statistical reader comprehension.
