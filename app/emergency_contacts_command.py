# proyojo/app/commands.py - Agregar comando para crear contactos de emergencia

import click
from flask.cli import with_appcontext
from app import db
from app.models import Contact, User

@click.command('seed-emergency-contacts')
@click.argument('username')
@with_appcontext
def seed_emergency_contacts_command(username):
    """Crear contactos de emergencia predeterminados para un usuario."""
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        click.echo(f'❌ Usuario {username} no encontrado.')
        return
    
    # Contactos de emergencia comunes en México
    emergency_contacts = [
        {
            'name': 'Cruz Roja',
            'phone': '065',
            'relationship': 'emergencia',
            'is_emergency': True,
            'notes': 'Servicio de ambulancias y emergencias médicas'
        },
        {
            'name': 'Policía',
            'phone': '911',
            'relationship': 'emergencia',
            'is_emergency': True,
            'notes': 'Emergencias policiales y seguridad'
        },
        {
            'name': 'Bomberos',
            'phone': '068',
            'relationship': 'emergencia',
            'is_emergency': True,
            'notes': 'Emergencias de incendios y rescate'
        },
        {
            'name': 'Protección Civil',
            'phone': '911',
            'relationship': 'emergencia',
            'is_emergency': True,
            'notes': 'Emergencias y desastres naturales'
        },
        {
            'name': 'Centro de Atención a Emergencias',
            'phone': '911',
            'relationship': 'emergencia',
            'is_emergency': True,
            'notes': 'Número único de emergencias'
        }
    ]
    
    created = 0
    for contact_data in emergency_contacts:
        # Verificar si ya existe
        existing = Contact.query.filter_by(
            user_id=user.id,
            phone=contact_data['phone'],
            name=contact_data['name']
        ).first()
        
        if not existing:
            contact = Contact(
                user_id=user.id,
                **contact_data
            )
            db.session.add(contact)
            created += 1
    
    db.session.commit()
    
    click.echo(f'✅ {created} contactos de emergencia creados para {username}')
    click.echo('📞 Contactos disponibles:')
    for contact in Contact.query.filter_by(user_id=user.id, is_emergency=True).all():
        click.echo(f'   - {contact.name}: {contact.phone}')
