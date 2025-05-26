import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import folium
import warnings
import heapq
import math

from relief_centres import RELIEF_CENTRES 
from district_cities import DISTRICT_CITIES 

# Configure OSMnx settings to handle large areas
def configure_osmnx():
    """Configure OSMnx settings for better performance with large areas"""
    # Increase max query area size (default is ~2.5 billion, we're setting to 50 billion)
    ox.settings.max_query_area_size = 50 * 1000 * 1000 * 1000
    
    # Set timeout directly without requests_kwargs to avoid conflicts
    ox.settings.timeout = 180  # 3 minutes
    
    # Clear any existing requests_kwargs that might cause conflicts
    ox.settings.requests_kwargs = {}
    
    # Configure other settings
    ox.settings.use_cache = True
    ox.settings.cache_folder = "./osmnx_cache"
    
    # Suppress the specific warning about query area size
    warnings.filterwarnings('ignore', 'This area is .* times your configured Overpass max query area size')
    
    print("⚙️  OSMnx configured for large area queries")

# Call configuration at module load
configure_osmnx() 

def get_coordinates(place_name):
    """Get coordinates for a given place name"""
    geolocator = Nominatim(user_agent="uttarakhand-relief-routing")
    location = geolocator.geocode(place_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Coordinates not found for {place_name}")

def get_nearest_node(G, coord):
    """Get the nearest node in the graph to the given coordinates"""
    return ox.distance.nearest_nodes(G, coord[1], coord[0]) 

def get_custom_weight(u, v, k, data):
    """Calculate custom weight for edges based on road type and conditions"""
    base_length = data.get('length', 1)
    
    # If road is blocked, return infinite weight
    if data.get('blocked'):
        return float('inf')
    
    # Adjust weight based on highway type
    highway_type = data.get('highway')
    if isinstance(highway_type, list):
        highway_type = highway_type[0]
    
    if highway_type in ['residential', 'service']:
        return base_length * 1.5
    elif highway_type in ['motorway', 'trunk']:
        return base_length * 0.8
    else:
        return base_length

def dijkstra_shortest_path(G, source, target, weight_func):
    """
    Manual implementation of Dijkstra's algorithm for shortest path
    
    Args:
        G: NetworkX graph
        source: Starting node
        target: Destination node  
        weight_func: Function to calculate edge weights
    
    Returns:
        (path, total_distance) or (None, float('inf')) if no path exists
    """
    print(f"🔍 Running Dijkstra's algorithm from node {source} to {target}")
    
    # Initialize distances and previous nodes
    distances = {node: float('inf') for node in G.nodes()}
    previous = {node: None for node in G.nodes()}
    distances[source] = 0
    
    # Priority queue: [(distance, node)]
    pq = [(0, source)]
    visited = set()
    nodes_processed = 0
    
    print(f"📊 Total nodes in graph: {len(G.nodes())}")
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        nodes_processed += 1
        
        # Progress indicator
        if nodes_processed % 1000 == 0:
            print(f"   Processed {nodes_processed} nodes...")
        
        # Skip if already visited
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # Found target
        if current_node == target:
            print(f"✅ Target reached! Processed {nodes_processed} nodes")
            break
            
        # Skip if current distance is greater than recorded distance
        if current_dist > distances[current_node]:
            continue
        
        # Check all neighbors
        for neighbor in G.neighbors(current_node):
            if neighbor in visited:
                continue
                
            # Calculate weight for each edge (there might be multiple edges)
            min_edge_weight = float('inf')
            for key in G[current_node][neighbor]:
                edge_data = G[current_node][neighbor][key]
                edge_weight = weight_func(current_node, neighbor, key, edge_data)
                min_edge_weight = min(min_edge_weight, edge_weight)
            
            # Calculate new distance
            new_distance = distances[current_node] + min_edge_weight
            
            # Update if we found a shorter path
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))
    
    # Reconstruct path
    if distances[target] == float('inf'):
        print("❌ No path found between source and target")
        return None, float('inf')
    
    # Build path by backtracking
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    
    print(f"✅ Dijkstra completed! Path length: {len(path)} nodes, Total distance: {distances[target]:.2f} meters")
    return path, distances[target]

