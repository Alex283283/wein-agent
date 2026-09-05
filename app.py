"""
Wein-Empfehlungs-Agent
======================

Eine kleine Streamlit-Web-App, die:
1. Ein Foto einer Weinkarte entgegennimmt (Upload oder Handy-Kamera),
2. dein persönliches Geschmacksprofil kennt,
3. Claude (mit Vision) bittet, die Karte zu lesen und dir 1-2 passende
   Weine zu empfehlen, inklusive Begründung.

Für absolute Anfänger kommentiert. Wenn du noch keinen API-Key hast,
läuft die App trotzdem im "Demo-Modus" mit einer Beispiel-Antwort,
damit du die komplette Struktur schon mal live sehen kannst.
"""

import base64
import os

import streamlit as st

# Das "anthropic" Paket ist der offizielle Python-Client für die Claude API.
# Falls es nicht installiert ist (z.B. weil requirements.txt noch nicht
# ausgeführt wurde), fangen wir das ab und laufen automatisch im Demo-Modus.
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

# Welches Claude-Modell wir für die Empfehlung benutzen. claude-sonnet-5
# kann Bilder lesen (Vision) und ist ein guter Mix aus Preis und Qualität
# für so ein Hobby-Projekt. Für noch günstiger könntest du später auf
# "claude-haiku-4-5" wechseln, für noch bessere Qualität auf "claude-opus-5".
MODEL_NAME = "claude-sonnet-5"

st.set_page_config(page_title="Wein-Agent", page_icon="🍷", layout="centered")


def get_api_key():
    """Sucht den API-Key zuerst in den Streamlit-Secrets (fürs Deployment),
    dann in einer Umgebungsvariable (fürs lokale Testen). Findet er keinen,
    läuft die App im Demo-Modus weiter."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


API_KEY = get_api_key()
DEMO_MODE = not (API_KEY and ANTHROPIC_AVAILABLE)


# ---------------------------------------------------------------------------
# Geschmacksprofil (Sidebar) — bereits mit deinen bekannten Vorlieben vorbefüllt
# ---------------------------------------------------------------------------

st.sidebar.header("🍇 Dein Geschmacksprofil")
st.sidebar.caption("Das schickt die App mit, damit die Empfehlung wirklich zu dir passt.")

farben = st.sidebar.multiselect(
    "Welche Weinarten kommen für dich infrage?",
    ["Weißwein", "Rosé", "Rotwein", "Schaumwein"],
    default=["Weißwein", "Rosé"],
)

suesse = st.sidebar.radio(
    "Süße",
    ["Trocken", "Halbtrocken", "Lieblich", "Egal"],
    index=0,
)

stil_notizen = st.sidebar.text_area(
    "Stil-Notizen",
    value=(
        "Frisch, säurebetont, mittlerer Körper, nicht zu schwer oder "
        "buttrig/holzfassgereift. Lieblingsweine bisher: Cà dei Frati "
        "\"I Frati\" Lugana (Rebsorte Turbiana, Italien) und ein "
        "trockener deutscher Roséwein im Spätburgunder-Stil."
    ),
    height=140,
)

preis_max = st.sidebar.slider(
    "Preis pro Flasche bis (€, ca.)", min_value=10, max_value=150, value=45, step=5
)

no_gos = st.sidebar.text_input(
    "No-Gos (optional)",
    value="sehr tanninreiche oder stark holzfassgereifte Weine",
)


def profil_als_text():
    """Baut aus den Widget-Werten einen kompakten Text, den wir Claude
    als Beschreibung des Geschmacks mitgeben."""
    return (
        f"Bevorzugte Weinarten: {', '.join(farben) if farben else 'keine Einschränkung'}.\n"
        f"Süße: {suesse}.\n"
        f"Stil-Notizen: {stil_notizen}\n"
        f"Preisrahmen: bis ca. {preis_max} € pro Flasche.\n"
        f"No-Gos: {no_gos}."
    )


# ---------------------------------------------------------------------------
# Hauptbereich: Foto hochladen
# ---------------------------------------------------------------------------

st.title("🍷 Wein-Agent")
st.write(
    "Lade ein Foto der Weinkarte hoch (oder mach eins mit der Handy-Kamera), "
    "und der Agent empfiehlt dir passend zu deinem Geschmack."
)

if DEMO_MODE:
    st.info(
        "🧪 **Demo-Modus:** Es ist noch kein API-Key hinterlegt, daher siehst du "
        "gerade eine Beispiel-Antwort statt einer echten Analyse. Sobald du einen "
        "Anthropic API-Key hast, trag ihn als Secret ein (siehe README) — dann "
        "liest der Agent deine echte Karte.",
        icon="🧪",
    )

foto = st.file_uploader(
    "Foto der Weinkarte", type=["jpg", "jpeg", "png"], accept_multiple_files=False
)
kamera_foto = st.camera_input("...oder direkt fotografieren")

bild_datei = kamera_foto or foto

empfehlen = st.button("Empfehlung holen", type="primary", disabled=bild_datei is None)


# ---------------------------------------------------------------------------
# Die eigentliche "Agenten"-Logik
# ---------------------------------------------------------------------------

MOCK_ANTWORT = """\
**Weißwein: Vermentino, Sardinien (34 € auf der Karte)**
Ähnliche Stilrichtung wie deine Lugana: frisch, Zitrusnoten, mittlerer \
Körper, unoaked statt buttrig-schwer.
Vivino: 3.8 ★ (Beispielwert) · Einkaufspreis: ca. 10-14 € (Beispielwert)

