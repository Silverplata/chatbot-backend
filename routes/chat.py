from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ChatRequest
from config.settings import client
from utils.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=dict)
async def chat(request: ChatRequest, username: str = Depends(get_current_user)):
    try:
        # Extraer tema si la pregunta tiene el formato [tema] pregunta
        theme = "general"
        question_content = request.question
        if question_content.startswith("[") and "]" in question_content:
            theme = question_content[1:question_content.index("]")].lower()
            question_content = question_content[question_content.index("]") + 1:].strip()
        
        # Ajustar el prompt según el tema
        system_prompt = (
            f"Eres un asistente educativo para niños de 12 años. Responde de manera clara, simple y amigable, "
            f"usando ejemplos que un niño de sexto grado pueda entender. Evita tecnicismos y explica cualquier término difícil. "
            f"La pregunta está relacionada con el tema: {theme}. Las respuestas tienen que tener un máximo de 2000 tokens."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question_content}
            ],
            max_tokens=request.max_tokens
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))