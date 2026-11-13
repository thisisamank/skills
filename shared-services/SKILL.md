---
name: shared-services
description: Share admin, email, analytics and playbooks across several products instead of rebuilding them in each. Use when a change touches admin, email, blog, analytics or cross-product links, or when a product joins a shared service.
---

# Shared services

When one person runs several products, build common parts once and let each product plug in.

## Typical shared parts
| Part | Shape | How a product uses it |
|---|---|---|
| Admin | One admin Worker for all products, behind Cloudflare Access, with a folder for each product | Symlink `admin -> ../<admin-repo>` in each product. Read its AGENTS.md before you change it. |
| Email | One notification Worker that owns sending, fallback provider and suppression | The product calls it through the interface that the service documents. |
| Blog writer | Lives in the admin Worker and only drafts. A person publishes. | The product only reads published posts. |
| Analytics | One project, split by a `product` property | The analytics dashboard complements the admin. Do not copy metrics between them. |
| Playbooks | [`saas-seo-playbook`](https://github.com/thisisyashgarg/saas-seo-playbook) and [`pricing-saas`](https://github.com/thisisamank/pricing-saas). Get them as "External skills" in `product-lifecycle` says | Follow them. Add new learnings back. |
| Task app | The user's to-do app with an MCP server, if connected | Read tasks from it, save deferred work as a task, update tasks with findings. |

## Rules
- Onboard a product with wrangler or a CLI. Do not hand the user dashboard steps. Agents will onboard the next product. If no CLI exists, say so.
- Build a feature once in the shared service (for example coupons or plan changes in admin), then add it to each product.
- Promote products to each other where it helps users: a sidebar card, footer links, a landing section. Avoid heavy cross-linking in blog posts.
- Give each shared service an AGENTS.md that explains how other repos use it.
