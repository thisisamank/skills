const sa = JSON.parse(process.env.GSC_SERVICE_ACCOUNT);
const b64url = (bytes) => Buffer.from(bytes).toString("base64url");
const b64json = (v) => b64url(new TextEncoder().encode(JSON.stringify(v)));

async function token() {
  const der = Buffer.from(sa.private_key.replace(/-----[^-]+-----|\s|\\n/g, ""), "base64");
  const key = await crypto.subtle.importKey("pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const iat = Math.floor(Date.now() / 1000);
  const unsigned = `${b64json({ alg: "RS256", typ: "JWT" })}.${b64json({ iss: sa.client_email, scope: "https://www.googleapis.com/auth/webmasters", aud: "https://oauth2.googleapis.com/token", iat, exp: iat + 3600 })}`;
  const sig = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(unsigned)));
  const res = await fetch("https://oauth2.googleapis.com/token", { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion: `${unsigned}.${b64url(sig)}` }) });
  if (!res.ok) throw new Error(`token ${res.status} ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).access_token;
}
const t = await token();
const H = { authorization: `Bearer ${t}`, "content-type": "application/json" };

const sites = { "sc-domain:sharehue.com": "https://sharehue.com", "sc-domain:signkaro.org": "https://signkaro.org" };
for (const [site, origin] of Object.entries(sites)) {
  console.log(`\n===== ${site}`);
  const sm = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(site)}/sitemaps`, { headers: H });
  console.log("sitemaps:", sm.status, JSON.stringify((await sm.json()).sitemap?.map((s) => ({ path: s.path, lastSubmitted: s.lastSubmitted, lastDownloaded: s.lastDownloaded, errors: s.errors, warnings: s.warnings, pending: s.isPending, contents: s.contents })) ?? null));
  const xml = await (await fetch(`${origin}/sitemap.xml`)).text();
  const urls = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map((m) => m[1]);
  const blog = urls.filter((u) => u.includes("/blog/")).slice(0, 6);
  const sample = [origin + "/", ...blog, ...urls.filter((u) => /\/(for|templates)\//.test(u)).slice(0, 2)];
  for (const u of sample) {
    const res = await fetch("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", { method: "POST", headers: H, body: JSON.stringify({ inspectionUrl: u, siteUrl: site }) });
    const data = await res.json();
    if (!res.ok) { console.log(u, "->", res.status, JSON.stringify(data).slice(0, 300)); continue; }
    const r = data.inspectionResult?.indexStatusResult ?? {};
    console.log(u.replace(origin, ""), "|", r.verdict, "|", r.coverageState, "| crawl:", r.lastCrawlTime ?? "never", "| fetch:", r.pageFetchState, "| robots:", r.robotsTxtState, "| canon:", r.googleCanonical === r.userCanonical ? "same" : `${r.userCanonical} -> ${r.googleCanonical}`, "| sitemaps:", (r.sitemap ?? []).length, "| refs:", (r.referringUrls ?? []).length);
  }
}
