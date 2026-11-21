---
name: mockup-before-build
description: Make a local HTML mockup or a checkbox approval page before building. Use only when the user asks for a mockup or approval page, or before building a mobile app UI. Do not use for web work. The user checks web work with npm run dev.
---

# Mockup before build

## When to use
- Use this skill when the user asks for a mockup or approval page.
- Use it before you build a mobile app screen.
- Do not use it for web. Build the web UI directly. The user runs `npm run dev`.

## Two kinds of page
1. **Design mockup.** One static `.html` file that shows the screen with realistic data. The user reviews it and asks for changes. Iterate.
2. **Approval page.** One `.html` file with a checkbox and a notes box for each feature or option, in sections, with requirement IDs. A button copies the result as Markdown. The user pastes it back. Checked means build. A note is a decision.

## Rules
- Write a plain local `.html` file. Do not publish it unless the user asks.
- Open it for the user (`open file.html`).
- Show the hard cases: 10+ items, empty state, long names.
- When the approval Markdown comes back, build only the checked items and follow every note.
- When the list changes later, regenerate the page and drop what is already built.
- Approval of the mockup means start building now.
- For pricing, the approval page shows plan permutations so the user can place each feature in a plan.
