import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import pandas as pd
import textwrap
import numpy as np
import os

# --- SIVUN ASETUKSET ---
st.set_page_config(page_title="Aikajana", layout="wide")
st.title("Sukututkimuksen aikajana")

# --- DATAN LATAUS ---
filename = 'Aikajana17012026.xlsx'

if not os.path.exists(filename):
    st.error(f"Virhe: Tiedostoa '{filename}' ei löytynyt.")
    st.stop()

try:
    df = pd.read_excel(filename)
    required_cols = ['Vuosi', 'Sarake_B', 'Sarake_C']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Sarakkeet puuttuvat: {', '.join(required_cols)}")
        st.stop()

    df = df.dropna(subset=['Vuosi'])
    df['Vuosi'] = df['Vuosi'].astype(int)
    df['Sarake_B'] = df['Sarake_B'].fillna("")
    df['Sarake_C'] = df['Sarake_C'].fillna("")
    df = df.sort_values(by='Vuosi').reset_index(drop=True)

except Exception as e:
    st.error(f"Virhe: {e}")
    st.stop()

# --- DATAN KÄSITTELY ---
STEP = 10 
df['x_pos'] = df.index * STEP 

# --- KUVAAJA ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

# Aikajana
max_x = df['x_pos'].max()
ax.plot([-5, max_x + 5], [0, 0], color="black", linewidth=2, zorder=1)

# --- PIIRRETÄÄN TEKSTIT ---
text_width = 30
for i, row in df.iterrows():
    x = row['x_pos']
    ax.scatter(x, 0, s=100, color='firebrick', zorder=2)
    ax.text(x, -0.8, str(row['Vuosi']), ha='center', va='top', fontsize=12, fontweight='bold')
    ax.plot([x, x], [0, 3], color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.plot([x, x], [0, -3], color='gray', linestyle='--', alpha=0.5, linewidth=1)

    if row['Sarake_C']:
        wrapped_c = "\n".join(textwrap.wrap(str(row['Sarake_C']), text_width))
        ax.text(x, 3.2, wrapped_c, ha='center', va='bottom', fontsize=10, color='darkblue', 
                bbox=dict(boxstyle="round,pad=0.3", fc="aliceblue", ec="blue", alpha=0.8))

    if row['Sarake_B']:
        wrapped_b = "\n".join(textwrap.wrap(str(row['Sarake_B']), text_width))
        ax.text(x, -3.2, wrapped_b, ha='center', va='top', fontsize=10, color='darkgreen',
                 bbox=dict(boxstyle="round,pad=0.3", fc="honeydew", ec="green", alpha=0.8))

ax.set_ylim(-8, 8)

# --- ANIMATION FRAMES ---
camera_positions = []
pause_frames = 16   # Kuinka kauan pysytään paikallaan
slide_frames = 12   # Kuinka nopeasti liu'utaan

for i in range(len(df)):
    current_x = df.iloc[i]['x_pos']
    camera_positions.extend([current_x] * pause_frames)
    if i < len(df) - 1:
        next_x = df.iloc[i+1]['x_pos']
        transition = np.linspace(current_x, next_x, slide_frames)
        camera_positions.extend(transition)

def update(frame_x):
    window_width = 14
    ax.set_xlim(frame_x - (window_width/2), frame_x + (window_width/2))
    return ax,

# --- GIF TALLENNUS JA NÄYTTÖ ---
st.info(f"Generoidaan GIF-animaatiota ({len(camera_positions)} ruutua). Tämä vie hetken...")
progress_bar = st.progress(0)

ani = animation.FuncAnimation(fig, update, frames=camera_positions, blit=False)

# Tallennetaan GIF levylle
gif_filename = "aikajana_animaatio.gif"
try:
    # FPS määrittää nopeuden. 10 fps on hyvä kompromissi.
    writer = PillowWriter(fps=10) 
    ani.save(gif_filename, writer=writer)
    
    progress_bar.progress(100)
    st.success("Valmis!")
    
    # Näytetään GIF
    st.image(gif_filename, use_container_width=True)
    
    # Mahdollisuus ladata tiedosto
    with open(gif_filename, "rb") as file:
        st.download_button(
            label="Lataa GIF-tiedosto",
            data=file,
            file_name=gif_filename,
            mime="image/gif"
        )

except Exception as e:
    st.error(f"Virhe GIFin luonnissa: {e}")
