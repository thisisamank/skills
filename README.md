# Working-style skills

Skills for Claude Code. They encode one way to build and run SaaS products on Cloudflare Workers, and to design client websites and apps: spec first, micro commits on main, secrets through noenv, impeccable for UI, and shared services across products.

Start with `product-lifecycle` for product work and `ui-design` for design work.

## Install

1. Clone with submodules:
   ```sh
   git clone --recurse-submodules https://github.com/thisisamank/skills
   ```
   In an existing clone, run `git submodule update --init`.
2. Link each skill folder into `~/.claude/skills/`. A link (not a copy) makes every edit in this repo live at once:
   ```sh
   for d in */; do [ -f "$d/SKILL.md" ] && ln -sfn "$PWD/${d%/}" ~/.claude/skills/; done
   ```
3. Link the global rules:
   ```sh
   ln -sfn "$PWD/CLAUDE.global.md" ~/.claude/CLAUDE.md
   ```
4. Start a new Claude Code session. Run `/context` to see the loaded skills.

Two skills are git submodules:
- [`pricing-saas`](https://github.com/thisisamank/pricing-saas): unit economics, cost at scale, plan tiers, HTML report.
- [`saas-seo-playbook`](https://github.com/thisisyashgarg/saas-seo-playbook) (branch `launch-on-claude`): SEO, AI search, launch sites, ChatGPT and Claude directories. It is a playbook, not a skill folder. Skills point to it.

## How the skills work

There are three kinds:

| Kind | How it runs | Examples |
|---|---|---|
| **Auto** | Claude reads the description of every auto skill in each session and loads one when your request matches. You can also run it with `/<name>`. | `ui-design`, `low-level-design`, `design-engineering` |
| **Hand-called** | It has `disable-model-invocation: true`. Claude does not see it and does not pick it. You run it with `/<name>`. | `/ship-it`, `/motion`, `/pricing-saas` |
| **Global rules** | `CLAUDE.global.md` loads in every session. It is not a skill. | STE writing |

Some skills hold **guides**: one folder per guide, each with a `GUIDE.md`. The skill's `SKILL.md` is a short router that picks the guide. Only that guide loads.
- `motion/<guide>/GUIDE.md`: ten motion guides.
- `design-engineering/<guide>/GUIDE.md`: three polish guides.
- `ui-design/references/*.md`: six reference lists.
- `low-level-design/references/*.md`: patterns, smells, TypeScript, the structure pass and worked designs.

A reference like `motion/animate` in any skill means the file `~/.claude/skills/motion/animate/GUIDE.md`.

## Common requests

| You say | What runs |
|---|---|
| "Build a landing page for a bakery client" | `ui-design` → `landing-page-inspiration` |
| "Design the settings screen" | `ui-design` → `references/product-ui.md` |
| "Design the onboarding for our mobile app" | `ui-design` → `references/mobile-app.md` → `flutter-app` |
| "Find me a pricing section / a font / a logo idea" | `ui-design` → the matching reference list |
| "This button feels off" / "polish this card" | `design-engineering` |
| `/motion animate the modal` | `motion` → `animate` guide |
| `/motion it stutters` | `motion` → `animation-performance` guide |
| `/motion review` | `motion` → `review-animations` guide |
| "Try the worst case on this table" | `break-ui` |
| "Should we add team accounts?" | `feature-pushback` |
| "Where is this product, what is next?" | `product-lifecycle` |
| "Review this diff" / "restructure this folder" | `low-level-design` → `references/structure-pass.md` |
| `/ship-it` | commit, merge and deploy |

Not sure which skill fits? Run `/ask-emil` for UI and motion work, or `/product-lifecycle` for product work.

## Skills

### Product and process
| Skill | Kind | Use it for |
|---|---|---|
| product-lifecycle | auto | idea to launch to growth; which skill at which stage |
| new-saas-bootstrap | hand-called | start a new product: research, PRD, SPEC, AGENTS.md |
| feature-pushback | auto | an opinion on one feature before you build it |
| spec-driven-change | auto | features in repos with PRD, SPEC and AGENTS |
| pricing-saas | hand-called | unit economics, cost at scale, plan tiers, HTML report |
| traffic-ceiling | hand-called | how much organic traffic a product can reach, and what it is worth |
| mcp-marketplace-launch | hand-called | MCP server and Claude or ChatGPT directory listing |
| ai-model-switch | hand-called | compare or change AI models |
| shared-services | auto | admin, email, analytics and playbooks shared across products |

### Code
| Skill | Kind | Use it for |
|---|---|---|
| low-level-design | auto | write, review and restructure code: objects, APIs, concurrency, tests, patterns, repo standard |
| write-swift | auto | modern Swift and Swift 6 concurrency |
| flutter-app | auto | Flutter app structure, HTML-first design loop, device testing |
| ship-it | hand-called | commit, merge, deploy (micro commits, no AI attribution) |
| noenv-secrets-to-workers | auto | run commands with secrets; push them to Workers without printing them |
| local-dev-hygiene | auto | ports, local D1, dev server |
| web-fetch-fallback | auto | a research page returns 403 or empty content |

### UI and design
| Skill | Kind | Use it for |
|---|---|---|
| ui-design | auto | entry point for any UI work; runs impeccable and picks the reference list |
| landing-page-inspiration | auto | ~115 reference sites by client industry, plus galleries |
| ui-rules | auto | fixed rules for every screen |
| design-engineering | auto | UI polish craft bar (core, polish checklist, Apple-style) |
| mobile-native | auto | a web app that must feel native on a phone |
| break-ui | auto | stress-test UI with worst-case data |
| mockup-before-build | auto | HTML mockup or approval page first (mobile app UI) |
| ask-sonner | auto | Sonner toasts |
| 3d-mascot-designer | hand-called | design, build and animate a 3D product mascot |
| motion | hand-called | `/motion <job>`: build, choreograph, gestures, Expo, performance, naming, review, audit, add or remove motion |
| prototype | hand-called | several versions of a UI piece behind a live picker |
| pick-ui-library | hand-called | pick a frontend library from a curated list |
| learn-taste | hand-called | turn a session's design corrections into written rules |
| ask-emil | hand-called | router: which UI or motion skill fits |

## Add a new skill

The more skills Claude can pick from, the more often it picks the wrong one. Keep the list small and clear.

1. **Check for overlap first.** If an existing skill covers the area, add a guide or a reference file to it. Do not make a new skill.
2. **Pick the kind.** If you always run it on purpose (deploy, reports, audits), make it hand-called. Rules for every session go in `CLAUDE.global.md`.
3. **Write a short description.** About 200 to 300 characters: what it does, then "Use when…". Name the nearby skill it is not. Do not list trigger words.
4. **Keep `SKILL.md` short.** Under about 300 lines. Put long details in reference files and say when to read each one.
5. **Link it** into `~/.claude/skills/` and add it to the tables above.
6. **Test it.** Try three to five prompts that should load it and two that should load a nearby skill. Run `/context` now and then to check the skills list size.
