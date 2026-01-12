import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v18", page_icon="👑")

# --- VERBINDUNG ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = st.secrets["gsheets_url"]
except:
    st.error("❌ Link in den Secrets fehlt!")
    url = None

if 'auf_klo' not in st.session_state: st.session_state.auf_klo = {}

# Namen & Farben (gekürzt für Übersicht)
FARBEN = {"Leon": "#8A2BE2", "Arian": "#00CED1", "Alex": "#4682B4", "Sem": "#1a1a1a", "Cinar": "#FF4500", "Liam": "#1E90FF", "Nikita": "#FF1493", "Malik": "#DAA520", "Luca": "#32CD32", "Lakisha": "#9370DB", "Valeria": "#FF69B4", "Marianna": "#8B0000", "Anna": "#F08080", "Mia": "#FFB6C1", "Sofya": "#4B0082", "Natalia": "#DDA0DD", "Lenny": "#0000FF"}

wer_ist_weg = list(st.session_state.auf_klo.keys())[0] if st.session_state.auf_klo else None

# Zeit-Berechnung
dauer_m, rest_s = 0, 0
if wer_ist_weg:
    diff = int((datetime.now() - st.session_state.auf_klo[wer_ist_weg]).total_seconds())
    dauer_m, rest_s = diff // 60, diff % 60

st.title("🚽 Prechtl Control v18")

# --- BUTTON GRID ---
cols = st.columns(3)
for i, name in enumerate(sorted(FARBEN.keys())):
    with cols[i % 3]:
        weg = (wer_ist_weg == name)
        if st.button(f"{'⌛' if weg else ''} {name}", key=name, use_container_width=True, disabled=(wer_ist_weg and not weg)):
            jetzt = datetime.now()
            if not weg:
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                start = st.session_state.auf_klo.pop(name)
                d = jetzt - start
                m, s = divmod(int(d.total_seconds()), 60)
                
                # DATEN-OBJEKT
                new_row = pd.DataFrame([{"Datum": jetzt.strftime("%d.%m.%Y"), "Name": name, "Von": start.strftime("%H:%M:%S"), "Bis": jetzt.strftime("%H:%M:%S"), "Dauer": f"{m}m {s}s"}])
                
                # SPEICHER-VERSUCH
                try:
                    df_alt = conn.read(spreadsheet=url, ttl=0)
                    df_neu = pd.concat([df_alt, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=df_neu)
                    st.success("✅ Gespeichert!")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"❌ FEHLER BEIM SPEICHERN: {e}")
                    # Zeigt den Fehler für 10 Sekunden an
                    time.sleep(10)
                st.rerun()

if wer_ist_weg:
    st.metric("Zeit weg", f"{dauer_m}m {rest_s}s")
    time.sleep(5)
    st.rerun()
