import pandas as pd
import requests
import ssl
import os

# 1. Saltarse la verificación de certificados (Crucial para servidores)
ssl._create_default_https_context = ssl._create_unverified_context

# 2. La URL de descarga (asegúrate de que sea la correcta del CSV)
url = "https://www.bilbao.eus/aytoonline/jsp/opendata/movilidad/od_sonometro_mediciones.jsp?idioma=c&formato=csv"

print("Iniciando descarga de datos...")

try:
    # 3. Descarga con verificación desactivada
    response = requests.get(url, verify=False, timeout=60)
    
    # 4. Guardar el archivo
    with open("datos_sonometros.csv", "wb") as f:
        f.write(response.content)
    
    print("¡Archivo creado con éxito en el servidor!")
    
    # Verificación extra para el log
    if os.path.exists("datos_sonometros.csv"):
        print("Confirmado: El archivo existe físicamente.")
    else:
        print("Error: El archivo no se ha creado.")

except Exception as e:
    print(f"Error durante la descarga: {e}")
    exit(1)
