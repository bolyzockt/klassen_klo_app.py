import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v23", page_icon="👑", layout="wide")

# --- GOOGLE SHEETS VERBINDUNG ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Verbindung wird hergestellt...")

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

# Aktueller Status
wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None

# HINTERGRUND-LOGIK: Wenn frei -> Cooles Lila, Wenn besetzt -> Rave-Farbe
if wer_ist_weg:
    bg_color = FARBEN.get(wer_ist_weg, "#1e1233")
else:
    bg_color = "linear-gradient(135deg, #1e1233 0%, #3a007d 100%)"

# Zeitrechnung
dauer_m, dauer_s = 0, 0
if wer_ist_weg:
    diff = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    dauer_m, dauer_s = divmod(diff, 60)

# --- STYLE (Verbesserte GUI) ---
st.markdown(f"""
    <style>
    .stApp {{ 
        background: {bg_color}; 
        background-attachment: fixed;
        transition: background 0.8s ease; 
        color: white; 
    }}
    .stButton>button {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px; 
        color: white; 
        height: 90px; 
        font-size: 18px !important; 
        font-weight: bold;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        border-color: white;
        transform: scale(1.02);
        background: rgba(255, 255, 255, 0.15);
    }}
    /* Der "Ich bin weg" Button */
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important; 
        color: black !important; 
        border: 4px solid #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stMetric {{ background: rgba(0,0,0,0.2); padding: 10px; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);'>👑 PRECHTL CONTROL</h1>", unsafe_allow_html=True)

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("🏠 IM RAUM", len(FARBEN) - (1 if wer_ist_weg else 0))
with c2: st.metric("🚽 STATUS", "BESETZT" if wer_ist_weg else "FREI")
with c3: st.metric("⏱️ ZEIT", f"{dauer_m}m {dauer_s}s" if wer_ist_weg else "--")

st.write("---")

# --- GRID ---
cols = st.columns(3)
for i, name in enumerate(sorted(FARBEN.keys())):
    with cols[i % 3]:
        ist_weg = (wer_ist_weg == name)
        label = f"⌛ {name}" if ist_weg else name
        if st.button(label, key=name, use_container_width=True, disabled=(wer_ist_weg and not ist_weg)):
            jetzt = datetime.now()
            if not ist_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start = st.session_state.auf_klo.pop(name)
                diff_sec = int((jetzt - start).total_seconds())
                m, s = divmod(diff_sec, 60)
                
                # Speichern
                new_row = pd.DataFrame([{"Datum": jetzt.strftime("%d.%m.%Y"), "Name": name, "Von": start.strftime("%H:%M:%S"), "Bis": jetzt.strftime("%H:%M:%S"), "Dauer": f"{m}m {s}s"}])
                try:
                    df = conn.read(ttl=0)
                    updated = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated)
                    st.toast(f"✅ Eintrag für {name} erstellt!")
                except:
                    st.error("Online-Speicher fehlgeschlagen!")
                st.rerun()

# Timer Refresh
if wer_ist_weg:
    time.sleep(5)
    st.rerun()
