param(
  [switch]$Build
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot/..

if ($Build) {
  docker compose build
}

docker compose up -d
Write-Host "Sales API: http://localhost:8000"
Write-Host "Postgres: localhost:5434"
Write-Host "Ready check: curl http://localhost:8000/ready"
