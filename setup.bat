@echo off
echo ========================================
echo  BarberShop - Instalacion inicial
echo ========================================
echo.

echo [1/4] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [2/4] Creando tablas en la base de datos...
python manage.py migrate

echo.
echo [3/4] Cargando datos de demostracion...
python manage.py cargar_datos_demo

echo.
echo [4/4] Creando carpetas de medios...
if not exist "media\servicios" mkdir "media\servicios"
if not exist "media\barberos" mkdir "media\barberos"
if not exist "media\config" mkdir "media\config"
if not exist "staticfiles" mkdir "staticfiles"

echo.
echo ========================================
echo  Listo! Ejecuta el servidor con:
echo  python manage.py runserver
echo.
echo  Sitio publico:  http://localhost:8000/
echo  Panel admin:    http://localhost:8000/panel/
echo  Usuario: admin  Contrasena: admin123
echo ========================================
pause
