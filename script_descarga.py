import pandas as pd
import requests
import ssl
import os

# 1. Saltarse la verificación de certificados
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.bilbao.eus/aytoonline/jsp/opendata/movilidad/od_sonometro_mediciones.jsp?idioma=c&formato=csv"

# 2. EL DISFRAZ: Decimos que somos un navegador normal
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Iniciando descarga de datos...")

try:
    # 3. Intentamos la descarga con el disfraz y sin verificar SSL
    response = requests.get(url, headers=headers, verify=False, timeout=60)
    
    # Si la respuesta es buena (200), guardamos
    if response.status_code == 200:
        with open("datos_sonometros.csv", "wb") as f:
            f.write(response.content)
        print("¡Éxito! Archivo creado.")
    else:
        print(f"Error del servidor: Código {response.status_code}")
        exit(1)

except Exception as e:
    print(f"Error de conexión: {e}")
    exit(1)
