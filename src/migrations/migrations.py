import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from src.utils.database import execute_query, get_connection

logger = logging.getLogger('app')

def setup_database():
    """
    Configura o banco de dados inicial da aplicação.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        logger.info("Verificando se as tabelas já existem...")
        
        # Verifica se a tabela users existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        if not cursor.fetchone()[0]:
            logger.info("Criando tabelas iniciais...")
            
            # Tabela de usuários
            cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Tabela de sessões
            cursor.execute("""
            CREATE TABLE sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                token VARCHAR(100) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Tabela de vídeos
            cursor.execute("""
            CREATE TABLE videos (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                original_filename VARCHAR(255),
                video_url VARCHAR(255),
                is_file BOOLEAN DEFAULT TRUE,
                storage_path VARCHAR(255),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_language VARCHAR(10) DEFAULT 'en' NOT NULL,
                target_language VARCHAR(10) DEFAULT 'pt' NOT NULL,
                num_speakers INTEGER DEFAULT 0 NOT NULL
            );
            """)
            
            # Tabela de legendas
            cursor.execute("""
            CREATE TABLE subtitles (
                id SERIAL PRIMARY KEY,
                video_id INTEGER REFERENCES videos(id),
                language VARCHAR(10) NOT NULL,
                format VARCHAR(10) DEFAULT 'srt',
                storage_path VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Cria um usuário padrão
            from werkzeug.security import generate_password_hash
            salt = os.environ.get('SALT', 'autosub_salt')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            password_hash = generate_password_hash(f"{admin_password}{salt}")
            
            cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, is_active)
            VALUES (%s, %s, %s, %s, %s);
            """, ('admin', password_hash, 'admin@example.com', 'Administrador', True))
            
            logger.info("Banco de dados inicializado com sucesso!")
        else:
            logger.info("Banco de dados já configurado. Pulando inicialização...")
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Configuração do banco de dados concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {str(e)}")
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()

def add_is_admin_column():
    """
    Adiciona a coluna is_admin à tabela users.
    """
    try:
        # Verificar se a coluna já existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """, fetchone=True)
        
        if result:
            print("A coluna is_admin já existe. Pulando migração...")
            return
        
        print("Verificando se a coluna is_admin existe...")
        
        # Adicionar a coluna is_admin à tabela users
        execute_query("""
            ALTER TABLE users 
            ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
        """)
        
        print("Coluna is_admin adicionada com sucesso!")
        
        # Atualizar o usuário 'admin' para ter is_admin = TRUE
        execute_query("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE username = 'admin'
        """)
        
        print("Usuário admin atualizado para administrador com sucesso!")
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro ao adicionar coluna is_admin: {str(e)}")

def create_user_settings_table():
    """
    Cria a tabela user_settings se ela não existir.
    """
    try:
        # Verificar se a tabela já existe
        result = execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_settings'
            );
        """, fetchone=True)
        
        if result and result[0]:
            print("Tabela user_settings já existe.")
        else:
            # Criar a tabela user_settings
            execute_query("""
                CREATE TABLE user_settings (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES users(id),
                    transcription_service VARCHAR(20) DEFAULT 'whisper',
                    openai_api_key TEXT,
                    openai_model VARCHAR(50) DEFAULT 'gpt-4o-mini',
                    instagram_prompt TEXT,
                    tiktok_prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("Tabela user_settings criada com sucesso!")
        
        print("Tabela user_settings criada ou já existente.")
        
    except Exception as e:
        print(f"Erro ao criar tabela user_settings: {str(e)}")

def update_user_settings():
    """
    Atualiza a tabela user_settings com novos campos.
    """
    try:
        # Verificar se a coluna openai_model existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_settings' AND column_name = 'openai_model'
        """, fetchone=True)
        
        if not result:
            # Adicionar a coluna openai_model
            execute_query("""
                ALTER TABLE user_settings 
                ADD COLUMN openai_model VARCHAR(50) DEFAULT 'gpt-4o-mini'
            """)
            print("Coluna openai_model adicionada com sucesso!")
        
        # Criar configurações para usuários que não têm
        execute_query("""
            INSERT INTO user_settings (user_id, transcription_service)
            SELECT u.id, 'whisper'
            FROM users u
            LEFT JOIN user_settings us ON u.id = us.user_id
            WHERE us.id IS NULL
        """)
        
        print("Tabela user_settings atualizada com novos campos.")
        
    except Exception as e:
        print(f"Erro ao atualizar tabela user_settings: {str(e)}")

