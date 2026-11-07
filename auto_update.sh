#!/bin/bash
set -e

# Directorio de trabajo
DIR="$HOME/sonometrosbilbao"

echo "--- 1. Entrando en la carpeta ---"
cd "$DIR" || exit 1

echo "--- 2. Descargando datos nuevos ---"
/usr/bin/python3 "$DIR/script_descarga.py"

echo "--- 3. Subiendo a GitHub ---"
if [ -d "$DIR/.git" ]; then
    /usr/bin/git add datos_sonometros.csv
    
    # Realizar commit solo si hay diferencias detectadas en el CSV
    if ! /usr/bin/git diff --cached --quiet; then
        /usr/bin/git commit -m "Update automático: $(date)"
        /usr/bin/git pull --rebase origin main
        /usr/bin/git push origin main
        echo "--- Datos subidos a GitHub correctamente ---"
    else
        echo "No hay datos nuevos para actualizar en GitHub."
    fi
else
    echo "Error: $DIR no es un repositorio Git válido."
    exit 1
fi

echo "--- ¡PROCESO FINALIZADO CON ÉXITO! ---"
