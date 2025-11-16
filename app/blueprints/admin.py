# proyojo/app/blueprints/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Role, Robot
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para requerir rol de admin o support."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin() or current_user.is_support()):
            flash('No tienes permiso para acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Panel de administración principal."""
    # Estadísticas generales
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_robots = Robot.query.count()
    public_robots = Robot.query.filter_by(is_public=True).count()
    
    # Usuarios recientes
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         title="Panel de Administración",
                         total_users=total_users,
                         active_users=active_users,
                         total_robots=total_robots,
                         public_robots=public_robots,
                         recent_users=recent_users)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Listado de usuarios."""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', 
                         title="Gestión de Usuarios",
                         users=all_users)

@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Detalle de un usuario."""
    user = User.query.get_or_404(user_id)
    all_roles = Role.query.all()
    return render_template('admin/user_detail.html',
                         title=f"Usuario: {user.username}",
                         user=user,
                         all_roles=all_roles)

@admin_bp.route('/user/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Activar/desactivar un usuario."""
    user = User.query.get_or_404(user_id)
    
    # No permitir que el admin se desactive a sí mismo
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "activado" if user.is_active else "desactivado"
    flash(f'Usuario {user.username} {status} correctamente.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/update_role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Actualizar los roles de un usuario."""
    # Solo admins pueden cambiar roles
    if not current_user.is_admin():
        flash('Solo los administradores pueden cambiar roles.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir que el admin cambie sus propios roles
    if user.id == current_user.id:
        flash('No puedes modificar tus propios roles.', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Obtener roles seleccionados del formulario
    selected_role_ids = request.form.getlist('roles')
    
    if not selected_role_ids:
        flash('Debes seleccionar al menos un rol.', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Actualizar roles
    new_roles = Role.query.filter(Role.id.in_(selected_role_ids)).all()
    user.roles = new_roles
    db.session.commit()
    
    flash(f'Roles de {user.username} actualizados correctamente.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Eliminar un usuario (solo admin)."""
    # Solo admins pueden eliminar usuarios
    if not current_user.is_admin():
        flash('Solo los administradores pueden eliminar usuarios.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir que el admin se elimine a sí mismo
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'warning')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuario {username} eliminado correctamente.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/robots')
@login_required
@admin_required
def robots():
    """Gestión de robots."""
    all_robots = Robot.query.all()
    return render_template('admin/robots.html',
                         title="Gestión de Robots",
                         robots=all_robots)

@admin_bp.route('/robot/<int:robot_id>/toggle_public', methods=['POST'])
@login_required
@admin_required
def toggle_robot_public(robot_id):
    """Hacer un robot público o privado."""
    robot = Robot.query.get_or_404(robot_id)
    
    robot.is_public = not robot.is_public
    db.session.commit()
    
    status = "público" if robot.is_public else "privado"
    flash(f'Robot {robot.name} ahora es {status}.', 'success')
    return redirect(url_for('admin.robots'))

@admin_bp.route('/config')
@login_required
@admin_required
def config():
    """Panel de configuración del sistema."""
    return render_template('admin/config.html',
                         title="Configuración del Sistema")
