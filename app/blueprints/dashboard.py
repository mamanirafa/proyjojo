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