def dijkstra_all_paths(G, source, targets, weight_func):
    """
    Modified Dijkstra to find shortest paths to multiple targets efficiently
    
    Args:
        G: NetworkX graph
        source: Starting node
        targets: List of target nodes
        weight_func: Function to calculate edge weights
    
    Returns:
        Dictionary {target: (path, distance)} for each reachable target
    """
    print(f"🔍 Running Multi-target Dijkstra from node {source} to {len(targets)} targets")
    
    # Initialize
    distances = {node: float('inf') for node in G.nodes()}
    previous = {node: None for node in G.nodes()}
    distances[source] = 0
    
    pq = [(0, source)]
    visited = set()
    found_targets = {}
    remaining_targets = set(targets)
    nodes_processed = 0
    
    while pq and remaining_targets:
        current_dist, current_node = heapq.heappop(pq)
        nodes_processed += 1
        
        if nodes_processed % 1000 == 0:
            print(f"   Processed {nodes_processed} nodes, {len(remaining_targets)} targets remaining...")
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # Check if current node is one of our targets
        if current_node in remaining_targets:
            # Reconstruct path for this target
            path = []
            temp = current_node
            while temp is not None:
                path.append(temp)
                temp = previous[temp]
            path.reverse()
            
            found_targets[current_node] = (path, distances[current_node])
            remaining_targets.remove(current_node)
            print(f"   ✅ Found path to target {current_node} (distance: {distances[current_node]:.2f}m)")
        
        if current_dist > distances[current_node]:
            continue
        
        # Process neighbors
        for neighbor in G.neighbors(current_node):
            if neighbor in visited:
                continue
                
            min_edge_weight = float('inf')
            for key in G[current_node][neighbor]:
                edge_data = G[current_node][neighbor][key]
                edge_weight = weight_func(current_node, neighbor, key, edge_data)
                min_edge_weight = min(min_edge_weight, edge_weight)
            
            new_distance = distances[current_node] + min_edge_weight
            
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))
    
    print(f"✅ Multi-target Dijkstra completed! Found {len(found_targets)} out of {len(targets)} targets")
    return found_targets
    """Block a road between two nodes"""
    for key in G[u][v]:
        G[u][v][key]['blocked'] = True

def block_road(G, u, v):
    """Block a road between two nodes"""
    for key in G[u][v]:
        G[u][v][key]['blocked'] = True

def find_best_relief_center(district_name, G):
    """Find the best relief center for a given district using manual Dijkstra"""
    if district_name not in DISTRICT_CITIES:
        print(f"District '{district_name}' not found in database.")
        return None, None, None
    
    if district_name not in RELIEF_CENTRES:
        print(f"No relief centres found for district '{district_name}'.")
        return None, None, None
    
    disaster_info = DISTRICT_CITIES[district_name]
    disaster_coord = (disaster_info['lat'], disaster_info['lon'])
    disaster_node = get_nearest_node(G, disaster_coord)
    
    print(f"🎯 Disaster location: {disaster_coord}")
    print(f"🎯 Disaster node ID: {disaster_node}")

    # Get all relief center nodes
    relief_nodes = []
    relief_info_map = {}
    
    for relief_info in RELIEF_CENTRES[district_name]:
        r_coord = (relief_info['lat'], relief_info['lon'])
        r_node = get_nearest_node(G, r_coord)
        relief_nodes.append(r_node)
        relief_info_map[r_node] = {
            'name': relief_info['name'],
            'coord': r_coord
        }
        print(f"🏥 Relief center '{relief_info['name']}' at node {r_node}")
    
    # Use our manual Dijkstra implementation
    print(f"\n🚀 Starting Dijkstra's algorithm to find best relief center...")
    
    # Find paths from disaster location to all relief centers
    found_paths = dijkstra_all_paths(
        G, 
        source=disaster_node, 
        targets=relief_nodes,
        weight_func=lambda u, v, k, data: get_custom_weight(u, v, k, data)
    )
    
    if not found_paths:
        print("❌ No paths found to any relief centers")
        return None, None, None
    
    # Find the best (shortest) path
    best_node = None
    best_distance = float('inf')
    best_path = None
    
    for node, (path, distance) in found_paths.items():
        if distance < best_distance:
            best_distance = distance
            best_path = path
            best_node = node
    
    if best_path:
        best_relief_info = relief_info_map[best_node]
        print(f"\n🏆 BEST RELIEF CENTER FOUND:")
        print(f"   Name: {best_relief_info['name']}")
        print(f"   Distance: {round(best_distance/1000, 2)} km")
        print(f"   Path nodes: {len(best_path)}")
        print(f"   Coordinates: {best_relief_info['coord']}")
        
        return best_path, best_relief_info['coord'], disaster_coord
    else:
        return None, None, None

