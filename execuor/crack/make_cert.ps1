# make_cert.ps1 — bikin self-signed vexor.wtf yang PASTI exportable.
# New-SelfSignedCertificate kadang bikin KSP key non-exportable walau flag diset.
# .NET + CngKeyCreationParameters mengunci Exportable dari awal. Stdlib powershell aja.
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Security

$dns = "vexor.wtf"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. RSA key exportable di Machine store
$params = New-Object System.Security.Cryptography.CngKeyCreationParameters
$params.ExportPolicy = [System.Security.Cryptography.CngExportPolicies]::AllowExport
$params.KeyCreationOptions = [System.Security.Cryptography.CngKeyCreationOptions]::MachineKey
$params.Provider = [System.Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider
$params.Parameters.Add(
  (New-Object System.Security.Cryptography.CngProperty(
    "Length", [BitConverter]::GetBytes([int32]2048),
    [System.Security.Cryptography.CngPropertyOptions]::None)))
$keyName = "vexor-fake-" + [Guid]::NewGuid().ToString("N")
$key = [System.Security.Cryptography.CngKey]::Create(
  [System.Security.Cryptography.CngAlgorithm]::Rsa, $keyName, $params)
$rsa = New-Object System.Security.Cryptography.RSACng($key)

# 2. CertificateRequest self-signed, CN + SAN vexor.wtf, serverAuth EKU
$req = New-Object System.Security.Cryptography.X509Certificates.CertificateRequest(
  "CN=$dns",
  $rsa,
  [System.Security.Cryptography.HashAlgorithmName]::SHA256,
  [System.Security.Cryptography.RSASignaturePadding]::Pkcs1)
$san = New-Object System.Security.Cryptography.X509Certificates.SubjectAlternativeNameBuilder
$san.AddDnsName($dns)
$req.CertificateExtensions.Add($san.Build())
$req.CertificateExtensions.Add(
  (New-Object System.Security.Cryptography.X509Certificates.X509KeyUsageExtension(
    ([System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature -bor
     [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyEncipherment), $false)))
$eku = New-Object System.Security.Cryptography.OidCollection
$eku.Add((New-Object System.Security.Cryptography.Oid("1.3.6.1.5.5.7.3.1"))) | Out-Null
$req.CertificateExtensions.Add(
  (New-Object System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension($eku, $false)))
$cert = $req.CreateSelfSigned(
  [DateTimeOffset]::Now.AddDays(-1), [DateTimeOffset]::Now.AddYears(10))

# 3. simpan ke LocalMachine\My (butuh admin) + export pfx
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My", "LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()
Write-Host "[+] cert:" $cert.Thumbprint

$pwd = ConvertTo-SecureString -String "vexor" -Force -AsPlainText
[IO.File]::WriteAllBytes("$dir\vexor.pfx", $cert.Export("Pfx", $pwd))
Write-Host "[+] vexor.pfx written."
$rsa.Dispose()
