# proyojo/app/blueprints/dashboard.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Reminder
from datetime import datetime

# El nombre 'dashboard_bp' es el que importaremos
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Obtener estadísticas del usuario
    from app.models import Robot
    
    # Robots disponibles según el rol del usuario
    if current_user.is_admin() or current_user.is_support():
        user_robots = Robot.query.all()
    else:
        user_robots = Robot.query.filter_by(is_public=True).all()
    
    active_robots = [r for r in user_robots if r.is_active]
    online_robots = [r for r in user_robots if r.is_online]
    
    # Recordatorios próximos (siguientes 24 horas)
    from datetime import timedelta
    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)
    
    upcoming_reminders = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
        Reminder.is_completed == False,
        Reminder.reminder_time >= now,
        Reminder.reminder_time <= tomorrow
    ).order_by(Reminder.reminder_time).limit(5).all()
    
    # Recordatorios vencidos
    overdue_reminders = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
        Reminder.is_completed == False,
        Reminder.reminder_time < now
    ).count()
    
    return render_template('dashboard/index.html', 
                         title="Dashboard",
                         user=current_user,
                         robots=user_robots,
                         active_robots_count=len(active_robots),
                         online_robots_count=len(online_robots),
                         upcoming_reminders=upcoming_reminders,
                         overdue_reminders_count=overdue_reminders)


@dashboard_bp.route('/recordatorios')
@login_required
def recordatorios():
    """Página de gestión de recordatorios."""
    # Obtener todos los recordatorios del usuario ordenados por fecha
    reminders = Reminder.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(Reminder.reminder_time).all()
    
    # Separar recordatorios pendientes y completados
    pending = [r for r in reminders if not r.is_completed]
    completed = [r for r in reminders if r.is_completed]
    
    return render_template('dashboard/recordatorios.html', 
                         title="Mis Recordatorios",
                         pending_reminders=pending,
                         completed_reminders=completed)


