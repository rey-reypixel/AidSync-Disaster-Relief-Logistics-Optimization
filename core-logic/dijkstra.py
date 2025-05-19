#I am a Great Engineer


#Priority Queue (manual min-heap substitute)
def extract_min(queue, distances):
    """Finds the node with the smallest tentative distance."""
    min_dist = float('inf')
    min_node = None
    for node in queue:
        if distances[node] < min_dist:
            min_dist = distances[node]
            min_node = node
    queue.remove(min_node)
    return min_node


def dijkstra_with_path(graph, start_node):
    distances = {node: float('inf') for node in graph.adj_list}
    previous = {node: None for node in graph.adj_list}
    distances[start_node] = 0

    visited = set()
    queue = list(graph.adj_list.keys())

    def extract_min(q, dist):
        min_node = None
        min_dist = float('inf')
        for node in q:
            if dist[node] < min_dist:
                min_dist = dist[node]
                min_node = node
        q.remove(min_node)
        return min_node

    while queue:
        current = extract_min(queue, distances)
        visited.add(current)

        for neighbor, weight in graph.adj_list[current]:
            if neighbor in visited:
                continue
            new_dist = distances[current] + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current  # ← Path tracking

    return distances, previous

def reconstruct_path(previous, target):
    path = []
    while target is not None:
        path.append(target)
        target = previous[target]
    return path[::-1]  # reverse the path
