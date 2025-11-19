// proyojo/app/static/js/arm_control.js
// Control avanzado del brazo mecánico

class ArmController {
    constructor() {
        this.selectedRobot = null;
        this.leftJoystickActive = false;
        this.rightJoystickActive = false;
        this.gripperClosed = false;
        this.audioActive = false;
        this.audioStream = null;
        
        // Estado del brazo (ángulos en grados 0-180)
        this.armState = {
            base: 90,
            shoulder: 90,
            elbow: 90,
            wrist: 90,
            gripper: 0
        };
        
        this.init();
    }
    
    init() {
        this.setupRobotSelection();
        this.setupLeftJoystick();
        this.setupRightJoystick();
        this.setupControls();
    }
    
    setupRobotSelection() {
        document.querySelectorAll('.robot-card').forEach(card => {
            card.addEventListener('click', () => this.selectRobot(card));
        });
    }
    
    selectRobot(card) {
        document.querySelectorAll('.robot-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        
        this.selectedRobot = {
            id: card.dataset.robotId,
            name: card.dataset.robotName,
            ip: card.dataset.raspberryIp
        };
        
        document.getElementById('selectedRobotInfo').textContent = `Robot seleccionado: ${this.selectedRobot.name}`;
        document.getElementById('selectedRobotInfo').style.color = '#28a745';
        
        // Habilitar controles
        this.enableControls();
        this.updateConnectionStatus(true);
    }
    
    enableControls() {
        document.getElementById('gripperBtn').disabled = false;
        document.getElementById('audioBtn').disabled = false;
        document.getElementById('resetBtn').disabled = false;
    }
    
    updateConnectionStatus(connected) {
        const statusText = document.getElementById('connectionStatus');
        const indicator = document.getElementById('connectionIndicator');
        
        if (connected && this.selectedRobot) {
            statusText.textContent = `Conectado: ${this.selectedRobot.name}`;
            statusText.style.color = '#28a745';
            indicator.style.color = '#28a745';
        } else {
            statusText.textContent = 'Desconectado';
            statusText.style.color = '#dc3545';
            indicator.style.color = '#dc3545';
        }
    }
    
    setupLeftJoystick() {
        const joystick = document.getElementById('leftJoystick');
        const stick = document.getElementById('leftStick');
        
        joystick.addEventListener('mousedown', (e) => this.startJoystick(e, 'left'));
        joystick.addEventListener('touchstart', (e) => this.startJoystick(e, 'left'));
        
        document.addEventListener('mousemove', (e) => this.moveJoystick(e, 'left', joystick, stick));
        document.addEventListener('touchmove', (e) => this.moveJoystick(e, 'left', joystick, stick));
        
        document.addEventListener('mouseup', () => this.stopJoystick('left', stick));
        document.addEventListener('touchend', () => this.stopJoystick('left', stick));
    }
    
    setupRightJoystick() {
        const joystick = document.getElementById('rightJoystick');
        const stick = document.getElementById('rightStick');
        
        joystick.addEventListener('mousedown', (e) => this.startJoystick(e, 'right'));
        joystick.addEventListener('touchstart', (e) => this.startJoystick(e, 'right'));
        
        document.addEventListener('mousemove', (e) => this.moveJoystick(e, 'right', joystick, stick));
        document.addEventListener('touchmove', (e) => this.moveJoystick(e, 'right', joystick, stick));
        
        document.addEventListener('mouseup', () => this.stopJoystick('right', stick));
        document.addEventListener('touchend', () => this.stopJoystick('right', stick));
    }
    
    startJoystick(e, side) {
        if (!this.selectedRobot) return;
        
        if (side === 'left') {
            this.leftJoystickActive = true;
        } else {
            this.rightJoystickActive = true;
        }
    }
    
    moveJoystick(e, side, joystick, stick) {
        const isActive = side === 'left' ? this.leftJoystickActive : this.rightJoystickActive;
        if (!isActive) return;
        
        e.preventDefault();
        const rect = joystick.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        let clientX, clientY;
        if (e.type.includes('touch')) {
            clientX = e.touches[0].clientX - rect.left;
            clientY = e.touches[0].clientY - rect.top;
        } else {
            clientX = e.clientX - rect.left;
            clientY = e.clientY - rect.top;
        }
        
        let deltaX = clientX - centerX;
        let deltaY = clientY - centerY;
        
        // Limitar al radio
        const maxRadius = (rect.width / 2) - 40;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        if (distance > maxRadius) {
            const angle = Math.atan2(deltaY, deltaX);
            deltaX = Math.cos(angle) * maxRadius;
            deltaY = Math.sin(angle) * maxRadius;
        }
        
        stick.style.transform = `translate(calc(-50% + ${deltaX}px), calc(-50% + ${deltaY}px))`;
        
        // Actualizar valores
        if (side === 'left') {
            this.armState.base = Math.round(90 + (deltaX / maxRadius) * 90);
            this.armState.shoulder = Math.round(90 - (deltaY / maxRadius) * 90);
            
            document.getElementById('baseValue').textContent = this.armState.base;
            document.getElementById('shoulderValue').textContent = this.armState.shoulder;
            
            this.sendCommand('base', this.armState.base);
            this.sendCommand('shoulder', this.armState.shoulder);
        } else {
            this.armState.elbow = Math.round(90 + (deltaX / maxRadius) * 90);
            this.armState.wrist = Math.round(90 - (deltaY / maxRadius) * 90);
            
            document.getElementById('elbowValue').textContent = this.armState.elbow;
            document.getElementById('wristValue').textContent = this.armState.wrist;
            
            this.sendCommand('elbow', this.armState.elbow);
            this.sendCommand('wrist', this.armState.wrist);
        }
    }
    
    stopJoystick(side, stick) {
        if (side === 'left') {
            this.leftJoystickActive = false;
        } else {
            this.rightJoystickActive = false;
        }
        stick.style.transform = 'translate(-50%, -50%)';
    }
    
    setupControls() {
        // Gripper
        document.getElementById('gripperBtn').addEventListener('click', () => {
            this.toggleGripper();
        });
        
        // Audio
        document.getElementById('audioBtn').addEventListener('click', () => {
            this.toggleAudio();
        });
        
        // Reset
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetPosition();
        });
    }
    
    toggleGripper() {
        this.gripperClosed = !this.gripperClosed;
        const btn = document.getElementById('gripperBtn');
        
        if (this.gripperClosed) {
            btn.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)';
            document.getElementById('gripperText').textContent = 'Abrir Pinza';
            this.armState.gripper = 180;
        } else {
            btn.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
            document.getElementById('gripperText').textContent = 'Cerrar Pinza';
            this.armState.gripper = 0;
        }
        
        this.sendCommand('gripper', this.armState.gripper);
    }
    
    async toggleAudio() {
        this.audioActive = !this.audioActive;
        const btn = document.getElementById('audioBtn');
        
        if (this.audioActive) {
            try {
                this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                btn.classList.add('active');
                document.getElementById('audioText').textContent = 'Desactivar Audio';
                console.log('Audio activado');
                
                // Aquí se puede implementar el envío de audio
                this.sendAudioToRobot();
            } catch (err) {
                console.error('Error al activar audio:', err);
                alert('No se pudo acceder al micrófono');
                this.audioActive = false;
            }
        } else {
            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop());
                this.audioStream = null;
            }
            btn.classList.remove('active');
            document.getElementById('audioText').textContent = 'Activar Audio';
            console.log('Audio desactivado');
        }
    }
    
    sendAudioToRobot() {
        // Implementación futura: enviar audio por WebSocket o WebRTC
        console.log('Enviando audio al robot:', this.selectedRobot.name);
    }
    
    resetPosition() {
        this.armState = {
            base: 90,
            shoulder: 90,
            elbow: 90,
            wrist: 90,
            gripper: 0
        };
        
        document.getElementById('baseValue').textContent = 90;
        document.getElementById('shoulderValue').textContent = 90;
        document.getElementById('elbowValue').textContent = 90;
        document.getElementById('wristValue').textContent = 90;
        
        // Enviar comandos
        Object.keys(this.armState).forEach(joint => {
            this.sendCommand(joint, this.armState[joint]);
        });
        
        // Reset gripper UI
        this.gripperClosed = false;
        document.getElementById('gripperBtn').style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
        document.getElementById('gripperText').textContent = 'Cerrar Pinza';
    }
    
    sendCommand(joint, value) {
        if (!this.selectedRobot) return;
        
        const topic = `robot/${this.selectedRobot.id}/arm/${joint}`;
        const payload = { value: value };
        
        fetch('/api/mqtt/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                payload: payload
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(`Comando enviado - ${joint}: ${value}°`);
        })
        .catch(err => {
            console.error('Error enviando comando:', err);
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const armController = new ArmController();
});
