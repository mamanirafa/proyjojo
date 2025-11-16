# ESP32-CAM JoJo AsisTECH - Guía de Programación

## 📋 Requisitos Previos

### Software necesario:
1. **Arduino IDE** (versión 2.0 o superior)
   - Descarga: https://www.arduino.cc/en/software

2. **Soporte para ESP32** en Arduino IDE:
   - Abrir Arduino IDE
   - File → Preferences → Additional Boards Manager URLs
   - Agregar: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Tools → Board → Boards Manager
   - Buscar "esp32" e instalar "esp32 by Espressif Systems"

### Hardware necesario:
- ESP32-CAM AI-Thinker
- Programador FTDI USB-TTL (3.3V) o adaptador USB
- Cables Dupont
- Cable micro USB

## 🔌 Conexión del Programador FTDI

Conecta el FTDI a la ESP32-CAM así:

```
FTDI          ESP32-CAM
-----         ---------
3.3V    →     3.3V
GND     →     GND
TX      →     U0R (RX)
RX      →     U0T (TX)
              GPIO0 → GND (para modo programación)
```

**⚠️ IMPORTANTE:** 
- Conectar GPIO0 a GND ANTES de dar alimentación
- Esto pone la ESP32-CAM en modo programación
- Desconectar GPIO0 de GND después de programar

## 📝 Pasos para Programar

### 1. Abrir el código en Arduino IDE
```
Archivo → Abrir → ESP32_CAM_JoJo/ESP32_CAM_JoJo.ino
```

### 2. Configurar la placa
```
Tools → Board → ESP32 Arduino → AI Thinker ESP32-CAM
Tools → Port → [Seleccionar el puerto COM de tu FTDI]
Tools → Upload Speed → 115200
Tools → Flash Frequency → 80MHz
Tools → Partition Scheme → Huge APP (3MB No OTA)
```

### 3. Cargar el código
1. Conectar GPIO0 a GND
2. Conectar el FTDI al USB
3. Click en "Upload" (flecha →)
4. Esperar a que termine (aparece "Done uploading")
5. **Desconectar GPIO0 de GND**
6. Presionar el botón RST en la ESP32-CAM

### 4. Verificar funcionamiento
1. Abrir Serial Monitor (Tools → Serial Monitor)
2. Configurar a 115200 baudios
3. Presionar RST en la ESP32-CAM
4. Deberías ver:
   ```
   ESP32-CAM JoJo AsisTECH - Iniciando...
   Conectando a WiFi.........
   ¡WiFi conectado!
   Dirección IP: 192.168.1.103
   URL de streaming: http://192.168.1.103/stream
   Servidor de cámara iniciado
   ```

## 🔧 Configuración para otros robots

### Para Tina (192.168.1.104):
Cambiar en el código:
```cpp
IPAddress local_IP(192, 168, 1, 104);  // Cambiar 103 → 104
```

### Para JoJo (192.168.1.105):
Cambiar en el código:
```cpp
IPAddress local_IP(192, 168, 1, 105);  // Cambiar 103 → 105
```

## 🧪 Probar el Streaming

1. **Desde el navegador:**
   ```
   http://192.168.1.103/stream
   ```

2. **Desde la aplicación Flask:**
   - Iniciar sesión
   - Ir a "Mis Robots"
   - Seleccionar "Carl"
   - El video debería aparecer automáticamente

## ❌ Solución de Problemas

### No se conecta a WiFi:
- Verificar que JOJO_NET esté activa
- Verificar contraseña "jojo2025"
- Revisar Serial Monitor para mensajes de error

### No aparece el puerto COM:
- Instalar drivers FTDI: https://ftdichip.com/drivers/vcp-drivers/
- Verificar que el FTDI es 3.3V (NO 5V)

### Error al cargar código:
- Verificar que GPIO0 está conectado a GND
- Intentar con velocidad de carga más baja (57600)
- Presionar y mantener el botón IO0 durante la carga

### Cámara no funciona:
- Verificar conexiones del módulo de cámara
- Asegurarse que el cable ribbon está bien insertado
- Probar con menor calidad (cambiar FRAMESIZE_SVGA a FRAMESIZE_VGA)

### IP diferente a la esperada:
- Verificar configuración del router
- El router podría estar asignando IPs automáticamente
- Revisar Serial Monitor para ver la IP real asignada

## 📚 Recursos Adicionales

- [Documentación ESP32-CAM](https://github.com/espressif/esp32-camera)
- [Ejemplos Arduino ESP32](https://github.com/espressif/arduino-esp32/tree/master/libraries/ESP32/examples)
- [Pinout ESP32-CAM](https://randomnerdtutorials.com/esp32-cam-ai-thinker-pinout/)

## 🎯 Próximos Pasos

Después de programar la cámara:
1. Programar ESP32 #1 (Control de motores)
2. Programar ESP32 #2 (Sensores y display)
3. Configurar broker MQTT en Raspberry Pi
4. Integrar módulos de voz y audio
