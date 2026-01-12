import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl", page_icon="🚽", layout="wide")

# --- STATE MANAGEMENT ---
# Hier werden die Daten gespeichert, solange die App läuft
if 'log_data' not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Datum", "Name", "Von", "Bis", "Dauer"])

if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

# NAMEN & DEINE FARBEN
FARBEN = {
    "Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", 
    "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", 
    "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", 
    "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", 
    "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", 
    "Natalia": "#DDA0DD", "Lenny": "#0000FF"
}

# Wer ist weg?
wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None
bg_color = FARBEN.get(wer_ist_weg, "#1e1233") if wer_ist_weg else "#1e1233"

# --- STYLE (Dein ursprüngliches Rave-Design) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; transition: background 0.8s ease; color: white; }}
    .stButton>button {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        color: white;
        height: 120px;
        font-size: 22px !important;
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    /* Gold-Effekt wenn jemand weg ist */
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important;
        color: black !important;
        border: 5px solid gold !important;
    }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>👑 PRECHTL LOGBUCH</h1>", unsafe_allow_html=True)

# --- STATUS ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("🏠 IM RAUM", len(FARBEN) - (1 if wer_ist_weg else 0))
with c2: st.metric("🚽 STATUS", "BESETZT" if wer_ist_weg else "FREI")
if wer_ist_weg:
    sekunden_weg = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    m, s = divmod(sekunden_weg, 60)
    with c3: st.metric("⏳ LIVE-ZEIT", f"{m}m {s}s")

st.write("---")

# --- SCHÜLER GRID ---
cols = st.columns(3)
namen_sortiert = sorted(FARBEN.keys())

for i, name in enumerate(namen_sortiert):
    with cols[i % 3]:
        ist_dieser_weg = (wer_ist_weg == name)
        label = f"⌛ {name}" if ist_dieser_weg else name
        
        # Button ist deaktiviert, wenn schon jemand anderes weg ist
        if st.button(label, key=f"btn_{name}", use_container_width=True, disabled=(wer_ist_weg is not None and not ist_dieser_weg)):
            jetzt = datetime.now()
            if not ist_dieser_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start_zeit = st.session_state.auf_klo.pop(name)
                diff = jetzt - start_zeit
                m, s = divmod(int(diff.total_seconds()), 60)
                
                # In die interne Liste eintragen
                neue_daten = pd.DataFrame([{
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start_zeit.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                st.session_state.log_data = pd.concat([st.session_state.log_data, neue_daten], ignore_index=True)
                st.rerun()

# --- DOWNLOAD FÜR DIE LEHRERIN ---
st.write("---")
with st.expander("🔐 DOWNLOAD PROTOKOLL"):
    if not st.session_state.log_data.empty:
        st.table(st.session_state.log_data)
        csv = st.session_state.log_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Liste als CSV speichern",
            data=csv,
            file_name=f"Klo_Log_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.write("Noch keine Einträge vorhanden.")

# Automatischer Refresh für den Live-Timer
if wer_ist_weg:
    time.sleep(5)
    st.rerun()
