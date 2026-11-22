# Working-style skills

Small skills for building and running several SaaS products on Cloudflare Workers with Claude Code. They encode one way of working: spec first, micro commits on main, secrets through noenv, impeccable for UI, and shared services across products.

Start with `product-lifecycle`. It maps every stage of a product to the skill to use.

Two skills are git submodules:
- [`pricing-saas`](https://github.com/thisisamank/pricing-saas): unit economics, cost at scale, plan tiers, HTML report.
- [`saas-seo-playbook`](https://github.com/thisisyashgarg/saas-seo-playbook) (branch `launch-on-claude`): SEO, AI search, launch sites, ChatGPT and Claude directories.

Clone with `git clone --recurse-submodules`. In an existing clone, run `git submodule update --init`.

To use one, copy or symlink its folder into `~/.claude/skills/`.

| Skill | Use it when |
|---|---|
| pricing-saas | unit economics, cost at scale, plan tiers, HTML report |
| ste-writing | language rules for every reply and doc |
| product-lifecycle | idea to launch to growth; which skill at which stage |
| ship-it | commit, merge, deploy |
| noenv-secrets-to-workers | run commands with secrets and push them to Workers without printing them |
| flutter-app | Flutter app structure, HTML-first design loop, device testing |
| ui-design | any UI work or screenshot feedback; runs impeccable |
| landing-page-inspiration | 15 reference landing pages; pick one for the product |
| design-engineering | motion, interaction and polish craft rules |
| ui-rules | fixed UI rules for every screen |
| mockup-before-build | HTML mockup or checkbox approval page first |
| spec-driven-change | features in repos with PRD/SPEC/AGENTS |
| new-saas-bootstrap | start a new product |
| shared-services | admin, email, analytics and playbooks shared across products |
| mcp-marketplace-launch | MCP server and Claude/ChatGPT listing |
| ai-model-switch | compare or change AI models |
| web-fetch-fallback | 403 on research pages |
| local-dev-hygiene | ports, local D1, dev server |
| code-structure-pass | review, ponytail, restructure |
| low-level-design | how to write code: order of work, objects, APIs, concurrency, tests, pattern triggers |
| feature-pushback | discuss a feature before building |
| traffic-ceiling | how much organic traffic a product can reach, and what it is worth; Search Console plus Keyword Planner through the user's browser |
| 3d-mascot-designer | design, build and animate a 3D product mascot; preview page, GLB, Blender and app integration |
