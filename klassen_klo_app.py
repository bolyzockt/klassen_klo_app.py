import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import io
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v16", page_icon="👑", layout="wide")

# --- GOOGLE SHEETS VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- STATE MANAGEMENT ---
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
LEHRER_PASSWORT = "prechtl"

wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None
bg_color = FARBEN.get(wer_ist_weg, "#1e1233") if wer_ist_weg else "#1e1233"

# Zeit-Berechnung
dauer_minuten, rest_sekunden = 0, 0
if wer_ist_weg:
    sekunden_weg = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    dauer_minuten = sekunden_weg // 60
    rest_sekunden = sekunden_weg % 60

# --- STYLING ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 0.8s ease; color: white; }}
    .stButton>button {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        color: white;
        height: 120px;
        font-size: 22px !important;
        font-weight: bold;
    }}
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(0,0,0,0.8); color: white;
        text-align: center; padding: 15px; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: -50px;'>👑 PRECHTL CONTROL CENTER v16</h1>", unsafe_allow_html=True)

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("🏫 IM RAUM", len(FARBEN) - (1 if wer_ist_weg else 0))
with c2: st.metric("🚽 STATUS", "BESETZT" if wer_ist_weg else "FREI")
with c3: st.metric("⏳ LIVE-ZEIT", f"{dauer_minuten}m {rest_sekunden}s")

st.write("---")

# --- GRID ---
cols = st.columns(3)
for i, name in enumerate(sorted(FARBEN.keys())):
    with cols[i % 3]:
        weg = (wer_ist_weg == name)
        deakt = (wer_ist_weg is not None and not weg)
        label = f"⌛ {name}\n({dauer_minuten}m {rest_sekunden}s)" if weg else f"{name}"
        
        if st.button(label, key=f"b_{name}", use_container_width=True, disabled=deakt):
            jetzt = datetime.now()
            if not weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start_zeit = st.session_state.auf_klo.pop(name)
                diff = jetzt - start_zeit
                m, s = divmod(int(diff.total_seconds()), 60)
                
                # DATEN FÜR GOOGLE SHEETS
                new_row = pd.DataFrame([{
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start_zeit.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                
                # SCHNELLER SPEICHERN (Nur beim Zurückkommen!)
                try:
                    url = st.secrets["gsheets_url"]
                    # Wir lesen die Daten nur einmal kurz, um sie zu erweitern
                    existing_data = conn.read(spreadsheet=url, ttl=0) 
                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                except Exception as e:
                    st.error("Speicher-Lag! Daten wurden lokal gesichert.")
                
                st.rerun()

# --- LEHRER BEREICH ---
with st.expander("🔐 ONLINE PROTOKOLL"): 
    pw = st.text_input("Passwort", type="password")
    if pw == LEHRER_PASSWORT:
        url = st.secrets.get("gsheets_url", "#")
        st.markdown(f"### [Hier klicken für die Online-Tabelle]({url})")
        if st.button("Tabelle jetzt laden"):
            data = conn.read(spreadsheet=url, ttl=0)
            st.table(data)

# FOOTER
st.markdown('<div class="footer">© 2026 Programmed by Bolyzockt | Leon</div>', unsafe_allow_html=True)

# --- PERFORMANCE TIMER ---
if wer_ist_weg:
    time.sleep(5) # Wartezeit für weniger Lag
    st.rerun()
