#!/usr/bin/env python3
"""Dump module asli sekali (pakai akun valid / trial), simpan jadi module.bin
biar fake server bisa serve file beneran setelah crack.
Usage: python 04_dump_module.py --token <JWT> --hwid <HWID>
HWID = nilai header X-Vexor-HWID (cek log loader / Fiddler)."""
import sys, requests, hashlib, argparse
ap = argparse.ArgumentParser()
ap.add_argument("--token", required=True); ap.add_argument("--hwid", required=True)
ap.add_argument("--base", default="https://vexor.wtf"); ap.add_argument("--out", default="module.bin")
a = ap.parse_args()
H = {"Authorization": f"Bearer {a.token}", "X-Vexor-HWID": a.hwid}
m = requests.get(a.base + "/api/updater/v2/metadata", headers=H, timeout=20).json()
print("[meta]", m)
blob = requests.get(a.base + "/api/updater/v2/file", headers=H, timeout=60).content
print(f"[file] {len(blob)} bytes, sha256={hashlib.sha256(blob).hexdigest()}")
open(a.out, "wb").write(blob); print(f"[+] saved {a.out}")
