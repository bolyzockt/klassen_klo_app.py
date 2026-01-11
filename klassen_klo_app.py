import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v9", page_icon="👑", layout="wide")

# NAMEN & FARBEN
FARBEN = {
    "Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", 
    "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", 
    "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", 
    "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", 
    "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", 
    "Natalia": "#DDA0DD", "Lenny": "#0000FF"
}

LEHRER_PASSWORT = "prechtl"
ALARM_ZEIT_MIN = 15

# --- STATE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'auf_klo' not in st.session_state: st.session_state.auf_klo = {}

wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None
bg_color = FARBEN.get(wer_ist_weg, "#1e1233") if wer_ist_weg else "#1e1233"

# Zeit-Berechnung für die Anzeige
dauer_minuten, rest_sekunden = 0, 0
if wer_ist_weg:
    sekunden_weg = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    dauer_minuten = sekunden_weg // 60
    rest_sekunden = sekunden_weg % 60

# --- CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: all 0.5s ease; color: white; }}
    .stButton>button {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        color: white;
        height: 130px;
        font-size: 22px !important;
        font-weight: 800;
        white-space: pre-wrap;
    }}
    div[data-testid="stButton"] button:contains("⌛") {{
        background: white !important; color: black !important;
        border: 5px solid gold !important;
    }}
    .status-card {{ background: rgba(0,0,0,0.5); padding: 20px; border-radius: 25px; text-align: center; }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>👑 PRECHTL CONTROL CENTER v9</h1>", unsafe_allow_html=True)

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='status-card'><h3>🏫 IM RAUM</h3><h2>{len(FARBEN) - (1 if wer_ist_weg else 0)}</h2></div>", unsafe_allow_html=True)
with c2: 
    st.markdown(f"<div class='status-card'><h3>🚽 STATUS</h3><h2>{'BESETZT' if wer_ist_weg else 'FREI'}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='status-card'><h3>⏳ LIVE-ZEIT</h3><h2>{dauer_minuten}m {rest_sekunden}s</h2></div>", unsafe_allow_html=True)

# --- ALARM ---
if wer_ist_weg and dauer_minuten >= ALARM_ZEIT_MIN:
    st.markdown(f"<h1 style='color: red; text-align: center; background: white;'>🚨 {wer_ist_weg.upper()} ÜBER 15 MIN! 🚨</h1>", unsafe_allow_html=True)

st.write("---")

# --- GRID ---
cols = st.columns(3)
for i, name in enumerate(sorted(FARBEN.keys())):
    with cols[i % 3]:
        weg = (wer_ist_weg == name)
        deakt = (wer_ist_weg is not None and not weg)
        label = f"⌛ {name}\n({dauer_minuten}m {rest_sekunden}s)\nZURÜCKKOMMEN" if weg else f"{name} ✨"
        
        if st.button(label, key=f"b_{name}", use_container_width=True, disabled=deakt):
            jetzt = datetime.now()
            if not weg:
                st.session_state.auf_klo[name] = jetzt
            else:
                start_zeit = st.session_state.auf_klo.pop(name)
                diff = jetzt - start_zeit
                m, s = divmod(int(diff.total_seconds()), 60)
                
                # DAS PROTOKOLL-FORMAT
                st.session_state.logs.append({
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start_zeit.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m} Min, {s} Sek"
                })
            st.rerun()

# --- LEHRER LOG ---
st.write("---")
with st.expander("🔐 LEHRER-PROTOKOLL (Passwort: prechtl)"):
    pw = st.text_input("Passwort", type="password")
    if pw == LEHRER_PASSWORT:
        if st.session_state.logs:
            # Tabelle mit ausgerichteten Spalten
            df = pd.DataFrame(st.session_state.logs)
            st.table(df[["Datum", "Name", "Von", "Bis", "Dauer"]])
            
            # Excel Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Excel-Liste herunterladen", buffer.getvalue(), "Klo_Protokoll.xlsx")
            
            if st.button("🗑️ Alle Einträge löschen"):
                st.session_state.logs = []
                st.rerun()
        else:
            st.write("Noch keine Einträge vorhanden.")