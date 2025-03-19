import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "autosub")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

def get_connection():
    """Retorna uma conexão com o banco de dados PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def execute_query(query, params=None, fetchall=False, fetchone=False):
    """Executa uma query SQL e retorna o resultado se necessário."""
    connection = None
    cursor = None
    result = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, params)
        
        if fetchall:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()
            
        connection.commit()
        return result
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao executar query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def check_db_connection():
    """Verifica se é possível conectar ao banco de dados."""
    try:
        connection = get_connection()
        connection.close()
        return True
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return False 