from pyvis.network import Network
import networkx as nx

G = nx.karate_club_graph()
net = Network(notebook=False, height="100%", width="100%")
net.from_nx(G)
net.show("graph.html")
