# Guía para desplegar en Vercel

## Pasos realizados para preparar el proyecto

1. Se creó el archivo `vercel.json` con la configuración para Vercel
2. Se modificó `laboratorio_project/wsgi.py` para exponer la aplicación como `app`
3. Se actualizó `laboratorio_project/settings.py` para:
   - Usar variables de entorno para SECRET_KEY y DEBUG
   - Configurar la base de datos con dj-database-url
   - Añadir soporte para archivos estáticos con WhiteNoise
   - Permitir dominios de Vercel
4. Se actualizó `requirements.txt` con las dependencias necesarias

## Requisitos previos para el despliegue

1. Crear una cuenta en Vercel (https://vercel.com)
2. Instalar la CLI de Vercel:
   ```
   npm install -g vercel
   ```
3. Crear una base de datos PostgreSQL en algún servicio como:
   - Railway (https://railway.app)
   - Supabase (https://supabase.com)
   - Neon (https://neon.tech)

## Pasos para desplegar

1. Inicia sesión en Vercel:
   ```
   vercel login
   ```

2. Despliega la aplicación:
   ```
   vercel
   ```

3. Durante el despliegue, configura las siguientes variables de entorno:
   - `DEBUG`: False
   - `SECRET_KEY`: (una clave secreta segura)
   - `DATABASE_URL`: (la URL de conexión a tu base de datos PostgreSQL)

4. Después del despliegue, ejecuta las migraciones:
   - Ve a tu panel de control en Vercel
   - Navega a tu proyecto → Settings → Functions → Console
   - Ejecuta:
     ```
     python manage.py migrate
     ```

## Verificación del despliegue

1. Accede a la URL proporcionada por Vercel
2. Verifica que puedes acceder a todas las páginas de tu aplicación
3. Comprueba que los archivos estáticos se cargan correctamente
4. Prueba las funcionalidades principales de la aplicación

## Solución de problemas comunes

1. **Problema**: Los archivos estáticos no se cargan
   **Solución**: Ejecuta `python manage.py collectstatic` en la consola de Vercel

2. **Problema**: Error de conexión a la base de datos
   **Solución**: Verifica que la URL de la base de datos sea correcta y que el servicio esté funcionando

3. **Problema**: Error 500 al acceder a la aplicación
   **Solución**: Verifica los logs en Vercel para identificar el problema

4. **Problema**: Tiempo de ejecución excedido
   **Solución**: Optimiza tu código o considera otra plataforma si tu aplicación es muy compleja

## Mantenimiento

- Para actualizar tu aplicación, simplemente haz push a tu repositorio y Vercel se encargará del despliegue automático
- Recuerda ejecutar migraciones después de cambios en los modelos

## Limitaciones de Vercel

- Entorno serverless con límites de tiempo de ejecución
- Límite de 100 MB para el código fuente en el plan gratuito
- No ideal para aplicaciones Django muy complejas 