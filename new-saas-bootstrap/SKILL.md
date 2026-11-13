---
name: new-saas-bootstrap
description: Start a new SaaS product on Cloudflare Workers with research, PRD, SPEC and AGENTS.md. Use when the user shares a product idea and wants it bootstrapped.
---

# New SaaS bootstrap

## Step 1: research and name
- Research the market, competitors, legal points and the technical approach. Cite sources in `docs/RESEARCH.md`.
- Check the name. If the domain or name belongs to a product that does the same thing, propose short, simple, available names. The user picks.

## Step 2: files
Create a sibling folder next to the user's other products with:
- `PRD.md`: why, who, scope, out of scope. Easy to read.
- `SPEC.md`: behaviour with requirement IDs, in ASD-STE100. Source of truth.
- `AGENTS.md`: read-first table, commands table, layout, rules, production facts. `CLAUDE.md` points to it.
- An approval page if scope is open (see `mockup-before-build`).

## Default stack
- Cloudflare primitives first, on Workers. Use an outside service only when no Cloudflare product fits. Choose storage and background services for each feature from the Cloudflare docs and Cloudflare skills, not by habit (see "How to build each feature" in `product-lifecycle`).
- Web: Next.js on vinext, TypeScript, CSS Modules with design tokens. Mobile: Flutter (see `flutter-app`).
- Sign-in: email magic link or email code through Cloudflare Email Service. Add Google sign-in later.
- Payments: Dodo Payments, one brand for each product. All plans in one file.
- Analytics: one PostHog project for all products, split by a `product` event property.
- AI: the latest fast Gemini model by default. Log the cost of each call.
- Secrets: noenv.
- Admin, email and blog: plug into the shared services (see `shared-services`).
- Pricing: run [`pricing-saas`](https://github.com/thisisamank/pricing-saas) before you set plans.
- SEO: follow [`saas-seo-playbook`](https://github.com/thisisyashgarg/saas-seo-playbook) from the first public page.

To get these two, follow "External skills" in `product-lifecycle`. For the stages after bootstrap, see `product-lifecycle`.

## Step 3: domain
- When the domain is on the user's Cloudflare account, set it up with wrangler: custom domain, `www` redirect, Email Sending, DMARC, and Email Routing for `support@`, `abuse@` and `security@`.
