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

```bash
# Clone the repository
git clone https://github.com/yourusername/pytrafikk.git
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

# Get all European highway measurement points
points = query_traffic_registration_points(BASE_URL, "E")

# Query hourly traffic volume for a point
volumes = query_traffic_volume(
    BASE_URL,
    point_id="97411V72313",  # Example: E6 Mortenhals
    from_time="2024-01-01T00:00:00+01:00",
    to_time="2024-01-02T00:00:00+01:00"
)

# Query daily traffic volume
daily = query_traffic_volume_by_day(
    BASE_URL,
    point_id="97411V72313",
    from_time="2024-01-01T00:00:00+01:00",
    to_time="2024-01-07T00:00:00+01:00"
)
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
