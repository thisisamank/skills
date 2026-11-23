---
name: traffic-ceiling
description: Measure how much organic traffic a product can get at the extreme, and what that is worth. Pulls Search Console for the floor, drives Google Keyword Planner through the user's own Brave or Chrome for the market size, filters out competitor and other-brand queries, and turns the sum into a ceiling and a revenue forecast. Use when the user asks how big the market is, what traffic the site can reach, whether SEO is worth it, or what to expect from a product organically.
disable-model-invocation: true
---

# Traffic ceiling

The ceiling is the sum of monthly searches for every query the product can rank for, times the click share at a position. Search Console gives the floor (what the site gets today). Keyword Planner gives the universe. The report ends with a forecast table and the levers that move it.

Do the steps in order. Every number is an order of magnitude, say so in the report.

## 1. Floor: Search Console

The service account JSON lives in noenv as `GSC_SERVICE_ACCOUNT`. Find the project that holds it with `noenv secret list` in each product repo. The same account is a Restricted user on all properties.

```
cd <repo-with-the-secret> && noenv exec -- node scripts/gsc-pull.mjs <out.json>
```

Edit the site list at the bottom of `scripts/gsc-pull.mjs` first. It writes 28 and 90 day query rows, query by page, and page rows. Print them sorted by impressions. A young site shows tens of rows; that is normal.

`scripts/gsc-inspect.mjs` runs the URL Inspection API over the sitemap's newest URLs and lists the submitted sitemaps with their last download time. Use it when the user says pages are not getting indexed. "URL is unknown to Google" on pages newer than the sitemap's last download is crawl latency, not a bug.

Do not use Ahrefs for this unless the account has a paid plan. The connected account returns "Insufficient plan" for Keywords Explorer, Site Explorer and the GSC tools.

## 2. Universe: Keyword Planner through the user's browser

Keyword Planner needs a Google Ads login. There is no API without a developer token, so drive the user's own browser over the DevTools protocol.

1. Ask the user to quit Brave and start it with `open -a "Brave Browser" --args --remote-debugging-port=9222`, sign in to ads.google.com, and open Tools, Planning, Keyword Planner, Discover new keywords.
2. List tabs: `node scripts/kp-cdp.mjs tabs`. Copy the Keyword Planner tab id.
3. Set the location: `node scripts/kp-cdp.mjs location <tab> "United States"`. Run it once per country you want. Worldwide is the state after you remove every location.
4. Run the seeds and download: `node scripts/kp-cdp.mjs run <tab> "seed one" "seed two" ...` with 10 seeds at most. The CSV lands in `~/Downloads/Keyword Stats <date>.csv`. Copy it into the product repo as `docs/seo/keyword-planner/<product>-<geo>.csv`.
5. Repeat for each product and country. A typical set is United States, India, and worldwide.

Things that cost time the first run:

- Enter seeds one per Enter. A comma list keeps only the first and last seed.
- Key events reach the page only when the tab is in front, and Enter must be a rawKeyDown, char, keyUp sequence. `kp-cdp.mjs` does both. Reloading `ideas/new` lands on Keyword Planner home, so `run` starts from home and clicks Discover new keywords.
- Downloads can arrive after the 30 second wait. Move each CSV only if it is newer than the previous step, then check the first keyword and the row count against the logged "keyword ideas available" count.
- A page reload resets the plan's location to the account default. Set the location, then run, without reloading between them. The `run` command reloads first, so set the location after it and use `download` instead of a second `run` when only the location changed.
- Pick a location from the suggestion list by its Include button. Arrow down and Enter selects the wrong row.
- Playwright based scenario tools cancel browser downloads. Plain DevTools clicks let Brave save the file.
- Volumes are range midpoints in an account with no ad spend: 50, 500, 5,000, 50,000, 500,000. Exact numbers need one campaign that has run.
- The CSV is UTF-16 with tabs. Read it with `iconv -f UTF-16 -t UTF-8`.

Seeds that worked: for a brand tool, `brand guidelines`, `brand guidelines template`, `brand guideline software`, `brand book`, `brand style guide`, `brand asset library`, `logo usage guidelines`, `brand colors`, `hex to rgb`, `extract logo from pdf`. For an e-signature tool, `electronic signature`, `sign pdf online`, `esign`, `nda template`, `rental agreement`, `offer letter format`, `partnership deed`, `lease renewal letter`, `consent form`, `docusign pricing`.

## 3. Filter and sum

Run `python3 scripts/ceiling.py <filters.json> <csv>...`. Copy `references/filters-example.json` and edit the three regexes and the cluster map for the product.

The script removes three buckets and reports them separately:

- competitor-branded queries (DocuSign, Frontify): winnable only through comparison pages;
- other companies' brands (Nike brand guidelines, Google sign in): never winnable;
- off-topic tasks the product does not do (logo makers, PDF editors).

It then groups the rest into clusters, sums the volume per cluster, and applies the click shares: 27% at position 1, 11% at position 3, 2.5% averaged over positions 6 to 10. Position 1 is the hard upper bound. Positions 6 to 10 is what a small new site reaches in year one if it ranks for most of the cluster. Keyword Planner lists close variants as separate rows, so sums overcount.

The output also gives the search-weighted top of page bid per cluster and searches times bid ("ad value"), in the account currency. A high bid means a click turns into money for someone. Use it to compare willingness to pay across clusters or across ideas.

Split clusters when one seed drags in a different market. Colour converters pulled in a colour-code universe fifteen times the size of the brand guideline market, with a different visitor.

## 4. Forecast and levers

Turn the ceiling into money with the product's own plans and these defaults: 3% of product-page visitors sign up, 0.5% of tool-page visitors sign up, 3% of free accounts pay. Average revenue per paying account comes from the pricing page with the higher plan in the mix. Give four rows: months 1 to 3, month 6, month 12, and the ceiling. State that churn is not included.

Then name the levers in order of effect. The ones that held for two products:

1. Sell to the customer who brings others (an agency, a landlord with tenants).
2. Let the product market itself: a badge or link on free-plan output.
3. Own the two or three largest product-intent queries with dedicated pages.
4. Treat high-volume tool queries as reach and links, not sign-ups.
5. Push the AI assistant channel; early sign-ups came from ChatGPT more than Google.
6. Size the blog to the market. Two posts a day on a 160,000-search market is too many.

Compare products if the user has more than one. A 25 times larger market changes where the effort should go.

## Idea validation (no product yet)

The same steps size an idea before it exists. Skip step 1. Find complaints first (Firecrawl search on Reddit), run one Keyword Planner seed set per candidate idea, write one filters file per idea, and compare the product-intent clusters by volume and bid. Then check who already sells the product before you call it a gap. Example: `idea-research/2026-11-14-passive-income/` in experiments-sass.

## 5. Report

The deliverable is one HTML file the person opens in a browser: `docs/seo/traffic-ceiling.html` in the product repo.

1. Write the content as JSON. Copy `references/report-example.json` and replace the numbers, bullets and levers. The order of sections is: method, one section per product, the forecast table, the levers, the comparison, the files.
2. Render it: `python3 scripts/report.py report.json docs/seo/traffic-ceiling.html`. The page is self-contained, has no external assets, and follows the system light or dark mode.
3. Keep the JSON next to it as `docs/seo/traffic-ceiling.json` so the next refresh edits numbers, not prose. Keep the CSVs in `docs/seo/keyword-planner/`.
4. Open it with `open docs/seo/traffic-ceiling.html` and tell the user the path.

Say the date, the account state (ranges or exact), the click shares, and the caveats inside the report. Do not publish it as an Artifact. Do not commit unless asked.
