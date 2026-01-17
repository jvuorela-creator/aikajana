import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import textwrap

# Asetetaan sivun otsikko
st.title("Sukututkimuksen aikajana")
st.write("Tämä animaatio näyttää tapahtumat aikajanalla.")

# 1. Data (Voit myöhemmin muuttaa tämän tiedoston lataukseksi st.file_uploader:lla)
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

# 2. Luodaan kuvaaja
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
ax.set_ylim(-10, 10)
ax.set_xlim(0, 10)
ax.axhline(y=0, color='black', linewidth=2)

# Alustetaan tekstit
vuosi_text = ax.text(5, 0, '', ha='center', va='center', fontsize=20, 
                     bbox=dict(boxstyle="round", fc="white", ec="black"))
ylateksti = ax.text(5, 4, '', ha='center', va='center', fontsize=14, color='darkblue', wrap=True)
alateksi = ax.text(5, -4, '', ha='center', va='center', fontsize=14, color='darkgreen', wrap=True)

ax.text(9, 1, "Sarake C", fontsize=8, color='grey')
ax.text(9, -1, "Sarake B", fontsize=8, color='grey')

def update(frame):
    row = df.iloc[frame]
    vuosi_text.set_text(str(row['Vuosi']))
    
    width = 40
    ylateksti.set_text("\n".join(textwrap.wrap(row['Sarake_C'], width)))
    alateksi.set_text("\n".join(textwrap.wrap(row['Sarake_B'], width)))
    return vuosi_text, ylateksti, alateksi

# 3. Luodaan animaatio
ani = animation.FuncAnimation(fig, update, frames=len(df), interval=2000, blit=False)

# --- TÄMÄ OSA ON MUUTETTU STREAMLITIA VARTEN ---
# Muutetaan animaatio HTML/JS-muotoon, jotta selain osaa toistaa sen
st.components.v1.html(ani.to_jshtml(), height=600)
