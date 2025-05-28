import streamlit as st
import numpy as np
import time
import random

st.title("🌿 Ecosistema Animado: Hormigas, Hongos, Parásitos y Depredadores")

# Parámetros del ecosistema
tam = st.slider("Tamaño del ecosistema (NxN)", 10, 50, 20)
num_hormigas = st.slider("Número de hormigas", 1, 200, 30)
num_hojas = st.slider("Número de hojas", 1, 100, 40)
num_hongos = st.slider("Cantidad inicial de alimento", 1, 50, 10)
num_parasitos = st.slider("Número inicial de parásitos", 0, 30, 5)
num_depredadores = st.slider("Número inicial de depredadores", 0, 10, 3)
pasos = st.slider("Pasos de la simulación", 1, 200, 100)
velocidad = st.slider("Velocidad de animación (s)", 0.01, 1.0, 0.2)

def posiciones_aleatorias(n):
    return [(random.randint(0, tam - 1), random.randint(0, tam - 1)) for _ in range(n)]

hormigas = posiciones_aleatorias(num_hormigas)
hojas = posiciones_aleatorias(num_hojas)
hongos = posiciones_aleatorias(num_hongos)
parasitos = posiciones_aleatorias(num_parasitos)
depredadores = posiciones_aleatorias(num_depredadores)

def renderizar_tablero():
    grid = [["⬛" for _ in range(tam)] for _ in range(tam)]
    for x, y in hojas:
        grid[x][y] = "🌿"
    for x, y in hongos:
        grid[x][y] = "🍄"
    for x, y in parasitos:
        grid[x][y] = "🧫"
    for x, y in depredadores:
        grid[x][y] = "🐍"
    for x, y in hormigas:
        grid[x][y] = "🟠"
    return "\n".join("".join(fila) for fila in grid)

output = st.empty()

for paso in range(pasos):
    # Mover hormigas
    nuevas_hormigas = []
    nuevas_hojas = hojas.copy()
    nuevas_hongos = hongos.copy()
    for x, y in hormigas:
        dx, dy = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])
        nx, ny = min(max(0, x + dx), tam - 1), min(max(0, y + dy), tam - 1)

        if (nx, ny) in nuevas_hojas:
            nuevas_hojas.remove((nx, ny))
            nuevas_hongos.append((nx, ny))

        if (nx, ny) not in parasitos and (nx, ny) not in depredadores:
            nuevas_hormigas.append((nx, ny))  # Solo sobrevive si no hay amenaza

    hormigas = nuevas_hormigas

    # Mover depredadores
    nuevas_depredadores = []
    for x, y in depredadores:
        dx, dy = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])
        nx, ny = min(max(0, x + dx), tam - 1), min(max(0, y + dy), tam - 1)
        nuevas_depredadores.append((nx, ny))
        # Eliminar hormiga si pisa una
        hormigas = [h for h in hormigas if h != (nx, ny)]
    depredadores = nuevas_depredadores

    # Movimiento y daño por parásitos (no se mueven en este modelo simple)
    hormigas = [h for h in hormigas if h not in parasitos]

    # Posibilidad de que aparezcan nuevos parásitos
    if random.random() < 0.05:  # 5% de probabilidad por paso
        parasitos.append((random.randint(0, tam - 1), random.randint(0, tam - 1)))

    hojas = nuevas_hojas
    hongos = nuevas_hongos

    output.text(renderizar_tablero())
    time.sleep(velocidad)

st.success("Simulación completada ✅")

