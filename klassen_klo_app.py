import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v27", page_icon="🚽", layout="wide")

# --- STATE (Speichert die Daten lokal in der App) ---
if 'log_data' not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Datum", "Name", "Von", "Bis", "Dauer"])

if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

# NAMEN & FARBEN (Dein Rave-Design)
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
bg_color = FARBEN.get(wer_ist_weg, "#1e1233") if wer_ist_weg else "linear-gradient(135deg, #1e1233 0%, #3a007d 100%)"

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 0.8s ease; color: white; }}
    .stButton>button {{
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2); border-radius: 15px;
        color: white; height: 90px; font-size: 20px !important; font-weight: bold;
    }}
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important; color: black !important; border: 4px solid gold !important;
    }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>👑 PRECHTL LOGBUCH</h1>", unsafe_allow_html=True)

# --- STATUS ANZEIGE ---
c1, c2 = st.columns(2)
with c1: st.metric("🚽 STATUS", "BESETZT" if wer_ist_weg else "FREI")
if wer_ist_weg:
    diff = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    m, s = divmod(diff, 60)
    with c2: st.metric("⏳ ZEIT", f"{m}m {s}s")

st.write("---")

# --- SCHÜLER GRID ---
cols = st.columns(3)
namen_sortiert = sorted(FARBEN.keys())

for i, name in enumerate(namen_sortiert):
    with cols[i % 3]:
        ist_dieser_weg = (wer_ist_weg == name)
        label = f"⌛ {name}" if ist_dieser_weg else name
        
        if st.button(label, key=name, use_container_width=True, disabled=(wer_ist_weg and not ist_dieser_weg)):
            jetzt = datetime.now()
            if not ist_dieser_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start = st.session_state.auf_klo.pop(name)
                diff_sec = int((jetzt - start).total_seconds())
                m, s = divmod(diff_sec, 60)
                
                # In die lokale Liste schreiben
                neue_zeile = pd.DataFrame([{
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                st.session_state.log_data = pd.concat([st.session_state.log_data, neue_zeile], ignore_index=True)
                st.rerun()

# --- EXPORT BEREICH ---
st.write("---")
with st.expander("💾 LISTE SPEICHERN (Für Frau Prechtl)"):
    if not st.session_state.log_data.empty:
        st.dataframe(st.session_state.log_data, use_container_width=True)
        
        # CSV/Excel Download Button
        csv = st.session_state.log_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Liste als CSV herunterladen",
            data=csv,
            file_name=f"Klo-Logbuch_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Noch keine Einträge für heute vorhanden.")

# Timer Refresh
if wer_ist_weg:
    time.sleep(5)
    st.rerun()
