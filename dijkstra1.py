import heapq
import math
import requests
import json
import time
import folium
import webbrowser
import os
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta

from district_cities import DISTRICT_CITIES
from relief_centres import RELIEF_CENTRES

class OSMRoadNetwork:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.city_nodes = {}
        self.relief_nodes = {}
        self.blocked_ways = set()
        
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    
    def get_osm_data(self, bbox: Tuple[float, float, float, float]) -> Dict:
        query = f"""
        [out:json][timeout:30];
        (way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]
         ({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}););
        (._;>;);out geom;
        """
        
        urls = ["https://overpass-api.de/api/interpreter", 
                "http://overpass-api.de/api/interpreter"]
        
        for url in urls:
            try:
                response = requests.post(url, data=query, timeout=30)
                return response.json()
            except:
                continue
        return {"elements": []}
    
    def build_network(self, cities: List[Tuple[str, float, float]], 
                     relief_centers: List[Tuple[str, float, float]]):
        all_points = cities + relief_centers
        lats = [p[1] for p in all_points]
        lons = [p[2] for p in all_points]
        
        bbox = (min(lats) - 0.1, min(lons) - 0.1, 
                max(lats) + 0.1, max(lons) + 0.1)
        
        osm_data = self.get_osm_data(bbox)
        
        if not osm_data.get("elements"):
            self._build_direct_network(cities, relief_centers)
            return
        
        self._process_osm_data(osm_data, cities, relief_centers)
    
    def _build_direct_network(self, cities, relief_centers):
        node_id = 1
        
        for city_name, lat, lon in cities:
            self.nodes[node_id] = (lat, lon)
            self.city_nodes[city_name] = node_id
            node_id += 1
        
        for relief_name, lat, lon in relief_centers:
            self.nodes[node_id] = (lat, lon)
            self.relief_nodes[relief_name] = node_id
            node_id += 1
        
        for city_name, city_lat, city_lon in cities:
            city_node = self.city_nodes[city_name]
            self.edges[city_node] = []
            
            for relief_name, relief_lat, relief_lon in relief_centers:
                relief_node = self.relief_nodes[relief_name]
                distance = self.haversine_distance(city_lat, city_lon, relief_lat, relief_lon)
                
                if distance <= 200:
                    self.edges[city_node].append((relief_node, distance))
                    if relief_node not in self.edges:
                        self.edges[relief_node] = []
                    self.edges[relief_node].append((city_node, distance))
    
    def _process_osm_data(self, osm_data, cities, relief_centers):
        nodes_dict = {}
        for element in osm_data.get("elements", []):
            if element["type"] == "node":
                node_id = element["id"]
                self.nodes[node_id] = (element["lat"], element["lon"])
                nodes_dict[node_id] = (element["lat"], element["lon"])
        
        for element in osm_data.get("elements", []):
            if element["type"] == "way" and "highway" in element.get("tags", {}):
                way_nodes = element["nodes"]
                
                for i in range(len(way_nodes) - 1):
                    node1, node2 = way_nodes[i], way_nodes[i + 1]
                    
                    if node1 in nodes_dict and node2 in nodes_dict:
                        lat1, lon1 = nodes_dict[node1]
                        lat2, lon2 = nodes_dict[node2]
                        distance = self.haversine_distance(lat1, lon1, lat2, lon2)
                        
                        if node1 not in self.edges:
                            self.edges[node1] = []
                        if node2 not in self.edges:
                            self.edges[node2] = []
                        
                        self.edges[node1].append((node2, distance))
                        self.edges[node2].append((node1, distance))
        
        self._find_nearest_nodes(cities, relief_centers)
    
    def _find_nearest_nodes(self, cities, relief_centers):
        for city_name, lat, lon in cities:
            nearest = self._find_nearest_node(lat, lon)
            if nearest:
                self.city_nodes[city_name] = nearest
        
        for relief_name, lat, lon in relief_centers:
            nearest = self._find_nearest_node(lat, lon)
            if nearest:
                self.relief_nodes[relief_name] = nearest
    
    def _find_nearest_node(self, target_lat, target_lon):
        min_distance = float('inf')
        nearest = None
        
        for node_id, (lat, lon) in self.nodes.items():
            distance = self.haversine_distance(target_lat, target_lon, lat, lon)
            if distance < min_distance:
                min_distance = distance
                nearest = node_id
        
        return nearest if min_distance < 10.0 else None

