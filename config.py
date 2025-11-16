# proyojo/config.py

import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

class Config:
    """Clase base de configuración."""
    
    # Clave secreta para proteger formularios y sesiones.
    # Es VITAL para la seguridad.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    
    # Configuración de la Base de Datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'jojo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración MQTT (Broker en Raspberry Pi 192.168.1.100)
    MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST') or '192.168.1.100'
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT') or 1883)
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME') or ''
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD') or ''
    MQTT_KEEPALIVE = int(os.environ.get('MQTT_KEEPALIVE') or 60)
    
    # Configuración ESP32-CAM (Streaming directo)
    ESP32_CAM_IP = os.environ.get('ESP32_CAM_IP') or '192.168.1.103'
    ESP32_CAM_STREAM_URL = os.environ.get('ESP32_CAM_STREAM_URL') or 'http://192.168.1.103/stream'