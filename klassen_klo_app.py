import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v26", page_icon="👑", layout="wide")

# --- DESIGN ---
# Ein cooles Lila als Standard, damit es nicht schwarz ist
bg_style = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1233 0%, #3a007d 100%);
        color: white;
    }
    .stButton>button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px; color: white; height: 80px; font-weight: bold;
    }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """
st.markdown(bg_style, unsafe_allow_html=True)

# --- VERBINDUNGS-CHECK ---
@st.cache_resource
def get_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        return e

conn = get_connection()

if isinstance(conn, Exception):
    st.error(f"⚠️ Verbindungsproblem: {conn}")
    st.info("Checke deine Secrets in Streamlit Cloud!")
    st.stop()

# --- STATE ---
if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

FARBEN = {
    "Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", 
    "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", 
    "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", 
    "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", 
    "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", 
    "Natalia": "#DDA0DD", "Lenny": "#0000FF"
}

klo_liste = list(st.session_state.auf_klo.keys())
aktuell_weg = klo_liste[0] if len(klo_liste) > 0 else None

# --- UI ---
st.title("👑 PRECHTL CONTROL")

if aktuell_weg:
    diff = int((datetime.now() - st.session_state.auf_klo[aktuell_weg]).total_seconds())
    m, s = divmod(diff, 60)
    st.warning(f"⚠️ {aktuell_weg} ist seit {m}m {s}s auf Toilette")
else:
    st.success("✅ Alle Schüler sind im Raum")

st.write("---")

cols = st.columns(3)
for i, name in enumerate(sorted(FARBEN.keys())):
    with cols[i % 3]:
        ist_weg = (aktuell_weg == name)
        label = f"⌛ {name}" if ist_weg else name
        disabled = (aktuell_weg is not None and not ist_weg)
        
        if st.button(label, key=f"btn_{name}", use_container_width=True, disabled=disabled):
            jetzt = datetime.now()
            if not ist_weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start = st.session_state.auf_klo.pop(name)
                d_sec = int((jetzt - start).total_seconds())
                m, s = divmod(d_sec, 60)
                
                try:
                    # Daten senden
                    new_data = pd.DataFrame([{
                        "Datum": jetzt.strftime("%d.%m.%Y"),
                        "Name": name,
                        "Von": start.strftime("%H:%M:%S"),
                        "Bis": jetzt.strftime("%H:%M:%S"),
                        "Dauer": f"{m}m {s}s"
                    }])
                    df = conn.read(ttl=0)
                    updated = pd.concat([df, new_data], ignore_index=True)
                    conn.update(data=updated)
                    st.toast("Gespeichert!")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
                    time.sleep(5)
                st.rerun()

if aktuell_weg:
    time.sleep(5)
    st.rerun()