def dijkstra_step_by_step_demo(G, source, target, weight_func, max_steps=10):
    """
    Demonstration version of Dijkstra that shows step-by-step execution
    """
    print(f"\n🎓 DIJKSTRA'S ALGORITHM STEP-BY-STEP DEMO")
    print(f"=" * 50)
    print(f"Source: {source}, Target: {target}")
    
    distances = {node: float('inf') for node in G.nodes()}
    previous = {node: None for node in G.nodes()}
    distances[source] = 0
    
    pq = [(0, source)]
    visited = set()
    step = 0
    
    print(f"\nStep 0: Initialize")
    print(f"   Distance to source {source}: 0")
    print(f"   Priority queue: {pq[:3]}{'...' if len(pq) > 3 else ''}")
    
    while pq and step < max_steps:
        step += 1
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        print(f"\nStep {step}: Processing node {current_node}")
        print(f"   Current distance: {current_dist:.2f}")
        print(f"   Visited nodes: {len(visited)}")
        
        if current_node == target:
            print(f"   🎉 TARGET REACHED!")
            break
        
        neighbors_updated = 0
        for neighbor in list(G.neighbors(current_node))[:3]:  # Show first 3 neighbors
            if neighbor in visited:
                continue
                
            min_edge_weight = float('inf')
            for key in G[current_node][neighbor]:
                edge_data = G[current_node][neighbor][key]
                edge_weight = weight_func(current_node, neighbor, key, edge_data)
                min_edge_weight = min(min_edge_weight, edge_weight)
            
            new_distance = distances[current_node] + min_edge_weight
            
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))
                neighbors_updated += 1
                print(f"   Updated neighbor {neighbor}: distance = {new_distance:.2f}")
        
        print(f"   Updated {neighbors_updated} neighbors")
        print(f"   Priority queue size: {len(pq)}")
    
    if step >= max_steps:
        print(f"\n⏸️  Demo stopped after {max_steps} steps (algorithm continues...)")
    
    return step
    """Find the best relief center for a given district"""
    if district_name not in DISTRICT_CITIES:
        print(f"District '{district_name}' not found in database.")
        return None, None, None
    
    if district_name not in RELIEF_CENTRES:
        print(f"No relief centres found for district '{district_name}'.")
        return None, None, None
    
    disaster_info = DISTRICT_CITIES[district_name]
    disaster_coord = (disaster_info['lat'], disaster_info['lon'])
    disaster_node = get_nearest_node(G, disaster_coord)

    best_path = None
    best_distance = float('inf')
    best_relief_name = None
    best_relief_coord = None

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
                best_relief_coord = r_coord
        except nx.NetworkXNoPath:
            continue

    if best_path:
        print(f"Selected relief centre: {best_relief_name} (Distance: {round(best_distance/1000, 2)} km)")
        return best_path, best_relief_coord, disaster_coord
    else:
        return None, None, None

def path_to_coordinates(G, path):
    """Convert path nodes to coordinates"""
    return [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]

def draw_route_map(route_coords, start_coord, end_coord, relief_name, district_name):
    """Create and save a folium map with the route"""
    # Calculate center point for map
    center_lat = (start_coord[0] + end_coord[0]) / 2
    center_lon = (start_coord[1] + end_coord[1]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9)
    
    # Add markers
    folium.Marker(start_coord, 
                  tooltip=f"Relief Centre: {relief_name}", 
                  icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(end_coord, 
                  tooltip=f"Disaster Area: {district_name}", 
                  icon=folium.Icon(color='red')).add_to(m)
    
    # Add route
    folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.8).add_to(m)
    
    # Save map
    map_filename = "optimized_route_map.html"
    m.save(map_filename)
    print(f"🗺️ Route map saved to: {map_filename}")
    return map_filename

