from src.utils.database import execute_query

def update_user_settings_table():
    """Atualiza a tabela user_settings adicionando campos para modelo da OpenAI e prompt personalizado."""
    
    query = """
    ALTER TABLE user_settings 
    ADD COLUMN IF NOT EXISTS openai_model VARCHAR(50) DEFAULT 'gpt-4o-mini',
    ADD COLUMN IF NOT EXISTS custom_prompt TEXT;
    """
    
    execute_query(query)
    
    print("Tabela user_settings atualizada com novos campos: openai_model e custom_prompt.")
    
if __name__ == "__main__":
    update_user_settings_table() 