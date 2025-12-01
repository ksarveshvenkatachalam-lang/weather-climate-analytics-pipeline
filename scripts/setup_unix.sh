#!/bin/bash
# Weather & Climate Analytics Pipeline - Automated Setup Script for Mac/Linux
# This script sets up the complete pipeline with your API keys

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "${CYAN}====================================${NC}"
echo "${CYAN}Weather & Climate Analytics Pipeline${NC}"
echo "${CYAN}Automated Setup for Mac/Linux${NC}"
echo "${CYAN}====================================${NC}"
echo ""

# Configuration
OPENWEATHER_KEY="862f5954b893e54f0304d39c6d538cbc"
NOAA_TOKEN="qMMkYGzfDpMLjrVWUVbUARDIYTgNVZLV"
REPO_URL="https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline.git"
PROJECT_DIR="weather-climate-analytics-pipeline"

# Step 1: Check prerequisites
echo "${YELLOW}[1/9] Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo "${RED}ERROR: Git is not installed. Please install Git first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "${RED}ERROR: Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "${RED}ERROR: Python 3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi

echo "${GREEN}✓ All prerequisites installed${NC}"
echo ""

# Step 2: Clone repository
echo "${YELLOW}[2/9] Cloning repository...${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo "${YELLOW}Directory already exists. Removing...${NC}"
    rm -rf "$PROJECT_DIR"
fi

git clone "$REPO_URL"
cd "$PROJECT_DIR"

echo "${GREEN}✓ Repository cloned successfully${NC}"
echo ""

# Step 3: Create .env file
echo "${YELLOW}[3/9] Configuring environment variables...${NC}"

cat > .env << EOF
OPENWEATHER_API_KEY=$OPENWEATHER_KEY
NOAA_API_KEY=$NOAA_TOKEN
AIRFLOW_UID=$(id -u)
AIRFLOW_GID=0
DUCKDB_PATH=../data/weather_analytics.duckdb
EOF

echo "${GREEN}✓ Environment file created with API keys${NC}"
echo ""

# Step 4: Create data directories
echo "${YELLOW}[4/9] Creating data directories...${NC}"

mkdir -p data/raw data/clean data/analytics

echo "${GREEN}✓ Data directories created${NC}"
echo ""

# Step 5: Initialize Airflow
echo "${YELLOW}[5/9] Initializing Airflow (this may take 3-5 minutes)...${NC}"

cd airflow
docker-compose up airflow-init

echo "${GREEN}✓ Airflow initialized${NC}"
echo ""

# Step 6: Start Airflow services
echo "${YELLOW}[6/9] Starting Airflow services (this may take 2-3 minutes)...${NC}"

docker-compose up -d

echo "${GREEN}✓ Airflow services started${NC}"
echo "${CYAN}  - Airflow UI: http://localhost:8080${NC}"
echo "${CYAN}  - Username: airflow${NC}"
echo "${CYAN}  - Password: airflow${NC}"
echo ""

# Step 7: Wait for Airflow to be ready
echo "${YELLOW}[7/9] Waiting for Airflow to be ready (30 seconds)...${NC}"
sleep 30
echo "${GREEN}✓ Airflow should be ready${NC}"
echo ""

# Step 8: Trigger DAGs via API
echo "${YELLOW}[8/9] Triggering data pipeline DAGs...${NC}"

AIRFLOW_URL="http://localhost:8080/api/v1"
AUTH="airflow:airflow"

# Enable and trigger weather_ingestion DAG
echo "${CYAN}  Triggering weather_ingestion DAG...${NC}"

# Enable DAG
curl -X PATCH "$AIRFLOW_URL/dags/weather_ingestion" \
  -H "Content-Type: application/json" \
  -u "$AUTH" \
  -d '{"is_paused": false}' \
  --silent --output /dev/null || echo "${YELLOW}  ⚠ Could not enable DAG via API${NC}"

# Trigger DAG
curl -X POST "$AIRFLOW_URL/dags/weather_ingestion/dagRuns" \
  -H "Content-Type: application/json" \
  -u "$AUTH" \
  -d '{}' \
  --silent --output /dev/null && echo "${GREEN}  ✓ weather_ingestion DAG triggered${NC}" || echo "${YELLOW}  ⚠ Could not trigger via API. Please trigger manually in UI${NC}"

echo ""
echo "${GREEN}✓ DAGs configured${NC}"
echo ""

# Step 9: Install Streamlit dependencies
echo "${YELLOW}[9/9] Installing Streamlit dependencies...${NC}"

cd ../streamlit_app

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "${GREEN}✓ Streamlit dependencies installed${NC}"
else
    echo "${YELLOW}⚠ Warning: Some dependencies may not have installed correctly${NC}"
fi

cd ..
echo ""

# Final instructions
echo "${GREEN}====================================${NC}"
echo "${GREEN}✓ SETUP COMPLETE!${NC}"
echo "${GREEN}====================================${NC}"
echo ""
echo "${CYAN}Next Steps:${NC}"
echo ""
echo "${NC}1. Open Airflow UI: http://localhost:8080${NC}"
echo "   Login: airflow / airflow"
echo ""
echo "${NC}2. Monitor the 'weather_ingestion' DAG (should be running)${NC}"
echo "   Wait 5-10 minutes for first data collection"
echo ""
echo "${NC}3. After DAG completes, launch Streamlit dashboard:${NC}"
echo "   ${YELLOW}cd streamlit_app${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}streamlit run app.py${NC}"
echo ""
echo "${NC}4. Optional: Trigger 'climate_analysis' DAG in Airflow UI${NC}"
echo "   (This fetches historical climate data)"
echo ""
echo "${CYAN}Troubleshooting:${NC}"
echo "- Check DAG status: ${YELLOW}docker-compose -f airflow/docker-compose.yml logs airflow-scheduler${NC}"
echo "- Restart Airflow: ${YELLOW}docker-compose -f airflow/docker-compose.yml restart${NC}"
echo "- View database: ${YELLOW}python3 -c 'import duckdb; conn=duckdb.connect(\"data/weather_analytics.duckdb\"); print(conn.execute(\"SHOW TABLES\").fetchall())'${NC}"
echo ""
