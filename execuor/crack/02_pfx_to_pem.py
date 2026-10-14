#!/usr/bin/env python3
"""Convert vexor.pfx (password 'vexor') -> vexor.crt + vexor.key, stdlib only.
Needs: pip install cryptography (sekali aja)."""
try:
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, PublicFormat, NoEncryption,
        pkcs12, BestAvailableEncryption)
except ImportError:
    print("[!] butuh sekali: pip install cryptography")
    raise SystemExit(1)
import os
d = os.path.dirname(os.path.abspath(__file__))
pfx = open(os.path.join(d, "vexor.pfx"), "rb").read()
priv, cert, _ = pkcs12.load_key_and_certificates(pfx, b"vexor")
open(os.path.join(d, "vexor.crt"), "wb").write(cert.public_bytes(Encoding.PEM))
open(os.path.join(d, "vexor.key"), "wb").write(priv.private_bytes(
    Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))
print("[+] vexor.crt + vexor.key written.")
