import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v24", page_icon="👑", layout="wide")

# --- GOOGLE SHEETS VERBINDUNG ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Warte auf Verbindung...")

# --- STATE ---
if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

# NAMEN & FARBEN
FARBEN = {
    "Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", 
    "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", 
    "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", 
    "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", 
    "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", 
    "Natalia": "#DDA0DD", "Lenny": "#0000FF"
}

# Wer ist weg? (Sicherheits-Check gegen TypeError)
klo_liste = list(st.session_state.auf_klo.keys())
aktuell_weg = klo_liste[0] if len(klo_liste) > 0 else None

# HINTERGRUND-LOGIK
if aktuell_weg:
    # Rave-Farbe des Schülers
    bg_color = FARBEN.get(aktuell_weg, "#1e1233")
else:
    # Cooles Space-Lila statt Schwarz
    bg_color = "linear-gradient(135deg, #1e1233 0%, #3a007d 100%)"

# Zeitrechnung
dauer_m, dauer_s = 0, 0
if aktuell_weg:
    diff = int((datetime.now() - st.session_state.auf_klo[aktuell_weg]).total_seconds())
    dauer_m, dauer_s = divmod(diff, 60)

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ 
        background: {bg_color}; 
        background-attachment: fixed;
        transition: background 0.8s ease; 
        color: white; 
    }}
    .stButton>button {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px; color: white; height: 90px; 
        font-size: 18px !important; font-weight: bold;
    }}
    /* Gold-Modus für den Schüler auf Klo */
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important; color: black !important; 
        border: 4px solid gold !important;
    }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>👑 PRECHTL CONTROL</h1>", unsafe_allow_html=True)

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("🏠 IM RAUM", len(FARBEN) - (1 if aktuell_weg else 0))
with c2: st.metric("🚽 STATUS", "BESETZT" if aktuell_weg else "FREI")
with c3: st.metric("⏱️ ZEIT", f"{dauer_m}m {dauer_s}s" if aktuell_weg else "--")

st.write("---")

# --- BUTTON GRID ---
cols = st.columns(3)
namen_sortiert = sorted(FARBEN.keys())

for i, name in enumerate(namen_sortiert):
    with cols[i % 3]:
        ist_dieser_weg = (aktuell_weg == name)
        # Sicherheitsschaltung für den Button-Status
        button_disabled = bool(aktuell_weg is not None and not ist_dieser_weg)
        
        button_label = f"⌛ {name}" if ist_dieser_weg else name
        
        if st.button(button_label, key=f"btn_{name}", use_container_width=True, disabled=button_disabled):
            jetzt = datetime.now()
            if not ist_dieser_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start = st.session_state.auf_klo.pop(name)
                diff_sec = int((jetzt - start).total_seconds())
                m, s = divmod(diff_sec, 60)
                
                # In Google Sheets speichern
                try:
                    with st.spinner("Speichere im Logbuch..."):
                        new_row = pd.DataFrame([{
                            "Datum": jetzt.strftime("%d.%m.%Y"),
                            "Name": name,
                            "Von": start.strftime("%H:%M:%S"),
                            "Bis": jetzt.strftime("%H:%M:%S"),
                            "Dauer": f"{m}m {s}s"
                        }])
                        df = conn.read(ttl=0)
                        updated = pd.concat([df, new_row], ignore_index=True)
                        conn.update(data=updated)
                    st.toast(f"✅ Log für {name} gespeichert!")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"Speicherfehler: {e}")
                    time.sleep(2)
                st.rerun()

# Automatischer Refresh für den Timer
if aktuell_weg:
    time.sleep(5)
    st.rerun()
