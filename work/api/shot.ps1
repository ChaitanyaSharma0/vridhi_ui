# Headless Edge full-page screenshot of the running app (http://localhost:8770).
# Usage: powershell -File shot.ps1 -Name x -Query "persona=coder&autorun=1" [-Page engine.html] [-W 1440] [-H 3600]
param([string]$Name, [string]$Query = "", [string]$Page = "engine.html", [int]$W = 1440, [int]$H = 3600)
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$out = Join-Path $PSScriptRoot "_shots\$Name.png"
$ud = "$env:TEMP\edge-shot-profile"
$args_ = @("--headless=new", "--disable-gpu", "--hide-scrollbars", "--user-data-dir=`"$ud`"", "--window-size=$W,$H", "--virtual-time-budget=20000", "--screenshot=`"$out`"", "http://localhost:8770/$Page`?$Query")
$p = Start-Process -FilePath $edge -ArgumentList $args_ -Wait -PassThru -WindowStyle Hidden
"$Name -> exit $($p.ExitCode), exists $(Test-Path $out)"
