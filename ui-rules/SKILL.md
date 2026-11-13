---
name: ui-rules
description: Fixed UI rules for every screen - loading states, long tasks, login, asset grids, layout checks and dark mode. Use with ui-design and landing-page-inspiration, and when building any button, loader, form, login, asset grid or long-running task UI.
---

# UI rules

## Ease
- Test: can a non-technical, older person finish the main task in a few clicks? Remove friction. Use the fewest clicks.
- Keep important options visible. Do not hide them in a generic overflow menu.
- Use real icons. Do not use dots as the only marker. Group lists under subheadings.
- Design the hard cases: 10+ items, empty state, long names, too many header items.

## Feedback and state
- Every button that starts work shows a loading state inside the button. Show one loader at a time.
- Page loaders are consistent and centered. Handle every error state.
- Save buttons stay disabled until there is a change.
- Long work (import, publish, generate) shows the steps, the elapsed time, and a notice when it takes longer than usual. It runs in the background, so the user can leave the page. Send an email when it finishes.
- No flicker on swaps or streamed chat. Fix the cause, not with an animation.

## Standard screens
- A signed-in visitor sees "Dashboard", not "Sign in".
- Login has two columns: the auth form on one side, a product graphic or animation on the other.
- Asset grids (logos, images, illustrations, fonts) start with an "Upload" card. Each item can be removed or replaced on its own.
- Users can reverse a visible state (unshare a link, take a site offline) from where they see it.

## Layout
- The app fits the viewport. No stray vertical scroll on dashboards.
- Check 360, 768 and 1280 px. No horizontal scroll. Text 12 px minimum. Touch targets 44 px minimum.
- Dark mode follows the system and has a toggle. Check mobile headers in dark mode.

## Content
- No founder phone numbers or personal details in the UI.
- Show imported text in lowercase when uppercase looks loud. Let the user change it.