def load_graph_optimized():
    """Load graph with optimized settings to reduce query size"""
    # Option 1: Increase max query area size
    ox.settings.max_query_area_size = 50 * 1000 * 1000 * 1000  # 50 billion square meters
    
    # Option 2: Configure timeout and other settings
    ox.settings.timeout = 300  # 5 minutes timeout
    ox.settings.requests_kwargs = {'timeout': 300}
    
    print("📡 Loading Uttarakhand road network with optimized settings...")
    print("⏱️  This may take 5-10 minutes due to the large area...")
    
    try:
        # Try loading the full state
        G = ox.graph_from_place("Uttarakhand, India", network_type='drive')
        G = ox.add_edge_lengths(G)
        print("✅ Full road network loaded successfully!")
        return G
    except Exception as e:
        print(f"⚠️  Full state loading failed: {str(e)}")
        print("🔄 Trying alternative approach...")
        return None

def load_graph_by_bbox():
    """Load graph using bounding box coordinates for better control"""
    # Uttarakhand approximate bounding box
    north, south, east, west = 31.5, 28.6, 81.0, 77.5
    
    print("📡 Loading road network using bounding box...")
    try:
        G = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive')
        G = ox.add_edge_lengths(G)
        print("✅ Road network loaded via bounding box!")
        return G
    except Exception as e:
        print(f"❌ Bounding box loading failed: {str(e)}")
        return None

def load_graph_simple():
    """Simple graph loading with minimal configuration"""
    print("📡 Loading road network with basic settings...")
    try:
        # Reset OSMnx to default settings first
        ox.settings.timeout = 180
        ox.settings.max_query_area_size = 50 * 1000 * 1000 * 1000
        
        # Try a simpler approach
        G = ox.graph_from_place("Uttarakhand, India", network_type='drive', simplify=True)
        G = ox.add_edge_lengths(G)
        print("✅ Road network loaded with basic settings!")
        return G
    except Exception as e:
        print(f"❌ Basic loading failed: {str(e)}")
        return None

def load_graph_by_districts():
    """Load smaller graphs for specific districts and combine them"""
    print("📡 Loading road networks by districts...")
    combined_graphs = []
    
    # Load graphs for major districts
    major_districts = ["Dehradun", "Haridwar", "Nainital", "Almora", "Chamoli", "Pauri Garhwal", "Uttarkashi"]
    
    for district in major_districts:
        try:
            print(f"  Loading {district}...")
            district_query = f"{district}, Uttarakhand, India"
            G_district = ox.graph_from_place(district_query, network_type='drive')
            G_district = ox.add_edge_lengths(G_district)
            combined_graphs.append(G_district)
            print(f"  ✅ {district} loaded ({len(G_district.nodes)} nodes, {len(G_district.edges)} edges)")
        except Exception as e:
            print(f"  ⚠️  {district} failed: {str(e)}")
    
    if combined_graphs:
        # Combine all district graphs
        print("🔗 Combining district graphs...")
        G = combined_graphs[0]
        total_nodes = len(G.nodes)
        total_edges = len(G.edges)
        
        for i, graph in enumerate(combined_graphs[1:], 1):
            try:
                G = nx.compose(G, graph)
                print(f"  Combined district {i+1}/{len(combined_graphs)}")
            except Exception as e:
                print(f"  ⚠️  Failed to combine district {i+1}: {str(e)}")
        
        final_nodes = len(G.nodes)
        final_edges = len(G.edges)
        print(f"✅ Combined district network ready!")
        print(f"   Total nodes: {final_nodes}")
        print(f"   Total edges: {final_edges}")
        print(f"   Successfully loaded {len(combined_graphs)} districts")
        return G
    else:
        print("❌ Failed to load any district networks")
        return None
    """Load using a smaller polygon approach"""
    print("📡 Loading road network using smaller regions...")
    try:
        # Try loading just the central part of Uttarakhand
        place_name = "Uttarakhand, India"
        
        # Get the place boundary but with more restrictive settings
        gdf = ox.geocode_to_gdf(place_name)
        
        # Create a smaller bounding box from the center
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2
        
        # Create a smaller area around the center (about 50% of original size)
        width = (bounds[2] - bounds[0]) * 0.7
        height = (bounds[3] - bounds[1]) * 0.7
        
        small_bbox = (
            center_y + height/2,  # north
            center_y - height/2,  # south  
            center_x + width/2,   # east
            center_x - width/2    # west
        )
        
        G = ox.graph_from_bbox(bbox=small_bbox, network_type='drive')
        G = ox.add_edge_lengths(G)
        print("✅ Road network loaded using central region!")
        return G
    except Exception as e:
        print(f"❌ Polygon loading failed: {str(e)}")
        return None
    """Load smaller graphs for specific districts and combine them"""
    print("📡 Loading road networks by districts...")
    combined_graphs = []
    
    # Load graphs for major districts
    major_districts = ["Dehradun", "Haridwar", "Nainital", "Almora", "Chamoli"]
    
    for district in major_districts:
        try:
            print(f"  Loading {district}...")
            district_query = f"{district}, Uttarakhand, India"
            G_district = ox.graph_from_place(district_query, network_type='drive')
            G_district = ox.add_edge_lengths(G_district)
            combined_graphs.append(G_district)
            print(f"  ✅ {district} loaded")
        except Exception as e:
            print(f"  ⚠️  {district} failed: {str(e)}")
    
    if combined_graphs:
        # Combine all district graphs
        print("🔗 Combining district graphs...")
        G = combined_graphs[0]
        for graph in combined_graphs[1:]:
            G = nx.compose(G, graph)
        print("✅ Combined district network ready!")
        return G
    else:
        return None

