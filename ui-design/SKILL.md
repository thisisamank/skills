---
name: ui-design
description: Entry point for all UI and visual design work - builds or redesigns UI through impeccable, picks the right reference list (landing pages, product UI, mobile apps, sections and components, motion, type and brand), and applies the fixed UI rules. Use for any UI build or redesign, when looking for design inspiration or references, and when the user sends a screenshot of a broken or poor screen.
---

# UI design

This skill sets the direction and picks the references. The `impeccable` skill does the design work.

## Steps
1. Load the `impeccable` skill with the Skill tool. Follow its process for the whole task.
2. Pick the reference list for the job (table below). Files under `references/` are in this skill's folder; read only the one you need. Pick one primary reference from it.
   - App screens: also match the product's own landing page, so the app and the site feel like one product.
3. Give impeccable the product facts: who uses it, the main job, brand colours and fonts, and the chosen reference with screenshots.
4. Apply `ui-rules` to every screen. Use `design-engineering` for motion and interaction details.
5. For a large change or an open direction, make a local HTML mockup first (see `mockup-before-build`).
6. Make the result visible in the user's running dev server.

## Which reference list
| The job | Read |
|---|---|
| A whole landing page, marketing site or client website, any industry | `landing-page-inspiration` |
| Screens inside a web product: dashboard, settings, onboarding, tables, empty states | `references/product-ui.md` |
| Mobile app screens, app icon or store screens | `references/mobile-app.md`, then the design loop in `flutter-app` |
| One section (hero, navbar, pricing, CTA, footer) or one component | `references/section-component.md` |
| Animation ideas: text, scroll, 3D, transitions, backgrounds, sounds | `references/motion.md` |
| Fonts, pairing, colour palettes, logos, brand identity | `references/type-brand.md` |
| Claude design skills, AI design generators, style extractors, screenshot tools | `references/tools.md` in this skill |

Not sure of the vibe yet: start with [Pinterest](https://www.pinterest.com/) or [Designeer](https://www.designeer.xyz/) with the user or client, then pick a list.

## Using references
1. Collect screenshots of the parts you like. Open the live site in a headless browser; do not work from memory. If it does not load, use `web-fetch-fallback`.
2. For each one, write exactly what to take: "the spacing on this hero", "how the pricing cards stack on the phone". A reference without a note gets copied whole.
3. Tell the user which reference you picked and why, in one or two lines.
4. Copy the structure, rhythm and quality bar. Do not copy text, logos, product names, photos or illustrations.
5. Check the licence before you ship a font, component, sound or background. Many sites mix free and paid.

## Screenshot feedback
1. Find every issue in the screenshot, not only the marked one.
2. Fix the root UX problem. Rethink the experience. Do not patch it.
3. A layout can fail by having too much or too little. Change the amount of detail, not only the style.
4. Check 360, 768 and 1280 px before you report.
