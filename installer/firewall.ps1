# Smart Flight Deck Companion - Firewall Configuration
# Run as Administrator

$AppName = "SmartFlightDeck"
$AppPath = "$PSScriptRoot\output\SmartFlightDeck\SmartFlightDeck.exe"
$Port = 8080

Write-Host "Configuring Windows Firewall for $AppName..." -ForegroundColor Cyan

# Remove existing rules (if any)
Write-Host "Removing existing rules..."
Remove-NetFirewallRule -DisplayName "$AppName*" -ErrorAction SilentlyContinue

# Add inbound rule for the application
Write-Host "Adding inbound rule for application..."
New-NetFirewallRule -DisplayName "$AppName App" `
    -Direction Inbound `
    -Program $AppPath `
    -Action Allow `
    -Profile Private `
    -Description "Allow Smart Flight Deck Companion to accept connections"

# Add inbound rule for the port
Write-Host "Adding inbound rule for port $Port..."
New-NetFirewallRule -DisplayName "$AppName Port $Port" `
    -Direction Inbound `
    -LocalPort $Port `
    -Protocol TCP `
    -Action Allow `
    -Profile Private `
    -Description "Allow connections to Smart Flight Deck Companion on port $Port"

Write-Host ""
Write-Host "Firewall configuration complete!" -ForegroundColor Green
Write-Host "Rules added for Private network profile only (home network)."
Write-Host ""
Write-Host "If you have issues, make sure:"
Write-Host "  1. Both PC and mobile are on the same Wi-Fi network"
Write-Host "  2. Your network is set to 'Private' in Windows settings"
