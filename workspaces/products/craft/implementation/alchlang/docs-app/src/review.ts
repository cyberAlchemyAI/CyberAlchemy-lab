const reviewProject = "alchlang-docs";
const reviewSchemaVersion = "alchlang-review-snapshot/v1" as const;

export type ReviewComment = {
  id?: string;
  resolved?: boolean;
  [key: string]: unknown;
};

type AnnotateApi = {
  version: string;
  open(): void;
  comments(): ReviewComment[];
};

type AnnotateConfig = {
  project: string;
  accent: string;
  theme: "auto" | "light" | "dark";
  position: "bottom-right" | "bottom-left";
  startOpen: boolean;
  note: string;
};

export type ReviewSnapshot = {
  schema_version: typeof reviewSchemaVersion;
  project: typeof reviewProject;
  page: {
    href: string;
    pathname: string;
    search: string;
    hash: string;
    title: string;
  };
  viewport: {
    width: number;
    height: number;
    device_pixel_ratio: number;
  };
  tool: {
    name: "reviewjs/annotate";
    version: string;
  };
  summary: {
    total: number;
    open: number;
    resolved: number;
  };
  annotations: ReviewComment[];
};

export type AlchReviewApi = {
  status(): { enabled: true; ready: boolean; error: string | null };
  whenReady(timeoutMs?: number): Promise<AlchReviewApi>;
  open(): boolean;
  snapshot(): ReviewSnapshot;
  json(): string;
};

declare global {
  interface Window {
    Annotate?: AnnotateApi;
    AnnotateConfig?: AnnotateConfig;
    __ALCH_REVIEW__?: AlchReviewApi;
  }
}

export function reviewModeRequested(search: string): boolean {
  const value = new URLSearchParams(search).get("review");
  return value === "1" || value === "true";
}

export function createReviewSnapshot(input: {
  href: string;
  pathname: string;
  search: string;
  hash: string;
  title: string;
  width: number;
  height: number;
  devicePixelRatio: number;
  version: string;
  comments: ReviewComment[];
}): ReviewSnapshot {
  const annotations = input.comments
    .map((comment) => structuredClone(comment))
    .sort((left, right) => String(left.id ?? "").localeCompare(String(right.id ?? "")));
  const resolved = annotations.filter((comment) => comment.resolved === true).length;

  return {
    schema_version: reviewSchemaVersion,
    project: reviewProject,
    page: {
      href: input.href,
      pathname: input.pathname,
      search: input.search,
      hash: input.hash,
      title: input.title,
    },
    viewport: {
      width: input.width,
      height: input.height,
      device_pixel_ratio: input.devicePixelRatio,
    },
    tool: {
      name: "reviewjs/annotate",
      version: input.version,
    },
    summary: {
      total: annotations.length,
      open: annotations.length - resolved,
      resolved,
    },
    annotations,
  };
}

export function reviewSnapshotJson(snapshot: ReviewSnapshot): string {
  return JSON.stringify(snapshot, null, 2);
}

function currentSnapshot(annotate: AnnotateApi): ReviewSnapshot {
  return createReviewSnapshot({
    href: window.location.href,
    pathname: window.location.pathname,
    search: window.location.search,
    hash: window.location.hash,
    title: document.title,
    width: window.innerWidth,
    height: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio,
    version: annotate.version,
    comments: annotate.comments(),
  });
}

export function installReviewMode(): AlchReviewApi | null {
  if (!import.meta.env.DEV || !reviewModeRequested(window.location.search)) return null;
  if (window.__ALCH_REVIEW__) return window.__ALCH_REVIEW__;

  let loadError: string | null = null;

  const bridge: AlchReviewApi = {
    status() {
      return { enabled: true, ready: Boolean(window.Annotate), error: loadError };
    },
    async whenReady(timeoutMs = 10_000) {
      const startedAt = performance.now();
      while (!window.Annotate) {
        if (loadError) throw new Error(loadError);
        if (performance.now() - startedAt >= timeoutMs) {
          throw new Error(`AlchLang review mode did not become ready within ${timeoutMs}ms.`);
        }
        await new Promise((resolve) => window.setTimeout(resolve, 25));
      }
      return bridge;
    },
    open() {
      if (!window.Annotate) return false;
      window.Annotate.open();
      return true;
    },
    snapshot() {
      if (!window.Annotate) throw new Error("AlchLang review mode is not ready.");
      return currentSnapshot(window.Annotate);
    },
    json() {
      return reviewSnapshotJson(bridge.snapshot());
    },
  };

  window.__ALCH_REVIEW__ = bridge;
  window.AnnotateConfig = {
    project: reviewProject,
    accent: "#a9ca3b",
    theme: "auto",
    position: "bottom-right",
    startOpen: false,
    note: "Select text or mark an area, then describe the change you want. Codex can read these comments directly through Playwright.",
  };

  void import("@reviewjs/annotate").catch((error: unknown) => {
    loadError = error instanceof Error ? error.message : String(error);
    console.error("Unable to start AlchLang review mode.", error);
  });

  return bridge;
}

