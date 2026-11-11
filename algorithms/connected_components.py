"""Tim cac thanh phan lien thong cua do thi vo huong."""
from collections import deque

def connected_components(graph):
    visited = set()
    components = []
    for start in graph:
        if start in visited:
            continue
        component = []
        queue = deque([start])
        visited.add(start)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor, _weight in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return components