def main():
    """Main function to execute the relief routing system"""
    try:
        print("🚨 Uttarakhand Disaster Relief Routing System")
        print("=" * 50)
        
        # Try different loading strategies
        G = None
        
        # Strategy 1: Try simple loading first
        G = load_graph_simple()
        
        # Strategy 2: Try optimized full loading
        if G is None:
            G = load_graph_optimized()
        
        
        # Strategy 4: If full loading fails, try bounding box
        if G is None:
            G = load_graph_by_bbox()
        
        # Strategy 5: If bounding box fails, load by districts
        if G is None:
            G = load_graph_by_districts()
        
        # Strategy 6: Last resort - load a smaller area
        if G is None:
            print("🔄 Loading single district (Dehradun) as fallback...")
            try:
                G = ox.graph_from_place("Dehradun, India", network_type='drive')
                G = ox.add_edge_lengths(G)
                print("✅ Fallback area loaded! (Limited to Dehradun region)")
            except Exception as e:
                print(f"❌ Even fallback failed: {str(e)}")
        
        if G is None:
            raise Exception("Failed to load any road network data. Please check your internet connection.")

        # Optional: block a road for demo
        # Example: block_road(G, node_id1, node_id2)

        # 2. Input disaster district
        print(f"\nAvailable districts: {list(DISTRICT_CITIES.keys())}")
        district_input = input("\nEnter disaster-affected district: ").strip()

        # 3. Find best route using manual Dijkstra
        print(f"\n🔍 Finding optimal route from relief centres to {district_input} using Dijkstra's algorithm...")
        
        # Optional: Show step-by-step demo for educational purposes
        show_demo = input("Show Dijkstra step-by-step demo? (y/n): ").lower().strip() == 'y'
        
        path, relief_coord, disaster_coord = find_best_relief_center(district_input, G)
        
        if show_demo and path and len(path) > 1:
            print(f"\n📚 Educational Demo:")
            dijkstra_step_by_step_demo(
                G, 
                source=path[0], 
                target=path[-1], 
                weight_func=lambda u, v, k, data: get_custom_weight(u, v, k, data),
                max_steps=5
            )

        if path:
            coords = path_to_coordinates(G, path)
            
            # Calculate route statistics
            route_length_km = round(sum(ox.utils_graph.get_route_edge_attributes(G, path, 'length')) / 1000, 2)
            
            print(f"\n✅ Optimized route found!")
            print(f"📍 Relief Centre Coords: {relief_coord}")
            print(f"📍 Disaster Location Coords: {disaster_coord}")
            print(f"📏 Route Distance: {route_length_km} km")
            print(f"📎 Total Road Junctions on path: {len(path)}")

            # Create and save map
            relief_name = None
            for relief_info in RELIEF_CENTRES[district_input]:
                if (relief_info['lat'], relief_info['lon']) == relief_coord:
                    relief_name = relief_info['name']
                    break
            
            draw_route_map(coords, relief_coord, disaster_coord, relief_name, district_input)
            print("\n🔍 Open the HTML file in a browser to view the visual route.")
            
        else:
            print(f"\n❌ No available route found to {district_input} due to network issues or disconnected roads.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Program interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your internet connection and input data.")

if __name__ == "__main__":
    main()