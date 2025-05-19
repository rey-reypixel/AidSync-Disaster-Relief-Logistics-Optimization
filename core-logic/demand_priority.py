class AffectedArea:
    def __init__(self, name, urgency, disaster_type, demands):
        self.name = name
        self.urgency = urgency  # Higher means more urgent
        self.disaster_type = disaster_type
        self.demands = demands

    def __repr__(self):
        return f"{self.name} ({self.disaster_type}) - Urgency: {self.urgency}"




#changes-->max heap(?)

def build_urgency_list():
    areas = [
        AffectedArea("A", 8, "Flood", ["Water", "Food"]),
        AffectedArea("B", 10, "Earthquake", ["Medical", "Tents"]),
        AffectedArea("C", 6, "Landslide", ["Rescue Gear"]),
        AffectedArea("D", 9, "Cyclone", ["Water", "Power"]),
    ]
    return areas
