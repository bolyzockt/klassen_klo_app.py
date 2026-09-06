import hmac
import json
import secrets
import threading
import zlib
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Klassen-Klo-Terminal", page_icon="🚽", layout="wide")

APP_DIR = Path.home() / ".klassen_klo_terminal"
APP_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = APP_DIR / "klo_log.csv"
CONFIG_FILE = APP_DIR / "config.json"

LOG_COLUMNS = ["Datum", "Name", "Von", "Bis", "Dauer"]
ALARM_MINUTEN = 15
REFRESH_SEKUNDEN = 2

STANDARD_SCHUELER = [
    "Leon", "Arian", "Alex", "Sem", "Cinar", "Liam", "Nikita", "Malik",
    "Luca", "Lakisha", "Valeria", "Marianna", "Anna", "Mia", "Sofya",
    "Natalia", "Lenny",
]

EMOJI_POOL = [
    "⚡", "🔥", "🧊", "🕶️", "🌋", "🌊", "🌸", "👑", "🍀", "✨", "💎", "🌹",
    "🍭", "🌈", "🔮", "🌙", "🚀", "🐯", "🦊", "🐼", "🐸", "🦄", "🌵", "🍕",
    "🎸", "⚽", "🎨", "🧩", "🎯", "🍩",
]


def emoji_fuer(name: str) -> str:
    return EMOJI_POOL[zlib.crc32(name.encode("utf-8")) % len(EMOJI_POOL)]


def hash_password(password: str, salt: str) -> str:
    return sha256((salt + password).encode("utf-8")).hexdigest()


def default_config() -> dict:
    return {"password_hash": None, "password_salt": None, "schueler": list(STANDARD_SCHUELER)}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            cfg = default_config()
            cfg.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
            return cfg
        except Exception:
            pass
    return default_config()


def save_config(cfg: dict) -> None:
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


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
        "config": load_config(),
        "log": load_log(),
        "auf_klo": {},
        "lock": threading.Lock(),
    }


shared = get_shared_state()

BASIS_CSS = """
    <style>
    .ultra-title { text-align: center; font-size: 40px !important; font-weight: 900; text-shadow: 0 0 20px white; margin-bottom: 20px; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """


def render_ersteinrichtung():
    st.markdown(BASIS_CSS, unsafe_allow_html=True)
    st.markdown('<div class="ultra-title">🚀 ERSTEINRICHTUNG 🚀</div>', unsafe_allow_html=True)
    st.write("Willkommen! Bevor es losgeht: Admin-Passwort festlegen und Schülernamen eintragen.")
    with st.form("setup_form"):
        pw1 = st.text_input("Admin-Passwort festlegen", type="password")
        pw2 = st.text_input("Passwort wiederholen", type="password")
        namen_text = st.text_area(
            "Schülernamen (ein Name pro Zeile, später jederzeit im Admin-Bereich änderbar)",
            value="\n".join(STANDARD_SCHUELER),
            height=280,
        )
        abgeschickt = st.form_submit_button("✅ Einrichtung abschließen")

    if abgeschickt:
        if not pw1:
            st.error("Bitte ein Passwort eingeben.")
        elif pw1 != pw2:
            st.error("Passwörter stimmen nicht überein.")
        else:
            namen = [n.strip() for n in namen_text.splitlines() if n.strip()]
            salt = secrets.token_hex(16)
            with shared["lock"]:
                shared["config"]["password_salt"] = salt
                shared["config"]["password_hash"] = hash_password(pw1, salt)
                shared["config"]["schueler"] = namen
                save_config(shared["config"])
            st.success("Fertig! Die App startet jetzt neu.")
            st.rerun()


def berechne_status():
    auf_klo = shared["auf_klo"]
    wer_ist_weg = next(iter(auf_klo), None)
    sekunden_weg = 0
    ist_alarm = False
    if wer_ist_weg:
        sekunden_weg = int((datetime.now() - auf_klo[wer_ist_weg]).total_seconds())
        ist_alarm = sekunden_weg >= ALARM_MINUTEN * 60
    return wer_ist_weg, sekunden_weg, ist_alarm


