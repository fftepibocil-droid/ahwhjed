#!/usr/bin/env python3
"""VEXOR fake server — accepts ANY username/password + ANY license key.
Listens HTTPS on 443, answers every auth/validate/claim/metadata endpoint.
Run as ADMIN (port 443). Pair with hosts patch: 127.0.0.1 vexor.wtf"""
import http.server, ssl, json, os, base64, time, hashlib

HOST, PORT = "127.0.0.1", 443
CERT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vexor.crt")
KEY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vexor.key")

def fake_jwt(user="cracked"):
    h = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    p = base64.urlsafe_b64encode(json.dumps({
        "sub": user, "vexor_username": user, "vexor_id": "1337",
        "premium": True, "exp": int(time.time()) + 86400 * 30}).encode()).decode().rstrip("=")
    return f"{h}.{p}."

class H(http.server.BaseHTTPRequestHandler):
    @staticmethod
    def _stub_pe():
        """Minimal valid PE64 (MZ + headers + 1 byte .text) — cukup buat
        lolos size/PE/hash check loader. BUKAN modul asli: step Inject
        bakal gagal/run stub. Fungsinya: konfirmasi full auth chain tembus."""
        import struct
        dos = bytearray(64); dos[0:2] = b"MZ"; struct.pack_into("<I", dos, 0x3C, 64)
        pe = b"PE\x00\x00" + struct.pack("<HHIIIHH", 0x8664, 1, 0, 0, 0, 0xF0, 0x22)
        opt = bytearray(0xF0); struct.pack_into("<H", opt, 0, 0x20B)
        sec = struct.pack("<8sIIIIIIHHI", b".text\x00\x00\x00", 1, 0x1000, 1, 512, 0, 0, 0, 0, 0x60000020)
        hdr = bytes(dos) + pe + bytes(opt) + sec
        body = b"\xC3"  # ret
        return hdr + b"\x00" * (512 - len(hdr)) + body
    def log_message(self, *a): print("[vexor-fake]", *a)
    def body(self):
        try: return self.rfile.read(int(self.headers.get("Content-Length", 0) or 0)).decode(errors="ignore")
        except Exception: return ""
    def send(self, obj, code=200):
        data = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close"); self.end_headers()
        self.wfile.write(data)
        print(f"  -> {code} {data[:300]!r}")
    def send_bin(self, data, code=200, ctype="application/octet-stream"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data))); self.end_headers()
        self.wfile.write(data)
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        try: b = self.rfile.read(length).decode(errors="ignore")
        except Exception: b = ""
        print(f"POST {self.path} H=[{self.headers.get('Content-Type')}] :: {b[:300]}")
        user = "cracked"
        try: user = json.loads(b).get("username") or json.loads(b).get("license_key", "cracked")[:16]
        except Exception: pass
        if self.path.startswith("/api/updater/token"):
            return self.send({"access_token": fake_jwt(user), "token_type": "Bearer",
                "vexor_username": user, "vexor_id": "1337"})
        if self.path.startswith("/api/private/validate") or self.path.startswith("/api/updater/redeem-license"):
            return self.send({"valid": True, "premium": True, "vexor_username": user})
        if self.path.startswith("/api/premium/claim"):
            return self.send({"success": True, "claimed": True, "premium": True, "product": "vexor"})
        if self.path.startswith("/api/presence/"):
            return self.send({"ok": True})
        return self.send({"ok": True, "valid": True, "premium": True})
    def do_GET(self):
        print(f"GET {self.path}")
        if self.path.startswith("/api/updater/v2/metadata") or self.path.startswith("/api/updater/metadata"):
            mod = os.path.join(os.path.dirname(os.path.abspath(__file__)), "module.bin")
            if os.path.exists(mod):
                blob = open(mod, "rb").read()
            else:
                blob = self._stub_pe()
            h = hashlib.sha256(blob).hexdigest(); sz = len(blob)
            return self.send({"sha256": h, "size_bytes": sz, "size": sz,
                "filename": "module.bin", "software_label": "roblox",
                "type": "roblox", "version": "99.99-cracked",
                "url": "/api/updater/v2/file",
                "success": True, "vexor_username": "cracked",
                "vexor_id": "1337", "discord_avatar_url": "",
                "code": "ok"})
        if self.path.startswith("/api/updater/v2/file") or self.path.startswith("/api/updater/file"):
            mod = os.path.join(os.path.dirname(os.path.abspath(__file__)), "module.bin")
            if os.path.exists(mod): return self.send_bin(open(mod, "rb").read())
            # tanpa module asli: serve STUB PE valid biar downloader lolos,
            # hash check dilewati karena sha256 di metadata = hash stub ini
            stub = self._stub_pe()
            return self.send_bin(stub)
        return self.send({"ok": True})

if __name__ == "__main__":
    srv = http.server.HTTPServer((HOST, PORT), H)
    srv.timeout = 10
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, KEY)
    ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    print(f"[vexor-fake] HTTPS https://vexor.wtf/ -> {HOST}:{PORT}  (login apa aja = diterima)")
    srv.serve_forever()
