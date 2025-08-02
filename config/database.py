import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

db_config = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "childbot_db"),
    'port': int(os.getenv("DB_PORT", "3306"))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to database")
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")