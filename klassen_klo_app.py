import hmac
import os
import threading
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Frau Prechtls krasses Terminal - 8bm", page_icon="🚽", layout="wide")

LOG_COLUMNS = ["Datum", "Name", "Von", "Bis", "Dauer"]
LOG_FILE = Path(__file__).parent / "klo_log.csv"
ALARM_MINUTEN = 15
REFRESH_SEKUNDEN = 2

SCHUELER_INFO = {
    "Leon": {"emoji": "⚡"},
    "Arian": {"emoji": "🔥"},
    "Alex": {"emoji": "🧊"},
    "Sem": {"emoji": "🕶️"},
    "Cinar": {"emoji": "🌋"},
    "Liam": {"emoji": "🌊"},
    "Nikita": {"emoji": "🌸"},
    "Malik": {"emoji": "👑"},
    "Luca": {"emoji": "🍀"},
    "Lakisha": {"emoji": "✨"},
    "Valeria": {"emoji": "💎"},
    "Marianna": {"emoji": "🌹"},
    "Anna": {"emoji": "🍭"},
    "Mia": {"emoji": "🌈"},
    "Sofya": {"emoji": "🔮"},
    "Natalia": {"emoji": "🌙"},
    "Lenny": {"emoji": "🚀"},
}


def get_admin_password() -> str:
    env_pw = os.environ.get("KLO_ADMIN_PASSWORD")
    if env_pw:
        return env_pw
    try:
        return st.secrets["admin_password"]
    except Exception:
        return "prechtl"


def load_log() -> pd.DataFrame:
    if LOG_FILE.exists():
        try:
            return pd.read_csv(LOG_FILE, dtype=str)
        except Exception:
            pass
    return pd.DataFrame(columns=LOG_COLUMNS)


def save_log(df: pd.DataFrame) -> None:
    try:
        df.to_csv(LOG_FILE, index=False)
    except Exception:
        pass


@st.cache_resource
def get_shared_state():
    return {
        "log": load_log(),
        "auf_klo": {},
        "lock": threading.Lock(),
    }


shared = get_shared_state()


@st.fragment(run_every=REFRESH_SEKUNDEN)
def render_app():
    auf_klo = shared["auf_klo"]
    wer_ist_weg = next(iter(auf_klo), None)

    ist_alarm = False
    sekunden_weg = 0
    if wer_ist_weg:
        sekunden_weg = int((datetime.now() - auf_klo[wer_ist_weg]).total_seconds())
        ist_alarm = sekunden_weg >= ALARM_MINUTEN * 60

    bg_color = "#FF0000" if ist_alarm else ("#8A2BE2" if wer_ist_weg else "#1e1233")

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; transition: background 0.5s ease; color: white; }}
        .ultra-title {{ text-align: center; font-size: 40px !important; font-weight: 900; text-shadow: 0 0 20px white; margin-bottom: 20px; }}
        .stButton>button {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 15px;
            color: white; height: 80px; font-size: 18px !important; font-weight: bold;
        }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
        .alarm-text {{ color: yellow; font-weight: bold; text-align: center; font-size: 30px; animation: blink 1s infinite; border: 3px dashed yellow; border-radius: 10px; padding: 10px; }}
        .copyright {{ text-align: center; font-size: 12px; color: rgba(255,255,255,0.3); margin-top: 50px; }}
        header {{visibility: hidden;}} footer {{visibility: hidden;}}
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="ultra-title">🚀 FRAU PRECHTLS KRASSES TERMINAL 🚀</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👥 IM RAUM", f"{len(SCHUELER_INFO) - (1 if wer_ist_weg else 0)}")
    with c2:
        st.metric("🚽 STATUS", "BESETZT 🛑" if wer_ist_weg else "FREI ✅")
    if wer_ist_weg:
        m, s = divmod(sekunden_weg, 60)
        with c3:
            st.metric("⏳ ZEIT WEG", f"{m:02d}:{s:02d}")
        if ist_alarm:
            st.markdown(f'<div class="alarm-text">⚠️ ALARM: {wer_ist_weg} IST ÜBERFÄLLIG! ⚠️</div>', unsafe_allow_html=True)

    st.write("---")

    cols = st.columns(3)
    namen_sortiert = sorted(SCHUELER_INFO.keys())
    for i, name in enumerate(namen_sortiert):
        with cols[i % 3]:
            ist_dieser_weg = (wer_ist_weg == name)
            info = SCHUELER_INFO[name]
            label = f"🚽 {info['emoji']} {name}" if ist_dieser_weg else f"{info['emoji']} {name}"
            geklickt = st.button(
                label,
                key=f"btn_{name}",
                use_container_width=True,
                type="primary" if ist_dieser_weg else "secondary",
                disabled=(wer_ist_weg is not None and not ist_dieser_weg),
            )
            if geklickt:
                jetzt = datetime.now()
                with shared["lock"]:
                    if not auf_klo and name not in auf_klo:
                        auf_klo[name] = jetzt
                    elif name in auf_klo:
                        start_zeit = auf_klo.pop(name)
                        diff = jetzt - start_zeit
                        m, s = divmod(int(diff.total_seconds()), 60)
                        neue_zeile = pd.DataFrame([{
                            "Datum": jetzt.strftime("%d.%m.%Y"),
                            "Name": name,
                            "Von": start_zeit.strftime("%H:%M:%S"),
                            "Bis": jetzt.strftime("%H:%M:%S"),
                            "Dauer": f"{m}m {s}s",
                        }])
                        shared["log"] = pd.concat([shared["log"], neue_zeile], ignore_index=True)
                        save_log(shared["log"])
                st.rerun()

    st.write("---")
    with st.expander("🛠️ ADMIN TERMINAL"):
        pw_input = st.text_input("Identity Verification", type="password", placeholder="Access Code eingeben...")
        if pw_input and hmac.compare_digest(pw_input, get_admin_password()):
            st.success("Access Granted. 8bm Core Online.")
            st.dataframe(shared["log"], use_container_width=True)
            csv = shared["log"].to_csv(index=False).encode("utf-8")
            dateiname = f"Prechtl_Log_8bm_{datetime.now().strftime('%Y-%m-%d')}.csv"
            st.download_button(label="💾 DOWNLOAD LOGS", data=csv, file_name=dateiname, mime="text/csv")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ CLEAR SYSTEM MEMORY"):
                    shared["log"] = pd.DataFrame(columns=LOG_COLUMNS)
                    save_log(shared["log"])
                    st.rerun()
            with col_b:
                if wer_ist_weg and st.button(f"🔓 {wer_ist_weg} manuell zurückholen"):
                    with shared["lock"]:
                        auf_klo.pop(wer_ist_weg, None)
                    st.rerun()

            st.markdown("---")
            st.write("© 2026 bolyzockt | System: bolyzockt OS v501")
        elif pw_input:
            st.error("Invalid Code. Access Denied.")

    st.markdown('<div class="copyright">© 2026 bolyzockt - Frau Prechtls krasses Terminal 8bm</div>', unsafe_allow_html=True)


render_app()
