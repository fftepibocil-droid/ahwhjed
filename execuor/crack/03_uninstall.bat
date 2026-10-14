@echo off
:: 03_uninstall.bat — RUN AS ADMIN. balikin semua.
cd /d "%~dp0"
echo [*] hapus hosts entry...
findstr /v "vexor.wtf" C:\Windows\System32\drivers\etc\hosts > "%TEMP%\hosts_clean"
copy /y "%TEMP%\hosts_clean" C:\Windows\System32\drivers\etc\hosts >nul
del "%TEMP%\hosts_clean"
findstr /c:"vexor.wtf" C:\Windows\System32\drivers\etc\hosts >nul
if errorlevel 1 ( echo [+] hosts bersih. ) else ( echo [!] masih ada, hapus manual via Notepad admin. )
ipconfig /flushdns >nul
echo [*] hapus cert dari Root...
certutil -delstore Root "vexor.wtf"
echo [+] bersih. server asli balik lagi.
pause
