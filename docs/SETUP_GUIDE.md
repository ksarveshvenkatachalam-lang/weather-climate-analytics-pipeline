# Complete Setup Guide

## Prerequisites

- Docker & Docker Compose installed
- Python 3.11 or higher
- Git
- API Keys:
  - OpenWeatherMap (free tier)
  - NOAA CDO (free)

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline.git
cd weather-climate-analytics-pipeline
```

### 2. Get API Keys

#### OpenWeatherMap API
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for free account
3. Go to API Keys section
4. Copy your API key

#### NOAA CDO API
1. Visit [NOAA CDO](https://www.ncdc.noaa.gov/cdo-web/token)
2. Enter your email
3. Check email for token
4. Copy token

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Add your keys:
```bash
OPENWEATHER_API_KEY=your_key_here
NOAA_API_KEY=your_token_here
```

### 4. Start Airflow

```bash
cd airflow

# Initialize Airflow (first time only)
docker-compose up airflow-init

# Start Airflow services
docker-compose up -d

# Check services are running
docker-compose ps
```

### 5. Access Airflow UI

1. Open browser: `http://localhost:8080`
2. Login:
   - Username: `airflow`
   - Password: `airflow`

### 6. Enable and Run DAGs

1. In Airflow UI, toggle ON:
   - `weather_ingestion`
   - `climate_analysis`

2. Trigger manual run:
   - Click on DAG name
   - Click "Trigger DAG" button (play icon)
   - Monitor progress in Graph view

3. Wait for first run to complete (5-10 minutes)

### 7. Verify Data

```bash
# Check if database was created
ls -lh data/weather_analytics.duckdb

# Optional: Query database
python3 << EOF
import duckdb
conn = duckdb.connect('data/weather_analytics.duckdb')
print(conn.execute("SELECT COUNT(*) FROM raw.weather_current").fetchone())
conn.close()
EOF
```

### 8. Install Streamlit Dependencies

```bash
cd ../streamlit_app
pip install -r requirements.txt
```

### 9. Run Dashboard

```bash
streamlit run app.py
```

### 10. Access Dashboard

Open browser: `http://localhost:8501`

## Troubleshooting

### Airflow Won't Start

```bash
# Check logs
cd airflow
docker-compose logs airflow-webserver

# Restart services
docker-compose down
docker-compose up -d
```

### DAGs Not Appearing

```bash
# Check DAG folder is mounted
docker-compose exec airflow-webserver ls -la /opt/airflow/dags

# Check for Python errors
docker-compose logs airflow-scheduler | grep ERROR
```

### API Request Failures

1. Verify API keys in `.env`
2. Check API rate limits
3. View DAG logs in Airflow UI
4. Test API manually:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENWEATHER_API_KEY')

response = requests.get(
    f"https://api.openweathermap.org/data/2.5/weather?q=London,GB&appid={api_key}"
)
print(response.json())
```

### No Data in Dashboard

1. Ensure DAGs have run successfully
2. Check database has data:
   ```bash
   ls -lh data/weather_analytics.duckdb
   ```
3. Verify DUCKDB_PATH in environment
4. Check Streamlit logs for errors

### Port Conflicts

If ports 8080 or 8501 are in use:

**Airflow (8080)**:
```yaml
# Edit airflow/docker-compose.yml
services:
  airflow-webserver:
    ports:
      - "8081:8080"  # Change to 8081
```

**Streamlit (8501)**:
```bash
streamlit run app.py --server.port 8502
```

## Production Deployment

### Secure API Keys

1. Use secrets management (AWS Secrets Manager, Azure Key Vault)
2. Never commit `.env` to git
3. Use environment variables in production

### Scale Airflow

```yaml
# Edit docker-compose.yml
environment:
  - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
```

Add Redis and Celery workers.

### Deploy Streamlit

Options:
1. **Streamlit Cloud** (free, easy)
2. **AWS EC2** with Docker
3. **Heroku** with buildpack
4. **Google Cloud Run**

### Monitor Pipeline

1. Set up Airflow alerting
2. Configure email notifications
3. Add health check endpoints
4. Use monitoring tools (Prometheus, Grafana)

## Next Steps

1. Add more cities to track
2. Implement Great Expectations
3. Add forecast accuracy metrics
4. Create CI/CD pipeline
5. Write comprehensive tests

## Support

For help:
- Check [GitHub Issues](https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/issues)
- Review Airflow logs
- Consult API documentation
