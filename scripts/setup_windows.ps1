# Weather & Climate Analytics Pipeline - Automated Setup Script for Windows
# This script sets up the complete pipeline with your API keys

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Weather & Climate Analytics Pipeline" -ForegroundColor Cyan
Write-Host "Automated Setup for Windows" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$OPENWEATHER_KEY = "862f5954b893e54f0304d39c6d538cbc"
$NOAA_TOKEN = "qMMkYGzfDpMLjrVWUVbUARDIYTgNVZLV"
$REPO_URL = "https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline.git"
$PROJECT_DIR = "weather-climate-analytics-pipeline"

# Step 1: Check prerequisites
Write-Host "[1/9] Checking prerequisites..." -ForegroundColor Yellow

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed. Please install Git from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed. Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

Write-Host "✓ All prerequisites installed" -ForegroundColor Green
Write-Host ""

# Step 2: Clone repository
Write-Host "[2/9] Cloning repository..." -ForegroundColor Yellow

if (Test-Path $PROJECT_DIR) {
    Write-Host "Directory already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $PROJECT_DIR
}

git clone $REPO_URL
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to clone repository" -ForegroundColor Red
    exit 1
}

Set-Location $PROJECT_DIR
Write-Host "✓ Repository cloned successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Create .env file
Write-Host "[3/9] Configuring environment variables..." -ForegroundColor Yellow

$envContent = @"
OPENWEATHER_API_KEY=$OPENWEATHER_KEY
NOAA_API_KEY=$NOAA_TOKEN
AIRFLOW_UID=50000
AIRFLOW_GID=0
DUCKDB_PATH=../data/weather_analytics.duckdb
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host "✓ Environment file created with API keys" -ForegroundColor Green
Write-Host ""

# Step 4: Create data directories
Write-Host "[4/9] Creating data directories..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "data/raw" | Out-Null
New-Item -ItemType Directory -Force -Path "data/clean" | Out-Null
New-Item -ItemType Directory -Force -Path "data/analytics" | Out-Null

Write-Host "✓ Data directories created" -ForegroundColor Green
Write-Host ""

# Step 5: Initialize Airflow
Write-Host "[5/9] Initializing Airflow (this may take 3-5 minutes)..." -ForegroundColor Yellow

Set-Location airflow
docker-compose up airflow-init

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Airflow initialization failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Airflow initialized" -ForegroundColor Green
Write-Host ""

# Step 6: Start Airflow services
Write-Host "[6/9] Starting Airflow services (this may take 2-3 minutes)..." -ForegroundColor Yellow

docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start Airflow services" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Airflow services started" -ForegroundColor Green
Write-Host "  - Airflow UI: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  - Username: airflow" -ForegroundColor Cyan
Write-Host "  - Password: airflow" -ForegroundColor Cyan
Write-Host ""

# Step 7: Wait for Airflow to be ready
Write-Host "[7/9] Waiting for Airflow to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✓ Airflow should be ready" -ForegroundColor Green
Write-Host ""

# Step 8: Trigger DAGs via API
Write-Host "[8/9] Triggering data pipeline DAGs..." -ForegroundColor Yellow

$airflowUrl = "http://localhost:8080/api/v1"
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("airflow:airflow"))
$headers = @{
    "Authorization" = "Basic $auth"
    "Content-Type" = "application/json"
}

# Enable and trigger weather_ingestion DAG
Write-Host "  Triggering weather_ingestion DAG..." -ForegroundColor Cyan
try {
    # Enable DAG
    Invoke-RestMethod -Uri "$airflowUrl/dags/weather_ingestion" -Method Patch -Headers $headers -Body '{"is_paused": false}' -ErrorAction SilentlyContinue | Out-Null
    
    # Trigger DAG
    Invoke-RestMethod -Uri "$airflowUrl/dags/weather_ingestion/dagRuns" -Method Post -Headers $headers -Body '{}' -ErrorAction SilentlyContinue | Out-Null
    Write-Host "  ✓ weather_ingestion DAG triggered" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Could not trigger via API. Please trigger manually in UI" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✓ DAGs configured" -ForegroundColor Green
Write-Host ""

# Step 9: Install Streamlit dependencies
Write-Host "[9/9] Installing Streamlit dependencies..." -ForegroundColor Yellow

Set-Location ../streamlit_app
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Warning: Some dependencies may not have installed correctly" -ForegroundColor Yellow
} else {
    Write-Host "✓ Streamlit dependencies installed" -ForegroundColor Green
}

Set-Location ..
Write-Host ""

# Final instructions
Write-Host "====================================" -ForegroundColor Green
Write-Host "✓ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open Airflow UI: http://localhost:8080" -ForegroundColor White
Write-Host "   Login: airflow / airflow" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Monitor the 'weather_ingestion' DAG (should be running)" -ForegroundColor White
Write-Host "   Wait 5-10 minutes for first data collection" -ForegroundColor Gray
Write-Host ""
Write-Host "3. After DAG completes, launch Streamlit dashboard:" -ForegroundColor White
Write-Host "   cd streamlit_app" -ForegroundColor Gray
Write-Host "   streamlit run app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Optional: Trigger 'climate_analysis' DAG in Airflow UI" -ForegroundColor White
Write-Host "   (This fetches historical climate data)" -ForegroundColor Gray
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Cyan
Write-Host "- Check DAG status: docker-compose -f airflow/docker-compose.yml logs airflow-scheduler" -ForegroundColor Gray
Write-Host "- Restart Airflow: docker-compose -f airflow/docker-compose.yml restart" -ForegroundColor Gray
Write-Host "- View database: python -c 'import duckdb; conn=duckdb.connect(\"data/weather_analytics.duckdb\"); print(conn.execute(\"SHOW TABLES\").fetchall())'" -ForegroundColor Gray
Write-Host ""
