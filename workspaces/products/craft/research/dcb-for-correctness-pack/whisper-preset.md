# Whisper Preset — Research Finding, Victor's Voice

Preset ID: `domainspec_v2_research_finding_victor`
Transport: research finding explainer (peer-to-peer technical write-up)
Status: active draft preset
Voice source: `business-philosopher/write-style.md` + `discovery/persona.md`
First use: `dcb-for-correctness-pack/DCB-FOR-CORRECTNESS.victor.md`

## Purpose

Explain a research finding to a technical peer who knows the adjacent field but
not our system. The reader should arrive at the finding themselves — when the
tool is right, when it's overkill — instead of being handed a verdict.

This preset exists because the first DCB write-up came out too polished:
thought-leadership prose, slick lines that sound earned but hide the path, an
abstract term ("freshness") used before it was ever grounded in a real moment.
This preset is the correction.

## Resonance Core

- Voice: peer at a whiteboard. Plain, declarative. One claim per sentence.
- Energy: calm and a little self-critical. We part-deflate our own favored tool.
- Emotional residue: "I see exactly when I'd reach for this, and when I wouldn't."
- Value signal: claim ≤ proof. We admit when the thing we were excited about is
  the wrong tool for most of the job.
- Forbidden feel: thought-leadership, TED-talk cadence, guru tone, aphorisms,
  "imagine if…" staging, hype.

## Relevance Core

- Primary reader: knows DCB / event sourcing well. Does not know DomainSpec.
- Reader state: technical, skeptical, will catch hand-waving. Wants to know
  exactly when to reach for this and when not to.
- Authority mode: reporting what we built and observed. Not prescribing.
- Assumptions: reader knows read-sets, append conditions, tags, optimistic
  concurrency. Reader does not know our spec/validator machinery.
- Objections to answer up front:
  - "Isn't this just cache invalidation?"
  - "Why not just rerun the check?"
  - "Is this proven, or a toy?"

## Trajectory Core

- Objective: show that DCB is the wrong tool for proving correctness and the
  right tool for one narrow thing — guarding a decision against facts that moved
  after it read them.
- Opening policy: open with a concrete moment, not the abstract frame. The
  attribution-drift case (a number restated from R$100k to R$75k a day later) is
  the canonical opener. Define "freshness" through that moment, not before it.
- Structure: real case → what freshness actually is → the 90-second
  system primer → the finding (DCB only earns its keep on facts you can't
  rerun) → the toy we ran → honest boundaries → one-paragraph summary.
- Ending policy: one clean statement plus, at most, one labeled open question.
  No motivational close, no call to greatness.

## Diction

Prefer:

- "the number moved", "stale", "read it last Tuesday", "you can't rerun a human's
  approval", "rerunning gives a different answer", "the fact is owned by someone
  else"
- plain verbs: check, reject, read, change, rerun, accept

Avoid:

- "underwrite", "the seam where X and only X adds value", "earns its keep"
  (once, maybe — not as a refrain), "thesis", "uniquely", thought-leader nouns
- any sentence that would survive on a slide with no context (that's the
  aphorism test from write-style.md §G — cut it)
- restating the same insight three times in publish form (let reframing run in
  the draft, keep the sharpest one)

## Style Rules

- Short declaratives. Break every 3-clause chain into two sentences.
- Concrete before abstract. No more than one abstract paragraph before a
  concrete one (write-style.md §E).
- Commit fully on what we built and observed (the toy, the attribution case).
  Hedge openly only on the generalization to "this is how correctness should
  work everywhere."
- Never narrate the rhetorical move. Make it and move on.
- Ground "freshness" in a real fact that changed before using it as a term.

## Validation Checklist

- The piece opens on a concrete moment, not a definition.
- "Freshness" is grounded in a real example before it's used as jargon.
- At least one real case the reader can map to their own work appears early.
- No aphorism survives the slide test.
- DCB is honestly deflated for the deterministic-fact case, not oversold.
- Claim ≤ proof: the toy is called a bounded witness, not a proof.
- A skeptical DCB reader's three objections are answered.
- No sentence sounds like a lectern.
