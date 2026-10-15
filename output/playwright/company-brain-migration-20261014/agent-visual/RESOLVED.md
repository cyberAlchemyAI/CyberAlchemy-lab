# Same-document legacy fragment scrolling resolved

PASS: final narrow confirmation on the updated local build, at 390px light, using `verify=scroll-final-review`.

Changed the hash on the same loaded document through Craft → hero-title → Craft. Each URL canonicalized correctly and each actual target immediately reached the viewport top region:

- #craft → #paper-craft: target top36.34375, scrollY3588.
- #hero-title → #paper-hero-title: H1 top20.125, scrollY492.
- #craft → #paper-craft again: target top36.34375, scrollY3588.

The issue recorded in CONFIRMATION.md is resolved by this build. No source edits performed. Evidence: scroll-final-review.log and resolved-1-craft.png, resolved-2-hero-title.png, resolved-3-craft.png. Owned browser closed after capture.
