class Location:
    def __init__(self, name, disaster_type, resource_need, urgency_score):
        self.name = name
        self.disaster_type = disaster_type
        self.resource_need = resource_need  # list of resource names
        self.urgency_score = urgency_score  # score to prioritise later

    def __str__(self):
        return f"{self.name} ({self.disaster_type}) - Needs: {self.resource_need}, Urgency: {self.urgency_score}"


class Graph:
    def __init__(self):
        self.adj_list = {}  
        self.locations = {}  

    def add_location(self, name, disaster_type, resource_need, urgency_score):
        location = Location(name, disaster_type, resource_need, urgency_score)
        self.locations[name] = location
        self.adj_list[name] = []

    def add_road(self, from_loc, to_loc, distance):
        self.adj_list[from_loc].append((to_loc, distance))
        self.adj_list[to_loc].append((from_loc, distance)) 

    def block_road(self, from_loc, to_loc):
        self.adj_list[from_loc] = [(nbr, dist) for nbr, dist in self.adj_list[from_loc] if nbr != to_loc]
        self.adj_list[to_loc] = [(nbr, dist) for nbr, dist in self.adj_list[to_loc] if nbr != from_loc]

    def show_graph(self):
        for loc in self.adj_list:
            print(f"{loc} --> {self.adj_list[loc]}")

    def show_locations(self):
        for loc in self.locations:
            print(self.locations[loc])


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