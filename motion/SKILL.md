---
name: motion
description: All animation and motion work in one place - build, choreograph, gestures, React Native and Expo, performance, naming an effect, and auditing, adding, removing or reviewing motion. Run it as /motion followed by the job, for example "/motion animate the modal" or "/motion review".
disable-model-invocation: true
---

# Motion

One skill with ten guides. Each guide is a folder next to this file with a `GUIDE.md` and sometimes extra files (`RECIPES.md`, `STANDARDS.md`, `AUDIT.md`, `PLAN-TEMPLATE.md`).

## Pick the guide
If the first word after `/motion` is a guide name, use that guide. Otherwise pick from the user's words with this table. Read only the guide you need, then follow it fully.

| The job | Guide |
|---|---|
| Build one animation or transition on the web | `animate/` |
| Several elements move together: stagger, sequence, hero entrance, view swap | `choreograph/` |
| The finger drives it: drag, swipe, fling, sheets, snap points, pull to refresh | `gestures/` |
| Any motion, gesture or haptic in React Native or Expo | `animate-expo/` |
| It stutters, drops frames or is janky; which property to animate | `animation-performance/` |
| "What is it called when…" - name an effect | `animation-vocabulary/` |
| Review the motion in a diff or a component against a strict bar | `review-animations/` |
| Audit the motion of a whole codebase and write fix plans | `improve-animations/` |
| It feels static: find what should animate | `find-animation-opportunities/` |
| It feels slow or over-animated: remove motion | `remove-animations/` |

If the user is not sure between the last three, ask one question: is the problem *bad* motion, *missing* motion, or *too much* motion?

## Names inside the guides
The guides were separate skills before. When a guide says "use `animate`" or "that's `review-animations`", it means the guide folder with that name in this skill. Read that `GUIDE.md`. Do not try to load it as a skill.

## Related skills
- `design-engineering` for the general craft bar for UI polish, springs and interaction details.
- `ui-design` (its `references/motion.md`) for motion ideas, scroll sites, backgrounds and UI sounds.
- `mobile-native` for a web app that must feel native on a phone.
