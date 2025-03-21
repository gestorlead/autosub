from src.utils.database import execute_query

def create_user_settings_table():
    """Cria a tabela de configurações de usuário."""
    
    query = """
    CREATE TABLE IF NOT EXISTS user_settings (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        transcription_service VARCHAR(50) NOT NULL DEFAULT 'autosub',
        openai_api_key VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(user_id)
    );
    """
    
    execute_query(query)
    
    print("Tabela user_settings criada ou já existente.")
    
if __name__ == "__main__":
    create_user_settings_table() 