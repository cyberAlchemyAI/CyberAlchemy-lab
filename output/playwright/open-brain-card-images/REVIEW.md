# Homepage card images

Added three generated editorial illustrations to the local preview's Marketing, Customer support and Sales handoff cards. Artwork follows the established engraving, warm paper and crimson direction. Existing card copy and destinations remain.

Selected assets are stored in the preview's `assets/card-images/` with a source/hash manifest. Responsive 480px/960px WebP variants, explicit dimensions, lazy loading and asynchronous decoding keep the images below the opening lightweight. The illustrations are decorative metaphors; empty image alternative text leaves the card heading and action as its accessible meaning. Images remain on their paper surface in dark appearance; colors are not inverted.

Chromium checks passed at 320, 390, 768 and 1440px in both themes: all three images load, no horizontal page overflow, all original destinations retained, action targets44px. Final card-grid screenshots at1440light and390dark were visually inspected. See `browser-checks.txt` and `card-grid-*.png`.

Static verification:513 HTML pages; zero missing internal files/fragments/assets or duplicate IDs in recomposed pages. All2,271 maintained baseline files remain unchanged. No publication or live host changes.
