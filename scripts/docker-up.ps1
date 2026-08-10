param(
  [switch]$Build
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot/..

if ($Build) {
  docker compose build
}

docker compose up -d
$port = if ($env:SALES_API_HOST_PORT) { $env:SALES_API_HOST_PORT } else { "8001" }
Write-Host "Sales API: http://localhost:$port"
Write-Host "Postgres: localhost:5434"
Write-Host "Ready check: curl http://localhost:$port/ready"
