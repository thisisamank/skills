---
name: ui-design
description: Design or redesign UI through the impeccable skill, with a chosen reference and fixed UI rules. Use for any UI build or redesign, and when the user sends a screenshot of a broken or poor screen.
---

# UI design

This skill sets the direction. The `impeccable` skill does the design work.

## Steps
1. Load the `impeccable` skill with the Skill tool. Follow its process for the whole task.
2. Pick the reference:
   - Landing or marketing page: load `landing-page-inspiration` and pick one reference from it.
   - App screens (dashboard, editor, settings): match the product's own landing page, so the app and the site feel like one product.
   - Mobile app screens: follow the design loop in `flutter-app`.
3. Give impeccable the product facts: who uses it, the main job, brand colours and fonts, and the chosen reference.
4. Apply `ui-rules` to every screen. Use `design-engineering` for motion and interaction details.
5. For a large change or an open direction, make a local HTML mockup first (see `mockup-before-build`).
6. Make the result visible in the user's running dev server.

## Screenshot feedback
1. Find every issue in the screenshot, not only the marked one.
2. Fix the root UX problem. Rethink the experience. Do not patch it.
3. A layout can fail by having too much or too little. Change the amount of detail, not only the style.
4. Check 360, 768 and 1280 px before you report.
