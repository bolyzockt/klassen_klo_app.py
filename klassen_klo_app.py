import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
st.set_page_config(page_title="Klo-Logbuch Prechtl v19", page_icon="👑")

# --- VERBINDUNG ZU GOOGLE ---
# Wir laden die Verbindung nur einmal am Anfang
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = st.secrets["gsheets_url"]
except Exception as e:
    st.error("Secrets oder Google-Link fehlen!")
    url = None

# --- STATE INITIALISIERUNG ---
if 'auf_klo' not in st.session_state:
    st.session_state.auf_klo = {}

# NAMEN
NAMEN = ["Leon", "Arian", "Alex", "Sem", "Cinar", "Liam", "Nikita", "Malik", "Luca", "Lakisha", "Valeria", "Marianna", "Anna", "Mia", "Sofya", "Natalia", "Lenny"]

# Wer ist weg? (Sichere Abfrage)
aktuell_weg = list(st.session_state.auf_klo.keys())[0] if len(st.session_state.auf_klo) > 0 else None

# --- TIMER BERECHNUNG ---
dauer_text = "Frei"
if aktuell_weg:
    sekunden = int((datetime.now() - st.session_state.auf_klo[aktuell_weg]).total_seconds())
    m, s = divmod(sekunden, 60)
    dauer_text = f"⏱️ {aktuell_weg}: {m}m {s}s"

st.title("🚽 Prechtl Control v19")
st.subheader(dauer_text)

# --- BUTTON GRID ---
cols = st.columns(3)
for i, name in enumerate(sorted(NAMEN)):
    with cols[i % 3]:
        # Logik: Ist dieser Schüler gerade weg?
        ist_weg = (aktuell_weg == name)
        # Logik: Ist der Button gesperrt? (Ja, wenn jemand anderes weg ist)
        button_gesperrt = (aktuell_weg is not None and not ist_weg)
        
        label = f"⌛ {name}" if ist_weg else name
        
        if st.button(label, key=f"btn_{name}", use_container_width=True, disabled=button_gesperrt):
            jetzt = datetime.now()
            
            if not ist_weg:
                # Jemand geht
                st.session_state.auf_klo[name] = jetzt
                st.rerun()
            else:
                # Jemand kommt zurück
                start = st.session_state.auf_klo.pop(name)
                diff = jetzt - start
                m, s = divmod(int(diff.total_seconds()), 60)
                
                # Zeile für Google
                neue_daten = pd.DataFrame([{
                    "Datum": jetzt.strftime("%d.%m.%Y"),
                    "Name": name,
                    "Von": start.strftime("%H:%M:%S"),
                    "Bis": jetzt.strftime("%H:%M:%S"),
                    "Dauer": f"{m}m {s}s"
                }])
                
                # Speichern Versuch
                if url:
                    try:
                        with st.spinner('Speichere in Google Sheets...'):
                            alt = conn.read(spreadsheet=url, ttl=0)
                            kombiniert = pd.concat([alt, neue_daten], ignore_index=True)
                            conn.update(spreadsheet=url, data=kombiniert)
                        st.success("Gespeichert!")
                        time.sleep(1)
                    except Exception as e:
                        st.error(f"Google Fehler: {e}")
                        time.sleep(3)
                
                st.rerun()

# --- REFRESH FÜR TIMER ---
if aktuell_weg:
    time.sleep(5)
    st.rerun()
