@echo off
:: 06_sniff_hwid.bat — RUN AS ADMIN. nyalain server palsu mode LOG ONLY:
:: loader login (ngarang GPP) -> server catat HWID asli dari header -> tampil di log.
cd /d "%~dp0"
python 06_hwid_sniff.py
pause
