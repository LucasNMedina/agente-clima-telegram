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
        lista_pronosticos = []
        for item in datos["list"][:4]:
            hora = item["dt_txt"].split(" ")[1][:5]  # Extrae solo 'HH:MM'
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
    
            lista_pronosticos.append({
                "hora": hora,
                "temperatura": temp,
                "descripcion": desc
            })
        return lista_pronosticos
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

@bot.message_handler(commands=['pronostico'])
def responder_pronostico(mensaje):
    partes = mensaje.text.split(maxsplit=1)
    if len(partes) == 1:
        ciudad = "quilmes"
    else:
        ciudad = partes[1]

    pronosticos = obtener_pronostico(ciudad, API_KEY_WEATHER)
    
    if pronosticos:
        texto = f"📅 *Pronóstico para las próximas horas en {ciudad.capitalize()}*\n\n"
        # Iteramos sobre los 4 reportes de la lista
        for p in pronosticos:
            texto += f"⏰ *{p['hora']} hs* ➔ {p['temperatura']}°C, {p['descripcion'].capitalize()}\n"
        
        bot.reply_to(mensaje, texto, parse_mode="Markdown")
    else:
        bot.reply_to(mensaje, f"❌ No pude encontrar el pronóstico para '{ciudad}'. Revisá el nombre.")

print("Bot escuchando mensajes...")
bot.infinity_polling()