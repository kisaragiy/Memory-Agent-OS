$Git = "C:\Program Files\Git\cmd\git.exe"
$Repo = "\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem"
$Log = "$Repo\scripts\do_push_now.log"
$Remote = "https://github.com/kisaragiy/Memory-Agent-OS.git"

Set-Content -Path $Log -Value "" -Encoding UTF8
function L($m) {
    $line = "$(Get-Date -Format 'HH:mm:ss') $m"
    Write-Host $line
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

& $Git config --global --add safe.directory $Repo | Out-Null
& $Git -C $Repo config user.name "张伟强"
& $Git -C $Repo config user.email "126777810+kisaragiy@users.noreply.github.com"
& $Git -C $Repo remote set-url origin $Remote

$br = (& $Git -C $Repo branch --show-current).Trim()
if (-not $br) { $br = "main" }
L "branch=$br"
L "local=$(& $Git -C $Repo log -1 --oneline)"

& $Git -C $Repo fetch origin 2>&1 | ForEach-Object { L "$_" }

$pullOut = & $Git -C $Repo pull origin main --allow-unrelated-histories --no-edit 2>&1
$pullOut | ForEach-Object { L "$_" }

if ($LASTEXITCODE -ne 0) {
    L "pull failed - using force-with-lease (remote only Initial commit)"
    $pushOut = & $Git -C $Repo push -u origin main --force-with-lease 2>&1
} else {
    $pushOut = & $Git -C $Repo push -u origin main 2>&1
}
$pushOut | ForEach-Object { L "$_" }

$local = (& $Git -C $Repo rev-parse HEAD).Trim()
$remoteLine = & $Git -C $Repo ls-remote origin refs/heads/main 2>&1
L "ls-remote: $remoteLine"
$remote = ($remoteLine -split '\s+')[0]

if ($remote -and $remote -ne "85811d8d1d1ce25ea6ee29a0dd99900dde5286be") {
    L "SUCCESS https://github.com/kisaragiy/Memory-Agent-OS"
    exit 0
}
L "FAILED local=$local remote=$remote"
exit 1
