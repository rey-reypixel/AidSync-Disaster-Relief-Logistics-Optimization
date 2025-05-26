# demand_priority.py

# Class representing each affected area
class AffectedArea:
    def __init__(self, name, urgency, disaster_type):
        self.name = name
        self.urgency = urgency
        self.disaster_type = disaster_type
        self.demands = get_default_demands(disaster_type)

    def __repr__(self):
        return f"{self.name} ({self.disaster_type}) - Urgency: {self.urgency}"


# Disaster → Default demand logic
def get_default_demands(disaster_type):
    demand_map = {
        "Flood": ["Water", "Food", "Blankets"],
        "Earthquake": ["Medical", "Tents", "Rescue Gear"],
        "Cyclone": ["Water", "Power", "Roofing Sheets"],
        "Landslide": ["Rescue Gear", "Medical"],
    }
    return demand_map.get(disaster_type, ["General Aid"])


# Manual Max-Heap to prioritise areas by urgency
class UrgencyMaxHeap:
    def __init__(self):
        self.heap = []

    def insert(self, area):
        self.heap.append(area)
        self._heapify_up(len(self.heap) - 1)

    def extract_max(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        max_area = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return max_area

    def _heapify_up(self, index):
        while index > 0:
            parent_idx = (index - 1) // 2
            if self.heap[index].urgency > self.heap[parent_idx].urgency:
                self.heap[index], self.heap[parent_idx] = self.heap[parent_idx], self.heap[index]
                index = parent_idx
            else:
                break

    def _heapify_down(self, index):
        size = len(self.heap)
        while index < size:
            largest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self.heap[left].urgency > self.heap[largest].urgency:
                largest = left
            if right < size and self.heap[right].urgency > self.heap[largest].urgency:
                largest = right

            if largest != index:
                self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
                index = largest
            else:
                break

    def is_empty(self):
        return len(self.heap) == 0



# Example usage   #--->urgencty-->ML Model
if __name__ == "__main__":
    heap = UrgencyMaxHeap()
    
    # Add areas with urgency and disaster types
    heap.insert(AffectedArea("A", 5, "Flood"))
    heap.insert(AffectedArea("B", 10, "Earthquake"))
    heap.insert(AffectedArea("C", 6, "Landslide"))
    heap.insert(AffectedArea("D", 9, "Cyclone"))

    print(" Responding to areas by urgency:")
    while not heap.is_empty():
        area = heap.extract_max()
        print(f"→ {area.name} (Urgency: {area.urgency}) — Disaster: {area.disaster_type} — Needs: {area.demands}")