
# Product UI references

For screens inside a product. For the marketing site use `landing-page-inspiration`. For phone apps read `mobile-app.md` in this folder.

## How to use
1. Name the screen and its one job: "list of invoices, find and pay one", "first-run onboarding, connect a data source".
2. Pick one product from "Products to study" that solves the same job well. Open it (or its public screenshots and docs) and take screenshots of that flow, not only the first screen. Include the empty, loading and error states when you can find them.
3. Use the galleries below to see more variants of the same screen type. Search by screen name ("settings", "billing", "onboarding", "table").
4. Match the product's own landing page so the app and the site feel like one product (see `ui-design`).
5. Hand the reference to `impeccable`. Apply `ui-rules` and `design-engineering`.
6. Copy the flow and the quality bar. Do not copy the brand.

## Products to study
| Product | Study it for |
|---|---|
| linear.app | Lists, keyboard shortcuts, command menu, issue detail, calm dark UI |
| attio.com | Data tables, record pages, filters, relationship views |
| notion.com | Blocks, slash menu, empty pages that teach |
| stripe.com (dashboard and docs) | Billing, settings, forms, dense data made calm |
| vercel.com (dashboard) | Deploy logs, project lists, status, monochrome system |
| raycast.com | Command palette, search-first UI, extensions |
| cal.com | Booking flow, availability editor, settings |
| superhuman.com | Speed, onboarding that trains shortcuts |
| posthog.com | Analytics dashboards, charts, many products in one shell |
| cursor.com, claude.ai | AI chat, streaming output, inline diffs |
| figma.com | Toolbars, panels, canvas UI |
| mercury.com | Banking: transactions, cards, trust in every detail |

## Galleries for product screens
| Site | Use it for |
|---|---|
| [60fps](https://60fps.design/) | 2,000+ animation clips from the best apps and websites; see real interaction flows |
| [Collect UI](https://collectui.com/) | Hand-picked interfaces by screen type, updated weekly |
| [Godly](https://godly.design/) | Hand-picked web, app and UI design |
| [Dribbble](https://dribbble.com/) | Search the exact screen: "settings page", "empty state", "billing". Concepts only; check that it works with real data |
| [Refero Styles](https://styles.refero.design/) | Design systems from real products as files for Claude Code |
| [DesignMD](https://designmd.me/) | Get a product's colours, fonts and spacing as a file |
| [Mobbin](https://mobbin.com/) (not on the source list) | Largest library of real web and app flows by screen and pattern |

## Details and interactions
| Site | Use it for |
|---|---|
| [details.so](https://www.details.so/inspo) | Little details: transitions, micro-interactions. Press Copy for AI |
| [Design Spells](https://designspells.com/) | Small UI details that make a product feel expensive |
| [Bencho Finds](https://bencho.dev/finds) | 100+ UI interaction clips from designers |
| [Amicro loaders](https://amicro.vercel.app/loaders) | Loading animations and micro-transitions |
| [Amicro buttons](https://amicro.vercel.app/buttons) | Button micro-transitions |
| [DialKit](https://www.dialkit.dev/) | Live sliders to tune animation, colour and layout by feel |

## Components for product UI
| Site | Use it for |
|---|---|
| [21st.dev](https://21st.dev/) | 12,000+ components, each with a prompt for Claude |
| [Spectrum UI](https://ui.spectrumhq.in/docs) | Cards, buttons, inputs and AI chat |
| [Libraries.dev skill](https://libraries.dev/skill#installation) | AI-app effects: glowing borders, thinking orbs |
| [Spell UI](https://spell.sh/docs/components) | Small, polished copy-paste components |
| [Open Source UI](https://opensourceui.in/components) | 200+ free components |
| [Iconly](https://iconly.design/) | 2,400+ app and web icons |

For library picks (toasts, drawers, command menus, tables, charts) use `pick-ui-library`.

## Rules
- A product screen is judged on real data. Test it with `break-ui`.
- Every screen needs its empty, loading and error state. Copy those from the reference too.
- Product UI moves less than a landing page. Use `motion/remove-animations` thinking: no motion on keyboard actions or high-frequency surfaces.
- Dense is fine when it is aligned. Calm comes from alignment and type, not from empty space.
