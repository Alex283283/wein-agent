# 🍷 Wein-Agent

Ein kleiner Agent, der ein Foto einer Weinkarte liest und dir passend zu
deinem Geschmack 1-2 Weine empfiehlt — als Web-App, die du am Handy im
Browser öffnest.

## Was ist hier drin?

- `app.py` — die ganze App (Streamlit-Oberfläche + Aufruf der Claude API)
- `requirements.txt` — die Pakete, die die App braucht (werden beim
  Deployment automatisch installiert)

## Lokal testen (optional, auf deinem PC)

Falls du es vorher auf deinem PC ausprobieren willst:

1. Python installieren (falls noch nicht vorhanden): https://www.python.org/downloads/
2. In diesem Ordner ein Terminal öffnen und ausführen:
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. Es öffnet sich automatisch dein Browser mit der App (Demo-Modus, da noch
   kein API-Key hinterlegt ist).

Du kannst diesen Schritt aber auch überspringen und direkt deployen (siehe
unten) — dann läuft es sowieso in der Cloud, nicht auf deinem PC.

## Live schalten, damit es am Handy funktioniert

Kein Git/Terminal nötig — komplett über den Browser:

1. **GitHub-Account erstellen** (falls noch nicht vorhanden): https://github.com/signup
2. **Neues Repository anlegen**: oben rechts auf **+** → **New repository**,
   z.B. Name `wein-agent`, "Public" oder "Private" ist beide okay, dann
   **Create repository**.
3. Auf der neuen Repo-Seite: **Add file → Upload files**, dann `app.py` und
   `requirements.txt` aus diesem Ordner per Drag & Drop hochladen, unten
   **Commit changes** klicken.
4. Auf **https://share.streamlit.io** gehen, mit GitHub einloggen.
5. **Create app** → dein `wein-agent`-Repository auswählen → als
   Hauptdatei `app.py` angeben → **Deploy**.
6. Nach ein bis zwei Minuten bekommst du einen Link
   (z.B. `https://dein-name-wein-agent.streamlit.app`) — den kannst du am
   Handy im Browser öffnen oder dir als Lesezeichen/Homescreen-Symbol
   speichern.

## Später: echten API-Key hinterlegen

Ohne Key läuft die App im Demo-Modus (Beispiel-Antwort). Sobald du einen
Key von https://console.anthropic.com hast:

1. In Streamlit Cloud bei deiner App auf **Settings → Secrets**.
2. Dort eintragen:
   ```
   ANTHROPIC_API_KEY = "dein-key-hier"
   ```
3. Speichern — die App startet neu und liest ab jetzt echte Weinkarten.
