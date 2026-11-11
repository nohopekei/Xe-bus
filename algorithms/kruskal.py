"""Kruskal MST bang Disjoint Set Union (DSU)."""

class DSU:
    def __init__(self, vertices):
        self.parent = {vertex: vertex for vertex in vertices}
        self.rank = {vertex: 0 for vertex in vertices}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, first, second):
        root_first = self.find(first)
        root_second = self.find(second)
        if root_first == root_second:
            return False
        if self.rank[root_first] < self.rank[root_second]:
            self.parent[root_first] = root_second
        elif self.rank[root_first] > self.rank[root_second]:
            self.parent[root_second] = root_first
        else:
            self.parent[root_second] = root_first
            self.rank[root_first] += 1
        return True


def kruskal_mst(graph):
    """Tra ve (danh_sach_canh, tong_trong_so); do thi roi rac tra ve forest."""
    unique_edges = {}
    for source, neighbors in graph.items():
        for destination, weight in neighbors:
            if source == destination:
                continue
            key = tuple(sorted((source, destination)))
            if key not in unique_edges or weight < unique_edges[key]:
                unique_edges[key] = weight

    edges = [(weight, a, b) for (a, b), weight in unique_edges.items()]
    edges.sort()
    dsu = DSU(graph.keys())
    mst_edges = []
    total_weight = 0.0

    for weight, source, destination in edges:
        if dsu.union(source, destination):
            mst_edges.append((source, destination, weight))
            total_weight += weight
            if len(mst_edges) == max(0, len(graph) - 1):
                break
    return mst_edges, total_weight
