# Participant purpose, custody and access model

Status: software design for a private research challenge, not a selected legal basis or approved privacy notice. Geography and controller have not been chosen. The release owner must record the applicable jurisdiction, lawful basis for each processing purpose, controller/processor roles, vendor/region, retention schedule and participant contact route before real media is collected. Brazil's ANPD explains that research by an organization outside the statutory “research body” category still needs an applicable legal basis; it also describes purpose-dependent retention and participant rights. See the [ANPD academic/research guide announcement](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-lanca-guia-orientativo-sobre-tratamento-de-dados-pessoais-para-fins-academicos), [ANPD FAQ](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes) and [rights guide](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares). If the project runs elsewhere, recheck local rules for that deployment.

## Purpose matrix for the first release

| Purpose | Participant choice and product behavior | Data allowed | Not allowed in this release |
| --- | --- | --- | --- |
| Deliver challenge and feedback | Present necessary processing notice at invitation/recording; service begins only under the approved basis and participant action. | Invite, exact case/session media, transcript, ratings, report and rights log, each with the approved retention class. | Employer access or silent research/model-training reuse. |
| Optional research analysis | Separate, unbundled choice before inclusion in a study extract; withdrawal route remains visible. | Pseudonymous cases, ratings, timing, error and approved outcome fields under registered protocol. | Contact/face images in default extract; inclusion after withdrawal. |
| Optional follow-up | Separate contact choice. | Contact vault and follow-up response only for the named study/time horizon. | Treating challenge use as follow-up permission. |
| Optional subgroup/access audit | Separate approved collection route, minimized categories and restricted access. | Only attributes necessary for the registered error/access analysis, where lawful. | Passing protected attributes to the scorer or making individual score adjustments without a studied method. |
| Model training or employer selection | No enabled choice or API in MVP. | None. | Using answers to train a general scorer or screen applicants from challenge participation alone. |

The interface places a short purpose statement next to the action it governs. A nearby expandable detail explains retention, recipients and rights, opens when relevant, and can be collapsed/reopened. The participant can view the complete notice and current choices later. Do not rely on a preselected opt-in checkbox. The lawful basis is a controller decision recorded separately from UI choice; a software checkbox is not a legal conclusion.

## Media minimization and protection

The premise offers a recorded video answer, but the proposed score uses **answer content**. The MVP captures video only for a stated pilot purpose and segregates it from the default transcript-based scorer. No facial, voice-emotion, identity-trait or behavior inference is permitted. Audio-only/text/diagram paths are documented for access and tested as response modes. If video adds no necessary evidence, the product decision should remove routine video storage rather than preserve it by habit. Do not expose raw media to reviewers who only need text. Any ASR/AI vendor receives the minimum approved data and has a recorded processor/retention arrangement.

Protect media with private object storage, encryption, short-lived grants, content hashes, narrow staff roles and access audit. Protect reidentification and contact separately. Backups inherit deletion/expiry policy. Research exports are purpose-filtered and time-limited; a download is recorded, and downstream revocation/withdrawal handling is explicit. Test a full participant deletion/correction path through media, transcript versions, scoring runs, reports, exports and backups before launch.

## Accessible assessment path

Build keyboard-operable controls, visible timer and status, readable captions/instructions and an alternative to recording when needed. The selected target accessibility standard and tests are a release decision; [WCAG 2.2](https://www.w3.org/TR/WCAG22/) supplies a current reference for perceivable media and operable interface requirements. A different response mode is recorded for analysis, never treated as a low score. Directly compare construct/criterion behavior across modes before claiming score equivalence. Accommodation contact must not require disclosure of a diagnosis to the scorer.

## Participant controls and support

From the challenge dashboard, participants can inspect notice/choice versions, correct a transcript, request their data, withdraw optional research use, request deletion under the applicable policy, challenge an inaccurate report and contact a human. Show request state and a receipt. A rights request may require identity verification and exception review, so the UI should state the next step and the approved response time rather than promise instant removal. A failed upload or ASR run offers recovery, not a zero rating.

## Separation from employment use

The first release has no employer dashboard, recruiter API, pass/fail endpoint or export of individual scores to hiring teams. A later employment product would need role-specific validation, access/accommodation review and exact employer/jurisdiction decisions. In the US, the [EEOC's selection-procedure guidance](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures) links employment-test use to job relevance, validation and disability accommodation; it does not approve this challenge. No statement here selects a jurisdiction for the MVP.
