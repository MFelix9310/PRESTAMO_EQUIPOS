"""
WSGI config for laboratorio_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratorio_project.settings')

# Importar y ejecutar la configuración de la base de datos
try:
    from setup_database import setup_database
    setup_database()
except Exception as e:
    print(f"Error al configurar la base de datos: {e}")

application = get_wsgi_application()

# Importante: Vercel busca una variable llamada 'app'
app = application