@st.fragment(run_every=REFRESH_SEKUNDEN)
def render_status(anzahl_schueler: int):
    wer_ist_weg, sekunden_weg, ist_alarm = berechne_status()
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

    st.markdown('<div class="ultra-title">🚀 KLASSEN-KLO-TERMINAL 🚀</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👥 IM RAUM", f"{anzahl_schueler - (1 if wer_ist_weg else 0)}")
    with c2:
        st.metric("🚽 STATUS", "BESETZT 🛑" if wer_ist_weg else "FREI ✅")
    if wer_ist_weg:
        m, s = divmod(sekunden_weg, 60)
        with c3:
            st.metric("⏳ ZEIT WEG", f"{m:02d}:{s:02d}")
        if ist_alarm:
            st.markdown(f'<div class="alarm-text">⚠️ ALARM: {wer_ist_weg} IST ÜBERFÄLLIG! ⚠️</div>', unsafe_allow_html=True)


def render_rest():
    config = shared["config"]
    schueler = sorted(config["schueler"])
    auf_klo = shared["auf_klo"]
    wer_ist_weg, _, _ = berechne_status()

    st.write("---")

    if not schueler:
        st.info("Noch keine Schüler eingetragen. Im 🛠️ ADMIN TERMINAL unten hinzufügen.")
    else:
        cols = st.columns(3)
        for i, name in enumerate(schueler):
            with cols[i % 3]:
                ist_dieser_weg = (wer_ist_weg == name)
                emoji = emoji_fuer(name)
                label = f"🚽 {emoji} {name}" if ist_dieser_weg else f"{emoji} {name}"
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
        pw_input = st.text_input("Identity Verification", type="password", placeholder="Access Code eingeben...", key="admin_pw_input")
        eingeloggt = bool(pw_input) and hmac.compare_digest(hash_password(pw_input, config["password_salt"]), config["password_hash"])

        if eingeloggt:
            st.success("Access Granted.")
            st.dataframe(shared["log"], use_container_width=True)
            csv = shared["log"].to_csv(index=False).encode("utf-8")
            dateiname = f"Klo_Log_{datetime.now().strftime('%Y-%m-%d')}.csv"
            st.download_button(label="💾 DOWNLOAD LOGS", data=csv, file_name=dateiname, mime="text/csv")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ LOG LEEREN"):
                    shared["log"] = pd.DataFrame(columns=LOG_COLUMNS)
                    save_log(shared["log"])
                    st.rerun()
            with col_b:
                if wer_ist_weg and st.button(f"🔓 {wer_ist_weg} manuell zurückholen"):
                    with shared["lock"]:
                        auf_klo.pop(wer_ist_weg, None)
                    st.rerun()

            st.markdown("---")
            st.subheader("👥 Schüler verwalten")
            with st.form("schueler_hinzufuegen_form", clear_on_submit=True):
                neuer_name = st.text_input("Name hinzufügen")
                hinzugefuegt = st.form_submit_button("➕ Hinzufügen")
            if hinzugefuegt and neuer_name.strip():
                with shared["lock"]:
                    if neuer_name.strip() not in shared["config"]["schueler"]:
                        shared["config"]["schueler"].append(neuer_name.strip())
                        save_config(shared["config"])
                st.rerun()

            if schueler:
                zu_entfernen = st.selectbox("Schüler entfernen", options=[""] + schueler)
                if zu_entfernen and st.button(f"🗑️ {zu_entfernen} entfernen"):
                    with shared["lock"]:
                        if zu_entfernen in shared["config"]["schueler"]:
                            shared["config"]["schueler"].remove(zu_entfernen)
                        auf_klo.pop(zu_entfernen, None)
                        save_config(shared["config"])
                    st.rerun()

            st.markdown("---")
            st.subheader("🔑 Passwort ändern")
            with st.form("passwort_aendern_form", clear_on_submit=True):
                altes_pw = st.text_input("Aktuelles Passwort", type="password")
                neues_pw1 = st.text_input("Neues Passwort", type="password")
                neues_pw2 = st.text_input("Neues Passwort wiederholen", type="password")
                pw_geaendert = st.form_submit_button("Passwort ändern")
            if pw_geaendert:
                if not hmac.compare_digest(hash_password(altes_pw, config["password_salt"]), config["password_hash"]):
                    st.error("Aktuelles Passwort ist falsch.")
                elif not neues_pw1:
                    st.error("Neues Passwort darf nicht leer sein.")
                elif neues_pw1 != neues_pw2:
                    st.error("Neue Passwörter stimmen nicht überein.")
                else:
                    with shared["lock"]:
                        neuer_salt = secrets.token_hex(16)
                        shared["config"]["password_salt"] = neuer_salt
                        shared["config"]["password_hash"] = hash_password(neues_pw1, neuer_salt)
                        save_config(shared["config"])
                    st.success("Passwort geändert.")
        elif pw_input:
            st.error("Invalid Code. Access Denied.")

    st.markdown('<div class="copyright">Klassen-Klo-Terminal</div>', unsafe_allow_html=True)


if not shared["config"].get("password_hash"):
    render_ersteinrichtung()
else:
    render_status(len(shared["config"]["schueler"]))
    render_rest()
