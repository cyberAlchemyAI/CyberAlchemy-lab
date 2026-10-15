# Real-world problems behind the Craft article

Research notes · 10 October 2026

These are primary-source engineering accounts, incident analyses, API contracts and research studies. Historical accounts describe the system at the reported date. API documentation describes a version-scoped contract rather than an incident. The proposed design questions below are our interpretation for the article, not the companies' claims about Craft.

## 1. Architectural boundaries that are easy to cross

**Case:** Shopify's modular-monolith work, 2019, with a follow-up in 2020.

**Reported:** Shipping and checkout responsibilities had become tightly coupled. Shopify described component interfaces and data ownership, plus Wedge tooling that identified cross-component access and coupling. Its later account emphasizes design tradeoffs, developer behavior and gradual change.

**Design question:** Which dependencies are permitted, through which public contracts, and who owns the data?

**Article use:** Ground the distinction between organizing files and constraining interactions.

Sources: [Deconstructing the Monolith](https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity); [Under Deconstruction](https://shopify.engineering/shopify-monolith).

## 2. A business process that is not simply complete or incomplete

**Case:** Stripe's documented PaymentIntent lifecycle.

**Reported:** A payment can require customer action, remain processing for an asynchronous method, or succeed. These states have different consequences for the payment flow.

**Design question:** Which state permits fulfillment, and which observation establishes that state?

**Article use:** Explain why a domain model needs explicit lifecycle distinctions.

**Boundary:** This is a production API contract, not a reported merchant incident. A complete payment integration is not claimed as part of the capacity fixture.

Source: [Payment and Setup Intent lifecycles](https://docs.stripe.com/payments/paymentintents/lifecycle).

## 3. A retry whose identity affects its effects

**Case:** Stripe API v1 idempotency.

**Reported:** After endpoint execution begins, v1 retains a request's first response under its key, including error responses. Reuse checks parameters. Keys can be pruned after at least 24 hours; reuse after pruning can produce a new request. API v2 has different documented retry semantics.

**Design question:** What makes two attempts the same operation, and how do retention and failure affect that promise?

**Article use:** Give identity and lifecycle contracts an everyday purpose.

Source: [Idempotent requests](https://docs.stripe.com/api/idempotent_requests).

## 4. A rule that passes checks but exceeds operational bounds

**Case:** Cloudflare's 2 July 2019 outage.

**Reported:** A WAF regular expression caused CPU exhaustion. Contributing factors included removed protection, missing CPU-consumption testing and global routine rollout without staging.

**Design question:** Which resource and release constraints must hold, and which checks establish them?

**Article use:** Explain that a passing delivery process only covers the properties it actually examines.

**Boundary:** A typed model or deterministic compiler alone does not establish execution cost or safe deployment.

Source: [Cloudflare postmortem](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/).

## 5. A deployment that contains conflicting versions of meaning

**Case:** Knight Capital's August 2012 incident; SEC findings published in 2013.

**Reported:** New code was not copied to one of eight servers. A reused flag triggered old Power Peg behavior there. Deployment review and control deficiencies contributed to the failure.

**Design question:** Which artifact and flag meanings are valid on each target, and how is retirement checked?

**Article use:** Connect source and artifact identity to actual deployment state.

**Boundary:** This is a lifecycle example, not evidence that Craft would have prevented the incident.

Source: [SEC findings](https://www.sec.gov/Archives/edgar/data/1569391/000119312513401173/d613486dex101.htm).

## 6. Infrastructure recovery that violates application assumptions

**Case:** GitHub's October 2018 incident.

**Reported:** A brief network partition triggered database failover. The resulting cross-region topology was incompatible with application latency expectations, and writes diverged between sites. GitHub prioritized data integrity during recovery.

**Design question:** Which topology transitions are admissible for the application, given replication and latency constraints?

**Article use:** Explain that an infrastructure transition and an application-safe transition can have different contracts.

**Boundary:** Modeling a transition does not prove a live failover safe. Observations and provider assumptions remain necessary.

Source: [GitHub post-incident analysis](https://github.blog/news-insights/company-news/oct21-post-incident-analysis/).

## 7. A backup procedure whose existence does not establish recoverability

**Case:** GitLab's January 2017 database outage.

**Reported:** Regular logical backups were failing because of a PostgreSQL tool-version mismatch, and failure emails were rejected. Recovery relied on a snapshot created roughly six hours earlier. The report identified missing ownership of regular recovery testing.

**Design question:** What evidence establishes that this backup is current, usable and restorable with this toolchain?

**Article use:** Distinguish configured capability, artifact existence and demonstrated recovery.

Source: [GitLab postmortem](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/).

## 8. An API change that requires coordinated consumer evolution

**Case:** Stripe's API release-process announcement, October 2024.

**Reported:** Stripe distinguished breaking major releases from compatible monthly feature updates, with associated SDKs, documentation and upgrade guidance.

**Design question:** Which consumers depend on a contract, and which changes require migration rather than an ordinary update?

**Article use:** Ground successor models, compatibility and consumer impact in a familiar development lifecycle.

**Boundary:** This describes the announced policy at that time, not a claim that today's schedule is identical.

Source: [Stripe release-process announcement](https://stripe.com/blog/introducing-stripes-new-api-release-process).

## 9. Agent sessions that lose continuity or overstate completion

**Case:** Anthropic's long-running agent engineering report, November 2025.

**Reported:** In its application-building experiments, agents left undocumented partial work, later sessions had to reconstruct progress, and completion was sometimes claimed without adequate end-to-end evaluation.

**Design question:** Which requirements, decisions and observations must survive a handoff, and what evidence permits a completion claim?

**Article use:** Ground the agent continuity problem. Local guard changes, duplicated rules and changed test expectations in the draft are illustrative review scenarios, not reported incidents from this source.

Sources: [Long-running agent harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## 10. Local solutions that accumulate structural debt across changes

**Case:** SlopCodeBench v2 (May 2026 preprint), CodeTaste (ICML 2026), and SWE-CI v4 (April 2026 preprint).

**Reported:** SlopCodeBench evaluates agents repeatedly extending their own solutions under evolving specifications. It tracks redundant code and concentrated complexity, reporting degradation across many trajectories; quality-oriented instructions improve the starting code without eliminating later degradation. CodeTaste reports stronger performance when refactorings are specified than when agents must identify the human-selected improvements. SWE-CI examines repeated repository maintenance through development and CI rounds.

**Design question:** Does today's implementation leave responsibilities clear enough for the next change, and how do shortcuts affect later work?

**Article use:** Define brittleness through accumulated design shortcuts. Extend the capacity scenario through reservation, a background caller and retries, showing how copied rules, mixed responsibilities and exceptions can compound.

**Boundary:** The studies measure selected tasks and proxies or contracts, rather than all dimensions of maintainability. They do not establish that all agent-built projects fail or that Craft reduces debt. The capacity extension is our illustrative design analysis, beyond the existing compiled fixture.

Sources: [SlopCodeBench v2](https://arxiv.org/abs/2603.24755v2); [CodeTaste](https://proceedings.mlr.press/v306/thillen26a.html); [SWE-CI v4](https://arxiv.org/abs/2603.03823v4).

## 11. Related research: sensitivity to task presentation

**Case:** ReCode (ACL 2023) and *A Jagged Frontier* (August 2026 preprint).

**Reported:** ReCode evaluates code generation using transformations of descriptions, names, syntax and formatting intended to retain meaning. The later study evaluates repository-level agents under intended behavior-preserving transformations, including control-flow rewrites, identifier changes and inert code. Effects vary by configuration; its qualitative analysis includes mislocalization and distraction by transformed code.

**Design question:** Does an agent preserve the required decision when the task or code looks different but the intended meaning stays constant?

**Article use:** Define brittleness and extend the capacity walkthrough with two logically equivalent instructions. Explain how structured contracts separate construction from conversational wording and how exact artifact bindings support investigation.

**Boundary:** ReCode is a code-generation study, not a repository-agent study. The later work is a preprint; its transformation validation is test-bounded rather than a universal proof of equivalence. Neither measures Craft. The capacity scenario and proposed evaluation are our design interpretation. Exact artifact comparison can reject a behavior-preserving rewrite because it differs from the selected implementation; it is not an equivalence checker.

Sources: [ReCode](https://aclanthology.org/2023.acl-long.773/); [A Jagged Frontier](https://arxiv.org/abs/2608.18389); [full text and observed failure patterns](https://arxiv.org/html/2608.18389v1).

## How to use these examples

Use short examples where they clarify a principle. Keep the capacity decision as the continuous model-to-code walkthrough. The main draft now uses Shopify for architecture, Stripe for state and retry meaning, Cloudflare for check coverage, and Knight Capital for deployment identity.

GitHub, GitLab and API-version evolution are available for later expanded articles. Each needs enough context to avoid presenting a complex incident as a single missing model field.

The relationship to Craft is a design interpretation: these cases identify obligations worth representing, observing and reviewing. Actual compiler or enforcement coverage must be established separately for a selected profile.
