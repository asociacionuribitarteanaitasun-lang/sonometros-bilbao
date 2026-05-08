#!/bin/bash

# Usamos comillas para que los espacios de OneDrive no rompan el comando
echo "--- 1. Entrando en la carpeta ---"
cd "/Users/lourdes/Library/CloudStorage/OneDrive-Personal/Deusto/2025/Primero/Curso-IA/Trabajos/sonometrosbilbao"

echo "--- 2. Descargando datos nuevos ---"
# Ejecutamos python directamente
/usr/bin/python3 script_descarga.py

echo "--- 3. Subiendo a GitHub ---"
/usr/bin/git add datos_sonometros.csv
/usr/bin/git commit -m "Update automático: $(date)"
/usr/bin/git push origin main

echo "--- ¡PROCESO FINALIZADO! ---"