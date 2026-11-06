#!/bin/bash

# 1. Entrando en la carpeta
echo "--- 1. Entrando en la carpeta ---"
cd "/Users/lourdes/Library/CloudStorage/OneDrive-Personal/Deusto/2025/Primero/Curso-IA/Trabajos/sonometrosbilbao" || exit 1

# 2. Descargando datos nuevos
echo "--- 2. Descargando datos nuevos ---"
# Ejecutamos python y guardamos su resultado en una variable
SALIDA_PYTHON=$(/usr/bin/python3 script_descarga.py 2>&1)
echo "$SALIDA_PYTHON"

# SI EN EL TEXTO DICE "Error del servidor", DETENEMOS EL SCRIPT AQUÍ
if echo "$SALIDA_PYTHON" | grep -q "Error del servidor"; then
    echo "❌ Descarga fallida debido al servidor de Bilbao. Abortando subida a GitHub."
    exit 1
fi

# 3. Subiendo a GitHub
echo "--- 3. Subiendo a GitHub ---"
/usr/bin/git config user.name "Lourdes"
/usr/bin/git config user.email "l.llorens@opendeusto.es" 

/usr/bin/git add datos_sonometros.csv

# Comprobamos si realmente hay cambios que subir para evitar el mensaje molesto de Git
if /usr/bin/git diff-index --quiet HEAD --; then
    echo "ℹ️ No hay datos nuevos que actualizar (el archivo es idéntico al de GitHub)."
else
    /usr/bin/git commit -m "Update automático: $(date)"
    /usr/bin/git push origin main
    echo "--- ¡PROCESO FINALIZADO CON ÉXITO! ---"
fi
