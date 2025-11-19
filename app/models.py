# proyojo/app/models.py

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
check_password_hash
from flask_login import UserMixin # <-- 1. Importar UserMixin

# Tabla de asociación para la relación Muchos a Muchos entre User y Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relación con Role
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    
    # Relación con Robot (un usuario puede tener varios robots)
    robots = db.relationship('Robot', backref='owner', lazy=True)
    
    # Relación con Reminder (un usuario puede tener varios recordatorios)
    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def has_role(self, role_name):
        """Verifica si el usuario tiene un rol específico."""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.has_role('admin')
    
    def is_support(self):
        """Verifica si el usuario es soporte."""
        return self.has_role('support') or self.has_role('admin')

    def set_password(self, password):
        """Crea un hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica el hash de la contraseña."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Robot(db.Model):
    """Modelo para los robots JoJo - Compartido entre usuarios."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    mqtt_topic = db.Column(db.String(200), nullable=False)
    camera_ip = db.Column(db.String(50))  # IP de la ESP32-CAM
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)
    battery_level = db.Column(db.Integer, default=100)
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key al usuario creador (solo para tracking)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Indica si es un robot público (disponible para todos)
    is_public = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Robot {self.name} ({self.serial_number})>'
    
    @property
    def camera_stream_url(self):
        """URL del stream de video de la ESP32-CAM."""
        if self.camera_ip:
            return f'http://{self.camera_ip}/stream'
        return None


class Reminder(db.Model):
    """Modelo para recordatorios del usuario."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50))  # 'medicina', 'cita', 'actividad', 'otro'
    is_completed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    repeat = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly', 'once'
    robot_notification = db.Column(db.Boolean, default=True)  # Notificar vía robot
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign Key al usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Reminder {self.title} - {self.reminder_time}>'
    
    @property
    def is_overdue(self):
        """Verifica si el recordatorio está vencido."""
        if self.is_completed:
            return False
        return datetime.utcnow() > self.reminder_time
    
    @property
    def time_until(self):
        """Tiempo hasta el recordatorio en formato legible."""
        if self.is_completed:
            return "Completado"
        
        delta = self.reminder_time - datetime.utcnow()
        
        if delta.total_seconds() < 0:
            return "Vencido"
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"En {days} día{'s' if days > 1 else ''}"
        elif hours > 0:
            return f"En {hours} hora{'s' if hours > 1 else ''}"
        elif minutes > 0:
            return f"En {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "Ahora"


class Contact(db.Model):
    """Modelo para contactos y agenda telefónica del usuario."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    
    # Relación del contacto
    relationship = db.Column(db.String(50))  # 'familia', 'amigo', 'medico', 'emergencia', 'otro'
    
    # Indicador de contacto de emergencia
    is_emergency = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Información adicional
    notes = db.Column(db.Text)
    photo_url = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_call = db.Column(db.DateTime)
    
    # Foreign Key al usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Contact {self.name} - {self.phone}>'
    
    @property
    def relationship_icon(self):
        """Retorna el icono de FontAwesome según la relación."""
        icons = {
            'familia': 'fa-users',
            'amigo': 'fa-user-friends',
            'medico': 'fa-user-md',
            'emergencia': 'fa-ambulance',
            'otro': 'fa-user'
        }
        return icons.get(self.relationship, 'fa-user')
    
    @property
    def relationship_color(self):
        """Retorna el color según la relación."""
        colors = {
            'familia': '#813772',
            'amigo': '#17a2b8',
            'medico': '#28a745',
            'emergencia': '#dc3545',
            'otro': '#6c757d'
        }
        return colors.get(self.relationship, '#6c757d')
    
    @property
    def formatted_phone(self):
        """Formatea el número de teléfono."""
        # Eliminar caracteres no numéricos
        digits = ''.join(filter(str.isdigit, self.phone))
        
        # Formato para números de 10 dígitos (XXX) XXX-XXXX
        if len(digits) == 10:
            return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
        return self.phone