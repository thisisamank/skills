# Structure pass: review and restructure

## Standard
- TypeScript everywhere. Web is Next.js on vinext. No HTML, CSS or JS in strings. No `innerHTML`.
- Organize by folders. Many files flat in `src/` is wrong. Deep nesting for its own sake is also wrong.
- Create a shared package only when two or more apps use the code.
- No hardcoded colours or fonts. A `design-system` package holds `core` tokens and one folder for each theme.
- No inline comments.
- Prefer clear models: a base class with its parts at the root level beats a bag of optional extras. Do not reuse names that clash with framework terms (for example React "components").

For Flutter code, use the rules in `flutter-app`.

For logic and object design, the main `SKILL.md` of this skill is the standard. For TypeScript, also read `typescript.md` in this folder.

## Review
1. Run the `ponytail` review for over-engineering and repetition. Review only the diff when the user asks for that.
2. Check the code against the rules in `SKILL.md` and `smells.md` in this folder. Report each smell with the fix from that file.
3. Show findings first. Clean up after the user agrees.
4. Implicit state machines: find status flags and boolean combinations that hide states. List them. Fix them one by one with explicit states and transitions.

## Large migrations
- Plan, get the user's choices (runtime, big-bang or step by step), then let `sonnet` subagents port while you review each part.
- Benchmark only after the migration is complete.
- Treat performance as a feature. Measure before and after.
