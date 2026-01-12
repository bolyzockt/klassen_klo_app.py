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

# DEINE NAMEN & FARBEN & EMOJIS
SCHUELER_INFO = {
    "Leon": {"farbe": "#8A2BE2", "emoji": "⚡"},
    "Arian": {"farbe": "#00CED1", "emoji": "🔥"},
    "Alex": {"farbe": "#4682B4", "emoji": "🧊"},
    "Sem": {"farbe": "#1a1a1a", "emoji": "🕶️"},
    "Cinar": {"farbe": "#FF4500", "emoji": "🌋"},
    "Liam": {"farbe": "#1E90FF", "emoji": "🌊"},
    "Nikita": {"farbe": "#FF1493", "emoji": "🌸"},
    "Malik": {"farbe": "#DAA520", "emoji": "👑"},
    "Luca": {"farbe": "#32CD32", "emoji": "🍀"},
    "Lakisha": {"farbe": "#9370DB", "emoji": "✨"},
    "Valeria": {"farbe": "#FF69B4", "emoji": "💎"},
    "Marianna": {"farbe": "#8B0000", "emoji": "🌹"},
    "Anna": {"farbe": "#F08080", "emoji": "🍭"},
    "Mia": {"farbe": "#FFB6C1", "emoji": "🌈"},
    "Sofya": {"farbe": "#4B0082", "emoji": "🔮"},
    "Natalia": {"farbe": "#DDA0DD", "emoji": "🌙"},
    "Lenny": {"farbe": "#0000FF", "emoji": "🚀"}
}

# HIER IST DAS PASSWORT IM CODE GESPEICHERT (wird in der App nicht angezeigt)
GEHEIMES_PW = "prechtl"

# Wer ist weg?
wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None
current_color = SCHUELER_INFO.get(wer_ist_weg, {}).get("farbe", "#1e1233") if wer_ist_weg else "#1e1233"

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {current_color}; transition: background 0.8s ease; color: white; }}
    
    .ultra-title {{
        text-align: center;
        font-size: 45px !important;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 15px {current_color}, 0 0 30px white;
        margin-bottom: 20px;
        padding: 10px;
    }}

    .stButton>button {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        color: white;
        height: 110px;
        font-size: 24px !important;
        font-weight: 800;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        border-color: white;
        transform: scale(1.02);
    }}
    
    div[data-testid="stButton"] button:contains("🚽") {{
        background: white !important;
        color: black !important;
        border: 5px solid gold !important;
        box-shadow: 0 0 40px gold;
    }}
    
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div class="ultra-title">🚀 ULTIMATIVE KLO LISTE 4000 v500 🚀</div>', unsafe_allow_html=True)

# --- STATUS DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("👥 IM RAUM", f"{len(SCHUELER_INFO) - (1 if wer_ist_weg else 0)}")
with c2: st.metric("🚽 STATUS", "BESETZT 🛑" if wer_ist_weg else "FREI ✅")
if wer_ist_weg:
    sekunden_weg = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    m, s = divmod(sekunden_weg, 60)
    with c3: st.metric("⏳ MISSION TIME", f"{m:02d}:{s:02d}")

st.write("---")

# --- SCHÜLER GRID ---
cols = st.columns(3)
namen_sortiert = sorted(SCHUELER_INFO.keys())

for i, name in enumerate(namen_sortiert):
    with cols[i % 3]:
        ist_dieser_weg = (wer_ist_weg == name)
        info = SCHUELER_INFO[name]
        label = f"🚽 {info['emoji']} {name} {info['emoji']}" if ist_dieser_weg else f"{info['emoji']} {name}"
        
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
                    "Name": f"{info['emoji']} {name}",
                    "Von": start_zeit.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                st.session_state.log_data = pd.concat([st.session_state.log_data, neue_daten], ignore_index=True)
                st.rerun()

# --- GEHEIMER PROTOKOLL BEREICH ---
st.write("---")
with st.expander("🛠️ ADMIN TERMINAL"):
    pw_input = st.text_input("Access Code erforderlich", type="password")
    if pw_input == GEHEIMES_PW:
        st.success("ZUGRIFF GEWÄHRT")
        if not st.session_state.log_data.empty:
            st.dataframe(st.session_state.log_data, use_container_width=True)
            csv = st.session_state.log_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="💾 DATEN-EXPORT", data=csv, file_name="klo_log.csv", mime="text/csv")
            if st.button("🗑️ PROTOKOLL LÖSCHEN"):
                st.session_state.log_data = pd.DataFrame(columns=["Datum", "Name", "Von", "Bis", "Dauer"])
                st.rerun()
        else:
            st.info("Keine Daten in der Datenbank.")
    elif pw_input != "":
        st.error("ZUGRIFF VERWEIGERT!")

# Auto-Refresh
if wer_ist_weg:
    time.sleep(5)
    st.rerun()
