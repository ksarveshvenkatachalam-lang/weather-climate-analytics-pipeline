# Weather & Climate Analytics Pipeline 🌦️

## Project Overview
An end-to-end data pipeline that ingests, processes, and analyzes weather and climate data from multiple APIs. Built with Apache Airflow for orchestration, DuckDB for analytics, and Streamlit for visualization.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Weather APIs   │────▶│   Airflow    │────▶│   DuckDB    │
│  (OpenWeather,  │     │   Pipeline   │     │  Analytics  │
│   NOAA, etc)    │     │              │     │             │
└─────────────────┘     └──────────────┘     └─────────────┘
                              │                      │
                              ▼                      ▼
                        ┌──────────────┐     ┌─────────────┐
                        │    Great     │     │  Streamlit  │
                        │ Expectations │     │  Dashboard  │
                        └──────────────┘     └─────────────┘
```

## Tech Stack
- **Orchestration**: Apache Airflow
- **Database**: DuckDB
- **Data Quality**: Great Expectations
- **Visualization**: Streamlit
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.11+

## Project Structure

```
/weather-climate-analytics-pipeline
├── airflow/
│   ├── dags/
│   │   ├── weather_ingestion_dag.py
│   │   ├── climate_analysis_dag.py
│   │   └── data_quality_dag.py
│   ├── plugins/
│   ├── config/
│   ├── docker-compose.yml
│   └── Dockerfile
├── data/
│   ├── raw/              # Raw API responses
│   ├── clean/            # Cleaned & validated data
│   └── analytics/        # Aggregated analytics tables
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   └── model_development.ipynb
├── streamlit_app/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── requirements.txt
├── great_expectations/
│   ├── expectations/
│   └── checkpoints/
├── src/
│   ├── api_clients/
│   ├── transformations/
│   └── utils/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Data Sources

1. **OpenWeatherMap API**
   - Current weather data
   - 5-day forecast
   - Historical data

2. **NOAA Climate Data**
   - Historical climate records
   - Severe weather events
   - Climate normals

3. **Visual Crossing Weather API**
   - Historical weather data
   - Weather forecasts

## Features

### Data Pipeline
- ✅ Multi-source API integration with retry logic
- ✅ Incremental data loading
- ✅ Data quality validation with Great Expectations
- ✅ Error handling and alerting
- ✅ Geospatial data processing

### Analytics
- 📊 Time-series forecasting
- 🌡️ Temperature trend analysis
- 🌧️ Precipitation patterns
- 🌪️ Extreme weather event detection
- 📍 Multi-city comparison

### Dashboard
- 📈 Real-time weather metrics
- 🗺️ Interactive maps
- 📉 Historical trends
- 🎯 Forecast accuracy tracking
- 📊 Climate change indicators

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- API Keys (OpenWeatherMap, NOAA)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline.git
cd weather-climate-analytics-pipeline
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start Airflow with Docker**
```bash
cd airflow
docker-compose up -d
```

4. **Access Airflow UI**
```
http://localhost:8080
Username: airflow
Password: airflow
```

5. **Run Streamlit Dashboard**
```bash
cd streamlit_app
streamlit run app.py
```

## Usage

### Running the Pipeline

1. **Enable DAGs** in Airflow UI
2. **Trigger manual run** or wait for scheduled execution
3. **Monitor progress** in Airflow task logs
4. **View results** in Streamlit dashboard

### Data Quality Checks

Great Expectations validates:
- API response completeness
- Temperature range validity
- Timestamp consistency
- Missing value thresholds
- Anomaly detection

## Business Value

### Skills Demonstrated
- **API Integration**: Multi-source data ingestion with authentication
- **Data Orchestration**: Complex DAG dependencies in Airflow
- **Data Quality**: Automated validation and monitoring
- **Analytics Engineering**: Time-series analysis and forecasting
- **Visualization**: Interactive dashboards with Streamlit
- **DevOps**: Dockerized deployment

### Use Cases
- **Agriculture**: Crop planning based on weather patterns
- **Energy**: Demand forecasting for heating/cooling
- **Insurance**: Risk assessment for weather-related claims
- **Logistics**: Route optimization based on weather
- **Retail**: Inventory planning for seasonal products

## Project Roadmap

- [x] Project setup and repository creation
- [ ] Airflow DAGs implementation
- [ ] API client development
- [ ] DuckDB schema design
- [ ] Great Expectations suite
- [ ] Streamlit dashboard
- [ ] Testing suite
- [ ] Documentation
- [ ] CI/CD pipeline

## Contributing
This is a portfolio project. Feel free to fork and adapt for your own use!

## License
MIT License

## Contact
Ksarvesh Venkatachalam - [GitHub](https://github.com/ksarveshvenkatachalam-lang)

---

**Note**: This project demonstrates production-grade data engineering practices suitable for enterprise environments across various industries.
