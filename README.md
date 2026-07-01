# TRAIBER

Aplicación web tipo Uber/inDrive, 100% en español y adaptada al Perú (moneda: Soles S/).
Construida con Django + Django Channels (WebSockets para tracking en vivo), Leaflet + OpenStreetMap
para mapas (sin necesidad de API key), y pagos simulados (Yape, Plin, tarjeta, efectivo).

## Requisitos

- Python 3.11+

## Instalación

```bash
cd TRAIBER
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo    # opcional: crea un pasajero y un conductor de prueba
```

## Levantar el servidor (con soporte de WebSockets)

Este proyecto usa Django Channels, por lo que se debe correr con un servidor ASGI (daphne),
no con `runserver` clásico:

```bash
python manage.py runserver
```

`runserver` en Django 4+ ya detecta `ASGI_APPLICATION` y sirve WebSockets automáticamente
en desarrollo, así que basta con el comando de siempre.

La app quedará disponible en http://127.0.0.1:8000/

## Usuarios de prueba (creados con `seed_demo`)

- Pasajero: `pasajero_demo` / `Demo2026!`
- Conductor (ya aprobado, con vehículo aprobado): `conductor_demo` / `Demo2026!`
- Admin (superusuario): el que creaste con `createsuperuser`

## Flujo principal

1. El pasajero pide un viaje desde `/viajes/pasajero/`, elige origen/destino en el mapa,
   y define tarifa automática o propone su propia tarifa (estilo inDrive).
2. Los conductores disponibles ven la solicitud en tiempo real (WebSocket) y la aceptan u ofertan.
3. Pasajero y conductor hacen seguimiento en vivo del viaje en el mapa.
4. Al finalizar, se registra el pago (simulado) y ambos se califican mutuamente.
5. El administrador aprueba conductores/vehículos y monitorea viajes activos desde `/panel/`
   (ingresando con una cuenta con `is_superuser=True` o `tipo_usuario=admin`).

## Notas técnicas

- **Mapas**: Leaflet + OpenStreetMap (Nominatim para geocodificación, OSRM demo server para rutas).
  Ambos son servicios públicos gratuitos; para producción con alto tráfico se recomienda
  hostear tu propia instancia de Nominatim/OSRM o contratar un plan.
- **Pagos**: Yape, Plin y tarjeta están **simulados** (se registra el pago en la base de datos
  sin conectar a una pasarela real). Para producción, conectar con Culqi, Niubiz o Mercado Pago.
- **WebSockets**: si existe la variable de entorno `REDIS_URL`, se usa `channels_redis`
  (recomendado en producción con más de un worker). Si no, cae a `InMemoryChannelLayer`,
  válido solo para un único proceso/worker (suficiente en el plan gratuito de Render).
- **Verificación de identidad**: el registro no envía SMS/correo real de verificación (no hay
  proveedor conectado); los campos `celular_verificado` / `correo_verificado` existen en el
  modelo `Usuario` para conectar un proveedor (Twilio, etc.) más adelante.

## Despliegue en GitHub + Render

### 1. Subir el código a GitHub

```bash
cd TRAIBER
git init
git add .
git commit -m "Version inicial de TRAIBER"
git branch -M main
git remote add origin <URL_DE_TU_REPO>
git push -u origin main
```

### 2. Desplegar en Render (con Blueprint, un clic)

Este proyecto incluye un [`render.yaml`](render.yaml) que crea automáticamente:
- Un **Web Service** Python que corre `daphne` (soporta WebSockets, necesario para el
  tracking en vivo).
- Una base de datos **PostgreSQL** (Render, plan gratuito/starter según disponibilidad).

Pasos:
1. En el dashboard de Render, click en **New +** → **Blueprint**.
2. Conecta tu repositorio de GitHub (`traiber`).
3. Render detecta `render.yaml` automáticamente y muestra el plan: un Web Service + una
   base de datos Postgres. Click en **Apply**.
4. Espera a que termine el build (instala dependencias, corre `collectstatic` y `migrate`
   automáticamente, ver `buildCommand` en `render.yaml`).
5. Una vez desplegado, entra a la **Shell** del servicio en Render (o usa el botón "Shell"
   en el dashboard) y crea el superusuario y los usuarios de prueba:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo
   ```

Si prefieres configurarlo manualmente (sin Blueprint):
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `daphne -b 0.0.0.0 -p $PORT config.asgi:application`
- Variables de entorno mínimas: `SECRET_KEY` (genera una), `DEBUG=False`, `DATABASE_URL`
  (la de tu Postgres de Render), `WEB_CONCURRENCY=1`.

### Limitaciones a tener en cuenta en producción

- **Archivos subidos (fotos de perfil, licencia, SOAT, vehículo)**: en el plan gratuito/estándar
  de Render el disco es efímero, así que estos archivos se pierden en cada redeploy o reinicio.
  Para producción real, conectar un almacenamiento externo (S3, Cloudflare R2, o un
  [Persistent Disk](https://render.com/docs/disks) de Render) usando `django-storages`.
- **Postgres gratuito de Render** puede expirar tras un periodo de prueba; revisa el plan
  vigente en tu cuenta y actualiza `render.yaml` si es necesario.
- **Un solo worker (`WEB_CONCURRENCY=1`)**: necesario si usas `InMemoryChannelLayer` (sin Redis),
  para que todos los WebSockets pasen por el mismo proceso. Si agregas un Redis de Render y
  defines la variable `REDIS_URL`, puedes escalar a más workers/instancias sin problema.
