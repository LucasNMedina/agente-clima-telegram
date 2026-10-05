import os
import requests

# Cargar credenciales desde variables de entorno
API_KEY_WEATHER = os.getenv("OPENWEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

#Funcion para obtener el clima
def obtener_clima(ciudad : str, api_key : str):
    URL = "https://api.openweathermap.org/data/2.5/weather"
    parametros = {
        "q" : ciudad,
        "appid" :api_key,
        "units" : "metric",
        "lang" : "es"

    }

    try:
        respuesta = requests.get(URL, params = parametros)
        if respuesta.status_code != 200: #!200 Porque 200 es el código de que esta todo OK.
            print(f"Error HTTP {respuesta.status_code}: {respuesta.json().get('message', 'Error desconocido')}")
            return None
        
        datos = respuesta.json()

        clima_info = {
            "temperatura" : datos["main"]["temp"],
            "sensacion" : datos["main"]["feels_like"],
            "descripcion" : datos["weather"][0]["description"]

        }
        return clima_info
    except requests.RequestException as e:
        print(f"Error de conexión a la API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error en la estructura del JSON devuelto: se esperaba otra clave ({e})")
        return None

#funcion para enviar mensaje
def enviar_mensaje(mensaje : str, token : str, chat_id : str):
    URL = f"https://api.telegram.org/bot{token}/sendMessage"
    datos = {
        "chat_id" : chat_id,
        "text" : mensaje
    }

    respuesta = requests.post(URL, data = datos)
    if respuesta.status_code == 200:
        print("enviado correctamente")
    else:
        print("No se envio")

def mi_bot_clima():
    if not API_KEY_WEATHER or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Falta alguna de las variables de entorno (API_KEY, TELEGRAM_TOKEN o TELEGRAM_CHAT_ID).")
        return

    respuesta_clima = obtener_clima("quilmes", API_KEY_WEATHER)
    if respuesta_clima:
        mensaje_txt = (
            f"☀️ *Reporte del Clima - Quilmes*\n\n"
            f"🌡️ Temperatura: {respuesta_clima['temperatura']}°C\n"
            f"🤔 Sensación térmica: {respuesta_clima['sensacion']}°C\n"
            f"☁️ Estado: {respuesta_clima['descripcion'].capitalize()}"
        )
        enviar_mensaje(mensaje_txt, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        print("Mensaje enviado con éxito.")
    else:
        print("No se pudo obtener el clima.")

if __name__ == "__main__":
    mi_bot_clima()
