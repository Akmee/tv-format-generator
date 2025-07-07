#!/bin/bash

# Dieses Skript wird von Vercel während des Build-Prozesses ausgeführt.

# 1. Ersetze den Platzhalter in der HTML-Datei mit dem echten API-Key,
#    der als Umgebungsvariable in Vercel gespeichert ist.
#    WARNUNG: Dies schreibt den Key in die HTML-Datei, die Vercel bereitstellt.
#    Der Key ist NICHT im Git-Repository sichtbar.
sed "s|%%OPENAI_API_KEY%%|${OPENAI_API_KEY}|g" index.html > vercel-build-output.html

# 2. Überschreibe die originale index.html mit der neuen Datei, die den Key enthält.
#    Vercel wird dann diese Datei bereitstellen.
mv vercel-build-output.html index.html

echo "Build abgeschlossen: OpenAI API Key wurde in index.html injiziert."