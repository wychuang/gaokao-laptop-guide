$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$index = Join-Path $root "index.html"
$data = Join-Path $root "data/laptops.json"

if (-not (Test-Path $index)) { throw "Missing src/index.html" }
if (-not (Test-Path $data)) { throw "Missing data/laptops.json" }

$json = Get-Content $data -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $json.items -or $json.items.Count -lt 1) { throw "No laptop items found" }

$html = Get-Content $index -Raw -Encoding UTF8
if ($html -notmatch "laptops.json") { throw "index.html does not load laptops.json" }

Write-Host "OK: static guide files are present and data JSON parses."
