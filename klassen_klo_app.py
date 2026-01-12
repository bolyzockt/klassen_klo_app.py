import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Ultimative Klo Liste 4000 v500", page_icon="🚽", layout="wide")

# --- STATE MANAGEMENT ---
if 'log_data' not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Datum", "Name", "Von", "Bis", "Dauer"])

if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

# DEINE NAMEN & FARBEN
FARBEN = {
    "Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", 
    "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", 
    "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", 
    "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", 
    "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", 
    "Natalia": "#DDA0DD", "Lenny": "#0000FF"
}
LEHRER_PASSWORT = "prechtl"

# Wer ist weg?
wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None
bg_color = FARBEN.get(wer_ist_weg, "#1e1233") if wer_ist_weg else "#1e1233"

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; transition: background 0.8s ease; color: white; }}
    
    /* Der ultimative Titel-Glow */
    .ultra-title {{
        text-align: center;
        font-size: 50px !important;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.8), 0 0 20px rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }}

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
    
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important;
        color: black !important;
        border: 5px solid gold !important;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
    }}
    
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# Neuer ultimativer Header
st.markdown('<div class="ultra-title">ULTIMATIVE KLO LISTE 4000 v500</div>', unsafe_allow_html=True)

# --- STATUS ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("🏠 IM RAUM", len(FARBEN) - (1 if wer_ist_weg else 0))
with c2: st.metric("🚽 STATUS", "BESETZT" if wer_ist_weg else "FREI")
if wer_ist_weg:
    sekunden_weg = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    m, s = divmod(sekunden_weg, 60)
    with c3: st.metric("⏳ LIVE-TIMER", f"{m}m {s}s")

st.write("---")

# --- SCHÜLER GRID ---
cols = st.columns(3)
namen_sortiert = sorted(FARBEN.keys())

for i, name in enumerate(namen_sortiert):
    with cols[i % 3]:
        ist_dieser_weg = (wer_ist_weg == name)
        label = f"⌛ {name}" if ist_dieser_weg else name
        
        if st.button(label, key=f"btn_{name}", use_container_width=True, disabled=(wer_ist_weg is not None and not ist_dieser_weg)):
            jetzt = datetime.now()
            if not ist_dieser_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start_zeit = st.session_state.auf_klo.pop(name)
                diff = jetzt - start_zeit
                m, s = divmod(int(diff.total_seconds()), 60)
                
                neue_daten = pd.DataFrame([{
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start_zeit.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                st.session_state.log_data = pd.concat([st.session_state.log_data, neue_daten], ignore_index=True)
                st.rerun()

# --- PROTOKOLL ---
st.write("---")
with st.expander("🔐 LEHRER-PROTOKOLL (PASSWORT: prechtl)"):
    pw_input = st.text_input("Administrator Passwort", type="password")
    if pw_input == LEHRER_PASSWORT:
        if not st.session_state.log_data.empty:
            st.dataframe(st.session_state.log_data, use_container_width=True)
            csv = st.session_state.log_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Protokoll", data=csv, file_name="klo_log_ultra.csv", mime="text/csv")
        else:
            st.info("Noch keine Daten.")
    elif pw_input != "":
        st.error("Falsches Passwort!")

# Auto-Refresh
if wer_ist_weg:
    time.sleep(5)
    st.rerun()
