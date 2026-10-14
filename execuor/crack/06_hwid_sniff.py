#!/usr/bin/env python3
"""Sniff HWID: fake server mode log-only. Jalankan (admin), lalu login di loader
pakai akun VALID (iham). Server catat X-Vexor-HWID asli + body, lalu PROXY
request token ke server asli biar login tetap jalan? TIDAK — server asli
ketutup hosts. Jadi: catat HWID, matikan server, balikin hosts, claim via 05.
Tetap butuh 2 langkah, tapi HWID dijamin 100% sama dengan buatan loader."""
import http.server, ssl, os
HOST, PORT = "127.0.0.1", 443
D = os.path.dirname(os.path.abspath(__file__))
CERT, KEY = os.path.join(D, "vexor.crt"), os.path.join(D, "vexor.key")

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _dump(self):
        ln = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(ln).decode(errors="ignore") if ln else ""
        print("=" * 60)
        print(self.command, self.path)
        for k in ("X-Vexor-HWID", "Authorization", "X-Vexor-License-Key",
                  "X-Discord-Avatar-Url", "Content-Type"):
            if self.headers.get(k): print(f"  {k}: {self.headers.get(k)}")
        print("  body:", body[:400])
        print("=" * 60)
        data = b'{"ok":true}'
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close"); self.end_headers()
        self.wfile.write(data)
    do_POST = _dump
    do_GET = _dump

srv = http.server.HTTPServer((HOST, PORT), H)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(CERT, KEY)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
print("[sniff] server nyala. buka loader, login — HWID muncul di sini.")
print("[sniff] habis dapat HWID: Ctrl+C, 03_uninstall, run 05_claim_and_dump.py")
srv.serve_forever()
