# proyojo/app/blueprints/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role

# El nombre 'auth_bp' es el que importaremos en __init__.py
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            
            # Actualizar último login
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('¡Has iniciado sesión correctamente!', 'success')
            
            # Redirigir a la página solicitada o dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html', title="Iniciar Sesión")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')
            first_name = request.form.get('first_name', '')
            last_name = request.form.get('last_name', '')
            
            # Validaciones
            if not all([username, email, password, password_confirm]):
                flash('Todos los campos obligatorios deben ser completados.', 'danger')
                return redirect(url_for('auth.register'))
            
            if password != password_confirm:
                flash('Las contraseñas no coinciden.', 'danger')
                return redirect(url_for('auth.register'))
            
            if len(password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está en uso.', 'danger')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(email=email).first():
                flash('El correo electrónico ya está registrado.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Obtener rol de usuario común
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                flash('Error de configuración del sistema. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Crear nuevo usuario
            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            new_user.set_password(password)
            new_user.roles.append(user_role)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'¡Cuenta creada exitosamente! Bienvenido {username}.', 'success')
            
            # Iniciar sesión automáticamente
            login_user(new_user)
            return redirect(url_for('dashboard.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title="Registrarse")


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado la sesión.', 'info')
    return redirect(url_for('auth.login'))