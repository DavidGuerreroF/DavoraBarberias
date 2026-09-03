"""
Comando de gestión para cargar datos de demostración.
Uso: python manage.py cargar_datos_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Carga datos de demostración para la barbería'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Cargando datos de demostración...'))

        # Importar modelos aquí para evitar errores de carga temprana
        from core.models import ConfiguracionBarberia
        from barberos.models import Barbero
        from servicios.models import Servicio
        from clientes.models import Cliente

        # ── Configuración de la barbería ──────────────────────────
        config, created = ConfiguracionBarberia.objects.get_or_create(
            activo=True,
            defaults={
                'nombre': 'BarberShop Elite',
                'slogan': 'Estilo y precisión en cada corte. Tu mejor versión comienza aquí.',
                'descripcion': 'Somos una barbería profesional con más de 10 años de experiencia. Ofrecemos cortes, barbas y diseños de la más alta calidad.',
                'whatsapp': '573001234567',
                'telefono': '3001234567',
                'email': 'info@barbershop.com',
                'direccion': 'Calle 45 # 23-10, Bogotá',
                'instagram': 'barbershop_elite',
                'facebook': 'barbershopelite',
                'horario_texto': 'Lunes – Viernes: 9:00am – 8:00pm\nSábados: 8:00am – 7:00pm\nDomingos: 10:00am – 4:00pm',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Configuración creada'))
        else:
            self.stdout.write('  · Configuración ya existe')

        # ── Servicios ─────────────────────────────────────────────
        servicios_demo = [
            {'nombre': 'Corte Clásico', 'precio': 25000, 'duracion_minutos': 30, 'orden': 1,
             'descripcion': 'Corte tradicional con tijera y máquina. Incluye lavado y peinado.'},
            {'nombre': 'Corte + Barba', 'precio': 40000, 'duracion_minutos': 45, 'orden': 2,
             'descripcion': 'Servicio completo de corte de cabello y arreglo de barba con navaja.'},
            {'nombre': 'Arreglo de Barba', 'precio': 20000, 'duracion_minutos': 20, 'orden': 3,
             'descripcion': 'Perfilado y arreglo de barba con navaja y productos premium.'},
            {'nombre': 'Diseño y Degradado', 'precio': 35000, 'duracion_minutos': 40, 'orden': 4,
             'descripcion': 'Corte con degradado gradual y diseño personalizado a tu estilo.'},
            {'nombre': 'Corte Infantil', 'precio': 18000, 'duracion_minutos': 25, 'orden': 5,
             'descripcion': 'Corte para niños hasta 12 años. Ambiente tranquilo y divertido.'},
            {'nombre': 'Color y Mechas', 'precio': 60000, 'duracion_minutos': 90, 'orden': 6,
             'descripcion': 'Aplicación de color, mechas o decoloración con productos de alta calidad.'},
        ]
        for s_data in servicios_demo:
            s, created = Servicio.objects.get_or_create(
                nombre=s_data['nombre'],
                defaults=s_data
            )
            estado = '✓ Creado' if created else '· Ya existe'
            self.stdout.write(f'  {estado}: Servicio "{s.nombre}"')

        # ── Barberos ──────────────────────────────────────────────
        barberos_demo = [
            {'nombre': 'Carlos', 'apellido': 'Mendoza', 'telefono': '3101234567',
             'especialidades': 'Corte clásico, Degradado, Diseños', 'orden': 1},
            {'nombre': 'Andrés', 'apellido': 'Torres', 'telefono': '3201234567',
             'especialidades': 'Barba, Corte moderno, Color', 'orden': 2},
            {'nombre': 'Miguel', 'apellido': 'García', 'telefono': '3151234567',
             'especialidades': 'Degradado, Corte infantil, Diseños', 'orden': 3},
        ]
        for b_data in barberos_demo:
            b, created = Barbero.objects.get_or_create(
                nombre=b_data['nombre'],
                apellido=b_data['apellido'],
                defaults=b_data
            )
            estado = '✓ Creado' if created else '· Ya existe'
            self.stdout.write(f'  {estado}: Barbero "{b.nombre_completo}"')

        # ── Superusuario ──────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@barbershop.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Superusuario creado: admin / admin123'))
        else:
            self.stdout.write('  · Superusuario "admin" ya existe')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('¡Datos de demostración cargados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write('')
        self.stdout.write('Acceso al panel:')
        self.stdout.write('  URL: http://localhost:8000/panel/')
        self.stdout.write('  Usuario: admin')
        self.stdout.write('  Contraseña: admin123')
        self.stdout.write('')
        self.stdout.write('Sitio público: http://localhost:8000/')
        self.stdout.write('')
