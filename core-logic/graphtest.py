if __name__ == "__main__":
    g = Graph()

    # Add locations
    g.add_location("A", "Flood", ["Water", "Food"], urgency_score=8)
    g.add_location("B", "Earthquake", ["Medical", "Tents"], urgency_score=9)
    g.add_location("C", "Landslide", ["Rescue Gear"], urgency_score=6)

    # Add roads
    g.add_road("A", "B", 10)
    g.add_road("B", "C", 15)
    g.add_road("A", "C", 25)

    # Block one road
    g.block_road("A", "C")

    # Display structure
    print("== Locations ==")
    g.show_locations()

    print("\n== Road Network ==")
    g.show_graph()
