// proyojo/app/static/js/robot_control.js

/**
 * Sistema de control del robot JoJo
 * Maneja la interacción del usuario con los botones y envía comandos a la API
 */

class RobotController {
    constructor(robotId, mqttTopic) {
        this.robotId = robotId;
        this.mqttTopic = mqttTopic;
        this.apiUrl = `/api/robot/${robotId}/command`;
        this.statusUrl = `/api/robot/${robotId}/status`;
        this.isCommandInProgress = false;
        
        this.init();
    }
    
    init() {
        console.log(`Controlador de robot inicializado - ID: ${this.robotId}`);
        this.attachEventListeners();
        this.startStatusPolling();
    }
    
    /**
     * Adjunta event listeners a todos los botones de control
     */
    attachEventListeners() {
        // Botones direccionales
        const directionButtons = document.querySelectorAll('.direction-btn[data-direction]');
        directionButtons.forEach(btn => {
            btn.addEventListener('mousedown', () => this.handleDirectionPress(btn.dataset.direction));
            btn.addEventListener('mouseup', () => this.handleDirectionRelease());
            btn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.handleDirectionPress(btn.dataset.direction);
            });
            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.handleDirectionRelease();
            });
        });
        
        // Botones de acción
        const actionButtons = document.querySelectorAll('.action-btn[data-action]');
        actionButtons.forEach(btn => {
            btn.addEventListener('click', () => this.handleAction(btn.dataset.action));
        });
        
        // Soporte para teclado
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
    }
    
    /**
     * Maneja presión de botón direccional
     */
    async handleDirectionPress(direction) {
        if (this.isCommandInProgress) return;
        
        console.log(`Dirección presionada: ${direction}`);
        await this.sendCommand(direction);
    }
    
    /**
     * Maneja liberación de botón direccional
     */
    async handleDirectionRelease() {
        console.log('Botón liberado - enviando comando de parada');
        await this.sendCommand('stop');
    }
    
    /**
     * Maneja acciones especiales (bocina, luces, etc.)
     */
    async handleAction(action) {
        console.log(`Acción ejecutada: ${action}`);
        
        // Para acciones instantáneas, enviamos el comando directo
        await this.sendCommand(action);
    }
    
    /**
     * Maneja teclas del teclado
     */
    handleKeyDown(e) {
        if (this.isCommandInProgress) return;
        
        const keyMap = {
            'ArrowUp': 'forward',
            'w': 'forward',
            'W': 'forward',
            'ArrowDown': 'backward',
            's': 'backward',
            'S': 'backward',
            'ArrowLeft': 'left',
            'a': 'left',
            'A': 'left',
            'ArrowRight': 'right',
            'd': 'right',
            'D': 'right',
            ' ': 'stop'
        };
        
        const direction = keyMap[e.key];
        if (direction) {
            e.preventDefault();
            this.handleDirectionPress(direction);
        }
    }
    
    /**
     * Maneja liberación de teclas
     */
    handleKeyUp(e) {
        const moveKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'a', 's', 'd', 'W', 'A', 'S', 'D'];
        if (moveKeys.includes(e.key)) {
            e.preventDefault();
            this.handleDirectionRelease();
        }
    }
    
    /**
     * Envía un comando al backend mediante fetch
     */
    async sendCommand(action, value = null) {
        this.isCommandInProgress = true;
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: action,
                    value: value
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                console.log('Comando enviado exitosamente:', data);
                this.showFeedback('success', `Comando "${action}" enviado`);
            } else {
                console.error('Error en la respuesta:', data);
                this.showFeedback('error', data.error || 'Error al enviar comando');
            }
            
        } catch (error) {
            console.error('Error al enviar comando:', error);
            this.showFeedback('error', 'Error de conexión con el servidor');
        } finally {
            // Pequeño delay para evitar spam de comandos
            setTimeout(() => {
                this.isCommandInProgress = false;
            }, 100);
        }
    }
    
    /**
     * Obtiene el estado actual del robot
     */
    async fetchRobotStatus() {
        try {
            const response = await fetch(this.statusUrl);
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.updateStatusDisplay(data.robot);
            }
        } catch (error) {
            console.error('Error al obtener estado del robot:', error);
        }
    }
    
    /**
     * Actualiza la interfaz con el estado del robot
     */
    updateStatusDisplay(robotData) {
        // Actualizar batería
        const batteryElement = document.querySelector('.sensor-item .value');
        if (batteryElement && robotData.battery_level !== undefined) {
            batteryElement.textContent = `${robotData.battery_level}%`;
        }
        
        // Actualizar badge de estado
        const statusBadge = document.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = robotData.is_online ? 
                'status-badge status-online' : 
                'status-badge status-offline';
            statusBadge.innerHTML = robotData.is_online ?
                '<i class="fa-solid fa-circle"></i> En línea' :
                '<i class="fa-solid fa-circle"></i> Desconectado';
        }
    }
    
    /**
     * Inicia el polling periódico del estado del robot
     */
    startStatusPolling() {
        // Obtener estado inmediatamente
        this.fetchRobotStatus();
        
        // Luego cada 5 segundos
        setInterval(() => {
            this.fetchRobotStatus();
        }, 5000);
    }
    
    /**
     * Muestra feedback visual al usuario
     */
    showFeedback(type, message) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Inicializar el controlador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Las variables ROBOT_ID y MQTT_TOPIC se inyectan desde el template
    if (typeof ROBOT_ID !== 'undefined') {
        window.robotController = new RobotController(ROBOT_ID, MQTT_TOPIC);
    }
});

// Agregar estilos para las animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
