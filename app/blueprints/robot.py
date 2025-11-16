# proyojo/app/blueprints/robot.py

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Robot

robot_bp = Blueprint('robot', __name__)

@robot_bp.route('/robots')
@login_required
def select():
    """Muestra la lista de robots disponibles para el usuario."""
    # Usuarios comunes ven todos los robots públicos
    # Admins y soporte también pueden ver todos
    if current_user.is_admin() or current_user.is_support():
        user_robots = Robot.query.all()
    else:
        user_robots = Robot.query.filter_by(is_public=True).all()
    
    return render_template('robot/select.html', robots=user_robots, title="Robots Disponibles")

@robot_bp.route('/robot/<int:robot_id>/control')
@login_required
def control(robot_id):
    """Página de control de un robot específico."""
    robot = Robot.query.get_or_404(robot_id)
    
    # Verificar permisos: admin/support tienen acceso completo, usuarios comunes solo a robots públicos
    if not (current_user.is_admin() or current_user.is_support() or robot.is_public):
        flash('No tienes permiso para controlar este robot.', 'danger')
        return redirect(url_for('robot.select'))
    
    return render_template('robot/control.html', robot=robot, title=f"Control - {robot.name}")