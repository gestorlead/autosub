import os
import sys
import time
from src.utils.database import execute_query, check_db_connection

def wait_for_db():
    """Aguarda até que o banco de dados esteja disponível."""
    MAX_RETRIES = 30
    RETRY_INTERVAL = 2  # segundos
    
    print("Aguardando conexão com o banco de dados...")
    for retry in range(MAX_RETRIES):
        if check_db_connection():
            print("Conexão com o banco de dados estabelecida!")
            return True
        print(f"Tentativa {retry+1}/{MAX_RETRIES}. Tentando novamente em {RETRY_INTERVAL} segundos...")
        time.sleep(RETRY_INTERVAL)
    
    print("Não foi possível conectar ao banco de dados. Verifique as configurações.")
    return False

def check_if_column_exists():
    """Verifica se a coluna is_admin já existe na tabela users."""
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'is_admin'
    );
    """
    result = execute_query(query, fetchone=True)
    return result[0] if result else False

def add_is_admin_column():
    """Adiciona a coluna is_admin à tabela users."""
    print("Verificando se a coluna is_admin existe...")
    
    if check_if_column_exists():
        print("A coluna is_admin já existe. Pulando migração...")
        return
    
    print("Adicionando coluna is_admin à tabela users...")
    
    # Adicionar coluna is_admin
    add_column_query = """
    ALTER TABLE users
    ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
    """
    execute_query(add_column_query)
    
    # Definir o primeiro usuário como administrador
    update_admin_query = """
    UPDATE users
    SET is_admin = TRUE
    WHERE id = 1;
    """
    execute_query(update_admin_query)
    
    print("Coluna is_admin adicionada com sucesso!")
    print("Usuário ID 1 definido como administrador.")

def run_migration():
    """Executa a migração para adicionar a coluna is_admin."""
    if not wait_for_db():
        sys.exit(1)
    
    add_is_admin_column()
    
    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    run_migration() 