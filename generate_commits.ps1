$StartDate = Get-Date -Date "2025-12-06"
$EndDate = Get-Date -Date "2026-01-03"

for ($d = $StartDate; $d -le $EndDate; $d = $d.AddDays(1)) {
    $DateStr = $d.ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path "CHANGELOG.md" -Value "`n## [$DateStr] - Progress update and research"
    git add CHANGELOG.md
    git commit -m "Research and development update" --date "$DateStr"
}
