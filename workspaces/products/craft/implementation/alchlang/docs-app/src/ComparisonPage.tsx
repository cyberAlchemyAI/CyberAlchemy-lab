import { useEffect, useMemo, useState } from "react";
import {
  canonicalJson,
  comparisonEvidence,
  comparisonPairs,
  dimensionDetails,
  observationComplete,
  preferenceDimensions,
  reviewComplete,
  sha256,
  variantDetails,
  type PairObservation,
  type PreferenceChoice,
  type PreferenceDimension,
} from "./comparison";

const storageKey = "alchlang-pareto-review-v1";

function readStoredObservations(): Record<string, PairObservation> {
  try {
    const parsed = JSON.parse(localStorage.getItem(storageKey) || "{}");
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function VariantFrame({ side, variant }: { side: "A" | "B"; variant: keyof typeof variantDetails }) {
  const details = variantDetails[variant];
  return (
    <article className="comparison-variant">
      <header>
        <span>{side}</span>
        <div><strong>{details.label}</strong><p>{details.treatment}</p></div>
        <a href={`?variant=${variant}#quickstart`} target="_blank" rel="noreferrer">Open ↗</a>
      </header>
      <iframe src={`?variant=${variant}#quickstart`} title={`Variant ${side}: ${details.label}`} loading="eager" />
    </article>
  );
}

function ChoiceRow({
  dimension,
  value,
  onChange,
}: {
  dimension: PreferenceDimension;
  value?: PreferenceChoice;
  onChange: (choice: PreferenceChoice) => void;
}) {
  const details = dimensionDetails[dimension];
  return (
    <fieldset className="comparison-choice">
      <legend><strong>{details.label}</strong><span>{details.prompt}</span></legend>
      <div>
        {(["left", "tie", "right"] as const).map((choice) => (
          <button
            type="button"
            key={choice}
            className={value === choice ? "is-selected" : ""}
            aria-pressed={value === choice}
            onClick={() => onChange(choice)}
          >{choice === "left" ? "A" : choice === "right" ? "B" : "Tie"}</button>
        ))}
      </div>
    </fieldset>
  );
}

export function ComparisonPage() {
  const [observations, setObservations] = useState<Record<string, PairObservation>>(readStoredObservations);
  const [pairIndex, setPairIndex] = useState(() => {
    const firstIncomplete = comparisonPairs.findIndex((pair) => !observationComplete(readStoredObservations()[pair.id]));
    return firstIncomplete < 0 ? 0 : firstIncomplete;
  });
  const [exportDigest, setExportDigest] = useState("");
  const pair = comparisonPairs[pairIndex];
  const observation = observations[pair.id] || { pairId: pair.id, choices: {}, note: "" };
  const completed = comparisonPairs.filter((item) => observationComplete(observations[item.id])).length;
  const allComplete = reviewComplete(observations);
  const evidence = useMemo(() => comparisonEvidence(observations), [observations]);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(observations));
    setExportDigest("");
  }, [observations]);

  function updateChoice(dimension: PreferenceDimension, choice: PreferenceChoice) {
    setObservations((current) => {
      const latest = current[pair.id] || { pairId: pair.id, choices: {}, note: "" };
      return {
        ...current,
        [pair.id]: {
          ...latest,
          choices: { ...latest.choices, [dimension]: choice },
        },
      };
    });
  }

  function updateNote(note: string) {
    setObservations((current) => {
      const latest = current[pair.id] || { pairId: pair.id, choices: {}, note: "" };
      return { ...current, [pair.id]: { ...latest, note } };
    });
  }

  function resetReview() {
    if (!window.confirm("Clear all six comparison observations?")) return;
    setObservations({});
    setPairIndex(0);
  }

  async function downloadEvidence() {
    const canonical = canonicalJson(evidence);
    const digest = await sha256(canonical);
    const receipt = { ...evidence, evidence_sha256: digest };
    const blob = new Blob([`${JSON.stringify(receipt, null, 2)}\n`], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = `alchlang-human-comparison-${digest.slice(0, 12)}.json`;
    anchor.click();
    URL.revokeObjectURL(href);
    setExportDigest(digest);
  }

  return (
    <div className="comparison-shell">
      <a className="skip-link" href="#comparison-content">Skip to comparison</a>
      <header className="comparison-topbar">
        <a href="?view=overview#overview" className="comparison-brand">AlchLang <span>Human review</span></a>
        <div className="comparison-progress" aria-label={`${completed} of ${comparisonPairs.length} comparisons complete`}>
          <span><i style={{ width: `${(completed / comparisonPairs.length) * 100}%` }} /></span>
          <strong>{completed} / {comparisonPairs.length}</strong>
        </div>
        <button type="button" onClick={resetReview}>Reset review</button>
      </header>

      <main id="comparison-content">
        <section className="comparison-intro">
          <div>
            <p>PAIRWISE PARETO REVIEW · MATCH {pairIndex + 1} OF {comparisonPairs.length}</p>
            <h1>Compare the experience,<br /><em>one trade-off at a time.</em></h1>
          </div>
          <aside>
            <strong>Review task</strong>
            <p>Find the complete backend-type reference, identify how SFOL business rules remain deterministic, and locate the mini workspace. Then record which treatment better supports the task.</p>
          </aside>
        </section>

        <section className="comparison-frames" aria-label={`Comparison ${pairIndex + 1}`}>
          <VariantFrame side="A" variant={pair.left} />
          <VariantFrame side="B" variant={pair.right} />
        </section>

        <section className="comparison-form" aria-labelledby="comparison-form-title">
          <div className="comparison-form-heading">
            <div><p>YOUR OBSERVATION</p><h2 id="comparison-form-title">Which treatment works better?</h2></div>
            <p>Choose A, B, or Tie for every dimension. There is no weighted total and no automatic winner.</p>
          </div>
          <div className="comparison-choices">
            {preferenceDimensions.map((dimension) => (
              <ChoiceRow
                key={dimension}
                dimension={dimension}
                value={observation.choices[dimension]}
                onChange={(choice) => updateChoice(dimension, choice)}
              />
            ))}
          </div>
          <label className="comparison-note">
            <span>Optional observation</span>
            <textarea value={observation.note} onChange={(event) => updateNote(event.target.value)} placeholder="Record the reason for a choice or a usability issue…" />
          </label>
        </section>

        <nav className="comparison-navigation" aria-label="Comparison matches">
          <button type="button" onClick={() => setPairIndex((current) => Math.max(0, current - 1))} disabled={pairIndex === 0}>← Previous</button>
          <div>
            {comparisonPairs.map((item, index) => (
              <button
                type="button"
                key={item.id}
                className={index === pairIndex ? "is-active" : observationComplete(observations[item.id]) ? "is-complete" : ""}
                aria-label={`Open comparison ${index + 1}${observationComplete(observations[item.id]) ? ", complete" : ""}`}
                aria-current={index === pairIndex ? "step" : undefined}
                onClick={() => setPairIndex(index)}
              >{index + 1}</button>
            ))}
          </div>
          <button type="button" onClick={() => setPairIndex((current) => Math.min(comparisonPairs.length - 1, current + 1))} disabled={pairIndex === comparisonPairs.length - 1}>Next →</button>
        </nav>

        <section className={`comparison-result ${allComplete ? "is-ready" : ""}`} aria-live="polite">
          <div>
            <p>COMPARISON EVIDENCE</p>
            <h2>{allComplete ? "The Pareto layers are ready." : `${comparisonPairs.length - completed} matches remain.`}</h2>
            <p>{allComplete ? "Every treatment that is not dominated across the five observed dimensions appears in the first layer. Trade-offs remain visible." : "Complete every dimension in all six matches before exporting the comparison receipt."}</p>
          </div>
          {allComplete && <div className="comparison-frontier">
            <span>FRONTIER</span>
            {(evidence.pareto_layers[0] || []).map((variant) => <strong key={variant}>{variantDetails[variant].label}</strong>)}
          </div>}
          <button type="button" disabled={!allComplete} onClick={() => void downloadEvidence()}>Download JSON receipt</button>
          {exportDigest && <code>sha256:{exportDigest}</code>}
          <small>Comparison evidence does not approve or merge a treatment.</small>
        </section>
      </main>
    </div>
  );
}
