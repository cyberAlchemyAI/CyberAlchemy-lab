import { describe, expect, it } from "vitest";
import { createReviewSnapshot, reviewModeRequested, reviewSnapshotJson } from "./review";

describe("AlchLang visual review bridge", () => {
  it("requires an explicit review query flag", () => {
    expect(reviewModeRequested("?review=1")).toBe(true);
    expect(reviewModeRequested("?variant=baseline&review=true")).toBe(true);
    expect(reviewModeRequested("?review=0")).toBe(false);
    expect(reviewModeRequested("")).toBe(false);
  });

  it("creates a stable agent-facing snapshot with open and resolved counts", () => {
    const snapshot = createReviewSnapshot({
      href: "http://127.0.0.1:4193/?review=1#overview",
      pathname: "/",
      search: "?review=1",
      hash: "#overview",
      title: "AlchLang Docs",
      width: 1440,
      height: 900,
      devicePixelRatio: 1,
      version: "1.2.0",
      comments: [
        { id: "comment-b", text: "Second", resolved: true },
        { id: "comment-a", text: "First", resolved: false },
      ],
    });

    expect(snapshot.schema_version).toBe("alchlang-review-snapshot/v1");
    expect(snapshot.summary).toEqual({ total: 2, open: 1, resolved: 1 });
    expect(snapshot.annotations.map((comment) => comment.id)).toEqual(["comment-a", "comment-b"]);
    expect(JSON.parse(reviewSnapshotJson(snapshot))).toEqual(snapshot);
  });
});

