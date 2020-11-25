$ex_pol = Get-Executionpolicy -scope CurrentUser
if (-Not($ex_pol -eq "RemoteSigned"))
{
    Start-Process PowerShell -ArgumentList 'Set-ExecutionPolicy RemoteSigned -scope CurrentUser -force' -Verb RunAs
}

try
{
    get-command scoop > $null -ErrorAction Stop
    Write-Host "Scoop is already installed" -ForegroundColor Green
    Write-Host "checking for updates" -ForegroundColor Cyan
    scoop update
}
catch
{
    Write-Host "Scoop not installed, installing now"
    Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')
    write-host "`n"

}
Write-Host "`nStarting install of programs" -ForegroundColor Cyan
scoop bucket add extras
scoop bucket add versions
scoop install aria2

$programs = "innounp", "python", "git", "ffmpeg", "mpv", "youtube-dl"
foreach ($program in $programs)
{
    try
    {
        get-command $program > $null -ErrorAction Stop
    }
    Catch
    {
        scoop install $program
    }
}
scoop update *

