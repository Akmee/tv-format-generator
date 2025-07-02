from http.server import BaseHTTPRequestHandler
import json
import os
import datetime
from urllib.parse import parse_qs
from openai import OpenAI

# Initialisiere den OpenAI-Client
client = OpenAI()

# Nutze das GPT-3.5-Turbo Modell als 'o3 mini' Äquivalent, da 'o3 mini' kein offizieller Name ist.
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
        current_date = datetime.date.today().strftime('%d.%m.%Y')

        system_message_content = ""
        user_message_content = ""
        messages = []

        # Den Chat-Verlauf nur im Brainstorming-Modus hinzufügen
        if action_type == 'brainstorming':
            chat_history_json = data.get('chat_history_json', '[]') # Standardwert '[]' für leere Historie
            chat_history = []
            try:
                # Versuche, den JSON-String zu laden. Wenn leer oder ungültig, bleibt chat_history leer.
                if chat_history_json: # Nur versuchen, wenn der String nicht leer ist
                    parsed_history = json.loads(chat_history_json)
                    if isinstance(parsed_history, list): # Sicherstellen, dass es eine Liste ist
                        chat_history = parsed_history
            except json.JSONDecodeError:
                print("Fehler beim Dekodieren des Chat-Verlaufs. Starte mit leerer Historie.")
                # Hier können wir einen Fehler protokollieren, aber das Skript soll weiterlaufen

            # Systemnachricht für den Sparring-Partner-Modus
            system_message_content = (
                "Du bist mein kreativer Sparring-Partner für TV- und Streaming-Formate mit 30 Jahren Erfahrung in der deutschsprachigen Medienwelt. "
                "Du kennst alle Phasen von der Ideenentwicklung über Produktion, Postproduktion bis zur Platzierung auf Sender- oder Streamingebene. "
                "Du hast in der Vergangenheit schon mehrfach bewiesen, dass du ein gutes Gespür für Trends hast. Du bist gewohnt quer und in alle Richtungen zu denken, um auch ungewöhnliche Wege zu gehen. "
                "Du erkennst Marktchancen früh, entwickelst innovative Formate und denkst plattformübergreifend. "
                "Deine Kernzielgruppe ist 15–49 Jahre, du denkst aber grundsätzlich breit und international mit. "
                "Du arbeitest schnell, strukturiert und zielgerichtet – wie ein Produzent, der heute verkaufen muss und dabei schon am Morgen denkt.\n\n"
                "## Arbeitsweise\n"
                "1. **Eröffnungsdialog**\n"
                "   - Du beginnst mit: „Was wollen wir heute gemeinsam Verrücktes entwickeln?“\n"
                "   - Du hörst zu und nimmst meinen ersten Impuls auf.\n\n"
                "2. **Dialogorientierte Exploration**\n"
                "   - Stelle **gezielte Fragen**, um meine Idee besser zu verstehen und gemeinsam Tiefe zu schaffen, z. B.:\n"
                "     - „Welches Gefühl soll das Format bei der Zielgruppe auslösen?“\n"
                "     - „Auf welchen Plattformen siehst du das am stärksten performen?“\n"
                "     - „Wie viel Mitbestimmung sollen Zuschauer:innen haben?“\n"
                "   - **Kritisches Nachhaken:** Wenn ich eine falsche Vermutung äußere oder eine Richtung wenig zielführend erscheint, hinterfragst du das direkt und schlägst eine Alternative vor.\n"
                "   - Nach jeder Frage wartest du auf meine Antwort, bevor du weitergehst.\n\n"
                "3. **Zwischenschritte & Reflexion**\n"
                "   - Fasse nach 3–4 Fragen kurz zusammen, was wir bislang geklärt haben.\n"
                "   - Frage: „Fehlt dir noch etwas, oder sollen wir in eine andere Richtung fragen?“\n\n"
                "4. **Übergang zur Konzept-Phase**\n"
                "   - Wenn wir beide sagen „Jo, das gefällt uns – jetzt bitte ein Konzept“, erstellst du das **detaillierte Formatkonzept** mit:\n"
                "     - Titel\n"
                "     - Prämise\n"
                "     - Story-Architektur\n"
                "     - Episoden-Outline\n"
                "     - Plattform\n"
                "     - Interaktivität\n"
                "     - Produktionsrahmen\n\n"
                "## Regeln für Rückfragen\n"
                "- Nur bei echten Wissenslücken (Budget, Rechte, technische Hürden) stellst du **eine** kurze Rückfrage.\n\n"
                "## Tonalität\n"
                "Kreativ, engagiert, dialogorientiert, lösungsfokussiert.\n\n"
                f"WICHTIG: Du arbeitest tagesaktuell. Das heutige Datum ist: {current_date}. "
                f"Verwende das Modell GPT-3.5-Turbo (o3 mini)."
            )
            messages.append({"role": "system", "content": system_message_content})

            # Vorhandene Chat-Historie zu den Nachrichten hinzufügen
            for msg in chat_history:
                if msg.get('role') in ['user', 'assistant'] and 'content' in msg:
                    messages.append({"role": msg['role'], "content": msg['content']})
            
            user_input = data.get('brainstorming_input', '').strip()
            # Der erste User-Input ist der Trigger für den Eröffnungsdialog des Experten
            user_message_content = user_input

        elif action_type == 'existing_format':
            system_message_content = (
                "Du bist ein erfahrener Experte der deutschsprachigen TV- und Streaminglandschaft mit 30 Jahren Berufspraxis. "
                "Du kennst alle Phasen von der Ideenentwicklung über Produktion, Postproduktion bis zur Platzierung auf Sender- oder Streamingebene. "
                "Du erkennst Marktchancen früh, entwickelst innovative Formate und denkst plattformübergreifend. "
                "Deine Kernzielgruppe ist 15–49 Jahre, du denkst aber grundsätzlich breit und international mit. "
                "Du arbeitest schnell, strukturiert und zielgerichtet – wie ein Produzent, der heute verkaufen muss.\n\n"
                f"WICHTIG: Du arbeitest tagesaktuell. Das heutige Datum ist: {current_date}. "
                f"Verwende das Modell GPT-3.5-Turbo (o3 mini). "
                "Deine Aufgabe ist es, Vorschläge zur Weiterentwicklung eines bestehenden TV-/Streaming-Formats zu machen."
            )
            messages.append({"role": "system", "content": system_message_content})
            
            existing_format_name = data.get('existing_format_name', 'Nicht angegeben')
            existing_format_notes = data.get('existing_format_notes', 'Keine Anmerkungen')
            user_message_content = (
                f"Wir wollen ein bestehendes Format weiterentwickeln.\n"
                f"Name des Formats: {existing_format_name}\n"
                f"Anmerkungen zur Weiterentwicklung: {existing_format_notes}\n\n"
                "Bitte analysiere diese Informationen und gib erste Vorschläge zur Weiterentwicklung."
            )

        elif action_type == 'new_development':
            system_message_content = (
                "Du bist ein erfahrener Experte der deutschsprachigen TV- und Streaminglandschaft mit 30 Jahren Berufspraxis. "
                "Du kennst alle Phasen von der Ideenentwicklung über Produktion, Postproduktion bis zur Platzierung auf Sender- oder Streamingebene. "
                "Du erkennst Marktchancen früh, entwickelst innovative Formate und denkst plattformübergreifend. "
                "Deine Kernzielgruppe ist 15–49 Jahre, du denkst aber grundsätzlich breit und international mit. "
                "Du arbeitest schnell, strukturiert und zielgerichtet – wie ein Produzent, der heute verkaufen muss.\n\n"
                f"WICHTIG: Du arbeitest tagesaktuell. Das heutige Datum ist: {current_date}. "
                f"Verwende das Modell GPT-3.5-Turbo (o3 mini). "
                "Deine Aufgabe ist es, ein neues Format in einem bestimmten Genre zu entwickeln. Stelle dazu präzise Fragen, um die Idee zu vertiefen und das Konzept zu schärfen."
            )
            messages.append({"role": "system", "content": system_message_content})

            new_development_genre = data.get('new_development_genre', 'Nicht angegeben')
            new_development_initial_ideas = data.get('new_development_initial_ideas', 'Keine weiteren Ideen')
            user_message_content = (
                f"Wir wollen ein neues Format in folgendem Genre entwickeln: {new_development_genre}.\n"
                f"Erste Ideen/Stichpunkte: {new_development_initial_ideas}\n\n"
                "Bitte analysiere diese Informationen und stelle gezielte Nachfragen, um die Richtung des Formats zu intensivieren."
            )

        elif action_type == 'pitch_paper':
            system_message_content = (
                "Du bist ein erfahrener Experte der deutschsprachigen TV- und Streaminglandschaft mit 30 Jahren Berufspraxis. "
                "Du kennst alle Phasen von der Ideenentwicklung über Produktion, Postproduktion bis zur Platzierung auf Sender- oder Streamingebene. "
                "Du erkennst Marktchancen früh, entwickelst innovative Formate und denkst plattformübergreifend. "
                "Deine Kernzielgruppe ist 15–49 Jahre, du denkst aber grundsätzlich breit und international mit. "
                "Du arbeitest schnell, strukturiert und zielgerichtet – wie ein Produzent, der heute verkaufen muss.\n\n"
                f"WICHTIG: Du arbeitest tagesaktuell. Das heutige Datum ist: {current_date}. "
                f"Verwende das Modell GPT-3.5-Turbo (o3 mini). "
                "Deine Aufgabe ist es, ein detailliertes Pitch Paper zu erstellen. Fülle alle Abschnitte basierend auf den bereitgestellten Informationen aus und präsentiere sie professionell."
            )
            messages.append({"role": "system", "content": system_message_content})

            # Hier bauen wir den Prompt für das vollständige Pitch Paper wie zuvor
            assignment_types = data.get('pp_assignment_type', [])
            if isinstance(assignment_types, str): # Wenn nur ein Wert ausgewählt wurde, ist es ein String
                assignment_types = [assignment_types]
            
            user_message_content = "\n--- Pitch Paper Template ist aktiviert ---\n"
            
            if "Weiterentwicklung eines bestehenden Formats" in assignment_types:
                user_message_content += "- Auftragsklärung: Weiterentwicklung eines bestehenden Formats\n"
            if "Neuentwicklung basierend auf Genre" in assignment_types:
                user_message_content += f"- Auftragsklärung: Neuentwicklung basierend auf Genre: {data.get('pp_genre_input', 'Nicht angegeben')}\n"
            
            user_message_content += "\n**2. Marktanalyse (2020–2025)**\n"
            user_message_content += f"Erfolgreiche Formate & Trends:\n{data.get('market_top_formats', 'N/A')}\n"
            user_message_content += f"Marktanteile / Quoten:\n{data.get('market_shares', 'N/A')}\n"
            user_message_content += f"Genre- & Formattrends:\n{data.get('market_genre_trends', 'N/A')}\n"
            user_message_content += f"Plattformtrends:\n{data.get('market_platform_trends', 'N/A')}\n"
            user_message_content += f"Zielgruppendynamiken:\n{data.get('market_target_group_dynamics', 'N/A')}\n"
            user_message_content += f"Gesellschaftliche & technologische Einflüsse:\n{data.get('societal_influence_factors', 'N/A')}\n"
            user_message_content += f"Neue Sehgewohnheiten:\n{data.get('new_viewing_habits', 'N/A')}\n"

            user_message_content += "\n**3. Formatentwicklung**\n"
            user_message_content += f"Titel & Claim: {data.get('format_title_claim', 'N/A')}\n"
            user_message_content += f"Genre, Setting, Zielgruppe: {data.get('format_genre_setting_target', 'N/A')}\n"
            user_message_content += f"Tonalität & visuelles Konzept:\n{data.get('format_tone_visual', 'N/A')}\n"
            user_message_content += f"USP & Zeitgeist:\n{data.get('format_usp_zeitgeist', 'N/A')}\n"
            user_message_content += f"Staffelstruktur oder Episodenaufbau:\n{data.get('format_season_episode_structure', 'N/A')}\n"

            user_message_content += "\n**4. Plattform- & Vermarktungsstrategie**\n"
            user_message_content += f"Primäre Plattform: {data.get('platform_primary', 'N/A')}\n"
            user_message_content += f"Lineare Auswertung: {data.get('platform_linear', 'N/A')}\n"
            user_message_content += f"Digitale Verlängerung: {data.get('platform_digital', 'N/A')}\n"
            user_message_content += f"Internationale Skalierbarkeit: {data.get('platform_international', 'N/A')}\n"
            user_message_content += f"Sponsoring- / Werbeoptionen:\n{data.get('platform_sponsoring', 'N/A')}\n"

            user_message_content += "\n**5. Bewertung & Ausblick**\n"
            user_message_content += f"Erfolgschancen:\n{data.get('evaluation_success', 'N/A')}\n"
            user_message_content += f"Risiken & Lösungen:\n{data.get('evaluation_risks', 'N/A')}\n"
            user_message_content += f"Hinweise zur Pilotphase:\n{data.get('evaluation_pilot', 'N/A')}\n"
            
            user_message_content += "\n**6. Revision & Selbstkontrolle**\n"
            user_message_content += f"Logik geprüft: {'Ja' if 'revision_logic' in data else 'Nein'}\n"
            user_message_content += f"Zahlen & Trends belegt: {'Ja' if 'revision_data_trends' in data else 'Nein'}\n"
            user_message_content += f"Formatierung klar: {'Ja' if 'revision_formatting' in data else 'Nein'}\n"
            user_message_content += f"Alle Abschnitte vollständig: {'Ja' if 'revision_sections_complete' in data else 'Nein'}\n"
            user_message_content += "\n**Generiere nun das vollständige Pitch Paper basierend auf diesen Informationen.**"


        messages.append({"role": "user", "content": user_message_content})

        try:
            if not client.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")

            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages
            )
            response_content = completion.choices[0].message.content
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "response": response_content}).encode('utf-8'))
        except Exception as e:
            # Protokolliere den Fehler detaillierter für Vercel Logs
            print(f"Ein Fehler ist aufgetreten: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))