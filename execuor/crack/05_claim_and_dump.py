#!/usr/bin/env python3
"""Claim VXP key ke server asli + dump module.bin. Hosts HARUS bersih."""
import requests, hashlib, sys, json
BASE = "https://vexor.wtf"
USER = input("username: ").strip()
PW = input("password: ").strip()
KEY = "VXP-4212-65FB-5E2C-69BC-3974-AA05"
HWID = input("HWID (X-Vexor-HWID, intip via Fiddler / biarkan kosong utk auto): ").strip()

# HWID auto: loader derive dari mesin — coba ambil via wmic bios/cpu
if not HWID:
    import subprocess
    try:
        u = subprocess.run(["wmic", "csproduct", "get", "uuid"], capture_output=True, text=True).stdout
        HWID = u.splitlines()[1].strip()
        print("[*] HWID auto:", HWID)
    except Exception as e:
        print("[!] HWID auto gagal:", e); sys.exit(1)

s = requests.Session()
print("[1] login...")
r = s.post(BASE + "/api/updater/token",
    json={"username": USER, "password": PW, "machine_id": HWID, "hwid": HWID}, timeout=20)
print("   ", r.status_code, r.text[:300])
tok = r.json().get("access_token")
if not tok:
    print("[!] login gagal, cek user/pass."); sys.exit(1)
H = {"Authorization": f"Bearer {tok}", "X-Vexor-HWID": HWID, "X-Vexor-License-Key": KEY}
print("[2] claim key...")
r = s.post(BASE + "/api/premium/claim", json={"license_key": KEY, "hwid": HWID}, headers=H, timeout=20)
print("   ", r.status_code, r.text[:300])
print("[3] redeem fallback (kalau claim already_entitled)...")
r = s.post(BASE + "/api/updater/redeem-license", json={"license_key": KEY, "hwid": HWID}, headers=H, timeout=20)
print("   ", r.status_code, r.text[:300])
print("[4] metadata...")
r = s.get(BASE + "/api/updater/v2/metadata", headers=H, timeout=20)
print("   ", r.status_code, r.text[:300])
print("[5] download module...")
r = s.get(BASE + "/api/updater/v2/file", headers=H, timeout=60)
print("    bytes:", len(r.content))
if len(r.content) > 10000:
    open("module.bin", "wb").write(r.content)
    print("[+] saved module.bin sha256=", hashlib.sha256(r.content).hexdigest())
else:
    print("[!] download gagal:", r.text[:300])
