# PyTrafikk

A Python client and web application for accessing Norwegian traffic data from the Norwegian Public Roads Administration (Statens vegvesen).

## Features

- Query traffic registration points across Norway
- Filter by road categories (European, National, County, Municipal, Private)
- Interactive map view showing all measurement points
- Time series analysis with:
  - Hourly and daily traffic volume data
  - Interactive plots
  - Date range selection
  - Station search

## Installation

### From PyPI (recommended)

```bash
pip install pytrafikk
```

### From Source

```bash
# Clone the repository
git clone https://github.com/paulskeie/pytrafikk.git
cd pytrafikk

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Usage

### Web Application

Start the Flask development server:

```bash
flask --app pytrafikk.web.app run
```

Then open http://localhost:5000 in your browser to access:
- Interactive map view at `/map`
- Time series analysis at `/timeseries`

### Python API

```python
from pytrafikk.client import (
    query_traffic_registration_points,
    query_traffic_volume,
    query_traffic_volume_by_day
)

# API base URL
BASE_URL = "https://trafikkdata-api.atlas.vegvesen.no/"

# Get measurement points for different road categories
e_roads = query_traffic_registration_points(BASE_URL, "E")  # European highways
national = query_traffic_registration_points(BASE_URL, "R")  # National roads
county = query_traffic_registration_points(BASE_URL, "F")   # County roads

# Print some point details
for point in e_roads[:3]:
    print(f"Name: {point.name}")
    print(f"ID: {point.id}")
    print(f"Location: {point.location.coordinates.latLon.lat}, {point.location.coordinates.latLon.lon}\n")

# Query hourly traffic volume for yesterday
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

oslo_tz = ZoneInfo("Europe/Oslo")
yesterday = datetime.now(oslo_tz) - timedelta(days=1)
start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
end_time = start_time + timedelta(days=1)

volumes = query_traffic_volume(
    BASE_URL,
    point_id="97411V72313",  # Example: E6 Mortenhals
    from_time=start_time.isoformat(),
    to_time=end_time.isoformat()
)

# Print hourly volumes
for volume in volumes.volumes:
    print(f"Time: {volume.from_time.strftime('%H:%M')} - {volume.to_time.strftime('%H:%M')}")
    print(f"Vehicles: {volume.total}")
    print(f"Coverage: {volume.coverage_percentage}%\n")

# Get daily traffic for the last week
week_start = start_time - timedelta(days=7)
daily = query_traffic_volume_by_day(
    BASE_URL,
    point_id="97411V72313",
    from_time=week_start.isoformat(),
    to_time=end_time.isoformat()
)

# Calculate average daily traffic
avg_traffic = sum(v.total for v in daily.volumes) / len(daily.volumes)
print(f"Average daily traffic: {avg_traffic:.0f} vehicles")

# Query hourly traffic volume for a point
volume_data = query_traffic_volume(
    BASE_URL,
    point_id="97411V72313",  # Example: E6 Mortenhals
    from_time="2024-01-01T00:00:00+01:00",
    to_time="2024-01-03T00:00:00+01:00"
)

# Create a DataFrame from the volume data
df = pd.DataFrame([
            {
                'timestamp': v.from_time,
                'volume': v.total,
                'coverage': v.coverage_percentage,
                'weekday': v.from_time.strftime('%A')
            }
            for v in volume_data.volumes
        ])

```

## Development

### Running Tests

Tests are written using pytest and can be run with:

```bash
pytest
```

### Project Structure

```
pytrafikk/
├── __init__.py
├── client.py          # Core API client
├── explore.py         # Road category analysis tools
├── tests/
│   └── test_client.py # API client tests
└── web/              # Flask web application
    ├── app.py
    └── templates/
        ├── index.html
        ├── map.html
        └── timeseries.html
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
