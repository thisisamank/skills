---
name: code-structure-pass
description: Review and restructure code to a fixed standard - TypeScript, Next.js on vinext, folders, tokens, explicit states - using the ponytail review. Use when the user asks for a code review, a diff cleanup, a restructure, a Next.js migration, or a hunt for implicit state machines.
---

# Code structure pass

## Standard
- TypeScript everywhere. Web is Next.js on vinext. No HTML, CSS or JS in strings. No `innerHTML`.
- Organize by folders. Many files flat in `src/` is wrong. Deep nesting for its own sake is also wrong.
- Create a shared package only when two or more apps use the code.
- No hardcoded colours or fonts. A `design-system` package holds `core` tokens and one folder for each theme.
- No inline comments.
- Prefer clear models: a base class with its parts at the root level beats a bag of optional extras. Do not reuse names that clash with framework terms (for example React "components").

For Flutter code, use the rules in `flutter-app`.

## Review
1. Run the `ponytail` review for over-engineering and repetition. Review only the diff when the user asks for that.
2. Show findings first. Clean up after the user agrees.
3. Implicit state machines: find status flags and boolean combinations that hide states. List them. Fix them one by one with explicit states and transitions.

## Large migrations
- Plan, get the user's choices (runtime, big-bang or step by step), then let `sonnet` subagents port while you review each part.
- Benchmark only after the migration is complete.
- Treat performance as a feature. Measure before and after.
