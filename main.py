# main.py
import requests
import time
import os
from datetime import datetime

# === CONFIGURACIÓN desde variables de entorno (más seguro) ===
STREAM_URL = os.getenv("STREAM_URL", "https://cdn.instream.audio/stream/radiodelaciudad")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "5493794335828")  # Cambia por tu número
API_KEY = os.getenv("API_KEY", "9208867")  # Tu API Key de CallMeBot
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # En segundos

# Estado inicial
last_status_online = None

def send_whatsapp_alert(message):
    """Envía un mensaje por WhatsApp usando CallMeBot"""
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={message}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "File sent" in response.text:
            print("✅ WhatsApp enviado correctamente.")
        else:
            print(f"⚠ WhatsApp falló. Código: {response.status_code}, Respuesta: {response.text}")
    except Exception as e:
        print("⚠ Error al enviar WhatsApp:", e)

def check_stream():
    """Verifica el estado del stream"""
    global last_status_online
    try:
        # Usamos HEAD para solo verificar el encabezado (más rápido y ligero)
        response = requests.head(STREAM_URL, timeout=10)
        is_online = response.status_code == 200
        current_time = datetime.now().strftime("%H:%M:%S")

        if is_online:
            print(f"✅ [{current_time}] Streaming en línea (HTTP {response.status_code}).")
            if last_status_online is False:
                msg = f"🟢 *¡Radio de Vuelta al Aire!* 📻\n\n📻 *Radio de la Ciudad*\n🕒 {current_time}"
                send_whatsapp_alert(msg)
            last_status_online = True
        else:
            print(f"🔴 [{current_time}] Fuera de línea (HTTP {response.status_code}).")
            if last_status_online in [True, None]:
                msg = f"🔴 *ALERTA: Radio Fuera de Aire* 📻\n\n📻 *Radio de la Ciudad*\n🕒 {current_time}\n🔗 {STREAM_URL}"
                send_whatsapp_alert(msg)
            last_status_online = False

    except requests.exceptions.RequestException as e:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"❌ [{current_time}] Error de conexión: {e}")
        if last_status_online in [True, None]:
            msg = f"🔴 *ERROR de conexión* 📻\n\n🕒 {current_time}\n🔧 {str(e)[:100]}..."
            send_whatsapp_alert(msg)
        last_status_online = False

# === BUCLE PRINCIPAL ===
if __name__ == '__main__':
    print("🚀 Iniciando monitor de stream...")
    print(f"📡 Monitoreando: {STREAM_URL}")
    print(f"🔔 Alertas a: +{PHONE_NUMBER}")
    print(f"⏱️ Intervalo: {CHECK_INTERVAL} segundos")
    print("-" * 50)

    while True:
        check_stream()
        time.sleep(CHECK_INTERVAL)