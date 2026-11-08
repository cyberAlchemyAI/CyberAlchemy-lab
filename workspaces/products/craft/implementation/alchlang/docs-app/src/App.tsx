import { useEffect, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type ReactNode, type RefObject } from "react";
import {
  actionExample,
  backendTypeAnchor,
  backendTypes,
  backendTypesExample,
  constructionSteps,
  commonDiagnostics,
  declarationClauses,
  declarationGrammar,
  diagnosticAnchor,
  docsSearchEntries,
  docsViewForHash,
  effectExample,
  fileGrammar,
  grammarNotation,
  lexicalRules,
  memoryRunExample,
  metaTypeExtensionSteps,
  navGroups,
  outboxOperations,
  outboxRunExample,
  overviewHero,
  systemLayers,
  integratedJourney,
  packageRoles,
  artifactRoles,
  patternCommands,
  quickstart,
  domainSpecTarget,
  sections,
  sfolGrammar,
  sfolExample,
  sourceExample,
  supportingDeclarations,
  supportingDeclarationAnchor,
  typeDecisionGuide,
  typedBackendExample,
  validationBoundary,
} from "./content";
import { defaultWorkspaceSource, runWorkspaceCommand, workspaceCommands, type WorkspaceResult } from "./workspace";
import { variantClassName, variantFromSearch, type ExperimentVariant } from "./variants";
import { ComparisonPage } from "./ComparisonPage";
import alchLangMark from "./assets/alchlang-mark.svg";
import craftMark from "./assets/craft-mark.svg";
import cyberAlchemyOrb from "../../../../../../../../cyberalchemy-exchange/knowledge-exchange-protocol/capabilities/hosted-devnet-exchange/v1/implementation/static/assets/cyberalchemy-orb-frozen.webp";
import cyberAlchemyLabLogo from "../../../../../../../../cyberalchemy-exchange/knowledge-exchange-protocol/capabilities/hosted-devnet-exchange/v1/implementation/static/assets/cyberalchemy-lab-logo-light-v2.svg";

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4 4" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="8" y="8" width="11" height="11" rx="2" />
      <path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" />
    </svg>
  );
}

const focusableSelector = "a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex='-1'])";

