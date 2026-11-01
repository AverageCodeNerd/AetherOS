param(
    [string]$Name = "AetherOS Beta Review",
    [string]$IsoPath = (Join-Path (Split-Path -Parent $PSScriptRoot) "build\aether-welcome-test2.iso"),
    [string]$BaseFolder = (Join-Path (Split-Path -Parent $PSScriptRoot) "build\virtualbox"),
    [int]$MemoryMB = 4096,
    [int]$DiskSizeGB = 32
)

$ErrorActionPreference = "Stop"

$VBoxManage = (Get-Command "VBoxManage.exe" -ErrorAction SilentlyContinue).Source
if (-not $VBoxManage) {
    $DefaultVBoxManage = Join-Path $env:ProgramFiles "Oracle\VirtualBox\VBoxManage.exe"
    if (Test-Path $DefaultVBoxManage) {
        $VBoxManage = $DefaultVBoxManage
    }
}
if (-not $VBoxManage) {
    throw "VBoxManage.exe was not found. Install Oracle VirtualBox or add it to PATH."
}

$IsoPath = [System.IO.Path]::GetFullPath($IsoPath)
$BaseFolder = [System.IO.Path]::GetFullPath($BaseFolder)
$IsoManifest = "$IsoPath.sha256"
if (-not (Test-Path -LiteralPath $IsoPath -PathType Leaf)) {
    throw "ISO not found: $IsoPath"
}
if (-not (Test-Path -LiteralPath $IsoManifest -PathType Leaf)) {
    throw "ISO checksum manifest not found: $IsoManifest"
}
if ($MemoryMB -lt 2048) {
    throw "MemoryMB must be at least 2048."
}
if ($DiskSizeGB -lt 20) {
    throw "DiskSizeGB must be at least 20."
}

$ExpectedHash = ((Get-Content -LiteralPath $IsoManifest -Raw).Trim() -split "\s+")[0]
$ActualHash = (Get-FileHash -LiteralPath $IsoPath -Algorithm SHA256).Hash
if ($ActualHash -ne $ExpectedHash) {
    throw "ISO checksum mismatch. Expected $ExpectedHash, got $ActualHash."
}

$VMFolder = Join-Path $BaseFolder $Name
$DiskPath = Join-Path $VMFolder "$Name.vdi"
if (Test-Path -LiteralPath $VMFolder) {
    throw "VM folder already exists; refusing to overwrite it: $VMFolder"
}

$RegisteredVMs = & $VBoxManage list vms
if ($LASTEXITCODE -ne 0) {
    throw "VBoxManage list vms failed with exit code $LASTEXITCODE."
}
if ($RegisteredVMs -match ('^"' + [regex]::Escape($Name) + '"\s+\{')) {
    throw "A VirtualBox VM named '$Name' is already registered; refusing to modify it."
}

New-Item -ItemType Directory -Path $BaseFolder -Force | Out-Null

& $VBoxManage createvm --name $Name --ostype Debian_64 --basefolder $BaseFolder --register
if ($LASTEXITCODE -ne 0) { throw "VBoxManage createvm failed with exit code $LASTEXITCODE." }

& $VBoxManage modifyvm $Name --memory $MemoryMB --cpus 2 --vram 128 --graphicscontroller vmsvga --firmware efi --ioapic on --boot1 dvd --boot2 disk --boot3 none --boot4 none --nic1 nat --audio-enabled off --usb off
if ($LASTEXITCODE -ne 0) { throw "VBoxManage modifyvm failed with exit code $LASTEXITCODE." }

& $VBoxManage createhd --filename $DiskPath --size ($DiskSizeGB * 1024) --format VDI --variant Standard
if ($LASTEXITCODE -ne 0) { throw "VBoxManage createhd failed with exit code $LASTEXITCODE." }

& $VBoxManage storagectl $Name --name SATA --add sata --controller IntelAhci --portcount 2 --bootable on
if ($LASTEXITCODE -ne 0) { throw "VBoxManage storagectl failed with exit code $LASTEXITCODE." }

& $VBoxManage storageattach $Name --storagectl SATA --port 0 --device 0 --type hdd --medium $DiskPath
if ($LASTEXITCODE -ne 0) { throw "Attaching the virtual disk failed with exit code $LASTEXITCODE." }

& $VBoxManage storageattach $Name --storagectl SATA --port 1 --device 0 --type dvddrive --medium $IsoPath
if ($LASTEXITCODE -ne 0) { throw "Attaching the ISO failed with exit code $LASTEXITCODE." }

Write-Host "Created VirtualBox VM '$Name'."
Write-Host "ISO: $IsoPath (SHA-256 verified: $ActualHash)"
Write-Host "VM files: $VMFolder"
Write-Host "Profile: 4 GB RAM, 2 CPUs, UEFI, NAT, $DiskSizeGB GB dynamically allocated virtual disk."
Write-Host "Start it from VirtualBox Manager. The only install target is its new VDI; no host disks or shared folders are configured."
