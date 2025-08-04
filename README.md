# Chatbot Backend

## Descripción

El backend del proyecto **Childbot** es una API RESTful construida con **FastAPI** que proporciona funcionalidades de autenticación y un endpoint de chat integrado con la API de OpenAI. Está diseñado para servir como el servidor principal de una aplicación de chatbot educativa dirigida a niños de 12 años, ofreciendo respuestas claras, simples y amigables.

### Características principales
- **Autenticación JWT**: Permite a los usuarios iniciar sesión con credenciales y obtener un token de acceso.
- **Endpoint de chat**: Procesa preguntas de los usuarios y genera respuestas usando el modelo `gpt-3.5-turbo` de OpenAI.
- **CORS**: Configurado para permitir solicitudes desde el frontend en `http://localhost:4200`.
- **Base de datos simulada**: Usa un diccionario en memoria para almacenar usuarios (puede expandirse a una base de datos real).

## Requisitos

- **Python**: 3.12.4
- **Docker**: (Opcional) Para ejecutar el backend en un contenedor.
- **Dependencias** (listadas en `requirements.txt`):
annotated-types==0.7.0
anyio==4.9.0
bcrypt==4.0.1
certifi==2025.7.14
cffi==1.17.1
click==8.2.1
colorama==0.4.6
cryptography==45.0.5
distro==1.9.0
ecdsa==0.19.1
fastapi==0.116.1
h11==0.16.0
httpcore==1.0.9
httpx==0.27.0
idna==3.10
jiter==0.10.0
openai==1.51.0
passlib==1.7.4
pyasn1==0.6.1
pycparser==2.22
pydantic==2.11.7
pydantic_core==2.33.2
python-dotenv==1.1.1
python-jose==3.5.0
python-multipart==0.0.20
rsa==4.9.1
six==1.17.0
sniffio==1.3.1
starlette==0.47.2
tqdm==4.67.1
typing-inspection==0.4.1
typing_extensions==4.14.1
uvicorn==0.35.0
mysql-connector-python==8.4.0
- **Clave de API de OpenAI**: Necesaria para las solicitudes al modelo `gpt-3.5-turbo`.

## Estructura del proyecto

```
chatbot-backend/
├── Dockerfile           # Configuración para construir la imagen de Docker
├── main.py             # Código principal de la API FastAPI
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```

## Configuración

1. **Clonar el repositorio** (si no lo has hecho):
   ```bash
   git clone <url-del-repositorio>
   cd chatbot-backend
   ```

2. **Crear un entorno virtual** (opcional, si no usas Docker):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   source venv/bin/activate  # En Linux/Mac
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   Crea un archivo `.env` en el directorio raíz del proyecto (`E:\childbot`) con el siguiente contenido:
   ```plaintext
   OPENAI_API_KEY=tu_clave_de_openai
   SECRET_KEY=tu_clave_secreta
   ```
   Reemplaza `tu_clave_de_openai` con una clave válida de OpenAI y `tu_clave_secreta` con una clave segura para JWT.

## Ejecución

### Opción 1: Localmente con Uvicorn
1. Activa el entorno virtual (si lo creaste):
   ```bash
   .\venv\Scripts\activate  # En Windows
   ```
2. Ejecuta el servidor:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. La API estará disponible en `http://localhost:8000`.

### Opción 2: Con Docker
1. Asegúrate de que el archivo `docker-compose.yml` esté en el directorio raíz (`E:\childbot`) y que incluya el servicio `backend`.
2. Construye y ejecuta el contenedor:
   ```bash
   cd E:\childbot
   docker-compose up --build
   ```
3. La API estará disponible en `http://localhost:8000`.

## Endpoints

- **POST /login**: Autentica a un usuario y devuelve un token JWT.
  - Cuerpo de la solicitud:
    ```json
    {
      "username": "student1",
      "password": "password123"
    }
    ```
  - Respuesta:
    ```json
    {
      "access_token": "<token_jwt>",
      "token_type": "bearer"
    }
    ```

- **POST /chat**: Procesa una pregunta y devuelve una respuesta generada por `gpt-3.5-turbo`.
  - Encabezado: `Authorization: Bearer <token_jwt>`
  - Cuerpo de la solicitud:
    ```json
    {
      "question": "Cuales son los ciclos lunares",
      "max_tokens": 500
    }
    ```
  - Respuesta:
    ```json
    {
      "response": "¡Hola! Los ciclos lunares son las diferentes formas que vemos de la Luna en el cielo..."
    }
    ```

- **GET /test**: Verifica que el backend esté funcionando.
  - Respuesta:
    ```json
    {
      "message": "Backend is running"
    }
    ```

## Pruebas

1. **Probar el endpoint de login**:
   ```bash
   curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=student1&password=password123"
   ```

2. **Probar el endpoint de chat**:
   Usa el token obtenido del endpoint `/login`:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <tu_token_jwt>" \
     -d '{"question": "Cuales son los ciclos lunares", "max_tokens": 500}'
   ```

3. **Probar el endpoint de test**:
   ```bash
   curl http://localhost:8000/test
   ```

## Notas
- Asegúrate de que la clave `OPENAI_API_KEY` sea válida para evitar errores en las solicitudes a la API de OpenAI.
- El valor predeterminado de `max_tokens` en el endpoint `/chat` es 500. Ajusta este valor en la solicitud si necesitas respuestas más largas.
- Para entornos de producción, considera usar una base de datos real en lugar de `fake_users_db` y configurar HTTPS.

## Solución de problemas
- **Error `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`**:
  - Asegúrate de usar `openai==1.30.0` y las versiones de dependencias especificadas en `requirements.txt`.
  - Verifica que el archivo `.env` contenga una clave válida para `OPENAI_API_KEY`.
- **Logs**: Revisa los logs del contenedor con:
  ```bash
  docker-compose logs backend
  ```