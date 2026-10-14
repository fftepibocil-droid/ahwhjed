@echo off
:: 02_install.bat — RUN AS ADMIN. cert exportable via .NET (CngKey), no openssl.
cd /d "%~dp0"
echo [*] hapus cert vexor lama...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem 'Cert:\LocalMachine\My' | Where-Object { $_.Subject -match 'vexor' } | Remove-Item; Get-ChildItem 'Cert:\LocalMachine\Root' | Where-Object { $_.Subject -match 'vexor' } | Remove-Item; Write-Host '[+] lama dibersihkan.'"
echo [*] bikin cert EXPORTABLE via .NET...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0make_cert.ps1"
if errorlevel 1 ( echo [!] bikin cert gagal. & pause & exit /b 1 )
if not exist "%~dp0vexor.pfx" ( echo [!] vexor.pfx tidak muncul. & pause & exit /b 1 )
echo [*] convert pfx -^> pem...
python "%~dp002_pfx_to_pem.py"
if errorlevel 1 ( echo [!] convert gagal. & pause & exit /b 1 )
echo [*] trust cert ke Root...
certutil -addstore Root "%~dp0vexor.crt" >nul
echo [+] cert trusted.
echo [*] patch hosts: vexor.wtf -^> 127.0.0.1
findstr /c:"vexor.wtf" C:\Windows\System32\drivers\etc\hosts >nul
if errorlevel 1 (
  echo 127.0.0.1 vexor.wtf>>C:\Windows\System32\drivers\etc\hosts
  echo [+] hosts patched.
) else ( echo [=] hosts sudah ada vexor.wtf, skip. )
echo [*] tutup: CheatEngine, Wireshark, Fiddler, IDA, dnSpy, PE-bear sebelum run.
echo [*] start fake server (port 443, butuh admin)...
python "%~dp001_fake_server.py"
pause
