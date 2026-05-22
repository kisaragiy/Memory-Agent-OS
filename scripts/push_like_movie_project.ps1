# 用与 Movie-Recomand-System 相同的方式推送（Windows Git + HTTPS）
# 在 PowerShell 中运行: .\scripts\push_like_movie_project.ps1
$ErrorActionPreference = "Stop"
$Git = "C:\Program Files\Git\cmd\git.exe"
$Repo = "\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem"
$Remote = "https://github.com/kisaragiy/Memory-Agent-OS.git"
$Log = Join-Path $Repo "scripts\push_movie_style.log"

function Log($msg) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

Set-Content -Path $Log -Value "=== push_like_movie_project ===" -Encoding UTF8

& $Git config --global --add safe.directory $Repo 2>$null
& $Git -C $Repo remote set-url origin $Remote
Log "remote: $(& $Git -C $Repo remote get-url origin)"

$branch = & $Git -C $Repo branch --show-current
if (-not $branch) { $branch = "main" }
Log "branch: $branch"
Log "local:  $(& $Git -C $Repo log -1 --oneline)"

# 与远程 Initial commit 合并后推送（若需要）
& $Git -C $Repo fetch origin 2>&1 | Out-String | ForEach-Object { Log $_ }
$pushOut = & $Git -C $Repo push -u origin $branch 2>&1 | Out-String
Log $pushOut

if ($LASTEXITCODE -ne 0) {
    Log "直接 push 失败，尝试 pull --rebase…"
    & $Git -C $Repo pull origin $branch --rebase --allow-unrelated-histories 2>&1 | Out-String | ForEach-Object { Log $_ }
    $pushOut2 = & $Git -C $Repo push -u origin $branch 2>&1 | Out-String
    Log $pushOut2
}

$localSha = (& $Git -C $Repo rev-parse $branch).Trim()
$remoteSha = (& $Git -C $Repo ls-remote origin "refs/heads/$branch" 2>$null | ForEach-Object { ($_ -split '\s+')[0] })
Log "local=$localSha remote=$remoteSha"

if ($localSha -eq $remoteSha) {
    Log "OK: https://github.com/kisaragiy/Memory-Agent-OS"
    exit 0
}
Log "FAIL: 未同步。请在 IDEA 中对本仓库执行 VCS - Push（与电影项目相同账号）。"
exit 1
