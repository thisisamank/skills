#!/usr/bin/env python3
"""Tools for a mascot preview page made from assets/preview-template.html.

  inline  PAGE OUT.html     Put three.js inside the page. The result is one file with no network requests.
  module  PAGE OUT.js       Copy the portable mascot block to an ES module for React or plain Three.js.
  qa      PAGE OUT.png      Headless browser: save the contact sheet and print the self-test report.
  shot    PAGE OUT.png      Headless browser: screenshot of any page. --mobile for a phone size, --full for the whole page.
  rig     PAGE OUT.json     Headless browser: save the rig data that rebuild_in_blender.py reads.
  glb     PAGE OUT.glb      Headless browser: save a GLB with all clips. Needs the page from before "inline".
  cleanup                   Kill every headless browser this script started and delete its profile folder.

Every headless command first kills browsers left behind by earlier runs that were killed or timed out,
and kills its own browser (the whole process group) when it ends, fails or gets a signal.

The headless commands need a Chrome-family browser (Chrome, Chromium, Brave, Edge).
Only the Python standard library is used.
"""
import argparse, atexit, base64, glob, json, os, pathlib, re, shutil, signal, socket, struct, subprocess, sys, tempfile, time, urllib.parse, urllib.request

THREE_VERSION = "0.170.0"   # the last release with a one-file module build; "inline" depends on that
THREE_URL = "https://cdn.jsdelivr.net/npm/three@%s/build/three.module.min.js" % THREE_VERSION
BLOCK = re.compile(r"<!-- THREE:BEGIN.*?THREE:END -->", re.S)
MASCOT = re.compile(r"// MASCOT:BEGIN\n(.*?)// MASCOT:END", re.S)


def die(msg):
    sys.exit("mascot_tools: " + msg)


def three_source(path=None):
    if path:
        return pathlib.Path(path).read_text(encoding="utf-8")
    cache = pathlib.Path(tempfile.gettempdir()) / ("three-%s.module.min.js" % THREE_VERSION)
    if not cache.exists():
        try:
            with urllib.request.urlopen(THREE_URL, timeout=60) as r:
                cache.write_bytes(r.read())
        except Exception as e:
            die("cannot download three.js (%s). Download %s and pass it with --three." % (e, THREE_URL))
    return cache.read_text(encoding="utf-8")


