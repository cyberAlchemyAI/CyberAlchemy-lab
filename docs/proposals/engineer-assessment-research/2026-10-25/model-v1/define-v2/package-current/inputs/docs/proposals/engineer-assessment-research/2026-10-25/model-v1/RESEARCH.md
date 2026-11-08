# Research baseline and inquiry program

Status: scoped source scan, not a systematic review. Record search dates, inclusion decisions, study populations, measures and conflicting results in the evidence ledger before making a literature-derived claim. Distinguish peer-reviewed evidence, official guidance and vendor statements.

## Questions and competing explanations

| ID | Question | Rival explanation or failure mode |
| --- | --- | --- |
| EA-RQ-01 | Do unusual cases reveal job-relevant creativity, analysis and ingenuity? | Riddle familiarity, language fluency, coaching, or test-taking confidence explains scores. |
| EA-RQ-02 | Can three ten-minute answers reliably distinguish candidates near the decision threshold? | Case specificity and short sampling dominate stable skill variance. |
| EA-RQ-03 | Do scores predict later role performance better than an equal-time comparator, and as well as a longer pipeline? | Scores track existing credentials or interview polish without incremental value. |
| EA-RQ-04 | Which evidence is lost or distorted through ASR, video, time limits and AI scoring? | Accent, disability, bandwidth, language, stress or rater artifacts drive score differences. |
| EA-RQ-05 | Does the cooperation case predict cooperative behavior outside a narrated hypothetical? | Socially desirable answers and game knowledge create construct-irrelevant variance. |
| EA-RQ-06 | Are the challenge's feedback and employer's selection value worth participant burden and operating cost? | An accessible short work sample provides the same value more cheaply. |

## Source map and bounded reading

| Evidence | What it informs | Boundary |
| --- | --- | --- |
| [OPM job analysis](https://www.opm.gov/policy-data-oversight/assessment-and-selection/job-analysis/) and [structured interviews](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/structured-interviews/) | Start from role work and anchored, consistent scoring. | Public-sector guidance, not this product's validity study. |
| [Sackett et al. 2022](https://pubmed.ncbi.nlm.nih.gov/34968080/) | Updated validity estimates and correction practices. | Broad selection literature cannot validate these three cases. |
| [Thorsteinson 2018](https://doi.org/10.1111/joop.12186) | Interview length is an empirical variable. | No result establishes this exact three-session design. |
| [Short medical MMI study](https://pubmed.ncbi.nlm.nih.gov/26873767/) and [12-station MMI study](https://pubmed.ncbi.nlm.nih.gov/19659490/) | Short multi-case interviews can be studied; station count and case variance matter. | Medicine and academic/clinical outcomes do not transfer to engineering hiring. |
| [Wingate et al. 2025](https://doi.org/10.1111/ijsa.12494) | Construct and question-level scoring deserve explicit tests. | Aggregate structured-interview findings do not identify our constructs. |
| [Amabile's consensual assessment](https://doi.org/10.1037//0022-3514.43.5.997), [divergent-thinking scoring](https://doi.org/10.1002/j.2162-6057.2011.tb01081.x), [engineering novelty and requirement satisfaction](https://www.cambridge.org/core/journals/ai-edam/article/systematic-approach-to-assessing-novelty-requirement-satisfaction-and-creativity/3385C36C4678F2223535AC90D681AD5D), [insight assumptions](https://pubmed.ncbi.nlm.nih.gov/18411549/) | Separate novelty, useful constraint handling, analysis and revision; compare expert judgments. | Riddle success alone is not workplace creativity. |
| [Koenecke et al. ASR disparities](https://pubmed.ncbi.nlm.nih.gov/32205437/) | Audit transcription errors across speech groups and modes. | Historical systems and population; remeasure our actual stack. |
| [Raghavan et al. hiring algorithms](https://doi.org/10.1145/3351095.3372828) | Challenge vague vendor bias/validity claims. | Qualitative study, not our effect estimate. |
| [EEOC selection guidance](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures), [EEOC disability guidance](https://www.eeoc.gov/laws/guidance/visual-disabilities-workplace-and-americans-disabilities-act), [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689), [NYC AEDT rules](https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page), [Brazil ANPD rights](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares) | Flag deployment-specific legal and access reviews. | Exact obligations depend on jurisdiction and use; recheck before deployment. |
| [NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) and [AERA/APA/NCME Standards](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf) | Risk and measurement evidence structure. | Frameworks do not certify a product. |
| [HackerRank developer report](https://embed.hackerrank.com/reports/developer-skills-report-2025) | Industry pain and candidate preference hypotheses. | Vendor survey, not independently established validity. |

## Evidence rules

Every finding records source identity, exact design, sample, role/outcome, uncertainty, limitations and relevance judgment. Do not pool medical and engineering coefficients as though populations match. Do not convert human/AI agreement into prediction. Separate convergent construct evidence from outcome prediction, and subgroup score distributions from subgroup error or adverse impact. Keep negative and null results in the ledger. Register analysis and stopping rules before outcome data are examined; label exploratory analyses plainly.
