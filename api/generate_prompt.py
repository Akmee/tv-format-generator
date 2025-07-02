from http.server import BaseHTTPRequestHandler
import json
import os
import datetime
from urllib.parse import parse_qs
from openai import OpenAI

# Initialisiere den OpenAI-Client
# Der API-Schlüssel wird automatisch aus der Umgebungsvariable OPENAI_API_KEY geladen.
client = OpenAI()

# Nutze das GPT-3.5-Turbo Modell als 'o3 mini' Äquivalent, da 'o3 mini' kein offizieller Name ist.
# Wenn du ein spezifischeres Modell hast, ändere es hier.
OPENAI_MODEL = "gpt-3.5-turbo" # Kannst du auch auf "gpt-4o-mini" ändern, wenn es verfügbar ist

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # FormData verarbeiten
        form_data = parse_qs(post_data.decode('utf-8'), keep_blank_values=True)
        # Konvertiere Listen zu einzelnen Werten (FormData gibt Listen zurück)
        data = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}

        action_type = data.get('action_type', '')
        genre_input = data.get('genre_input', '')
        current_date = datetime.date.today().strftime('%d.%m.%Y')

        prompt_parts = []
        prompt_parts.append(f"Du bist ein erfahrener Experte der deutschsprachigen TV- und Streaminglandschaft mit 30 Jahren Berufspraxis. "
                             f"Du kennst alle Phasen von der Ideenentwicklung über Produktion, Postproduktion bis zur Platzierung auf Sender- oder Streamingebene. "
                             f"Du erkennst Marktchancen früh, entwickelst innovative Formate und denkst plattformübergreifend. "
                             f"Deine Kernzielgruppe ist 15–49 Jahre, du denkst aber grundsätzlich breit und international mit. "
                             f"Du arbeitest schnell, strukturiert und zielgerichtet – wie ein Produzent, der heute verkaufen muss.\n\n"
                             f"WICHTIG: Du arbeitest tagesaktuell. Das heutige Datum ist: {current_date}.")

        if action_type == 'brainstorming':
            prompt_parts.append("\n\n--- Brainstorming-Modus: Locker Ideen entwickeln ---")
            prompt_parts.append("Als Experte leite ich dich durch einen Dialog. Es muss nicht zwangsläufig ein vollständiges Format am Ende entstehen. Wir können auch ergebnislos enden.")
            prompt_parts.append("Ziel des Brainstormings: Gemeinsam neue Formatansätze finden, mit gezielten Fragen und strukturiertem Nachfragen.")
            prompt_parts.append("Basierend auf Markt, Trends, Zielgruppen und deiner Intuition.")
            prompt_parts.append("\n**Beginne den Experten-Dialog basierend auf den folgenden Eingaben des Nutzers. Stelle gezielte Nachfragen, um die Idee zu formen oder neue Richtungen vorzuschlagen:**")
            prompt_parts.append(f"1. Genre/Themenfeld, das gerade ein gutes Gefühl oder eine Idee weckt: {data.get('brainstorming_genre_feeling', 'Nicht angegeben')}")
            prompt_parts.append(f"2. Marktbeobachtung (was fehlt oder läuft gut): {data.get('brainstorming_market_observation', 'Nicht angegeben')}")
            prompt_parts.append(f"3. Zielgruppe und gewünschte Emotion: {data.get('brainstorming_target_group_emotion', 'Nicht angegeben')}")
            prompt_parts.append(f"4. Ton & Look des gedachten Trailers: {data.get('brainstorming_trailer_tone', 'Nicht angegeben')}")
            prompt_parts.append(f"5. Format-Pitch (wenn in einem Satz möglich): {data.get('brainstorming_format_pitch', 'Nicht angegeben')}")
            prompt_parts.append(f"6. Für welche Plattform wäre das geeignet (linear oder digital): {data.get('brainstorming_platform_suitability', 'Nicht angegeben')}")
            prompt_parts.append("\n**Antworte nun als Experte. Stelle gezielte Fragen zur weiteren Entwicklung der Idee oder schlage neue Richtungen vor. Denke daran, dass der Dialog auch ergebnislos enden kann. Halte deine Antwort flexibel und dialogorientiert.**")

        else: # Pitch Paper Template
            prompt_parts.append("\n\n--- Pitch Paper Template ist aktiviert ---")
            
            assignment_types = data.get('pp_assignment_type', [])
            # Convert to list if it's a single string for consistent processing
            if isinstance(assignment_types, str):
                assignment_types = [assignment_types]
            
            if "Weiterentwicklung eines bestehenden Formats" in assignment_types:
                prompt_parts.append("- Auftragsklärung: Weiterentwicklung eines bestehenden Formats")
            if "Neuentwicklung basierend auf Genre" in assignment_types:
                prompt_parts.append(f"- Auftragsklärung: Neuentwicklung basierend auf Genre: {data.get('pp_genre_input', 'Nicht angegeben')}")
            
            prompt_parts.append("\n**2. Marktanalyse (2020–2025)**")
            prompt_parts.append(f"Erfolgreiche Formate & Trends:\n{data.get('market_top_formats', 'N/A')}")
            prompt_parts.append(f"Marktanteile / Quoten:\n{data.get('market_shares', 'N/A')}")
            prompt_parts.append(f"Genre- & Formattrends:\n{data.get('market_genre_trends', 'N/A')}")
            prompt_parts.append(f"Plattformtrends:\n{data.get('market_platform_trends', 'N/A')}")
            prompt_parts.append(f"Zielgruppendynamiken:\n{data.get('market_target_group_dynamics', 'N/A')}")
            prompt_parts.append(f"Gesellschaftliche & technologische Einflüsse:\n{data.get('societal_influence_factors', 'N/A')}")
            prompt_parts.append(f"Neue Sehgewohnheiten:\n{data.get('new_viewing_habits', 'N/A')}")

            prompt_parts.append("\n**3. Formatentwicklung**")
            prompt_parts.append(f"Titel & Claim: {data.get('format_title_claim', 'N/A')}")
            prompt_parts.append(f"Genre, Setting, Zielgruppe: {data.get('format_genre_setting_target', 'N/A')}")
            prompt_parts.append(f"Tonalität & visuelles Konzept:\n{data.get('format_tone_visual', 'N/A')}")
            prompt_parts.append(f"USP & Zeitgeist:\n{data.get('format_usp_zeitgeist', 'N/A')}")
            prompt_parts.append(f"Staffelstruktur oder Episodenaufbau:\n{data.get('format_season_episode_structure', 'N/A')}")

            prompt_parts.append("\n**4. Plattform- & Vermarktungsstrategie**")
            prompt_parts.append(f"Primäre Plattform: {data.get('platform_primary', 'N/A')}")
            prompt_parts.append(f"Lineare Auswertung: {data.get('platform_linear', 'N/A')}")
            prompt_parts.append(f"Digitale Verlängerung: {data.get('platform_digital', 'N/A')}")
            prompt_parts.append(f"Internationale Skalierbarkeit: {data.get('platform_international', 'N/A')}")
            prompt_parts.append(f"Sponsoring- / Werbeoptionen:\n{data.get('platform_sponsoring', 'N/A')}")

            prompt_parts.append("\n**5. Bewertung & Ausblick**")
            prompt_parts.append(f"Erfolgschancen:\n{data.get('evaluation_success', 'N/A')}")
            prompt_parts.append(f"Risiken & Lösungen:\n{data.get('evaluation_risks', 'N/A')}")
            prompt_parts.append(f"Hinweise zur Pilotphase:\n{data.get('evaluation_pilot', 'N/A')}")
            
            prompt_parts.append("\n**6. Revision & Selbstkontrolle**")
            prompt_parts.append(f"Logik geprüft: {'Ja' if 'revision_logic' in data else 'Nein'}")
            prompt_parts.append(f"Zahlen & Trends belegt: {'Ja' if 'revision_data_trends' in data else 'Nein'}")
            prompt_parts.append(f"Formatierung klar: {'Ja' if 'revision_formatting' in data else 'Nein'}")
            prompt_parts.append(f"Alle Abschnitte vollständig: {'Ja' if 'revision_sections_complete' in data else 'Nein'}")
            prompt_parts.append("\n**Generiere nun das vollständige Pitch Paper basierend auf diesen Informationen.**")


        full_prompt = "\n".join(prompt_parts)

        try:
            # Stelle sicher, dass der API-Schlüssel gesetzt ist
            if not client.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")

            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Experte in der TV- und Streaminglandschaft. Deine Aufgabe ist es, entweder einen Brainstorming-Dialog zu führen oder ein Pitch Paper zu erstellen, basierend auf den Anweisungen. Wenn Brainstorming aktiv ist, konzentriere dich auf den Dialog und gib keine fertigen Ergebnisse aus, solange nicht explizit danach gefragt wird oder ein tragfähiger Kern entsteht."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            response_content = completion.choices[0].message.content
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "response": response_content}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))