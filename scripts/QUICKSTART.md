# 🚀 Quick Start Guide

## One-Command Setup

Get your Weather & Climate Analytics Pipeline running in minutes with these automated setup scripts!

### For Windows Users

**Prerequisites:**
- Git installed
- Docker Desktop running
- Python 3.9+ installed

**Run this command in PowerShell:**

```powershell
# Download and run the setup script
irm https://raw.githubusercontent.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/main/scripts/setup_windows.ps1 | iex
```

**Or download and run locally:**

```powershell
# Download script
curl -O https://raw.githubusercontent.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/main/scripts/setup_windows.ps1

# Run script
.\setup_windows.ps1
```

---

### For Mac/Linux Users

**Prerequisites:**
- Git installed
- Docker installed and running
- Python 3.9+ installed

**Run this command in Terminal:**

```bash
# Download and run the setup script
bash <(curl -fsSL https://raw.githubusercontent.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/main/scripts/setup_unix.sh)
```

**Or download and run locally:**

```bash
# Download script
curl -O https://raw.githubusercontent.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/main/scripts/setup_unix.sh

# Make executable
chmod +x setup_unix.sh

# Run script
./setup_unix.sh
```

---

## What the Script Does

The automated setup script will:

1. ✅ Check that Git, Docker, and Python are installed
2. ✅ Clone the repository
3. ✅ Configure environment variables with pre-loaded API keys
4. ✅ Create required data directories
5. ✅ Initialize and start Airflow with Docker
6. ✅ Trigger the weather data ingestion DAG
7. ✅ Install Streamlit and dependencies
8. ✅ Display next steps

**Total setup time:** ~10-15 minutes

---

## After Setup Completes

### 1. Access Airflow UI

Open your browser and go to: **http://localhost:8080**

- **Username:** `airflow`
- **Password:** `airflow`

You should see the `weather_ingestion` DAG running automatically.

### 2. Monitor Data Collection

Wait 5-10 minutes for the first DAG run to complete. You can watch the progress in the Airflow UI.

### 3. Launch Streamlit Dashboard

Once data is collected, launch the dashboard:

**Windows (PowerShell):**
```powershell
cd weather-climate-analytics-pipeline\streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

**Mac/Linux (Terminal):**
```bash
cd weather-climate-analytics-pipeline/streamlit_app
source venv/bin/activate
streamlit run app.py
```

The dashboard will open at **http://localhost:8501**

### 4. (Optional) Trigger Climate Analysis

For historical climate data and advanced analytics:

1. Go to Airflow UI: http://localhost:8080
2. Find the `climate_analysis` DAG
3. Toggle it ON
4. Click the Play button to trigger it
5. Wait 10-15 minutes for completion
6. Refresh your Streamlit dashboard

---

## Troubleshooting

### Docker not running
```bash
# Windows: Open Docker Desktop
# Mac/Linux: Start Docker service
sudo systemctl start docker  # Linux
open -a Docker  # Mac
```

### Port 8080 already in use
```bash
# Check what's using port 8080
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# Kill the process or change Airflow port in docker-compose.yml
```

### Airflow DAG not running
```bash
# Check Airflow logs
cd weather-climate-analytics-pipeline/airflow
docker-compose logs airflow-scheduler

# Restart Airflow
docker-compose restart
```

### No data in dashboard
```bash
# Check if database exists
ls -lh weather-climate-analytics-pipeline/data/weather_analytics.duckdb

# Verify Airflow DAG completed successfully in UI
# Look for green checkmarks on all tasks
```

### Python packages not installing
```bash
# Update pip
python -m pip install --upgrade pip

# Install dependencies again
pip install -r requirements.txt
```

---

## Manual Setup (Alternative)

If you prefer to set up manually instead of using the automated script, see the main [README.md](../README.md) for detailed step-by-step instructions.

---

## Project Structure

After setup, your project will look like this:

```
weather-climate-analytics-pipeline/
├── airflow/
│   ├── dags/                    # Airflow DAG definitions
│   └── docker-compose.yml       # Airflow services
├── data/
│   ├── raw/                     # Raw API responses (JSON)
│   ├── clean/                   # Processed data
│   ├── analytics/               # Aggregated analytics
│   └── weather_analytics.duckdb # DuckDB database
├── src/
│   ├── api_clients/             # OpenWeather & NOAA clients
│   ├── utils/                   # Database & processing utilities
│   └── config/                  # Configuration
├── streamlit_app/
│   ├── app.py                   # Main dashboard
│   ├── pages/                   # Multi-page app
│   └── requirements.txt         # Streamlit dependencies
├── scripts/
│   ├── setup_windows.ps1        # Windows setup script
│   ├── setup_unix.sh            # Mac/Linux setup script
│   └── QUICKSTART.md            # This file
└── .env                         # Environment variables (created by script)
```

---

## What's Next?

### Customize Your Pipeline

- **Add more cities:** Edit `airflow/dags/weather_ingestion_dag.py`
- **Change schedule:** Modify DAG schedule intervals
- **Add data sources:** Integrate new weather APIs
- **Extend analytics:** Add new aggregations and metrics

### Deploy to Production

- **Streamlit Cloud:** Deploy dashboard for free
- **AWS/GCP/Azure:** Run Airflow on cloud infrastructure
- **Docker Hub:** Containerize for easy deployment

### Portfolio Enhancement

- Add Great Expectations for data quality testing
- Implement dbt for data transformations
- Create ML forecasting models
- Add alerting with Airflow notifications

---

## Support

- **Issues:** Report bugs on [GitHub Issues](https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/issues)
- **Documentation:** See [docs/](../docs/) folder
- **Architecture:** Read [ARCHITECTURE.md](../docs/ARCHITECTURE.md)

---

**Happy Data Engineering! 🌦️📊**
