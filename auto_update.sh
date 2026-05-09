#!/bin/bash

# Usamos comillas para que los espacios de OneDrive no rompan el comando
echo "--- 1. Entrando en la carpeta ---"
cd "/Users/lourdes/Library/CloudStorage/OneDrive-Personal/Deusto/2025/Primero/Curso-IA/Trabajos/sonometrosbilbao"

echo "--- 2. Descargando datos nuevos ---"
# Ejecutamos python directamente
/usr/bin/python3 script_descarga.py

echo "--- 3. Subiendo a GitHub ---"
# CONFIGURACIÓN DE IDENTIDAD (Añade esto para que el robot no se pierda)
/usr/bin/git config user.name "Lourdes"
/usr/bin/git config user.email "l.llorens@opendeusto.es" 

/usr/bin/git add datos_sonometros.csv
/usr/bin/git commit -m "Update automático: $(date)"
/usr/bin/git push origin main

echo "--- ¡PROCESO FINALIZADO! ---"