function containKeyboardFocus(event: ReactKeyboardEvent<HTMLElement>, container: HTMLElement) {
  if (event.key !== "Tab") return;
  const focusable = [...container.querySelectorAll<HTMLElement>(focusableSelector)].filter((element) => {
    const style = window.getComputedStyle(element);
    return style.display !== "none" && style.visibility !== "hidden";
  });
  if (!focusable.length) {
    event.preventDefault();
    container.focus();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && (document.activeElement === first || document.activeElement === container)) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function ProductLogo({ compact = false }: { compact?: boolean }) {
  return (
    <span className={`product-logo ${compact ? "is-compact" : ""}`} aria-hidden="true">
      <span className="product-identity alchlang-identity">
        <img src={alchLangMark} alt="" />
        <strong>AlchLang</strong>
      </span>
      <i className="product-bridge">+</i>
      <span className="product-identity craft-identity">
        <img src={craftMark} alt="" />
        <em>Craft</em>
      </span>
    </span>
  );
}

function ProductFooter({ tutorial = false }: { tutorial?: boolean }) {
  return (
    <footer className={`product-footer ${tutorial ? "is-tutorial" : ""}`}>
      <div className="product-footer-main">
        <a className="product-footer-brand" href="?view=overview#overview" aria-label="AlchLang and Craft home"><ProductLogo /></a>
        <nav aria-label="Footer navigation">
          <a href="#quickstart">Documentation</a>
          <a href="#workspace">Workspace</a>
          <a href="#domainspec-target">Craft compiler</a>
        </nav>
        <div className="lab-signature">
          <span>Created by</span>
          <img src={cyberAlchemyLabLogo} width="188" height="44" alt="CyberAlchemy Lab" />
        </div>
      </div>
      <div className="product-footer-meta">
        <span>Language → graph → implementation → evidence</span>
        <span>AlchLang + Craft</span>
      </div>
    </footer>
  );
}

function ConstructionWalkthrough() {
  const [stepIndex, setStepIndex] = useState(0);
  const [displayMode, setDisplayMode] = useState<"normal" | "minimized" | "maximized">("normal");
  const builder = useRef<HTMLElement>(null);
  const sourcePane = useRef<HTMLPreElement>(null);
  const hasRendered = useRef(false);
  const step = constructionSteps[stepIndex];

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
      sourcePane.current?.scrollTo({ top: sourcePane.current.scrollHeight, behavior });

      if (!hasRendered.current) {
        hasRendered.current = true;
        return;
      }
      if (displayMode === "minimized") return;

      const bottom = builder.current?.getBoundingClientRect().bottom;
      const visibleBottom = window.innerHeight - 12;
      if (bottom !== undefined && bottom > visibleBottom) {
        window.scrollBy({ top: bottom - visibleBottom, behavior });
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, [displayMode, stepIndex]);

  return (
    <>
      <section
        ref={builder}
        className={`overview-builder is-${displayMode}`}
        data-theme="console"
        data-step={stepIndex + 1}
        aria-label="Build an AlchLang file step by step"
        aria-expanded={displayMode !== "minimized"}
      >
        <div className="builder-head">
          <span><i />workspace.alch</span>
          <div className="builder-window-controls">
            <small>Step {stepIndex + 1} of {constructionSteps.length}</small>
            <button
              type="button"
              aria-label={displayMode === "minimized" ? "Restore walkthrough" : "Minimize walkthrough"}
              aria-expanded={displayMode !== "minimized"}
              onClick={() => setDisplayMode(displayMode === "minimized" ? "normal" : "minimized")}
            ><span aria-hidden="true">−</span></button>
            <button
              type="button"
              aria-label={displayMode === "maximized" ? "Restore walkthrough" : "Maximize walkthrough"}
              aria-pressed={displayMode === "maximized"}
              onClick={() => setDisplayMode(displayMode === "maximized" ? "normal" : "maximized")}
            ><span aria-hidden="true">{displayMode === "maximized" ? "↙" : "↗"}</span></button>
          </div>
        </div>
        <div className="builder-explanation" aria-live="polite">
          <span>{step.label}</span>
          <strong>{step.title}</strong>
          <p>{step.explanation}</p>
        </div>
        <pre ref={sourcePane} aria-live="polite"><code>{step.source}</code></pre>
        <div className="builder-controls">
          <button type="button" onClick={() => setStepIndex((current) => Math.max(0, current - 1))} disabled={stepIndex === 0} aria-label="Previous construction step">←</button>
          <div role="group" aria-label="Construction steps">
            {constructionSteps.map((item, index) => (
              <button
                type="button"
                key={item.id}
                className={index === stepIndex ? "active" : ""}
                aria-label={`Step ${index + 1}: ${item.label}`}
                aria-pressed={index === stepIndex}
                onClick={() => setStepIndex(index)}
              >{index + 1}</button>
            ))}
          </div>
          <button type="button" onClick={() => setStepIndex((current) => Math.min(constructionSteps.length - 1, current + 1))} disabled={stepIndex === constructionSteps.length - 1} aria-label="Next construction step">→</button>
        </div>
      </section>
    </>
  );
}

function OverviewPage({ variant }: { variant: ExperimentVariant }) {
  return (
    <div className={`overview-shell ${variantClassName(variant)}`} data-experiment-variant={variant} id="overview">
      <a className="skip-link" href="#overview-content">Skip to content</a>
      <header className="overview-header">
        <a className="overview-brand" href="#overview" aria-label="AlchLang and Craft home"><ProductLogo compact /></a>
        <img className="overview-orb" src={cyberAlchemyOrb} width="42" height="42" alt="" aria-hidden="true" />
        <a className="overview-header-link" href="#quickstart">Open tutorial <span>→</span></a>
      </header>

      <main id="overview-content">
        <section className="overview-hero" aria-labelledby="overview-title">
          <div className="overview-hero-copy">
            <p className="eyebrow">A LANGUAGE FOR THE AGENTIC ERA</p>
            <h1 id="overview-title">{overviewHero.lead}<br /><em>{overviewHero.emphasis}</em></h1>
            <p className="overview-lede">{overviewHero.descriptionBeforeFile}<code>.alch</code>{overviewHero.descriptionAfterFile}</p>
            <p className="overview-values">{overviewHero.value}</p>
            <div className="overview-actions">
              <a className="primary-action" href="#quickstart">Start building <span>→</span></a>
              <a className="text-action" href="#workspace">Explore the workspace <span>↘</span></a>
            </div>
          </div>
          <ConstructionWalkthrough />
        </section>

        <section className="overview-purpose" aria-labelledby="purpose-title">
          <div>
            <p className="section-kicker">ONE CONNECTED TOOLCHAIN</p>
            <h2 id="purpose-title">Human language in. Checked system out.</h2>
          </div>
          <p>AlchLang is the authoring experience. Craft is the system compiler. Together they preserve a visible path from the words a team agrees on to the typed graph and generated code an application can use.</p>
        </section>

        <section className="overview-system" aria-label="Product responsibilities">
          {systemLayers.map((layer, index) => (
            <article key={layer.id}>
              <header><span>{String(index + 1).padStart(2, "0")}</span><small>{layer.label}</small></header>
              <p>{layer.product}</p>
              <h2>{layer.title}</h2>
              <div>{layer.description}</div>
              <ul>{layer.outputs.map((output) => <li key={output}>{output}</li>)}</ul>
            </article>
          ))}
        </section>

        <section className="overview-path" data-theme="console" aria-labelledby="path-title">
          <div className="overview-path-copy">
            <p className="section-kicker">THE PATH</p>
            <h2 id="path-title">One journey. Clear responsibilities.</h2>
            <p>The guide follows one source from readable domain language through compilation, generated code, application integration, and bounded evidence.</p>
            <div className="interpretation-note">
              <span>THE HANDOFF</span>
              <h3>AlchLang lowers; Craft compiles</h3>
              <p>AlchLang preserves source meaning and provenance while producing the supported Craft project. Craft validates that typed project, builds one graph, and generates the selected realization.</p>
            </div>
            <a href="#quickstart">Follow the complete path <span>→</span></a>
          </div>
          <ol>
            <li><span>01</span><strong>.alch source</strong><small>Readable domain meaning</small></li>
            <li><span>02</span><strong>AlchLang lowering</strong><small>Typed project + source provenance</small></li>
            <li><span>03</span><strong>Craft compilation</strong><small>Graph + generated realization</small></li>
            <li><span>04</span><strong>Application evidence</strong><small>Explicit integration + observations</small></li>
          </ol>
        </section>

        <section className="overview-next">
          <p>READY TO BEGIN?</p>
          <h2>Author in AlchLang. Compile with Craft.</h2>
          <a className="primary-action" href="#quickstart">Start the tutorial <span>→</span></a>
        </section>
      </main>
      <ProductFooter />
    </div>
  );
}

function CodeBlock({ code, label }: { code: string; label: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  }

  return (
    <div className="code-card" data-theme="console">
      <div className="code-head">
        <span><i />{label}</span>
        <button type="button" onClick={copy} aria-label={`Copy ${label}`}>
          <CopyIcon /> {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre role="group" tabIndex={0} aria-label={`${label} code`}><code>{code}</code></pre>
    </div>
  );
}

function TutorialSection({ variant, id, className = "", title, progressive = false, children }: {
  variant: ExperimentVariant;
  id: string;
  className?: string;
  title: string;
  progressive?: boolean;
  children: ReactNode;
}) {
  const sectionClass = `doc-section ${className}`.trim();
  if (variant === "progressive-reference" && progressive) {
    return (
      <details id={id} className={`experiment-disclosure ${sectionClass}`}>
        <summary><span>REFERENCE</span><strong>{title}</strong><small>Open section</small></summary>
        <section aria-label={title}>{children}</section>
      </details>
    );
  }
  return <section id={id} className={sectionClass}>{children}</section>;
}

function ClauseTable({ syntax }: { syntax: string }) {
  const clauses = declarationClauses[syntax];
  if (!clauses?.length) return <p className="no-clauses">This declaration has no body clauses.</p>;

  return (
    <div className="clause-table" role="table" aria-label={`${syntax} clauses`}>
      <div className="clause-head" role="row">
        <span role="columnheader">Clause</span><span role="columnheader">Value</span><span role="columnheader">Cardinality</span><span role="columnheader">Meaning</span>
      </div>
      {clauses.map((clause) => (
        <div role="row" key={clause.clause}>
          <code role="cell">{clause.clause}</code>
          <span role="cell">{clause.value}</span>
          <b role="cell">{clause.cardinality}</b>
          <p role="cell">{clause.meaning}</p>
        </div>
      ))}
    </div>
  );
}

function Sidebar({ open, onClose, active, navigationRef }: { open: boolean; onClose: () => void; active: string; navigationRef: RefObject<HTMLElement | null> }) {
  return (
    <aside ref={navigationRef} id="docs-navigation" className={`sidebar ${open ? "is-open" : ""}`} aria-label="Documentation navigation" tabIndex={-1} onKeyDown={(event) => open && containKeyboardFocus(event, event.currentTarget)}>
      <a className="brand" href="?view=overview#overview" aria-label="AlchLang and Craft home" onClick={onClose}><ProductLogo /></a>
      <nav>
        {navGroups.map((group) => (
          <div className="nav-group" key={group.label}>
            <p>{group.label}</p>
            {group.items.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className={active === item.id ? "active" : ""}
                aria-current={active === item.id ? "location" : undefined}
                onClick={onClose}
              >
                {item.title}
              </a>
            ))}
          </div>
        ))}
      </nav>
      <div className="sidebar-foot">
        <span className="status-dot" />
        <span><strong>CLI v0.4</strong> Candidate</span>
      </div>
    </aside>
  );
}

