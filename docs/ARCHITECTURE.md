# System Architecture

## Overview

The Weather & Climate Analytics Pipeline is a production-grade data engineering system demonstrating modern data stack principles and best practices.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ OpenWeatherMap  │  │   NOAA CDO API   │              │
│  │  - Current      │  │  - Historical   │              │
│  │  - Forecast     │  │  - Climate Data │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────┘
            │                           │
            │                           │
            ▼                           ▼
┌─────────────────────────────────────────────────────┐
│              INGESTION LAYER (Airflow)                     │
│                                                              │
│  ┌────────────────────────────────────────────┐  │
│  │         API Clients                          │  │
│  │  - OpenWeatherClient                          │  │
│  │  - NOAAClient                                 │  │
│  │  - Retry Logic & Error Handling               │  │
│  └────────────────────────────────────────────┘  │
│                        │                                   │
│  ┌────────────────────────────────────────────┐  │
│  │         Orchestration DAGs                   │  │
│  │  - weather_ingestion (Hourly)                 │  │
│  │  - climate_analysis (Daily)                   │  │
│  └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│           STORAGE LAYER (DuckDB)                           │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐              │
│  │   Raw Schema   │  │  Clean Schema  │              │
│  │  - weather    │  │  - daily       │              │
│  │  - forecast   │  │  - aggregated  │              │
│  │  - climate    │  └────────────────┘              │
│  └────────────────┘                                 │
│                    ┌─────────────────────┐      │
│                    │ Analytics Schema  │      │
│                    │  - trends         │      │
│                    │  - patterns       │      │
│                    └─────────────────────┘      │
└─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│         PRESENTATION LAYER (Streamlit)                      │
│                                                              │
│  - Real-time dashboards                                      │
│  - Interactive visualizations                                │
│  - Multi-page analytics                                      │
└─────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Sources

#### OpenWeatherMap API
- **Purpose**: Real-time and forecast weather data
- **Endpoints**:
  - Current weather
  - 5-day forecast (3-hour intervals)
  - Air quality data
  - Geocoding
- **Rate Limits**: 60 calls/minute (free tier)
- **Update Frequency**: Hourly

#### NOAA CDO API
- **Purpose**: Historical climate data
- **Datasets**: GHCND (Daily Summaries)
- **Data Types**: TMAX, TMIN, PRCP, SNOW
- **Rate Limits**: 1000 calls/day
- **Update Frequency**: Daily

### 2. Ingestion Layer

#### Apache Airflow
- **Version**: 2.8.1
- **Executor**: LocalExecutor (upgradable to Celery)
- **Backend**: PostgreSQL
- **Scheduling**: Cron-based

#### DAGs

**weather_ingestion**:
- Schedule: `0 * * * *` (hourly)
- Tasks:
  1. Initialize database
  2. Fetch current weather (parallel)
  3. Fetch forecasts (parallel)
  4. Process and load data
  5. Aggregate to daily summaries
- Retry: 3 attempts
- Timeout: 30 minutes

**climate_analysis**:
- Schedule: `0 2 * * *` (daily at 2 AM)
- Tasks:
  1. Fetch NOAA climate data
  2. Process and load
  3. Compute temperature trends
  4. Compute weather patterns
- Retry: 2 attempts
- Timeout: 60 minutes

### 3. Storage Layer

#### DuckDB
- **Type**: Embedded OLAP database
- **File**: `weather_analytics.duckdb`
- **Size**: ~10-100 MB (grows with data)
- **Query Performance**: <100ms for typical queries

#### Schema Design

**Raw Schema** (Bronze Layer):
- `weather_current`: Current weather snapshots
- `weather_forecast`: Forecast data
- `climate_data`: NOAA historical data
- **Purpose**: Store unmodified API responses
- **Retention**: All historical data

**Clean Schema** (Silver Layer):
- `weather_daily`: Daily aggregated weather
- **Purpose**: Validated, transformed data
- **Quality**: Data quality checks applied
- **Retention**: Rolling 2 years

**Analytics Schema** (Gold Layer):
- `temperature_trends`: Monthly trends by city
- `weather_patterns`: Condition frequencies
- **Purpose**: Pre-computed analytics
- **Update**: Daily refresh

### 4. Presentation Layer

#### Streamlit Dashboard
- **Framework**: Streamlit 1.29.0
- **Visualization**: Plotly
- **Caching**: 5-minute TTL
- **Pages**:
  1. Main: Current weather + trends
  2. Advanced Analytics: Statistical analysis
  3. Geographic View: Map visualizations

## Data Flow

### Batch Processing

```
1. API Request (Airflow Task)
   ↓
2. JSON Response
   ↓
3. Save Raw JSON (Backup)
   ↓
4. Transform to DataFrame
   ↓
5. Insert to DuckDB (Raw Schema)
   ↓
6. Data Quality Checks
   ↓
7. Aggregate/Transform
   ↓
8. Load to Clean/Analytics Schemas
   ↓
9. Dashboard Refresh
```

### Query Flow

```
User Request (Streamlit)
   ↓
Check Cache (5 min TTL)
   ↓ (cache miss)
Execute DuckDB Query
   ↓
Transform to DataFrame
   ↓
Generate Plotly Chart
   ↓
Render in Browser
```

## Scalability Considerations

### Current Limits
- **Cities**: 5 (configurable)
- **API Calls**: ~2,000/day
- **Data Volume**: ~10 MB/month
- **Query Performance**: Sub-second

### Scaling Options

**Horizontal Scaling**:
1. Add Celery workers for Airflow
2. Distribute across multiple servers
3. Use message queue (Redis/RabbitMQ)

**Vertical Scaling**:
1. Increase Docker resource limits
2. Optimize DuckDB indexes
3. Add query result caching

**Data Scaling**:
1. Partition DuckDB by date
2. Archive old data to S3
3. Implement data retention policies

## Security

### Current Implementation
- API keys in environment variables
- No public endpoints
- Local database file

### Production Recommendations
1. Use secrets manager (AWS Secrets Manager)
2. Enable HTTPS for Streamlit
3. Add authentication (OAuth, LDAP)
4. Encrypt database at rest
5. Implement API rate limiting
6. Add monitoring and alerting

## Technology Choices

### Why DuckDB?
- Embedded (no separate server)
- Fast analytical queries
- SQL interface
- Small footprint
- Perfect for portfolio projects

### Why Airflow?
- Industry standard
- Rich UI for monitoring
- Extensive integrations
- Scalable architecture
- Great for demonstrating orchestration skills

### Why Streamlit?
- Rapid development
- Python-native
- Interactive by default
- Easy deployment
- Professional appearance

## Future Enhancements

1. **Data Quality**:
   - Great Expectations integration
   - Automated anomaly detection
   - Data lineage tracking

2. **Features**:
   - Machine learning forecasts
   - Weather alerts
   - Email reports
   - Mobile app

3. **Infrastructure**:
   - Kubernetes deployment
   - CI/CD pipeline
   - Infrastructure as Code (Terraform)
   - Monitoring (Prometheus/Grafana)

4. **Data**:
   - Additional APIs (Weather Underground)
   - Satellite imagery
   - Air quality expanded
   - UV index, pollen count
