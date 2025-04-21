# PharmaPlus - Tienda en línea

Este proyecto es una tienda en línea para productos farmacéuticos y de cuidado personal, desarrollada con Django.

## Características

- Catálogo de productos por categorías
- Sistema de autenticación de usuarios
- Carrito de compras
- Gestión de direcciones de envío
- Procesamiento de pagos con Stripe y PayPal
- Panel de administración para gestionar productos, pedidos y usuarios

## Requisitos

- Python 3.10+
- Django 5.2
- Stripe y PayPal para procesamiento de pagos

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/pharmaplus.git
   cd pharmaplus
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv env
   # En Windows
   env\Scripts\activate
   # En macOS/Linux
   source env/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno:
   - Crear un archivo `.env` en la raíz del proyecto basándote en `.env.example`
   - Añadir tus claves API de Stripe y PayPal

5. Aplicar las migraciones:
   ```bash
   python manage.py migrate
   ```

6. Crear un superusuario:
   ```bash
   python manage.py createsuperuser
   ```

7. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Configuración de pasarelas de pago

### Stripe

1. Crear una cuenta en [Stripe](https://stripe.com)
2. Obtener las claves API de prueba desde el panel de Stripe
3. Añadir las claves al archivo `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### PayPal

1. Crear una cuenta de desarrollador en [PayPal Developer](https://developer.paypal.com)
2. Crear una aplicación para obtener las credenciales de API
3. Añadir las claves al archivo `.env`:
   ```
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_SECRET_KEY=your_secret_key
   PAYPAL_RECEIVER_EMAIL=your_business_email@example.com
   ```

## Uso

1. Acceder al panel de administración en `/admin/` para gestionar productos, categorías, usuarios y pedidos
2. Los usuarios pueden:
   - Registrarse y gestionar su perfil
   - Explorar productos por categorías
   - Añadir productos al carrito
   - Gestionar direcciones de envío
   - Realizar pagos con Stripe o PayPal
   - Ver el historial de pedidos

## Estructura del proyecto

- `app/` - Aplicación principal
  - `models.py` - Modelos de datos
  - `views.py` - Lógica de negocio
  - `urls.py` - Enrutamiento de URLs
  - `forms.py` - Formularios
  - `admin.py` - Configuración del panel de administración
  - `templates/` - Plantillas HTML
  - `static/` - Archivos estáticos (CSS, JS, imágenes)
- `ec/` - Configuración del proyecto
  - `settings.py` - Configuración de Django
  - `urls.py` - URLs principales
- `media/` - Archivos subidos por los usuarios (imágenes de productos)

## Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un pull request