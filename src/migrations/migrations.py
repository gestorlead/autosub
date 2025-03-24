import os
import logging
import sys
from src.utils.database import execute_query, get_connection, check_db_connection
from src.utils.logging_config import logger

# Flag global para evitar migrações duplicadas
_migration_executed = False

def setup_database():
    """
    Configura o banco de dados inicial da aplicação.
    Verifica e atualiza as tabelas existentes, mas não recria o banco.
    """
    global _migration_executed
    # Evitar executar migrations mais de uma vez por reinicialização
    if _migration_executed:
        logger.info("Migrações já executadas nesta sessão. Pulando.")
        return
        
    # Verificar se é possível conectar ao banco de dados
    if not check_db_connection():
        logger.error("Não foi possível conectar ao banco de dados. Interrompendo processo de migração.")
        sys.exit(1)
        
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        logger.info("Conectado ao banco de dados. Verificando estrutura...")
        
        # Verificar se a função de atualização automática existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_proc WHERE proname = 'update_updated_at_column'
            );
        """)
        
        if not cursor.fetchone()[0]:
            logger.info("Criando função update_updated_at_column()...")
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                   NEW.updated_at = now(); 
                   RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            logger.info("Função update_updated_at_column() criada com sucesso.")
            
        # Verificar se a tabela users existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        # Criar tabela users se não existir
        if not cursor.fetchone()[0]:
            logger.info("Tabela 'users' não encontrada. Criando...")
            cursor.execute("""
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
            """)
            logger.info("Tabela 'users' criada com sucesso.")
            
            # Verificar se já existe um usuário admin antes de criar
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s;", 
                          (os.environ.get('ADMIN_USERNAME', 'admin'),))
            if cursor.fetchone()[0] == 0:
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
                
                logger.info(f"Usuário administrador '{admin_username}' criado com sucesso.")
        else:
            logger.info("Tabela 'users' já existe. Pulando criação.")
        
        # Verificar se a tabela sessions existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sessions'
            );
        """)
        
        # Criar tabela sessions se não existir
        if not cursor.fetchone()[0]:
            logger.info("Tabela 'sessions' não encontrada. Criando...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                token VARCHAR(100) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            logger.info("Tabela 'sessions' criada com sucesso.")
        else:
            logger.info("Tabela 'sessions' já existe. Pulando criação.")
        
        # Verificar se a tabela videos existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'videos'
            );
        """)
        
        videos_exists = cursor.fetchone()[0]
        
        # Criar tabela videos se não existir
        if not videos_exists:
            logger.info("Tabela 'videos' não encontrada. Criando...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
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
            
            cursor.execute("""
                CREATE TRIGGER update_videos_updated_at BEFORE UPDATE
                ON videos FOR EACH ROW EXECUTE PROCEDURE 
                update_updated_at_column();
            """)
            logger.info("Tabela 'videos' criada com sucesso.")
        else:
            logger.info("Tabela 'videos' já existe. Verificando colunas...")
            # Verificar se existem as colunas necessárias na tabela videos
            for coluna, tipo in [
                ('source_language', 'VARCHAR(10) DEFAULT \'en\' NOT NULL'),
                ('target_language', 'VARCHAR(10) DEFAULT \'pt\' NOT NULL'),
                ('num_speakers', 'INTEGER DEFAULT 0 NOT NULL')
            ]:
                try:
                    # Verificar se a coluna existe
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'videos'
                            AND column_name = '{coluna}'
                        );
                    """)
                    
                    if not cursor.fetchone()[0]:
                        logger.info(f"Coluna '{coluna}' não encontrada na tabela 'videos'. Adicionando...")
                        cursor.execute(f"""
                            ALTER TABLE videos 
                            ADD COLUMN {coluna} {tipo};
                        """)
                        logger.info(f"Coluna '{coluna}' adicionada com sucesso.")
                    else:
                        logger.info(f"Coluna '{coluna}' já existe na tabela 'videos'.")
                        
                except Exception as e:
                    logger.warning(f"Erro ao verificar/adicionar coluna '{coluna}' na tabela videos: {str(e)}")
        
        # Verificar se a tabela subtitles existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'subtitles'
            );
        """)
        
        # Criar tabela subtitles se não existir
        if not cursor.fetchone()[0]:
            logger.info("Tabela 'subtitles' não encontrada. Criando...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtitles (
                id SERIAL PRIMARY KEY,
                video_id INTEGER REFERENCES videos(id),
                language VARCHAR(10) NOT NULL,
                format VARCHAR(10) DEFAULT 'srt',
                storage_path VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            logger.info("Tabela 'subtitles' criada com sucesso.")
        else:
            logger.info("Tabela 'subtitles' já existe. Pulando criação.")
        
        # Verificar se a tabela user_settings existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_settings'
            );
        """)
        
        user_settings_exists = cursor.fetchone()[0]
        
        # Criar tabela user_settings se não existir
        if not user_settings_exists:
            logger.info("Tabela 'user_settings' não encontrada. Criando...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
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
            
            cursor.execute("""
                CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE
                ON user_settings FOR EACH ROW EXECUTE PROCEDURE 
                update_updated_at_column();
            """)
            logger.info("Tabela 'user_settings' criada com sucesso.")
            
            # Se o usuário admin existir, verificar se tem config
            cursor.execute("SELECT id FROM users WHERE username = %s;", 
                         (os.environ.get('ADMIN_USERNAME', 'admin'),))
            admin_result = cursor.fetchone()
            if admin_result:
                admin_id = admin_result[0]
                
                # Verificar se já tem configuração
                cursor.execute("SELECT COUNT(*) FROM user_settings WHERE user_id = %s;", (admin_id,))
                if cursor.fetchone()[0] == 0:
                    # Criar configurações padrão para o usuário admin
                    cursor.execute("""
                    INSERT INTO user_settings (user_id, transcription_service, openai_model)
                    VALUES (%s, %s, %s);
                    """, (admin_id, 'whisper', 'gpt-4o-mini'))
                    
                    logger.info("Configurações para o usuário administrador criadas com sucesso.")
        else:
            logger.info("Tabela 'user_settings' já existe. Verificando colunas...")
            # Garantir que todas as colunas existam na tabela user_settings
            for coluna, tipo in [
                ('openai_model', 'VARCHAR(50) DEFAULT \'gpt-4o-mini\''),
                ('instagram_prompt', 'TEXT'),
                ('tiktok_prompt', 'TEXT'),
                ('google_translate_api_key', 'VARCHAR(255)')
            ]:
                try:
                    # Verificar se a coluna existe
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'user_settings'
                            AND column_name = '{coluna}'
                        );
                    """)
                    
                    if not cursor.fetchone()[0]:
                        logger.info(f"Coluna '{coluna}' não encontrada na tabela 'user_settings'. Adicionando...")
                        cursor.execute(f"""
                            ALTER TABLE user_settings 
                            ADD COLUMN {coluna} {tipo};
                        """)
                        logger.info(f"Coluna '{coluna}' adicionada com sucesso.")
                    else:
                        logger.info(f"Coluna '{coluna}' já existe na tabela 'user_settings'.")
                        
                except Exception as e:
                    logger.warning(f"Erro ao verificar/adicionar coluna '{coluna}' na tabela user_settings: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        _migration_executed = True
        logger.info("Verificação e atualização das tabelas concluída com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao verificar/atualizar tabelas no banco de dados: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()
        raise

def run_all_migrations():
    """
    Função principal que verifica e configura o banco de dados.
    Apenas verifica e atualiza tabelas, sem recriar o banco.
    """
    try:
        logger.info("Iniciando verificação das tabelas do banco de dados...")
        setup_database()
        logger.info("Verificação de tabelas concluída com sucesso.")
    except Exception as e:
        logger.error(f"Erro durante a verificação das tabelas: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_migrations() 