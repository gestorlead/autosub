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

def check_if_tables_exist():
    """Verifica se as tabelas já existem no banco de dados."""
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'users'
    );
    """
    result = execute_query(query, fetchone=True)
    return result[0] if result else False

def create_tables():
    """Cria as tabelas no banco de dados se elas não existirem."""
    print("Criando tabelas no banco de dados...")
    
    # Tabela de usuários
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        full_name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(users_table)
    
    # Tabela de vídeos
    videos_table = """
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        title VARCHAR(255) NOT NULL,
        description TEXT,
        original_filename VARCHAR(255),
        video_url VARCHAR(500),
        is_file BOOLEAN NOT NULL,
        storage_path VARCHAR(500),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(videos_table)
    
    # Tabela de legendas
    subtitles_table = """
    CREATE TABLE IF NOT EXISTS subtitles (
        id SERIAL PRIMARY KEY,
        video_id INTEGER REFERENCES videos(id),
        language VARCHAR(10) NOT NULL,
        format VARCHAR(10) DEFAULT 'srt',
        storage_path VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(subtitles_table)
    
    # Tabela de sessões
    sessions_table = """
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(sessions_table)
    
    print("Tabelas criadas com sucesso!")

def create_admin_user():
    """Cria um usuário administrador padrão se não existir nenhum usuário."""
    check_query = "SELECT COUNT(*) FROM users;"
    result = execute_query(check_query, fetchone=True)
    
    if result[0] == 0:
        # Importar o módulo de hash de senha em tempo de execução para evitar dependências circulares
        from src.utils.auth import hash_password
        
        # Configurações do usuário admin
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "admin123")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        full_name = "Administrador"
        
        # Hash da senha
        password_hash = hash_password(password)
        
        # Inserir usuário admin
        insert_query = """
        INSERT INTO users (username, password_hash, email, full_name, is_active, is_admin)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        execute_query(insert_query, params=(username, password_hash, email, full_name, True, True))
        print(f"Usuário administrador '{username}' criado com sucesso!")

def setup_database():
    """Configura o banco de dados, cria tabelas e usuário admin se necessário."""
    if not wait_for_db():
        sys.exit(1)
    
    if not check_if_tables_exist():
        create_tables()
        create_admin_user()
    else:
        print("Banco de dados já configurado. Pulando inicialização...")
    
    print("Configuração do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    setup_database() 