function SearchDialog({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const results = useMemo(() => {
    const needle = query.toLowerCase().trim();
    return needle
      ? docsSearchEntries.filter((item) => `${item.title} ${item.summary} ${item.terms.join(" ")}`.toLowerCase().includes(needle))
      : docsSearchEntries.slice(0, sections.length);
  }, [query]);

  return (
    <div className="search-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="search-dialog" role="dialog" aria-modal="true" aria-label="Search documentation" onMouseDown={(event) => event.stopPropagation()} onKeyDown={(event) => containKeyboardFocus(event, event.currentTarget)}>
        <label>
          <SearchIcon />
          <input aria-label="Search documentation" autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search AlchLang + Craft…" />
          <kbd>Esc</kbd>
        </label>
        <p className="sr-only" aria-live="polite">{results.length} search {results.length === 1 ? "result" : "results"}</p>
        <div className="search-results">
          {results.map((item) => (
            <a key={`${item.eyebrow}-${item.title}`} href={`#${item.id}`} onClick={onClose}>
              <span>{item.eyebrow}</span>
              <strong>{item.title}</strong>
              <p>{item.summary}</p>
            </a>
          ))}
          {results.length === 0 && <p className="empty">No matching section.</p>}
        </div>
      </section>
    </div>
  );
}

function MiniWorkspace() {
  const source = defaultWorkspaceSource;
  const [command, setCommand] = useState<string>(workspaceCommands.check);
  const [running, setRunning] = useState(false);
  const [history, setHistory] = useState<WorkspaceResult[]>([
    { command: "", status: "info", output: "Fixed-example simulation ready. No source is compiled or action executed here. Choose a preview or type help." },
  ]);

  async function execute(nextCommand: string) {
    if (nextCommand.trim() === "clear") {
      setHistory([]);
      setCommand("");
      return;
    }
    setRunning(true);
    const result = await runWorkspaceCommand(nextCommand, source);
    setHistory((current) => [...current, result]);
    setCommand("");
    setRunning(false);
  }

  return (
    <div className="workspace-shell" data-theme="console">
      <div className="workspace-bar">
        <div><span className="workspace-lights"><i /><i /><i /></span><strong>AlchLang workspace</strong></div>
        <div className="sandbox-badge"><span /> Fixed-example simulation · no compiler or runtime</div>
      </div>
      <div className="workspace-grid">
        <section className="workspace-editor" aria-label="Fixed AlchLang example source">
          <div className="pane-head">
            <span className="file-icon">A</span>
            <strong>workspace.alch</strong>
            <span>Read-only example</span>
          </div>
          <textarea
            aria-label="Read-only workspace.alch example source"
            value={source}
            readOnly
            spellCheck={false}
          />
        </section>
        <section className="workspace-terminal" aria-label="Browser command terminal">
          <div className="pane-head"><span className="terminal-icon">›_</span><strong>Terminal</strong><i>in memory</i></div>
          <div className="terminal-output" role="log" aria-live="polite">
            {history.length === 0 && <p className="terminal-empty">Output cleared.</p>}
            {history.map((entry, index) => (
              <div className={`terminal-entry ${entry.status}`} key={`${entry.command}-${index}`}>
                {entry.command && <p><span>$</span> {entry.command}</p>}
                <pre>{entry.output}</pre>
              </div>
            ))}
            {running && <p className="terminal-running"><span /> preparing illustration…</p>}
          </div>
          <form className="terminal-command" onSubmit={(event) => { event.preventDefault(); void execute(command); }}>
            <span>$</span>
            <input
              aria-label="CLI command"
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              placeholder="Type help"
              autoComplete="off"
            />
            <button type="submit" disabled={running || !command.trim()}>Preview ↵</button>
          </form>
        </section>
      </div>
      <div className="workspace-actions" role="group" aria-label="Example commands">
        <span>Try a command</span>
        <button type="button" onClick={() => void execute(workspaceCommands.check)}>Preview check</button>
        <button type="button" onClick={() => void execute(workspaceCommands.build)}>Preview artifacts</button>
        <button type="button" onClick={() => void execute(workspaceCommands.patterns)}>Inspect patterns</button>
        <button type="button" onClick={() => void execute(workspaceCommands.run)}>Preview action</button>
      </div>
    </div>
  );
}

export function App() {
  const variant = useMemo(() => variantFromSearch(window.location.search), []);
  const comparisonView = useMemo(() => new URLSearchParams(window.location.search).get("view") === "compare", []);
  const [view, setView] = useState(() => docsViewForHash(window.location.hash));
  const [active, setActive] = useState("quickstart");
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const navigationRef = useRef<HTMLElement>(null);
  const searchReturnFocusRef = useRef<HTMLElement | null>(null);

  function openSearch() {
    searchReturnFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setMenuOpen(false);
    setSearchOpen(true);
  }

  function closeSearch() {
    setSearchOpen(false);
    searchReturnFocusRef.current?.focus();
  }

  function closeMenu(restoreFocus = false) {
    setMenuOpen(false);
    if (restoreFocus) menuButtonRef.current?.focus();
  }

  useEffect(() => {
    function route() {
      setView(docsViewForHash(window.location.hash));
      window.requestAnimationFrame(() => {
        const target = document.getElementById(window.location.hash.replace(/^#/, ""));
        if (target instanceof HTMLDetailsElement) target.open = true;
      });
    }
    window.addEventListener("hashchange", route);
    return () => window.removeEventListener("hashchange", route);
  }, []);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      if (view === "overview") {
        window.scrollTo(0, 0);
        return;
      }
      const target = window.location.hash.replace(/^#/, "");
      if (target && target !== "tutorial") {
        const element = document.getElementById(target);
        if (element instanceof HTMLDetailsElement) element.open = true;
        element?.scrollIntoView();
      } else {
        window.scrollTo(0, 0);
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, [view]);

  useEffect(() => {
    if (view !== "tutorial") return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: "-18% 0px -62%", threshold: [0, 0.2, 0.6] },
    );
    sections.forEach((section) => {
      const element = document.getElementById(section.id);
      if (element) observer.observe(element);
    });
    return () => observer.disconnect();
  }, [view]);

  useEffect(() => {
    function keydown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openSearch();
      }
      if (event.key === "Escape") {
        if (searchOpen) closeSearch();
        else if (menuOpen) closeMenu(true);
      }
    }
    window.addEventListener("keydown", keydown);
    return () => window.removeEventListener("keydown", keydown);
  }, [menuOpen, searchOpen]);

  useEffect(() => {
    if (menuOpen) window.requestAnimationFrame(() => navigationRef.current?.focus());
  }, [menuOpen]);

  if (comparisonView) return <ComparisonPage />;
  if (view === "overview") return <OverviewPage variant={variant} />;

  return (
    <div className={`app-shell ${variantClassName(variant)}`} data-experiment-variant={variant} id="top">
      <a className="skip-link" href="#content">Skip to content</a>
      <Sidebar open={menuOpen} onClose={() => closeMenu()} active={active} navigationRef={navigationRef} />
      {menuOpen && <button className="menu-backdrop" aria-label="Close navigation" onClick={() => closeMenu(true)} tabIndex={-1} />}

      <header className="topbar">
        <button ref={menuButtonRef} className="menu-button" type="button" onClick={() => setMenuOpen(true)} aria-label="Open navigation" aria-controls="docs-navigation" aria-expanded={menuOpen}><span /><span /></button>
        <a className="mobile-brand" href="?view=overview#overview" aria-label="AlchLang and Craft home"><ProductLogo compact /></a>
        <button className="search-button" type="button" onClick={openSearch} aria-label="Search documentation" aria-haspopup="dialog">
          <SearchIcon /> <span>Search documentation</span><kbd>Ctrl/⌘ K</kbd>
        </button>
        <a className="source-link" href="?view=overview#overview">How they work together <span>↑</span></a>
      </header>

      <main id="content" className="article">
        <section className={`hero ${variant === "task-first" ? "task-first-hero" : ""}`} aria-labelledby="page-title">
          {variant === "task-first" ? <>
            <p className="eyebrow">ALCHLANG WORKING TUTORIAL <span>·</span> START WITH SOURCE</p>
            <h1 id="page-title">Build the domain.<br /><em>Inspect every step.</em></h1>
            <p className="lede">Inspect a complete <code>.alch</code> example and preview fixed outcomes in the browser, then follow the guide to run real checks with the installed CLI.</p>
            <div id="workspace" className="task-first-workspace"><MiniWorkspace /></div>
          </> : <>
            <p className="eyebrow">ALCHLANG + CRAFT <span>·</span> COMPLETE GUIDE</p>
            <h1 id="page-title">Author the meaning.<br /><em>Compile the system.</em></h1>
            <p className="lede">Use AlchLang to describe the domain, then use Craft to validate its typed graph, generate implementation code, and verify the result.</p>
            <div className="hero-actions">
              <a className="primary-action" href="#quickstart">Start building <span>→</span></a>
              <a className="text-action" href="#sfol">Language overview <span>↓</span></a>
            </div>
          </>}
        </section>

        <section id="quickstart" className="doc-section">
          <p className="section-kicker">01 — Start here</p>
          <h2>Five-minute quickstart</h2>
          <p>Install the downloaded core package archive in a project, save the maintained example from the workspace as <code>workspace.alch</code>, then validate it and generate application code.</p>
          <CodeBlock code={quickstart} label="Terminal — package quickstart" />
          <p>Continue with <a href="#integration">the complete product journey</a>, then use <a href="#domainspec-target">the Craft 1.0.0 compiler guide</a> for the checked graph and generated target.</p>
          <div className="callout"><span>✓</span><p><strong>Expected result</strong>A valid check returns a deterministic plan digest. The build creates a manifest and generated domain files.</p></div>
        </section>

        {variant !== "task-first" && <section id="workspace" className="doc-section workspace-section">
          <p className="section-kicker">02 — Try it</p>
          <h2>Run a mini workspace</h2>
          <p>Inspect the read-only source, choose a preview, and inspect the illustrated result. This fixed browser simulation does not parse, compile, generate files, or execute an action; install the core package for those operations.</p>
          <MiniWorkspace />
        </section>}

        <section id="model" className="doc-section">
          <p className="section-kicker">03 — Mental model</p>
          <h2>One source, explicit layers</h2>
          <p>AlchLang and Craft are connected, but they are not interchangeable. Each boundary has one job and one visible output.</p>
          <div className="flow" role="group" aria-label="AlchLang processing layers">
            {[".alch source", "Alch validation", "Craft project", "Typed graph", "Generated target", "Runtime evidence"].map((item, index) => (
              <div className="flow-item" key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong>{index < 5 && <i>→</i>}</div>
            ))}
          </div>
          <div className="principle-grid">
            <article><span>AlchLang</span><h3>What does the domain mean?</h3><p>Owns readable source, language diagnostics, semantic annotations, and lowering.</p></article>
            <article><span>Craft</span><h3>Is the system structurally closed?</h3><p>Owns the typed graph, realization selection, generation, and verification.</p></article>
            <article><span>Application</span><h3>What actually ran?</h3><p>Owns runtime inputs, infrastructure bindings, execution, and observations.</p></article>
          </div>
        </section>

        <section id="integration" className="doc-section integration-section">
          <p className="section-kicker">04 — AlchLang + Craft</p>
          <h2>Follow meaning into implementation</h2>
          <p>One source moves through six explicit stages. The owner changes at a visible handoff, so a generated file is never confused with authored meaning and a successful build is never confused with a deployment.</p>
          <ol className="integrated-journey">
            {integratedJourney.map((item) => <li key={item.step}><span>{item.step}</span><small>{item.owner}</small><strong>{item.title}</strong><p>{item.detail}</p></li>)}
          </ol>
          <div className="reference-heading"><span>PACKAGE ROLES</span><h3>Install only the capabilities you use</h3></div>
          <div className="package-matrix">
            {packageRoles.map((item) => <article key={item.name}><code>{item.name}</code><span>{item.status}</span><p>{item.detail}</p></article>)}
          </div>
          <div className="reference-heading"><span>ARTIFACT MAP</span><h3>Know which result you are reading</h3></div>
          <div className="artifact-map" role="table" aria-label="AlchLang and Craft artifact ownership">
            <div className="artifact-map-head" role="row"><span role="columnheader">Artifact</span><span role="columnheader">Owner</span><span role="columnheader">Purpose</span></div>
            {artifactRoles.map((item) => <div role="row" key={item.artifact}><code role="cell">{item.artifact}</code><strong role="cell">{item.owner}</strong><p role="cell">{item.purpose}</p></div>)}
          </div>
          <div className="callout"><span>✓</span><p><strong>Safe by default</strong><code>check</code>, compilation, generation, and verification do not publish, deploy, or start the generated application.</p></div>
        </section>

        <section id="source" className="doc-section">
          <p className="section-kicker">05 — Source format</p>
          <h2>Author canonical .alch files</h2>
          <p>Canonical source is lowercase <code>.alch</code>, plain UTF-8 without a byte-order mark or Markdown fence. Each maintained file declares its domain, owner, and <code>logic sfol-v1</code> profile before indented declarations.</p>
          <CodeBlock code={sourceExample} label="inventory.alch" />
          <div className="fact-grid" role="group" aria-label="AlchLang source rules">
            <article><span>FILE</span><strong>One domain and owner</strong><p>Identifiers begin with a letter or underscore and may contain digits, dots, and hyphens.</p></article>
            <article><span>TYPES</span><strong>Eleven scalar shapes</strong><p>String, integer, decimal, boolean, identifier, timestamp, duration, enum, reference, list, and record.</p></article>
            <article><span>BODY</span><strong>Indent declarations</strong><p>Top-level declarations are flush left. Fields and clauses belong to their indented section body.</p></article>
            <article><span>LEGACY</span><strong>Markdown is compatibility-only</strong><p>A legacy <code>.md</code> container must hold exactly one fenced <code>alchlang</code> block.</p></article>
          </div>
        </section>

        <section id="sfol" className="doc-section">
          <p className="section-kicker">06 — Language</p>
          <h2>Express rules with SFOL</h2>
          <p>Canonical source uses the <code>.alch</code> extension and declares <code>logic sfol-v1</code>. The same bounded formula model powers rules, filters, permissions, guards, and policy cases.</p>
          <CodeBlock code={sfolExample} label="typed-backend.alch" />
          <div className="operator-row" role="group" aria-label="Supported SFOL operators">
            {["==", "!=", "<", "<=", ">", ">=", "in", "contains", "and", "or", "not", "exists", "absent"].map((operator) => <code key={operator}>{operator}</code>)}
          </div>
          <div className="inline-note"><strong>Bounded and deterministic</strong><p>The profile evaluates quantifier-free formulas over caller-supplied values. It excludes provider reads, embedded host-language expressions, proof scripts, reflection, and automatic theorem proving.</p></div>
        </section>

        <section id="contracts" className="doc-section">
          <p className="section-kicker">07 — Typed backend</p>
          <h2>Shape reads and decisions</h2>
          <p>Four constructs cover the common path from source values to an explicit result. They stay deterministic and side-effect free.</p>
          <div className="contract-list">
            <article><span>Q</span><div><h3>Query</h3><p>Filters, orders, limits, and projects caller-supplied rows.</p></div></article>
            <article><span>C</span><div><h3>Calculation</h3><p>Evaluates checked UInt64 arithmetic with explicit rounding.</p></div></article>
            <article><span>M</span><div><h3>Mapping</h3><p>Constructs only authored target fields from source clauses and defaults.</p></div></article>
            <article><span>P</span><div><h3>Policy</h3><p>Selects one declared calculation or action for a separate runtime step.</p></div></article>
          </div>
          <CodeBlock code={typedBackendExample} label="typed-backend.alch" />
          <div className="callout"><span>✓</span><p><strong>Evaluation boundary</strong>Queries consume caller-supplied rows; calculations use checked UInt64 arithmetic; mappings emit only authored fields; policy selection never executes its target.</p></div>
        </section>

        <section id="backend-types" className="doc-section">
          <p className="section-kicker">08 — Craft profile</p>
          <h2>Use all 13 backend types</h2>
          <p>The backend alphabet separates identity, values, decisions, write-side behavior, orchestration, boundaries, transformations, and lifecycle. The IDs are intentionally non-contiguous: <code>DS-D1.10</code> was Saga and is not reused.</p>
          <div className="type-catalog" role="group" aria-label="Craft backend type catalog">
            {backendTypes.map((type) => (
              <article key={type.id}>
                <span>{type.id}</span>
                <div><small>{type.category}</small><h3>{type.name}</h3><p>{type.meaning}</p></div>
                <code>{type.syntax}</code>
              </article>
            ))}
          </div>
          <CodeBlock code={backendTypesExample} label="backend-types.alch" />
          <div className="inline-note"><strong>Language realization boundary</strong><p>The AlchLang core renders Node/TypeScript contracts. Craft 1.0 separately binds all 13 types to TypeScript, Python, and Rust. Optional AlchLang packages add supported Rust workflows without making Rust part of the core installation.</p></div>
        </section>

        <section id="type-selection" className="doc-section">
          <p className="section-kicker">09 — Choose a construct</p>
          <h2>Select the type that owns the meaning</h2>
          <p>Start with the semantic distinction, not the spelling. These questions separate the pairs that most often look interchangeable at first.</p>
          <div className="decision-table" role="table" aria-label="AlchLang type selection guide">
            {typeDecisionGuide.map((item) => (
              <div role="row" key={item.question}>
                <p role="cell">{item.question}</p>
                <strong role="cell">{item.choose}</strong>
                <small role="cell">{item.instead}</small>
              </div>
            ))}
          </div>
          <div className="callout"><span>→</span><p><strong>Declaration or extension?</strong>Naming <code>entity Ledger</code> creates a domain declaration. Adding a new category beside Entity or Operation changes the language and follows the extension path in the formal grammar section.</p></div>
        </section>

        <TutorialSection variant={variant} id="lexical-reference" className="syntax-reference-section" title="Read tokens and source structure" progressive>
          <p className="section-kicker">10 — Lexical reference</p>
          <h2>Read tokens and source structure</h2>
          <p>Lexical rules describe how source bytes become identifiers, literals, lists, comments, headers, and indented bodies. Declaration semantics are validated later.</p>
          <div className="lexical-table" role="table" aria-label="AlchLang lexical rules">
            <div className="lexical-head" role="row"><span role="columnheader">Subject</span><span role="columnheader">Syntax</span><span role="columnheader">Rule</span><span role="columnheader">Diagnostic</span></div>
            {lexicalRules.map((item) => (
              <div role="row" key={item.subject}><strong role="cell">{item.subject}</strong><code role="cell">{item.syntax}</code><p role="cell">{item.rule}</p><small role="cell">{item.error}</small></div>
            ))}
          </div>
          <CodeBlock code={fileGrammar} label="Canonical source shape" />
          <div className="scalar-reference">
            <span>SCALAR FIELD TYPES</span>
            <div>{["string", "integer", "decimal", "boolean", "identifier", "timestamp", "duration", "enum", "reference", "list", "record"].map((type) => <code key={type}>{type}</code>)}</div>
            <p>Scalar types describe values stored in fields. They do not introduce declaration behavior and are not Craft backend meta-types.</p>
          </div>
        </TutorialSection>

        <TutorialSection variant={variant} id="declaration-reference" className="syntax-reference-section" title="Inspect every declaration contract" progressive>
          <p className="section-kicker">11 — Declaration reference</p>
          <h2>Inspect every declaration contract</h2>
          <p>The reference follows the current parser and validator. Each entry combines meaning, selection criteria, canonical syntax, semantic requirements, and its compilation surface.</p>
          <div className="reference-heading"><span>13 BACKEND META-TYPES</span><h3>Domain meaning and generated contracts</h3></div>
          <div className="syntax-type-list">
            {backendTypes.map((type, index) => (
              <details id={backendTypeAnchor(type.syntax)} className="syntax-type-card" key={type.id} open={index === 0}>
                <summary>
                  <span>{type.id}</span>
                  <div><small>{type.category}</small><strong>{type.name}</strong><p>{type.meaning}</p></div>
                  <code>{type.syntax}</code><i aria-hidden="true">+</i>
                </summary>
                <div className="syntax-type-body">
                  <div className="syntax-purpose"><span>USE IT WHEN</span><p>{type.useWhen}</p></div>
                  <pre><code>{type.form}</code></pre>
                  <ClauseTable syntax={type.syntax} />
                  <div className="syntax-requirements"><span>VALIDATION CONTRACT</span><ul>{type.requirements.map((requirement) => <li key={requirement}>{requirement}</li>)}</ul></div>
                  <div className="syntax-output"><span>COMPILATION SURFACE</span><p>{type.compilesTo}</p></div>
                </div>
              </details>
            ))}
          </div>
          <div className="reference-heading"><span>SUPPORTING DECLARATIONS</span><h3>Contracts around the backend types</h3></div>
          <div className="support-reference">
            {supportingDeclarations.map((item) => (
              <article id={supportingDeclarationAnchor(item.syntax)} key={item.name}><div><small>{item.syntax}</small><h3>{item.name}</h3><p>{item.detail}</p></div><pre><code>{item.form}</code></pre><ClauseTable syntax={item.syntax} /></article>
            ))}
          </div>
        </TutorialSection>

        <TutorialSection variant={variant} id="formal-grammar" className="syntax-reference-section" title="Read the closed language grammar" progressive>
          <p className="section-kicker">12 — Formal grammar</p>
          <h2>Read the closed language grammar</h2>
          <p>This compact grammar is a human-readable index of the supported source forms. The parser remains the executable reference; semantic validation supplies constraints that grammar alone cannot express.</p>
          <div className="notation-grid" role="group" aria-label="Grammar notation legend">
            {grammarNotation.map((item) => <article key={item.mark}><code>{item.mark}</code><p>{item.meaning}</p></article>)}
          </div>
          <CodeBlock code={declarationGrammar} label="Top-level declaration grammar" />
          <CodeBlock code={sfolGrammar} label="sfol-v1 expression grammar" />
          <div className="validation-layers" role="group" aria-label="Grammar and validation boundaries">
            {validationBoundary.map((item) => <article key={item.layer}><h3>{item.layer}</h3><p><strong>Establishes</strong>{item.proves}</p><p><strong>Does not establish</strong>{item.doesNotProve}</p></article>)}
          </div>
          <div className="inline-note"><strong>Current parser boundary</strong><p>Quoted strings are canonical. A bare undeclared word on the right side of a comparison may currently parse as a string literal. <code>in</code> and <code>contains</code> parse without operand-shape validation.</p></div>

          <div className="extension-answer" data-theme="console">
            <div><span>LANGUAGE EXTENSION</span><strong>Can a .alch file define a new meta-type?</strong></div>
            <p><b>No.</b> The grammar is closed over the declarations listed above. An unknown top-level declaration fails with <code>TEXT_SYNTAX</code>. Domain authors may instantiate or compose the existing types; a new category requires a versioned Craft and compiler evolution.</p>
          </div>
          <ol className="extension-steps">
            {metaTypeExtensionSteps.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, "0")}</span><p>{step}</p></li>)}
          </ol>
          <div className="warning"><span>!</span><p><strong>Language extensions require a coordinated release.</strong>A parser change alone does not add a supported meta-type; the Craft definition, compiler mapping, generator, validation, and documentation must evolve together.</p></div>
          <div className="diagnostic-index" role="group" aria-label="Common compiler diagnostics"><span>COMMON DIAGNOSTICS</span><div>{commonDiagnostics.map((error) => <code id={diagnosticAnchor(error)} key={error}>{error}</code>)}</div></div>
        </TutorialSection>

        <section id="domainspec-target" className="doc-section">
          <p className="section-kicker">13 — Craft {domainSpecTarget.version}</p>
          <h2>Compile with Craft 1.0.0</h2>
          <p>Craft 1.0 provides the stable compiler boundary for typed project validation, graph construction, deterministic code generation, verification, and certificates. AlchLang lowers the declarations supported by its selected profile into that compiler.</p>
          <h3>Add the compiler package</h3>
          <p>Craft builds currently use the compatibility package identifier <code>@domainspec-v2/cli@1.0.0</code> and the <code>domainspec</code> CLI namespace. Install its archive in the same project as AlchLang; ordinary AlchLang checks do not require this optional peer.</p>
          <CodeBlock code={domainSpecTarget.install} label="Terminal — add Craft" />
          <h3>Build a checked target</h3>
          <CodeBlock code={domainSpecTarget.commands} label="Terminal — Craft target" />
          <p>{domainSpecTarget.supported}</p>
          <h3>Understand the generated files</h3>
          <p>{domainSpecTarget.bindings}</p>
          <p>{domainSpecTarget.outputs}</p>
          <div className="callout"><span>i</span><p><strong>Choose a new output directory</strong>Its parent must exist. Even an empty destination is rejected; this target does not accept <code>--force</code>.</p></div>
          <h3>Call the generated code</h3>
          <CodeBlock code={domainSpecTarget.usage} label="TypeScript — application integration" />
          <p>Your application supplies facts, decides whether to execute a selected target, and applies the runtime validation required by its environment. Generation does not perform those application-owned effects.</p>
          <details className="advanced-reference">
            <summary><strong>Advanced: exact UInt64 commerce profile</strong><small>Queries, calculations, and thresholds</small></summary>
            <div>
              <p>{domainSpecTarget.migration}</p>
              <CodeBlock code={domainSpecTarget.exactCommands} label="Terminal — exact commerce" />
              <p>The bound compiler must advertise <code>domainspec.typescript-exact-uint64/v1</code>. This profile adds queries, integer records, parameterized calculations and threshold policies. The sidecar must select the same profile.</p>
              <p>The generated entry also exports <code>evaluateQuery</code> and <code>evaluateCalculation</code>. Calculations accept bigint, safe Numbers or canonical unsigned decimal strings and return bigint across the full UInt64 range. Integer record and policy inputs accept bigint or nonnegative safe Numbers. Unsafe Numbers reject.</p>
              <p>Queries preserve tie order and supplied values, with one sort key and explicit projection. Multiple keys and overlapping row/parameter names reject. Numeric predicate/default literals must be safe integers. Effects and additional backend kinds remain outside this profile.</p>
            </div>
          </details>
          <p>The browser mini workspace is a fixed-example simulation. It does not validate edited source, invoke the compiler, generate files, or execute actions.</p>
        </section>

        <section id="compiler" className="doc-section">
          <p className="section-kicker">14 — Compiler</p>
          <h2>Inspect deterministic artifacts</h2>
          <p><code>check</code> performs the compiler pipeline entirely in memory. <code>build</code> writes the same lowered plan into a dedicated directory and binds every payload with SHA-256 digests.</p>
          <div className="compiler-pipeline" role="group" aria-label="Compiler pipeline">
            {["Parse", "Normalize", "Validate", "Lower", "Render", "Write"].map((stage, index) => <div key={stage}><span>{String(index + 1).padStart(2, "0")}</span><strong>{stage}</strong></div>)}
          </div>
          <div className="artifact-groups">
            <article><span>CORE OUTPUT</span><h3>Domain package</h3><p>Types, schema, machine, events, operations, workflows, interfaces, tools, graph, test obligations, traceability, unsupported residue, and manifest.</p></article>
            <article><span>TYPED BACKEND</span><h3>Executable contracts</h3><p><code>domain.typed-backend.ts</code> materializes Query, Calculation, Mapping, and Policy behavior.</p></article>
            <article><span>EFFECTFUL DOMAIN</span><h3>Generated provider slice</h3><p>Effect descriptors plus pattern-owned ports, migration, SQLite provider, worker, integration provider, and executable tests.</p></article>
          </div>
          <div className="warning"><span>!</span><p><strong>Output replacement is explicit.</strong>Build refuses a non-empty output directory. <code>--force</code> recursively replaces it and should be used only when every existing entry is disposable.</p></div>
        </section>

        <section id="actions" className="doc-section">
          <p className="section-kicker">15 — Action runtime</p>
          <h2>Run guarded actions</h2>
          <p>The runtime resolves an action only after its actor, required facts, SFOL rules, permission, authority boundary, grant, and adapter are all explicit.</p>
          <div className="guard-stack" role="group" aria-label="Action execution checks">
            {["Declared actor", "Required facts", "SFOL rules", "Permission contract", "Exact authority grant", "Selected adapter or binding"].map((check, index) => <div key={check}><span>{index + 1}</span><strong>{check}</strong><i>required</i></div>)}
          </div>
          <CodeBlock code={memoryRunExample} label="Memory adapter" />
          <div className="inline-note"><strong>No implicit execution</strong><p>A memory adapter is valid only for an action with no declared Effect. An effectful action fails with <code>EFFECT_BINDING_REQUIRED</code> instead of silently falling back to memory.</p></div>
        </section>

        <section id="effects" className="doc-section">
          <p className="section-kicker">16 — Operation patterns</p>
          <h2>Resolve effects and bindings</h2>
          <p>An Effect names its architecture pattern, integration binding, writes, emitted events, transaction guarantee, failure continuation, and authority boundary. Pattern availability is derived from registered prerequisites rather than assumed from an identifier.</p>
          <CodeBlock code={effectExample} label="Effect contract" />
          <CodeBlock code={actionExample} label="Operation contract" />
          <CodeBlock code={patternCommands} label="Pattern registry CLI" />
          <div className="generated-strip" role="group" aria-label="Transactional Outbox generated files">
            {[["PORT", "domain.outbox.port.ts"], ["SQL", "domain.outbox.migration.sql"], ["STORE", "domain.outbox.sqlite.ts"], ["WORKER", "domain.outbox.worker.ts"], ["PROVIDER", "domain.outbox.provider.ts"], ["TEST", "domain.outbox.test.ts"]].map(([kind, file]) => <div key={file}><span>{kind}</span><code>{file}</code></div>)}
          </div>
          <div className="warning"><span>!</span><p><strong>Execution remains explicit.</strong> A source-level binding identifies a runtime path; the caller still selects the provider inputs and authority grant.</p></div>
        </section>

        <section id="outbox" className="doc-section">
          <p className="section-kicker">17 — Durable runtime</p>
          <h2>Operate the transactional Outbox</h2>
          <p>The SQLite provider commits aggregate state and pending messages in one transaction. Delivery is a separate at-least-once worker operation with lease ownership, bounded retry, dead-letter recovery, replay reconciliation, telemetry, and an idempotent inbox for consumers.</p>
          <CodeBlock code={outboxRunExample} label="Atomic local commit" />
          <div className="status-flow" role="group" aria-label="Outbox message lifecycle">
            <div><span>01</span><strong>pending</strong><small>available for claim</small></div>
            <i>→</i><div><span>02</span><strong>leased</strong><small>owned by one worker</small></div>
            <i>→</i><div><span>03</span><strong>published</strong><small>transport accepted</small></div>
            <b>or</b><div><span>04</span><strong>dead</strong><small>retry budget exhausted</small></div>
          </div>
          <CodeBlock code={outboxOperations} label="Inspect and dispatch" />
          <div className="runtime-grid">
            <article><span>ATOMICITY</span><strong>State + message</strong><p>A failpoint after state write rolls back both records.</p></article>
            <article><span>RECOVERY</span><strong>Lease + replay</strong><p>Expired work is claimable after restart; exact commit replay does not duplicate writes.</p></article>
            <article><span>DELIVERY</span><strong>Retry + dead letter</strong><p>Exponential backoff is bounded; dead messages require explicit requeue.</p></article>
            <article><span>CONSUMER</span><strong>Idempotent inbox</strong><p>A local handler and its message receipt share one SQLite transaction.</p></article>
          </div>
          <div className="warning"><span>!</span><p><strong>HTTP is confirmation-gated.</strong>The endpoint origin must exactly match both <code>--allow-origin</code> and <code>--confirm-network-dispatch</code>. Each request carries the message ID as its idempotency key.</p></div>
        </section>

        <section id="evidence" className="doc-section final-section">
          <p className="section-kicker">18 — Evidence and limits</p>
          <h2>Close the evidence loop</h2>
          <p>Compilation establishes source validity. Runtime receipts establish performed operations. ORODI evaluates those observations against obligations from the relevant environment.</p>
          <div className="evidence-stack">
            <div><span>01</span><p><strong>Source</strong>Formula and contract validation</p><i>valid</i></div>
            <div><span>02</span><p><strong>Runtime</strong>Provider receipt and observation</p><i>observed</i></div>
            <div><span>03</span><p><strong>ORODI</strong>Bound operational evaluation</p><i>evaluated</i></div>
          </div>
          <div className="limits-list">
            <h3>Current implementation boundaries</h3>
            <ul>
              <li><code>in</code> and <code>contains</code> parse without operand-shape validation.</li>
              <li><code>total true</code> checks authored mapping clauses; required target coverage still needs review.</li>
              <li>Permission action membership must be checked by the calling application before runtime invocation.</li>
              <li>AlchLang emits TypeScript today; Python and Rust realizations belong to the separate Craft instantiation CLI, currently distributed under its <code>domainspec</code> compatibility identifier.</li>
              <li>Workflow contracts are statically compiled; durable compensation dispatch is provided by a separate runtime component.</li>
              <li>HTTP dispatch is opt-in; compilation, pattern availability, and local tests grant no deployment authority.</li>
            </ul>
          </div>
          <div className="error-row" role="group" aria-label="Common causal errors">
            {["SOURCE_EXTENSION", "SFOL_PROFILE", "SFOL_FORMULA_TYPE", "UNRESOLVED_REFERENCE", "TYPE_MISMATCH", "OUTPUT_EXISTS", "AUTHORITY_DENIED", "EFFECT_BINDING_REQUIRED"].map((error) => <code key={error}>{error}</code>)}
          </div>
          <div className="next-card" data-theme="console"><p>Try the implementation</p><h3>Edit, validate, build, and run the maintained example.</h3><a href="#workspace">Open the mini workspace <span>→</span></a></div>
        </section>
      </main>

      <ProductFooter tutorial />

      <aside className="toc" aria-label="On this page">
        <p>On this page</p>
        {sections.map((section) => <a key={section.id} href={`#${section.id}`} className={active === section.id ? "active" : ""} aria-current={active === section.id ? "location" : undefined}>{section.title}</a>)}
        <div className="toc-rule" />
        <a href="#quickstart">CLI overview <span>↓</span></a>
        <a href="#sfol">Language overview <span>↓</span></a>
      </aside>

      {searchOpen && <SearchDialog onClose={closeSearch} />}
    </div>
  );
}
