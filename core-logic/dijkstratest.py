if __name__ == "__main__":
    g = Graph()
    g.add_location("A", "Flood", ["Water", "Food"], urgency_score=8)
    g.add_location("B", "Earthquake", ["Medical", "Tents"], urgency_score=9)
    g.add_location("C", "Landslide", ["Rescue Gear"], urgency_score=6)
    g.add_road("A", "B", 10)
    g.add_road("B", "C", 15)
    g.add_road("A", "C", 25)
    # g.block_road("A", "C")

    distances, previous = dijkstra_with_path(g, "A")
    
    print("\n== Shortest paths from A ==")
    for loc in distances:
        path = reconstruct_path(previous, loc)
        print(f"A → {loc} = {distances[loc]} via {path}")
