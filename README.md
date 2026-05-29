# Proyecto LANDA

Prototipo web en Python para una banca en línea con login por usuario y contraseña, y reconocimiento facial opcional como acceso rápido. El flujo incluye alta de cliente, cambio de contraseña, activación o desactivación del rostro y un protocolo guiado de tres capturas con el rostro centrado en pantalla.

## Flujo principal

- El cliente crea sus credenciales con usuario y contraseña.
- Entra a su banca en línea con contraseña escrita.
- Desde Ajustes puede activar o desactivar el acceso facial.
- Si activa el rostro, el sistema solicita tres capturas: frontal, izquierda y derecha.
- Si el reconocimiento facial falla, la contraseña sigue disponible como respaldo.

## Principios de calidad aplicados

- Funcionalidad: autenticación por contraseña y por rostro con respaldo.
- Confiabilidad: validación de usuario, contraseña y calidad mínima de captura.
- Usabilidad: interfaz bancaria clara, responsive y con guía visual de cámara.
- Mantenibilidad: separación entre persistencia, lógica de autenticación, visión y vistas.
- Seguridad: contraseñas con hash, trazabilidad de eventos y biometría opcional.
- Trazabilidad: cada acción de seguridad queda registrada en SQLite.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

Luego abre `http://127.0.0.1:5000`.

## Alcance

Este repositorio sigue siendo un prototipo académico. Para producción todavía faltarían controles como MFA real, detección de liveness avanzada, cifrado de biometría en reposo, protección antifraude y validación normativa formal.

## Anexo: Información adicional (explicativa)

Este anexo describe de forma concisa la intención del proyecto, la estructura del código, y pasos prácticos para ejecutar y probar el prototipo.

- **Propósito:** Proveer un prototipo educativo de una banca en línea que demuestra integración de autenticación clásica (usuario/contraseña) con un método biométrico opcional (reconocimiento facial) pensado como acceso rápido y no como único factor.

- **Estructura del repositorio:**
	- `app.py`: Punto de entrada de la aplicación Flask.
	- `landa_biometrics/`: Módulo principal con la lógica de autenticación, gestión de sesiones, servicios de rostro y almacenamiento.
		- `web.py`, `auth.py`, `face_service.py`, `storage.py`, `config.py` y `__init__.py`.
	- `templates/`: Plantillas HTML (login, dashboard, wizard de rostro).
	- `static/`: JS y CSS del cliente (`face.js`, `styles.css`).
	- `data/uploads/`: Carpeta para archivos subidos (ej. capturas de rostro durante pruebas).
	- `tests/`: Pruebas unitarias básicas (ej. `test_storage.py`).

- **Dependencias clave:** Revisa `requirements.txt` para la lista completa; incluye Flask y bibliotecas usadas para manejo de imágenes/biometría en el prototipo.

- **Cómo ejecutar localmente (rápido):**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000` en el navegador.

- **Pruebas:** Ejecutar las pruebas unitarias con `pytest` (instalar `pytest` si hace falta):

```bash
pip install pytest
pytest -q
```

- **Notas de seguridad y privacidad:**
	- Las capturas faciales en este prototipo se almacenan en el sistema de archivos y en SQLite para trazabilidad; en entornos reales **no** deben almacenarse sin cifrado y consentimiento explícito.
	- La biometría aquí es opcional y la contraseña actúa como factor de respaldo.

- **Siguientes pasos recomendados para producción:**
	- Añadir cifrado en reposo y control de acceso estricto para datos biométricos.
	- Integrar detección de liveness robusta y mecanismos anti-spoofing.
	- Revisar requisitos legales y privacidad (consentimientos, retención, eliminación).

Si quieres, puedo adaptar este anexo para incluir ejemplos de API, diagramas de arquitectura o instrucciones de despliegue en un contenedor Docker.
