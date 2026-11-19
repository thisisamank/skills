import { writeFileSync } from "node:fs";

const sa = JSON.parse(process.env.GSC_SERVICE_ACCOUNT);
const b64url = (bytes) => Buffer.from(bytes).toString("base64url");
const b64json = (v) => b64url(new TextEncoder().encode(JSON.stringify(v)));
const isoDay = (ms) => new Date(ms).toISOString().slice(0, 10);

async function jwt() {
  const der = Buffer.from(sa.private_key.replace(/-----[^-]+-----|\s|\\n/g, ""), "base64");
  const key = await crypto.subtle.importKey("pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const iat = Math.floor(Date.now() / 1000);
  const unsigned = `${b64json({ alg: "RS256", typ: "JWT" })}.${b64json({ iss: sa.client_email, scope: "https://www.googleapis.com/auth/webmasters.readonly", aud: "https://oauth2.googleapis.com/token", iat, exp: iat + 3600 })}`;
  const sig = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(unsigned)));
  return `${unsigned}.${b64url(sig)}`;
}

const tok = await fetch("https://oauth2.googleapis.com/token", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion: await jwt() }),
});
if (!tok.ok) throw new Error(`token ${tok.status} ${(await tok.text()).slice(0, 200)}`);
const { access_token } = await tok.json();

async function query(site, days, dimensions) {
  const now = Date.now();
  const res = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(site)}/searchAnalytics/query`, {
    method: "POST",
    headers: { authorization: `Bearer ${access_token}`, "content-type": "application/json" },
    body: JSON.stringify({ startDate: isoDay(now - (days - 1) * 864e5), endDate: isoDay(now), dimensions, dataState: "all", rowLimit: 5000 }),
  });
  if (!res.ok) throw new Error(`${site} ${res.status} ${(await res.text()).slice(0, 300)}`);
  const data = await res.json();
  return (data.rows ?? []).map((r) => ({ keys: r.keys, clicks: r.clicks, impressions: r.impressions, ctr: r.ctr, position: r.position }));
}

const out = {};
const sites = process.argv.slice(3);
if (!sites.length) throw new Error("usage: noenv exec -- node gsc-pull.mjs <out.json> sc-domain:example.com ...");
for (const site of sites) {
  out[site] = {
    q28: await query(site, 28, ["query"]),
    q90: await query(site, 90, ["query"]),
    qp28: await query(site, 28, ["query", "page"]),
    p28: await query(site, 28, ["page"]),
  };
  for (const [k, v] of Object.entries(out[site])) console.log(site, k, v.length, "rows");
}
writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