class DijkstraPathfinder:
    def __init__(self, network: OSMRoadNetwork):
        self.network = network
    
    def dijkstra(self, start: int, targets: Set[int]) -> Tuple[Optional[int], float, List[int]]:
        pq = [(0, start, [start])]
        visited = set()
        distances = {start: 0}
        
        while pq:
            current_dist, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node in targets:
                return current_node, current_dist, path
            
            for neighbor, weight in self.network.edges.get(current_node, []):
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    
                    if neighbor not in distances or new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor, path + [neighbor]))
        
        return None, float('inf'), []
    
    def find_nearest_relief(self, city_name: str) -> Tuple[Optional[str], float, List[Tuple[float, float]]]:
        if city_name not in self.network.city_nodes:
            return self._direct_search(city_name)
        
        start_node = self.network.city_nodes[city_name]
        target_nodes = set(self.network.relief_nodes.values())
        
        if not target_nodes:
            return self._direct_search(city_name)
        
        target_node, distance, path_nodes = self.dijkstra(start_node, target_nodes)
        
        if target_node is None:
            return self._direct_search(city_name)
        
        relief_name = None
        for name, node in self.network.relief_nodes.items():
            if node == target_node:
                relief_name = name
                break
        
        path_coords = []
        for node in path_nodes:
            if node in self.network.nodes:
                path_coords.append(self.network.nodes[node])
        
        return relief_name, distance, path_coords
    
    def _direct_search(self, city_name: str) -> Tuple[Optional[str], float, List[Tuple[float, float]]]:
        city_coords = self._get_city_coords(city_name)
        if not city_coords:
            return None, float('inf'), []
        
        min_distance = float('inf')
        nearest_relief = None
        nearest_coords = None
        
        for district, centers in RELIEF_CENTRES.items():
            for relief_name, coords in centers.items():
                distance = self.network.haversine_distance(
                    city_coords[0], city_coords[1], coords[0], coords[1]
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_relief = relief_name
                    nearest_coords = coords
        
        if nearest_relief:
            return nearest_relief, min_distance, [city_coords, nearest_coords]
        
        return None, float('inf'), []
    
    def _get_city_coords(self, city_name: str) -> Optional[Tuple[float, float]]:
        for district, cities in DISTRICT_CITIES.items():
            for city_data in cities:
                if city_data[0] == city_name:
                    return (city_data[1], city_data[2])
        return None

def create_map(city_name: str, city_coords: Tuple[float, float],
               relief_center: str, relief_coords: Tuple[float, float],
               path_coords: List[Tuple[float, float]], distance: float) -> folium.Map:
    
    if not path_coords:
        path_coords = [city_coords, relief_coords]
    
    center_lat = sum(coord[0] for coord in path_coords) / len(path_coords)
    center_lon = sum(coord[1] for coord in path_coords) / len(path_coords)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    folium.Marker(
        city_coords,
        popup=f"<b>{city_name}</b><br>Starting Point",
        icon=folium.Icon(color='blue', icon='home')
    ).add_to(m)
    
    folium.Marker(
        relief_coords,
        popup=f"<b>{relief_center}</b><br>Distance: {distance:.2f} km",
        icon=folium.Icon(color='red', icon='plus')
    ).add_to(m)
    
    if len(path_coords) > 1:
        folium.PolyLine(
            path_coords,
            weight=5,
            color='green',
            opacity=0.8
        ).add_to(m)
    
    return m

def find_path_for_city(city_name: str) -> Dict:
    try:
        all_cities = []
        for district, cities in DISTRICT_CITIES.items():
            all_cities.extend(cities)
        
        all_relief_centers = []
        for district, centers in RELIEF_CENTRES.items():
            for center_name, coords in centers.items():
                all_relief_centers.append((center_name, coords[0], coords[1]))
        
        network = OSMRoadNetwork()
        network.build_network(all_cities, all_relief_centers)
        
        pathfinder = DijkstraPathfinder(network)
        relief_center, distance, path_coords = pathfinder.find_nearest_relief(city_name)
        
        if relief_center:
            city_coords = pathfinder._get_city_coords(city_name)
            relief_coords = None
            
            for district, centers in RELIEF_CENTRES.items():
                if relief_center in centers:
                    relief_coords = centers[relief_center]
                    break
            
            if city_coords and relief_coords:
                map_obj = create_map(city_name, city_coords, relief_center, 
                                   relief_coords, path_coords, distance)
                
                filename = f"{city_name.lower()}_route.html"
                map_obj.save(filename)
                
                # Open the HTML file automatically
                webbrowser.open('file://' + os.path.realpath(filename))
                
                return {
                    'success': True,
                    'city': city_name,
                    'relief_center': relief_center,
                    'distance_km': distance,
                    'map_file': filename
                }
        
        return {'success': False, 'city': city_name, 'error': 'No relief center found'}
    
    except Exception as e:
        return {'success': False, 'city': city_name, 'error': str(e)}

def main():
    city_name = input("Enter city name: ").strip()
    if not city_name:
        city_name = "Roorkee"
    
    print(f"Finding route from {city_name}...")
    result = find_path_for_city(city_name)
    
    if result['success']:
        print(f"✅ Nearest relief center: {result['relief_center']}")
        print(f"📏 Distance: {result['distance_km']:.2f} km")
        print(f"🗺️ Map opened in browser: {result['map_file']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    main()