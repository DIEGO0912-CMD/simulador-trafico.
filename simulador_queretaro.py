import streamlit as st
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random

st.set_page_config(layout="wide", page_title="Simulador de Tráfico - Querétaro")

st.title("🚦 Simulador de Tráfico Urbano con Feromonas - Querétaro 🇲🇽")

with st.expander("📋 Instrucciones"):
    st.markdown("""
    Esta aplicación simula el tráfico urbano en Querétaro usando un algoritmo inspirado en el comportamiento de las hormigas.
    - Las **zonas importantes** actúan como fuentes de tráfico.
    - Las **feromonas** se acumulan en caminos más utilizados.
    - Las **hormigas** (vehículos simulados) refuerzan rutas más eficientes.
    """)

place_name = "Querétaro, Mexico"
st.write(f"Descargando red vial de: {place_name}...")
G = ox.graph_from_place(place_name, network_type='drive')
G = ox.simplify_graph(G)
G = nx.convert_node_labels_to_integers(G)
pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
nodes = list(G.nodes())

# Parámetros de simulación
num_hormigas = st.slider("🐜 Número de hormigas", 100, 1000, 300, 50)
evaporacion = st.slider("💨 Tasa de evaporación de feromonas", 0.01, 0.2, 0.05)
iteraciones = st.slider("🔁 Iteraciones de simulación", 10, 200, 100, 10)

# Selección de zonas importantes (simuladas aleatoriamente)
zonas_importantes = random.sample(nodes, 10)
feromonas = {edge: 1.0 for edge in G.edges()}

def encontrar_camino(G, origen, destino, feromonas):
    actual = origen
    camino = []
    visitados = set()
    while actual != destino:
        vecinos = list(G.neighbors(actual))
        random.shuffle(vecinos)
        vecinos = [v for v in vecinos if (actual, v) in feromonas or (v, actual) in feromonas]
        if not vecinos:
            break
        pesos = []
        for vecino in vecinos:
            e = (actual, vecino) if (actual, vecino) in feromonas else (vecino, actual)
            pesos.append(feromonas[e])
        total = sum(pesos)
        probs = [p / total for p in pesos]
        siguiente = random.choices(vecinos, weights=probs)[0]
        camino.append((actual, siguiente))
        visitados.add(actual)
        actual = siguiente
        if actual in visitados:
            break
    return camino

# Simulación principal
with st.spinner("Simulando tránsito con feromonas..."):
    for _ in range(iteraciones):
        for _ in range(num_hormigas):
            origen = random.choice(nodes)
            destino = random.choice(zonas_importantes)
            if origen == destino:
                continue
            camino = encontrar_camino(G, origen, destino, feromonas)
            for e in camino:
                if e in feromonas:
                    feromonas[e] += 1
                elif (e[1], e[0]) in feromonas:
                    feromonas[(e[1], e[0])] += 1
        for e in feromonas:
            feromonas[e] *= (1 - evaporacion)

# Visualización de resultados
st.subheader("📍 Mapa con rutas optimizadas por feromonas")
fig, ax = plt.subplots(figsize=(12, 12))
edges = G.edges()
colores = [feromonas.get(edge, 0.1) for edge in edges]
nx.draw(G, pos, node_size=1, edge_color=colores, edge_cmap=plt.cm.inferno, width=2, ax=ax)
ax.set_title("Maqueta de tráfico en Querétaro optimizada con feromonas", fontsize=16)
st.pyplot(fig)