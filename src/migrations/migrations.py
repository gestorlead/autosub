import os
import logging
from src.utils.database import execute_query, get_connection

logger = logging.getLogger('app')

def setup_database():
    """
    Configura o banco de dados inicial da aplicação.
    Cria todas as tabelas necessárias de uma única vez se o banco estiver vazio.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        logger.info("Verificando se o banco de dados já está configurado...")
        
        # Verifica se a tabela users existe (indicativo de banco já configurado)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        if not cursor.fetchone()[0]:
            logger.info("Banco de dados vazio. Criando estrutura completa...")
            
            # Função para atualização automática do campo updated_at
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                   NEW.updated_at = now(); 
                   RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            # 1. Tabela de usuários
            cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # 2. Tabela de sessões
            cursor.execute("""
            CREATE TABLE sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                token VARCHAR(100) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # 3. Tabela de vídeos
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
                source_language VARCHAR(10) DEFAULT 'en' NOT NULL,
                target_language VARCHAR(10) DEFAULT 'pt' NOT NULL,
                num_speakers INTEGER DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Trigger para atualização automática do updated_at em vídeos
            cursor.execute("""
                CREATE TRIGGER update_videos_updated_at BEFORE UPDATE
                ON videos FOR EACH ROW EXECUTE PROCEDURE 
                update_updated_at_column();
            """)
            
            # 4. Tabela de legendas
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
            
            # 5. Tabela de configurações de usuário
            cursor.execute("""
            CREATE TABLE user_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE REFERENCES users(id),
                transcription_service VARCHAR(20) DEFAULT 'whisper',
                openai_api_key TEXT,
                openai_model VARCHAR(50) DEFAULT 'gpt-4o-mini',
                instagram_prompt TEXT,
                tiktok_prompt TEXT,
                google_translate_api_key VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Trigger para atualização automática do updated_at em configurações
            cursor.execute("""
                CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE
                ON user_settings FOR EACH ROW EXECUTE PROCEDURE 
                update_updated_at_column();
            """)
            
            # Cria um usuário padrão
            from src.utils.auth import hash_password
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            
            password_hash = hash_password(admin_password)
            
            cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, is_active, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s);
            """, (admin_username, password_hash, admin_email, 'Administrador', True, True))
            
            # Obter o ID do usuário admin recém-criado
            cursor.execute("""
            SELECT id FROM users WHERE username = %s;
            """, (admin_username,))
            
            admin_id = cursor.fetchone()[0]
            
            # Criar configurações padrão para o usuário admin
            cursor.execute("""
            INSERT INTO user_settings (user_id, transcription_service, openai_model)
            VALUES (%s, %s, %s);
            """, (admin_id, 'whisper', 'gpt-4o-mini'))
            
            logger.info("Estrutura completa do banco de dados criada com sucesso!")
        else:
            logger.info("Banco de dados já configurado. Nenhuma ação necessária.")
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Configuração do banco de dados concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()
        raise

def run_all_migrations():
    """
    Função principal que verifica e configura o banco de dados.
    """
    try:
        logger.info("Iniciando verificação do banco de dados...")
        setup_database()
        logger.info("Banco de dados configurado com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a configuração do banco de dados: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_migrations() 