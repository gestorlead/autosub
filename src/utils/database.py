import os
import psycopg2
import psycopg2.extras
import logging
from src.utils.logging_config import logger

# Configurações do banco de dados diretamente das variáveis de ambiente
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "autosub")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

def get_connection():
    """
    Retorna uma conexão com o banco de dados PostgreSQL.
    Não tenta criar o banco de dados, apenas conecta ao existente.
    Registra erros detalhados em caso de falha na conexão.
    """
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except psycopg2.OperationalError as e:
        logger.error(f"Erro operacional ao conectar ao banco: {e}")
        if "does not exist" in str(e):
            logger.error(f"O banco de dados '{DB_NAME}' não existe. Por favor, crie-o manualmente.")
        elif "password authentication failed" in str(e):
            logger.error(f"Falha na autenticação para o usuário {DB_USER}. Verifique as credenciais.")
        elif "could not connect to server" in str(e):
            logger.error(f"Não foi possível conectar ao servidor PostgreSQL em {DB_HOST}:{DB_PORT}.")
        raise
    except Exception as e:
        logger.error(f"Erro geral ao conectar ao banco: {e}")
        raise

def execute_query(query, params=None, fetchall=False, fetchone=False):
    """
    Executa uma query SQL e retorna o resultado se necessário.
    Registra erros detalhados em caso de falha.
    """
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
    except psycopg2.Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Erro PostgreSQL ao executar query: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Parâmetros: {params}")
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Erro geral ao executar query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def check_db_connection():
    """
    Verifica se é possível conectar ao banco de dados.
    Retorna True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        connection = get_connection()
        connection.close()
        logger.info(f"Conexão com o banco de dados '{DB_NAME}' testada com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Não foi possível conectar ao banco de dados: {e}")
        return False 