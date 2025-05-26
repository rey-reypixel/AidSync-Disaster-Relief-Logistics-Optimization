import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import folium
import heapq
from shapely.geometry import Polygon  # Import the Polygon class

from relief_centres import RELIEF_CENTRES 
from district_cities import DISTRICT_CITIES 

def get_coordinates(place_name):
    geolocator = Nominatim(user_agent="uttarakhand-relief-routing")
    location = geolocator.geocode(place_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Coordinates not found for {place_name}")

def get_nearest_node(G, coord):
    return ox.distance.nearest_nodes(G, coord[1], coord[0]) 

def get_custom_weight(u, v, k, data):
    base_length = data.get('length', 1)
    if data.get('blocked'):
        return float('inf')
    highway_type = data.get('highway')
    if isinstance(highway_type, list):
        highway_type = highway_type[0]
    if highway_type in ['residential', 'service']:
        return base_length * 1.5
    elif highway_type in ['motorway', 'trunk']:
        return base_length * 0.8
    return base_length

def block_road(G, u, v):
    for key in G[u][v]:
        G[u][v][key]['blocked'] = True

def dijkstra(G, start_node):
    distances = {node: float('inf') for node in G.nodes}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]
    previous_nodes = {node: None for node in G.nodes}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in G.neighbors(current_node):
            edge_data = G[current_node][neighbor]
            weight = get_custom_weight(current_node, neighbor, None, edge_data)
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous_nodes

def find_best_relief_center(district_name, G):
    disaster_info = DISTRICT_CITIES[district_name]
    disaster_coord = (disaster_info['lat'], disaster_info['lon'])
    disaster_node = get_nearest_node(G, disaster_coord)

    best_path = None
    best_distance = float('inf')
    best_relief_name = None

    for relief_info in RELIEF_CENTRES[district_name]:
        r_coord = (relief_info['lat'], relief_info['lon'])
        r_node = get_nearest_node(G, r_coord)

        distances, previous_nodes = dijkstra(G, r_node)

        if distances[disaster_node] < best_distance:
            best_distance = distances[disaster_node]
            best_path = []
            current_node = disaster_node

            while current_node is not None:
                best_path.append(current_node)
                current_node = previous_nodes[current_node]

            best_path.reverse()
            best_relief_name = relief_info['name']

    if best_path:
        print(f"Selected relief centre: {best_relief_name} (Distance: {round(best_distance, 2)} km)")
        return best_path
    else:
        return None

def path_to_coordinates(G, path):
    return [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]

def draw_route_map(route_coords, start, end):
    m = folium.Map(location=start, zoom_start=9)
    folium.Marker(start, tooltip="Relief Centre", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(end, tooltip="Disaster Area", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(route_coords, color='blue', weight=5).add_to(m)
    m.save("optimized_route_map.html")
    print("Saved map to 'optimized_route_map.html'")

if __name__ == "__main__":
    # Define a polygon for Uttarakhand using shapely
    polygon_coords = [
        (30.5, 78.5),  # North-East
        (30.5, 80.5),  # North-West
        (29.5, 80.5),  # South-West
        (29.5, 78.5)   # South-East
    ]
    polygon = Polygon(polygon_coords)  # Create a shapely Polygon

    # Build graph using the polygon
    G = ox.graph_from_polygon(polygon, network_type='drive')

    # 2. Input disaster district
    district_input = input("Enter disaster-affected district (e.g., Chamoli): ").strip()

    # 3. Find best route
    path = find_best_relief_center(district_input, G)

    if path:
        coords = path_to_coordinates(G, path)
        draw_route_map(coords, coords[0], coords[-1])
    else:
        print("No available route found from any relief centre.")
