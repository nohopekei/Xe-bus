"""BFS - duyet do thi theo chieu rong."""
from collections import deque

def bfs(graph, start):
    """Tra ve thu tu cac dinh co the tiep can tu start."""
    if start not in graph:
        return []
    queue = deque([start])
    visited = {start}
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor, _weight in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
