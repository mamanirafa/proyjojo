/*
 * ESP32-CAM JoJo AsisTECH - Streaming de Video
 * Configuración para Robot Carl (192.168.1.103)
 * 
 * Hardware: ESP32-CAM AI-Thinker
 * Modelo de cámara: OV2640
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// Configuración de red JOJO_NET
const char* ssid = "JOJO_NET";
const char* password = "jojo2025";

// IP estática para Carl
IPAddress local_IP(192, 168, 1, 103);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// Pin definition for CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

httpd_handle_t stream_httpd = NULL;

// Handlers
static esp_err_t stream_handler(httpd_req_t *req){
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;
    char * part_buf[64];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
    if(res != ESP_OK){
        return res;
    }

    while(true){
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            res = ESP_FAIL;
        } else {
            if(fb->format != PIXFORMAT_JPEG){
                bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
                esp_camera_fb_return(fb);
                fb = NULL;
                if(!jpeg_converted){
                    Serial.println("JPEG compression failed");
                    res = ESP_FAIL;
                }
            } else {
                _jpg_buf_len = fb->len;
                _jpg_buf = fb->buf;
            }
        }
        if(res == ESP_OK){
            size_t hlen = snprintf((char *)part_buf, 64, "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
            res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
        }
        if(res == ESP_OK){
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
        }
        if(res == ESP_OK){
            res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 13);
        }
        if(fb){
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if(_jpg_buf){
            free(_jpg_buf);
            _jpg_buf = NULL;
        }
        if(res != ESP_OK){
            break;
        }
    }
    return res;
}

static esp_err_t index_handler(httpd_req_t *req){
    const char* html = "<html><head><title>ESP32-CAM JoJo</title></head>"
                       "<body><h1>ESP32-CAM Carl - JoJo AsisTECH</h1>"
                       "<p>IP: 192.168.1.103</p>"
                       "<p><a href='/stream'>Ver Stream de Video</a></p>"
                       "</body></html>";
    return httpd_resp_send(req, html, strlen(html));
}

void startCameraServer(){
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_uri_t index_uri = {
        .uri       = "/",
        .method    = HTTP_GET,
        .handler   = index_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &index_uri);
        httpd_register_uri_handler(stream_httpd, &stream_uri);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n\nESP32-CAM JoJo AsisTECH - Iniciando...");

    // Configuración de la cámara
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    
    // Configuración de calidad
    if(psramFound()){
        config.frame_size = FRAMESIZE_SVGA;  // 800x600
        config.jpeg_quality = 10;            // 0-63 menor es mejor calidad
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_VGA;   // 640x480
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    // Inicialización de la cámara
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Error al inicializar cámara: 0x%x\n", err);
        return;
    }

    sensor_t * s = esp_camera_sensor_get();
    // Ajustes de imagen
    s->set_brightness(s, 0);     // -2 a 2
    s->set_contrast(s, 0);       // -2 a 2
    s->set_saturation(s, 0);     // -2 a 2
    s->set_special_effect(s, 0); // 0 = Normal
    s->set_whitebal(s, 1);       // 0 = Desactivar, 1 = Activar
    s->set_awb_gain(s, 1);       // 0 = Desactivar, 1 = Activar
    s->set_wb_mode(s, 0);        // 0 = Auto
    s->set_exposure_ctrl(s, 1);  // 0 = Desactivar, 1 = Activar
    s->set_aec2(s, 0);           // 0 = Desactivar, 1 = Activar
    s->set_ae_level(s, 0);       // -2 a 2
    s->set_aec_value(s, 300);    // 0 a 1200
    s->set_gain_ctrl(s, 1);      // 0 = Desactivar, 1 = Activar
    s->set_agc_gain(s, 0);       // 0 a 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 a 6
    s->set_bpc(s, 0);            // 0 = Desactivar, 1 = Activar
    s->set_wpc(s, 1);            // 0 = Desactivar, 1 = Activar
    s->set_raw_gma(s, 1);        // 0 = Desactivar, 1 = Activar
    s->set_lenc(s, 1);           // 0 = Desactivar, 1 = Activar
    s->set_hmirror(s, 0);        // 0 = Desactivar, 1 = Activar
    s->set_vflip(s, 0);          // 0 = Desactivar, 1 = Activar
    s->set_dcw(s, 1);            // 0 = Desactivar, 1 = Activar
    s->set_colorbar(s, 0);       // 0 = Desactivar, 1 = Activar

    // Configurar IP estática
    if (!WiFi.config(local_IP, gateway, subnet)) {
        Serial.println("Fallo en configuración de IP estática");
    }

    // Conectar a WiFi
    WiFi.begin(ssid, password);
    Serial.print("Conectando a WiFi");
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if(WiFi.status() == WL_CONNECTED){
        Serial.println("\n¡WiFi conectado!");
        Serial.print("Dirección IP: ");
        Serial.println(WiFi.localIP());
        Serial.print("URL de streaming: http://");
        Serial.print(WiFi.localIP());
        Serial.println("/stream");
        
        // Iniciar servidor de cámara
        startCameraServer();
        Serial.println("Servidor de cámara iniciado");
    } else {
        Serial.println("\nError: No se pudo conectar a WiFi");
    }
}

void loop() {
    // El servidor maneja las peticiones automáticamente
    delay(10000);
    
    // Imprimir estado cada 10 segundos
    if(WiFi.status() == WL_CONNECTED){
        Serial.print("Estado: Conectado | IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("Estado: Desconectado - Reintentando...");
        WiFi.reconnect();
    }
}
