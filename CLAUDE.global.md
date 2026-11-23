# Global rules

This file is linked to `~/.claude/CLAUDE.md`. It applies to every session.

## Writing: STE

Write in ASD-STE100 Simplified Technical English. Follow it about 80% of the time. The other 20% is room for names and terms that must stay exact.

### Applies to
- Chat replies, reports, summaries and plans.
- SPEC.md, PRD.md, AGENTS.md, README files and other docs.
- Commit messages, PR bodies and task descriptions.
- Text in HTML reports and approval pages.

### Rules
- Short sentences. At most 20 words for an instruction and 25 words for a description.
- One instruction per sentence.
- Active voice. Simple present or simple past tense.
- Write instructions in the imperative ("Run the migration.", not "The migration should be run.").
- Use plain words that have one meaning. Use the same word for the same thing every time.
- Use articles ("the", "a"). Do not stack more than three nouns.
- Use lists for steps and conditions. Number the steps.
- Give the result first, then the details.

### Keep exact
- Product names, technical terms, code, commands, file paths, identifiers and quoted text stay as they are, even when they are not STE words.

### Tone
- Direct and short. No filler, no corporate words.
- State trade-offs. Say clearly when something failed or was not done.

### Example
- Not this: "It might be worth considering the possibility of running the migrations prior to deployment in order to avoid potential issues."
- This: "Run the migrations before you deploy. If you do not, the deploy fails."

## Skills with guides
- `motion` and `design-engineering` hold several guides, one folder each. A reference like `motion/animate` means the file `~/.claude/skills/motion/animate/GUIDE.md`. Read that file directly.
- `motion` is hand-called. Do not try to load it with the Skill tool. Read the guide file, or ask the user to run `/motion <guide>`.
