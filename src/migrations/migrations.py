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
            from src.utils.auth import hash_password
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            
            password_hash = hash_password(admin_password)
            
            cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, is_active)
            VALUES (%s, %s, %s, %s, %s);
            """, (admin_username, password_hash, admin_email, 'Administrador', True))
            
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

def fix_admin_password():
    """
    Atualiza a senha do usuário admin usando o algoritmo correto.
    """
    try:
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        # Verifica se o usuário admin existe
        user_exists = execute_query("""
            SELECT id FROM users WHERE username = %s
        """, params=(admin_username,), fetchone=True)
        
        if not user_exists:
            print(f"Usuário {admin_username} não encontrado. Pulando correção de senha.")
            return
            
        # Importa a função correta para hash de senha
        from src.utils.auth import hash_password
        
        # Gera o hash da senha usando o algoritmo correto
        password_hash = hash_password(admin_password)
        
        # Atualiza a senha do usuário admin
        execute_query("""
            UPDATE users 
            SET password_hash = %s 
            WHERE username = %s
        """, params=(password_hash, admin_username))
        
        print(f"Senha do usuário {admin_username} atualizada com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao corrigir senha do admin: {str(e)}")
        print(f"Erro ao corrigir senha do admin: {str(e)}")

def add_google_translate_api_key_column():
    """
    Adiciona a coluna google_translate_api_key na tabela user_settings.
    """
    try:
        # Verificar se a tabela user_settings existe
        table_exists = execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_settings'
            );
        """, fetchone=True)
        
        if not table_exists or not table_exists[0]:
            print("A tabela user_settings não existe. Pulando adição da coluna google_translate_api_key.")
            return
            
        # Verificar se a coluna google_translate_api_key já existe
        column_exists = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_settings' AND column_name = 'google_translate_api_key'
        """, fetchone=True)
        
        if not column_exists:
            print("Adicionando coluna google_translate_api_key à tabela user_settings...")
            execute_query("""
                ALTER TABLE user_settings 
                ADD COLUMN google_translate_api_key VARCHAR(255) DEFAULT NULL
            """)
            print("Coluna google_translate_api_key adicionada com sucesso.")
        else:
            print("A coluna google_translate_api_key já existe. Pulando...")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna google_translate_api_key: {str(e)}")
        print(f"Erro ao adicionar coluna google_translate_api_key: {str(e)}")

def run_all_migrations():
    """
    Executa todas as migrações necessárias para a aplicação.
    """
    try:
        logger.info("Iniciando execução de migrações...")
        
        # Configuração inicial do banco de dados
        setup_database()
        
        # Migrações específicas
        add_updated_at_column()
        add_language_columns()
        fix_password_column()
        
        # Corrigir senha do admin
        fix_admin_password()
        
        # Adicionar coluna is_admin
        add_is_admin_column()
        
        # Migração para configurações de usuário
        create_user_settings_table()
        
        # Atualizar configurações
        update_user_settings()
        
        # Atualizar prompts
        update_user_settings_prompts()
        
        # Adicionar colunas específicas de configuração
        add_openai_model_column()
        add_social_media_prompts_columns()
        add_google_translate_api_key_column()
        
        logger.info("Todas as migrações foram executadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a execução das migrações: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_migrations() 