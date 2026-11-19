"""Sum Keyword Planner exports into a traffic ceiling.

usage: python3 ceiling.py filters.json product-us.csv [product-in.csv ...]

filters.json:
{
  "competitors": "\\b(docusign|adobe)\\b",
  "other_brands": "\\b(nike|google)\\b",
  "off_topic": "\\b(sign ?in|login)\\b",
  "clusters": { "e-signature": "\\b(sign|signature|esign)\\b", "contract templates": "\\b(agreement|contract|template)\\b" }
}
Rows are tested in that order. Rows that match no cluster go to "other".
"avg top bid" is the search-weighted top of page bid (high range); "ad value" is searches x that bid,
what advertisers would pay for the same clicks each month. Use it to compare willingness to pay across ideas.
"""
import csv, io, json, re, sys
from collections import defaultdict

CTR = {"position 1": 0.27, "position 3": 0.11, "positions 6 to 10": 0.025}


def load(path):
    text = open(path, "rb").read().decode("utf-16")
    rows = csv.DictReader(io.StringIO("\n".join(text.splitlines()[2:])), delimiter="\t")
    out, bids, cur = {}, {}, ""
    for r in rows:
        k = (r.get("Keyword") or "").strip().lower()
        v = (r.get("Avg. monthly searches") or "").replace(",", "").strip()
        if k and v.isdigit():
            out[k] = max(out.get(k, 0), int(v))
            b = (r.get("Top of page bid (high range)") or "").replace(",", "").strip()
            bids[k] = float(b) if b.replace(".", "", 1).isdigit() else 0.0
            cur = cur or r.get("Currency") or ""
    return out, bids, cur


def main(filters_path, paths):
    f = json.load(open(filters_path))
    rx = {k: re.compile(f[k]) for k in ("competitors", "other_brands", "off_topic")}
    clusters = {name: re.compile(p) for name, p in f["clusters"].items()}
    for path in paths:
        data, bids, cur = load(path)
        val = defaultdict(float)
        vol = defaultdict(int)
        n = defaultdict(int)
        top = defaultdict(list)
        for kw, v in data.items():
            bucket = next((name for name, r in rx.items() if r.search(kw)), None)
            if bucket is None:
                bucket = next((name for name, r in clusters.items() if r.search(kw)), "other")
            vol[bucket] += v
            val[bucket] += v * bids.get(kw, 0)
            n[bucket] += 1
            top[bucket].append((v, kw))
        print(f"\n## {path} ({len(data)} rows)")
        print(f"| cluster | keywords | searches/mo | avg top bid ({cur}) | ad value/mo ({cur}) | " + " | ".join(CTR) + " |")
        print("|---|---|---|---|---|" + "---|" * len(CTR))
        for name in sorted(vol, key=lambda k: -vol[k]):
            excluded = name in rx
            shares = ["excluded"] * len(CTR) if excluded else [f"{int(vol[name] * c):,}" for c in CTR.values()]
            avg = val[name] / vol[name] if vol[name] else 0
            print(f"| {name} | {n[name]} | {vol[name]:,} | {avg:,.2f} | {int(val[name]):,} | " + " | ".join(shares) + " |")
        for name in sorted(vol, key=lambda k: -vol[k]):
            print(f"- {name}: " + ", ".join(f"{kw} ({v:,})" for v, kw in sorted(top[name], reverse=True)[:12]))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2:])
