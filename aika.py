import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
    
    # Tarkistetaan sarakkeet
    required_cols = ['Vuosi', 'Sarake_B', 'Sarake_C']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel-tiedostosta puuttuu sarakkeita: {', '.join(required_cols)}")
        st.stop()

    df = df.dropna(subset=['Vuosi'])
    df['Vuosi'] = df['Vuosi'].astype(int)
    df['Sarake_B'] = df['Sarake_B'].fillna("")
    df['Sarake_C'] = df['Sarake_C'].fillna("")
    df = df.sort_values(by='Vuosi').reset_index(drop=True)

    # VAROITUS SUURESTA DATAMÄÄRÄSTÄ
    if len(df) > 30:
        st.warning(f"Huomio: Tiedostossa on {len(df)} tapahtumaa. Animaation luonti voi kestää yli minuutin.")

except Exception as e:
    st.error(f"Virhe: {e}")
    st.stop()

# --- DATAN KÄSITTELY ---
STEP = 10 
df['x_pos'] = df.index * STEP 

# --- KUVAAJA ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.yaxis.set_visible(False)
ax.axis('off') # Poistetaan kaikki reunat

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

# --- OPTIMOITU ANIMAATION LOGIIKKA ---
camera_positions = []

# NÄMÄ ARVOT VAIKUTTAVAT NOPEUTEEN JA RASKAUTEEN
pause_frames = 10   # Pidetään kuva paikallaan (vähennetty 20 -> 10)
slide_frames = 5    # Siirtymän pituus ruutuina (vähennetty 40 -> 5)

for i in range(len(df)):
    current_x = df.iloc[i]['x_pos']
    camera_positions.extend([current_x] * pause_frames)
    
    if i < len(df) - 1:
        next_x = df.iloc[i+1]['x_pos']
        # Luodaan vähemmän väliaskelia -> kevyempi tiedosto
        transition = np.linspace(current_x, next_x, slide_frames)
        camera_positions.extend(transition)

def update(frame_x):
    window_width = 14
    ax.set_xlim(frame_x - (window_width/2), frame_x + (window_width/2))
    return ax,

# --- RENDEROINTI ---
total_frames = len(camera_positions)
st.info(f"Luodaan animaatiota ({total_frames} ruutua). Tämä vie hetken, odota rauhassa...")

# Progress bar visuaalisuuden vuoksi (ei päivity animaation sisällä, mutta näyttää että prosessi on käynnissä)
bar = st.progress(10)

# interval = 200ms (hidas) kompensoi pientä ruutumäärää. Liike on hieman "töksähtävämpi" mutta latautuu.
ani = animation.FuncAnimation(fig, update, frames=camera_positions, interval=200, blit=False)

try:
    # Generoidaan HTML
    jshtml = ani.to_jshtml()
    bar.progress(100)
    st.components.v1.html(jshtml, height=600)
    st.success("Animaatio valmis!")
except Exception as e:
    st.error(f"Animaation luonti epäonnistui (muisti loppui?). Vähennä Excelin rivimäärää. Virhe: {e}")
