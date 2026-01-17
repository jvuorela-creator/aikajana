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

# Tarkistetaan, löytyykö tiedosto
if not os.path.exists(filename):
    st.error(f"Virhe: Tiedostoa '{filename}' ei löytynyt. Varmista, että se on ladattu samaan kansioon koodin kanssa.")
    st.stop()

try:
    # Luetaan Excel
    df = pd.read_excel(filename)
    
    # Tarkistetaan sarakkeet
    required_cols = ['Vuosi', 'Sarake_B', 'Sarake_C']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel-tiedostosta puuttuu sarakkeita. Varmista että otsikot ovat: {', '.join(required_cols)}")
        st.stop()

    # Siivotaan dataa:
    # 1. Poistetaan rivit, joista puuttuu vuosi
    df = df.dropna(subset=['Vuosi'])
    # 2. Muutetaan vuosi kokonaisluvuksi (ettei näy 1900.0)
    df['Vuosi'] = df['Vuosi'].astype(int)
    # 3. Korvataan tyhjät tekstikentät tyhjällä merkkijonolla
    df['Sarake_B'] = df['Sarake_B'].fillna("")
    df['Sarake_C'] = df['Sarake_C'].fillna("")
    
    # Järjestetään data varmuuden vuoksi vuoden mukaan vanhimmasta uusimpaan
    df = df.sort_values(by='Vuosi').reset_index(drop=True)

except Exception as e:
    st.error(f"Virhe luettaessa Excel-tiedostoa: {e}")
    st.stop()

# --- DATAN KÄSITTELY ANIMAATIOTA VARTEN ---

# Määritellään etäisyys tapahtumien välillä x-akselilla
STEP = 10 
df['x_pos'] = df.index * STEP 

# --- KUVAAJAN ALUSTUS ---
fig, ax = plt.subplots(figsize=(12, 6))

# Piilotetaan turhat elementit
ax.yaxis.set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# Piirretään aikajana
max_x = df['x_pos'].max()
ax.plot([-5, max_x + 5], [0, 0], color="black", linewidth=2, zorder=1)

# --- STAATTISET TEKSTIT JA OBJEKTIT ---
# Piirretään kaikki valmiiksi paikoilleen, animaatio vain liikuttaa kameraa.
text_width = 30

for i, row in df.iterrows():
    x = row['x_pos']
    
    # Pallo aikajanalle
    ax.scatter(x, 0, s=100, color='firebrick', zorder=2)
    
    # Vuosiluku
    ax.text(x, -0.8, str(row['Vuosi']), ha='center', va='top', fontsize=12, fontweight='bold')
    
    # Pystyviivat
    ax.plot([x, x], [0, 3], color='gray', linestyle='--', alpha=0.5, linewidth=1) # Ylös
    ax.plot([x, x], [0, -3], color='gray', linestyle='--', alpha=0.5, linewidth=1) # Alas

    # Yläteksti (Sarake C)
    if row['Sarake_C']: # Piirretään vain jos tekstiä on
        wrapped_c = "\n".join(textwrap.wrap(str(row['Sarake_C']), text_width))
        ax.text(x, 3.2, wrapped_c, ha='center', va='bottom', fontsize=10, color='darkblue', 
                bbox=dict(boxstyle="round,pad=0.3", fc="aliceblue", ec="blue", alpha=0.8))

    # Alateksti (Sarake B)
    if row['Sarake_B']: # Piirretään vain jos tekstiä on
        wrapped_b = "\n".join(textwrap.wrap(str(row['Sarake_B']), text_width))
        ax.text(x, -3.2, wrapped_b, ha='center', va='top', fontsize=10, color='darkgreen',
                 bbox=dict(boxstyle="round,pad=0.3", fc="honeydew", ec="green", alpha=0.8))

# Asetetaan Y-rajat
ax.set_ylim(-8, 8)

# --- KAMERAN LIIKE (ANIMAATION LOGIIKKA) ---
camera_positions = []

pause_frames = 20   # Pysähdys lukemista varten
slide_frames = 40   # Siirtymän kesto

for i in range(len(df)):
    current_x = df.iloc[i]['x_pos']
    
    # 1. Pysähdys
    camera_positions.extend([current_x] * pause_frames)
    
    # 2. Liuku seuraavaan
    if i < len(df) - 1:
        next_x = df.iloc[i+1]['x_pos']
        transition = np.linspace(current_x, next_x, slide_frames)
        camera_positions.extend(transition)

def update(frame_x):
    # Liikutetaan "kameraa" eli x-akselin rajausta
    window_width = 12
    ax.set_xlim(frame_x - (window_width/2), frame_x + (window_width/2))
    return ax,

# --- ANIMAATION RENDEROINTI ---
st.write(f"Ladattu {len(df)} tapahtumaa tiedostosta '{filename}'. Generoidaan animaatiota...")

# Luodaan animaatio
ani = animation.FuncAnimation(fig, update, frames=camera_positions, interval=50, blit=False)

# Näytetään HTML-muodossa
st.components.v1.html(ani.to_jshtml(), height=600)

st.success("Valmis!")
