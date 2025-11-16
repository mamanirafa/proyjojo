# proyojo/app/mqtt_client.py

import paho.mqtt.client as mqtt
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class MQTTClient:
    """Cliente MQTT singleton para comunicación con los robots."""
    
    def __init__(self):
        self.client = None
        self.connected = False
    
    def init_app(self, app):
        """Inicializa el cliente MQTT con la configuración de Flask."""
        self.client = mqtt.Client(client_id="jojo_web_app", protocol=mqtt.MQTTv311)
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Configurar autenticación si existe
        username = app.config.get('MQTT_USERNAME')
        password = app.config.get('MQTT_PASSWORD')
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Intentar conectar
        try:
            broker = app.config.get('MQTT_BROKER_HOST', 'localhost')
            port = app.config.get('MQTT_BROKER_PORT', 1883)
            keepalive = app.config.get('MQTT_KEEPALIVE', 60)
            
            logger.info(f"Conectando al broker MQTT en {broker}:{port}")
            self.client.connect_async(broker, port, keepalive)
            self.client.loop_start()  # Inicia el loop en segundo plano
            
        except Exception as e:
            logger.error(f"Error al conectar con MQTT broker: {str(e)}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker."""
        if rc == 0:
            self.connected = True
            logger.info("Conectado exitosamente al broker MQTT")
            # Suscribirse a tópicos de estado de robots
            client.subscribe("jojo/+/status")
        else:
            logger.error(f"Falló la conexión al broker MQTT. Código: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta del broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Desconexión inesperada del broker MQTT. Código: {rc}")
        else:
            logger.info("Desconectado del broker MQTT")
    
    def _on_message(self, client, userdata, msg):
        """Callback cuando se recibe un mensaje."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.info(f"Mensaje recibido - Tópico: {topic}, Payload: {payload}")
            
            # Aquí puedes procesar mensajes de estado de los robots
            # Por ejemplo, actualizar la base de datos con el estado
            
        except Exception as e:
            logger.error(f"Error al procesar mensaje MQTT: {str(e)}")
    
    def publish(self, topic, payload, qos=1):
        """
        Publica un mensaje en un tópico MQTT.
        
        Args:
            topic (str): El tópico MQTT
            payload (dict or str): El mensaje a enviar
            qos (int): Quality of Service (0, 1, o 2)
        
        Returns:
            bool: True si se publicó exitosamente
        """
        if not self.connected:
            logger.warning("No conectado al broker MQTT. Intentando enviar de todas formas...")
        
        try:
            # Convertir payload a JSON si es un diccionario
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            result = self.client.publish(topic, payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Mensaje publicado - Tópico: {topic}, Payload: {payload}")
                return True
            else:
                logger.error(f"Error al publicar mensaje. Código: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al publicar mensaje: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta del broker MQTT."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Cliente MQTT desconectado")


# Instancia global del cliente MQTT
mqtt_client = MQTTClient()