**Rosé: Spätburgunder Rosé, Baden (31 € auf der Karte)**
Gleiche Traube (Spätburgunder = Pinot Noir) wie dein bisheriger \
Lieblings-Rosé, hell und frisch mit roten Beeren.
Vivino: 3.6 ★ (Beispielwert) · Einkaufspreis: ca. 9-12 € (Beispielwert)

*(Das ist eine Beispiel-Antwort im Demo-Modus — mit echtem API-Key liest \
der Agent hier deine tatsächliche Karte und sucht echte Vivino-Bewertungen \
und Preise im Web.)*
"""


def bild_zu_base64(uploaded_file):
    """Wandelt die hochgeladene Bilddatei in Base64 um — so verlangt es
    die Claude API für Bilder."""
    raw_bytes = uploaded_file.getvalue()
    media_type = uploaded_file.type or "image/jpeg"
    return base64.standard_b64encode(raw_bytes).decode("utf-8"), media_type


def hole_empfehlung(uploaded_file, profil_text):
    if DEMO_MODE:
        return MOCK_ANTWORT

    b64_bild, media_type = bild_zu_base64(uploaded_file)
    client = anthropic.Anthropic(api_key=API_KEY)

    system_prompt = (
        "Du bist ein hilfsbereiter Sommelier-Assistent. Du bekommst ein Foto "
        "einer Weinkarte und ein Geschmacksprofil. Lies alle Weine von der "
        "Karte, wähle die 1-2 besten Treffer (z.B. je einen Weißwein/Rosé/"
        "Rotwein, soweit vorhanden und passend) und begründe kurz und "
        "konkret, warum sie zum Profil passen (z.B. Rebsorte, Stil, Region, "
        "Preis).\n\n"
        "Für JEDEN empfohlenen Wein nutze außerdem die Websuche, um "
        "herauszufinden:\n"
        "1. Die Vivino-Bewertung (Punkte von 1-5 und, falls zu finden, die "
        "Anzahl der Bewertungen), z.B. \"Vivino: 3.9 ★ (12.000 Bewertungen)\".\n"
        "2. Den ungefähren Einkaufspreis im Handel/Online-Weinshop (also was "
        "man für die Flasche zum Selberkaufen zahlt, NICHT der Preis auf der "
        "Restaurantkarte), inkl. kurzer Quellenangabe, z.B. \"Einkaufspreis: "
        "ca. 12-15 € (z.B. weinfreunde.de)\".\n"
        "Findest du zu einem Wein nichts Eindeutiges (z.B. weil Jahrgang "
        "oder genauer Name unklar ist), schreib das ehrlich dazu statt etwas "
        "zu erfinden.\n\n"
        "Antworte auf Deutsch, in Markdown, ohne unnötige Länge."
    )

    response = client.messages.create(
        model=MODEL_NAME,
        # Großzügig bemessen: Bild lesen + bis zu 4 Websuchen + Text
        # brauchen mehr "Denk-Platz" als eine reine Text-Antwort.
        max_tokens=4096,
        system=system_prompt,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_bild,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Mein Geschmacksprofil:\n{profil_text}",
                    },
                ],
            }
        ],
    )
    # Bei Websuche kann die Antwort aus mehreren Blöcken bestehen (Text +
    # Suchergebnisse dazwischen) — wir hängen nur die Text-Blöcke aneinander.
    antwort = "\n\n".join(
        block.text for block in response.content if block.type == "text"
    )

    if not antwort.strip():
        # Kam nichts Verwertbares zurück (z.B. weil das Token-Limit mitten in
        # den Websuchen erreicht wurde), zeigen wir das transparent an statt
        # einer stillen Leerseite.
        antwort = (
            "⚠️ Ich konnte diesmal keine vollständige Antwort erzeugen "
            f"(Grund laut API: `{response.stop_reason}`). "
            "Versuch es gerne nochmal — manchmal hilft ein zweiter Versuch, "
            "oder probier ein schärferes/kleineres Foto der Karte."
        )
    return antwort


if empfehlen and bild_datei is not None:
    with st.spinner("Lese Karte und überlege..."):
        try:
            antwort = hole_empfehlung(bild_datei, profil_als_text())
            st.markdown("### 🍷 Empfehlung")
            st.markdown(antwort)
        except Exception as exc:  # Für Anfänger: Fehler sichtbar machen statt Absturz
            st.error(f"Da ist etwas schiefgelaufen: {exc}")
