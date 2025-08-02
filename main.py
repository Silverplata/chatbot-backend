from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from openai import OpenAI
import httpx
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
logger.info(f"DB_HOST: {os.getenv('DB_HOST')}")
logger.info(f"DB_PORT: {os.getenv('DB_PORT')}")
logger.info(f"DB_USER: {os.getenv('DB_USER')}")
logger.info(f"DB_NAME: {os.getenv('DB_NAME')}")

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

# Configuración de MySQL
db_config = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "childbot_db"),
    'port': int(os.getenv("DB_PORT", "3306"))  # Convertir a entero para asegurar compatibilidad
}

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de autenticación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 2000

class ColorPalette(BaseModel):
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str

class User(BaseModel):
    username: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str

# Funciones de utilidad
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to database")
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")

def get_user(db, username: str):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoints
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db_connection()
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()

@app.post("/chat")
async def chat(request: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente educativo para niños de 12 años. Responde de manera clara, simple y amigable, usando ejemplos que un niño de sexto grado pueda entender. Evita tecnicismos y explica cualquier término difícil. Las respuestas tienen que tener un maximo de 2000 tokens"},
                {"role": "user", "content": request.question}
            ],
            max_tokens=request.max_tokens
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user", response_model=User)
async def get_user_profile(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    db = get_db_connection()
    try:
        user = get_user(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "username": user["username"],
            "primary_color": user["primary_color"],
            "secondary_color": user["secondary_color"],
            "accent_color": user["accent_color"],
            "background_color": user["background_color"]
        }
    finally:
        db.close()

@app.put("/user/palette")
async def update_user_palette(palette: ColorPalette, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE users 
            SET primary_color = %s, secondary_color = %s, accent_color = %s, background_color = %s 
            WHERE username = %s
            """,
            (palette.primary_color, palette.secondary_color, palette.accent_color, palette.background_color, username)
        )
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Palette updated successfully"}
    finally:
        cursor.close()
        db.close()

@app.get("/test")
async def test():
    return {"message": "Backend is running"}