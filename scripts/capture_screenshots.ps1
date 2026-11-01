$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$outDir = "d:\Downloads\pymong\recycletrace\presentation\screenshots"
$userDir = "d:\Downloads\pymong\temp_chrome"

if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

$targets = @(
    @{ Name = "1_homepage.png"; Url = "http://127.0.0.1:5000" },
    @{ Name = "2_public_tracking.png"; Url = "http://127.0.0.1:5000/track/WT-2026-1001" },
    @{ Name = "3_login_screen.png"; Url = "http://127.0.0.1:5000/login" },
    @{ Name = "4_citizen_dashboard.png"; Url = "http://127.0.0.1:5000/preview/citizen" },
    @{ Name = "5_collector_dashboard.png"; Url = "http://127.0.0.1:5000/preview/collector" },
    @{ Name = "6_facility_dashboard.png"; Url = "http://127.0.0.1:5000/preview/facility_operator" },
    @{ Name = "7_admin_analytics.png"; Url = "http://127.0.0.1:5000/preview/admin" }
)

foreach ($t in $targets) {
    $outFile = Join-Path $outDir $t.Name
    Write-Host "Capturing $($t.Name) from $($t.Url)..."
    Start-Process -FilePath $chrome -ArgumentList "--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1280,800", "--virtual-time-budget=2500", "--user-data-dir=$userDir", "--screenshot=$outFile", $t.Url -Wait
}

Write-Host "Screenshots captured successfully in $outDir!"
