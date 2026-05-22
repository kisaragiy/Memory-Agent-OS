param([string]$ServiceName = "MemoryAgentOS")

$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if ($nssm) {
    & nssm stop $ServiceName
    & nssm remove $ServiceName confirm
} else {
    sc.exe stop $ServiceName
    sc.exe delete $ServiceName
}
Write-Host "Removed $ServiceName"
