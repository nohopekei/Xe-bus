"""
SMART BUS NETWORK - Web App
Giao dien Streamlit + ban do Folium.
Du lieu ket noi/thoi gian trong bo mau la SO LIEU MO PHONG.
"""
import csv
from pathlib import Path

import streamlit as st
import folium
from streamlit_folium import st_folium

from algorithms.bfs import bfs
from algorithms.connected_components import connected_components
from algorithms.dijkstra import dijkstra
from algorithms.kruskal import kruskal_mst

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"

st.set_page_config(
    page_title="Smart Bus Network | Hanoi",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS nho de giao dien gon va hien dai hon
st.markdown("""
<style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.4rem 1.6rem; border-radius: 18px;
        background: linear-gradient(120deg, #102a43, #176b87);
        color: white; margin-bottom: 1rem;
    }
    .hero h1 {color: white; margin: 0;}
    .hero p {color: #d9edf5; margin: .4rem 0 0 0;}
    div[data-testid="stMetric"] {
        background: #f4f7fb; border: 1px solid #e4eaf1;
        padding: 12px 14px; border-radius: 14px;
    }
    .note {font-size: .88rem; color: #667085;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_dataset(dataset_folder):
    """Doc CSV va tao do thi co huong/vo huong."""
    folder = DATA_DIR / dataset_folder

    def read_csv(file_name):
        file_path = folder / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Khong tim thay {file_path}")
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    stops = read_csv("stops.csv")
    routes = read_csv("routes.csv")
    connections = read_csv("connections.csv")

    if not stops:
        raise ValueError("stops.csv khong co du lieu.")

    stop_ids = [row["stop_id"].strip() for row in stops]
    if len(stop_ids) != len(set(stop_ids)):
        raise ValueError("stop_id bi trung lap.")

    valid_ids = set(stop_ids)
    directed = {stop_id: [] for stop_id in stop_ids}
    undirected = {stop_id: [] for stop_id in stop_ids}

    for row in connections:
        source = row["from_stop"].strip()
        destination = row["to_stop"].strip()
        if source not in valid_ids or destination not in valid_ids:
            raise ValueError(f"Ket noi tham chieu tram khong ton tai: {source} -> {destination}")
        weight = float(row["travel_time"])
        if weight < 0:
            raise ValueError("Dijkstra yeu cau trong so khong am.")
        directed[source].append((destination, weight))
        undirected[source].append((destination, weight))
        undirected[destination].append((source, weight))

    names = {row["stop_id"]: row["stop_name"] for row in stops}
    return stops, routes, connections, directed, undirected, names


def make_map(stops, names, path=None):
    """Ve cac tram va to mau hanh trinh Dijkstra tren ban do."""
    valid_coords = []
    for stop in stops:
        try:
            lat = float(stop["latitude"])
            lon = float(stop["longitude"])
            valid_coords.append((stop["stop_id"], lat, lon))
        except (KeyError, TypeError, ValueError):
            continue

    if valid_coords:
        center = [
            sum(item[1] for item in valid_coords) / len(valid_coords),
            sum(item[2] for item in valid_coords) / len(valid_coords),
        ]
    else:
        center = [21.028, 105.80]

    route_ids = set(path or [])
    bus_map = folium.Map(location=center, zoom_start=13, control_scale=True)

    for stop_id, lat, lon in valid_coords:
        if path and stop_id == path[0]:
            color, label = "green", "Diem xuat phat"
        elif path and stop_id == path[-1]:
            color, label = "red", "Diem den"
        elif stop_id in route_ids:
            color, label = "orange", "Tram tren hanh trinh"
        else:
            color, label = "blue", "Tram"
        folium.CircleMarker(
            location=[lat, lon],
            radius=8 if stop_id in route_ids else 5,
            color=color,
            fill=True,
            fill_opacity=0.85,
            tooltip=f"{names.get(stop_id, stop_id)} ({stop_id})",
            popup=f"<b>{names.get(stop_id, stop_id)}</b><br>{label}",
        ).add_to(bus_map)

    if path:
        coord_by_id = {sid: (lat, lon) for sid, lat, lon in valid_coords}
        path_coords = [coord_by_id[sid] for sid in path if sid in coord_by_id]
        if len(path_coords) >= 2:
            folium.PolyLine(
                path_coords, color="#e63946", weight=6, opacity=0.9,
                tooltip="Duong di Dijkstra"
            ).add_to(bus_map)

    return bus_map


# Sidebar
st.sidebar.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=48)
st.sidebar.title("Smart Bus Network")
st.sidebar.caption("Mo phong mang luoi xe buyt Ha Noi")
dataset_options = {
    "Dataset Main (15 tram)": "dataset_main",
    "Dataset Manual (6 tram)": "dataset_manual",
    "Dataset Modified (15 tram)": "dataset_modified",
}
selected_dataset_label = st.sidebar.selectbox("Chon bo du lieu", list(dataset_options))
dataset_folder = dataset_options[selected_dataset_label]

try:
    stops, routes, connections, directed_graph, undirected_graph, names = load_dataset(dataset_folder)
except Exception as error:
    st.error(f"Khong the doc du lieu: {error}")
    st.stop()

st.markdown("""
<div class="hero">
  <h1>🚌 SMART BUS NETWORK</h1>
  <p>He thong mo phong tim duong va phan tich mang luoi xe buyt Ha Noi</p>
</div>
""", unsafe_allow_html=True)

st.caption("Luu y: toa do, ket noi va thoi gian trong bo du lieu mau la du lieu mo phong, chua duoc xac minh nhu du lieu van hanh xe buyt thuc te.")

# KPI
m1, m2, m3, m4 = st.columns(4)
m1.metric("So tram", len(stops))
m2.metric("So tuyen trong CSV", len(routes))
m3.metric("So ket noi co huong", len(connections))
m4.metric("Dataset dang chon", selected_dataset_label.split(" ")[1])

tab_route, tab_network, tab_data = st.tabs(["🧭 Tìm đường", "📊 Phân tích mạng lưới", "📋 Dữ liệu trạm"])

with tab_route:
    st.subheader("Tìm hành trình giữa hai trạm")
    stop_ids = [row["stop_id"] for row in stops]
    col_start, col_end = st.columns(2)
    with col_start:
        start_id = st.selectbox(
            "Điểm xuất phát",
            stop_ids,
            format_func=lambda sid: f"{names[sid]} ({sid})",
            key="start_stop",
        )
    with col_end:
        end_id = st.selectbox(
            "Điểm đến",
            stop_ids,
            index=len(stop_ids) - 1,
            format_func=lambda sid: f"{names[sid]} ({sid})",
            key="end_stop",
        )

    if st.button("🔎 Tìm đường đi ngắn nhất", type="primary", use_container_width=True):
        if start_id == end_id:
            st.warning("Điểm xuất phát và điểm đến đang giống nhau. Hãy chọn hai trạm khác nhau.")
            st.session_state["route_result"] = None
        else:
            path, distance = dijkstra(directed_graph, start_id, end_id)
            st.session_state["route_result"] = (start_id, end_id, path, distance)

    result = st.session_state.get("route_result")
    if result:
        saved_start, saved_end, path, distance = result
        if saved_start != start_id or saved_end != end_id:
            st.info("Mày đã đổi điểm chọn. Nhấn nút tìm đường để cập nhật kết quả.")
        elif not path:
            st.error("Không tìm thấy đường đi theo các kết nối có hướng trong Dataset này.")
        else:
            r1, r2, r3 = st.columns(3)
            r1.metric("Số trạm trên hành trình", len(path))
            r2.metric("Số chặng", max(0, len(path) - 1))
            r3.metric("Tổng trọng số mô phỏng", f"{distance:g} phút")

            st.success("Đã tìm thấy hành trình có tổng trọng số nhỏ nhất theo dữ liệu hiện tại.")
            st.markdown("**Các trạm đi qua**")
            for index, stop_id in enumerate(path, start=1):
                st.write(f"{index}. {names[stop_id]} ({stop_id})")

            st.markdown("**Bản đồ các trạm và hành trình**")
            st_folium(make_map(stops, names, path), width=None, height=520, key="route_map")
    else:
        st.info("Chọn điểm xuất phát, điểm đến rồi nhấn “Tìm đường đi ngắn nhất”.")

with tab_network:
    st.subheader("Phân tích mạng lưới bằng 4 thuật toán")
    default_start = stop_ids[0]
    bfs_start = st.selectbox(
        "Chọn trạm bắt đầu cho BFS",
        stop_ids,
        format_func=lambda sid: f"{names[sid]} ({sid})",
        key="bfs_start",
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Chạy BFS", use_container_width=True):
            visited = bfs(directed_graph, bfs_start)
            st.write(f"**BFS tìm được {len(visited)} trạm có thể tiếp cận:**")
            st.write(" → ".join(names[sid] for sid in visited))
    with c2:
        if st.button("Chạy Connected Components", use_container_width=True):
            groups = connected_components(undirected_graph)
            st.write(f"**Số thành phần liên thông: {len(groups)}**")
            for i, group in enumerate(groups, start=1):
                st.write(f"Nhóm {i}: " + ", ".join(names[sid] for sid in group))

    if st.button("Chạy Kruskal (MST)", use_container_width=True):
        mst_edges, total = kruskal_mst(undirected_graph)
        st.write(f"**Số cạnh được chọn: {len(mst_edges)}**")
        st.write(f"**Tổng trọng số: {total:g} (đơn vị mô phỏng)**")
        st.dataframe(
            [
                {"Trạm 1": names[a], "Trạm 2": names[b], "Trọng số": weight}
                for a, b, weight in mst_edges
            ],
            use_container_width=True,
        )

with tab_data:
    st.subheader("Danh sách trạm trong Dataset")
    st.dataframe(
        [
            {
                "Mã trạm": row["stop_id"],
                "Tên trạm": row["stop_name"],
                "Vĩ độ": row.get("latitude", ""),
                "Kinh độ": row.get("longitude", ""),
            }
            for row in stops
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Danh sách tuyến trong CSV")
    st.dataframe(routes, use_container_width=True, hide_index=True)

st.divider()
st.caption("Smart Bus Network | Đồ án học tập – Python, Graph Algorithms, Streamlit và Folium")
