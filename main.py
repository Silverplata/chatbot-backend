from fastapi import FastAPI
from config.settings import configure_cors
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.user import router as user_router

app = FastAPI()

# Configurar CORS
configure_cors(app)

# Incluir routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(user_router, prefix="/user", tags=["user"])

@app.get("/test")
async def test():
    return {"message": "Backend is running"}