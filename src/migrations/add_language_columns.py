import logging
from src.utils.database import execute_query

logger = logging.getLogger('app')

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
            execute_query("""
                ALTER TABLE videos 
                ADD COLUMN target_language VARCHAR(10) DEFAULT 'pt' NOT NULL
            """)
            print("Coluna target_language adicionada com sucesso.")
        else:
            print("A coluna target_language já existe. Pulando...")
        
        # Verificar se a coluna num_speakers já existe
        result = execute_query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'videos' AND column_name = 'num_speakers'
        """, fetchone=True)
        
        if not result:
            print("Adicionando coluna num_speakers à tabela videos...")
            execute_query("""
                ALTER TABLE videos 
                ADD COLUMN num_speakers INTEGER DEFAULT 0 NOT NULL
            """)
            print("Coluna num_speakers adicionada com sucesso.")
        else:
            print("A coluna num_speakers já existe. Pulando...")
        
        print("Migração concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao adicionar colunas na tabela videos: {str(e)}")
        print(f"Erro ao adicionar colunas na tabela videos: {str(e)}")

if __name__ == "__main__":
    add_language_columns() 