"""Dijkstra: tim duong di co tong trong so nho nhat."""
import heapq

def dijkstra(graph, start, goal):
    if start not in graph or goal not in graph:
        return [], float("inf")
    distances = {vertex: float("inf") for vertex in graph}
    previous = {}
    distances[start] = 0.0
    priority_queue = [(0.0, start)]
    while priority_queue:
        current_distance, current = heapq.heappop(priority_queue)
        if current_distance > distances[current]:
            continue
        if current == goal:
            break
        for neighbor, weight in graph[current]:
            if weight < 0:
                raise ValueError("Dijkstra khong chap nhan trong so am.")
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                heapq.heappush(priority_queue, (new_distance, neighbor))
    if distances[goal] == float("inf"):
        return [], float("inf")
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = previous[current]
    path.append(start)
    path.reverse()
    return path, distances[goal]
