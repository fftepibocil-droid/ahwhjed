# VEXOR crack — fake local server + hosts redirect
# Cara kerja: vexor-updater.exe ngomong ke https://vexor.wtf (/api/updater/token,
# /api/private/validate, /api/premium/claim, /api/updater/v2/metadata, /api/updater/v2/file).
# Kita belokkan vexor.wtf -> 127.0.0.1, lalu serve respons palsu yang selalu valid.
# HTTPS-nya pakai self-signed cert + install ke Trusted Root (script 02 yang urus).
#
# File:
#   01_fake_server.py  - server HTTPS palsu (login apa aja diterima)
#   02_install.bat     - install cert + patch hosts + run server (ADMIN)
#   03_uninstall.bat   - balikin hosts + hapus cert (ADMIN)

# ============ 01_fake_server.py ============