@dashboard_bp.route('/recordatorio/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_recordatorio():
    """Crear un nuevo recordatorio."""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.form.get('title')
            description = request.form.get('description', '')
            date = request.form.get('date')
            time = request.form.get('time')
            category = request.form.get('category', 'otro')
            repeat = request.form.get('repeat', 'once')
            robot_notification = request.form.get('robot_notification') == 'on'
            
            # Validar campos requeridos
            if not title or not date or not time:
                flash('Título, fecha y hora son requeridos.', 'danger')
                return redirect(url_for('dashboard.nuevo_recordatorio'))
            
            # Combinar fecha y hora
            reminder_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            # Verificar que la fecha no sea en el pasado
            if reminder_datetime < datetime.utcnow():
                flash('La fecha y hora deben ser futuras.', 'danger')
                return redirect(url_for('dashboard.nuevo_recordatorio'))
            
            # Crear recordatorio
            new_reminder = Reminder(
                title=title,
                description=description,
                reminder_time=reminder_datetime,
                category=category,
                repeat=repeat,
                robot_notification=robot_notification,
                user_id=current_user.id
            )
            
            db.session.add(new_reminder)
            db.session.commit()
            
            flash(f'Recordatorio "{title}" creado exitosamente.', 'success')
            return redirect(url_for('dashboard.recordatorios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear recordatorio: {str(e)}', 'danger')
            return redirect(url_for('dashboard.nuevo_recordatorio'))
    
    return render_template('dashboard/nuevo_recordatorio.html', title="Nuevo Recordatorio")


@dashboard_bp.route('/recordatorio/<int:reminder_id>/completar', methods=['POST'])
@login_required
def completar_recordatorio(reminder_id):
    """Marcar un recordatorio como completado."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Verificar que pertenece al usuario
    if reminder.user_id != current_user.id:
        flash('No tienes permiso para esta acción.', 'danger')
        return redirect(url_for('dashboard.recordatorios'))
    
    reminder.is_completed = True
    reminder.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Recordatorio "{reminder.title}" marcado como completado.', 'success')
    return redirect(url_for('dashboard.recordatorios'))


@dashboard_bp.route('/recordatorio/<int:reminder_id>/eliminar', methods=['POST'])
@login_required
def eliminar_recordatorio(reminder_id):
    """Eliminar un recordatorio."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Verificar que pertenece al usuario
    if reminder.user_id != current_user.id:
        flash('No tienes permiso para esta acción.', 'danger')
        return redirect(url_for('dashboard.recordatorios'))
    
    title = reminder.title
    db.session.delete(reminder)
    db.session.commit()
    
    flash(f'Recordatorio "{title}" eliminado.', 'info')
    return redirect(url_for('dashboard.recordatorios'))


@dashboard_bp.route('/mapeado')
@login_required
def mapeado():
    """Página de mapeado del hogar."""
    from app.models import Robot
    
    # Obtener robots disponibles según el rol del usuario
    if current_user.is_admin() or current_user.is_support():
        user_robots = Robot.query.all()
    else:
        user_robots = Robot.query.filter_by(is_public=True).all()
    
    return render_template('dashboard/mapeado.html', 
                         title="Mapeado del Hogar",
                         robots=user_robots)

@dashboard_bp.route('/llamadas')
@login_required
def llamadas():
    """Página de videollamadas con los robots."""
    from app.models import Robot
    
    # Obtener robots disponibles según el rol del usuario
    if current_user.is_admin() or current_user.is_support():
        user_robots = Robot.query.all()
    else:
        user_robots = Robot.query.filter_by(is_public=True).all()
    
    return render_template('dashboard/llamadas.html',
                         title="Videollamadas",
                         robots=user_robots)

@dashboard_bp.route('/brazo')
@login_required
def brazo():
    """Página de control del brazo mecánico."""
    from app.models import Robot
    
    # Obtener robots disponibles según el rol del usuario
    if current_user.is_admin() or current_user.is_support():
        user_robots = Robot.query.all()
    else:
        user_robots = Robot.query.filter_by(is_public=True).all()
    
    return render_template('dashboard/brazo.html',
                         title="Control de Brazo",
                         robots=user_robots)

@dashboard_bp.route('/contactos')
@login_required
def contactos():
    """Página de gestión de contactos."""
    from app.models import Contact
    
    # Obtener todos los contactos del usuario
    all_contacts = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.name).all()
    
    # Separar por categorías
    emergency_contacts = [c for c in all_contacts if c.is_emergency]
    family_contacts = [c for c in all_contacts if c.relationship == 'familia']
    friends_contacts = [c for c in all_contacts if c.relationship == 'amigo']
    medical_contacts = [c for c in all_contacts if c.relationship == 'medico']
    other_contacts = [c for c in all_contacts if c.relationship not in ['familia', 'amigo', 'medico'] and not c.is_emergency]
    
    return render_template('dashboard/contactos.html',
                         title="Agenda de Contactos",
                         all_contacts=all_contacts,
                         emergency_contacts=emergency_contacts,
                         family_contacts=family_contacts,
                         friends_contacts=friends_contacts,
                         medical_contacts=medical_contacts,
                         other_contacts=other_contacts)

@dashboard_bp.route('/contactos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_contacto():
    """Crear un nuevo contacto."""
    from app.models import Contact
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        relationship = request.form.get('relationship')
        is_emergency = request.form.get('is_emergency') == 'on'
        is_favorite = request.form.get('is_favorite') == 'on'
        notes = request.form.get('notes')
        
        # Validación básica
        if not name or not phone:
            flash('El nombre y teléfono son obligatorios.', 'danger')
            return redirect(url_for('dashboard.nuevo_contacto'))
        
        # Crear contacto
        new_contact = Contact(
            name=name,
            phone=phone,
            email=email,
            address=address,
            relationship=relationship,
            is_emergency=is_emergency,
            is_favorite=is_favorite,
            notes=notes,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_contact)
            db.session.commit()
            flash(f'Contacto {name} agregado correctamente.', 'success')
            return redirect(url_for('dashboard.contactos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el contacto: {str(e)}', 'danger')
            return redirect(url_for('dashboard.nuevo_contacto'))
    
    return render_template('dashboard/nuevo_contacto.html',
                         title="Nuevo Contacto")

@dashboard_bp.route('/contactos/<int:contact_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_contacto(contact_id):
    """Editar un contacto existente."""
    from app.models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    
    # Verificar que el contacto pertenece al usuario
    if contact.user_id != current_user.id:
        flash('No tienes permiso para editar este contacto.', 'danger')
        return redirect(url_for('dashboard.contactos'))
    
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.phone = request.form.get('phone')
        contact.email = request.form.get('email')
        contact.address = request.form.get('address')
        contact.relationship = request.form.get('relationship')
        contact.is_emergency = request.form.get('is_emergency') == 'on'
        contact.is_favorite = request.form.get('is_favorite') == 'on'
        contact.notes = request.form.get('notes')
        
        try:
            db.session.commit()
            flash(f'Contacto {contact.name} actualizado correctamente.', 'success')
            return redirect(url_for('dashboard.contactos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el contacto: {str(e)}', 'danger')
    
    return render_template('dashboard/editar_contacto.html',
                         title=f"Editar {contact.name}",
                         contact=contact)

@dashboard_bp.route('/contactos/<int:contact_id>/eliminar', methods=['POST'])
@login_required
def eliminar_contacto(contact_id):
    """Eliminar un contacto."""
    from app.models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    
    # Verificar que el contacto pertenece al usuario
    if contact.user_id != current_user.id:
        flash('No tienes permiso para eliminar este contacto.', 'danger')
        return redirect(url_for('dashboard.contactos'))
    
    name = contact.name
    try:
        db.session.delete(contact)
        db.session.commit()
        flash(f'Contacto {name} eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el contacto: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.contactos'))

@dashboard_bp.route('/contactos/<int:contact_id>/llamar', methods=['POST'])
@login_required
def llamar_contacto(contact_id):
    """Iniciar llamada a un contacto."""
    from app.models import Contact, Robot
    
    contact = Contact.query.get_or_404(contact_id)
    
    # Verificar que el contacto pertenece al usuario
    if contact.user_id != current_user.id:
        flash('No tienes permiso para llamar a este contacto.', 'danger')
        return redirect(url_for('dashboard.contactos'))
    
    robot_id = request.form.get('robot_id')
    
    if not robot_id:
        flash('Debes seleccionar un robot para realizar la llamada.', 'warning')
        return redirect(url_for('dashboard.contactos'))
    
    robot = Robot.query.get(robot_id)
    
    if not robot:
        flash('Robot no encontrado.', 'danger')
        return redirect(url_for('dashboard.contactos'))
    
    # Enviar comando MQTT para llamar
    from app.mqtt_client import mqtt_client
    topic = f'robot/{robot.id}/call'
    payload = {
        'action': 'dial',
        'phone': contact.phone,
        'name': contact.name
    }
    
    mqtt_client.publish(topic, payload)
    
    # Actualizar última llamada
    contact.last_call = datetime.utcnow()
    db.session.commit()
    
    flash(f'Llamando a {contact.name} ({contact.formatted_phone}) desde {robot.name}...', 'success')
    return redirect(url_for('dashboard.contactos'))