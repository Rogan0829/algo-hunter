$logPath = "C:\Users\bonch\clawd\algo_hunter\algo_hunter.log"
$appPath = "C:\Users\bonch\clawd\algo_hunter"

# 이미 실행 중이면 스킵
$running = Get-NetTCPConnection -LocalPort 8502 -ErrorAction SilentlyContinue
if ($running) {
    Write-Output "$(Get-Date): Algo Hunter already running on port 8502" | Out-File $logPath -Append
    exit 0
}

Write-Output "$(Get-Date): Starting Algo Hunter..." | Out-File $logPath -Append
Set-Location $appPath
Start-Process python -ArgumentList "-m", "streamlit", "run", "app.py", "--server.port", "8502", "--server.headless", "true" -WindowStyle Hidden
Write-Output "$(Get-Date): Algo Hunter started." | Out-File $logPath -Append
