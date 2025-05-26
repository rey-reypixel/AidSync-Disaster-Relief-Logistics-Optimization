class graph:
    def __init__(self):
        self.adj_list = {}
        self.locations = {}  

    def add_location(self, name, disaster_type, resources, urgency_score):
        self.adj_list[name] = []
        self.locations[name] = {
            "disaster_type": disaster_type,
            "resources": resources,
            "urgency_score": urgency_score
        }

    def add_road(self, from_loc, to_loc, distance):
     
        self.adj_list[from_loc].append((to_loc, distance))
        self.adj_list[to_loc].append((from_loc, distance))



def dijkstra_with_path(graph, start_node):
    distances = {node: float('inf') for node in graph.adj_list}
    previous = {node: None for node in graph.adj_list}
    distances[start_node] = 0

    visited = set()
    queue = list(graph.adj_list.keys())

    while queue:
        # Extract the node with minimum distance
        min_node = None
        min_dist = float('inf')
        for node in queue:
            if distances[node] < min_dist:
                min_dist = distances[node]
                min_node = node
        queue.remove(min_node)

        visited.add(min_node)

        for neighbor, weight in graph.adj_list[min_node]:
            if neighbor in visited:
                continue
            new_dist = distances[min_node] + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = min_node

    return distances, previous


def reconstruct_path(previous, target):
    path = []
    while target is not None:
        path.append(target)
        target = previous[target]
    return path[::-1]  #trace


if __name__ == "__main__":
    g = graph()
    g.add_location("A", "Flood", ["Water", "Food"], urgency_score=8)
    g.add_location("B", "Earthquake", ["Medical", "Tents"], urgency_score=9)
    g.add_location("C", "Landslide", ["Rescue Gear"], urgency_score=6)
    g.add_road("A", "B", 10)
    g.add_road("B", "C", 15)
    g.add_road("A", "C", 25)
    
    distances, previous = dijkstra_with_path(g, "A")

    print("\n== Shortest paths from A ==")
    for loc in distances:
        path = reconstruct_path(previous, loc)
        print(f"A → {loc} = {distances[loc]} via {path}")
