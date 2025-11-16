# 🤖 Arquitectura del Sistema JoJo - AsisTECH

## 📡 Hardware del Robot

### **Componentes Principales:**

1. **Cerebro 1 - Raspberry Pi 2** (Servidor Central)
   - Aloja la aplicación web (Flask + HTML/CSS/JS)
   - Ejecuta el Broker MQTT (Mosquitto)
   - Maneja la lógica principal del sistema
   - IP fija: `192.168.1.100`

2. **Cerebro 2 - ESP32 (1)** (Control Principal)
   - Controla servomotores MG90S (x4) - Brazo robótico
   - Controla motor L298N - Movimiento
   - Display TFT
   - DFPlayer Mini - Audio
   - Módulo de voz Elechouse V3
   - Conectado al Broker MQTT

3. **Cerebro 3 - ESP32 (2)** (Sensores y Display)
   - Display LCD 16x2
   - Sensor ultrasónico
   - Buzzer
   - Servo de rotación 180°
   - Conectado al Broker MQTT

4. **Cerebro 4 - ESP32-CAM** (Visión)
   - Transmisión de video MJPEG
   - Stream HTTP directo
   - IP: `192.168.1.103`

---

## 🌐 Configuración de Red

```
Red Wi-Fi: JOJO_NET
Password: jojo2025
Router: 192.168.1.1

Dispositivos:
├─ Raspberry Pi 2 (Broker MQTT + Web): 192.168.1.100
├─ ESP32 (1) Control: 192.168.1.101 (auto DHCP)
├─ ESP32 (2) Sensores: 192.168.1.102 (auto DHCP)
└─ ESP32-CAM Video: 192.168.1.103
```

---

## 🔄 Flujo de Comunicación

### **1. Usuario → App Web → ESP32s (Comandos)**

```
Usuario (Navegador)
    ↓ HTTP
App Web (Raspberry Pi:5000)
    ↓ MQTT Publish
Broker MQTT (Raspberry Pi:1883)
    ↓ MQTT Subscribe
ESP32 (1) / ESP32 (2)
    ↓
Hardware (Servos, Motores, etc.)
```

### **2. ESP32s → App Web (Sensores y Estado)**

```
Sensores (Ultrasonido, Batería, etc.)
    ↓
ESP32 (1) / ESP32 (2)
    ↓ MQTT Publish
Broker MQTT (Raspberry Pi:1883)
    ↓ MQTT Subscribe
App Web (Raspberry Pi:5000)
    ↓ WebSocket / Polling
Usuario (Navegador)
```

### **3. ESP32-CAM → Usuario (Video)**

```
ESP32-CAM (192.168.1.103)
    ↓ HTTP Stream (/stream)
Usuario (Navegador)
```

**Nota:** El video NO pasa por el servidor Flask. Conexión directa para menor latencia.

---

## 📊 Estructura de Tópicos MQTT

### **Formato:**
```
jojo/<serial_robot>/<componente>/<accion>
```

### **Tópicos Principales:**

#### **Comandos (Publicados por la App Web):**
```
jojo/CARL-001/movimiento/adelante
jojo/CARL-001/movimiento/atras
jojo/CARL-001/movimiento/izquierda
jojo/CARL-001/movimiento/derecha
jojo/CARL-001/movimiento/parar

jojo/CARL-001/brazo/servo1    # Payload: {"angulo": 90}
jojo/CARL-001/brazo/servo2
jojo/CARL-001/brazo/servo3
jojo/CARL-001/brazo/servo4

jojo/CARL-001/audio/play      # Payload: {"archivo": "recordatorio.mp3"}
jojo/CARL-001/audio/volumen   # Payload: {"nivel": 20}

jojo/CARL-001/voz/activar
jojo/CARL-001/voz/desactivar

jojo/CARL-001/display/mensaje # Payload: {"texto": "Hola"}
```

#### **Estado (Publicados por los ESP32s):**
```
jojo/CARL-001/estado/bateria      # Payload: {"nivel": 85}
jojo/CARL-001/estado/online       # Payload: {"estado": true}
jojo/CARL-001/estado/sensores     # Payload: {"ultrasonico": 25cm}
jojo/CARL-001/estado/temperatura  # Payload: {"cpu": 45}
```

---

## 🛠️ Configuración Actual del Proyecto

### **Variables de Entorno (.env):**
```bash
SECRET_KEY='clave-secreta-para-desarrollo-12345'

# Broker MQTT (Raspberry Pi)
MQTT_BROKER_HOST='192.168.1.100'
MQTT_BROKER_PORT=1883
MQTT_USERNAME=''
MQTT_PASSWORD=''
MQTT_KEEPALIVE=60

# ESP32-CAM
ESP32_CAM_IP='192.168.1.103'
ESP32_CAM_STREAM_URL='http://192.168.1.103/stream'
```

### **Base de Datos - Tabla Robot:**
```python
id: int
name: string (ej. "Carl")
serial_number: string (ej. "CARL-001")
mqtt_topic: string (ej. "jojo/carl-001")
camera_ip: string (ej. "192.168.1.103")
is_active: boolean
is_online: boolean
battery_level: int
last_seen: datetime
user_id: foreign_key
```

---

## 🚀 Próximos Pasos de Implementación

### **Fase 1: Control Básico (Ya implementado)**
- ✅ Interfaz web de control
- ✅ API REST para comandos
- ✅ Cliente MQTT integrado
- ✅ Streaming de video ESP32-CAM

### **Fase 2: Integración con ESP32s**
- [ ] Programar ESP32 (1) con lógica de control
- [ ] Programar ESP32 (2) con sensores
- [ ] Suscribir ESP32s a tópicos MQTT
- [ ] Publicar estado de sensores

### **Fase 3: Funcionalidades Avanzadas**
- [ ] Reconocimiento de voz offline
- [ ] Sistema de recordatorios con DFPlayer
- [ ] Control del brazo robótico 4-DOF
- [ ] Telemetría en tiempo real
- [ ] Mapeado del entorno

---

## 📝 Notas Importantes

1. **Broker MQTT:** Instalar Mosquitto en la Raspberry Pi:
   ```bash
   sudo apt-get update
   sudo apt-get install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   ```

2. **ESP32-CAM:** Usar el ejemplo `CameraWebServer` de Arduino IDE con configuración MJPEG.

3. **IPs Fijas:** Configurar el router para asignar IPs fijas por MAC address.

4. **Seguridad:** En producción, habilitar autenticación MQTT con usuario/contraseña.

---

**Última actualización:** 16 de Noviembre de 2025
