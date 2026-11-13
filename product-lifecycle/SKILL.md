---
name: product-lifecycle
description: The full path of a SaaS product from idea to a launched, priced, findable and growing product, with the skill to use at each stage. Use when starting a product, when asking "what is next for this product?", or to find where a product stands and what stage comes after.
---

# Product lifecycle

A product moves through these stages in order. Later stages loop. Each stage names the skill or playbook that does the work.

This skill describes what the user of the product experiences at each stage. It does not choose the architecture.

## How to build each feature
- Build on Cloudflare primitives first: compute, storage, state, background work, email, AI, auth at the edge, and domains. Look for a Cloudflare product before you look anywhere else.
- Use an outside service only when no Cloudflare primitive fits the need (for example a payment provider or a model Cloudflare does not offer). Say in one line why Cloudflare does not cover it.
- Do not pick a platform primitive by habit. Do not add a queue, a workflow or any other service for its own sake.
- For each feature, read the Cloudflare documentation and the Cloudflare skills (for example `cloudflare`, `workers-best-practices`, `durable-objects`, `agents-sdk`) to find the best fit. Use the Cloudflare docs search tool when it is available.
- Start from the experience the feature must give. Then choose the simplest design that gives it. Say in one line why you chose it.

To find where a product stands, read PRD.md and SPEC.md, list what is built and what is not, and name the next stage. Report it as two short lists: built and not built.

## External skills
Two stages use skills from other repos. Before you use one, find it or get it:
1. Look for it installed: `~/.claude/skills/<name>` or the project's `.claude/skills/<name>`.
2. Look for a clone next to the current repo (`../<name>`).
3. If neither exists, clone it: `git clone <url> ~/.claude/skills/<name>`.

| Name | URL | What it does |
|---|---|---|
| `pricing-saas` | https://github.com/thisisamank/pricing-saas | Unit economics, cost at 100 to 1,000,000 users, plan tiers, HTML report |
| `saas-seo-playbook` | https://github.com/thisisyashgarg/saas-seo-playbook | SEO, AI search, launch sites, ChatGPT and Claude directories |

Read a playbook chapter from the local copy: `saas-seo-playbook/docs/<chapter>.md`.

## 1. Idea to bootstrap
- Research the market, rivals and legal points. Check the name and domain.
- Write PRD, SPEC (ASD-STE100) and AGENTS.md. No review gate.
- Put open scope on an approval page and build only what the user checks.
- Skills: `new-saas-bootstrap`, `mockup-before-build`.

## 2. Core build
- Build the core flow end to end from SPEC, one requirement group at a time.
- Test on real inputs. Stay generic: test data is a sample, not the product.
- Users never wait on a frozen screen. Slow work continues when they leave the page, and they can see its progress when they come back.
- Skills: `spec-driven-change`, `ship-it`, `local-dev-hygiene`. For a mobile app, `flutter-app`.

## 3. Domain, landing page, first deploy
- Set up the domain on Cloudflare with wrangler. Deploy every Worker.
- Build the landing page from one reference. Build the app screens to match it.
- Skills: `ui-design`, `landing-page-inspiration`, `ui-rules`.

## 4. Accounts and first-run experience
- Sign-in takes one email and one click or code. Google sign-in comes next.
- Users get an email at sign-in, after onboarding, and when a slow job finishes.
- Onboarding: a short, simple flow that collects profile data (individual or business), creates one example item, and guides the user to it on the dashboard. Prompt the user to share it with someone.
- Skills: `shared-services`, `ui-rules`.

## 5. Visibility for the owner
- The owner can see who signs up, who pays, what users do, and what each AI call costs.
- The owner sees this in the shared admin dashboard and the analytics dashboard, without duplication.
- Skills: `shared-services`, `ai-model-switch`.

## 6. Quality pass
- Loading and error states everywhere. Hunt implicit state machines and fix them.
- Every screen feels fast. Measure, then fix the slowest paths.
- Every screen works at three widths, in dark mode, and on a phone.
- The code stays easy to change, so the next stages stay fast.
- Skills: `code-structure-pass`, `ui-rules`. For a mobile app, `flutter-app` (structure, state, testing layers).

## 7. Pricing and billing
- Measure the unit economics and the cost at 100 to 1,000,000 users. Get a plan recommendation as an HTML report.
- Let the user choose plan contents on an approval page.
- Users can upgrade, downgrade, cancel and see what is left in their quota. The owner can give coupons and change a user's plan.
- While the payment account waits for verification, give all features free and cap only the costly AI actions.
- Skill: [`pricing-saas`](https://github.com/thisisamank/pricing-saas) (see External skills).

## 8. SEO and launch
- Remove personal details from public pages. Blog posts use a company author.
- Follow the SEO playbook in order: foundations, indexing, page programs, blog writer, AI search, off-page, measurement.
- Make launch assets (logo, gallery images) yourself. Only a demo video needs the user.
- Promote the user's other products where it helps users.
- Playbook: [`saas-seo-playbook`](https://github.com/thisisyashgarg/saas-seo-playbook), chapters 1 to 7 (see External skills).

## 9. AI app directories
- Users can use the product from inside Claude and ChatGPT, and they find it in those directories.
- Skill: `mcp-marketplace-launch`. Playbook: [`saas-seo-playbook` chapter 8](https://github.com/thisisyashgarg/saas-seo-playbook/blob/main/docs/08-ai-app-directories.md).

## 10. Evolve (loop)
- Pick the next features from a feature-gap list or user feedback. Push back on features nobody asked for.
- Typical growth steps: teams and seats, branding, templates, more countries and languages (one hand-edited source file, generated translations), integrations.
- Each visible feature updates SPEC, the landing page and the product facts. Trim the landing page when it grows too long.
- Revisit pricing when features or costs change. Re-check rival facts every quarter.
- Save deferred work in the user's task app if one is connected.
- Skills: `feature-pushback`, `spec-driven-change`, `ship-it`.
