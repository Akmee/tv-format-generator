#!/bin/bash

# Ersetze den Platzhalter in der index.html mit dem Key
sed "s|%%OPENAI_API_KEY%%|${OPENAI_API_KEY}|g" index.html > index-temp.html

# Ersetze die alte index.html mit der neuen
mv index-temp.html index.html

echo "Build abgeschlossen: API Key wurde in index.html injiziert."