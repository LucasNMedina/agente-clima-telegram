import os
import requests
import telebot
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY_WEATHER = os.getenv("OPENWEATHER_API_KEY")

# 2. Inicializar el bot de Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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

#Funcion para obtener el pronostico
def obtener_pronostico(ciudad : str, api_key : str):
    URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
    parametros = {
        "q" : ciudad,
        "appid" : api_key,
        "units" : "metric",
        "lang" : "es"
    }

    try:
        respuesta = requests.get(URL_FORECAST, params = parametros)
        if respuesta.status_code != 200: #!200 Porque 200 es el código de que esta todo OK.
            print(f"Error HTTP {respuesta.status_code}: {respuesta.json().get('message', 'Error desconocido')}")
            return None
            
        datos = respuesta.json()
        return datos
    except requests.RequestException as e:
        print(f"Error de conexión a la API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error en la estructura del JSON devuelto: se esperaba otra clave ({e})")
        return None


@bot.message_handler(commands=['start', 'hola'])
def iniciar_bot(mensaje):
    bot.reply_to(mensaje, "Hola Lucas, Soy tu agente personal.")

@bot.message_handler(commands=['clima'])
def responder_clima(mensaje):
    # 'mensaje.text' contiene todo lo que escribió el usuario (ej: "/clima quilmes")
    # Para separar el comando de la ciudad, podés usar .split() de Python:
    partes = mensaje.text.split(maxsplit=1)
    
    # Si puso solo "/clima", elegimos una ciudad por defecto (ej: Quilmes)
    if len(partes) == 1:
        ciudad = "quilmes"
    else:
        ciudad = partes[1]  # La ciudad que escribió el usuario

    respuesta_clima = obtener_clima(ciudad, API_KEY_WEATHER)
    if respuesta_clima:
        texto = (
            f"☀️ *Reporte del Clima - {ciudad.capitalize()}*\n\n"
            f"🌡️ Temperatura: {respuesta_clima['temperatura']}°C\n"
            f"🤔 Sensación térmica: {respuesta_clima['sensacion']}°C\n"
            f"☁️ Estado: {respuesta_clima['descripcion'].capitalize()}"
        )
        bot.reply_to(mensaje, texto, parse_mode="Markdown")
    else:
        bot.reply_to(mensaje, f"❌ No pude encontrar información sobre el clima de '{ciudad}'. Revisa el nombre.")

print("Bot escuchando mensajes...")
bot.infinity_polling()