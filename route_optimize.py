import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import folium

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
        try:
            path = nx.shortest_path(G, source=r_node, target=disaster_node,
                                    weight=lambda u, v, k: get_custom_weight(u, v, k, G[u][v][k]))
            length = nx.path_weight(G, path, weight=lambda u, v, k: get_custom_weight(u, v, k, G[u][v][k]))
            if length < best_distance:
                best_distance = length
                best_path = path
                best_relief_name = relief_info['name']
        except nx.NetworkXNoPath:
            continue

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

'''if name == "main":
# 1. Build graph
    G = ox.graph_from_place("Uttarakhand, India", network_type='drive')
    G = ox.add_edge_lengths(G)


# Optional: block a road for demo
# block_road(G, node_id1, node_id2)

# 2. Input disaster district
    district_input = input("Enter disaster-affected district (e.g., Chamoli): ").strip()

# 3. Find best route
    path = find_best_relief_center(district_input, G)

    if path:
        coords = path_to_coordinates(G, path)
        draw_route_map(coords, coords[0], coords[-1])
    else:
        print("No available route found from any relief centre.")'''

if path:
    coords = path_to_coordinates(G, path)
    print(f"\n✅ Optimized route found between {origin_city} ➡️ {disaster_city}")
    print(f"📍 Relief Centre Coords: {origin_coord}")
    print(f"📍 Disaster Location Coords: {disaster_coord}")
    print(f"📏 Route Distance: {round(sum(ox.utils_graph.get_route_edge_attributes(G, path, 'length')) / 1000, 2)} km")
    print(f"📎 Total Road Junctions on path: {len(path)}")

    # Save map
    import folium
    m = folium.Map(location=origin_coord, zoom_start=9)
    folium.PolyLine(coords, color='blue', weight=4).add_to(m)
    folium.Marker(origin_coord, tooltip="Relief Centre", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(disaster_coord, tooltip="Disaster Area", icon=folium.Icon(color='red')).add_to(m)
    m.save("optimized_route_map.html")

    print(f"🗺️ Route map saved to: optimized_route_map.html\n")
    print("🔍 Open the HTML file in a browser to view the visual route.\n")
else:
    print(f"\n❌ No available route found from {origin_city} to {disaster_city} due to network issues or disconnected roads.")
