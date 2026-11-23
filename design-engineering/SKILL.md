---
name: design-engineering
description: The craft bar for UI polish - component feel, press and hover states, shadows, borders, typography details, icons, springs, Apple-style fluid interfaces and materials, and accessibility. Use when building or reviewing a component or screen that must feel finished, when the user says it "feels off" or asks to polish it, and with ui-design. For animation work itself, the user runs /motion.
---

# Design engineering

One skill with three guides. Each guide is a folder next to this file. Read only the guide you need.

## Pick the guide
| The job | Guide |
|---|---|
| Build or review a component's interactions and feel: animation decisions, springs, clip-path, drag details, the Sonner principles, review format | `core/GUIDE.md` (the main guide; start here when unsure) |
| A fast polish pass on visual details: radius, shadows, borders, optical alignment, tabular numbers, image outlines, icons, enter and exit details | `make-interfaces-feel-better/GUIDE.md` and its topic files (`surfaces.md`, `typography.md`, `icons.md`, `animations.md`, `performance.md`) |
| Apple-style interfaces: fluid physical motion, interruptible gestures, momentum, materials and depth, optical type, the design foundations | `apple-design/GUIDE.md` |

For a full review, use `core` for the review format and add the checks from `make-interfaces-feel-better`.

## Names inside the guides
The guides were separate skills before. A mention of `make-interfaces-feel-better`, `apple-design` or `emil-design-eng` means a guide in this skill. Mentions of `animate`, `choreograph`, `gestures`, `review-animations` and other motion names mean the guides of the `motion` skill. That skill is hand-called: read `~/.claude/skills/motion/<name>/GUIDE.md` directly, or ask the user to run `/motion`.

## Works with
- `ui-design` sets the direction and the reference. `ui-rules` sets the fixed rules. This skill sets the craft bar.
- `break-ui` stress-tests the result with worst-case data.
