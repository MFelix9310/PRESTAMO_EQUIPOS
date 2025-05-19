"""
Script para configurar automáticamente la base de datos en Vercel.
"""

import os
import django
from django.core.management import call_command
from django.conf import settings

def setup_database():
    # Configurar la base de datos
    if 'DATABASE_URL' in os.environ:
        # Si estamos en Vercel, usar la URL de la base de datos proporcionada
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['DATABASE_URL'].split('/')[-1],
            'USER': os.environ['DATABASE_URL'].split('://')[1].split(':')[0],
            'PASSWORD': os.environ['DATABASE_URL'].split(':')[2].split('@')[0],
            'HOST': os.environ['DATABASE_URL'].split('@')[1].split(':')[0],
            'PORT': os.environ['DATABASE_URL'].split(':')[-1].split('/')[0],
        }
    else:
        # Si estamos en desarrollo local, usar SQLite
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
        }

    # Ejecutar migraciones
    call_command('migrate', '--noinput')

    # Crear superusuario si no existe
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratorio_project.settings')
    django.setup()
    setup_database() 