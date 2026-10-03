# Registers a Windows Scheduled Task to start GPT Researcher at logon. :-)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $ProjectRoot "scripts\start-gptr-server.ps1"
$TaskName = "GPT Researcher Server"

if (-not (Test-Path $StartScript)) {
    throw "Start script not found at $StartScript"
}

# Headless conhost gives the server a console with no window. Plain "powershell -WindowStyle Hidden" is shown
# in Windows Terminal when it is the default terminal, and closing that window kills the server. :-)
$action = New-ScheduledTaskAction `
    -Execute "conhost.exe" `
    -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$StartScript`"" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$trigger.Delay = "PT20S"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Starts GPT Researcher FastAPI (uvicorn) at Windows logon." `
    -Force | Out-Null

Write-Host "Registered scheduled task '$TaskName'."
Write-Host "It will start 20 seconds after you log in."
Write-Host "Logs: $ProjectRoot\logs\startup.log"
Write-Host "To remove it later: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
