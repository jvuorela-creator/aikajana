import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import textwrap
import numpy as np

# Asetukset
st.set_page_config(page_title="Aikajana", layout="wide")
st.title("Sukututkimuksen aikajana")
st.write("Aikajana liukuu vasemmalta oikealle. Kamera pysähtyy hetkeksi jokaisen tapahtuman kohdalle.")

# 1. Data
data = {
    'Vuosi': [1850, 1865, 1892, 1905, 1917, 1939],
    'Sarake_B': [
        "Matti Meikäläinen syntyy torpassa.",
        "Suuret nälkävuodet koettelevat seutua.",
        "Matti muuttaa Amerikkaan.",
        "Kyläkoulu perustetaan.",
        "Suomi itsenäistyy.",
        "Talvisota alkaa."
    ],
    'Sarake_C': [
        "Kirkonkirjat: Kastettu 15.2.1850.",
        "Väestötilasto: Kuolleisuus huipussaan.",
        "Matkustajaluettelo: RMS Titanic (ei sentään).",
        "Kansakouluasetus voimaan.",
        "Valtiomuoto muuttuu.",
        "Liikekannallepanojulistus."
    ]
}
df = pd.DataFrame(data)

# Määritellään etäisyys tapahtumien välillä x-akselilla
STEP = 10 
df['x_pos'] = df.index * STEP  # Esim. 0, 10, 20, 30...

# 2. Luodaan kuvaaja (Figuuri)
fig, ax = plt.subplots(figsize=(12, 6))

# Piilotetaan y-akseli ja reunat, mutta jätetään x-akseli viitteeksi (valinnainen)
ax.yaxis.set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# Piirretään pitkä musta aikajana koko datan halki
# Viiva alkaa kohdasta -5 ja päättyy viimeisen tapahtuman ohi
max_x = df['x_pos'].max()
ax.plot([-5, max_x + 5], [0, 0], color="black", linewidth=2, zorder=1)

# 3. Piirretään KAIKKI tekstit valmiiksi paikoilleen
# Matplotlib on tehokkaampi, kun objektit ovat olemassa ja vain "kamera" liikkuu
text_width = 30

for i, row in df.iterrows():
    x = row['x_pos']
    
    # Pallo aikajanalle
    ax.scatter(x, 0, s=100, color='firebrick', zorder=2)
    
    # Vuosiluku pallon sisään tai viereen (tässä pallon alle hieman)
    ax.text(x, -0.8, str(row['Vuosi']), ha='center', va='top', fontsize=12, fontweight='bold')
    
    # Pystyviivat teksteihin (visuaalinen apu)
    ax.plot([x, x], [0, 3], color='gray', linestyle='--', alpha=0.5, linewidth=1) # Ylös
    ax.plot([x, x], [0, -3], color='gray', linestyle='--', alpha=0.5, linewidth=1) # Alas

    # Yläteksti (Sarake C)
    wrapped_c = "\n".join(textwrap.wrap(row['Sarake_C'], text_width))
    ax.text(x, 3.2, wrapped_c, ha='center', va='bottom', fontsize=10, color='darkblue', 
            bbox=dict(boxstyle="round,pad=0.3", fc="aliceblue", ec="blue", alpha=0.8))

    # Alateksti (Sarake B)
    wrapped_b = "\n".join(textwrap.wrap(row['Sarake_B'], text_width))
    ax.text(x, -3.2, wrapped_b, ha='center', va='top', fontsize=10, color='darkgreen',
             bbox=dict(boxstyle="round,pad=0.3", fc="honeydew", ec="green", alpha=0.8))

# Asetetaan Y-rajat kiinteiksi, jotta tekstit mahtuvat
ax.set_ylim(-8, 8)

# 4. Animaation logiikka: Kameran liike
# Luodaan lista x-koordinaateista, joissa kamera käy ("frames")
camera_positions = []

pause_frames = 20   # Kuinka monta ruutua pysytään paikallaan (lukuaika)
slide_frames = 30   # Kuinka monta ruutua kestää liuku seuraavaan

for i in range(len(df)):
    current_x = df.iloc[i]['x_pos']
    
    # 1. Pysähdy hetkeksi tapahtuman kohdalle
    camera_positions.extend([current_x] * pause_frames)
    
    # 2. Liiku seuraavaan (jos ei olla viimeisessä)
    if i < len(df) - 1:
        next_x = df.iloc[i+1]['x_pos']
        # Luodaan liukuva siirtymä nykyisestä seuraavaan
        transition = np.linspace(current_x, next_x, slide_frames)
        camera_positions.extend(transition)

def update(frame_x):
    # Päivitetään vain x-akselin näkymä (xlim)
    # Näytetään ikkuna: [keskipiste - 6, keskipiste + 6]
    window_width = 12
    ax.set_xlim(frame_x - (window_width/2), frame_x + (window_width/2))
    return ax,

# Luodaan animaatio
# interval = millisekuntia per ruutu. Pienempi luku = nopeampi liike.
ani = animation.FuncAnimation(fig, update, frames=camera_positions, interval=50, blit=False)

# Näytetään Streamlitissä
st.write("Generoidaan animaatiota, hetki pieni...")
st.components.v1.html(ani.to_jshtml(), height=600)

st.success("Valmis!")
