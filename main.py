"""
SMART BUS NETWORK - mo hinh hoc tap khu vuc Ha Noi.

Du lieu ket noi va travel_time trong bo mau la SO LIEU MO PHONG,
khong phai lich trinh/thoi gian xe buyt thuc te da duoc xac minh.
"""
import csv
from pathlib import Path

from algorithms.bfs import bfs
from algorithms.connected_components import connected_components
from algorithms.dijkstra import dijkstra
from algorithms.kruskal import kruskal_mst

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"


def read_csv(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {file_path}")
    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def build_graph(data_folder):
    folder = Path(data_folder)
    stops = read_csv(folder / "stops.csv")
    routes = read_csv(folder / "routes.csv")
    connections = read_csv(folder / "connections.csv")

    if not stops or not {"stop_id", "stop_name"}.issubset(stops[0]):
        raise ValueError("stops.csv can co cot stop_id, stop_name va co du lieu.")
    required = {"from_stop", "to_stop", "route_id", "travel_time"}
    if not connections or not required.issubset(connections[0]):
        raise ValueError("connections.csv thieu cot hoac khong co du lieu.")

    stop_ids = [row["stop_id"].strip() for row in stops]
    if len(stop_ids) != len(set(stop_ids)):
        raise ValueError("stop_id bi trung lap.")
    valid_ids = set(stop_ids)
    directed = {stop_id: [] for stop_id in stop_ids}
    undirected = {stop_id: [] for stop_id in stop_ids}

    for line_no, row in enumerate(connections, start=2):
        source = row["from_stop"].strip()
        destination = row["to_stop"].strip()
        if source not in valid_ids or destination not in valid_ids:
            raise ValueError(f"Ma tram khong ton tai tai dong {line_no}: {source}->{destination}")
        try:
            weight = float(row["travel_time"])
        except (TypeError, ValueError):
            raise ValueError(f"travel_time khong hop le tai dong {line_no}.")
        if weight < 0:
            raise ValueError("travel_time phai khong am de dung Dijkstra.")
        directed[source].append((destination, weight))
        undirected[source].append((destination, weight))
        undirected[destination].append((source, weight))

    return stops, routes, directed, undirected


def name_map(stops):
    return {row["stop_id"]: row["stop_name"] for row in stops}


def display_info(stops, routes, graph, title):
    edge_count = sum(len(items) for items in graph.values())
    print("\n" + "=" * 58)
    print(title)
    print("=" * 58)
    print(f"So tram/dinh: {len(stops)}")
    print(f"So tuyen ghi trong routes.csv: {len(routes)}")
    print(f"So ket noi co huong: {edge_count}")
    print("Luu y: trong so trong bo du lieu mau la so lieu mo phong.")


def run_dijkstra(graph, names, start, goal):
    print("\n--- DIJKSTRA: DUONG DI CO TONG TRONG SO NHO NHAT ---")
    path, distance = dijkstra(graph, start, goal)
    if not path:
        print("Khong tim thay duong di.")
    else:
        print("Hanh trinh:", " -> ".join(names.get(v, v) for v in path))
        print(f"Tong thoi gian mo phong: {distance:g} phut")


def run_bfs(graph, names, start):
    print("\n--- BFS: CAC TRAM TIEP CAN THEO CHIEU DI ---")
    result = bfs(graph, start)
    for number, stop in enumerate(result, start=1):
        print(f"{number}. {names.get(stop, stop)} ({stop})")
    print("Tong so tram tiep can:", len(result))


def run_components(graph, names):
    print("\n--- CONNECTED COMPONENTS (DO THI VO HUONG) ---")
    groups = connected_components(graph)
    print("So thanh phan lien thong:", len(groups))
    for number, group in enumerate(groups, start=1):
        print(f"Nhom {number}:", ", ".join(names.get(v, v) for v in group))


def run_kruskal(graph, names):
    print("\n--- KRUSKAL: MINIMUM SPANNING TREE / FOREST ---")
    edges, total = kruskal_mst(graph)
    for source, destination, weight in edges:
        print(f"{names.get(source, source)} -- {names.get(destination, destination)}: {weight:g}")
    connected = len(graph) <= 1 or len(edges) == len(graph) - 1
    if connected:
        print(f"MST co {len(edges)} canh.")
    else:
        print(f"Do thi khong lien thong: ket qua la rung khung nho nhat ({len(edges)} canh).")
    print(f"Tong trong so: {total:g} (don vi mo phong)")


def test_dataset(title, folder_name):
    try:
        stops, routes, directed, undirected = build_graph(DATA_DIR / folder_name)
        names = name_map(stops)
        display_info(stops, routes, directed, title)
        ids = list(directed)
        if len(ids) < 2:
            raise ValueError("Can it nhat 2 tram.")
        start, goal = ids[0], ids[-1]
        print(f"Tram dau: {names[start]} ({start})")
        print(f"Tram dich: {names[goal]} ({goal})")
        run_dijkstra(directed, names, start, goal)
        run_bfs(directed, names, start)
        run_components(undirected, names)
        run_kruskal(undirected, names)
        print("\nKET THUC KIEM THU:", title)
        return True
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nKIEM THU THAT BAI - {title}")
        print("Ly do:", error)
        return False


def test_all_datasets():
    datasets = [
        ("Dataset 1 - Manual", "dataset_manual"),
        ("Dataset 2 - Main", "dataset_main"),
        ("Dataset 3 - Modified", "dataset_modified"),
    ]
    results = [test_dataset(title, folder) for title, folder in datasets]
    print("\n========== TONG KET ==========")
    print(f"Dataset chay thanh cong: {sum(results)}/{len(results)}")


def main():
    while True:
        print("\n" + "=" * 42)
        print("       SMART BUS NETWORK - HA NOI")
        print("=" * 42)
        print("1. Kiem thu Dataset 1 - Manual")
        print("2. Kiem thu Dataset 2 - Main")
        print("3. Kiem thu Dataset 3 - Modified")
        print("4. Kiem thu ca 3 Dataset")
        print("0. Thoat")
        choice = input("Lua chon cua ban: ").strip()

        if choice == "1":
            test_dataset("Dataset 1 - Manual", "dataset_manual")
        elif choice == "2":
            test_dataset("Dataset 2 - Main", "dataset_main")
        elif choice == "3":
            test_dataset("Dataset 3 - Modified", "dataset_modified")
        elif choice == "4":
            test_all_datasets()
        elif choice == "0":
            print("Da thoat chuong trinh.")
            break
        else:
            print("Lua chon khong hop le. Hay nhap tu 0 den 4.")


if __name__ == "__main__":
    main()
