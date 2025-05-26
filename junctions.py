# find_nearest_junctions.py

import osmnx as ox
from district_cities import DISTRICT_CITIES
from relief_centres import RELIEF_CENTRES

# Function to get the nearest junction
def get_nearest_junction(lat, lon):
    try:
        # Create a graph from the point with a larger distance
        G = ox.graph_from_point((lat, lon), dist=1000, network_type='all')
        # Get the nearest junction
        nearest = ox.distance.nearest_nodes(G, lat, lon)
        return (G.nodes[nearest]['y'], G.nodes[nearest]['x'])
    except Exception as e:
        print(f"Error finding nearest junction for ({lat}, {lon}): {e}")
        return None  # Return None if there's an error

# Dictionary to store nearest junctions
nearest_junctions = {}

# Process district cities
for district, cities in DISTRICT_CITIES.items():
    nearest_junctions[district] = {}
    for city, lat, lon in cities:
        junction = get_nearest_junction(lat, lon)
        if junction:
            nearest_junctions[district][city] = {"junction": junction}

# Process relief centers
for district, centers in RELIEF_CENTRES.items():
    if district not in nearest_junctions:
        nearest_junctions[district] = {}
    for center, (lat, lon) in centers.items():
        junction = get_nearest_junction(lat, lon)
        if junction:
            nearest_junctions[district][center] = {"junction": junction}

# Print the nearest junctions
for district, locations in nearest_junctions.items():
    print(f"{district}:")
    for location, data in locations.items():
        print(f"  - {location}: {data['junction']}")