def update_user_settings_prompts():
    """
    Adiciona e atualiza as colunas de prompts na tabela user_settings.
    """
    try:
        # Verificar se as colunas já existem
        instagram_result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_settings' AND column_name = 'instagram_prompt'
        """, fetchone=True)
        
        tiktok_result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_settings' AND column_name = 'tiktok_prompt'
        """, fetchone=True)
        
        custom_result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_settings' AND column_name = 'custom_prompt'
        """, fetchone=True)
        
        # Adicionar as colunas se não existirem
        if not instagram_result:
            execute_query("""
                ALTER TABLE user_settings 
                ADD COLUMN instagram_prompt TEXT
            """)
        
        if not tiktok_result:
            execute_query("""
                ALTER TABLE user_settings 
                ADD COLUMN tiktok_prompt TEXT
            """)
        
        # Se existe coluna custom_prompt, migrar para as novas colunas e remover
        if custom_result:
            # Migrar dados
            execute_query("""
                UPDATE user_settings 
                SET instagram_prompt = custom_prompt, tiktok_prompt = custom_prompt
                WHERE custom_prompt IS NOT NULL
            """)
            
            # Verificar se pode remover a coluna
            try:
                execute_query("""
                    ALTER TABLE user_settings 
                    DROP COLUMN custom_prompt
                """)
                print("Coluna custom_prompt removida após migração.")
            except Exception as e:
                print(f"Aviso: Não foi possível remover coluna custom_prompt: {str(e)}")
        
        print("Colunas instagram_prompt e tiktok_prompt adicionadas com sucesso.")
        print("Dados migrados de custom_prompt para os novos campos.")
        print("Migração de prompts concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro ao atualizar prompts: {str(e)}")

def add_language_columns():
    """
    Adiciona as colunas source_language, target_language e num_speakers na tabela videos.
    """
    try:
        # Verificar se a coluna source_language já existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'videos' AND column_name = 'source_language'
        """, fetchone=True)
        
        if not result:
            print("Adicionando coluna source_language à tabela videos...")
            execute_query("""
                ALTER TABLE videos 
                ADD COLUMN source_language VARCHAR(10) DEFAULT 'en' NOT NULL
            """)
            print("Coluna source_language adicionada com sucesso.")
        else:
            print("A coluna source_language já existe. Pulando...")
        
        # Verificar se a coluna target_language já existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'videos' AND column_name = 'target_language'
        """, fetchone=True)
        
        if not result:
            print("Adicionando coluna target_language à tabela videos...")
            try:
                execute_query("""
                    ALTER TABLE videos 
                    ADD COLUMN target_language VARCHAR(10) DEFAULT 'pt' NOT NULL
                """)
                print("Coluna target_language adicionada com sucesso.")
            except Exception as e:
                if "already exists" in str(e):
                    print("A coluna target_language já existe. Ignorando erro.")
                else:
                    raise
        else:
            print("A coluna target_language já existe. Pulando...")
        
        # Verificar se a coluna num_speakers já existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'videos' AND column_name = 'num_speakers'
        """, fetchone=True)
        
        if not result:
            print("Adicionando coluna num_speakers à tabela videos...")
            try:
                execute_query("""
                    ALTER TABLE videos 
                    ADD COLUMN num_speakers INTEGER DEFAULT 0 NOT NULL
                """)
                print("Coluna num_speakers adicionada com sucesso.")
            except Exception as e:
                if "already exists" in str(e):
                    print("A coluna num_speakers já existe. Ignorando erro.")
                else:
                    raise
        else:
            print("A coluna num_speakers já existe. Pulando...")
        
        print("Migração concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao adicionar colunas na tabela videos: {str(e)}")
        print(f"Erro ao adicionar colunas na tabela videos: {str(e)}")

def fix_password_column():
    """
    Verifica e corrige a coluna de senha na tabela users.
    Renomeia 'password' para 'password_hash' se necessário.
    """
    try:
        # Verificar se a tabela users existe
        table_exists = execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """, fetchone=True)
        
        if not table_exists or not table_exists[0]:
            print("A tabela users não existe. Pulando correção de coluna de senha.")
            return
            
        # Verificar se a coluna password existe
        password_exists = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'password'
        """, fetchone=True)
        
        # Verificar se a coluna password_hash existe
        password_hash_exists = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'password_hash'
        """, fetchone=True)
        
        # Se password existe e password_hash não existe, renomear a coluna
        if password_exists and not password_hash_exists:
            print("Renomeando coluna password para password_hash...")
            execute_query("""
                ALTER TABLE users
                RENAME COLUMN password TO password_hash;
            """)
            print("Coluna password renomeada para password_hash com sucesso!")
        elif not password_hash_exists:
            # Se nenhuma das colunas existe (caso estranho), criar a coluna password_hash
            print("Criando coluna password_hash...")
            execute_query("""
                ALTER TABLE users
                ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';
            """)
            print("Coluna password_hash criada com sucesso!")
        else:
            print("A coluna de senha já está correta. Pulando correção.")
            
    except Exception as e:
        logger.error(f"Erro ao corrigir coluna de senha: {str(e)}")
        print(f"Erro ao corrigir coluna de senha: {str(e)}")

def run_all_migrations():
    """
    Executa todas as migrações em ordem.
    """
    print("Iniciando processo de migração do banco de dados...")
    
    # Configuração inicial do banco
    setup_database()
    
    # Corrigir nome da coluna de senha
    fix_password_column()
    
    # Adicionar coluna is_admin
    add_is_admin_column()
    
    # Criar tabela de configurações de usuário
    create_user_settings_table()
    
    # Atualizar configurações
    update_user_settings()
    
    # Atualizar prompts
    update_user_settings_prompts()
    
    # Adicionar colunas de idioma
    add_language_columns()
    
    print("Todas as migrações foram concluídas com sucesso!")

if __name__ == "__main__":
    run_all_migrations() 