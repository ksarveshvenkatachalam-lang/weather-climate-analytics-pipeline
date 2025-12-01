# Weather Analytics Dashboard 🌤️

## Overview

Interactive Streamlit dashboard for visualizing real-time weather data and climate analytics from the weather pipeline.

## Features

### 🏠 Current Weather Tab
- Real-time weather conditions for all tracked cities
- Temperature, humidity, wind speed metrics
- Weather descriptions and conditions
- Last updated timestamp

### 📈 Trends Analysis Tab
- Temperature trends over configurable time periods (7-90 days)
- Multi-city comparison charts
- Min/Max temperature ranges visualization
- Summary statistics by city
- Weather conditions distribution

### 🔮 Forecasts Tab
- 5-day weather forecast visualization
- Hourly temperature predictions
- Precipitation probability
- Expandable daily forecast details

### 🌍 Weather Patterns Tab
- Monthly weather pattern heatmaps
- Temperature variance analysis
- Days above/below average trends
- Condition frequency by month

### 📊 Data Quality Tab
- Record counts across pipeline stages
- Data freshness indicators
- Pipeline status monitoring
- Latest record timestamps

### Additional Pages
- **Advanced Analytics**: Statistical analysis, correlations, moving averages
- **Geographic View**: Interactive map with weather overlays

## Installation

### Prerequisites
- Python 3.11+
- DuckDB database populated by Airflow pipeline

### Setup

1. **Install dependencies**:
```bash
cd streamlit_app
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# Copy .env from project root or set DUCKDB_PATH
export DUCKDB_PATH="../data/weather_analytics.duckdb"
```

3. **Run the dashboard**:
```bash
streamlit run app.py
```

4. **Access dashboard**:
```
http://localhost:8501
```

## Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Docker Deployment

Create `Dockerfile` in streamlit_app directory:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t weather-dashboard .
docker run -p 8501:8501 -v $(pwd)/../data:/app/data weather-dashboard
```

### Streamlit Cloud Deployment

1. **Push to GitHub** (already done)

2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select repository: `ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline`
   - Main file path: `streamlit_app/app.py`
   - Click "Deploy"

3. **Configure secrets** in Streamlit Cloud settings:
```toml
DUCKDB_PATH = "/mount/data/weather_analytics.duckdb"
```

**Note**: For Streamlit Cloud, you'll need to modify data access since DuckDB file needs to be accessible. Options:
- Use Streamlit's file upload
- Connect to cloud database (PostgreSQL, Snowflake)
- Use S3/Cloud Storage for DuckDB file

## Configuration

### Theme Customization

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"  # Main accent color
backgroundColor = "#ffffff"  # Background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar
textColor = "#262730"  # Text color
```

### Data Refresh

- Dashboard caches data for 5 minutes (300 seconds)
- Use "Refresh Data" button in sidebar to clear cache
- Automatic refresh on page reload

## Usage Tips

### Optimal Viewing
- Use wide layout for best visualization
- Works on desktop, tablet, and mobile
- Chrome/Firefox recommended

### Performance
- Data is cached for 5 minutes to reduce database load
- Large date ranges (90+ days) may take longer to load
- Use date range selector to optimize performance

### Troubleshooting

**No data displayed**:
- Ensure Airflow DAGs have run at least once
- Check DuckDB path is correct
- Verify database file exists and has data

**Slow loading**:
- Reduce date range in sidebar
- Limit number of cities in multi-select
- Clear browser cache

**Connection errors**:
- Check DuckDB_PATH environment variable
- Ensure database file permissions are correct
- Verify no other process has locked the database

## Project Structure

```
streamlit_app/
├── app.py                    # Main dashboard
├── pages/
│   ├── 1_Advanced_Analytics.py
│   └── 2_Geographic_View.py
├── .streamlit/
│   └── config.toml           # Theme configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Data Flow

```
Airflow DAGs → DuckDB → Streamlit Dashboard
     ↓           ↓              ↓
  API Data    Raw/Clean/    Interactive
             Analytics      Visualizations
```

## Screenshots

*Add screenshots after deployment*

## Contributing

This is a portfolio project. Feel free to fork and customize!

## License

MIT License

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline/issues)
- GitHub Profile: [@ksarveshvenkatachalam-lang](https://github.com/ksarveshvenkatachalam-lang)
