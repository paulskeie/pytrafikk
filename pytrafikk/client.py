import requests
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

# Define dataclasses for structured data
@dataclass
class LatLon:
    lat: float
    lon: float

@dataclass
class Coordinates:
    latLon: LatLon

@dataclass
class Location:
    coordinates: Coordinates

@dataclass
class TrafficRegistrationPoint:
    id: str
    name: str
    location: Location

# Function to query traffic registration points
def query_traffic_registration_points(base_url: str, road_category: str) -> List[TrafficRegistrationPoint]:
    query = """
    {
      trafficRegistrationPoints(searchQuery: {roadCategoryIds: [%s]}) {
        id
        name
        location {
          coordinates {
            latLon {
              lat
              lon
            }
          }
        }
      }
    }
    """ % road_category
    
    response = requests.post(
        base_url,
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code}, {response.text}")
    
    data = response.json().get("data", {}).get("trafficRegistrationPoints", [])
    
    # Map response to dataclasses
    points = []
    for point in data:
        lat_lon = LatLon(
            lat=point["location"]["coordinates"]["latLon"]["lat"],
            lon=point["location"]["coordinates"]["latLon"]["lon"]
        )
        coordinates = Coordinates(latLon=lat_lon)
        location = Location(coordinates=coordinates)
        points.append(TrafficRegistrationPoint(
            id=point["id"],
            name=point["name"],
            location=location
        ))
    return points

@dataclass
class VolumeByHour:
    from_time: datetime
    to_time: datetime
    total: int
    coverage_percentage: float

@dataclass
class VolumeByDay:
    from_time: datetime
    to_time: datetime
    total: int
    coverage_percentage: float

@dataclass 
class TrafficVolume:
    point_id: str
    volumes: List[VolumeByHour]

@dataclass
class DailyTrafficVolume:
    point_id: str
    volumes: List[VolumeByDay]

def query_traffic_volume(base_url: str, point_id: str, from_time: str, to_time: str) -> TrafficVolume:
    volumes = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        # Build the pagination part of the query
        after_arg = f', after: "{after_cursor}"' if after_cursor else ""
        
        query = """
        {
          trafficData(trafficRegistrationPointId: "%s") {
            volume {
              byHour(from: "%s", to: "%s"%s) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                edges {
                  node {
                    from
                    to
                    total {
                      volumeNumbers {
                        volume
                      }
                      coverage {
                        percentage
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """ % (point_id, from_time, to_time, after_arg)
        
        response = requests.post(
            base_url,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed: {response.status_code}, {response.text}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
                
        if "data" not in result:
            raise Exception(f"Unexpected response format: {result}")
                
        by_hour = result.get("data", {}).get("trafficData", {}).get("volume", {}).get("byHour", {})
        
        # Get pagination info
        page_info = by_hour.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")
        
        # Process the current page's data
        for edge in by_hour.get("edges", []):
            node = edge["node"]
            volumes.append(VolumeByHour(
                from_time=datetime.fromisoformat(node["from"]),
                to_time=datetime.fromisoformat(node["to"]),
                total=node["total"]["volumeNumbers"]["volume"],
                coverage_percentage=node["total"]["coverage"]["percentage"]
            ))
    
    return TrafficVolume(point_id=point_id, volumes=volumes)

# Example usage
def query_traffic_volume_by_day(base_url: str, point_id: str, from_time: str, to_time: str) -> DailyTrafficVolume:
    volumes = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        # Build the pagination part of the query
        after_arg = f', after: "{after_cursor}"' if after_cursor else ""
        
        query = """
        {
          trafficData(trafficRegistrationPointId: "%s") {
            volume {
              byDay(from: "%s", to: "%s"%s) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                edges {
                  node {
                    from
                    to
                    total {
                      volumeNumbers {
                        volume
                      }
                      coverage {
                        percentage
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """ % (point_id, from_time, to_time, after_arg)
        
        response = requests.post(
            base_url,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed: {response.status_code}, {response.text}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
                
        if "data" not in result:
            raise Exception(f"Unexpected response format: {result}")
                
        by_day = result.get("data", {}).get("trafficData", {}).get("volume", {}).get("byDay", {})
        
        # Get pagination info
        page_info = by_day.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")
        
        # Process the current page's data
        for edge in by_day.get("edges", []):
            node = edge["node"]
            volumes.append(VolumeByDay(
                from_time=datetime.fromisoformat(node["from"]),
                to_time=datetime.fromisoformat(node["to"]),
                total=node["total"]["volumeNumbers"]["volume"],
                coverage_percentage=node["total"]["coverage"]["percentage"]
            ))
    
    return DailyTrafficVolume(point_id=point_id, volumes=volumes)

if __name__ == "__main__":
    BASE_URL = "https://trafikkdata-api.atlas.vegvesen.no/"
    ROAD_CATEGORY = "E"  # Replace with desired road category

    try:
        traffic_points = query_traffic_registration_points(BASE_URL, ROAD_CATEGORY)
        for point in traffic_points:
            print(f"ID: {point.id}, Name: {point.name}, Lat: {point.location.coordinates.latLon.lat}, Lon: {point.location.coordinates.latLon.lon}")
    except Exception as e:
        print(f"Error: {e}")
