from fastapi import APIRouter, Depends, HTTPException
from config.database import get_db_connection
from utils.auth import get_current_user, get_user
from models.schemas import User, ColorPalette

router = APIRouter()

@router.get("/", response_model=User)
async def get_user_profile(username: str = Depends(get_current_user)):
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

@router.put("/palette")
async def update_user_palette(palette: ColorPalette, username: str = Depends(get_current_user)):
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