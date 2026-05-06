import requests
import pandas as pd
import os

def descargar():
    url = "TU_URL_DE_LA_API_O_CSV"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # Descargamos los datos
        response = requests.get(url, headers=headers, timeout=30)
        # Suponiendo que es un CSV, si es JSON usa pd.read_json
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        # Guardamos el archivo localmente
        df.to_csv("datos_sonometros.csv", index=False)
        print("Datos actualizados correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    descargar()