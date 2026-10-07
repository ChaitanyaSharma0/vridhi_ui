"""Vriddhi AI local server (standard library only). Serves the API and the v-fr frontend from one origin.
Run:  python work/api/server.py            then open http://127.0.0.1:8770/
Mock mode (UI work without models):  set VRIDDHI_MOCK=1  -> serves saved JSON from api/mock/ instead of live calls."""
import json
import os
import sys
import time
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRONT = HERE.parents[1] / "v-fr"
PORT = int(os.environ.get("VRIDDHI_PORT", 8770))
MOCK = os.environ.get("VRIDDHI_MOCK") == "1"
MOCK_DIR = HERE / "mock"

if not MOCK:
    sys.path.insert(0, str(HERE))
    from engine import Engine  # noqa: E402
    print("loading data and fitting models ...", flush=True)
    E = Engine()
    print(f"engine ready in {E.startup_s}s", flush=True)

GET = {"/api/meta": lambda: E.meta(), "/api/findings": lambda: E.findings(), "/api/market/premium": lambda: E.premium(),
       "/api/market/sankey": lambda: E.sankey(), "/api/market/gap": lambda: E.gap(), "/api/market/bundles": lambda: E.bundles(),
       "/api/graph": lambda: E.graph(), "/api/embedding": lambda: E.embedding(), "/api/confidence": lambda: E.conf, "/api/jd-examples": lambda: E.jd_examples(), "/api/showcase": lambda: E.showcase()}
POST = {"/api/jd-audit": lambda b: E.jd_audit(b.get("text", "")), "/api/analyze": lambda b: E.analyze(b), "/api/whatif": lambda b: E.whatif(b), "/api/xray": lambda b: E.xray(b.get("text", "")),
        "/api/compare": lambda b: E.compare(b.get("a", {}), b.get("b", {})),
        "/api/counterfactual": lambda b: E.counterfactual(E.analyze(b)["input"]["skills" if b.get("profile") != "senior" else "traits"],
                                                          "senior" if b.get("profile") == "senior" else "junior")}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(FRONT), **k)

    def log_message(self, fmt, *args):
        if "/api/" in str(args[0] if args else ""):
            sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def _json(self, obj, code=200):
        body = json.dumps(obj, default=_default).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def _mock(self, path):
        f = MOCK_DIR / (path.strip("/").replace("/", "_") + ".json")
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"error": f"no mock for {path}"}

    def do_OPTIONS(self):
        self.send_response(204)
        for h, v in [("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"), ("Access-Control-Allow-Headers", "Content-Type")]:
            self.send_header(h, v)
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/"):
            if path not in GET:
                return self._json({"error": "unknown endpoint"}, 404)
            try:
                return self._json(self._mock(path) if MOCK else GET[path]())
            except Exception as e:  # keep the UI alive; report the error
                traceback.print_exc(); return self._json({"error": str(e)}, 500)
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path not in POST:
            return self._json({"error": "unknown endpoint"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            return self._json(self._mock(path) if MOCK else POST[path](body))
        except Exception as e:
            traceback.print_exc(); return self._json({"error": str(e)}, 500)


def _default(o):
    import numpy as np
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


if __name__ == "__main__":
    print(f"Vriddhi AI on http://127.0.0.1:{PORT}/  (frontend: {FRONT})", flush=True)
    import socket
    import threading

    class V6(ThreadingHTTPServer):
        address_family = socket.AF_INET6
    servers = [ThreadingHTTPServer(("127.0.0.1", PORT), Handler)]  # loopback only: never exposed on the network
    try:
        servers.append(V6(("::1", PORT), Handler))  # 'localhost' may resolve to IPv6
    except OSError:
        pass
    for s in servers[1:]:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    servers[0].serve_forever()
