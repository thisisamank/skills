---
name: spec-driven-change
description: Keep code, SPEC.md and PRD.md in step, with requirement IDs and ASD-STE100 writing. Use when building a feature in a repo that has PRD.md, SPEC.md and AGENTS.md.
---

# Spec-driven change

1. Read AGENTS.md (or CLAUDE.md), then the SPEC section for the area.
2. For a new feature, write the SPEC requirements first, in ASD-STE100, with new IDs (`AREA-NN`). For a large feature, show the plan and the requirements, then build.
3. Build. If the code must differ from SPEC, change SPEC in the same change set.
4. Change PRD when a product decision changes (for example a new launch market).
5. Update the landing page when a feature is visible to users.
6. Update the product facts file (prices, limits, features) when one of them changes. The blog writer in the [`saas-seo-playbook` chapter 4](../saas-seo-playbook/docs/04-automated-blog-writer.md) reads it.
7. Commit with the requirement ID (see `ship-it`).

## Writing
- SPEC, PRD, AGENTS.md, reports and commit bodies follow the STE writing rules in `~/.claude/CLAUDE.md`.
- No inline code comments.
- Easy to read beats complete.
