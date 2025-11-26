# Sets Windows portproxy rules to forward localhost ports to WSL.
# Default mappings: 5050 (MLflow), 8001 (API), 3001 (Frontend)
param(
    [string[]]$Mappings = @("5050:5050", "8001:8001", "3001:3001"),
    [string]$WslIp = $(wsl.exe hostname -I | %{ $_.Split()[0] })
)

Write-Host "WSL IP: $WslIp"
foreach ($map in $Mappings) {
    $parts = $map.Split(":")
    $listen = $parts[0]
    $target = $parts[1]
    Write-Host "Adding portproxy: 127.0.0.1:$listen -> $WslIp:$target"
    netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=$listen connectaddress=$WslIp connectport=$target
}

netsh interface portproxy show all
Write-Host "Test after rules:"
Write-Host "  curl http://localhost:5050/health   # MLflow"
Write-Host "  curl http://localhost:8001/health   # API"
