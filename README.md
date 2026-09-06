# Klassen-Klo-Terminal

Kleine Anzeige-App für den Klassenraum: zeigt, wer gerade auf dem Klo ist, warnt bei
Überziehung und führt ein Log. Nur die Lehrkraft installiert und richtet die App ein;
Schüler bedienen sie am selben Bildschirm/Gerät im Raum.

## App herunterladen (kein Python nötig)

1. Im GitHub-Repo oben auf **Actions** → **Build Desktop App** klicken.
2. Neuesten erfolgreichen Lauf öffnen (oder über **Run workflow** manuell starten).
3. Ganz unten bei **Artifacts** die passende Datei herunterladen:
   - `KlassenKloTerminal-windows` → enthält `KlassenKloTerminal.exe`
   - `KlassenKloTerminal-mac` → enthält `KlassenKloTerminal` (Mac-Programm)
   - `KlassenKloTerminal-linux` → enthält `KlassenKloTerminal` (Linux-Programm)
4. Entpacken und die Datei doppelklicken. Es öffnet sich automatisch der Browser mit der App.

Windows/Mac zeigen beim ersten Start eventuell eine Sicherheitswarnung ("unbekannter
Herausgeber"), weil die Datei nicht signiert ist – auf "Trotzdem ausführen" bzw. im
Mac-Kontextmenü auf "Öffnen" klicken.

## Erste Einrichtung

Beim allerersten Start fragt die App nach:
- einem selbst gewählten Admin-Passwort (nur die Lehrkraft kennt es),
- den Namen der Schüler:innen (einer pro Zeile).

Beides lässt sich später jederzeit im Bereich **🛠️ ADMIN TERMINAL** ändern
(Passwort ändern, Schüler hinzufügen/entfernen).

Alle Daten (Passwort-Hash, Schülerliste, Klo-Log) liegen lokal auf dem Rechner unter
`~/.klassen_klo_terminal/` (bzw. unter Windows `C:\Users\<Name>\.klassen_klo_terminal\`)
und überleben Neustarts der App.

## Entwicklung / manuell starten

```bash
pip install -r requirements.txt
streamlit run klassen_klo_app.py
```

## Selbst als exe/App bauen

```bash
pip install -r requirements-build.txt
pyinstaller klassen_klo_terminal.spec
```

Das Ergebnis liegt danach in `dist/`. PyInstaller baut nur für das Betriebssystem, auf
dem es ausgeführt wird – für Windows- und Mac-Dateien übernimmt das die GitHub-Actions-
Pipeline (`.github/workflows/build.yml`) automatisch auf den jeweiligen Runnern.
