# Sistema de Préstamo de Equipos de Laboratorio

Aplicación web profesional para la gestión de préstamos de equipos en los laboratorios de Resistencia de Materiales, Instrumentación y Control, Metrología, Turbomaquinaria e Hidráulica.

## Características

- Gestión completa de personas (estudiantes y profesores)
- Gestión de equipos por laboratorio
- Sistema de préstamos con seguimiento
- Generación de PDF profesional para cada préstamo
- Interfaz gráfica moderna y responsive
- Búsqueda y filtrado avanzados

## Tecnologías

- **Backend**: Django
- **Frontend**: HTML, CSS, Bootstrap 5
- **Base de datos**: SQLite3
- **Generación de PDF**: WeasyPrint

## Estructura del Proyecto

```
laboratorio_app_django/
├── laboratorio_project/    # Configuración principal de Django
├── prestamos/              # Aplicación Django para la gestión de préstamos
│   ├── models.py           # Modelos de datos
│   ├── forms.py            # Formularios
│   ├── views.py            # Vistas
│   ├── urls.py             # Rutas
│   ├── templates/          # Plantillas HTML
│   │   ├── prestamos/      # Plantillas específicas de la aplicación
│   │   │   ├── pdf/        # Plantillas para generación de PDF
├── templates/              # Plantillas base
├── static/                 # Archivos estáticos
│   ├── css/                # Hojas de estilo
│   ├── js/                 # JavaScript
│   ├── img/                # Imágenes
├── venv/                   # Entorno virtual de Python
├── manage.py               # Script de gestión de Django
└── README.md               # Este archivo
```

## Instalación y Ejecución

### Requisitos previos

- Python 3.11+
- pip (gestor de paquetes de Python)

### Configuración del Entorno

1. Activar el entorno virtual:
   ```
   cd laboratorio_app_django
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Ejecutar migraciones:
   ```
   python manage.py migrate
   ```

4. Crear superusuario (opcional, si no existe):
   ```
   python manage.py createsuperuser
   ```

5. Iniciar el servidor:
   ```
   python manage.py runserver
   ```

6. Acceder a la aplicación en `http://localhost:8000`

## Credenciales de Acceso

- **Usuario**: admin
- **Contraseña**: admin123

## Uso

1. Iniciar sesión con las credenciales proporcionadas
2. Registrar laboratorios
3. Registrar personas (estudiantes o profesores)
4. Registrar equipos por laboratorio
5. Gestionar préstamos de equipos
6. Generar y descargar PDFs de préstamos

## Funcionalidades Principales

### Gestión de Personas
- Registro de estudiantes y profesores
- Búsqueda por cédula o código institucional
- Visualización de historial de préstamos

### Gestión de Equipos
- Registro de equipos por laboratorio
- Control de disponibilidad
- Búsqueda por código o nombre

### Gestión de Préstamos
- Registro de préstamos con fecha de devolución
- Búsqueda de personas por cédula
- Búsqueda de equipos por código
- Generación de PDF profesional con:
  - Encabezado institucional
  - Datos del préstamo
  - Tabla de equipos
  - Espacio para firma
  - Texto de responsabilidad
