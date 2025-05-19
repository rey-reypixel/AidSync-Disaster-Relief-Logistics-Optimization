#I am a Great Engineer.

#Nodes: Affected locations, Edges: Roads(with distance/cost and possible blockage)
#Edge weights: Time, road conditions, distance.
#Calamity Score   #Disaster Info  & b. Resource Needs-->stored per locations


class Location:
    def __init__(self, name, disaster_type, resource_need, urgency_score):
        self.name = name
        self.disaster_type = disaster_type
        self.resource_need = resource_need  # list of resource names
        self.urgency_score = urgency_score  # score to prioritise later  #ML MODEL PLS

    def __str__(self):
        return f"{self.name} ({self.disaster_type}) - Needs: {self.resource_need}, Urgency: {self.urgency_score}"
    


    class Graph:
        def __init__(self):
            self.adj_list = {}  # key = location name, value = list of (neighbor, weight)
            self.locations = {}  # key = location name, value = Location object

        def add_location(self, name, disaster_type, resource_need, urgency_score):
            location = Location(name, disaster_type, resource_need, urgency_score)
            self.locations[name] = location
            self.adj_list[name] = []

        def add_road(self, from_loc, to_loc, distance):
            self.adj_list[from_loc].append((to_loc, distance))
            self.adj_list[to_loc].append((from_loc, distance))  # Undirected by default

        def block_road(self, from_loc, to_loc):
            self.adj_list[from_loc] = [(nbr, dist) for nbr, dist in self.adj_list[from_loc] if nbr != to_loc]
            self.adj_list[to_loc] = [(nbr, dist) for nbr, dist in self.adj_list[to_loc] if nbr != from_loc]

        def show_graph(self):
            for loc in self.adj_list:
                print(f"{loc} --> {self.adj_list[loc]}")

        def show_locations(self):
            for loc in self.locations:
                print(self.locations[loc])


#testing where bitch
