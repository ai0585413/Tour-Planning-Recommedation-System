import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import font_manager
from geopy.distance import great_circle

# Path to the SolaimanLipi font
font_path = 'C:\\Users\\AYESHA CHOWDHURY\\Desktop\\SolaimanLipi_20-04-07.ttf'
font_prop = font_manager.FontProperties(fname=font_path)

# Create an undirected graph
G = nx.Graph()

# Define coordinates
coordinates = {
    "Humayun Rashid Chattar": (24.8776, 91.8755),
    "চৌরঙ্গী ঘাট, রাতারগুল।": (25.0125, 91.9351),
    "Ali Amjads Clock": (24.8884, 91.8678),
    "জাফলং Jaflong": (25.1834, 92.0117),
    "রাতারগুল চৌরঙ্গী ঘাট কায়াকিং এন্ড ক্যাম্পিং পয়েন্ট": (25.1048, 91.9686),
    "শ্যামল পাহাড়": (24.9287, 91.9517),
    "Panthumai waterfall": (25.178, 91.9556),
    "Tilagarh Eco Park": (24.9174, 91.9064),
    "Shahi Eidgah দক্ষিন চত্বর": (24.905, 91.8805)
}

# Add edges and calculate distances
# Correcting the edges list to match the node names in the coordinates dictionary
edges = [
    ("Humayun Rashid Chattar", "চৌরঙ্গী ঘাট, রাতারগুল।"),  # Fixed the name
    ("চৌরঙ্গী ঘাট, রাতারগুল।", "Ali Amjads Clock"),
    ("Ali Amjads Clock", "জাফলং Jaflong"),
    ("Humayun Rashid Chattar", "রাতারগুল চৌরঙ্গী ঘাট কায়াকিং এন্ড ক্যাম্পিং পয়েন্ট"),
    ("রাতারগুল চৌরঙ্গী ঘাট কায়াকিং এন্ড ক্যাম্পিং পয়েন্ট", "Ali Amjads Clock"),
    ("Humayun Rashid Chattar", "শ্যামল পাহাড়"),
    ("শ্যামল পাহাড়", "Ali Amjads Clock"),
    ("Humayun Rashid Chattar", "Panthumai waterfall"),
    ("Panthumai waterfall", "Tilagarh Eco Park"),
    ("Tilagarh Eco Park", "জাফলং Jaflong"),
    ("Panthumai waterfall", "Tilagarh Eco Park"),
    ("Tilagarh Eco Park", "জাফলং Jaflong"),
]


# Define average speed (km/h)
average_speed = 50  # Adjust this speed as necessary

# Add edges with distance and time as weights
for edge in edges:
    loc1, loc2 = edge
    coord1, coord2 = coordinates[loc1], coordinates[loc2]
    distance = great_circle(coord1, coord2).kilometers
    time_taken = distance / average_speed  # Time in hours
    G.add_edge(loc1, loc2, weight=distance, time=time_taken)

# Increase spacing between nodes
plt.figure(figsize=(22, 14))  # Increase width
pos = nx.spring_layout(G, seed=42, k=1.5, iterations=200)  # Increase k to space nodes further apart

# Draw nodes with a color map
node_colors = plt.cm.viridis([0.5 + 0.5 * i / len(G.nodes()) for i in range(len(G.nodes()))])
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2500, alpha=0.9)

# Draw edges with color map based on weights
edge_weights = nx.get_edge_attributes(G, 'weight')
edge_colors = plt.cm.plasma([weight / max(edge_weights.values()) for weight in edge_weights.values()])
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2.5, alpha=0.7)

# Draw labels with reduced font size to avoid overlap
for node, (x, y) in pos.items():
    plt.text(x, y, s=node, fontproperties=font_prop, fontsize=9, ha='center', va='center', color="#2F4F4F", weight='bold')

# Draw edge labels for distances
edge_labels = {(u, v): f'{d["weight"]:.2f} km' for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='black', label_pos=0.4)  # Adjusted label position

# Draw edge labels for time taken, slightly offset from the distance labels
edge_time_labels = {(u, v): f'{d["time"]:.2f} h' for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_time_labels, font_size=7, font_color='blue', label_pos=0.6)  # Adjusted label position

# Title with custom font
plt.title("Manual Graph with Distances and Time", fontsize=20, fontproperties=font_prop, color="#4B0082")

plt.axis("off")
plt.show()
