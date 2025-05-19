"""
Script para migrar datos de SQLite a PostgreSQL.
Uso: python migrate_to_postgres.py DATABASE_URL
"""

import os
import sys
import django
from django.core.management import call_command
from django.conf import settings

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratorio_project.settings')
    django.setup()

def migrate_to_postgres(database_url):
    # Configurar la base de datos PostgreSQL
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': database_url.split('/')[-1],
        'USER': database_url.split('://')[1].split(':')[0],
        'PASSWORD': database_url.split(':')[2].split('@')[0],
        'HOST': database_url.split('@')[1].split(':')[0],
        'PORT': database_url.split(':')[-1].split('/')[0],
    }

    # Crear las tablas en PostgreSQL
    call_command('migrate', '--run-syncdb')

    # Exportar datos de SQLite
    call_command('dumpdata', '--exclude', 'contenttypes', '--exclude', 'auth.permission', 
                '--exclude', 'admin.logentry', '--exclude', 'sessions.session',
                output='data.json')

    # Importar datos a PostgreSQL
    call_command('loaddata', 'data.json')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python migrate_to_postgres.py DATABASE_URL")
        sys.exit(1)

    database_url = sys.argv[1]
    setup_django()
    migrate_to_postgres(database_url)
    print("Migración completada exitosamente!") 