def cmd_inline(a):
    page = pathlib.Path(a.page).read_text(encoding="utf-8")
    if not BLOCK.search(page):
        die("no THREE:BEGIN ... THREE:END block in the page. Is it already inlined?")
    src = three_source(a.three)
    m = re.search(r"export\s*\{([^}]*)\}\s*;?\s*$", src)
    if not m or re.search(r"^\s*import\b", src, re.M):
        die("this three.js build is not a one-file module build. Use version " + THREE_VERSION + ".")
    pairs = []
    for item in m.group(1).split(","):
        item = item.strip()
        if item:
            local, _, public = item.partition(" as ")
            pairs.append("%s:%s" % ((public or local).strip(), local.strip()))
    body = src[: m.start()] + "window.THREE={" + ",".join(pairs) + "};"
    body = body.replace("</script", "<\\/script").replace("<!--", "<\\!--")
    out = BLOCK.sub(lambda _: '<script type="module">\n' + body + "\n</script>", page, count=1)
    pathlib.Path(a.out).write_text(out, encoding="utf-8")
    print("wrote %s (%d KB, three.js %s inside)" % (a.out, len(out.encode()) // 1024, THREE_VERSION))


def cmd_module(a):
    page = pathlib.Path(a.page).read_text(encoding="utf-8")
    m = MASCOT.search(page)
    if not m:
        die("no MASCOT:BEGIN ... MASCOT:END block in the page.")
    out = (
        "// Made by mascot_tools.py from %s. Edit the page, then run the tool again.\n" % os.path.basename(a.page)
        + "import * as THREE from 'three';\n\n"
        + m.group(1)
        + "\nexport { createMascot, MASCOT_DEFAULTS, PERSONALITIES };\n"
        + "export default function mascot(options) { return createMascot(THREE, options); }\n"
    )
    pathlib.Path(a.out).write_text(out, encoding="utf-8")
    print("wrote " + a.out)


def find_browser():
    env = os.environ.get("MASCOT_BROWSER")
    names = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "brave-browser", "microsoft-edge", "chrome"]
    paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in ([env] if env else []) + names + paths:
        found = shutil.which(c) or (c if os.path.exists(c) else None)
        if found:
            return found
    die("no Chrome-family browser found. Set MASCOT_BROWSER to its path, or do this check by hand.")


PROFILE_PREFIX = "mascot-browser-"


def _profile_of(pid):
    """The mascot profile folder a process uses, or None. Linux only (reads /proc)."""
    try:
        # Chrome rewrites its process title, so the arguments may be joined by spaces instead of NUL bytes.
        line = open("/proc/%d/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return None
    m = re.search(r"--user-data-dir=(\S*" + re.escape(PROFILE_PREFIX) + r"\S*)", line)
    return m.group(1) if m else None


def _owner_alive(profile):
    """A profile is in use while the Python process that made it is alive. It writes its pid to owner.pid."""
    try:
        pid = int(open(os.path.join(profile, "owner.pid")).read())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def _procs():
    """{pid: (ppid, pgid)} for every process. Linux only."""
    out = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                f = open("/proc/%s/stat" % d).read().rsplit(")", 1)[1].split()
                out[int(d)] = (int(f[1]), int(f[2]))
            except (OSError, IndexError, ValueError):
                pass
    return out


def _kill_tree(roots, procs):
    """SIGKILL the roots, their process groups and all their descendants. Renderer and GPU children do not
    carry --user-data-dir, so matching on the profile alone misses them. Returns the number killed."""
    groups = {procs[r][1] for r in roots if r in procs and procs[r][1] > 1 and procs[r][1] != os.getpgrp()}
    doomed, grew = set(roots) | {p for p, (_, g) in procs.items() if g in groups}, True
    while grew:
        more = {p for p, (pp, _) in procs.items() if pp in doomed and p not in doomed}
        doomed |= more
        grew = bool(more)
    doomed.discard(os.getpid())
    n = 0
    for pid in doomed:
        try:
            os.kill(pid, signal.SIGKILL)
            n += 1
        except OSError:
            pass
    return n


def reap(everything=False):
    """Kill mascot browsers whose owner is gone (or all of them) and delete their profiles. Returns the count."""
    killed, profiles = 0, set()
    if os.path.isdir("/proc"):
        roots = []
        for pid in _procs():
            prof = _profile_of(pid) if pid != os.getpid() else None
            if prof and (everything or not _owner_alive(prof)):
                profiles.add(prof)
                roots.append(pid)
        if roots:
            killed = _kill_tree(roots, _procs())
    for root in {tempfile.gettempdir(), "/tmp", "/var/tmp"}:
        for prof in glob.glob(os.path.join(root, PROFILE_PREFIX + "*")):
            fresh = time.time() - os.path.getmtime(prof) < 60   # another run may be writing owner.pid right now
            if everything or (not fresh and not _owner_alive(prof)):
                profiles.add(prof)
    for prof in profiles:
        shutil.rmtree(prof, ignore_errors=True)
    if everything and not os.path.isdir("/proc"):   # macOS and others: no /proc, match the command line instead
        if subprocess.run(["pkill", "-9", "-f", "user-data-dir=.*" + PROFILE_PREFIX], capture_output=True).returncode == 0:
            killed += 1
    return killed


def _raise_exit(signum, frame):
    sys.exit(128 + signum)   # turns SIGTERM / SIGHUP into SystemExit, so "with" blocks and atexit still close the browser


for _sig in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
    if _sig is not None:
        signal.signal(_sig, _raise_exit)


class Browser:
    """A headless browser driven over the DevTools protocol. The one-shot flags (--screenshot,
    --dump-dom) do not work in every Chrome-family browser, so this talks to it directly."""

    def __init__(self, width, height, scale=1, mobile=False):
        reap()   # browsers left by earlier runs that were killed before they could clean up
        self.proc = None
        self.profile = tempfile.mkdtemp(prefix=PROFILE_PREFIX)
        pathlib.Path(self.profile, "owner.pid").write_text(str(os.getpid()))
        atexit.register(self.close)
        cmd = [find_browser(), "--headless=new", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
               "--disable-crash-reporter", "--disable-breakpad",
               "--user-data-dir=" + self.profile, "--remote-debugging-port=0",
               "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
               "--window-size=%d,%d" % (width, height + 200), "about:blank"]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        # Own process group, so close() can kill the GPU, renderer and crashpad children too, not only the main process.
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        port_file = os.path.join(self.profile, "DevToolsActivePort")
        deadline = time.time() + 30
        while not os.path.exists(port_file) or not open(port_file).read().strip():
            if time.time() > deadline or self.proc.poll() is not None:
                self.close()
                die("the browser did not start in headless mode.")
            time.sleep(0.1)
        port = int(open(port_file).read().split()[0])
        target = None
        while not target and time.time() < deadline:
            with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=10) as r:
                target = next((t for t in json.load(r) if t.get("type") == "page"), None)
            time.sleep(0.1)
        if not target:
            self.close()
            die("the browser has no page to drive.")
        u = urllib.parse.urlparse(target["webSocketDebuggerUrl"])
        self.sock = socket.create_connection((u.hostname, u.port), timeout=180)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                           "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (u.path, u.hostname, u.port, key)).encode())
        self.buf = b""
        while b"\r\n\r\n" not in self.buf:
            self.buf += self.sock.recv(4096)
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            self.close()
            die("the browser refused the DevTools connection.")
        self.n = 0
        self.call("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=scale, mobile=mobile)

    def _recv(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise RuntimeError("the browser closed the connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _send(self, text, opcode=1):
        data, mask = text.encode(), os.urandom(4)
        n = len(data)
        head = bytes([0x80 | opcode]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n))
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self):
        message = b""
        while True:
            b0, b1 = self._recv(2)
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recv(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recv(8))[0]
            data = self._recv(n)
            op = b0 & 0x0F
            if op == 8:
                raise RuntimeError("the browser closed the connection")
            if op == 9:
                self._send(data.decode("utf-8", "replace"), opcode=10)
            elif op in (0, 1, 2):
                message += data
                if b0 & 0x80:
                    return message.decode("utf-8")

    def call(self, method, **params):
        self.n += 1
        self._send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self._read())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"].get("message")))
                return msg.get("result", {})

    def js(self, expression):
        r = self.call("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"].get("exception", {}).get("description") or r["exceptionDetails"].get("text"))
        return r["result"].get("value")

    def open(self, page, query=""):
        self.call("Page.navigate", url=pathlib.Path(page).resolve().as_uri() + (("?" + query) if query else ""))

    def wait_for_qa(self, seconds=150):
        deadline = time.time() + seconds
        while time.time() < deadline:
            title = self.js("document.title")
            if title == "QA done":
                return
            if title == "QA failed":
                die("the page failed: " + str(self.js("document.getElementById('qa-error').textContent")))
            time.sleep(0.3)
        die("the page did not finish in %d s. Does it load three.js? A page that uses the CDN needs a network." % seconds)

    def screenshot(self, out, full=False):
        size = self.call("Page.getLayoutMetrics")["cssContentSize" if full else "cssLayoutViewport"]
        clip = {"x": 0, "y": 0, "width": size.get("width") or size["clientWidth"], "height": size.get("height") or size["clientHeight"], "scale": 1}
        data = self.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=full)["data"]
        pathlib.Path(out).write_bytes(base64.b64decode(data))

    def close(self):
        """Kill the browser and every process it started, then delete the profile. Safe to call twice."""
        if self.proc is not None and self.proc.poll() is None:
            for sig, wait in ((signal.SIGTERM, 5), (signal.SIGKILL, 5)):
                try:
                    os.killpg(self.proc.pid, sig)
                    self.proc.wait(timeout=wait)
                    break
                except (OSError, subprocess.TimeoutExpired):
                    pass
        if self.proc is not None:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)   # children that outlived the main process
            except OSError:
                pass
        if os.path.isdir("/proc"):   # anything that left the group but still uses this profile, and its children
            procs = _procs()
            _kill_tree([p for p in procs if p != os.getpid() and _profile_of(p) == self.profile], procs)
        shutil.rmtree(self.profile, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def qa_data(page, mode):
    with Browser(1200, 900) as b:
        b.open(page, "qa=" + mode)
        b.wait_for_qa()
        return b.js("document.getElementById('qa-data').textContent")


def cmd_qa(a):
    with Browser(1200, 900) as b:
        b.open(a.page, "qa")
        b.wait_for_qa()
        report = json.loads(b.js("document.getElementById('qa-report').textContent"))
        sheet = b.js("document.querySelector('#qa canvas').toDataURL('image/png')")
    pathlib.Path(a.out).write_bytes(base64.b64decode(sheet.split(",", 1)[1]))
    print("contact sheet: " + a.out)
    for name, c in report["clips"].items():
        print("  %-10s %.2f s  %s  deepest overlap %.3f" % (name, c["duration"], "loop    " if c["loop"] else "one-shot", c["deepestOverlap"]))
    if report["ok"]:
        print("self-test: OK")
    else:
        print("self-test: %d issue(s)" % len(report["issues"]))
        for i in report["issues"]:
            print("  - " + i)
        sys.exit(1)


def cmd_shot(a):
    size = (390, 844, 2, True) if a.mobile else (1280, 800, 1, False)
    with Browser(*size) as b:
        b.open(a.page, a.query or "")
        time.sleep(a.wait / 1000)
        if a.play:
            b.js("window.mascot.play(%s)" % json.dumps(a.play))
            time.sleep(a.at)
        errors = b.js("document.getElementById('fail') ? document.getElementById('fail').textContent : ''")
        b.screenshot(a.out, full=a.full)
    print("screenshot: %s (%s%dx%d)" % (a.out, "full page, viewport " if a.full else "", size[0], size[1]))
    if errors:
        die(errors)


def cmd_rig(a):
    data = qa_data(a.page, "rig")
    rig = json.loads(data)
    pathlib.Path(a.out).write_text(data, encoding="utf-8")
    print("wrote %s: %d bones, %d meshes, %d clips" % (a.out, len(rig["bones"]), len(rig["meshes"]), len(rig["clips"])))


def cmd_glb(a):
    data = base64.b64decode(qa_data(a.page, "glb"))
    if data[:4] != b"glTF":
        die("the page did not return a GLB file.")
    pathlib.Path(a.out).write_bytes(data)
    print("wrote %s (%d KB)" % (a.out, len(data) // 1024))


def cmd_cleanup(a):
    n = reap(everything=True)
    print("cleanup: killed %d headless browser process(es), deleted the %s* profiles" % (n, PROFILE_PREFIX))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cleanup").set_defaults(fn=cmd_cleanup)
    for name, fn in [("inline", cmd_inline), ("module", cmd_module), ("qa", cmd_qa), ("shot", cmd_shot), ("rig", cmd_rig), ("glb", cmd_glb)]:
        p = sub.add_parser(name)
        p.add_argument("page")
        p.add_argument("out")
        p.set_defaults(fn=fn)
        if name == "inline":
            p.add_argument("--three", help="path to three.module.min.js, version " + THREE_VERSION)
        if name == "shot":
            p.add_argument("--mobile", action="store_true")
            p.add_argument("--full", action="store_true", help="the whole page, not only the first screen; use it for SVG sheets")
            p.add_argument("--query", help="text after ? in the address, for example handoff")
            p.add_argument("--wait", type=int, default=2500, help="milliseconds to wait before the screenshot")
            p.add_argument("--play", help="clip to start before the screenshot, for example wave")
            p.add_argument("--at", type=float, default=0.6, help="seconds into the clip to take the screenshot")
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
