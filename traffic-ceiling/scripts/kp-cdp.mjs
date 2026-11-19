const [cmd, targetId, ...rest] = process.argv.slice(2);
const CDP = "http://127.0.0.1:9222";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

if (!cmd || cmd === "help") {
  console.log(`usage:
  node kp-cdp.mjs tabs                                  list Google Ads tabs
  node kp-cdp.mjs location <tab> "<Country>"            replace the plan location (no reload)
  node kp-cdp.mjs run <tab> "<seed>" ...                reload, enter up to 10 seeds, get results, download CSV
  node kp-cdp.mjs download <tab>                        download the current results as CSV
Start Brave with: open -a "Brave Browser" --args --remote-debugging-port=9222`);
  process.exit(0);
}

const list = await (await fetch(`${CDP}/json/list`)).json();
if (cmd === "tabs") {
  for (const t of list.filter((x) => x.type === "page" && /ads\.google\.com/.test(x.url))) console.log(t.id, t.title);
  process.exit(0);
}
const t = list.find((x) => x.id === targetId);
if (!t) throw new Error("tab not found; run: node kp-cdp.mjs tabs");
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m), pending.delete(m.id);
};
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async (expression) => { const r = await send("Runtime.evaluate", { expression, returnByValue: true }); return r.result?.result?.value ?? r.result?.exceptionDetails?.text ?? JSON.stringify(r.error); };
const key = async (k, code, vk) => { await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: k, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk }); await send("Input.dispatchKeyEvent", { type: "char", key: k, code, text: "\r", unmodifiedText: "\r", windowsVirtualKeyCode: vk }); await send("Input.dispatchKeyEvent", { type: "keyUp", key: k, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk }); };
await send("Page.bringToFront");
const vis = `el => !!(el.offsetWidth || el.offsetHeight)`;
const dialog = `[...document.querySelectorAll('[aria-label="Advanced location picker"]')].find(${vis})`;
const targeting = () => evaluate(`[...document.querySelectorAll('[aria-label="Targeting Settings"] button, [aria-label="Targeting Settings"] [role=button]')].map(b => b.innerText.trim().replace(/\\s+/g,' ')).join(' | ')`);

async function download() {
  console.log("count:", await evaluate(`(document.body.innerText.match(/[\\d,]+ keyword ideas available/)||['?'])[0]`));
  console.log("open menu:", await evaluate(`(() => { const b = [...document.querySelectorAll('material-menu.download material-button')].find(${vis}); if (!b) return 'no trigger'; b.click(); return 'clicked'; })()`));
  await sleep(1500);
  console.log("csv:", await evaluate(`(() => { const m = [...document.querySelectorAll('[role=menuitem]')].filter(${vis}).find(m => m.innerText.trim() === '.csv'); if (!m) return 'no csv item'; m.click(); return 'clicked'; })()`));
  await sleep(30000);
  console.log("look in ~/Downloads for 'Keyword Stats <date>.csv'");
}

if (cmd === "location") {
  const country = rest[0];
  if ((await evaluate(`!!(${dialog})`)) !== true) {
    await evaluate(`[...document.querySelectorAll('[aria-label="Targeting Settings"] button, [aria-label="Targeting Settings"] [role=button]')][0].click()`);
    await sleep(2000);
  }
  console.log("cleared:", await evaluate(`(() => { const d = ${dialog}; if (!d) return 'no dialog'; let n = 0; for (let k = 0; k < 10; k++) { const rows = [...d.querySelectorAll('*')].filter(${vis}).filter(e => /\\b(country|region|city|state)\\b/.test(e.innerText||'') && e.innerText.trim().length < 60 && e.children.length); if (!rows.length) break; let el = rows[rows.length-1], done = false; for (let i = 0; i < 6 && el && !done; i++) { const icon = [...el.parentElement.querySelectorAll('material-icon')].find(m => /cancel/.test(m.innerText) && (${vis})(m)); if (icon) { icon.click(); n++; done = true; } el = el.parentElement; } if (!done) break; } return n; })()`));
  await sleep(800);
  if (country) {
    await evaluate(`(() => { const d = ${dialog}; const i = d && [...d.querySelectorAll('input')].find(${vis}); i.focus(); i.click(); })()`);
    await send("Input.insertText", { text: country });
    await sleep(3000);
    console.log("include:", await evaluate(`(() => { const entry = [...document.querySelectorAll('location-data-suggestion-entry')].filter(${vis}).find(e => (e.innerText||'').trim().startsWith(${JSON.stringify(country + "\n")})); if (!entry) return 'no entry'; const b = [...entry.querySelectorAll('material-button, button, [role=button]')].find(b => /include/i.test(b.innerText)); (b || entry).click(); return entry.innerText.split('\\n')[0]; })()`));
    await sleep(1500);
  }
  console.log("save:", await evaluate(`(() => { const d = ${dialog}; if (!d) return 'dialog already closed'; const b = [...d.querySelectorAll('material-button, button')].filter(${vis}).find(b => /^save$/i.test(b.innerText.trim())); if (!b || b.getAttribute('aria-disabled') === 'true') return 'save disabled'; b.click(); return 'saved'; })()`));
  await sleep(9000);
  console.log("targeting:", await targeting());
}

if (cmd === "run") {
  await send("Page.navigate", { url: t.url.replace(/\/aw\/keywordplanner\/[^?]*/, "/aw/keywordplanner/home") });
  await sleep(10000);
  console.log("discover:", await evaluate(`(() => { const e = [...document.querySelectorAll('*')].find(e => e.children.length < 3 && e.innerText?.trim() === 'Discover new keywords'); if (!e) return 'no card'; e.click(); return 'clicked'; })()`));
  await sleep(4000);
  for (const s of rest.slice(0, 10)) {
    await evaluate(`[...document.querySelectorAll('input[aria-label="Search input"]')].find(${vis}).focus()`);
    await send("Input.insertText", { text: s });
    await sleep(300);
    await key("Enter", "Enter", 13);
    await sleep(600);
  }
  console.log("chips:", await evaluate(`[...document.querySelectorAll('material-chip, .chip')].filter(${vis}).map(c => c.innerText.trim().replace(/\\s+/g,' ')).join(' | ')`));
  console.log("get results:", await evaluate(`(() => { const b = [...document.querySelectorAll('material-button, button')].filter(${vis}).find(b => /^get results$/i.test(b.innerText.trim())); if (!b) return 'no button'; b.click(); return 'clicked'; })()`));
  await sleep(15000);
  await download();
}

if (cmd === "download") await download();
ws.close();
