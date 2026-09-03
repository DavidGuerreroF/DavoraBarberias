# BarberShop — Documentación Completa del Proyecto

> Sistema web para barbería desarrollado con Python + Django + SQLite.  
> Última actualización: Septiembre 2026

---

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Estructura de Carpetas](#3-estructura-de-carpetas)
4. [Base de Datos — Modelos y Relaciones](#4-base-de-datos--modelos-y-relaciones)
5. [Aplicaciones Django](#5-aplicaciones-django)
6. [URLs y Rutas](#6-urls-y-rutas)
7. [Vistas (Views)](#7-vistas-views)
8. [Formularios (Forms)](#8-formularios-forms)
9. [Templates y Diseño](#9-templates-y-diseño)
10. [Sistema de Reservas por WhatsApp](#10-sistema-de-reservas-por-whatsapp)
11. [Panel Administrativo](#11-panel-administrativo)
12. [Configuración del Proyecto](#12-configuración-del-proyecto)
13. [Guía de Modificaciones Comunes](#13-guía-de-modificaciones-comunes)
14. [Migración a PostgreSQL](#14-migración-a-postgresql)
15. [Despliegue en Producción](#15-despliegue-en-producción)
16. [Comandos de Gestión](#16-comandos-de-gestión)

---

## 1. Visión General

### ¿Qué hace esta aplicación?

BarberShop es un sistema web completo para la gestión de una barbería con dos partes claramente diferenciadas:

**Sitio Público** — accesible para cualquier visitante sin cuenta:
- Página de inicio con presentación de la barbería
- Catálogo de servicios con precios y duración
- Presentación del equipo de barberos
- Formulario de reserva de citas que se envía por WhatsApp

**Panel Administrativo** — solo para el personal de la barbería:
- Dashboard con resumen del día
- Gestión completa de citas (5 estados)
- Gestión de barberos, servicios y clientes
- Cambio rápido de estado de citas
- Validación anti-reservas duplicadas

### Flujo principal de una reserva

```
Cliente visita la web
        ↓
Selecciona servicio, barbero, fecha y hora
        ↓
Ingresa nombre y número WhatsApp
        ↓
La cita se guarda en la BD con estado "pendiente"
        ↓
Se abre WhatsApp con el mensaje pre-armado
        ↓
El cliente envía el mensaje a la barbería
        ↓
El admin confirma en el panel → estado "confirmada"
        ↓
Atención → estado "atendida"
```

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión | Rol |
|---|---|---|---|
| Lenguaje | Python | 3.10+ | Backend |
| Framework web | Django | 4.2.7 | MVC completo |
| Base de datos | SQLite | Incluida en Python | Almacenamiento local |
| ORM | Django ORM | — | Abstracción de BD |
| Frontend CSS | CSS personalizado + Bootstrap | 5.3.2 | Diseño responsive |
| Iconos | Bootstrap Icons | 1.11.3 | Iconografía |
| Tipografías | Google Fonts | — | Bebas Neue, Inter |
| Imágenes | Pillow | 10.1.0 | Procesamiento de fotos |
| Archivos estáticos | Whitenoise | 6.6.0 | Servir estáticos en producción |
| Configuración | python-decouple | 3.8 | Variables de entorno |

### Dependencias (`requirements.txt`)

```
Django==4.2.7
Pillow==10.1.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
whitenoise==6.6.0
python-decouple==3.8
```

---

## 3. Estructura de Carpetas

```
c:\Barber_Py\
│
├── config/                     # Configuración global del proyecto Django
│   ├── settings.py             # ← CONFIGURACIÓN PRINCIPAL
│   ├── urls.py                 # ← RUTAS RAÍZ
│   ├── wsgi.py                 # Servidor WSGI (producción)
│   └── asgi.py                 # Servidor ASGI (async)
│
├── core/                       # App: configuración de la barbería y página home
│   ├── models.py               # Modelo ConfiguracionBarberia
│   ├── views.py                # Vista home pública
│   ├── panel_views.py          # ← TODAS las vistas del panel admin
│   ├── urls.py                 # Rutas públicas de core (solo home)
│   ├── panel_urls.py           # ← RUTAS del panel admin
│   ├── admin.py                # Registro en Django Admin
│   └── management/
│       └── commands/
│           └── cargar_datos_demo.py  # Comando: python manage.py cargar_datos_demo
│
├── barberos/                   # App: gestión de barberos
│   ├── models.py               # Barbero, HorarioBarbero
│   ├── views.py                # Vista pública lista de barberos
│   ├── urls.py                 # /barberos/
│   └── admin.py
│
├── servicios/                  # App: catálogo de servicios
│   ├── models.py               # Servicio
│   ├── views.py                # Vista pública lista de servicios
│   ├── urls.py                 # /servicios/
│   └── admin.py
│
├── citas/                      # App: reservas y citas
│   ├── models.py               # Cita (modelo principal del negocio)
│   ├── views.py                # Reserva pública + API de horas disponibles
│   ├── forms.py                # ← TODOS los formularios del sistema
│   ├── urls.py                 # /citas/reservar/ y /citas/api/horas/
│   └── admin.py
│
├── clientes/                   # App: directorio de clientes
│   ├── models.py               # Cliente
│   └── admin.py
│
├── ventas/                     # App: ventas y caja (preparada, pendiente)
│   ├── models.py               # Venta, DetalleVenta
│   └── admin.py
│
├── inventario/                 # App: inventario de productos (preparada, pendiente)
│   ├── models.py               # Producto, CategoriaProducto, MovimientoInventario
│   └── admin.py
│
├── templates/                  # Plantillas HTML
│   ├── base.html               # Base mínima (solo HTML, head, scripts)
│   ├── base_public.html        # Base del sitio público (navbar + footer)
│   ├── base_panel.html         # Base del panel admin (sidebar + topbar)
│   ├── public/                 # Páginas del sitio público
│   │   ├── home.html
│   │   ├── servicios.html
│   │   ├── barberos.html
│   │   ├── reservar.html
│   │   └── reserva_exitosa.html
│   └── panel/                  # Páginas del panel admin
│       ├── login.html
│       ├── dashboard.html
│       ├── citas_lista.html
│       ├── cita_form.html
│       ├── barberos_lista.html
│       ├── barbero_form.html
│       ├── servicios_lista.html
│       ├── servicio_form.html
│       ├── clientes_lista.html
│       └── cliente_form.html
│
├── static/
│   └── css/
│       └── main.css            # ← TODO el CSS personalizado (tema morado/negro)
│
├── media/                      # Archivos subidos por usuarios
│   ├── barberos/               # Fotos de barberos
│   ├── servicios/              # Imágenes de servicios
│   └── config/                 # Logo y hero de la barbería
│
├── manage.py                   # CLI de Django
├── requirements.txt            # Dependencias Python
├── setup.bat                   # Script de instalación inicial (Windows)
└── db.sqlite3                  # Base de datos SQLite (se crea con migrate)
```

---

## 4. Base de Datos — Modelos y Relaciones

### Diagrama de Relaciones

```
ConfiguracionBarberia
        (singleton)

Barbero ←─────────────────────── HorarioBarbero
   │                              (día, hora inicio, hora fin)
   │
   ├──── FK ────→ Cita ←──── FK ──── Servicio
   │               │
   │               ├──── FK (nullable) ──── Cliente
   │               └──── OneToOne ──────── Venta
   │
   └──── FK ────→ Venta ←──── FK ──── DetalleVenta
                                           └──── FK (nullable) ──── Servicio

Producto ←──── FK ──── MovimientoInventario
    └──── FK ──── CategoriaProducto
```

---

### Modelo: `ConfiguracionBarberia` (app `core`)

Tabla singleton que guarda los datos globales de la barbería.

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | CharField(200) | Nombre de la barbería |
| `slogan` | CharField(300) | Slogan que aparece en el hero |
| `descripcion` | TextField | Descripción larga |
| `whatsapp` | CharField(20) | **Número al que llegan las reservas** (con código país: 573001234567) |
| `telefono` | CharField(20) | Teléfono de contacto |
| `email` | EmailField | Email de contacto |
| `direccion` | TextField | Dirección física |
| `instagram` | CharField(100) | Usuario de Instagram (sin @) |
| `facebook` | CharField(100) | Usuario de Facebook |
| `logo` | ImageField | Logo de la barbería |
| `imagen_hero` | ImageField | Imagen de fondo del hero |
| `horario_texto` | TextField | Texto libre con el horario de atención |
| `activo` | BooleanField | Si está activo (solo uno debe estarlo) |

**Método especial:** `ConfiguracionBarberia.get_config()` — retorna el registro activo o crea uno por defecto. Usado en todas las vistas.

---

### Modelo: `Barbero` (app `barberos`)

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | CharField(100) | Nombre |
| `apellido` | CharField(100) | Apellido |
| `telefono` | CharField(20) | WhatsApp personal |
| `foto` | ImageField | Foto del barbero |
| `especialidades` | TextField | Lista separada por comas |
| `activo` | BooleanField | Si aparece en el sitio público |
| `orden` | PositiveIntegerField | Orden de aparición (menor = primero) |

**Métodos:** `nombre_completo` (property), `get_especialidades_lista()` retorna lista Python.

---

### Modelo: `HorarioBarbero` (app `barberos`)

Relacionado con `Barbero`. Define disponibilidad por día de semana.

| Campo | Tipo | Descripción |
|---|---|---|
| `barbero` | FK → Barbero | Barbero al que pertenece |
| `dia_semana` | IntegerField | 0=Lunes, 1=Martes... 6=Domingo |
| `hora_inicio` | TimeField | Hora de entrada |
| `hora_fin` | TimeField | Hora de salida |
| `activo` | BooleanField | Si ese día trabaja |

> **Nota:** Los horarios aún no se usan para bloquear reservas automáticamente. La API de horas disponibles usa un rango fijo 8am–8pm con slots de 30 min.

---

### Modelo: `Servicio` (app `servicios`)

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | CharField(100) | Nombre del servicio |
| `descripcion` | TextField | Descripción |
| `precio` | DecimalField(8,2) | Precio en la moneda local |
| `duracion_minutos` | PositiveIntegerField | Duración estimada |
| `imagen` | ImageField | Foto del servicio |
| `activo` | BooleanField | Si aparece en el sitio público |
| `orden` | PositiveIntegerField | Orden de aparición |

---

### Modelo: `Cliente` (app `clientes`)

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | CharField(100) | Nombre |
| `apellido` | CharField(100) | Apellido |
| `whatsapp` | CharField(20) | Número de WhatsApp |
| `email` | EmailField | Email (opcional) |
| `notas` | TextField | Notas internas |
| `creado` | DateTimeField | Fecha de registro automática |

**Método:** `get_whatsapp_url()` — genera URL `wa.me/NUMERO`.

> Los clientes actualmente se crean manualmente desde el panel. En el futuro se puede vincular automáticamente cuando un cliente reserva por primera vez.

---

### Modelo: `Cita` (app `citas`) — MODELO CENTRAL

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre_cliente` | CharField(100) | Nombre (no requiere cuenta) |
| `whatsapp_cliente` | CharField(20) | WhatsApp del cliente |
| `barbero` | FK → Barbero | Barbero asignado (nullable) |
| `servicio` | FK → Servicio | Servicio solicitado (nullable) |
| `cliente` | FK → Cliente | Vínculo opcional con Cliente registrado |
| `fecha` | DateField | Fecha de la cita |
| `hora` | TimeField | Hora de la cita |
| `estado` | CharField(20) | Ver estados abajo |
| `notas` | TextField | Notas del cliente |
| `notas_admin` | TextField | Notas internas del admin |
| `creado` | DateTimeField | Fecha de creación automática |

#### Estados de la Cita

| Valor en BD | Etiqueta | Color | Significado |
|---|---|---|---|
| `pendiente` | Pendiente | Amarillo | Recién creada, sin confirmar |
| `confirmada` | Confirmada | Azul | Confirmada por la barbería |
| `atendida` | Atendida | Verde | El cliente fue atendido |
| `cancelada` | Cancelada | Rojo | Cancelada por cualquier parte |
| `no_asistio` | No asistió | Gris | El cliente no se presentó |

**Métodos:**
- `color_estado` — retorna el string Bootstrap para el badge
- `es_hoy` — `True` si la cita es para hoy
- `get_whatsapp_url()` — URL para enviar confirmación al cliente
- `get_whatsapp_reserva_url(barberia_whatsapp)` — URL para solicitud inicial de reserva

**Regla de negocio anti-duplicados:** No pueden existir dos citas con el mismo `barbero + fecha + hora` en estado `pendiente` o `confirmada`. Se valida tanto en el formulario público (`ReservaPublicaForm.verificar_disponibilidad()`) como en el formulario admin (`CitaAdminForm.clean()`).

---

### Modelo: `Venta` y `DetalleVenta` (app `ventas`)

Preparados para implementación futura. `Venta` se puede vincular a una `Cita` (OneToOne).

| Campo Venta | Tipo | Descripción |
|---|---|---|
| `cita` | OneToOne → Cita | Cita origen (opcional) |
| `barbero` | FK → Barbero | Barbero que realizó la venta |
| `total` | DecimalField | Total de la venta |
| `metodo_pago` | CharField | efectivo / transferencia / tarjeta |
| `registrado_por` | FK → User | Usuario del sistema que registró |

---

### Modelo: `Producto`, `CategoriaProducto`, `MovimientoInventario` (app `inventario`)

Preparados para implementación futura de control de stock.

---

## 5. Aplicaciones Django

### `core` — Núcleo del sistema

Contiene:
- `ConfiguracionBarberia`: datos globales de la barbería
- Vista `home`: página de inicio pública
- `panel_views.py`: **todas las vistas del panel administrativo** (dashboard, CRUD de citas, barberos, servicios, clientes, login/logout)
- `panel_urls.py`: todas las rutas del panel

### `barberos`

Gestión del equipo de barberos. Incluye horarios por día de semana.

### `servicios`

Catálogo de servicios con precio, duración e imagen.

### `citas`

El corazón del negocio. Maneja reservas públicas, validación de disponibilidad y la API de horas libres.

### `clientes`

Directorio de clientes. Actualmente se llenan manualmente; preparado para vincular automáticamente con reservas futuras.

### `ventas`

Módulo preparado para registro de ventas, caja y comisiones. No tiene vistas aún.

### `inventario`

Módulo preparado para control de stock de productos. No tiene vistas aún.

---

## 6. URLs y Rutas

### Raíz (`config/urls.py`)

```
/                    → core.urls           (home)
/citas/              → citas.urls          (reservas)
/servicios/          → servicios.urls      (catálogo)
/barberos/           → barberos.urls       (equipo)
/panel/              → core.panel_urls     (admin)
/django-admin/       → Django Admin nativo
```

### Rutas públicas completas

| URL | Nombre | Vista |
|---|---|---|
| `/` | `home` | `core.views.home` |
| `/servicios/` | `servicios` | `servicios.views.lista_servicios` |
| `/barberos/` | `barberos` | `barberos.views.lista_barberos` |
| `/citas/reservar/` | `reservar` | `citas.views.reservar` |
| `/citas/api/horas/` | `horas_disponibles` | `citas.views.horas_disponibles` |

### Rutas del panel admin (`/panel/...`)

| URL | Nombre | Descripción |
|---|---|---|
| `/panel/login/` | `panel_login` | Login |
| `/panel/logout/` | `panel_logout` | Logout |
| `/panel/` | `panel_dashboard` | Dashboard |
| `/panel/citas/` | `panel_citas` | Lista de citas (con filtros) |
| `/panel/citas/nueva/` | `panel_cita_crear` | Crear cita |
| `/panel/citas/<pk>/editar/` | `panel_cita_editar` | Editar cita |
| `/panel/citas/<pk>/estado/` | `panel_cita_estado` | Cambiar estado (POST) |
| `/panel/citas/<pk>/eliminar/` | `panel_cita_eliminar` | Eliminar (POST) |
| `/panel/barberos/` | `panel_barberos` | Lista barberos |
| `/panel/barberos/nuevo/` | `panel_barbero_crear` | Crear barbero |
| `/panel/barberos/<pk>/editar/` | `panel_barbero_editar` | Editar barbero |
| `/panel/barberos/<pk>/eliminar/` | `panel_barbero_eliminar` | Eliminar (POST) |
| `/panel/servicios/` | `panel_servicios` | Lista servicios |
| `/panel/servicios/nuevo/` | `panel_servicio_crear` | Crear servicio |
| `/panel/servicios/<pk>/editar/` | `panel_servicio_editar` | Editar servicio |
| `/panel/servicios/<pk>/eliminar/` | `panel_servicio_eliminar` | Eliminar (POST) |
| `/panel/clientes/` | `panel_clientes` | Lista clientes |
| `/panel/clientes/nuevo/` | `panel_cliente_crear` | Crear cliente |
| `/panel/clientes/<pk>/editar/` | `panel_cliente_editar` | Editar cliente |
| `/panel/clientes/<pk>/eliminar/` | `panel_cliente_eliminar` | Eliminar (POST) |

---

## 7. Vistas (Views)

### Vistas públicas

#### `core/views.py` → `home(request)`
Carga configuración, los primeros 6 servicios activos y todos los barberos activos. Renderiza `public/home.html`.

#### `servicios/views.py` → `lista_servicios(request)`
Todos los servicios activos ordenados. Renderiza `public/servicios.html`.

#### `barberos/views.py` → `lista_barberos(request)`
Todos los barberos activos ordenados. Renderiza `public/barberos.html`.

#### `citas/views.py` → `reservar(request)`
- **GET:** Muestra el formulario. Acepta `?servicio=<pk>` y `?barbero=<pk>` para pre-llenar campos.
- **POST:** Valida el formulario, verifica disponibilidad, crea la `Cita` con estado `pendiente`, genera la URL de WhatsApp y redirige a `reserva_exitosa.html`.

#### `citas/views.py` → `horas_disponibles(request)`
- **GET:** API JSON. Recibe `?barbero_id=X&fecha=YYYY-MM-DD`.
- Retorna `{"horas": ["08:00", "08:30", ...], "ocupadas": ["10:00"]}`.
- Genera slots de 30 min entre 8am y 8pm, excluyendo horas ya ocupadas.

### Vistas del panel (`core/panel_views.py`)

Todas requieren `@login_required`. Patrón general: GET muestra formulario o lista, POST procesa y redirige con mensaje de éxito.

#### `dashboard(request)`
Consulta citas de hoy, totales de pendientes/clientes/barberos, últimas 10 citas. Renderiza `panel/dashboard.html`.

#### `citas_lista(request)`
Acepta filtros GET: `?estado=`, `?fecha=`, `?barbero=`, `?q=` (búsqueda por nombre o WhatsApp). Renderiza tabla con `Cita.ESTADOS` disponibles para cambio inline.

#### `cita_cambiar_estado(request, pk)`
Solo POST. Acepta `?estado=nuevo_estado`. Si la petición tiene header `X-Requested-With: XMLHttpRequest` responde JSON (para uso futuro con AJAX). Normalmente redirige a la lista.

---

## 8. Formularios (Forms)

Todos en `citas/forms.py`.

### `ReservaPublicaForm` (forms.Form)

Formulario de reserva pública. No es ModelForm porque el proceso incluye lógica extra antes de crear la cita.

| Campo | Validación especial |
|---|---|
| `fecha` | No puede ser fecha pasada |
| `whatsapp` | Limpia caracteres, mínimo 7 dígitos |
| `barbero` | No requerido (puede ser "cualquiera") |

**Método `verificar_disponibilidad()`:** Se llama manualmente en la vista después de `form.is_valid()`. Lanza `ValidationError` si ya existe cita con el mismo barbero/fecha/hora en estado activo.

### `CitaAdminForm` (forms.ModelForm)

Para crear/editar citas desde el panel. Incluye `clean()` con la misma validación anti-duplicados, pero excluye la propia instancia al editar.

### `BarberoForm`, `ServicioForm`, `ClienteForm`

ModelForms estándar. Todos los widgets tienen `class="form-control form-control-dark"` para el tema oscuro.

---

## 9. Templates y Diseño

### Jerarquía de herencia

```
base.html
    ├── base_public.html    → hereda todas las páginas públicas
    │       ├── public/home.html
    │       ├── public/servicios.html
    │       ├── public/barberos.html
    │       ├── public/reservar.html
    │       └── public/reserva_exitosa.html
    │
    └── base_panel.html     → hereda todas las páginas del panel
            ├── panel/login.html  (no hereda base_panel, hereda base directo)
            ├── panel/dashboard.html
            ├── panel/citas_lista.html
            ├── panel/cita_form.html
            ├── panel/barberos_lista.html
            ├── panel/barbero_form.html
            ├── panel/servicios_lista.html
            ├── panel/servicio_form.html
            ├── panel/clientes_lista.html
            └── panel/cliente_form.html
```

### `base.html`
Solo estructura HTML mínima: `<!DOCTYPE html>`, meta tags, Bootstrap 5 CSS, Bootstrap Icons, Google Fonts, `main.css`. Bloque `{% block body %}`.

### `base_public.html`
Extiende `base.html`. Incluye:
- Navbar responsive con link a reservar
- Bloque `{% block content %}`
- Footer con redes sociales, contacto y horario (datos de `ConfiguracionBarberia`)

### `base_panel.html`
Extiende `base.html`. Incluye:
- Sidebar fijo con navegación y usuario
- Overlay para móvil
- Topbar con título de página y breadcrumb
- Mensajes de Django (`{% if messages %}`)
- Bloque `{% block panel_content %}`
- JavaScript para toggle del sidebar en móvil

### CSS (`static/css/main.css`)

Organizado en secciones con comentarios:

| Sección | Qué hace |
|---|---|
| Variables CSS (`:root`) | Paleta morado/negro, tipografías, radios, sombras |
| Navbar | Barra de navegación pública sticky |
| Hero | Sección principal con gradiente y efectos |
| Buttons | `.btn-primary-barber`, `.btn-outline-barber`, `.btn-whatsapp` |
| Section Headers | Título + eyebrow + divider morado |
| Cards | `.servicio-card`, `.barbero-card`, `.card-barber` |
| Forms | `.form-control-dark`, `.form-card`, `.form-label-barber` |
| Steps | Indicador de pasos del formulario de reserva |
| Badges | `.badge-estado` con variantes por estado de cita |
| Sidebar | Panel fijo con `.sidebar-link`, `.sidebar-badge` |
| Panel Content | Topbar, `.panel-main`, stat cards, tablas |
| Footer | Footer público |
| Animaciones | `.fade-up`, `.delay-1` al `.delay-5` |
| Responsive | Media queries para 991px y 768px |

#### Variables de color disponibles

```css
--purple-900 a --purple-100   /* Escala de morado */
--black-900 a --black-300     /* Escala de negro */
--gold                        /* Dorado para acentos */
--success / --danger / --warning / --info  /* Estados */
```

---

## 10. Sistema de Reservas por WhatsApp

### Cómo funciona

1. El cliente llena el formulario en `/citas/reservar/`
2. Se crea un objeto `Cita` en la BD con estado `pendiente`
3. Se genera una URL de WhatsApp usando `Cita.get_whatsapp_reserva_url(barberia_whatsapp)`
4. El cliente es redirigido a una página de éxito con un botón que abre WhatsApp
5. El mensaje pre-armado se envía al número de la barbería
6. El admin ve la cita en el panel y la confirma manualmente

### Formato del mensaje generado

```
Hola! Quisiera reservar una cita.
Nombre: [nombre del cliente]
Servicio: [servicio seleccionado]
Barbero: [barbero o "Cualquiera"]
Fecha: [dd/mm/yyyy]
Hora: [HH:MM]
WhatsApp: [número del cliente]
```

### Configurar el número de WhatsApp

Entrar a **Django Admin** → **Configuración de la Barbería** → campo `whatsapp`.

Formato requerido: código de país + número, **sin espacios ni símbolos**.
- ✅ Correcto: `573001234567`
- ❌ Incorrecto: `+57 300 123-4567`

### Mensaje de confirmación al cliente

Cuando el admin quiere confirmar la cita, puede hacer clic en el ícono de WhatsApp en la tabla de citas. Esto genera un mensaje de confirmación dirigido al número del cliente usando `Cita.get_whatsapp_url()`.

---

## 11. Panel Administrativo

### Acceso

- URL: `http://localhost:8000/panel/`
- Requiere usuario de Django (`User` del auth de Django)
- El comando `cargar_datos_demo` crea `admin` / `admin123`

### Crear usuarios adicionales

```cmd
python manage.py createsuperuser
```

O desde Django Admin: `http://localhost:8000/django-admin/` → Usuarios.

### Dashboard

Muestra en tiempo real:
- Total de citas del día con detalle por hora
- Conteo de citas por estado (pendiente, confirmada, atendida, cancelada)
- Total de clientes y barberos activos
- Últimas 10 solicitudes recibidas

### Gestión de Citas

**Filtros disponibles:** por estado, fecha, barbero, y búsqueda de texto (nombre o WhatsApp).

**Cambio de estado inline:** el `<select>` en la tabla hace POST automáticamente al cambiar el valor, sin necesidad de entrar al formulario de edición.

**Botón WhatsApp en tabla:** cada fila tiene un enlace que abre WhatsApp con mensaje de confirmación pre-armado para el cliente.

### Django Admin (`/django-admin/`)

Útil para:
- Editar `ConfiguracionBarberia` (nombre, WhatsApp, horario, logo)
- Hacer ajustes masivos en lotes
- Consultar datos crudos de cualquier tabla

---

## 12. Configuración del Proyecto

### `config/settings.py` — Variables importantes

| Variable | Descripción | Cambiar en producción |
|---|---|---|
| `SECRET_KEY` | Clave criptográfica | **Sí, obligatorio** |
| `DEBUG` | Modo debug | Cambiar a `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | Poner dominio real |
| `DATABASES` | Configuración de BD | Ver sección PostgreSQL |
| `LANGUAGE_CODE` | Idioma | `es-es` |
| `TIME_ZONE` | Zona horaria | `America/Bogota` (cambiar si es otro país) |
| `MEDIA_ROOT` | Dónde se guardan las fotos | Mover a almacenamiento externo en producción |
| `LOGIN_URL` | URL de login | `/panel/login/` |

### Zona horaria

Para cambiar la zona horaria edita en `config/settings.py`:
```python
TIME_ZONE = 'America/Bogota'  # Colombia
# TIME_ZONE = 'America/Mexico_City'  # México
# TIME_ZONE = 'America/Santiago'     # Chile
# TIME_ZONE = 'America/Lima'         # Perú
# TIME_ZONE = 'Europe/Madrid'        # España
```

---

## 13. Guía de Modificaciones Comunes

### Cambiar el nombre y datos de la barbería

**Opción 1 (recomendada):** Django Admin → Configuración de la Barbería.

**Opción 2:** Comando de demostración en `core/management/commands/cargar_datos_demo.py`, líneas del bloque `ConfiguracionBarberia.objects.get_or_create(...)`.

---

### Agregar un nuevo estado a las citas

Archivo: `citas/models.py`

```python
# 1. Agregar la constante
ESTADO_EN_PROCESO = 'en_proceso'

# 2. Agregar a la lista ESTADOS
ESTADOS = [
    ...
    (ESTADO_EN_PROCESO, 'En proceso'),
]

# 3. Agregar el color
ESTADO_COLORES = {
    ...
    ESTADO_EN_PROCESO: 'warning',
}
```

Luego agregar el estilo CSS en `static/css/main.css`:
```css
.badge-estado.en_proceso { background: rgba(255,152,0,0.15); color: #ff9800; border: 1px solid rgba(255,152,0,0.3); }
```

Luego ejecutar:
```cmd
python manage.py makemigrations
python manage.py migrate
```

---

### Cambiar los slots de tiempo de las reservas

Archivo: `citas/views.py`, función `horas_disponibles`.

```python
# Actualmente genera slots cada 30 min de 8am a 8pm
for h in range(8, 20):       # ← cambiar rango de horas
    for m in [0, 30]:        # ← cambiar a [0, 20, 40] para cada 20 min
```

---

### Agregar un campo nuevo a Barbero (ej: Instagram)

1. `barberos/models.py` — agregar el campo:
```python
instagram = models.CharField(max_length=100, blank=True)
```

2. Crear y aplicar migración:
```cmd
python manage.py makemigrations barberos
python manage.py migrate
```

3. `citas/forms.py` → `BarberoForm.Meta.fields` — agregar `'instagram'`

4. `templates/panel/barbero_form.html` — agregar el campo en el formulario:
```html
<div class="col-12">
    <label class="form-label-barber">Instagram</label>
    {{ form.instagram }}
</div>
```

5. Opcionalmente mostrar en la tarjeta pública `templates/public/barberos.html`.

---

### Agregar una nueva página pública (ej: Galería)

1. Crear vista en el app correspondiente o en `core/views.py`:
```python
def galeria(request):
    config = ConfiguracionBarberia.get_config()
    return render(request, 'public/galeria.html', {'config': config, 'page': 'galeria'})
```

2. Agregar URL en `core/urls.py`:
```python
path('galeria/', views.galeria, name='galeria'),
```

3. Crear template `templates/public/galeria.html`:
```html
{% extends 'base_public.html' %}
{% block content %}
  <!-- contenido aquí -->
{% endblock %}
```

4. Agregar el link en `templates/base_public.html` en el navbar:
```html
<a class="nav-link {% if page == 'galeria' %}active{% endif %}" href="{% url 'galeria' %}">
    Galería
</a>
```

---

### Agregar una sección en el panel admin (ej: módulo de Ventas)

1. Crear vistas en `core/panel_views.py` (o en `ventas/views.py` y importar).

2. Agregar URLs en `core/panel_urls.py`:
```python
path('ventas/', panel_views.ventas_lista, name='panel_ventas'),
```

3. Crear templates en `templates/panel/ventas_lista.html`.

4. Agregar link en el sidebar en `templates/base_panel.html`:
```html
<a href="{% url 'panel_ventas' %}" class="sidebar-link {% if page == 'ventas' %}active{% endif %}">
    <span class="sidebar-icon"><i class="bi bi-cash-stack"></i></span>
    Ventas
</a>
```

5. En cada vista del módulo pasar `'page': 'ventas'` en el contexto para que el sidebar marque el link activo.

---

### Cambiar los colores del tema

Archivo: `static/css/main.css`, sección `:root` al inicio del archivo.

```css
:root {
  --purple-600: #6600b3;   /* Color morado principal */
  --purple-400: #a929ff;   /* Morado claro (glow, acentos) */
  --purple-300: #c46aff;   /* Morado muy claro (textos sobre fondo oscuro) */
  --black-800: #0a0a0a;    /* Fondo principal de la página */
  --black-600: #1a1a1a;    /* Fondo de cards */
  --black-700: #111111;    /* Fondo del sidebar */
}
```

Para cambiar a un tema azul por ejemplo, reemplazar los valores `--purple-*` con tonos de azul.

---

### Habilitar registro automático de clientes

Cuando un cliente reserva, se puede crear automáticamente su registro en `Cliente`. Editar `citas/views.py`, función `reservar`, después de guardar la cita:

```python
# Después de cita.save()
from clientes.models import Cliente

cliente, creado = Cliente.objects.get_or_create(
    whatsapp=form.cleaned_data['whatsapp'],
    defaults={
        'nombre': form.cleaned_data['nombre'],
    }
)
cita.cliente = cliente
cita.save()
```

---

### Agregar validación de horario real del barbero

Actualmente la API usa 8am–8pm fijo. Para respetar `HorarioBarbero`:

En `citas/views.py`, función `horas_disponibles`, agregar:
```python
from barberos.models import HorarioBarbero
from datetime import date, time

dia_semana = fecha.weekday()  # 0=lunes
try:
    horario = HorarioBarbero.objects.get(barbero=barbero, dia_semana=dia_semana, activo=True)
    hora_inicio = horario.hora_inicio.hour
    hora_fin = horario.hora_fin.hour
except HorarioBarbero.DoesNotExist:
    return JsonResponse({'horas': [], 'mensaje': 'El barbero no trabaja ese día'})
```

Luego usar `hora_inicio` y `hora_fin` en el bucle en lugar del rango fijo.

---

## 14. Migración a PostgreSQL

Cuando el proyecto crezca o se lleve a un servidor, se recomienda migrar a PostgreSQL.

### Pasos

1. Instalar el adaptador:
```cmd
pip install psycopg2-binary
```

2. Crear la base de datos en PostgreSQL:
```sql
CREATE DATABASE barber_db;
CREATE USER barber_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE barber_db TO barber_user;
```

3. En `config/settings.py`, reemplazar el bloque `DATABASES`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barber_db',
        'USER': 'barber_user',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. Ejecutar migraciones sobre la nueva BD:
```cmd
python manage.py migrate
python manage.py cargar_datos_demo
```

> El bloque comentado ya está listo en `config/settings.py`. Solo hay que descomentar y llenar los datos.

---

## 15. Despliegue en Producción

### Variables de entorno recomendadas

Crear un archivo `.env` en la raíz (no subir a git):

```env
SECRET_KEY=una_clave_larga_y_aleatoria_aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DB_NAME=barber_db
DB_USER=barber_user
DB_PASSWORD=password_seguro
DB_HOST=localhost
```

Leer en `settings.py` con `python-decouple`:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

### Checklist de producción

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` cambiada por una aleatoria larga
- [ ] `ALLOWED_HOSTS` con el dominio real
- [ ] Base de datos migrada a PostgreSQL
- [ ] Archivos media en almacenamiento externo (S3, etc.)
- [ ] Ejecutar `python manage.py collectstatic`
- [ ] Configurar servidor web (nginx + gunicorn)
- [ ] SSL/HTTPS habilitado

### Recolectar archivos estáticos

```cmd
python manage.py collectstatic
```

Whitenoise sirve los estáticos automáticamente desde `staticfiles/`.

---

## 16. Comandos de Gestión

### Comandos estándar de Django

```cmd
# Aplicar migraciones
python manage.py migrate

# Crear migraciones después de modificar modelos
python manage.py makemigrations

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver

# Iniciar en puerto específico
python manage.py runserver 0.0.0.0:8080

# Verificar configuración
python manage.py check

# Recolectar estáticos para producción
python manage.py collectstatic

# Abrir shell de Python con Django cargado
python manage.py shell
```

### Comando personalizado: `cargar_datos_demo`

```cmd
python manage.py cargar_datos_demo
```

Crea:
- Configuración de la barbería con datos de ejemplo
- 6 servicios: Corte Clásico, Corte + Barba, Arreglo de Barba, Diseño y Degradado, Corte Infantil, Color y Mechas
- 3 barberos: Carlos Mendoza, Andrés Torres, Miguel García
- Superusuario: `admin` / `admin123`

Es seguro ejecutarlo múltiples veces — usa `get_or_create` y no duplica registros.

---

## Notas Finales

- **La base de datos** se crea automáticamente como `db.sqlite3` en la raíz del proyecto al ejecutar `migrate`. No necesitas instalar nada extra para SQLite.

- **Las imágenes** subidas (fotos de barberos, servicios, logo) se guardan en la carpeta `media/`. Incluir esta carpeta en los backups.

- **Las migraciones** en cada app (`*/migrations/`) deben subirse al control de versiones. Son el historial de cambios de la base de datos.

- **El panel de Django Admin** (`/django-admin/`) y el **panel propio** (`/panel/`) usan el mismo sistema de usuarios de Django. Un superusuario tiene acceso a ambos.
